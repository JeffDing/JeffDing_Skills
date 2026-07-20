#!/usr/bin/env python3
"""Cross-check that all 6 branches produce byte-identical patches + consistent commit messages.

Usage:
    GIT_TOKEN=xxx python3 verify_cross_branch.py 42082 42083 42084 42085 42086 42087

Fetches each PR's .patch via gitcode, strips commit-id/From/Date lines,
compares the normalized content across all PRs, and reports:
  - md5 of normalized patch (must be identical)
  - commit subject + body (must be identical)
  - any 'import torch' presence (F401 risk)
  - any '#xxx' placeholder leftover

Exit code 0 = consistent, 1 = differences found.
"""
import hashlib
import re
import sys
import urllib.request

PROJECT = "Ascend/pytorch"
TOKEN_ENV = "GIT_TOKEN"


def fetch_patch(pr_number: int, token: str) -> str:
    url = f"https://gitcode.com/{PROJECT}/pull/{pr_number}.patch"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    if token:
        req.add_header("Private-Token", token)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def normalize(patch: str) -> str:
    """Strip per-commit volatile lines (From hash, Date, git pseudo-headers)."""
    out = []
    for line in patch.splitlines():
        if line.startswith("From ") or line.startswith("Date:"):
            continue
        if line.startswith("diff --git") or line.startswith("index "):
            continue
        out.append(line)
    return "\n".join(out)


def extract_commit_message(patch: str) -> str:
    m = re.search(r"^Subject: \[PATCH\] (.+?)(?=\n---|\n\n\n)", patch, re.S | re.M)
    return m.group(1).strip() if m else ""


def main(pr_numbers):
    import os
    token = os.environ.get(TOKEN_ENV, "")
    patches = {}
    for pr in pr_numbers:
        patches[pr] = fetch_patch(pr, token)

    norms = {pr: normalize(p) for pr, p in patches.items()}
    digests = {pr: hashlib.md5(n.encode()).hexdigest() for pr, n in norms.items()}
    msgs = {pr: extract_commit_message(p) for pr, p in patches.items()}

    print(f"{'PR':<8}{'md5':<34}{'has import torch':<18}{'has #xxx'}")
    consistent_md5 = True
    consistent_msg = True
    for pr in pr_numbers:
        n = norms[pr]
        print(f"#{pr:<7}{digests[pr]:<34}"
              f"{'YES ⚠️' if re.search(r'^import torch\b', n, re.M) else 'no':<18}"
              f"{'YES ⚠️' if '#xxx' in n else 'no'}")

    ref_digest = digests[pr_numbers[0]]
    ref_msg = msgs[pr_numbers[0]]
    bad = []
    for pr in pr_numbers:
        if digests[pr] != ref_digest:
            consistent_md5 = False
            bad.append(f"#{pr} patch md5 differs from #{pr_numbers[0]}")
        if msgs[pr] != ref_msg:
            consistent_msg = False
            bad.append(f"#{pr} commit message differs from #{pr_numbers[0]}")

    print()
    if consistent_md5:
        print(f"✅ All {len(pr_numbers)} patches byte-identical (md5={ref_digest})")
    else:
        print("❌ Patches differ across branches")
    if consistent_msg:
        print("✅ All commit messages identical")
    else:
        print("❌ Commit messages differ across branches")

    if bad:
        print()
        for b in bad:
            print("  -", b)
        return 1
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main([int(x) for x in sys.argv[1:]]))
