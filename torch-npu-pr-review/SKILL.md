---
name: torch-npu-pr-review
description: 审核 Ascend torch-npu PR，支持单PR审核和多PR批量审核+跨分支对比，基于验收标准规范、其他要求规范和注意点进行逐项检查，输出检验报告。
---

# Torch NPU PR Review Skill — Ascend torch-npu 社区 PR 审核

> **执行模式：全自动运行**。本 skill 调用后应一次性完成所有数据收集、分析和报告生成，**不需要**逐步骤向用户确认权限，不需要用户手动介入。如果某个数据源无法访问，自动降级使用替代数据源，并在报告中标注数据来源。

## 使用方式

### 单 PR 审核
```
/torch-npu-pr-review https://gitcode.com/Ascend/pytorch/pull/33888
```

### 多 PR 批量审核（跨分支对比）
```
/torch-npu-pr-review \
  https://gitcode.com/Ascend/pytorch/pull/33888 v2.7.1 \
  https://gitcode.com/Ascend/pytorch/pull/33889 v2.9.0 \
  https://gitcode.com/Ascend/pytorch/pull/33890 v2.10.0
```

每个 PR 链接后跟对应的目标分支名，用于跨分支对比。

也可以不指定分支名，仅提供多个 PR 链接，skill 会从每个 PR 的目标分支自动推断：
```
/torch-npu-pr-review \
  https://gitcode.com/Ascend/pytorch/pull/33888 \
  https://gitcode.com/Ascend/pytorch/pull/33889
```

### 通用包入口（Codex / Claude Code / 普通终端）

本目录也可以作为通用包分发，不依赖 Codex skill 机制。其他 Agent 或终端环境优先运行内置数据采集脚本，再根据本文件的检查清单生成审核报告：

```bash
python scripts/gitcode_fetch.py \
  --issue https://gitcode.com/Ascend/pytorch/issues/2612 \
  --project-id 7404318 \
  --out outputs/issue-2612-data
```

也可以显式传入 PR：

```bash
python scripts/gitcode_fetch.py \
  --pr v2.7.1=https://gitcode.com/Ascend/pytorch/pull/40125 \
  --pr master=https://gitcode.com/Ascend/pytorch/pull/40130 \
  --out outputs/pr-data
```

脚本会自动选择 `token-enhanced` 或 `no-token` 模式，自动适配 User-Agent，保存 `summary.json`、`data_report.md` 和 `raw/` 原始响应。Claude Code 可参考 `examples/claude-code-command.md`；不支持 skill 的任意 Agent 可参考 `examples/generic-prompt.md`。

---

## 重要前提

- **本 skill 只检查代码格式和内容是否符合规范，不运行代码**
- 检查范围：PR 描述、提交信息、代码 diff、文件结构
- 如果某项检查需要更多信息但 PR 中未体现，在报告中标注「无法判断」
- **多 PR 模式下，额外执行跨分支对比检查**

---

## 审核范围

本 skill 的审核范围限定于 **Ascend torch-npu 的 API 用例开发与 API 情况说明**。具体包括：

| 在审核范围内 ✅ | 不在审核范围内 ❌ |
|-----------------|-------------------|
| `test/` 目录下的测试用例新增/修改 | 子模块更新（如 `third_party/op-plugin`） |
| `test_upstream/` 目录下的 patch 及测试 | CI 配置文件修改（`.gitlab-ci.yml` 等） |
| `docs/zh/native_apis` 文档变更 | 构建脚本/工具链变更 |
| `torch_npu/` 路径下的 API 实现补齐 | 纯版本号/分支管理操作 |
| PR 描述中涉及 API 功能说明/用例情况 | 其他明显不涉及 API 测试用例的 PR |

### 范围判定规则

在数据收集完成后（获取到 `.patch` / `.diff` 后），立即按以下规则判定：

1. **在范围内**：diff 中的改动文件包含 `test/` 路径、`test_upstream/` 路径、`docs/zh/native_apis` 路径，或 `torch_npu/` 路径下的 API 实现代码
2. **不在范围内**：改动文件仅涉及 `third_party/`、`.gitlab-ci.yml`、`CMakeLists.txt`、`setup.py`、构建脚本、子模块指针等非 API 测试/文档/实现文件

### 范围外 PR 的处理

如果判定 PR **不在审核范围内**，**立即停止后续检查**，不生成完整报告。直接告知用户：

```
PR #xxx（{PR_TITLE}）不在本 skill 的审核范围内。

改动内容：{简述改动文件和类型}
审核范围：API 用例开发（test/、test_upstream/）、API 文档（docs/zh/native_apis）、API 实现（torch_npu/）

该 PR 属于 {子模块更新 / CI 配置 / 构建脚本 / ...} 类型的变更，无需进行 API 测试用例规范审核。
```

**不再**执行检查清单、**不生成**报告文件。

---

## GitCode 平台数据采集策略（非常重要）

GitCode 是一个 SPA（客户端渲染）平台，且 API 受 CloudWAF 保护。**不同端点可达性不同**，信息收集时必须按以下策略降级：

### 数据源可达性

