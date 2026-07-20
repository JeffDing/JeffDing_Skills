# torch-npu-pr-review 通用包

用于审核 Ascend torch-npu 在 GitCode 上的 PR。这个包既可以作为 Codex skill 使用，也可以在 Claude Code、其他 Agent 或普通终端中直接运行。

核心能力：

- 获取 GitCode PR `.patch`、PR internal 元数据、issue 正文和 issue 关联 PR
- 支持 issue 入口自动发现关联 PR
- 支持显式传入单个或多个 PR
- 支持 `no-token` 和 `token-enhanced` 两种采集模式
- 自动适配完整 `User-Agent`
- 保存原始响应、结构化 summary 和 Markdown 数据报告

## 目录结构

```text
torch-npu-pr-review/
  SKILL.md
  README.md
  scripts/
    gitcode_fetch.py
  examples/
    claude-code-command.md
    generic-prompt.md
```

## 快速开始

只提供 issue，让脚本自动发现关联 PR：

```bash
python scripts/gitcode_fetch.py \
  --issue https://gitcode.com/Ascend/pytorch/issues/2612 \
  --project-id 7404318 \
  --out outputs/issue-2612-data
```

显式传入 PR：

```bash
python scripts/gitcode_fetch.py \
  --pr v2.7.1=https://gitcode.com/Ascend/pytorch/pull/40125 \
  --pr master=https://gitcode.com/Ascend/pytorch/pull/40130 \
  --project-id 7404318 \
  --out outputs/pr-data
```

生成后查看：

```text
outputs/.../summary.json
outputs/.../data_report.md
outputs/.../raw/
```

## 依赖

脚本只依赖 Python 标准库，不需要安装第三方包。

建议环境：

- Python 3.9+
- 可访问 `https://gitcode.com`

## 采集模式

脚本启动时会先尝试读取 token：

1. `GITCODE_ACCESS_TOKEN`
2. `gitcode_access_token`

如果 token 存在且非空，进入 `token-enhanced` 模式；否则进入 `no-token` 模式。

### no-token 模式

不带 Cookie，只使用完整 SPA 请求头访问公开接口。

适合：

- 公开仓库
- 公开 issue
- 公开 PR
- 不方便配置 token 的环境

风险：

- 私有仓库或受限 issue 通常无法访问
- 公开接口策略变化后可能返回 `401`、`403`、`418` 或 `429`
- 某些登录态字段、评论流、操作记录可能缺失
- 无法区分部分场景下的“无权限”和“不存在”

### token-enhanced 模式

优先使用：

```text
Cookie: GITCODE_ACCESS_TOKEN=...
```

如果带 Cookie 请求失败，脚本会自动退回无 Cookie 请求。

适合：

- 私有或受限资源
- 公开接口偶发失败
- 需要更稳定或更完整的登录态数据

不要使用 `Authorization: Bearer` 调用 GitCode issue API v5；实测该方式可能返回 `401 token not found`。

## 环境变量

可选变量：

```bash
export GITCODE_ACCESS_TOKEN='...'
export GITCODE_USER_AGENT='Mozilla/5.0 (...) Chrome/... Safari/...'
export GITCODE_ACCEPT_LANGUAGE='zh-CN,zh;q=0.9,en;q=0.8'
```

Windows PowerShell：

```powershell
$env:GITCODE_ACCESS_TOKEN = "..."
$env:GITCODE_USER_AGENT = "Mozilla/5.0 (...) Chrome/... Safari/..."
$env:GITCODE_ACCEPT_LANGUAGE = "zh-CN,zh;q=0.9,en;q=0.8"
```

安全约定：

- 不要把 token 写入命令历史、报告、仓库或日志
- 脚本只记录 token 是否存在，不输出 token 明文
- 如果 token 曾经暴露，应在 GitCode 重新刷新

## User-Agent 策略

脚本不会固定使用过短的 `Mozilla/5.0`。选择顺序：

1. `GITCODE_USER_AGENT`
2. `HTTP_USER_AGENT`
3. 按系统自动选择完整 Chrome UA

默认 `Accept-Language`：

```text
zh-CN,zh;q=0.9,en;q=0.8
```

默认不伪造 `sec-ch-ua*`，避免和真实运行环境不一致。

## 输出说明

`summary.json`：结构化采集结果，包括：

- collection mode
- User-Agent 来源
- issue 状态、标题、正文长度
- issue 关联 PR 数量
- PR 标题、源/目标分支、patch/internal HTTP 状态
- labels、close issue checkbox、commit/file 信息

`data_report.md`：面向人工和 Agent 的数据摘要。

`raw/`：保存原始 `.patch`、PR internal JSON、issue JSON 和 issue 关联 PR JSON，方便复核。

## Claude Code 使用

可以把 `examples/claude-code-command.md` 作为 Claude Code custom command 的内容。

建议流程：

1. 让 Claude Code 读取 `SKILL.md`
2. 运行 `scripts/gitcode_fetch.py`
3. 基于 `data_report.md`、`summary.json` 和 `raw/` 执行 `SKILL.md` 中的检查清单
4. 输出最终 PR 审核报告

## 普通 Agent 使用

不支持 Codex skill 的环境可以使用 `examples/generic-prompt.md`。

最小提示词：

```text
Read SKILL.md, run scripts/gitcode_fetch.py with the issue/PR URLs, then use generated artifacts to produce the review report. Never print token values.
```

## 常用参数

```text
--issue ISSUE_URL              指定 issue，可重复
--pr LABEL=PR_URL              指定 PR，可重复；LABEL 可为分支名
--project-id PROJECT_ID        PR internal API 的 project id，Ascend/pytorch 为 7404318
--out OUT                      输出目录
--timeout SECONDS              请求超时
--no-discover-prs              不从 issue 自动发现关联 PR
```

## 故障排查

`issue 正文为空`：

- 检查 `data_report.md` 中 HTTP 状态
- 尝试配置 `GITCODE_ACCESS_TOKEN`
- 确认 issue 是否公开可见

`关联 PR 为空`：

- 检查 `/pull_requests` 原始响应
- 尝试 token-enhanced 模式
- 如果用户已显式提供 PR，可继续通过 PR 描述反向确认 issue

`PR internal 失败`：

- `.patch` 仍可提供 diff、commit 和文件列表
- 但标题、描述、标签、close issue checkbox 可能缺失
- 尝试 token-enhanced 模式或稍后重试

`418/429/WAF/限流`：

- 降低并发或稍后重试
- 设置真实浏览器 `GITCODE_USER_AGENT`
- 使用 token-enhanced 模式

## 审核边界

本包只做数据采集和规则化审核，不运行 PR 中的代码。最终结论应基于：

- `SKILL.md` 检查清单
- GitCode API / patch 原始证据
- 必要的人工判断
