"""任务提取提示词模块

提供从Plan/Spec文档中提取结构化任务的LLM提示词模板，支持：
1. 混合粒度任务提取（根据文档类型动态调整）
2. YAML格式输出，符合TaskNodeInfo结构
3. 支持多个Spec文件拼接提取
"""

from typing import Dict, Any, List, Optional


class TaskExtractionPrompts:
    """任务提取提示词类"""

    TASK_EXTRACTION_SYSTEM = """你是"任务提取专家"——一个擅长从文档中提取结构化任务的AI助手。

【你的职责】
1. 解析Plan/Spec文档中的实施步骤和功能点
2. 将步骤转换为可执行的任务项（符合TaskNodeInfo格式）
3. 识别任务间的依赖关系
4. 分配优先级和预估工时

【任务提取原则】
1. 完整性：不遗漏文档中的任何步骤
2. 结构化：每个任务都有明确属性（id, type, description, inputs, outputs, dependencies）
3. 可执行：任务粒度适中，可独立完成
4. 可追溯：保留与原文档的对应关系

【粒度控制策略】
- Plan文档：粗粒度（按阶段划分，每个阶段2-5个任务）
- Spec文档：细粒度（按功能模块划分，每个接口/功能1-3个任务）
- 混合模式：根据内容自动调整（核心功能细粒度，辅助功能粗粒度）

【输出格式要求】
必须输出符合YAML格式的任务列表，可直接解析为TaskNodeInfo列表。"""

    @staticmethod
    def get_plan_task_extraction_prompt(
        plan_document: str,
        water_business_type: str = "flood_warning",
    ) -> str:
        """获取Plan文档任务提取提示词

        Args:
            plan_document: Plan文档内容
            water_business_type: 水利业务类型

        Returns:
            任务提取提示词
        """
        return f"""【任务】
请从以下Plan文档中提取任务列表（粗粒度）。

【Plan文档内容】
{plan_document}

【业务类型】
{water_business_type}

【提取策略】
Plan文档采用粗粒度提取：
- 按阶段划分任务（需求分析、设计、开发、测试、部署）
- 每个阶段提取2-5个核心任务
- 关注里程碑和交付物
- 任务粒度：阶段级别（5-10天/任务）

【输出要求】
请按以下YAML格式输出任务列表：

```yaml
# 任务分解（Plan模式-粗粒度）
tasks:
  - task_id: "plan_task_001"
    task_type: "execution"
    description: "需求调研与分析：调研现有系统、收集用户需求、分析业务流程"
    inputs: []
    outputs: ["requirements_doc", "business_flow"]
    dependencies: []
    estimated_time: 2880  # 5天 = 5*24*60分钟
    metadata:
      source: "plan_document"
      phase: "需求分析"
      deliverable: "《需求规格说明书》"
      priority: "P0"
      
  - task_id: "plan_task_002"
    task_type: "execution"
    description: "系统架构设计：设计系统整体架构、技术选型、模块划分"
    inputs: ["requirements_doc"]
    outputs: ["architecture_doc", "tech_stack"]
    dependencies: ["plan_task_001"]
    estimated_time: 2880
    metadata:
      source: "plan_document"
      phase: "设计"
      deliverable: "《系统架构设计文档》"
      priority: "P0"
      
  - task_id: "plan_task_003"
    task_type: "execution"
    description: "核心功能开发：开发数据采集、洪水预报、预警发布等核心模块"
    inputs: ["architecture_doc"]
    outputs: ["core_modules", "source_code"]
    dependencies: ["plan_task_002"]
    estimated_time: 11520  # 8天
    metadata:
      source: "plan_document"
      phase: "开发"
      deliverable: "核心功能模块代码"
      priority: "P0"
      
  - task_id: "plan_task_004"
    task_type: "verification"
    description: "系统集成测试：进行功能测试、性能测试、安全测试"
    inputs: ["core_modules"]
    outputs: ["test_report", "bug_list"]
    dependencies: ["plan_task_003"]
    estimated_time: 4320  # 3天
    metadata:
      source: "plan_document"
      phase: "测试"
      deliverable: "《测试报告》"
      priority: "P0"
      
  - task_id: "plan_task_005"
    task_type: "execution"
    description: "系统部署上线：部署到生产环境、配置监控、用户培训"
    inputs: ["test_report"]
    outputs: ["deployed_system", "user_manual"]
    dependencies: ["plan_task_004"]
    estimated_time: 2880  # 2天
    metadata:
      source: "plan_document"
      phase: "部署"
      deliverable: "《部署完成报告》"
      priority: "P0"

# 依赖关系图
dependencies:
  plan_task_001: []
  plan_task_002: ["plan_task_001"]
  plan_task_003: ["plan_task_002"]
  plan_task_004: ["plan_task_003"]
  plan_task_005: ["plan_task_004"]

# 阶段划分
phases:
  - name: "需求分析"
    tasks: ["plan_task_001"]
    duration: "5天"
    
  - name: "系统设计"
    tasks: ["plan_task_002"]
    duration: "5天"
    
  - name: "核心开发"
    tasks: ["plan_task_003"]
    duration: "8天"
    
  - name: "测试验证"
    tasks: ["plan_task_004"]
    duration: "3天"
    
  - name: "部署上线"
    tasks: ["plan_task_005"]
    duration: "2天"

# 里程碑
milestones:
  - name: "M1-需求确认"
    task: "plan_task_001"
    criteria: ["需求文档评审通过"]
    
  - name: "M2-设计完成"
    task: "plan_task_002"
    criteria: ["架构设计评审通过"]
    
  - name: "M3-开发完成"
    task: "plan_task_003"
    criteria: ["核心功能开发完成"]
    
  - name: "M4-测试通过"
    task: "plan_task_004"
    criteria: ["测试报告通过评审"]
    
  - name: "M5-上线运行"
    task: "plan_task_005"
    criteria: ["系统正式运行"]
```

【质量要求】
1. task_type从预定义类型选择：data_collection, prediction, calculation, decision, execution, verification
2. task_id格式：plan_task_XXX
3. estimated_time单位为分钟（天数*24*60）
4. 保持Plan文档中的阶段划分
5. 每个任务对应一个明确的交付物
6. 依赖关系必须形成有向无环图"""

    @staticmethod
    def get_spec_task_extraction_prompt(
        spec_documents: List[str],
        doc_names: List[str],
        water_business_type: str = "flood_warning",
    ) -> str:
        """获取Spec文档任务提取提示词（支持多文档拼接）

        Args:
            spec_documents: Spec文档内容列表（plan.md, spec.md, tasks.md, checklist.md）
            doc_names: 文档名称列表
            water_business_type: 水利业务类型

        Returns:
            任务提取提示词
        """
        # 拼接多个Spec文档
        docs_content = ""
        for i, (doc_name, doc_content) in enumerate(zip(doc_names, spec_documents)):
            docs_content += f"""
{'='*60}
【文档{i+1}: {doc_name}】
{'='*60}
{doc_content}

"""

        return f"""【任务】
请从以下Spec文档中提取开发任务（细粒度）。

{docs_content}

【业务类型】
{water_business_type}

【提取策略】
Spec文档采用细粒度提取：
- 按功能模块划分任务（数据采集、洪水预报、预警发布等）
- 每个接口/功能点提取1-3个任务
- 关注技术实现细节
- 任务粒度：功能级别（1-3天/任务）
- 区分前端、后端、算法、测试任务

【输出要求】
请按以下YAML格式输出任务列表：

```yaml
# 任务分解（Spec模式-细粒度）
tasks:
  # ========== 数据采集模块 ==========
  - task_id: "spec_task_001"
    task_type: "data_collection"
    description: "开发水文数据接收接口：实现POST /api/v1/hydrology/data，接收雨量站、水位站监测数据"
    inputs: []
    outputs: ["hydrology_data", "station_records"]
    dependencies: []
    estimated_time: 960  # 2天
    metadata:
      source: "spec.md"
      module: "数据采集"
      api_endpoint: "/api/v1/hydrology/data"
      tech_stack: ["Python", "Flask", "PostgreSQL"]
      priority: "P0"
      acceptance_criteria:
        - "接口符合SL 651数据格式"
        - "支持≥1000测点并发接入"
        - "数据延迟<5分钟"
      
  - task_id: "spec_task_002"
    task_type: "data_collection"
    description: "实现数据质量检查：异常值检测、数据插值补全、质量标记"
    inputs: ["hydrology_data"]
    outputs: ["quality_checked_data", "quality_flags"]
    dependencies: ["spec_task_001"]
    estimated_time: 720  # 1.5天
    metadata:
      source: "spec.md"
      module: "数据采集"
      algorithm: ["异常检测", "插值算法"]
      priority: "P0"
      
  # ========== 洪水预报模块 ==========
  - task_id: "spec_task_003"
    task_type: "prediction"
    description: "开发洪水预报模型：实现24小时预见期的洪水预报，洪峰误差<20%"
    inputs: ["quality_checked_data", "rainfall_forecast"]
    outputs: ["flood_forecast", "peak_flow_prediction"]
    dependencies: ["spec_task_002"]
    estimated_time: 2400  # 5天
    metadata:
      source: "spec.md"
      module: "洪水预报"
      model_type: "概念性水文模型/机器学习"
      accuracy_requirement: "洪峰误差<20%，峰现时间误差<6h"
      standard: "SL 250"
      priority: "P0"
      
  - task_id: "spec_task_004"
    task_type: "calculation"
    description: "实现预报模型训练和调优：参数率定、模型验证、精度评估"
    inputs: ["historical_flood_data"]
    outputs: ["trained_model", "model_metrics"]
    dependencies: ["spec_task_003"]
    estimated_time: 1440  # 3天
    metadata:
      source: "spec.md"
      module: "洪水预报"
      task_type: "模型训练"
      priority: "P0"
      
  # ========== 预警发布模块 ==========
  - task_id: "spec_task_005"
    task_type: "calculation"
    description: "开发预警等级判定引擎：实现蓝黄橙红四级预警判定逻辑"
    inputs: ["flood_forecast", "warning_thresholds"]
    outputs: ["warning_level", "warning_trigger"]
    dependencies: ["spec_task_003"]
    estimated_time: 960  # 2天
    metadata:
      source: "spec.md"
      module: "预警发布"
      logic: "蓝色(0.9)、黄色(1.0)、橙色(1.1)、红色(1.2)"
      priority: "P0"
      
  - task_id: "spec_task_006"
    task_type: "execution"
    description: "开发预警信息发布功能：支持短信、APP、广播多渠道发布"
    inputs: ["warning_trigger"]
    outputs: ["sent_notifications", "delivery_status"]
    dependencies: ["spec_task_005"]
    estimated_time: 1440  # 3天
    metadata:
      source: "spec.md"
      module: "预警发布"
      channels: ["短信", "APP推送", "广播"]
      priority: "P0"
      
  # ========== 前端界面模块 ==========
  - task_id: "spec_task_007"
    task_type: "execution"
    description: "开发数据监控界面：实时展示水文监测数据、数据质量状态"
    inputs: ["quality_checked_data"]
    outputs: ["monitoring_ui"]
    dependencies: ["spec_task_002"]
    estimated_time: 1440  # 3天
    metadata:
      source: "spec.md"
      module: "前端界面"
      tech_stack: ["React", "TypeScript"]
      priority: "P1"
      
  - task_id: "spec_task_008"
    task_type: "execution"
    description: "开发预警管理界面：预警列表、预警详情、预警确认"
    inputs: ["warning_trigger", "sent_notifications"]
    outputs: ["warning_management_ui"]
    dependencies: ["spec_task_006"]
    estimated_time: 960  # 2天
    metadata:
      source: "spec.md"
      module: "前端界面"
      tech_stack: ["React", "TypeScript"]
      priority: "P1"
      
  # ========== 测试验证模块 ==========
  - task_id: "spec_task_009"
    task_type: "verification"
    description: "编写单元测试：核心模块单元测试覆盖率>80%"
    inputs: ["source_code"]
    outputs: ["unit_test_report", "coverage_report"]
    dependencies: ["spec_task_003", "spec_task_006"]
    estimated_time: 960  # 2天
    metadata:
      source: "checklist.md"
      module: "测试"
      test_type: "单元测试"
      coverage_requirement: ">80%"
      priority: "P0"
      
  - task_id: "spec_task_010"
    task_type: "verification"
    description: "执行集成测试：验证各模块协同工作，接口兼容性"
    inputs: ["core_modules"]
    outputs: ["integration_test_report"]
    dependencies: ["spec_task_009"]
    estimated_time: 720  # 1.5天
    metadata:
      source: "checklist.md"
      module: "测试"
      test_type: "集成测试"
      priority: "P0"

# 依赖关系图（按模块分组）
dependencies:
  # 数据采集模块
  spec_task_001: []
  spec_task_002: ["spec_task_001"]
  
  # 洪水预报模块
  spec_task_003: ["spec_task_002"]
  spec_task_004: ["spec_task_003"]
  
  # 预警发布模块
  spec_task_005: ["spec_task_003"]
  spec_task_006: ["spec_task_005"]
  
  # 前端界面模块
  spec_task_007: ["spec_task_002"]
  spec_task_008: ["spec_task_006"]
  
  # 测试验证模块
  spec_task_009: ["spec_task_003", "spec_task_006"]
  spec_task_010: ["spec_task_009"]

# 模块划分
modules:
  - name: "数据采集"
    tasks: ["spec_task_001", "spec_task_002"]
    duration: "3.5天"
    
  - name: "洪水预报"
    tasks: ["spec_task_003", "spec_task_004"]
    duration: "8天"
    
  - name: "预警发布"
    tasks: ["spec_task_005", "spec_task_006"]
    duration: "5天"
    
  - name: "前端界面"
    tasks: ["spec_task_007", "spec_task_008"]
    duration: "5天"
    
  - name: "测试验证"
    tasks: ["spec_task_009", "spec_task_010"]
    duration: "3.5天"

# 资源分配
resources:
  - role: "后端工程师"
    tasks: ["spec_task_001", "spec_task_002", "spec_task_003", "spec_task_004", "spec_task_005", "spec_task_006"]
    
  - role: "前端工程师"
    tasks: ["spec_task_007", "spec_task_008"]
    
  - role: "测试工程师"
    tasks: ["spec_task_009", "spec_task_010"]

# 与Plan文档任务的映射关系
mapping_to_plan:
  plan_task_003:  # 核心功能开发
    - "spec_task_001"
    - "spec_task_002"
    - "spec_task_003"
    - "spec_task_004"
    - "spec_task_005"
    - "spec_task_006"
    
  plan_task_004:  # 系统集成测试
    - "spec_task_009"
    - "spec_task_010"
```

【质量要求】
1. task_type从预定义类型选择
2. task_id格式：spec_task_XXX
3. estimated_time单位为分钟
4. 按功能模块组织任务
5. 每个任务包含技术要点和验收标准（来自checklist.md）
6. 明确前后端、算法、测试任务分工
7. 包含与Plan文档任务的映射关系
8. 依赖关系必须形成有向无环图

【提取规则】
1. 从spec.md提取：系统架构、数据模型、接口设计、算法方案
2. 从tasks.md提取：任务分解、依赖关系、工时估算
3. 从checklist.md提取：验收标准、检查项
4. 合并重复任务，保留最详细的描述
5. 确保任务覆盖所有功能点"""

    @staticmethod
    def get_mixed_granularity_prompt(
        plan_doc: str,
        spec_docs: List[str],
        doc_names: List[str],
        water_business_type: str = "flood_warning",
    ) -> str:
        """获取混合粒度任务提取提示词

        结合Plan文档的粗粒度和Spec文档的细粒度，生成混合粒度的任务列表。

        Args:
            plan_doc: Plan文档内容
            spec_docs: Spec文档内容列表
            doc_names: 文档名称列表
            water_business_type: 水利业务类型

        Returns:
            混合粒度任务提取提示词
        """
        # 拼接Spec文档
        specs_content = ""
        for i, (doc_name, doc_content) in enumerate(zip(doc_names, spec_docs)):
            specs_content += f"""
{'='*60}
【文档{i+1}: {doc_name}】
{'='*60}
{doc_content}

"""

        return f"""【任务】
请从以下Plan和Spec文档中提取混合粒度的任务列表。

【Plan文档】
{'='*60}
{plan_doc}

【Spec文档集合】
{specs_content}

【业务类型】
{water_business_type}

【混合粒度策略】
根据任务重要性和复杂度动态调整粒度：

**粗粒度任务（阶段级别）：**
- 项目管理类任务（需求分析、项目协调）
- 跨模块集成任务
- 部署运维类任务
- 预估工时：3-5天

**细粒度任务（功能级别）：**
- 核心算法类任务（洪水预报模型）
- 关键接口开发（数据接入API）
- 复杂业务逻辑（预警判定引擎）
- 预估工时：1-3天

**中等粒度任务（模块级别）：**
- 通用功能开发（前端界面、测试）
- 标准接口实现
- 预估工时：2-3天

【输出要求】
请按以下YAML格式输出混合粒度的任务列表：

```yaml
# 混合粒度任务分解
tasks:
  # ========== 粗粒度：项目管理 ==========
  - task_id: "mix_task_001"
    task_type: "execution"
    description: "项目启动与需求分析：完成需求调研、方案设计、项目计划制定"
    inputs: []
    outputs: ["project_plan", "requirements_spec"]
    dependencies: []
    estimated_time: 4320  # 3天（粗粒度）
    granularity: "coarse"
    metadata:
      phase: "项目管理"
      includes: ["需求调研", "方案设计", "计划制定"]
      priority: "P0"
      
  # ========== 细粒度：核心算法 ==========
  - task_id: "mix_task_002"
    task_type: "prediction"
    description: "洪水预报模型开发：实现24小时预见期预报，洪峰误差<20%"
    inputs: ["hydrology_data"]
    outputs: ["flood_forecast_model"]
    dependencies: ["mix_task_001"]
    estimated_time: 2400  # 5天（细粒度，核心算法）
    granularity: "fine"
    metadata:
      module: "核心算法"
      algorithm: "概念性水文模型"
      accuracy: "洪峰误差<20%"
      standard: "SL 250"
      priority: "P0"
      
  - task_id: "mix_task_003"
    task_type: "calculation"
    description: "预报模型参数调优：模型训练、参数率定、精度验证"
    inputs: ["flood_forecast_model", "historical_data"]
    outputs: ["tuned_model", "model_metrics"]
    dependencies: ["mix_task_002"]
    estimated_time: 1440  # 2天（细粒度）
    granularity: "fine"
    metadata:
      module: "核心算法"
      task: "模型调优"
      priority: "P0"
      
  # ========== 中等粒度：功能开发 ==========
  - task_id: "mix_task_004"
    task_type: "execution"
    description: "数据采集与处理模块：开发数据接入接口、质量检查、存储管理"
    inputs: []
    outputs: ["data_module"]
    dependencies: ["mix_task_001"]
    estimated_time: 2880  # 4天（中等粒度）
    granularity: "medium"
    metadata:
      module: "数据采集"
      includes: ["接口开发", "质量检查", "数据存储"]
      priority: "P0"
      
  - task_id: "mix_task_005"
    task_type: "execution"
    description: "预警发布模块：预警判定、多渠道发布、发布记录"
    inputs: ["flood_forecast_model"]
    outputs: ["warning_module"]
    dependencies: ["mix_task_002"]
    estimated_time: 1440  # 2天（中等粒度）
    granularity: "medium"
    metadata:
      module: "预警发布"
      includes: ["判定引擎", "发布功能", "记录管理"]
      priority: "P0"
      
  # ========== 粗粒度：测试部署 ==========
  - task_id: "mix_task_006"
    task_type: "verification"
    description: "系统测试与验收：单元测试、集成测试、性能测试、安全测试"
    inputs: ["data_module", "flood_forecast_model", "warning_module"]
    outputs: ["test_reports", "accepted_system"]
    dependencies: ["mix_task_003", "mix_task_004", "mix_task_005"]
    estimated_time: 4320  # 3天（粗粒度）
    granularity: "coarse"
    metadata:
      phase: "测试验收"
      includes: ["单元测试", "集成测试", "性能测试", "安全测试"]
      priority: "P0"
      
  - task_id: "mix_task_007"
    task_type: "execution"
    description: "系统部署与交付：生产环境部署、监控配置、用户培训、文档交付"
    inputs: ["accepted_system"]
    outputs: ["deployed_system", "user_manual"]
    dependencies: ["mix_task_006"]
    estimated_time: 2880  # 2天（粗粒度）
    granularity: "coarse"
    metadata:
      phase: "部署交付"
      includes: ["环境部署", "监控配置", "用户培训", "文档交付"]
      priority: "P0"

# 粒度分布统计
granularity_stats:
  coarse:
    count: 3
    tasks: ["mix_task_001", "mix_task_006", "mix_task_007"]
    total_time: 11520  # 8天
    percentage: 35%
    
  medium:
    count: 2
    tasks: ["mix_task_004", "mix_task_005"]
    total_time: 4320  # 6天
    percentage: 26%
    
  fine:
    count: 2
    tasks: ["mix_task_002", "mix_task_003"]
    total_time: 3840  # 8天
    percentage: 39%

# 依赖关系
dependencies:
  mix_task_001: []
  mix_task_002: ["mix_task_001"]
  mix_task_003: ["mix_task_002"]
  mix_task_004: ["mix_task_001"]
  mix_task_005: ["mix_task_002"]
  mix_task_006: ["mix_task_003", "mix_task_004", "mix_task_005"]
  mix_task_007: ["mix_task_006"]

# 与Plan文档的映射
plan_mapping:
  plan_task_001: ["mix_task_001"]  # 需求分析
  plan_task_002: ["mix_task_001"]  # 架构设计（合并到项目管理）
  plan_task_003: ["mix_task_002", "mix_task_003", "mix_task_004", "mix_task_005"]  # 核心开发
  plan_task_004: ["mix_task_006"]  # 测试
  plan_task_005: ["mix_task_007"]  # 部署

# 与Spec文档的映射
spec_mapping:
  spec_task_001: ["mix_task_004"]  # 数据接口
  spec_task_002: ["mix_task_004"]  # 质量检查
  spec_task_003: ["mix_task_002"]  # 预报模型
  spec_task_004: ["mix_task_003"]  # 模型调优
  spec_task_005: ["mix_task_005"]  # 预警判定
  spec_task_006: ["mix_task_005"]  # 预警发布
```

【质量要求】
1. 根据任务性质选择合适的粒度
2. 核心算法和关键功能使用细粒度
3. 项目管理和测试部署使用粗粒度
4. 通用功能使用中等粒度
5. 保持与Plan和Spec文档的映射关系
6. 粒度分布合理（细粒度30-40%，中等粒度20-30%，粗粒度30-40%）
7. 所有任务符合TaskNodeInfo格式"""