| 数据源 | URL 格式 | 可达性 | 能获取的信息 |
|--------|----------|--------|------------|
| **`.patch` 端点** | `{PR_URL}.patch` | ✅ 始终可用 | commit 作者/邮箱/日期/消息、完整 diff、文件列表、commit 数量 |
| **PR internal API v1** | `/api/v1/projects/{repoId}/merge_requests/{iid}/internal` | ✅ 通常无需 token；必须带完整 SPA 请求头 | PR 标题、描述、源/目标分支、作者、CLA/CI 标签、是否勾选关闭 issue |
| **`.diff` 端点** | `{PR_URL}.diff` | ✅ 始终可用 | 纯 diff 内容（无 commit 元信息） |
| **`git fetch` MR ref** | `git fetch {repo} refs/merge-requests/{id}/head` | ✅ 通常可用 | commit 元数据、文件列表、diff |
| **Issue API v5** | `/api/v5/repos/{owner}/{repo}/issues/{iid}` | ✅ 带 `GITCODE_ACCESS_TOKEN` Cookie 时可用；无 Cookie 时可尝试公开 SPA 请求 | issue 标题、正文、状态等 |
| **Issue 关联 PR API v5** | `/api/v5/repos/{owner}/{repo}/issues/{iid}/pull_requests` | ✅ 公开 issue 通常无 Cookie 可用；token 增强模式优先带 Cookie | issue 关联 PR 列表、PR 编号、标题、源/目标分支 |
| **PR 页面 (HTML)** | `{PR_URL}` | ❌ SPA 壳 | 只有 `<div id="app"></div>`，无实际内容 |
| **API v4 端点** | `api/v4/projects/.../merge_requests/...` | ❌ WAF 拦截或不兼容 | 不可用 |
| **WebFetch 工具** | `{PR_URL}` | ❌ gitcode.com 未通过域名验证 | 不可用 |

### 模式选择（先于任何 API 调用）

执行数据采集前，先尝试从运行进程可见的环境变量读取 `GITCODE_ACCESS_TOKEN`，兼容小写 `gitcode_access_token`。只判断是否存在和长度，不打印 token 明文。

- **Token 增强模式**：如果 token 存在且非空，构造 `Cookie: GITCODE_ACCESS_TOKEN={token}`，后续 GitCode API 请求优先带 Cookie；如果某个端点带 Cookie 失败，再退回无 Cookie SPA 请求。
- **无 token 模式**：如果 token 获取不到或为空，所有 GitCode API 请求使用完整 SPA 请求头但不带 Cookie；公开 issue、公开关联 PR 和 PR internal 通常仍可获取。
- `.patch` / `.diff` 端点始终可以并行请求，不依赖 token。
- 不要把 `GITCODE_ACCESS_TOKEN` 放到报告、日志、错误信息或命令输出中。

### 请求头自适应（先于任何 API 调用）

不要固定使用过短的 `User-Agent: Mozilla/5.0`。先按以下顺序生成请求头：

1. 优先读取 `GITCODE_USER_AGENT`；为空时读取 `HTTP_USER_AGENT`。
2. 如果仍为空，按运行系统选择默认完整浏览器 UA：
   - Windows：`Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36`
   - macOS：`Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36`
   - Linux：`Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36`
3. `Accept-Language` 优先读取 `GITCODE_ACCEPT_LANGUAGE`，为空时使用 `zh-CN,zh;q=0.9,en;q=0.8`。
4. 默认不要伪造 `sec-ch-ua*` 请求头；这些值和真实运行环境不一致时反而可能降低可信度。

Bash/zsh 模式选择示例：
```bash
token="${GITCODE_ACCESS_TOKEN:-${gitcode_access_token:-}}"
cookie_header=()
mode="no-token"
if [ -n "$token" ]; then
  cookie_header=(-H "Cookie: GITCODE_ACCESS_TOKEN=$token")
  mode="token-enhanced"
fi

ua="${GITCODE_USER_AGENT:-${HTTP_USER_AGENT:-}}"
if [ -z "$ua" ]; then
  case "$(uname -s 2>/dev/null)" in
    Darwin*) ua="Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36" ;;
    Linux*) ua="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36" ;;
    *) ua="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36" ;;
  esac
fi
accept_language="${GITCODE_ACCEPT_LANGUAGE:-zh-CN,zh;q=0.9,en;q=0.8}"
```

PowerShell 模式选择示例：
```powershell
$token = $env:GITCODE_ACCESS_TOKEN
if (-not $token) { $token = $env:gitcode_access_token }
$cookieHeader = @()
$mode = "no-token"
if ($token) {
  $cookieHeader = @("-H", "Cookie: GITCODE_ACCESS_TOKEN=$token")
  $mode = "token-enhanced"
}

$ua = $env:GITCODE_USER_AGENT
if (-not $ua) { $ua = $env:HTTP_USER_AGENT }
if (-not $ua) {
  if ($IsMacOS) {
    $ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
  } elseif ($IsLinux) {
    $ua = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
  } else {
    $ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
  }
}
$acceptLanguage = $env:GITCODE_ACCEPT_LANGUAGE
if (-not $acceptLanguage) { $acceptLanguage = "zh-CN,zh;q=0.9,en;q=0.8" }
```

### 数据收集流程（按模式自动降级）

**第一优先：`.patch` 端点**（最重要，一次性获取最多信息）
```bash
curl -sL -H "User-Agent: $ua" -H "Accept-Language: $accept_language" "{PR_URL}.patch" -o /tmp/pr_{id}.patch
```
从 `.patch` 中提取：
- 提交者 ID（`From:` 行）
- 提交者邮箱（`From:` 行第二个字段）
- PR 标题（`Subject:` 行）
- 目标分支（从 commit message 中推断，如「for v2.7.1」）
- Commit 数量（统计 patch 中的 `From:` 行数）
- 改动文件列表（`--- a/...` / `+++ b/...` 行）
- 完整 diff 内容

**第二优先：PR internal API v1（token 增强模式优先带 Cookie；无 token 模式直接公开请求）**

GitCode 的 PR internal API 端点 `/api/v1/projects/{repoId}/merge_requests/{iid}/internal` 可以返回 PR 元数据和 PR 描述。实测在未配置 `GITCODE_ACCESS_TOKEN` 时，只要携带完整 SPA 请求头，也可以返回 200。该端点应与 `.patch` 并行请求：`.patch` 用于 diff 分析，PR internal API 用于标题、描述、分支、作者、标签和 checkbox。

> **WAF 绕过配方**：必须携带自适应的完整 `User-Agent` + `Accept-Language` + `Accept` + `X-Requested-With` + `Origin` + `Referer` + `sec-fetch-mode: cors` + `sec-fetch-site: same-origin`。缺少关键请求头可能触发 418 或空响应。

