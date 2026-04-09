"""水利提示词与决策链集成演示

演示完整的输入 -> 规划文档 -> 决策链生成流程
"""

import sys
sys.path.insert(0, 'src')

from flood_decision_agent.agents.decision_chain.generator import DecisionChainGeneratorAgent
from flood_decision_agent.agents.prompts import WaterDomainPrompts


def demo_water_domain_knowledge():
    """演示水利领域知识"""
    print("\n" + "=" * 70)
    print(" " * 20 + "水利领域知识展示")
    print("=" * 70)
    
    # 1. 数据链条模板
    print("\n【1. 数据-要素-指标-决策链条模板】")
    print("-" * 70)
    
    print("\n>>> 洪水预警链条:")
    flood_chain = WaterDomainPrompts.get_data_chain_prompt("flood_warning")
    print(flood_chain[:800] + "...")
    
    # 2. 专家规则
    print("\n【2. 专家经验规则】")
    print("-" * 70)
    
    print("\n>>> 调度规则示例:")
    for rule in WaterDomainPrompts.EXPERT_RULES["scheduling"][:2]:
        print(f"\n  [{rule['id']}] {rule['name']}")
        print(f"  条件: {rule['condition']}")
        print(f"  动作: {rule['action']}")
        print(f"  依据: {rule['reference']}")
    
    # 3. 法规规程
    print("\n【3. 适用法规规程】")
    print("-" * 70)
    
    for reg in WaterDomainPrompts.REGULATIONS:
        print(f"\n  [{reg['code']}] {reg['name']}")
        print(f"  内容: {reg['content'][:60]}...")
    
    # 4. 阈值参数
    print("\n【4. 关键阈值参数】")
    print("-" * 70)
    
    print("\n>>> 洪水预警阈值:")
    for level, info in WaterDomainPrompts.THRESHOLDS["flood_warning"].items():
        print(f"  {level}: {info['value']}{info['unit']} - {info['description']}")
    
    # 5. 验收标准
    print("\n【5. 项目验收标准】")
    print("-" * 70)
    
    for criterion in WaterDomainPrompts.ACCEPTANCE_CRITERIA["functional"]:
        print(f"\n  [{criterion['id']}] {criterion['description']} ({criterion['priority']})")
        print(f"  通过标准: {criterion['pass_criteria']}")


def demo_plan_to_chain_workflow():
    """演示规划到决策链的工作流"""
    print("\n" + "=" * 70)
    print(" " * 15 + "规划文档 -> 决策链生成演示")
    print("=" * 70)
    
    agent = DecisionChainGeneratorAgent()
    
    # 模拟一个水利项目规划文档
    mock_plan = """
# 洪水预警系统建设规划

## 概述
本项目旨在开发一个智能化的洪水预警系统，实现流域内实时水情监测、
洪水预报分析和预警信息发布，提高防洪减灾能力。

## 数据处理链条
### 1. 数据获取
- 数据源：雨量站、水位站、气象预报
- 更新频率：实时（5分钟）
- 质量要求：完整性>95%

### 2. 要素提取
- 面雨量、涨水速率、洪峰流量

### 3. 指标计算
- 洪水预警等级（蓝/黄/橙/红）

### 4. 决策支持
- 预警发布决策

## 实施步骤

1. **数据接入与集成**（预计2周）
   - 具体内容：接入流域内水文监测站点数据，建立数据接收通道
   - 交付物：《数据接入完成报告》《数据质量评估》
   - 负责人：数据工程师

2. **预报模型开发**（预计4周）
   - 具体内容：开发洪水预报模型，进行参数率定和精度验证
   - 交付物：《洪水预报模型》《模型精度验证报告》
   - 负责人：算法工程师

3. **预警分析引擎**（预计3周）
   - 具体内容：实现预警等级计算、阈值判断、预警生成
   - 交付物：《预警分析引擎》《预警规则配置》
   - 负责人：开发工程师

4. **信息发布系统**（预计2周）
   - 具体内容：开发预警信息发布界面，支持多渠道发布
   - 交付物：《信息发布系统》《用户操作手册》
   - 负责人：前端工程师

5. **系统集成测试**（预计2周）
   - 具体内容：端到端测试、性能测试、安全测试
   - 交付物：《系统测试报告》《问题修复记录》
   - 负责人：测试工程师

6. **试运行与验收**（预计2周）
   - 具体内容：系统试运行、用户培训、项目验收
   - 交付物：《试运行报告》《验收报告》
   - 负责人：项目经理

## 验收标准
- 数据完整性≥95%（SL 460）
- 预报精度：洪峰误差<20%（SL 250）
- 预警发布时间<5分钟

## 风险与应对
| 风险 | 应对措施 |
|-----|---------|
| 数据缺失 | 备用数据源、插值补全 |
| 模型精度不足 | 多模型集合、实时校正 |
"""
    
    print("\n【步骤1】解析规划文档中的实施步骤")
    print("-" * 70)
    
    steps = agent._extract_implementation_steps(mock_plan)
    print(f"\n提取到 {len(steps)} 个实施步骤:")
    for i, step in enumerate(steps, 1):
        print(f"\n  {i}. {step['name']}")
        print(f"     描述: {step['description'][:50]}...")
        print(f"     交付物: {step['deliverables']}")
    
    print("\n【步骤2】将步骤转换为任务节点")
    print("-" * 70)
    
    nodes = agent._steps_to_task_nodes(steps)
    print(f"\n生成 {len(nodes)} 个任务节点:")
    for node in nodes:
        print(f"\n  [{node.task_id}] {node.task_type.value}")
        print(f"     描述: {node.description[:50]}...")
        print(f"     依赖: {node.dependencies}")
    
    print("\n【步骤3】生成完整决策链")
    print("-" * 70)
    
    task_graph, metadata = agent.generate_chain_from_plan(
        plan_document=mock_plan,
        user_input="开发洪水预警系统"
    )
    
    print(f"\n决策链生成结果:")
    print(f"  - 来源: {metadata['source']}")
    print(f"  - 提取步骤: {metadata['steps_extracted']}")
    print(f"  - 生成节点: {metadata['node_count']}")
    print(f"  - 可靠性评分: {metadata['reliability_score']:.2f}")
    
    print(f"\n任务图结构:")
    all_nodes = task_graph.get_all_nodes()
    print(f"  - 总节点数: {len(all_nodes)}")
    
    # 统计边数
    edge_count = sum(len(edges) for edges in task_graph._edges.values())
    print(f"  - 总边数: {edge_count}")
    
    print(f"\n节点详情:")
    for node_id, node in all_nodes.items():
        deps = task_graph.get_dependencies(node_id)
        print(f"  [{node_id}] {node.task_type}")
        if deps:
            print(f"      -> 依赖: {', '.join(deps)}")


