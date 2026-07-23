---
name: torch-npu-api-alignment
description: Ascend torch-npu 单个 PyTorch 原生 API 的一致性补齐全流程：API 分析、场景判定（1.1/1.2/1.3）、本地 NPU 验证、编写测试用例、跨分支提交、关联任务书 issue、创建 PR、自审。包含本环境（Ascend910 + torch_npu）的实战命令、gitcode API 怪癖、常见坑和模板。
---

# Torch-NPU API 一致性补齐 Skill

> 把一个 PyTorch 原生 API 在 torch-npu 上「分析 → 用例 → 提交 → 自审」跑通的完整流程。
> 配套 `torch-npu-pr-review` skill 做提交前自审。

---

## 0. 铁律（每条都是血泪）

1. **本环境有 NPU**：Ascend910 ×2 + torch_npu（默认 python3，`import torch_npu` 可用）。**永远先本地跑通**，不要假设 CPU-only。
2. **不擅自动手**：每个有外部副作用的动作（push、建 PR、建/关 issue、force-push）**必须先拿到用户明确确认**。提供 token / fork URL ≠ 授权直接发 PR。
3. **关联任务书 issue**：每个 API 在 Ascend/pytorch 都有官方任务书 issue（标题含「社区任务第X期…」，正文中「API名称」节列出该 API）。**PR 关联到任务书，不要自建冗余 issue**。
4. **提交前自审**：用 `torch-npu-pr-review` skill 全清单 review，修完再 push。
5. **不要用 /sync**：跨分支 PR 必须手动逐个创建。

---

## 1. 环境速查

```bash
# NPU 在位
npu-smi info                              # Ascend910
python3 -c "import torch_npu; print(torch_npu.__version__)"
python3 -c "import torch; print(torch.accelerator.current_accelerator())"  # → npu

# 关键路径
source /usr/local/Ascend/ascend-toolkit/set_env.sh
# CANN: 9.0.0 ; python: /usr/local/python3.12.13/bin/python3 (python3.12)
# hostname 形如 a89d9d564fe4（写日志时保留 shell 提示符）

# GitCode API（PAT）
# - push:           https://{user}:{token}@gitcode.com/{user}/pytorch.git
# - api/v5:         -H "Private-Token: {token}"   （不要用 Bearer，会 401）
# - 关 issue:       PATCH .../issues/{n}  -d '{"state":"close"}'   （是 close 不是 closed，不是 state_event）
# - Ascend/pytorch project_id: 7404318
```

---

## 2. 阶段一：API 分析与场景判定

### 2.1 先克隆 **PyTorch 官方** 仓库（不是 torch-npu！）
```bash
git clone --depth 1 -b v2.7.1 https://github.com/pytorch/pytorch.git /tmp/opencode/pytorch-official
```
> 第一步错后面全错。torch-npu 仓库里的 pytorch 是老的 fork，不能拿来检索社区用例。

### 2.2 检索社区用例（用短关键字，不用全称）
```bash
grep -rn "update_arg\|Kernel" /tmp/opencode/pytorch-official/test --include="*.py"
grep -rn "from torch.autograd.profiler_util import" /tmp/opencode/pytorch-official/test --include="*.py"
```

### 2.3 判定场景（决定后续动作）

| 场景 | 条件 | 动作 | 提交目录 | 分支 |
|------|------|------|----------|------|
| **1.1** | 社区有用例 + 需 NPU 适配 | 生成 `.patch` 提交 | `test_upstream/` | 2.7.1/2.11.0/2.12.0（**不含 master**） |
| **1.2** | 社区有用例 + 无需任何修改 | 仅在 issue 说明，无 PR | — | — |
| **1.3** | 社区无用例 | 自写用例 | `test/` | 2.7.1/2.11.0/2.12.0 **+ master** |

> 记住：`test/` 场景含 master，`test_upstream/` 场景不含 master。

### 2.4 判断是否需要 API 代码补齐 / 资料补齐
- **API 补齐**：若 torch_npu 直接 `from torch...import` 复用（纯 Python / namedtuple / 工具类），**无需补齐**。
- **资料补齐**：检查 `docs/zh/native_apis/pytorch_2-X-X/torch-*.md`：
  - 非计算类 API（与数据类型无关）→ 限制说明写 `-`，不要写「支持 fp32」
  - 私有接口（带下划线前缀）→ 不补资料
  - 工具类（`Kernel`/`EventList`/`Interval` 等未列入支持度表的）→ 一般不补
  - 需要补则只提 PR 到 v2.7.1，但刷新所有版本子目录

---

## 3. 阶段二：本地 NPU 验证

**写用例之前**，先在本地 NPU 上把目标 API 跑一遍，确认行为：
```bash
source /usr/local/Ascend/ascend-toolkit/set_env.sh
TORCH_DEVICE_BACKEND_AUTOLOAD=1 python3.12 -c "
import torch, torch_npu
from torch.autograd.profiler_util import Kernel
k = Kernel('add','npu',10)
print(k.index(10))   # 2
"
```