> **运行器无关约定**：本 skill 不依赖 Codex、Claude Code 或任何特定 Agent。先按「模式选择」得到 `$cookie_header` / `$cookieHeader`：token 增强模式优先带 `Cookie: GITCODE_ACCESS_TOKEN=...` 调用；如果返回 401/403/418 或内容为空，再无 Cookie 重试一次。不要在报告、日志或错误信息中打印 token 明文。

```bash
# Ascend/pytorch 的 project ID 已知为 7404318
# bash/zsh 示例：token 增强模式先带 Cookie；失败时退回无 Cookie
api_url="https://gitcode.com/api/v1/projects/7404318/merge_requests/{pr_number}/internal"
referer="https://gitcode.com/Ascend/pytorch/pull/{pr_number}"

PR_DATA=$(curl -sS -L \
  -H "User-Agent: $ua" \
  -H "Accept-Language: $accept_language" \
  -H "Accept: application/json, text/plain, */*" \
  -H "X-Requested-With: XMLHttpRequest" \
  -H "Origin: https://gitcode.com" \
  -H "Referer: $referer" \
  -H "sec-fetch-mode: cors" \
  -H "sec-fetch-site: same-origin" \
  "${cookie_header[@]}" \
  "$api_url")

if [ "${#cookie_header[@]}" -gt 0 ] && printf '%s' "$PR_DATA" | grep -Eq '^(|.*"message":|"status":(401|403|418))'; then
  PR_DATA=$(curl -sS -L \
    -H "User-Agent: $ua" \
    -H "Accept-Language: $accept_language" \
    -H "Accept: application/json, text/plain, */*" \
    -H "X-Requested-With: XMLHttpRequest" \
    -H "Origin: https://gitcode.com" \
    -H "Referer: $referer" \
    -H "sec-fetch-mode: cors" \
    -H "sec-fetch-site: same-origin" \
    "$api_url")
fi

# 响应字段：title, description, source_branch, target_branch, state,
#           author.username, enterprise_labels, close_issue_when_merge
```

Windows PowerShell 示例（优先使用 `curl.exe`，不要优先使用 `Invoke-WebRequest`，它在 GitCode JSON 请求上可能偶发空引用异常）：
```powershell
$pr = "{pr_number}"
$apiUrl = "https://gitcode.com/api/v1/projects/7404318/merge_requests/$pr/internal"
$referer = "https://gitcode.com/Ascend/pytorch/pull/$pr"
$headers = @(
  "-H", "User-Agent: $ua",
  "-H", "Accept-Language: $acceptLanguage",
  "-H", "Accept: application/json, text/plain, */*",
  "-H", "X-Requested-With: XMLHttpRequest",
  "-H", "Origin: https://gitcode.com",
  "-H", "Referer: $referer",
  "-H", "sec-fetch-mode: cors",
  "-H", "sec-fetch-site: same-origin"
)

$PR_DATA = & curl.exe -sS -L @headers @cookieHeader $apiUrl
if ($cookieHeader.Count -gt 0 -and ($LASTEXITCODE -ne 0 -or -not $PR_DATA)) {
  $PR_DATA = & curl.exe -sS -L @headers $apiUrl
}
```

**PR internal API 每个 PR 最多 2 次调用**：token 增强模式先带 Cookie，失败时再无 Cookie；无 token 模式只调用 1 次无 Cookie SPA 请求。该端点返回 PR 描述，但 `linked_issues`/`e2e_issues` 可能为空；关联 issue 通常需要从 PR 描述中的 issue URL 或 `#数字` 提取。

**第三优先：`.diff` 端点**（当 .patch 不够时补充）
```bash
curl -sL -H "User-Agent: $ua" -H "Accept-Language: $accept_language" "{PR_URL}.diff" -o /tmp/pr_{id}.diff
```

**第四优先：`git fetch`**（验证 commit 元数据）
```bash
git init /tmp/pr_{id} && cd /tmp/pr_{id}
git fetch --depth=1 {repo_url} refs/merge-requests/{id}/head
git log FETCH_HEAD --format="%H%n%an%n%ae%n%s" -1
```

### Issue 内容与关联 PR 获取（按模式执行）

当用户提供 issue 链接，或 PR internal 响应/PR 描述中出现 `#123`、`https://gitcode.com/.../issues/123` 时，按以下顺序处理：

1. 从 issue URL、PR 描述、`linked_issues[].iid`、`linked_issues[].number`、`linked_issues[].id`、`e2e_issues` 提取 issue iid，并记录「已关联 issue #xxx」。
2. 用 `GET https://gitcode.com/api/v5/repos/{owner}/{repo}/issues/{issue_iid}` 获取 issue 正文。token 增强模式先带 `$cookie_header` / `$cookieHeader`；如果失败或字段缺失，再无 Cookie 重试。无 token 模式直接无 Cookie 请求。
3. 用 `GET https://gitcode.com/api/v5/repos/{owner}/{repo}/issues/{issue_iid}/pull_requests` 获取关联 PR。token 增强模式同样先带 Cookie，失败再无 Cookie；无 token 模式直接无 Cookie 请求。该接口可返回 PR `number`、`title`、`state`、`html_url`、`base.ref`、`head.ref`。
4. 如果 issue 正文接口和关联 PR 接口都不可用，才从已提供 PR 的描述中反向提取 issue 编号并继续审核；不要把 issue API 失败误判为未关联 issue。
5. 如果 `api/v5` 带 Cookie 和无 Cookie 均失败，才可把旧的 `api/v1/projects/{repoId}/issues/{issue_iid}` 与 `/internal` 作为兼容性兜底尝试；这些 v1 issue 路径常见 `404 NOT_PATH`。
6. issue 正文优先读取 `body`，其次读取 `description`、`content`、`issue.body`、`issue.description`；标题优先读取 `title`。
7. 如果 issue 详情接口 401/403/404/418，报告中写明「已识别关联 issue，但无法获取 issue 正文（HTTP 状态码：xxx）」。如果关联 PR 接口失败，写明「无法获取 issue 关联 PR（HTTP 状态码：xxx）」。

