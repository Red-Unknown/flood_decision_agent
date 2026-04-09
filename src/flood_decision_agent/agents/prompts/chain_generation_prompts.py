"""决策链生成提示词模块

提供决策链生成的LLM提示词模板，支持：
1. LLM辅助规则库的任务分解
2. 根据优化器策略动态调整备选链数量
3. YAML格式输出，符合TaskNodeInfo结构
"""

from typing import Dict, Any, Optional


class ChainGenerationPrompts:
    """决策链生成提示词类"""

    # 优化器策略配置
    OPTIMIZER_STRATEGIES = {
        "simple": {
            "name": "轻量级优化",
            "alternatives": 1,
            "reliability_threshold": 0.6,
            "iterations": 0,
            "description": "快速响应，1个备用链路，无迭代优化",
        },
        "plan": {
            "name": "Plan模式优化",
            "alternatives": 3,
            "reliability_threshold": 0.75,
            "iterations": 2,
            "description": "平衡质量和速度，2-3个备选方案，2次迭代",
        },
        "spec": {
            "name": "Spec模式优化",
            "alternatives": 6,
            "reliability_threshold": 0.85,
            "iterations": 3,
            "description": "确保功能完善，4-6个备选方案，3次迭代",
        },
    }

    CHAIN_GENERATION_SYSTEM = """你是"决策链生成专家"——一个精通工作流设计和任务分解的AI助手。

【你的职责】
1. 分析用户意图，理解业务目标
2. 基于规则库进行初始任务分解
3. 使用LLM优化和补充任务链
4. 生成符合优化器策略的备选决策链

【决策链设计原则】
1. 逆向思维：从最终目标倒推所需步骤
2. 数据驱动：明确每个任务的输入输出
3. 依赖清晰：形成有向无环图（DAG）
4. 粒度适中：任务可独立执行，避免过细

【任务类型定义】
- data_collection: 数据采集（获取外部数据）
- prediction: 预测任务（模型推理、预报）
- calculation: 计算任务（数值计算、分析）
- decision: 决策任务（方案选择、判断）
- execution: 执行任务（操作控制、下发指令）
- verification: 验证任务（结果校验、评估）

【水利行业特殊考虑】
- 数据时效性：实时监测数据更新频率（5分钟）
- 安全约束：调度决策必须符合安全规程（SL标准）
- 多源数据：整合气象、水文、工程数据
- 时效要求：洪水预报的预见期要求（24-48小时）

【输出格式要求】
必须输出符合YAML格式的决策链定义，可直接解析为TaskNodeInfo列表。"""

    @staticmethod
    def get_chain_generation_prompt(
        user_input: str,
        business_type: str,
        execution_type: str,
        entities: Dict[str, Any],
        mcp_tools: list,
        optimizer_strategy: str = "plan",
        rule_based_tasks: Optional[list] = None,
    ) -> str:
        """获取决策链生成提示词

        Args:
            user_input: 用户输入
            business_type: 业务类型
            execution_type: 执行类型
            entities: 提取的实体
            mcp_tools: 可用的MCP工具列表
            optimizer_strategy: 优化器策略（simple/plan/spec）
            rule_based_tasks: 规则库生成的初始任务（可选）

        Returns:
            决策链生成提示词
        """
        strategy = ChainGenerationPrompts.OPTIMIZER_STRATEGIES.get(
            optimizer_strategy, ChainGenerationPrompts.OPTIMIZER_STRATEGIES["plan"]
        )

        rule_tasks_str = ""
        if rule_based_tasks:
            import yaml
            rule_tasks_str = f"""
【规则库初始任务】
以下是由规则库生成的初始任务分解，请在此基础上进行优化和补充：

```yaml
{yaml.dump(rule_based_tasks, allow_unicode=True, sort_keys=False)}
```

请分析以上规则库任务的合理性，进行以下优化：
1. 补充缺失的任务步骤
2. 优化任务依赖关系
3. 调整任务粒度
4. 为任务匹配合适的工具"""

        mcp_tools_str = "\n".join([f"- {tool['name']}: {tool.get('description', '')}" for tool in mcp_tools]) if mcp_tools else "无"

        return f"""【任务】
请根据以下信息生成决策链。

【用户输入】
{user_input}

【意图解析结果】
- 业务类型：{business_type}
- 执行类型：{execution_type}
- 关键实体：{entities}

【可用MCP工具】
{mcp_tools_str}

【优化器策略】
- 策略名称：{strategy['name']}
- 备选链数量：{strategy['alternatives']}个
- 可靠性阈值：{strategy['reliability_threshold']}
- 迭代次数：{strategy['iterations']}
- 策略说明：{strategy['description']}
{rule_tasks_str}

【输出要求】
请按以下YAML格式输出决策链：

```yaml
# 决策链定义
chain:
  name: "决策链名称"
  description: "决策链描述"
  version: "1.0"
  
  # 主决策链
  primary:
    tasks:
      - task_id: "task_001"
        task_type: "data_collection"
        description: "采集降雨数据"
        inputs: []
        outputs: ["rainfall_data"]
        dependencies: []
        tool: "可选的MCP工具名称"
        estimated_time: 5
        metadata:
          priority: "P0"
          retry_count: 3
          
      - task_id: "task_002"
        task_type: "data_collection"
        description: "采集上游流量数据"
        inputs: []
        outputs: ["upstream_flow"]
        dependencies: []
        tool: ""
        estimated_time: 5
        metadata:
          priority: "P0"
          retry_count: 3
          
      - task_id: "task_003"
        task_type: "prediction"
        description: "预测未来来水"
        inputs: ["rainfall_data", "upstream_flow"]
        outputs: ["inflow_forecast"]
        dependencies: ["task_001", "task_002"]
        tool: "flood_forecast_model"
        estimated_time: 30
        metadata:
          priority: "P0"
          model_version: "v2.1"
          
      - task_id: "task_004"
        task_type: "data_collection"
        description: "获取当前水库状态"
        inputs: []
        outputs: ["current_state", "water_level", "inflow_rate"]
        dependencies: []
        tool: "reservoir_monitor"
        estimated_time: 2
        metadata:
          priority: "P0"
          
      - task_id: "task_005"
        task_type: "calculation"
        description: "计算调度方案"
        inputs: ["inflow_forecast", "current_state"]
        outputs: ["dispatch_plan"]
        dependencies: ["task_003", "task_004"]
        tool: "dispatch_optimizer"
        estimated_time: 10
        metadata:
          priority: "P0"
          
      - task_id: "task_006"
        task_type: "decision"
        description: "审核调度方案"
        inputs: ["dispatch_plan"]
        outputs: ["approved_plan"]
        dependencies: ["task_005"]
        tool: ""
        estimated_time: 5
        metadata:
          priority: "P0"
          requires_human: true
          
      - task_id: "task_007"
        task_type: "execution"
        description: "执行调度操作"
        inputs: ["approved_plan"]
        outputs: ["execution_result", "outflow_rate"]
        dependencies: ["task_006"]
        tool: "gate_controller"
        estimated_time: 10
        metadata:
          priority: "P0"
          safety_check: true
          
      - task_id: "task_008"
        task_type: "verification"
        description: "验证执行结果"
        inputs: ["execution_result", "outflow_rate"]
        outputs: ["verification_result"]
        dependencies: ["task_007"]
        tool: ""
        estimated_time: 5
        metadata:
          priority: "P1"

  # 备选决策链（根据优化器策略动态生成{strategy['alternatives']}个）
  alternatives:
    - name: "备选链1-保守调度"
      description: "安全优先的调度策略，降低出库流量，增加安全裕度"
      strategy: "conservative"
      modifications:
        - "task_005: 增加安全约束检查"
        - "task_007: 降低出库流量变化速率"
      tasks:
        # 与主链相同的任务结构，但参数不同
        - task_id: "task_005_alt1"
          task_type: "calculation"
          description: "计算保守调度方案"
          inputs: ["inflow_forecast", "current_state"]
          outputs: ["dispatch_plan_conservative"]
          dependencies: ["task_003", "task_004"]
          tool: "dispatch_optimizer"
          estimated_time: 10
          metadata:
            priority: "P0"
            strategy: "conservative"
            safety_margin: 1.2

    - name: "备选链2-快速响应"
      description: "时效优先的调度策略，缩短决策时间"
      strategy: "fast_response"
      modifications:
        - "task_003: 使用简化预报模型"
        - "task_005: 使用预计算方案"
      tasks:
        # 简化版任务链
        - task_id: "task_003_alt2"
          task_type: "prediction"
          description: "快速预报（简化模型）"
          inputs: ["rainfall_data", "upstream_flow"]
          outputs: ["inflow_forecast_quick"]
          dependencies: ["task_001", "task_002"]
          tool: "flood_forecast_model_fast"
          estimated_time: 10
          metadata:
            priority: "P0"
            model_type: "simplified"

  # 数据流说明
  data_flow:
    - "步骤1: 数据采集（降雨、流量）-> task_001, task_002"
    - "步骤2: 洪水预报（预测入库流量）-> task_003"
    - "步骤3: 状态获取（当前水库状态）-> task_004"
    - "步骤4: 调度计算（生成调度方案）-> task_005"
    - "步骤5: 方案审核（人工/自动审核）-> task_006"
    - "步骤6: 方案执行（控制闸门开度）-> task_007"
    - "步骤7: 结果验证（监测实际出库）-> task_008"

  # 可靠性评估
  reliability:
    primary_score: 0.85
    threshold: {strategy['reliability_threshold']}
    issues: []
    passed: true

  # 优化信息
  optimization:
    strategy: "{optimizer_strategy}"
    iterations: {strategy['iterations']}
    alternatives_generated: {strategy['alternatives']}
    generation_time: "2024-01-01T12:00:00Z"
```

【质量要求】
1. task_type必须从预定义类型中选择：data_collection, prediction, calculation, decision, execution, verification
2. task_id必须唯一，格式为task_XXX或task_XXX_altN
3. 依赖关系必须形成有向无环图（DAG），不能循环依赖
4. 每个任务都有明确的inputs和outputs
5. 优先使用可用的MCP工具（在tool字段指定）
6. 根据优化器策略生成{strategy['alternatives']}个备选决策链
7. 备选链应与主链有实质性差异（策略不同），而非简单复制
8. estimated_time单位为分钟
9. metadata可包含额外信息如priority、retry_count等

【TaskNodeInfo格式对照】
生成的YAML任务必须可直接映射为TaskNodeInfo：
- task_id -> task_id
- task_type -> task_type (TaskType枚举)
- description -> description
- inputs -> inputs (List[str])
- outputs -> outputs (List[str])
- dependencies -> dependencies (List[str])
- metadata -> metadata (Dict[str, Any])"""

    @staticmethod
    def get_chain_optimization_prompt(
        current_chain: Dict[str, Any],
        issues: list,
        iteration: int,
        max_iterations: int,
    ) -> str:
        """获取决策链优化提示词

        Args:
            current_chain: 当前决策链
            issues: 发现的问题列表
            iteration: 当前迭代次数
            max_iterations: 最大迭代次数

        Returns:
            决策链优化提示词
        """
        import yaml

        return f"""【任务】
请优化以下决策链（第{iteration}/{max_iterations}次迭代）。

【当前决策链】
```yaml
{yaml.dump(current_chain, allow_unicode=True, sort_keys=False)}
```

【发现的问题】
{chr(10).join([f"- {issue}" for issue in issues])}

【优化要求】
1. 修复上述问题
2. 提高可靠性评分（目标>0.75）
3. 优化任务依赖关系
4. 补充缺失的任务步骤
5. 调整任务粒度

【输出要求】
请输出优化后的决策链YAML，格式如下：

```yaml
# 优化后的决策链
name: "决策链名称"
strategy: "优化策略"
tasks:
  - task_id: "task_001"
    task_type: "data_collection"
    description: "优化后的任务描述"
    inputs: []
    outputs: ["output1"]
    dependencies: []
    estimated_time: 10
    metadata:
      priority: "P0"
      
  - task_id: "task_002"
    task_type: "prediction"
    description: "优化后的任务描述"
    inputs: ["output1"]
    outputs: ["output2"]
    dependencies: ["task_001"]
    estimated_time: 20
    metadata:
      priority: "P0"

# 优化信息
optimization:
  iteration: {iteration}
  changes:
    - "修复了XX问题"
    - "优化了XX依赖"
  improvement: "优化说明，如：减少了依赖层级，提高了并行度"
  reliability_score: 0.90
```

【重要提示】
1. 必须包含 `tasks:` 键，所有任务放在该列表下
2. 保持原有task_id不变
3. 只返回优化后的决策链，不要返回多个备选链
4. 确保YAML格式正确，缩进使用2个空格

【质量要求】
1. 保持YAML格式正确
2. 保持task_id不变
3. 保持数据流逻辑正确
4. 确保所有依赖关系有效
5. 必须包含 `tasks:` 键"""