---

## 4. 阶段三：编写测试用例（严格遵守 8.1–8.10）

### 4.1 文件路径
按 PyTorch 模块结构对应：`torch.<module>.<api>` → `test/<对应路径>/test_<module>.py`
- 例：`torch.autograd.profiler_util.Kernel.index` → `test/autograd/test_profiler_util.py`
- `torch.distributed.elastic.metrics.api.X` → `test/distributed/elastic/metrics/test_metrics_api.py`

### 4.2 文件模板（见 `templates/test_file_template.py`）
要点：
1. 顶部 docstring 说明功能 + 可扩展（同类 API 放同一文件）
2. `from torch.testing._internal.common_utils import TestCase, run_tests`（**不要** `import unittest`）
3. 涉及张量必须 NPU：`device_type = acc.type if (acc := torch.accelerator.current_accelerator()) else "cpu"` 然后 `.to(device_type)`
4. 结果比对用 `self.assert*`，**不要 try/except**（异常用 `with self.assertRaises(...)`）
5. **不要 print 调试日志**
6. 涉及张量才 `import torch`，**未使用绝不 import**（否则 FLAKE8 F401，CI 必挂）
7. 导入顺序：标准库 → torch → torch.testing → torch_npu（一般不需要 torch_npu，昇腾环境 import torch 自动加载）
8. 类前后空 2 行，方法间空 1 行
9. 聚焦核心功能，不要写「检测 NPU 是否存在」这类冗余守卫

### 4.3 flake8 必须用项目配置
```bash
python3 -m flake8 --config=/path/to/torch-npu/.flake8 test/xxx/test_yyy.py
```
> 项目 `.flake8`：`max-line-length=120`，`E501` 已 ignore（改用 B950）。
> 默认 `flake8`（79 字符）会误报 E501，**别被误导**。

---

## 5. 阶段四：准备 5 个分支

```bash
# fork 必须选「全部分支」，否则远程分支不存在
for v in v2.7.1 v2.11.0 v2.12.0 master; do
  git clone --depth 1 -b $v https://gitcode.com/Ascend/pytorch.git torch-npu-$v
done
```

### ⚠️ shallow clone 不能 push（"shallow update not allowed"）
第一次 push 前必须 unshallow 当前分支：
```bash
cd torch-npu-v2.7.1 && git fetch --unshallow origin v2.7.1
```

---

## 6. 阶段五：commit + push（每个 PR 单次 commit）

### 6.1 分支命名
- 本地 feature 分支：`test-<api-slug>-<version>`（version **不带 v**，如 `2.7.1`）
- 远程分支：`<version>-test-<api-slug>`（version **带 v**，如 `v2.7.1-test-...`），master 用 `master-test-...`

### 6.2 单次 commit（多次提交合并）
```bash
git checkout -b test-<api-slug>-2.7.1
cp <test_file> test/<path>/
git add test/<path>/<file>
git reset --soft origin/v2.7.1        # 关键：合并成单次 commit
git commit -F /tmp/commit_msg.txt      # commit_msg.txt 见 templates
```

### 6.3 commit message 必须 6 分支完全一致
- **禁止占位符**（如 `#xxx`）！要么不写 issue 号，要么写真号
- 用 `git commit -F file` 避免 shell 转义问题

### 6.4 push
```bash
git push "https://${USER}:${TOKEN}@gitcode.com/${USER}/pytorch.git" \
  test-<api-slug>-2.7.1:v2.7.1-test-<api-slug>
# force-push（修代码后）加 -f
```

---

## 7. 阶段六：关联任务书 issue + 创建 PR

### 7.1 找任务书 issue
```bash
# 在 Ascend/pytorch 搜社区任务 issue，正文中含该 API 名
curl -s -H "Private-Token: $TOKEN" "https://gitcode.com/api/v5/repos/Ascend/pytorch/issues?state=open&labels=event:api-consistency" \
  | python3 -c "import sys,json;[print(i['number'],i['title']) for i in json.loads(sys.stdin.read())]"
```
确认目标 issue 正文「API名称」节列出当前 API。

### 7.2 PR 描述（社区模板，见 `templates/pr_body_template.md`）
必须含 6 节：【合入来源】【修改方案】【资料变更】【接口变更】【功能验证】【CheckList】

**【功能验证】必须按这个格式（参考已合并 PR）**：
```
测试环境：
torch: 2.10.0+cpu
torch_npu: 2.10.0
CANN: 9.0.0
NPU: Ascend910

测试方法：
source /usr/local/Ascend/ascend-toolkit/set_env.sh
TORCH_DEVICE_BACKEND_AUTOLOAD=1 python3.12 /tmp/test_xxx.py -v

测试结果（20t NPU 实机环境）：
root@<hostname>:/home# source /usr/local/Ascend/ascend-toolkit/set_env.sh
root@<hostname>:/home# TORCH_DEVICE_BACKEND_AUTOLOAD=1 python3.12 /tmp/test_xxx.py -v
test_xxx ... ok
----------------------------------------------------------------------
Ran N tests in X.Xs
OK
```
> 真实日志要带 shell 提示符，不要伪造。

