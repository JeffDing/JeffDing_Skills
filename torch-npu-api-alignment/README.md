# torch-npu-api-alignment

把一个 PyTorch 原生 API 在 Ascend torch-npu 上「分析 → 用例 → 提交 → 自审」跑通的完整流程技能。

## 何时用

接到一个 torch-npu API 一致性补齐任务（形如 `torch.xxx.yyy.zzz`），需要：
- 判断场景（1.1 / 1.2 / 1.3）
- 写测试用例
- 跨分支提交 PR
- 关联官方任务书 issue

## 用法

1. 通读 `SKILL.md` —— 全流程 + 检查清单 + 常见坑
2. 按阶段执行：
   - 阶段一：API 分析（克隆 PyTorch 官方仓库检索）
   - 阶段二：本地 NPU 验证（**本环境有 Ascend910 + torch_npu**）
   - 阶段三：写用例（参考 `templates/test_file_template.py`，遵守 8.1–8.10）
   - 阶段四：`scripts/check_flake8.sh` 用项目配置 lint
   - 阶段五：6 分支 commit + push（`scripts/apply_to_all_branches.sh`）
   - 阶段六：关联任务书 issue、创建 PR（`templates/pr_body_template.md`）
   - 阶段七：用 `torch-npu-pr-review` skill 自审

## 铁律

1. **本环境有 NPU**，永远先本地跑通，不要假设 CPU-only
2. **不擅自动手**：push / 建 PR / 建-关 issue / force-push 前必须用户确认
3. **关联任务书 issue**，不要自建冗余 issue
4. **提交前自审**（`torch-npu-pr-review`）
5. **不用 /sync**

## 脚本

| 脚本 | 用途 |
|------|------|
| `scripts/check_flake8.sh <repo> <file...>` | 用项目 `.flake8` 配置 lint（避免默认 79 字符误报） |
| `scripts/apply_to_all_branches.sh` | 6 分支统一 commit（`reset --soft` 单 commit）+ force push |
| `scripts/verify_cross_branch.py <pr...>` | 验证 6 分支 patch 字节一致 + commit message 一致 + 无 F401/`#xxx` |

## 模板

| 模板 | 用途 |
|------|------|
| `templates/test_file_template.py` | 测试文件骨架（含 8.1–8.10 规范注释） |
| `templates/pr_body_template.md` | PR 描述（6 节社区模板，含功能验证格式） |
| `templates/commit_message_template.txt` | commit message（6 分支复用，禁止占位符） |

## 配套技能

- PR 审核：https://gitcode.com/Ascend/agent-skills/tree/master/official/PyTorch/torch-npu-pr-review

## 参考 PR

- test 目录新增用例：https://gitcode.com/Ascend/pytorch/pull/34025
- autograd profiler 类：https://gitcode.com/Ascend/pytorch/pull/41982
