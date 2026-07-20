# Claude Code command example

Use this file as the body of a Claude Code custom command such as `/torch-npu-pr-review`.

```text
You are reviewing Ascend torch-npu GitCode PRs.

Read the local package instructions from SKILL.md, then collect data with:

python scripts/gitcode_fetch.py {arguments}

Arguments may include:
- --issue https://gitcode.com/Ascend/pytorch/issues/2612
- --pr v2.7.1=https://gitcode.com/Ascend/pytorch/pull/40125
- --project-id 7404318
- --out outputs/torch-npu-pr-review

Use the generated data_report.md and raw/ artifacts as evidence. Apply the checklist in SKILL.md, then write the final review report in Markdown. Do not print token values.
```

Example invocation:

```bash
python scripts/gitcode_fetch.py \
  --issue https://gitcode.com/Ascend/pytorch/issues/2612 \
  --project-id 7404318 \
  --out outputs/issue-2612-data
```