### 7.3 创建 PR（gitcode api/v5）
```bash
curl -X POST -H "Private-Token: $TOKEN" -H "Content-Type: application/json" \
  "https://gitcode.com/api/v5/repos/Ascend/pytorch/pulls" \
  -d "{\"title\":\"[<ver>] test: ...\", \"head\":\"${USER}:<ver>-test-<slug>\", \"base\":\"<ver>\", \"body\":<json-encoded body>}"
```

### 7.4 CLA
- 用 **gitcode 绑定邮箱** 签 CLA（commit 作者邮箱必须与之一致，否则 CLA 不生效）
- 检查 PR 标签 `ascend-cla/yes`（不再是 `ascend-cla/no`）

---

## 8. 阶段七：提交前自审（强制）

用 `torch-npu-pr-review` skill：
```bash
python3 /tmp/opencode/agent-skills/official/PyTorch/torch-npu-pr-review/scripts/gitcode_fetch.py \
  --issue https://gitcode.com/Ascend/pytorch/issues/<task_issue> \
  --pr v2.7.1=https://gitcode.com/Ascend/pytorch/pull/<pr1> \
  ... \
  --project-id 7404318 --out /tmp/opencode/review-out
```
然后按 SKILL.md 检查清单逐项过，重点：
- **8.7 导入**：F401？顺序？
- **C2/C3**：6 分支 patch 字节一致？commit message 一致？
- **CLA / CI 标签**
- **关联 issue** 是否为任务书（非自建）

发现的问题**全部修完**再 push，不要带病提交。

---

## 9. 检查清单（提交前自检）

### 代码
- [ ] `flake8 --config=.flake8` 通过
- [ ] 本地 NPU 跑通（`run_tests` 输出 `OK`）
- [ ] 无 `import torch` 未使用 / 无 `import unittest` / 无 try-except / 无 print
- [ ] 张量在 NPU（`.to(device_type)` 或 `.npu()`）
- [ ] 文件顶部 docstring + 可扩展说明

### Commit
- [ ] 每个 PR **单次** commit（`reset --soft`）
- [ ] 6 分支 commit message **字节一致**，无占位符
- [ ] 6 分支 patch 字节一致（除非版本差异，需说明）

### PR
- [ ] 用社区模板（6 节齐全）
- [ ] 关联**任务书** issue（不是自建）
- [ ] 【功能验证】含 测试环境 + 方法 + 真实日志
- [ ] CLA 已签（`ascend-cla/yes`）
- [ ] CI 通过

### 分支覆盖
- [ ] `test/` 场景：6 分支（含 master）
- [ ] `test_upstream/` 场景：5 分支（不含 master）

---

## 10. 常见坑（踩过的）

| 现象 | 原因 | 解决 |
|------|------|------|
| push 报 `shallow update not allowed` | depth=1 浅克隆 | `git fetch --unshallow origin <branch>` |
| CI 报 FLAKE8 F401 | `import torch` 未使用 | 删掉未用 import；别为了「导入 torch」硬留 |
| 默认 flake8 报 E501 行太长 | 用了 79 字符默认 | 用项目 `.flake8`（120，E501 ignored） |
| 关 issue PATCH 不生效 | 字段写错 | `{"state":"close"}`（动词），不是 `closed`/`state_event` |
| api/v5 返回 401 token not found | 用了 Bearer | 用 `Private-Token` header |
| CLA 一直 `ascend-cla/no` | commit 邮箱 ≠ gitcode 绑定邮箱 | `git config user.email` 对齐后重 commit |
| PR 关联了自建 issue | 没找任务书 | 找官方任务书 issue（label `event:api-consistency`），关闭自建 |
| 6 分支 commit message 不一致 | 手敲 / 占位符没替换 | 用 `git commit -F msg.txt`，6 分支同一个文件 |
| 误把 master 也提交 test_upstream patch | 记错规则 | test_upstream 不含 master；test 含 master |
| 擅自创建 PR/issue 惹怒用户 | 没确认就动手 | 每个外部动作先问 |

---

## 11. 参考

- 任务指导书（原始）：见 issue 任务书正文 / 腾讯文档
- PR 审核技能：`https://gitcode.com/Ascend/agent-skills/tree/master/official/PyTorch/torch-npu-pr-review`
- 已合并参考 PR：
  - test 目录新增用例：`gitcode.com/Ascend/pytorch/pull/34025`
  - autograd profiler 类：`gitcode.com/Ascend/pytorch/pull/41982`
- 社区 PR 模板：仓库根 `.gitcode/PULL_REQUEST_TEMPLATE.md`