PowerShell issue 详情示例：
```powershell
$issueUrl = "https://gitcode.com/api/v5/repos/Ascend/pytorch/issues/{issue_iid}"
$pullsUrl = "https://gitcode.com/api/v5/repos/Ascend/pytorch/issues/{issue_iid}/pull_requests"

$issueJson = & curl.exe -sS -L @headers @cookieHeader $issueUrl
if ($cookieHeader.Count -gt 0 -and ($LASTEXITCODE -ne 0 -or -not $issueJson)) {
  $issueJson = & curl.exe -sS -L @headers $issueUrl
}

$pullsJson = & curl.exe -sS -L @headers @cookieHeader $pullsUrl
if ($cookieHeader.Count -gt 0 -and ($LASTEXITCODE -ne 0 -or -not $pullsJson)) {
  $pullsJson = & curl.exe -sS -L @headers $pullsUrl
}

$issue = $issueJson | ConvertFrom-Json
$issueDescription = $issue.body
if (-not $issueDescription) { $issueDescription = $issue.description }
if (-not $issueDescription) { $issueDescription = $issue.content }
$linkedPrs = $pullsJson | ConvertFrom-Json
```

**API 不可用时降级**：PR internal 在 token 增强模式下先带 Cookie，失败后无 Cookie 重试；仍失败时降级到 `.patch` 模式，并标注具体原因。issue 正文和关联 PR 也按相同模式执行；仍失败时只标注对应数据无法获取，不影响 PR 审核继续执行。

**无需尝试**：PR 页面 HTML（SPA 壳）、WebFetch 工具、`/api/v4/` 路径、PAT token 认证、issue API v5 的 `Authorization: Bearer` 认证。

### 数据获取能力矩阵

| 信息 | 无 token 模式 | Token 增强模式 |
|------|--------------------------------------------|----------------|
| PR 标题 | ✅ PR internal 无 Cookie；失败时用 commit subject | ✅ PR internal 带 Cookie；失败时退回无 Cookie |
| PR 描述正文 | ✅ PR internal 无 Cookie | ✅ PR internal 带 Cookie；失败时退回无 Cookie |
| 提交者 ID/邮箱 | ✅ `.patch` 的 `From:` + PR internal author | ✅ 同无 token 模式 |
| 目标分支 | ✅ PR internal 无 Cookie | ✅ PR internal 带 Cookie；失败时退回无 Cookie |
| 源分支名称 | ✅ PR internal 无 Cookie | ✅ PR internal 带 Cookie；失败时退回无 Cookie |
| Commit 数量 | ✅ 统计 `.patch` 中的 `From` 行 | ✅ 同无 token 模式 |
| 改动文件列表 | ✅ `.patch` / `.diff` 路径 | ✅ 同无 token 模式 |
| 关联 issue 编号 | ✅ issue API v5、关联 PR API v5、PR 描述 issue URL / `#数字` | ✅ 同无 token 模式，优先带 Cookie |
| 关联 issue 正文 | ✅ `api/v5` 无 Cookie SPA 请求；失败时标注 HTTP 状态 | ✅ `api/v5` + `Cookie: GITCODE_ACCESS_TOKEN=...`；失败时退回无 Cookie |
| issue 关联 PR | ✅ `/api/v5/repos/{owner}/{repo}/issues/{iid}/pull_requests` 无 Cookie 请求 | ✅ 同端点优先带 Cookie；失败时退回无 Cookie |
| CLA 签署状态 | ✅ PR internal `enterprise_labels`，如 `ascend-cla/yes` | ✅ PR internal 带 Cookie；失败时退回无 Cookie |
| CI 标签 | ✅ PR internal `enterprise_labels` | ✅ PR internal 带 Cookie；失败时退回无 Cookie |
| PR 评论 / /sync | ❌ 默认不获取评论流 | ⚠️ 需额外 discussions/notes API |
| PR 模板 checkbox | ✅ 从 PR 描述解析 checkbox；关闭 issue 也可看 `close_issue_when_merge` | ✅ PR internal 带 Cookie；失败时退回无 Cookie |

### 信息获取状态标注

在报告中，根据数据来源标注：

| 标注 | 含义 |
|------|------|
| **⚠️ 无法判断（PR internal 不可用）** | PR internal API 失败，且 `.patch` 无法提供该字段 |
| **⚠️ 无法判断（需额外 API）** | 需要评论流、讨论记录等默认采集未覆盖的数据 |
| **⚠️ 无法判断（需人工确认）** | 需要上下文判断但信息不足 |
| **⚠️ 无法获取 issue 正文（HTTP xxx）** | 已识别关联 issue，但 issue 详情接口请求失败；不能等同于未关联 issue |
| **⚠️ 无法获取 issue 关联 PR（HTTP xxx）** | 已识别 issue，但关联 PR 接口请求失败；可继续从用户提供的 PR 或 PR 描述中反向确认 |

### 如何配置 GITCODE_ACCESS_TOKEN（通用）

> GITCODE_ACCESS_TOKEN 是浏览器登录后的 JWT，**不是** PAT（Personal Access Token）。Issue API v5 使用它时应放入 `Cookie: GITCODE_ACCESS_TOKEN=...`，不要放入 `Authorization: Bearer ...`。

