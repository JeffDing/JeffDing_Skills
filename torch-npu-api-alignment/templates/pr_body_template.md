# 【合入来源】

- [ ] 需求
- [ ] 问题单
- [x] issue/工单
- [ ] 重构优化
- [ ] 资料更新

关联 issue: #<任务书 issue 号>（社区任务第X期 - Ascend for PyTorch API 一致性开发）

# 【修改方案】
为 `torch.<module>.<api>` 补齐验证用例（用例补齐场景 1.3 / 1.1）。

<2-4 句话说明 API 功能 + 在 torch 中的定义位置 + Kernel.index 是什么>

PyTorch 官方社区 `test/` 目录中无 `<api>` 的直接验证用例（<证据：哪些 test 文件只导入了什么、没覆盖什么>），故新增 `test/<对应路径>/test_<module>.py`，覆盖：
1. <场景 1>
2. <场景 2>
3. <场景 3>

文件按可扩展原则组织，后续同模块其他 API 可在同一文件补充。该 API 为 <纯 Python 非计算类 / 计算类>，<无需 NPU 适配 / 张量已迁移 NPU>。

# 【资料变更】
不涉及。已检查 `docs/zh/native_apis/` 下各版本目录（pytorch_2-7-1 … pytorch_2-12-0）的 `torch-*.md`，<api> <未列入支持度表格 / 已列入>；<api> 为 <非计算类纯 Python 方法 / 已支持>，<与数据类型无关，无需补充 / 详见 issue #xxx>。

# 【接口变更】
不涉及。仅新增测试文件，未修改任何对外接口。

# 【功能验证】
测试环境：
```text
torch: 2.10.0+cpu
torch_npu: 2.10.0
CANN: 9.0.0
NPU: Ascend910
```

测试方法：
```bash
source /usr/local/Ascend/ascend-toolkit/set_env.sh
TORCH_DEVICE_BACKEND_AUTOLOAD=1 python3.12 /tmp/test_<module>.py -v
```

测试结果（20t NPU 实机环境）：
```
root@<hostname>:/home# source /usr/local/Ascend/ascend-toolkit/set_env.sh
root@<hostname>:/home# TORCH_DEVICE_BACKEND_AUTOLOAD=1 python3.12 /tmp/test_<module>.py -v
test_<case1> ... ok
test_<case2> ... ok
test_<case3> ... ok

----------------------------------------------------------------------
Ran 3 tests in X.Xs

OK
```

# 【CheckList】
- [x] 代码注释完备，正确记录错误日志
- [x] 代码实现进行了返回值、空指针等校验
- [x] PR标题正确使用类型标签：test
- [x] PR持续集成流水线（CI）执行通过，代码检查无异常
