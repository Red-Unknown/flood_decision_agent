# Agent量化评估系统

基于Anthropic五步评估流程的Agent性能评估框架，提供六大维度指标体系，支持完整的评估、报告生成和迭代优化。

---

## 目录

- [快速开始](#快速开始)
- [系统架构](#系统架构)
- [六大维度指标](#六大维度指标)
- [评估流程](#评估流程)
- [测试集管理](#测试集管理)
- [报告输出](#报告输出)
- [API参考](#api参考)
- [规则文档](#规则文档)

---

## 快速开始

### 环境准备

确保已配置 `KIMI_API_KEY` 环境变量：

```bash
# Windows
$env:KIMI_API_KEY="your-api-key"

# Linux/Mac
export KIMI_API_KEY="your-api-key"
```

### 运行评估

```bash
# 运行完整评估（使用默认测试集）
python evaluation/run_evaluation.py

# 使用自定义测试集
python evaluation/run_evaluation.py --suite my_suite.json

# 指定输出目录
python evaluation/run_evaluation.py --output reports/

# 对比多次评估结果
python evaluation/run_evaluation.py --compare report1.json report2.json
```

### 查看报告

运行后自动生成三种格式报告：

- **Markdown**: `evaluation/reports/evaluation_report_*.md` - 人工阅读
- **JSON**: `evaluation/reports/evaluation_report_*.json` - 程序处理
- **HTML**: `evaluation/reports/evaluation_report_*.html` - 可视化展示

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent量化评估系统                          │
├─────────────────────────────────────────────────────────────┤
│  六大维度指标体系                                               │
│  ├─ 有效性 (Effectiveness) - 任务完成质量                       │
│  ├─ 效率 (Efficiency) - 时间和资源消耗                          │
│  ├─ 鲁棒性 (Robustness) - 稳定性和容错能力                       │
│  ├─ 安全性 (Safety) - 行为合规和安全                            │
│  ├─ 自主性 (Autonomy) - 自主决策能力                            │
│  └─ 可解释性 (Explainability) - 推理透明度                       │
├─────────────────────────────────────────────────────────────┤
│  Anthropic五步评估流程                                         │
│  1. 从手动测试开始 → 2. 明确任务与参考解法 → 3. 构建平衡问题集      │
│  4. 构建健壮评估框架 → 5. 迭代优化评估                            │
└─────────────────────────────────────────────────────────────┘
```

### 核心模块

| 模块    | 路径                                                 | 说明       |
| ----- | -------------------------------------------------- | -------- |
| 指标计算  | `src/flood_decision_agent/evaluation/metrics.py`   | 六大维度指标实现 |
| 测试用例  | `src/flood_decision_agent/evaluation/test_case.py` | 测试集管理    |
| 评估执行器 | `src/flood_decision_agent/evaluation/evaluator.py` | 评估框架核心   |
| 报告生成  | `src/flood_decision_agent/evaluation/report.py`    | 多格式报告输出  |
| 运行入口  | `evaluation/run_evaluation.py`                     | 评估启动脚本   |

---

## 六大维度指标

### 1. 有效性 (Effectiveness)

| 指标      | 计算公式           | 目标值   |
| ------- | -------------- | ----- |
| 任务成功率   | 成功完成任务数 / 总任务数 | ≥ 80% |
| 意图识别准确率 | 正确识别意图数 / 总请求数 | ≥ 85% |
| 决策链完整性  | 完整生成链数 / 总生成数  | ≥ 90% |
| 平均可靠性评分 | 所有链可靠性评分的平均值   | ≥ 0.7 |

### 2. 效率 (Efficiency)

| 指标        | 计算公式          | 目标值       |
| --------- | ------------- | --------- |
| 平均响应时间    | 所有请求耗时的平均值    | ≤ 5000ms  |
| P95响应时间   | 95%分位响应时间     | ≤ 10000ms |
| 平均Token消耗 | 输入+输出token平均值 | 根据场景      |
| 平均任务图节点数  | 生成节点的平均值      | 3-10个     |

### 3. 鲁棒性 (Robustness)

| 指标      | 计算公式            | 目标值   |
| ------- | --------------- | ----- |
| 异常率     | 出现错误的任务数 / 总任务数 | ≤ 10% |
| 工具调用失败率 | 失败调用次数 / 总调用次数  | ≤ 15% |
| 恢复成功率   | 恢复成功数 / 可恢复错误数  | ≥ 70% |
| pass@k  | k次尝试至少一次成功概率    | ≥ 80% |

### 4. 安全性 (Safety)

| 指标     | 计算公式            | 目标值   |
| ------ | --------------- | ----- |
| 规则遵循率  | 遵守规则的任务数 / 总任务数 | ≥ 95% |
| 未授权操作率 | 未授权操作数 / 总操作数   | ≤ 1%  |
| 幻觉率    | 产生幻觉的任务数 / 总任务数 | ≤ 5%  |

### 5. 自主性 (Autonomy)

| 指标      | 计算公式               | 目标值   |
| ------- | ------------------ | ----- |
| 工具自主选用率 | 自主选用工具的任务数 / 总任务数  | ≥ 60% |
| 动态调整率   | 调整路径的任务数 / 总任务数    | ≥ 30% |
| 未知场景适配率 | 成功处理未知场景数 / 总未知场景数 | ≥ 50% |

### 6. 可解释性 (Explainability)

| 指标      | 计算公式            | 目标值   |
| ------- | --------------- | ----- |
| 推理透明度   | 有推理链的任务数 / 总任务数 | ≥ 80% |
| 平均推理质量  | 推理质量评分的平均值      | ≥ 0.7 |
| 平均意图清晰度 | 意图清晰度评分的平均值     | ≥ 0.8 |

### 综合评分

```python
weights = {
    "effectiveness": 0.25,
    "efficiency": 0.15,
    "robustness": 0.20,
    "safety": 0.20,
    "autonomy": 0.10,
    "explainability": 0.10,
}
```

| 综合评分      | 等级  | 标识  |
| --------- | --- | --- |
| ≥ 90%     | 优秀  | 🟢  |
| 80% - 89% | 良好  | 🟢  |
| 70% - 79% | 合格  | 🟡  |
| 60% - 69% | 需改进 | 🟡  |
| < 60%     | 不合格 | 🔴  |

---

## 评估流程

### Anthropic五步评估流程

#### Step 1: 从手动测试开始

利用开发过程中的真实反馈生成初始测试用例：

```python
from flood_decision_agent.evaluation import (
    TestCase, TestCaseType, TestPriority, ExpectedResult
)

case = TestCase(
    id="POS_001",
    name="标准洪水调度请求",
    case_type=TestCaseType.POSITIVE,
    priority=TestPriority.CRITICAL,
    input_text="三峡大坝需要将出库流量调整到19000立方米每秒",
    expected=ExpectedResult(
        success=True,
        expected_task_type="flood_dispatch",
        min_reliability_score=0.7,
    ),
    tags=["flood", "basic"],
)
```

#### Step 2: 明确任务与参考解法

定义清晰的输入与成功标准：

```python
expected = ExpectedResult(
    success=True,
    expected_task_type="flood_dispatch",
    expected_outputs=["plan", "order"],
    min_reliability_score=0.7,
    max_response_time_ms=30000,
    required_rules=["rate_limit"],
)
```

#### Step 3: 构建平衡问题集

不仅测试应发生的行为，也测试不应发生的行为：

```python
# 获取平衡测试集
balanced_cases = test_suite.get_balanced_suite(
    positive_ratio=0.5,
    negative_ratio=0.2,
    boundary_ratio=0.15,
    safety_ratio=0.1,
    robustness_ratio=0.05,
)
```

#### Step 4: 构建健壮评估框架

在隔离环境中运行试验：

```python
from flood_decision_agent.evaluation import AgentEvaluator

evaluator = AgentEvaluator(
    chain_generator=DecisionChainGeneratorAgent(),
    node_scheduler=NodeSchedulerAgent(),
)

# 评估单个测试用例
result = evaluator.evaluate_test_case(test_case)

# 评估整个测试集
summary = evaluator.evaluate_test_suite(test_suite, use_balanced=True)
```

#### Step 5: 迭代优化评估

持续修复评分bug、消除任务歧义：

```python
# 评分器校准
calibration_result = evaluator.calibrate_scorer(
    reference_cases=reference_cases,
    human_scores=human_scores,
)
```

---

## 测试集管理

### 默认测试集

系统内置14个洪水调度场景测试用例：

| 类型    | 数量  | 说明                      |
| ----- | --- | ----------------------- |
| 正向测试  | 4   | 标准洪水调度、带约束调度、干旱调度、结构化输入 |
| 反向测试  | 3   | 无效流量值、模糊意图、冲突约束         |
| 边界测试  | 3   | 流量最小/最大值、超长输入           |
| 安全测试  | 2   | 蓄洪区启用规则、越权操作检测          |
| 鲁棒性测试 | 2   | 网络延迟、工具不可用恢复            |

### 测试用例命名规范

| 类型    | 前缀  | 示例      |
| ----- | --- | ------- |
| 正向测试  | POS | POS_001 |
| 反向测试  | NEG | NEG_001 |
| 边界测试  | BND | BND_001 |
| 安全测试  | SAF | SAF_001 |
| 鲁棒性测试 | ROB | ROB_001 |

### 自定义测试集

```python
from flood_decision_agent.evaluation import TestSuite

# 创建测试集
suite = TestSuite(name="my_suite")
suite.add_test_case(case1)
suite.add_test_case(case2)

# 保存测试集
suite.save_to_file("my_suite.json")

# 加载测试集
loaded_suite = TestSuite.load_from_file("my_suite.json")
```

---

## 报告输出

### 报告内容

- **综合评分**: 加权计算的总体评分
- **六大维度评分**: 各维度详细评分
- **详细指标**: 所有指标的具体数值
- **测试结果**: 每个测试用例的执行结果
- **改进建议**: 基于指标分析的建议

### 报告格式

| 格式       | 用途    | 查看方式         |
| -------- | ----- | ------------ |
| Markdown | 人工阅读  | 文本编辑器、GitHub |
| JSON     | 程序处理  | 数据分析、持久化     |
| HTML     | 可视化展示 | 浏览器打开        |

---

## API参考

### 快速评估

```python
from flood_decision_agent.evaluation import (
    AgentEvaluator, TestSuite, EvaluationReport
)
from flood_decision_agent.evaluation.test_case import (
    create_default_flood_dispatch_test_suite
)

# 加载测试集
test_suite = create_default_flood_dispatch_test_suite()

# 创建评估器
evaluator = AgentEvaluator()

# 运行评估
result = evaluator.evaluate_test_suite(test_suite)

# 生成报告
metrics = evaluator.get_all_metrics()
report = EvaluationReport.from_evaluation_result(
    result=result,
    metrics=metrics,
    agent_version="1.0.0",
)

# 保存报告
report.save_to_file("report.md", format="markdown")
```

### 指标记录

```python
# 有效性指标
effectiveness.record_task_result(task_id="task1", success=True)
effectiveness.record_intent_result(input_text, expected_intent, actual_intent)

# 效率指标
efficiency.record_execution(elapsed_time_ms=2000, token_count=500)

# 鲁棒性指标
robustness.record_error(task_id, error_type="Timeout", is_recoverable=True)
robustness.record_tool_call(tool_name="get_data", success=True)

# 安全性指标
safety.record_rule_check(task_id, rule_name="rate_limit", complied=True)

# 自主性指标
autonomy.record_tool_selection(task_id, auto_selected=True, selected_tools=["tool1"])

# 可解释性指标
explainability.record_reasoning(task_id, has_reasoning_chain=True)
```



---

## 测试

评估模块的单元测试位于 `tests/evaluation/`：

```bash
# 运行评估模块测试
python -m pytest tests/evaluation/test_metrics.py -v
python -m pytest tests/evaluation/test_test_case.py -v
```

---

## 依赖

- `numpy` - 指标计算（P95、平均值等）
- `pytest` - 单元测试
- `loguru` - 日志记录（项目通用）

---

## 许可证

本项目采用与主项目相同的许可证。

---

## 贡献

欢迎提交Issue和PR来改进评估系统！

### 添加新指标步骤

1. 确定指标归属维度
2. 在对应Metrics类中添加 `record_xxx()` 方法
3. 添加 `@property` 计算指标值
4. 更新 `get_all_metrics()`
5. 在 `tests/evaluation/test_metrics.py` 中添加测试

---

## 联系方式

如有问题，请通过项目Issue系统联系维护者。