1. 在浏览器登录 https://gitcode.com
2. 按 `F12` → **Application** → **Cookies** → `.gitcode.com`
3. 找到 `GITCODE_ACCESS_TOKEN`，复制其值
4. 将 token 放到运行 skill 的进程可见的环境变量 `GITCODE_ACCESS_TOKEN` 中。推荐优先使用环境变量或 Secret 管理，不要把 token 写进 skill 文件、报告、仓库代码或命令历史。

   Linux/macOS bash/zsh：
   ```bash
   export GITCODE_ACCESS_TOKEN='eyJhbGciOiJIUzUxMiJ9...'
   ```

   Windows PowerShell（当前会话）：
   ```powershell
   $env:GITCODE_ACCESS_TOKEN = "eyJhbGciOiJIUzUxMiJ9..."
   ```

   Windows PowerShell（用户级环境变量，设置后需重启运行器/终端）：
   ```powershell
   [Environment]::SetEnvironmentVariable("GITCODE_ACCESS_TOKEN", "eyJhbGciOiJIUzUxMiJ9...", "User")
   ```
   
   Claude Code（如使用 settings 注入 env）：
   ```json
   "GITCODE_ACCESS_TOKEN": "eyJhbGciOiJIUzUxMiJ9..."
   ```

   Codex 或其他桌面/IDE Agent：在启动该 Agent 的系统环境、终端环境、Agent 配置或 Secret 面板中设置同名环境变量，并重启 Agent，使新环境变量进入运行进程。

   CI/CD：使用平台的 secret/env 功能注入同名变量，例如 GitHub Actions 的 `${{ secrets.GITCODE_ACCESS_TOKEN }}` 或 GitLab CI 的 masked variable。
5. Token 过期后（通常几个月），重新从浏览器提取

> 已有 `GITCODE_TOKEN`（PAT）字段保留但仅用于公开 API，不影响 PR 审查。
> 执行审核前只检查 token 是否存在，不输出 token 值：PowerShell 使用 `if ($env:GITCODE_ACCESS_TOKEN) { "SET" } else { "NOT_SET" }`，bash/zsh 使用 `echo ${GITCODE_ACCESS_TOKEN:+SET}`。

---

## 执行流程

> **关键：执行时在单条消息中发起所有独立的 curl 调用（并行），收集完数据后直接完成检查并生成报告，中间不需要用户确认。**

### 阶段-1：采集模式选择

1. 尝试读取 `GITCODE_ACCESS_TOKEN`，若为空再读取 `gitcode_access_token`。
2. 如果 token 存在且非空，进入 **Token 增强模式**，构造 `Cookie: GITCODE_ACCESS_TOKEN=...`，后续 GitCode API 优先带 Cookie。
3. 如果 token 不存在或为空，进入 **无 token 模式**，后续 GitCode API 只带完整 SPA 请求头。
4. 不输出 token 明文，只可在必要时记录模式名：`token-enhanced` 或 `no-token`。

### 阶段〇：范围判定（数据收集后立即执行）

**在完成数据收集后，执行任何检查清单之前**，首先判定 PR 是否在审核范围内：

1. 检查 `.patch` / `.diff` 中的改动文件路径
2. 对照「审核范围」节进行判定
3. **如果在范围内**：继续执行阶段二
4. **如果不在范围内**：**立即停止**，按「范围外 PR 的处理」格式告知用户，**不执行后续检查、不生成报告文件**

### 阶段一：信息收集（全自动、并行执行）

对每个 PR，按以下优先级收集数据：

1. **并行**获取 `.patch`（用于 diff 分析）和 PR internal API（用于 PR 元数据、描述、分支、标签、checkbox）。PR internal API 按阶段-1 的模式请求：Token 增强模式先带 Cookie，失败后无 Cookie 重试；无 token 模式直接无 Cookie 请求。
2. 从 PR internal API 获取：PR 标题、描述、源/目标分支、state、author、enterprise_labels、close_issue_when_merge。
3. 从 `.patch` 获取：完整 diff、commit 数量、提交者邮箱、文件列表；当 PR internal 不可用时，用 `.patch` 补充标题等可推断元数据。
4. 如果存在关联 issue，调用 `api/v5/repos/{owner}/{repo}/issues/{iid}` 获取 issue 正文，并调用 `api/v5/repos/{owner}/{repo}/issues/{iid}/pull_requests` 获取 issue 关联 PR；两个端点都按阶段-1 的模式请求。失败时保留 issue 编号并标注失败原因。

**不再尝试**：WebFetch（域名限制）、PR 页面 HTML（SPA 壳）、`/api/v4/`、issue API v5 的 Bearer 认证。

### WAF 限流处理

CloudWAF 通过检查 `sec-fetch-*` 等浏览器安全头来区分合法 SPA 请求和外部调用。API 请求必须携带完整的 SPA 模拟头；如果仍触发 418，记录状态码并降级。PR internal 每个 PR 在无 token 模式调用 1 次，在 token 增强模式最多调用 2 次（带 Cookie、无 Cookie）。issue 正文和关联 PR 仅在识别到关联 issue 后按 issue 数量调用。

### 检查项判定能力（PR internal 不可用时）

代码 diff 可以覆盖大部分检查项，以下列出哪些项**可以不依赖 PR 描述**直接判定：

**无需 PR 描述即可判定**：
- 1.1（是否 test_upstream）→ 看 diff 路径
- 1.6（合入路径一致性）→ 对比 diff 路径与 pytorch 社区
- 1.7 代码部分（API 功能/用例完整性）→ 看 diff 代码
- 2.1（是否更新文档）→ 看 diff 是否含 docs 文件
- 2.4（私有接口资料）→ 看 API 名称是否带下划线前缀
- 3.1（是否涉及 API 补齐）→ 看 diff 是否非测试代码
- 二.1-5, 8.1-8.10（代码规范）→ 全部从 diff 判定
- 三.2（grep 位置）→ 看 diff 中是否有搜索命令
- 三.4-5（大文件）→ 看 diff 文件大小

**确实需要 PR 描述的项**（PR internal 不可用且 `.patch` 无法提供时才标注为无法判断）：
- 1.5（社区用例情况说明）
- 1.7 描述部分（运行日志）
- 2.2-2.3（资料支持说明）
- 3.2-3.5（运行日志、模板、issue 关联）
- 二.6-7（描述简洁性、/sync）
- 三.1（CLA）
- 三.3（分支管理说明）

### 阶段二：逐 PR 检查