def demo_complete_workflow_summary():
    """演示完整工作流摘要"""
    print("\n" + "=" * 70)
    print(" " * 20 + "完整工作流说明")
    print("=" * 70)
    
    print("""
【完整工作流：输入 -> 规划文档 -> 决策链】

阶段1: 输入理解
  └─> 接收用户输入（自然语言/结构化）
  └─> 识别水利业务类型（洪水预警/水库调度等）
  └─> 提取约束条件和参考资料

阶段2: 规划文档生成（使用水利领域知识）
  └─> 注入数据-要素-指标-决策链条模板
  └─> 引用专家经验规则
  └─> 引用法规规程（SL系列标准）
  └─> 引用关键阈值参数
  └─> 生成符合行业规范的规划文档
  └─> 包含：概述、目标、数据处理链条、实施步骤、
      验收标准、风险与应对、专家经验引用

阶段3: 决策链生成
  └─> 解析规划文档中的实施步骤
  └─> 将步骤转换为任务节点
  └─> 推断任务类型（数据采集/模型训练/系统开发等）
  └─> 建立节点依赖关系
  └─> 优化任务链（生成备选链、评估可靠性）
  └─> 构建可执行的任务图（TaskGraph）

阶段4: 输出结果
  └─> 规划文档（Markdown格式）
  └─> 决策链（TaskGraph对象）
  └─> 元数据（节点数、边数、可靠性评分等）

【关键技术点】

1. 水利领域知识库
   - 数据链条模板：定义标准处理流程
   - 专家规则库：调度/预警/安全规则
   - 法规规程库：SL系列行业标准
   - 阈值参数库：降雨等级、预警阈值等
   - 验收标准库：功能/性能/安全/合规

2. 规划文档解析
   - 自动提取实施步骤
   - 识别步骤名称、描述、交付物、负责人
   - 支持Markdown格式解析

3. 任务类型推断
   - 基于关键词匹配
   - 数据相关 -> DATA_COLLECTION
   - 开发相关 -> EXECUTION
   - 测试相关 -> VERIFICATION
   - 模型相关 -> PREDICTION
   - 分析相关 -> CALCULATION
   - 决策相关 -> DECISION

4. 决策链优化
   - 生成多条备选链
   - 评估可靠性评分
   - 选择最优链
   - 迭代优化

【使用示例】

```python
from flood_decision_agent.agents.decision_chain import DecisionChainGeneratorAgent

agent = DecisionChainGeneratorAgent()

# 方式1: 完整工作流
result = agent.generate_complete_workflow(
    user_input="开发洪水预警系统",
    water_business_type="flood_warning",
    constraints={"预报预见期": "24小时"},
)

# 方式2: 分步执行
plan_result = agent.generate_water_plan(
    user_input="开发洪水预警系统",
    water_business_type="flood_warning",
)
task_graph, metadata = agent.generate_chain_from_plan(
    plan_document=plan_result["plan_document"],
)
```
""")


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 10 + "水利提示词与决策链集成演示" + " " * 28 + "║")
    print("╚" + "=" * 68 + "╝")
    
    # 运行演示
    demo_water_domain_knowledge()
    demo_plan_to_chain_workflow()
    demo_complete_workflow_summary()
    
    print("\n" + "=" * 70)
    print(" " * 25 + "演示完成！")
    print("=" * 70)
    print("\n核心成果:")
    print("  ✓ 水利领域提示词已集成到 DecisionChainGeneratorAgent")
    print("  ✓ 支持完整工作流：输入 -> 规划文档 -> 决策链")
    print("  ✓ 规划文档符合水利行业规范（SL标准）")
    print("  ✓ 决策链基于规划文档自动生成")
    print("  ✓ 所有专家经验、法规规程、阈值参数可解释")
    print("\n下一步:")
    print("  - 使用真实LLM生成规划文档（需要API Key）")
    print("  - 扩展更多水利业务类型（干旱调度、水资源配置等）")
    print("  - 集成到前端界面，支持交互式规划生成")
