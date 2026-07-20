#!/usr/bin/env python3
"""Fetch GitCode PR/issue data for Ascend torch-npu review workflows.

This script is intentionally agent-agnostic: Codex, Claude Code, CI, or a
plain terminal can run it. It uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


DEFAULT_PROJECT_ID = "7404318"
DEFAULT_TIMEOUT = 30


@dataclass
class RuntimeConfig:
    token: str
    mode: str
    user_agent: str
    user_agent_source: str
    accept_language: str
    timeout: int = DEFAULT_TIMEOUT


@dataclass
class FetchResult:
    url: str
    status: int
    text: str
    used_cookie: bool
    attempts: list[dict[str, Any]] = field(default_factory=list)

    def json(self) -> Any:
        return json.loads(self.text)


def default_user_agent() -> tuple[str, str]:
    system = platform.system().lower()
    if system == "darwin":
        return (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/126.0.0.0 Safari/537.36",
            "default-macos",
        )
    if system == "linux":
        return (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "default-linux",
        )
    return (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "default-windows",
    )


def build_config(timeout: int) -> RuntimeConfig:
    token = os.environ.get("GITCODE_ACCESS_TOKEN") or os.environ.get("gitcode_access_token") or ""
    mode = "token-enhanced" if token else "no-token"
    user_agent = os.environ.get("GITCODE_USER_AGENT") or os.environ.get("HTTP_USER_AGENT") or ""
    if user_agent:
        source = "GITCODE_USER_AGENT" if os.environ.get("GITCODE_USER_AGENT") else "HTTP_USER_AGENT"
    else:
        user_agent, source = default_user_agent()
    accept_language = os.environ.get("GITCODE_ACCEPT_LANGUAGE") or "zh-CN,zh;q=0.9,en;q=0.8"
    return RuntimeConfig(
        token=token,
        mode=mode,
        user_agent=user_agent,
        user_agent_source=source,
        accept_language=accept_language,
        timeout=timeout,
    )


def base_headers(config: RuntimeConfig, referer: str | None = None, accept: str | None = None) -> dict[str, str]:
    headers = {
        "User-Agent": config.user_agent,
        "Accept-Language": config.accept_language,
        "Accept": accept or "application/json, text/plain, */*",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://gitcode.com",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
    }
    if referer:
        headers["Referer"] = referer
    return headers


def request_once(url: str, headers: dict[str, str], timeout: int) -> tuple[int, str, dict[str, str]]:
    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            charset = resp.headers.get_content_charset() or "utf-8"
            return resp.status, raw.decode(charset, errors="replace"), dict(resp.headers)
    except HTTPError as exc:
        raw = exc.read()
        return exc.code, raw.decode("utf-8", errors="replace"), dict(exc.headers)
    except URLError as exc:
        return 0, str(exc), {}


def should_retry_without_cookie(status: int, text: str, expect_json: bool) -> bool:
    if status in (0, 401, 403, 418):
        return True
    if not text.strip():
        return True
    if expect_json:
        try:
            json.loads(text)
        except json.JSONDecodeError:
            return True
    return False


def fetch(
    url: str,
    config: RuntimeConfig,
    referer: str | None = None,
    prefer_cookie: bool = True,
    expect_json: bool = True,
    accept: str | None = None,
) -> FetchResult:
    headers = base_headers(config, referer=referer, accept=accept)
    attempts: list[dict[str, Any]] = []
    if config.token and prefer_cookie:
        cookie_headers = dict(headers)
        cookie_headers["Cookie"] = f"GITCODE_ACCESS_TOKEN={config.token}"
        status, text, _ = request_once(url, cookie_headers, config.timeout)
        attempts.append({"used_cookie": True, "status": status, "bytes": len(text)})
        if not should_retry_without_cookie(status, text, expect_json):
            return FetchResult(url=url, status=status, text=text, used_cookie=True, attempts=attempts)

    status, text, _ = request_once(url, headers, config.timeout)
    attempts.append({"used_cookie": False, "status": status, "bytes": len(text)})
    return FetchResult(url=url, status=status, text=text, used_cookie=False, attempts=attempts)


def parse_gitcode_url(url: str) -> dict[str, str]:
    parsed = urlparse(url)
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        raise ValueError(f"Cannot parse GitCode URL: {url}")
    owner, repo = parts[0], parts[1]
    result = {"owner": owner, "repo": repo}
    for key in ("pull", "merge_requests", "issues"):
        if key in parts:
            idx = parts.index(key)
            if idx + 1 < len(parts):
                if key == "issues":
                    result["issue"] = parts[idx + 1]
                else:
                    result["pr"] = parts[idx + 1]
    return result


def parse_pr_arg(value: str) -> tuple[str | None, str]:
    if "=" in value and not value.startswith("http"):
        label, url = value.split("=", 1)
        return label.strip() or None, url.strip()
    return None, value.strip()


def canonical_pr_url(owner: str, repo: str, number: str) -> str:
    return f"https://gitcode.com/{owner}/{repo}/pull/{number}"


def patch_url(owner: str, repo: str, number: str) -> str:
    return f"{canonical_pr_url(owner, repo, number)}.patch"


def issue_api_url(owner: str, repo: str, iid: str) -> str:
    return f"https://gitcode.com/api/v5/repos/{owner}/{repo}/issues/{iid}"


def issue_pulls_url(owner: str, repo: str, iid: str) -> str:
    return f"https://gitcode.com/api/v5/repos/{owner}/{repo}/issues/{iid}/pull_requests"


def internal_pr_url(project_id: str, number: str) -> str:
    return f"https://gitcode.com/api/v1/projects/{project_id}/merge_requests/{number}/internal"


def parse_patch(text: str) -> dict[str, Any]:
    files = sorted(set(m.group(2) for m in re.finditer(r"(?m)^diff --git a/(.*?) b/(.*?)$", text)))
    added_lines = [line[1:] for line in text.splitlines() if line.startswith("+") and not line.startswith("+++")]
    from_match = re.search(r"(?m)^From: (.*?) <([^>]+)>", text)
    subject_match = re.search(r"(?m)^Subject: (?:\[PATCH\]\s*)?(.*)", text)
    return {
        "commit_count": len(re.findall(r"(?m)^From [0-9a-f]{40} ", text)),
        "from_name": from_match.group(1) if from_match else "",
        "from_email": from_match.group(2) if from_match else "",
        "subject": subject_match.group(1).strip() if subject_match else "",
        "files": files,
        "added_sha256": hashlib.sha256("\n".join(added_lines).encode("utf-8")).hexdigest(),
    }


def extract_issue_ids(text: str) -> list[str]:
    ids = set(re.findall(r"gitcode\.com/[^\s)]+/issues/(\d+)", text or ""))
    ids.update(re.findall(r"(?<![\w/])#(\d+)\b", text or ""))
    return sorted(ids, key=lambda item: int(item))


def safe_json(text: str) -> Any | None:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, data: Any) -> None:
    write_text(path, json.dumps(data, ensure_ascii=False, indent=2))


def summarize_labels(data: dict[str, Any] | None) -> list[str]:
    labels = []
    for item in (data or {}).get("enterprise_labels") or []:
        if isinstance(item, dict):
            labels.append(item.get("name") or item.get("title") or "")
        else:
            labels.append(str(item))
    return [item for item in labels if item]


def collect_issue(owner: str, repo: str, iid: str, config: RuntimeConfig, raw_dir: Path) -> dict[str, Any]:
    page = f"https://gitcode.com/{owner}/{repo}/issues/{iid}"
    detail = fetch(issue_api_url(owner, repo, iid), config, referer=page, expect_json=True)
    pulls = fetch(issue_pulls_url(owner, repo, iid), config, referer=page, expect_json=True)
    write_text(raw_dir / f"issue_{iid}.json", detail.text)
    write_text(raw_dir / f"issue_{iid}_pull_requests.json", pulls.text)
    detail_json = safe_json(detail.text)
    pulls_json = safe_json(pulls.text)
    return {
        "iid": iid,
        "url": page,
        "detail_status": detail.status,
        "detail_used_cookie": detail.used_cookie,
        "detail_attempts": detail.attempts,
        "pull_requests_status": pulls.status,
        "pull_requests_used_cookie": pulls.used_cookie,
        "pull_requests_attempts": pulls.attempts,
        "title": detail_json.get("title") if isinstance(detail_json, dict) else "",
        "body_length": len((detail_json or {}).get("body") or "") if isinstance(detail_json, dict) else 0,
        "linked_pr_count": len(pulls_json) if isinstance(pulls_json, list) else 0,
        "linked_prs": pulls_json if isinstance(pulls_json, list) else [],
    }


def collect_pr(
    owner: str,
    repo: str,
    number: str,
    label: str | None,
    project_id: str,
    config: RuntimeConfig,
    raw_dir: Path,
) -> dict[str, Any]:
    pr_page = canonical_pr_url(owner, repo, number)
    patch_result = fetch(
        patch_url(owner, repo, number),
        config,
        referer=pr_page,
        prefer_cookie=False,
        expect_json=False,
        accept="text/plain, */*",
    )
    internal_result = fetch(
        internal_pr_url(project_id, number),
        config,
        referer=pr_page,
        prefer_cookie=True,
        expect_json=True,
    )
    write_text(raw_dir / f"pr_{number}.patch", patch_result.text)
    write_text(raw_dir / f"pr_{number}.internal.json", internal_result.text)
    patch_info = parse_patch(patch_result.text)
    internal = safe_json(internal_result.text)
    description = internal.get("description", "") if isinstance(internal, dict) else ""
    return {
        "number": number,
        "label": label or "",
        "url": pr_page,
        "patch_status": patch_result.status,
        "patch_attempts": patch_result.attempts,
        "internal_status": internal_result.status,
        "internal_used_cookie": internal_result.used_cookie,
        "internal_attempts": internal_result.attempts,
        "title": (internal or {}).get("title") or patch_info.get("subject") or "",
        "source_branch": (internal or {}).get("source_branch") or "",
        "target_branch": (internal or {}).get("target_branch") or label or "",
        "author": ((internal or {}).get("author") or {}).get("username") if isinstance((internal or {}).get("author"), dict) else "",
        "labels": summarize_labels(internal if isinstance(internal, dict) else None),
        "close_issue_when_merge": (internal or {}).get("close_issue_when_merge") if isinstance(internal, dict) else None,
        "issue_ids": extract_issue_ids(description),
        "patch": patch_info,
    }


def linked_prs_to_inputs(owner: str, repo: str, linked_prs: list[Any]) -> list[tuple[str | None, str]]:
    values = []
    for item in linked_prs:
        if not isinstance(item, dict):
            continue
        number = str(item.get("number") or "")
        if not number:
            continue
        base = item.get("base") if isinstance(item.get("base"), dict) else {}
        label = base.get("ref") or None
        values.append((label, canonical_pr_url(owner, repo, number)))
    return values


def render_report(summary: dict[str, Any]) -> str:
    lines = [
        "# GitCode PR Review Data Report",
        "",
        f"Generated: {summary['generated_at']}",
        f"Repository: {summary['repository']}",
        f"Collection mode: {summary['collection_mode']}",
        f"User-Agent source: {summary['user_agent_source']}",
        "",
        "## Issues",
        "",
        "| Issue | Status | Title | Body bytes | Linked PRs |",
        "|---|---:|---|---:|---:|",
    ]
    for issue in summary["issues"]:
        lines.append(
            f"| #{issue['iid']} | {issue['detail_status']} | {issue.get('title') or ''} | "
            f"{issue['body_length']} | {issue['linked_pr_count']} |"
        )
    lines.extend(["", "## Pull Requests", "", "| PR | Label | Target | Source | Patch | Internal | Title |", "|---:|---|---|---|---:|---:|---|"])
    for pr in summary["pull_requests"]:
        lines.append(
            f"| {pr['number']} | {pr.get('label') or ''} | {pr.get('target_branch') or ''} | "
            f"{pr.get('source_branch') or ''} | {pr['patch_status']} | {pr['internal_status']} | {pr.get('title') or ''} |"
        )
    lines.extend(["", "## Notes", ""])
    lines.append("- Raw API responses and patches are saved under `raw/`.")
    lines.append("- Token values are never written to the report.")
    lines.append("- Use this report as data input for the checklist in `SKILL.md`.")
    return "\n".join(lines) + "\n"


def dedupe_pr_inputs(values: list[tuple[str | None, str]]) -> list[tuple[str | None, str]]:
    seen = set()
    result = []
    for label, url in values:
        info = parse_gitcode_url(url)
        number = info.get("pr")
        key = (info["owner"], info["repo"], number)
        if key in seen:
            continue
        seen.add(key)
        result.append((label, url))
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch GitCode issue/PR data for review.")
    parser.add_argument("--issue", action="append", default=[], help="Issue URL, e.g. https://gitcode.com/Ascend/pytorch/issues/2612")
    parser.add_argument("--pr", action="append", default=[], help="PR URL or label=URL. Can be repeated.")
    parser.add_argument("--project-id", default=DEFAULT_PROJECT_ID, help="GitCode project id for PR internal API.")
    parser.add_argument("--out", default="", help="Output directory. Defaults to outputs/torch-npu-pr-review-<timestamp>.")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--no-discover-prs", action="store_true", help="Do not add PRs discovered from issue pull_requests API.")
    args = parser.parse_args(argv)

    if not args.issue and not args.pr:
        parser.error("provide at least one --issue or --pr")

    first_url = args.issue[0] if args.issue else parse_pr_arg(args.pr[0])[1]
    first_info = parse_gitcode_url(first_url)
    owner, repo = first_info["owner"], first_info["repo"]

    output_dir = Path(args.out) if args.out else Path("outputs") / f"torch-npu-pr-review-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    raw_dir = output_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    config = build_config(args.timeout)
    issue_summaries = []
    pr_inputs = [parse_pr_arg(value) for value in args.pr]

    for issue_url in args.issue:
        info = parse_gitcode_url(issue_url)
        if "issue" not in info:
            raise ValueError(f"URL does not appear to be an issue URL (missing 'issues/' in path): {issue_url}")
        issue = collect_issue(info["owner"], info["repo"], info["issue"], config, raw_dir)
        issue = collect_issue(info["owner"], info["repo"], info["issue"], config, raw_dir)
        issue_summaries.append(issue)
        if not args.no_discover_prs:
            pr_inputs.extend(linked_prs_to_inputs(info["owner"], info["repo"], issue["linked_prs"]))

    pr_summaries = []
    for label, pr_url in dedupe_pr_inputs(pr_inputs):
        info = parse_gitcode_url(pr_url)
        if "pr" not in info:
            raise ValueError(f"Cannot find PR number in {pr_url}")
        pr_summaries.append(
            collect_pr(info["owner"], info["repo"], info["pr"], label, args.project_id, config, raw_dir)
        )

    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "repository": f"{owner}/{repo}",
        "project_id": args.project_id,
        "collection_mode": config.mode,
        "token_present": bool(config.token),
        "user_agent_source": config.user_agent_source,
        "user_agent_length": len(config.user_agent),
        "accept_language": config.accept_language,
        "issues": issue_summaries,
        "pull_requests": pr_summaries,
    }
    write_json(output_dir / "summary.json", summary)
    write_text(output_dir / "data_report.md", render_report(summary))
    print(json.dumps({"out": str(output_dir), "summary": str(output_dir / "summary.json"), "report": str(output_dir / "data_report.md")}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