对每个 PR 独立执行下列全部检查清单。代码层面检查直接基于 diff 完成；描述层面优先使用 PR internal API 返回的 `description`，只有 PR internal 不可用时才标记为「无法判断（PR internal 不可用）」。

### 阶段三（仅多 PR 模式）：跨分支对比

对所有 PR 进行横向对比，检查项见下方「跨分支对比检查」。

### 阶段四：生成报告

- **单 PR 模式**：生成一份报告，命名为 `{提交者ID}_{YYYY-MM-DD_HH-MM-SS}_review_report.md`
- **多 PR 模式**：生成一份汇总报告，命名为 `{提交者ID}_{YYYY-MM-DD_HH-MM-SS}_cross_branch_review_report.md`
- 报告直接输出到用户 home 目录或当前工作目录
- 在报告开头添加「数据来源说明」小节，清晰列出哪些数据来自哪个端点
- **在报告末尾生成「修改意见」小节**，将所有审核发现的问题转化为对 PR 提交者的具体修改指令，按类别分组（代码修改、描述补充、流程操作），每条使用祈使句式（如"请将 X 改为 Y"、"请在描述中补充 Z"），同类别内按严重程度排序

---

## 检查清单

### 一、验收标准规范检查

#### 1. 用例补齐检查

| # | 检查项 | 检查方法 |
|---|--------|----------|
| 1.1 | PR 是否涉及用例补齐（test_upstream 目录或有 .patch 文件） | 查看 PR 改动文件路径是否在 `test_upstream/` 下 |
| 1.2 | 若涉及 test_upstream patch，patch 路径是否与 pytorch 社区路径一一对应 | 对比 patch 文件名和路径是否与原 pytorch 社区文件路径一致 |
| 1.3 | 若 test_upstream 已有相关 patch，PR 中是否有说明原 patch 不合理的理由 | 检查 PR 描述是否包含对旧 patch 的分析 |
| 1.4 | 若无需提交 PR（仅 issue 说明），PR/issue 中是否有完整说明 | 检查说明是否包含 API 功能、用例完备性、适配方案、运行结果 |
| 1.5 | 若是新增用例（test 目录而非 test_upstream），PR 描述是否说明了社区用例情况及新增必要性 | 检查 PR 描述中是否有「社区用例情况」「是否确实缺失」「验证是否充分」等说明 |
| 1.6 | 新增用例的合入路径是否和 pytorch 社区一致 | 对比新增文件路径是否与 pytorch 官方社区对应 API 的路径一致 |
| 1.7 | 用例是否覆盖必需内容：API 功能、用例完整性、NPU 适配、运行日志 | 检查代码和 PR 描述 |

#### 2. 资料补齐检查

| # | 检查项 | 检查方法 |
|---|--------|----------|
| 2.1 | 若 PR 涉及 API 功能变更/新增，是否同步更新了 `docs/zh/native_apis` 下的文档 | 检查 diff 中是否有文档文件变更 |
| 2.2 | PR 描述中是否说明了资料支持情况 | 搜索 PR 描述中是否有「资料」「文档」「docs」相关说明 |
| 2.3 | 是否有「不涉及」三个字的敷衍说明 | 若出现「不涉及」且无进一步解释，标记为不合规 |
| 2.4 | PyTorch 私有接口是否被错误地要求补充资料 | 检查涉及的 API 是否为私有接口（私有接口不需要补充资料） |

#### 3. API 补齐检查

| # | 检查项 | 检查方法 |
|---|--------|----------|
| 3.1 | 若 PR 涉及 API 补齐，是否给出了补齐思路 | 检查 PR 描述中是否有适配方案说明 |
| 3.2 | 是否包含运行日志 | 检查 PR 描述中是否附有运行日志 |
| 3.3 | 是否使用了社区 PR 模板 | 检查 PR 描述是否符合社区模板格式 |
| 3.4 | 是否关联了对应 issue | 检查 PR 中是否有 `#issue编号` 或 issue 链接 |
| 3.5 | 是否勾选「PR 合入则关闭 issue」 | 检查 PR 描述中的 checkbox |
| 3.6 | 如果不需要提交 PR，issue 中是否有详细说明 | 仅在无需 PR 时检查 |

---

### 二、其他要求规范检查

| # | 检查项 | 检查方法 | 严重程度 |
|---|--------|----------|----------|
| 1 | 代码注释是否精简且使用英文 | 抽查 diff 中的注释 | 一般 |
| 2 | 同一 PR 是否有多次提交（应合并为一次） | 查看 PR 的 commit 数量 | 重要 |
| 3 | 新增用例中的张量是否运行在 NPU 上 | 检查代码中是否有 `device_type = acc.type if (acc := torch.accelerator.current_accelerator()) else "cpu"` 或 `.to(device_type)` 或 `.npu()` | 重要 |
| 4 | PR 或 issue 中 API 名字是否使用全名 | 检查描述文字中 API 名称是否完整（如 `torch.nn.Parameter` 而非 `Parameter`） | 一般 |
| 5 | Patch 是否由 git diff 生成（严禁手动修改 patch） | 检查 patch 文件格式是否为标准 git diff 格式 | 重要 |
| 6 | PR 描述是否在说清楚的基础上尽量简洁 | 人工判断，有无不必要的内容 | 一般 |
| 7 | PR 提交后是否使用了 /sync | 检查 PR 评论/操作记录 | 一般 |
| 8.1 | 新增测试用例是否从 `torch.testing` 导入 `run_tests` | 检查代码 import 部分 | 重要 |
| 8.2 | 是否直接导入了 `unittest`（不应直接导入，run_tests 默认导入） | 检查代码 import 中是否有 `import unittest` | 重要 |
| 8.3 | 结果比对是否使用 `self.assert` | 检查测试方法中是否使用 `self.assert*` | 重要 |
| 8.4 | 是否有不必要的 `print` 日志 | 检查代码中是否有调试性 print 语句 | 一般 |
| 8.5 | 测试用例是否在功能验证充分前提下尽量简化 | 检查用例是否聚焦核心功能（有无冗余检测如检测 NPU/torch-npu 是否存在） | 一般 |
| 8.6 | 是否使用了 try-except 捕获异常 | 检查代码中是否有 `try: ... except: ...` 结构 | 重要 |
| 8.7 | 导入顺序是否正确：标准库 → 第三方库 → 自定义模块 | 检查 import 顺序：先 torch、再 torch.testing、最后 torch_npu | 重要 |
| 8.8 | 类前后是否空 2 行，类内方法前是否空 1 行 | 检查代码格式 | 一般 |
| 8.9 | 是否不需要导入 torch_npu（昇腾环境导入 torch 默认导入） | 检查是否有不必要的 `import torch_npu` | 一般 |
| 8.10 | 新增测试文件顶部是否有解释说明 | 检查文件开头是否有 docstring 说明功能，格式是否为可扩展描述 | 重要 |

