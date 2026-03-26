---
name: "evaluation-workflow"
description: "Guides Agent evaluation workflow based on Anthropic's 5-step process. Invoke when user asks about evaluation process, creating test cases, Anthropic 5-step evaluation, scorer calibration, or comparing evaluation results."
---

# Agent评估工作流 Skill

基于Anthropic五步评估流程的Agent性能评估工作流指南。

## 调用时机

**当用户询问以下内容时触发：**
- "评估流程"、"如何运行评估"
- "创建测试用例"、"设计测试集"
- "Anthropic五步评估流程"
- "评分器校准"、"迭代优化"
- "对比评估结果"

---

## Anthropic五步评估流程

### Step 1: 从手动测试开始

**目标**: 利用开发过程中的真实反馈生成初始测试用例

**操作步骤**:
1. 收集实际使用场景（bug报告、用户反馈）
2. 创建正向测试用例（正常功能）
3. 创建反向测试用例（异常处理）
4. 创建边界测试用例（极限条件）

**代码实现**:
```python
from flood_decision_agent.evaluation import TestCase, TestCaseType, TestPriority

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

**默认测试集**: `create_default_flood_dispatch_test_suite()` 已包含14个基础用例

---

### Step 2: 明确任务与参考解法

**目标**: 每个任务定义清晰的输入与成功标准，创建参考解法校准评分器

**操作步骤**:
1. 定义预期结果 (`ExpectedResult`)
2. 设置成功标准（可靠性阈值、响应时间限制）
3. （可选）提供参考解法 (`reference_solution`)
4. 正向验证（任务可解）和反向验证（异常处理）

**代码实现**:
```python
from flood_decision_agent.evaluation import ExpectedResult

expected = ExpectedResult(
    success=True,
    expected_task_type="flood_dispatch",
    expected_outputs=["plan", "order"],
    min_reliability_score=0.7,
    max_response_time_ms=30000,
    required_rules=["rate_limit"],
)
```

---

### Step 3: 构建平衡问题集

**目标**: 不仅测试应发生的行为，也测试不应发生的行为，避免类别不平衡

**测试类型比例建议**:
| 类型 | 比例 | 用途 |
|------|------|------|
| 正向测试 | 50% | 验证正常功能 |
| 反向测试 | 20% | 验证异常处理 |
| 边界测试 | 15% | 验证边界条件 |
| 安全测试 | 10% | 验证合规性 |
| 鲁棒性测试 | 5% | 验证容错能力 |

**代码实现**:
```python
balanced_cases = test_suite.get_balanced_suite(
    positive_ratio=0.5,
    negative_ratio=0.2,
    boundary_ratio=0.15,
    safety_ratio=0.1,
    robustness_ratio=0.05,
)
```

**扣分机制**:
- 节点数超过10个：复杂度扣分
- 触发风险操作：安全隐患扣分
- 响应时间超过阈值：性能扣分

---

### Step 4: 构建健壮评估框架

**目标**: 在隔离环境中运行试验，混合使用代码基、模型基与人工评分器

**隔离环境**:
- 每次测试从干净状态启动
- 独立的 `SharedDataPool`
- 独立的Agent实例

**代码实现**:
```python
from flood_decision_agent.evaluation import AgentEvaluator

evaluator = AgentEvaluator(
    chain_generator=DecisionChainGeneratorAgent(),
    node_scheduler=NodeSchedulerAgent(),
)

result = evaluator.evaluate_test_case(test_case)
summary = evaluator.evaluate_test_suite(test_suite, use_balanced=True)
```

**评分器类型**:
1. **代码基评分器**: 基于规则的自动验证
2. **模型基评分器**: 使用LLM评估输出质量
3. **人工评分器**: 人工标注作为金标准

---

### Step 5: 迭代优化评估

**目标**: 将评估本身视为产品，持续修复评分bug、消除任务歧义

**迭代流程**:
```
运行评估 → 分析报告 → 识别问题 → 修复改进 → 重新评估
```

**评分器校准**:
```python
reference_cases = [...]  # 包含 reference_solution 的测试用例
human_scores = {"case_001": 0.85, "case_002": 0.92}

calibration_result = evaluator.calibrate_scorer(
    reference_cases=reference_cases,
    human_scores=human_scores,
)
```

**消除任务歧义**:
- 模糊意图 → 明确任务定义
- 冲突约束 → 添加约束优先级
- 边界不清 → 明确边界条件

---

## 评估执行命令

```bash
# 运行完整评估
python evaluation/run_evaluation.py

# 使用自定义测试集
python evaluation/run_evaluation.py --suite my_suite.json

# 指定输出目录
python evaluation/run_evaluation.py --output reports/

# 对比多次评估结果
python evaluation/run_evaluation.py --compare report1.json report2.json
```

---

## 测试用例设计规范

### 命名规范

| 类型 | 前缀 | 示例 |
|------|------|------|
| 正向测试 | POS | POS_001 |
| 反向测试 | NEG | NEG_001 |
| 边界测试 | BND | BND_001 |
| 安全测试 | SAF | SAF_001 |
| 鲁棒性测试 | ROB | ROB_001 |

### 优先级定义

| 优先级 | 说明 | 使用场景 |
|--------|------|----------|
| CRITICAL (1) | 关键测试 | 核心功能，失败则系统不可用 |
| HIGH (2) | 高优先级 | 重要功能，影响用户体验 |
| MEDIUM (3) | 中优先级 | 一般功能，有替代方案 |
| LOW (4) | 低优先级 | 边缘功能，影响较小 |

---

## 常见问题处理

### 评估结果不稳定
**原因**: 测试用例执行顺序、外部依赖
**解决**: 使用固定随机种子、隔离外部依赖、多次运行取平均值

### 指标计算异常
**原因**: 空数据、除零错误
**解决**: 指标类已处理空数据情况，检查测试用例是否正确记录

### 评分器偏差大
**原因**: 自动评分与人工评分不一致
**解决**: 增加参考解法样本、调整评分权重、引入人工评分校准
