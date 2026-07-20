# Generic agent prompt

Use this prompt when the environment does not support Codex skills.

```text
Use the torch-npu-pr-review package in the current directory.

1. Read SKILL.md for the review checklist and GitCode collection strategy.
2. Run scripts/gitcode_fetch.py with the issue and/or PR URLs I provide.
3. Use the generated summary.json, data_report.md, and raw artifacts.
4. Produce the Ascend torch-npu PR review report following SKILL.md.

Never print GITCODE_ACCESS_TOKEN. If the token exists, use token-enhanced mode. If it does not exist, use no-token mode.
```

Minimal terminal usage:

```bash
python scripts/gitcode_fetch.py --issue ISSUE_URL --out outputs/review-data
```

Optional token-enhanced mode:

```bash
export GITCODE_ACCESS_TOKEN='...'
python scripts/gitcode_fetch.py --issue ISSUE_URL --out outputs/review-data
```