---

### 三、注意点检查

| # | 检查项 | 检查方法 |
|---|--------|----------|
| 1 | 提交者邮箱是否已绑定 gitcode 并签署 CLA | 检查 PR 页面是否有 CLA 签署标识（无法判断时标注） |
| 2 | grep 搜索是否在正确的仓库（pytorch 官方而非 torch-npu） | 若 PR 描述提到搜索命令，检查是否指明在 pytorch 官方社区搜索 |
| 3 | 分支管理是否正确（是否 fork 了全部分支、是否一一对应合入） | 检查 PR 的目标分支是否正确 |
| 4 | 涉及大文件用例（如 test_nn.py）的 PR，是否注明了 API 用例在原文件中的行数范围 | 检查 PR 描述中是否有行数信息 |
| 5 | 涉及大文件 patch 修改的，patch 是否正确（先 apply 再修改再 git diff） | 检查 patch 是否完整、格式正确 |

---

### 四、跨分支对比检查（仅多 PR 模式）

根据文档要求（用例需提交到 2.7.1/2.9.0/2.10.0/2.11.0/2.12.0，master 视情况），跨分支对比检查以下项：

| # | 检查项 | 检查方法 |
|---|--------|----------|
| C1 | **分支覆盖完整性** — 需要覆盖的分支是否都已提交 PR | 检查 PR 列表是否覆盖了所有需要覆盖的目标分支（test_upstream 场景：2.7.1/2.9.0/2.10.0/2.11.0/2.12.0；test 目录场景：还需包含 master） |
| C2 | **改动一致性** — 各分支相同文件的改动是否一致（排除因版本差异导致的不一致） | 逐文件对比各分支 diff，标记出现差异的文件 |
| C3 | **Patch 差异合理性** — 若不同分支的 patch 内容不同，是否有说明原因（文档六.5：不同版本文件不同导致 patch 不同是合理的，但需确认是分别通过 git diff 生成的） | 对比各分支 patch 文件，若内容不同，检查 PR 描述是否说明了原因 |
| C4 | **分支命名规范性** — 各分支是否按规范命名（如 `test-xxx-2.7.1` 格式） | 检查每个 PR 的源分支名称 |
| C5 | **目标分支匹配** — 每个 PR 的目标分支是否与其改动内容匹配（2.7.1 分支的改动合入 2.7.1，master 合入 master） | 对比 PR 目标分支和文件改动是否对应 |
| C6 | **遗漏检查** — 是否有某个分支存在但缺少对应改动（如 2.9.0 有某个文件的改动但 2.10.0 没有） | 汇总所有分支的改动文件列表，交叉比对找出遗漏 |
| C7 | **多余检查** — 是否有不应该存在的分支提交（如 test_upstream 不需要 master，若 master 也提交了 test_upstream 则为多余） | 根据 PR 类型判断目标分支是否合理 |
| C8 | **描述一致性** — 各分支 PR 描述中的关键信息（API 名称、适配方案、issue 编号）是否一致 | 对比各 PR 的描述内容 |

---

## 报告模板

### 单 PR 报告模板

```markdown
# Ascend torch-npu PR 审核报告

**生成时间**：{YYYY-MM-DD HH:MM:SS}
**PR 链接**：{PR_URL}
**PR 标题**：{PR_TITLE}
**提交者 ID**：{SUBMITTER_ID}
**目标分支**：{TARGET_BRANCH}

---

> 📋 **数据来源**：{COLLECTION_MODE}（`token-enhanced` 或 `no-token`）
> - ✅ PR internal API：PR 标题、描述、源/目标分支、作者、CLA/CI 标签、关闭 issue checkbox；token 增强模式优先带 Cookie
> - ✅ `.patch` 端点：完整 diff、commit 验证、文件列表、提交者邮箱
> - ✅/⚠️ Issue API v5：issue 正文和关联 PR；失败时保留 issue 编号并标注 HTTP 状态码

---

## 一、验收标准规范

### 1. 用例补齐
| # | 检查项 | 结果 | 说明 |
|---|--------|------|------|
| 1.1 | ... | ✅ / ❌ / ⚠️ / N/A | ... |

### 2. 资料补齐
| # | 检查项 | 结果 | 说明 |
|---|--------|------|------|

### 3. API 补齐
| # | 检查项 | 结果 | 说明 |
|---|--------|------|------|

---

## 二、其他要求规范

| # | 检查项 | 严重程度 | 结果 | 说明 |
|---|--------|----------|------|------|

---

## 三、注意点

| # | 检查项 | 结果 | 说明 |
|---|--------|------|------|

---

## 总结

| 统计项 | 数量 |
|--------|------|
| 总检查项 | {N} |
| 通过 ✅ | {N} |
| 不通过 ❌ | {N} |
| 需关注 ⚠️ | {N} |
| 不适用 N/A | {N} |

### 必须修复的问题
1. {问题}

### 建议改进
1. {建议}

---

## 修改意见

> 以下是根据审核结果汇总的具体修改指令，请 PR 提交者逐条执行。

### 代码修改
1. {具体修改指令，如"请将 `test/fx/test_symbolic_shapes_api.py` 第 N 行的 `self.assertTrue(hasattr(...))` 改为 `if not hasattr(...): self.skipTest(...)` 模式，避免 API 不可用时直接失败"}
2. ...（如无需修改代码则写「无需修改」）

### 描述补充
1. {具体补充指令，如"请在 PR 描述中附上在 Ascend 设备上运行 `python test/fx/test_symbolic_shapes_api.py` 的完整输出日志"}
2. ...

### 流程操作
1. {具体操作指令，如"请在 PR 页面勾选「PR 合入则关闭 issue」checkbox"}
2. ...（如无需流程操作则写「无需操作」）

---

*本报告由 Torch NPU PR Review Skill 自动生成，仅检查格式和内容规范，未运行代码。*
```

### 多 PR 汇总报告模板

```markdown
# Ascend torch-npu 多 PR 跨分支审核报告

**生成时间**：{YYYY-MM-DD HH:MM:SS}
**提交者 ID**：{SUBMITTER_ID}
**涉及分支数**：{N}
**PR 列表**：
| 分支 | PR 链接 | PR 标题 |
|------|---------|---------|
| v2.7.1 | {URL} | {TITLE} |
| v2.9.0 | {URL} | {TITLE} |
| ... | ... | ... |

---

> 📋 **数据来源**：{COLLECTION_MODE}（`token-enhanced` 或 `no-token`）
> - ✅ PR internal API：PR 标题、描述、源/目标分支、作者、CLA/CI 标签、关闭 issue checkbox；token 增强模式优先带 Cookie
> - ✅ `.patch` 端点：完整 diff、commit 验证、文件列表、提交者邮箱
> - ✅/⚠️ Issue API v5：issue 正文和关联 PR；失败时保留 issue 编号并标注 HTTP 状态码

---

## 第一部分：各分支独立审核

### 1. v2.7.1 — {PR_URL}

#### 一、验收标准规范
（同单 PR 报告格式，每个分支一个章节）

#### 二、其他要求规范

#### 三、注意点

#### 小计
| 统计项 | 数量 |
|--------|------|
| 通过 ✅ | {N} |
| 不通过 ❌ | {N} |
| 需关注 ⚠️ | {N} |
| 不适用 N/A | {N} |

---

### 2. v2.9.0 — {PR_URL}
（同上）

---

（依次列出所有分支...）

---

## 第二部分：跨分支对比

| # | 检查项 | 结果 | 说明 |
|---|--------|------|------|
| C1 | 分支覆盖完整性 | ✅ / ❌ / ⚠️ | 缺少 {branches} 分支的 PR |
| C2 | 改动一致性 | ✅ / ❌ / ⚠️ | {具体差异文件} |
| C3 | Patch 差异合理性 | ✅ / ❌ / ⚠️ / N/A | {说明} |
| C4 | 分支命名规范性 | ✅ / ❌ / ⚠️ | {不规范的分支名} |
| C5 | 目标分支匹配 | ✅ / ❌ / ⚠️ | {不匹配的 PR} |
| C6 | 遗漏检查 | ✅ / ❌ | {遗漏的改动} |
| C7 | 多余检查 | ✅ / ❌ | {多余的提交} |
| C8 | 描述一致性 | ✅ / ❌ / ⚠️ | {不一致的描述} |

### 跨分支文件差异明细

```
文件: test_upstream/test_nn.py.patch
  v2.7.1: {hash} (base)
  v2.9.0: {hash} (与 v2.7.1 一致 / 不一致，原因：{说明})
  v2.10.0: {hash} (一致 / 不一致)
  ...

文件: test/test_xxx.py
  仅 v2.7.1: ✅
  仅 v2.9.0: ❌ 缺少
  ...
```

---

## 第三部分：总结

### 整体统计

| 分支 | 总项 | ✅ | ❌ | ⚠️ | N/A |
|------|------|----|----|----|-----|
| v2.7.1 | {N} | {N} | {N} | {N} | {N} |
| v2.9.0 | {N} | {N} | {N} | {N} | {N} |
| ... | ... | ... | ... | ... | ... |

### 跨分支统计
| 检查项 | 通过 | 不通过 |
|--------|------|--------|
| 共 8 项 | {N} | {N} |

---

### 必须修复的问题（按分支）

**v2.7.1:**
1. {问题}

**v2.9.0:**
1. {问题}

**跨分支:**
1. {问题}

---

### 建议改进
1. {建议}

---

## 修改意见

> 以下是根据审核结果汇总的具体修改指令，请 PR 提交者逐条执行。

### 代码修改
1. {具体修改指令，标注适用分支，如 "【全部 release 分支】请将 `test_hint_int` 方法中的 `self.assertTrue(hasattr(...))` 统一改为 `if not hasattr(...): self.skipTest(...)` 守卫模式"}
2. ...（如无需修改代码则写「无需修改」）

### 描述补充
1. {具体补充指令，标注适用分支，如 "【全部 PR】请在描述中附上对应目标分支的运行日志"}
2. ...

### 流程操作
1. {具体操作指令，标注适用分支}
2. ...（如无需流程操作则写「无需操作」）

---

*本报告由 Torch NPU PR Review Skill 自动生成，仅检查格式和内容规范，未运行代码。*
```

---

## 判定标准

- **✅ 通过**：该项完全符合规范要求
- **❌ 不通过**：该项明确违反规范，必须在合入前修复
- **⚠️ 需关注**：无法完全确认，或存在潜在风险需要人工复核
- **N/A**：该项不适用于当前 PR

## 跨分支判定标准

- **✅ 通过**：各分支之间一致或差异有合理解释
- **❌ 不通过**：存在遗漏分支、错误目标分支、无理由的差异
- **⚠️ 需关注**：需要人工确认的差异
