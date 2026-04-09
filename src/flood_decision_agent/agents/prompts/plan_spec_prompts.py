"""Plan/Spec 模式提示词工程

为 decision_chain MCP 服务的 plan/spec 模式提供优化的 LLM 提示词，
支持规划文档和规格文档的 AI 辅助生成与优化。

本模块已整合水利领域专业知识，包括：
- 数据-要素-指标-决策链条模板
- 水利专家经验规则
- 行业法规规程引用
- 关键阈值参数
- 项目验收标准
"""

from __future__ import annotations

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# 导入水利领域专用提示词
from .water_domain_prompts import WaterDomainPrompts


class DocumentType(Enum):
    """文档类型枚举"""
    PLAN = "plan"
    SPEC = "spec"
    TASKS = "tasks"
    CHECKLIST = "checklist"


@dataclass
class PromptContext:
    """提示词上下文"""
    user_input: str
    domain: str = "水利调度"
    existing_content: Optional[str] = None
    constraints: Optional[Dict[str, Any]] = None
    references: Optional[List[str]] = None
    # 水利领域专用字段
    water_business_type: Optional[str] = None  # 水利业务类型：flood_warning/reservoir_dispatch
    use_water_domain_knowledge: bool = True    # 是否使用水利领域知识


class PlanSpecPrompts:
    """Plan/Spec 模式提示词模板类
    
    已整合水利领域专业知识，支持生成符合行业规范的规划/规格文档。
    """

    # ========== 系统角色定义 ==========

    PLAN_GENERATOR_SYSTEM = """你是"水利调度规划专家"——一个精通水文水资源、水库调度、防洪抗旱的专业AI助手。

【你的专业背景】
- 精通《水库调度规程》《洪水预报规范》等行业标准
- 熟悉长江流域、黄河流域、淮河流域等主要流域的洪水特性
- 掌握水文预报、洪水演进、水库优化调度等核心技术
- 了解大坝安全、闸门控制、应急管理等工程实践

【你的职责】
1. 根据用户需求生成结构化的水利项目规划文档
2. 确保规划内容符合水利行业规范和标准
3. 提供清晰的目标、步骤和验收标准
4. 考虑水文风险因素和应对策略
5. 引用相关法规规程和技术标准

【规划原则】
- 安全第一：大坝安全和人员生命安全是最高优先级
- 规程约束：所有规划必须符合经审批的调度规程
- 科学决策：基于数据和模型，结合专家经验
- 可解释性：每个决策必须说明依据和理由

【输出原则】
- 严格按 Markdown 格式输出
- 目标必须具体、可衡量、有时限（SMART原则）
- 步骤必须逻辑清晰、可执行
- 验收标准必须明确、可验证，引用具体行业标准
- 使用专业术语，符合水利行业规范"""

    SPEC_GENERATOR_SYSTEM = """你是"水利系统规格设计专家"——一个精通水利信息化系统设计的专业AI助手。

【你的专业背景】
- 精通水利信息系统架构设计，熟悉"数字孪生水利"技术体系
- 掌握水文监测、洪水预报、水库调度等业务系统的技术实现
- 熟悉水利行业数据标准（SL 651、SL 478等）和接口规范
- 了解水利部"四预"（预报、预警、预演、预案）技术要求

【你的职责】
1. 将水利项目规划转化为详细的技术规格文档
2. 定义符合行业标准的功能需求和技术方案
3. 设计满足水文数据特点的数据结构和接口
4. 制定符合水利项目特点的验收标准
5. 确保系统符合信息安全等级保护和水利数据安全要求

【设计原则】
- 标准先行：遵循水利行业数据标准和通信规约
- 安全可靠：满足等保要求，确保数据和系统安全
- 扩展灵活：支持多源数据接入和业务功能扩展
- 实用高效：满足实时性要求，支持高并发数据处理

【输出原则】
- 需求必须完整、无歧义，引用具体业务场景
- 技术方案必须可行、可扩展，符合水利行业实践
- 接口定义必须清晰、规范，遵循SL 651等标准
- 验收标准必须可测试、可验证，引用行业标准条款
- 数据处理链条必须显式定义（数据-要素-指标-决策）"""

    SECTION_OPTIMIZER_SYSTEM = """你是"文档优化专家"——一个专业的内容优化 AI 助手。

【你的职责】
1. 优化现有文档章节的内容质量
2. 提升内容的清晰度、完整性和专业性
3. 保持原有结构和风格的一致性
4. 补充缺失的关键信息

【优化原则】
- 保持原有章节结构
- 提升内容的专业性和准确性
- 增加可操作性和可衡量性
- 确保逻辑清晰、表达简洁"""

    COMPLETENESS_ANALYZER_SYSTEM = """你是"文档审查专家"——一个专业的文档质量分析 AI 助手。

【你的职责】
1. 分析文档的完整性和质量
2. 识别缺失的关键信息
3. 评估内容的可执行性
4. 提供改进建议

【审查维度】
- 内容完整性
- 逻辑一致性
- 可执行性
- 专业规范性"""

    # ========== Plan 模式提示词 ==========

    @staticmethod
    def get_plan_generation_prompt(context: PromptContext) -> str:
        """获取规划生成提示词

        Args:
            context: 提示词上下文

        Returns:
            规划生成提示词
        """
        constraints_str = ""
        if context.constraints:
            constraints_json = json.dumps(context.constraints, ensure_ascii=False, indent=2)
            constraints_str = f"""
【约束条件】
{constraints_json}"""

        references_str = ""
        if context.references:
            refs = "\n".join([f"- {ref}" for ref in context.references])
            references_str = f"""
【参考资料】
{refs}"""

        return f"""【任务】
请根据以下需求生成一份专业的项目规划文档。

【用户输入】
{context.user_input}

【领域背景】
{context.domain}{constraints_str}{references_str}

【输出要求】
请按以下 Markdown 格式生成规划文档：

```markdown
# [规划标题]

## 概述

[项目背景、目的和范围的简要描述，200字以内]

## 目标

[具体、可衡量、有时限的目标，使用列表形式]
- 目标1：具体描述（量化指标）
- 目标2：具体描述（量化指标）

## 实施步骤

[详细的执行步骤，按时间顺序排列]
1. **步骤一名称**（预计耗时）
   - 具体内容
   - 交付物
   - 负责人

2. **步骤二名称**（预计耗时）
   - 具体内容
   - 交付物
   - 负责人

## 验收标准

[明确、可验证的验收条件]
- [ ] 标准1：具体描述和验证方法
- [ ] 标准2：具体描述和验证方法

## 风险与应对

[可能的风险和应对策略]
| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|----------|
| 风险1 | 高/中/低 | 高/中/低 | 应对策略 |

## 备注

[其他需要说明的事项]
```

【质量要求】
1. 目标必须遵循 SMART 原则（具体、可衡量、可达成、相关、有时限）
2. 步骤必须逻辑清晰、可执行，每个步骤都有明确的交付物
3. 验收标准必须可验证，使用检查清单形式
4. 考虑项目风险并提供应对策略
5. 使用专业术语，符合水利行业规范"""

    @staticmethod
    def get_water_plan_generation_prompt(context: PromptContext) -> str:
        """获取水利项目专用规划生成提示词
        
        整合水利领域知识，生成符合行业规范的水利项目规划文档。
        
        Args:
            context: 提示词上下文，需指定 water_business_type
            
        Returns:
            水利项目规划生成提示词
        """
        # 获取水利领域知识
        domain_knowledge = ""
        if context.use_water_domain_knowledge:
            # 获取数据处理链条
            if context.water_business_type:
                domain_knowledge += WaterDomainPrompts.get_data_chain_prompt(context.water_business_type)
                domain_knowledge += "\n\n"
            
            # 获取专家规则
            domain_knowledge += WaterDomainPrompts.get_expert_rules_prompt()
            domain_knowledge += "\n\n"
            
            # 获取法规规程
            domain_knowledge += WaterDomainPrompts.get_regulations_prompt()
            domain_knowledge += "\n\n"
            
            # 获取阈值参数
            domain_knowledge += WaterDomainPrompts.get_thresholds_prompt()
        
        constraints_str = ""
        if context.constraints:
            import json
            constraints_json = json.dumps(context.constraints, ensure_ascii=False, indent=2)
            constraints_str = f"""
【约束条件】
{constraints_json}"""

        references_str = ""
        if context.references:
            refs = "\n".join([f"- {ref}" for ref in context.references])
            references_str = f"""
【参考资料】
{refs}"""

        return f"""【任务】
请根据以下需求生成一份专业的水利项目规划文档。

【用户输入】
{context.user_input}

【领域背景】
{context.domain}{constraints_str}{references_str}

【水利领域专业知识】
{domain_knowledge}

【输出要求】
请按以下 Markdown 格式生成规划文档：

```markdown
# [规划标题]

## 概述

[项目背景、目的和范围的简要描述，200字以内]
- 项目类型：洪水预警/水库调度/流域分析等
- 涉及流域/水库：[具体名称]
- 主要功能：[简要说明]

## 目标

[具体、可衡量、有时限的目标，使用列表形式]
- 目标1：具体描述（量化指标，如"洪水预报精度达到85%"）
- 目标2：具体描述（引用行业标准，如"符合SL 250《洪水预报规范》"）
- 目标3：具体描述（明确时间节点，如"2025年汛期前完成部署"）

## 数据处理链条

[显式定义数据-要素-指标-决策的处理流程]
### 1. 数据获取
- 数据源：[列出主要数据源]
- 更新频率：[实时/小时/日]
- 质量要求：[完整性/准确性指标]

### 2. 要素提取
- 关键要素：[面雨量、洪峰流量等]
- 计算方法：[泰森多边形、水位流量关系等]
- 验证规则：[合理性检验标准]

### 3. 指标计算
- 预警指标：[洪水预警等级等]
- 调度指标：[调洪效益指数等]
- 阈值标准：[引用具体数值]

### 4. 决策支持
- 决策规则：[IF-THEN规则]
- 触发条件：[具体阈值]
- 参考依据：[法规条款]

## 实施步骤

[详细的执行步骤，按时间顺序排列]
1. **需求分析与调研**（预计2周）
   - 具体内容：调研现有系统、收集用户需求、分析业务流程
   - 交付物：《需求规格说明书》《现状调研报告》
   - 负责人：项目经理、业务分析师

2. **系统设计与开发**（预计8周）
   - 具体内容：架构设计、模块开发、接口实现
   - 交付物：《系统设计文档》《源代码》《接口文档》
   - 负责人：系统架构师、开发工程师

3. **数据接入与调试**（预计3周）
   - 具体内容：接入水文监测数据、调试数据链路、验证数据质量
   - 交付物：《数据接入报告》《数据质量评估报告》
   - 负责人：数据工程师

4. **模型训练与验证**（预计4周）
   - 具体内容：洪水预报模型训练、参数率定、精度验证
   - 交付物：《模型训练报告》《精度验证报告》
   - 负责人：算法工程师

5. **系统集成与测试**（预计3周）
   - 具体内容：模块集成、功能测试、性能测试、安全测试
   - 交付物：《测试报告》《问题修复记录》
   - 负责人：测试工程师

6. **试运行与验收**（预计4周）
   - 具体内容：系统试运行、用户培训、项目验收
   - 交付物：《试运行报告》《验收报告》《用户手册》
   - 负责人：项目经理

## 验收标准

[明确、可验证的验收条件，引用行业标准]
### 功能验收
- [ ] 数据获取完整性：关键水文要素完整性≥99%，一般要素≥95%（SL 460）
- [ ] 洪水预报精度：洪峰流量误差<20%，峰现时间误差<6h（SL 250）
- [ ] 决策可解释性：每个决策建议引用≥2条依据

### 性能验收
- [ ] 系统响应时间：平均响应时间<2s，95分位<5s
- [ ] 模型计算效率：24h预见期洪水预报<30s

### 安全验收
- [ ] 调度指令安全校验：100%拦截超出安全约束的指令
- [ ] 数据安全传输：符合等保2.0三级要求

### 合规验收
- [ ] 调度规程符合性：所有规则符合经审批的调度规程（SL 319）
- [ ] 数据接口标准：符合SL 651《水文监测数据通信规约》

## 风险与应对

[可能的风险和应对策略，考虑水利行业特点]
| 风险类别 | 风险描述 | 可能性 | 影响 | 应对措施 |
|---------|---------|--------|------|----------|
| 水文风险 | 极端洪水超预期 | 中 | 高 | 预留安全裕度，制定应急预案 |
| 技术风险 | 预报模型精度不达标 | 中 | 高 | 多模型集合，实时校正 |
| 数据风险 | 监测数据缺失/异常 | 高 | 中 | 数据质量控制，备用数据源 |
| 工程风险 | 泄洪设施故障 | 低 | 高 | 定期检修，备用设施 |
| 合规风险 | 不符合最新规程 | 中 | 中 | 跟踪法规更新，专家评审 |

## 专家经验引用

[引用相关专家经验和历史案例]
- 经验1：2020年长江洪水调度表明，多库联合调度可降低下游水位0.4m
- 经验2：预泄腾库需提前24-48小时启动，预留足够腾库时间
- 经验3：水位日变幅控制在1-2m以内，确保大坝安全

## 备注

[其他需要说明的事项]
- 本项目需与防汛指挥部门协调，确保调度权限清晰
- 系统上线后需经过至少一个汛期考验
- 建议每年汛前进行系统维护和模型更新
```

【质量要求】
1. 目标必须遵循 SMART 原则，量化指标引用行业标准
2. 数据处理链条必须显式定义，各环节输入输出清晰
3. 验收标准必须引用具体行业标准（SL系列规范）
4. 风险分析必须考虑水文、工程、数据等水利特有风险
5. 专家经验必须引用历史案例和调度经验
6. 所有决策规则必须注明参考依据（法规条款/专家经验）"""

    @staticmethod
    def get_plan_single_generation_prompt(context: PromptContext) -> str:
        """获取单一规划方案生成提示词（可编辑版本）

        生成单一、结构清晰的规划文档，支持后续编辑。

        Args:
            context: 提示词上下文

        Returns:
            单一规划方案生成提示词
        """
        constraints_str = ""
        if context.constraints:
            constraints_json = json.dumps(context.constraints, ensure_ascii=False, indent=2)
            constraints_str = f"""
【约束条件】
{constraints_json}"""

        references_str = ""
        if context.references:
            refs = "\n".join([f"- {ref}" for ref in context.references])
            references_str = f"""
【参考资料】
{refs}"""

        return f"""【任务】
请根据以下需求生成一份单一、结构清晰的项目规划文档。

【用户输入】
{context.user_input}

【领域背景】
{context.domain}{constraints_str}{references_str}

【重要说明】
1. **只生成单一规划方案**（非多备选），确保方案完整、可执行
2. **强调可编辑性**：文档结构清晰，各章节独立，便于后续修改
3. **章节结构固定**：严格遵循以下章节顺序，便于程序解析和用户编辑

【章节结构说明】
- **概述**：项目背景、目的和范围（200字以内，简洁明了）
- **目标**：SMART原则的具体目标（3-5条，每条可独立编辑）
- **实施步骤**：按时间顺序排列的执行步骤（每个步骤独立成块，便于增删改）
- **验收标准**：可验证的验收条件（检查清单形式，每条可勾选）
- **风险与应对**：风险表格（结构化数据，便于修改）
- **备注**：其他补充说明（可选，可自由编辑）

【输出格式】
请严格按以下 Markdown 格式生成规划文档：

```markdown
# [规划标题]

## 概述

[项目背景、目的和范围的简要描述，200字以内]

## 目标

[具体、可衡量、有时限的目标，使用列表形式]
- 目标1：具体描述（量化指标）
- 目标2：具体描述（量化指标）

## 实施步骤

[详细的执行步骤，按时间顺序排列]
1. **步骤一名称**（预计耗时）
   - 具体内容：[详细描述该步骤需要完成的工作]
   - 交付物：[该步骤的产出成果]
   - 负责人：[负责执行的角色或人员]

2. **步骤二名称**（预计耗时）
   - 具体内容：[详细描述]
   - 交付物：[产出成果]
   - 负责人：[负责角色]

## 验收标准

[明确、可验证的验收条件]
- [ ] 标准1：具体描述和验证方法
- [ ] 标准2：具体描述和验证方法

## 风险与应对

[可能的风险和应对策略]
| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|----------|
| 风险1 | 高/中/低 | 高/中/低 | 应对策略描述 |

## 备注

[其他需要说明的事项，可选]
```

【质量要求】
1. **单一方案**：只输出一个最优规划方案，不要提供多个备选
2. **可编辑性**：每个章节内容应相对独立，修改一个章节不影响其他章节
3. **结构清晰**：使用标准Markdown格式，标题层级明确
4. **内容完整**：覆盖项目规划的完整要素，不遗漏关键信息
5. **专业规范**：使用水利行业专业术语，符合行业标准
6. **可衡量性**：目标、步骤、验收标准都必须具体、可量化、可验证

【编辑提示】
- 用户可能会对生成的规划进行编辑，请确保内容格式规范
- 各章节使用明确的标题标记，便于定位和修改
- 列表项使用统一的格式，便于增删"""

    @staticmethod
    def get_plan_section_optimization_prompt(
        section_name: str,
        current_content: str,
        context: str = ""
    ) -> str:
        """获取规划章节优化提示词

        Args:
            section_name: 章节名称
            current_content: 当前内容
            context: 额外上下文

        Returns:
            章节优化提示词
        """
        return f"""【任务】
请优化以下规划文档的"{section_name}"章节。

【当前内容】
{current_content}

【上下文信息】
{context}

【优化要求】
1. 保持原有章节结构
2. 提升内容的专业性和准确性
3. 增加可操作性和可衡量性
4. 确保逻辑清晰、表达简洁
5. 补充缺失的关键信息

【输出格式】
直接输出优化后的章节内容，保持 Markdown 格式。
不要添加解释说明，只输出优化后的内容。"""

    # ========== Spec 模式提示词 ==========

    @staticmethod
    def get_spec_generation_prompt(context: PromptContext) -> str:
        """获取规格生成提示词

        Args:
            context: 提示词上下文

        Returns:
            规格生成提示词
        """
        existing_str = ""
        if context.existing_content:
            existing_str = f"""
【现有规划内容】
{context.existing_content}

请基于以上规划内容，生成详细的技术规格。"""

        return f"""【任务】
请根据以下需求生成一份完整的技术规格文档套装（spec.md、tasks.md、checklist.md）。

【用户输入】
{context.user_input}

【领域背景】
{context.domain}{existing_str}

【输出格式要求】
**非常重要**：请严格按照以下格式输出三个文档，使用 === 作为文档分隔符：

=== spec.md ===
# [功能名称] - 规格文档

## 概述

[功能背景、目的和范围的简要描述]

## 功能需求

### 功能需求1
- **需求描述**：详细描述
- **输入**：输入数据/参数
- **输出**：输出结果
- **约束**：限制条件
- **优先级**：P0/P1/P2

### 功能需求2
...

## 技术方案

### 架构设计
[系统架构图和说明]

### 核心算法
[关键算法和逻辑]

### 数据模型
[数据结构和关系]

## 接口定义

### API 接口
| 方法 | 路径 | 描述 | 请求参数 | 响应数据 |
|------|------|------|----------|----------|
| POST | /api/xxx | 描述 | {{"key": "value"}} | {{"result": "data"}} |

### 数据接口
[数据输入输出格式]

## 性能指标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 响应时间 | < 200ms | API平均响应时间 |
| 吞吐量 | > 1000 QPS | 系统处理能力 |
| 准确率 | > 95% | 预测准确率 |

## 验收标准

- [ ] 标准1：具体描述
- [ ] 标准2：具体描述

=== tasks.md ===
# [功能名称] - 任务列表

## 任务分解

- [ ] **任务1**：任务描述
  - 预估工时：X天
  - 负责人：XXX
  - 依赖：无/任务X
  - 验收：验收标准

- [ ] **任务2**：任务描述
  ...

## 依赖关系

任务1 -> 任务2 -> 任务3
任务1 -> 任务4

## 时间估算

| 阶段 | 任务数 | 预估工时 | 起止时间 |
|------|--------|----------|----------|
| 阶段1 | X个 | X天 | 第1-3天 |
| 阶段2 | X个 | X天 | 第4-7天 |

=== checklist.md ===
# [功能名称] - 检查清单

## 前置条件

- [ ] 需求已确认并评审通过
- [ ] 技术方案已评审通过
- [ ] 资源已分配（人力、环境）

## 开发检查项

- [ ] 代码实现完成
- [ ] 单元测试覆盖率 > 80%
- [ ] 代码审查通过
- [ ] 接口文档已更新

## 测试检查项

- [ ] 功能测试用例编写完成
- [ ] 功能测试执行通过
- [ ] 集成测试执行通过
- [ ] 性能测试达标

## 部署检查项

- [ ] 部署文档已编写
- [ ] 配置参数已确认
- [ ] 回滚方案已准备
- [ ] 监控告警已配置

## 文档检查项

- [ ] API文档已更新
- [ ] 用户手册已编写
- [ ] 运维文档已编写
- [ ] 培训材料已准备

【质量要求】
1. 需求必须完整、无歧义，使用用户故事格式
2. 技术方案必须可行，包含架构图和关键算法
3. 接口定义必须规范，包含请求/响应示例
4. 性能指标必须具体、可测试
5. 任务分解必须细化到可执行粒度
6. 检查清单必须覆盖全流程"""

    @staticmethod
    def get_water_spec_generation_prompt(context: PromptContext) -> str:
        """获取水利项目专用规格生成提示词

        基于规划文档生成符合水利行业规范的技术规格文档，
        包含系统架构、数据模型、接口规范、算法方案等专业内容。

        Args:
            context: 提示词上下文，包含规划文档和水利业务类型

        Returns:
            水利项目规格生成提示词
        """
        # 获取水利领域知识
        domain_knowledge = ""
        if context.use_water_domain_knowledge:
            # 获取数据处理链条
            if context.water_business_type:
                domain_knowledge += WaterDomainPrompts.get_data_chain_prompt(context.water_business_type)
                domain_knowledge += "\n\n"

            # 获取法规规程
            domain_knowledge += WaterDomainPrompts.get_regulations_prompt()
            domain_knowledge += "\n\n"

            # 获取阈值参数
            domain_knowledge += WaterDomainPrompts.get_thresholds_prompt()
            domain_knowledge += "\n\n"

            # 获取验收标准
            domain_knowledge += WaterDomainPrompts.get_acceptance_criteria_prompt()

        existing_str = ""
        if context.existing_content:
            existing_str = f"""
【规划文档内容】
{context.existing_content}

请基于以上规划文档，生成详细的技术规格文档。"""

        constraints_str = ""
        if context.constraints:
            import json
            constraints_json = json.dumps(context.constraints, ensure_ascii=False, indent=2)
            constraints_str = f"""
【约束条件】
{constraints_json}"""

        return f"""【任务】
请根据以下规划文档生成一份专业的水利信息系统技术规格文档。

【用户输入】
{context.user_input}

【领域背景】
{context.domain}{existing_str}{constraints_str}

【水利领域专业知识】
{domain_knowledge}

【输出要求】
请按以下 Markdown 格式生成技术规格文档：

```markdown
# [系统名称] - 技术规格文档

## 概述

[系统背景、目的和范围的简要描述]
- 系统类型：洪水预警/水库调度/流域分析等
- 涉及流域/水库：[具体名称]
- 主要功能模块：[简要说明]

## 系统架构

### 总体架构
[描述系统的整体架构，可以使用文字描述架构图]
- 数据采集层
- 数据处理层
- 业务逻辑层
- 应用展示层

### 技术栈
- 后端：[技术选型及版本]
- 前端：[技术选型及版本]
- 数据库：[数据库类型及版本]
- 消息队列：[如有]
- 缓存：[如有]

## 数据模型

### 数据实体
[描述核心数据实体及其关系]

#### 实体1：水文监测数据
- 字段定义：
  - station_id: 站点ID (string, 主键)
  - timestamp: 时间戳 (datetime)
  - water_level: 水位 (float, 单位：m)
  - flow_rate: 流量 (float, 单位：m³/s)
  - rainfall: 降雨量 (float, 单位：mm)
- 索引：station_id + timestamp
- 存储：时序数据库/关系数据库

#### 实体2：预警记录
- 字段定义：
  - warning_id: 预警ID (string, 主键)
  - level: 预警等级 (enum: 蓝/黄/橙/红)
  - trigger_time: 触发时间 (datetime)
  - content: 预警内容 (text)
- 关联：关联到监测数据

### 数据流
[描述数据在系统中的流动过程]
1. 数据采集 -> 2. 数据清洗 -> 3. 数据存储 -> 4. 数据分析 -> 5. 结果展示

## 接口设计

### 数据接入接口
[描述外部数据接入的接口规范]

#### 接口1：水文数据接收
- 接口路径：/api/v1/hydrology/data
- 请求方法：POST
- 请求格式：JSON
- 请求示例：
```json
{{
  "station_id": "ST001",
  "timestamp": "2024-01-01T12:00:00Z",
  "water_level": 45.2,
  "flow_rate": 1200.5,
  "rainfall": 15.5
}}
```
- 响应格式：JSON
- 响应示例：
```json
{{
  "code": 200,
  "message": "success",
  "data": {{
    "record_id": "REC001"
  }}
}}
```
- 数据标准：符合SL 651《水文监测数据通信规约》

### 业务接口
[描述系统提供的业务接口]

#### 接口2：洪水预报查询
- 接口路径：/api/v1/forecast/flood
- 请求方法：GET
- 请求参数：
  - station_id: 站点ID (required)
  - forecast_hours: 预报时长 (optional, default: 24)
- 响应示例：
```json
{{
  "code": 200,
  "data": {{
    "station_id": "ST001",
    "forecast_time": "2024-01-01T12:00:00Z",
    "predictions": [
      {{
        "time": "2024-01-01T13:00:00Z",
        "water_level": 45.5,
        "flow_rate": 1250.0,
        "confidence": 0.85
      }}
    ]
  }}
}}
```

## 算法方案

### 洪水预报模型
[描述洪水预报的核心算法]

#### 模型1：水文模型
- 模型类型：概念性水文模型/机器学习模型
- 输入参数：
  - 历史降雨数据
  - 当前水位流量
  - 流域特征参数
- 输出结果：
  - 未来水位过程
  - 洪峰流量预测
  - 峰现时间预测
- 精度要求：洪峰误差<20%，峰现时间误差<6h（SL 250）
- 更新频率：每6小时滚动预报

#### 模型2：预警等级判定
- 判定逻辑：
  - 蓝色：水位 ≥ 警戒水位×0.9
  - 黄色：水位 ≥ 警戒水位
  - 橙色：水位 ≥ 警戒水位×1.1
  - 红色：水位 ≥ 警戒水位×1.2
- 触发条件：实时监测数据+预报数据综合判断

## 性能指标

### 功能性能
- 数据接入延迟：< 5分钟（从采集到入库）
- 预报计算时间：< 30秒（24小时预见期）
- 预警发布时间：< 5分钟（从触发到发布）
- 查询响应时间：< 2秒（95分位）

### 可靠性指标
- 系统可用性：≥ 99.5%
- 数据完整性：≥ 99%（关键要素）
- 预报准确率：≥ 85%（合格率）

## 安全设计

### 数据安全
- 传输加密：HTTPS/TLS 1.2+
- 存储加密：敏感数据加密存储
- 访问控制：基于角色的权限管理（RBAC）
- 审计日志：关键操作记录

### 系统安全
- 等保等级：符合等保2.0三级要求
- 安全认证：用户身份认证+操作授权
- 数据备份：定期备份+异地容灾

## 部署架构

### 部署环境
- 服务器配置：CPU/内存/存储规格
- 网络架构：内外网隔离、DMZ区部署
- 高可用设计：主备部署、负载均衡

### 运维监控
- 监控指标：系统性能、业务指标、数据质量
- 告警机制：阈值告警、异常检测
- 日志管理：集中日志收集与分析

## 附录

### A. 术语表
[定义文档中使用的专业术语]
- 面雨量：流域内单位面积上的平均降雨量
- 洪峰流量：洪水过程中出现的最大流量
- 汛限水位：汛期允许的最高蓄水位

### B. 参考标准
[列出参考的行业标准]
- SL 250-2000 《洪水预报规范》
- SL 319-2005 《水库调度规程编制导则》
- SL 651-2014 《水文监测数据通信规约》
- SL 460-2009 《水文监测数据完整性评价规范》

### C. 数据字典
[详细的数据字段定义]
[略，可根据实际需要补充]
```

【质量要求】
1. 架构设计必须考虑水利行业特点（实时性、可靠性、安全性）
2. 数据模型必须符合SL 651等水文数据标准
3. 接口设计必须包含完整的请求/响应示例
4. 算法方案必须说明输入输出和精度要求
5. 性能指标必须具体、可测试、引用行业标准
6. 安全设计必须符合等保2.0三级要求
7. Spec文档中不包含验收标准和任务分解（这些内容在checklist.md和tasks.md中）"""

    @staticmethod
    def get_water_tasks_generation_prompt(context: PromptContext) -> str:
        """获取水利项目任务分解生成提示词

        基于规格文档生成详细的任务分解列表。

        Args:
            context: 提示词上下文

        Returns:
            任务分解生成提示词
        """
        existing_str = ""
        if context.existing_content:
            existing_str = f"""
【规格文档内容】
{context.existing_content}

请基于以上规格文档，生成详细的任务分解列表。"""

        return f"""【任务】
请根据以下规格文档生成水利信息系统开发任务分解列表（tasks.md）。

【用户输入】
{context.user_input}

【领域背景】
{context.domain}{existing_str}

【输出要求】
请按以下 Markdown 格式生成任务分解文档：

```markdown
# [系统名称] - 开发任务分解

## 任务列表

### 阶段1：需求分析与设计
- [ ] **TASK-001** 需求调研与分析
  - 描述：调研现有系统、收集用户需求、分析业务流程
  - 类型：分析
  - 预估工时：5天
  - 优先级：P0
  - 依赖：无
  - 交付物：《需求规格说明书》

- [ ] **TASK-002** 系统架构设计
  - 描述：设计系统整体架构、技术选型、模块划分
  - 类型：设计
  - 预估工时：5天
  - 优先级：P0
  - 依赖：TASK-001
  - 交付物：《系统架构设计文档》

- [ ] **TASK-003** 数据模型设计
  - 描述：设计数据实体、数据库表结构、数据流
  - 类型：设计
  - 预估工时：3天
  - 优先级：P0
  - 依赖：TASK-002
  - 交付物：《数据模型设计文档》

### 阶段2：核心功能开发
- [ ] **TASK-004** 数据采集模块开发
  - 描述：开发水文监测数据接入功能，实现与雨量站、水位站的数据对接
  - 类型：开发
  - 预估工时：8天
  - 优先级：P0
  - 依赖：TASK-003
  - 交付物：数据采集模块代码

- [ ] **TASK-005** 数据存储模块开发
  - 描述：开发数据存储功能，实现时序数据和关系数据的存储
  - 类型：开发
  - 预估工时：5天
  - 优先级：P0
  - 依赖：TASK-004
  - 交付物：数据存储模块代码

- [ ] **TASK-006** 洪水预报模型开发
  - 描述：开发洪水预报算法，实现24小时预见期的洪水预报
  - 类型：开发
  - 预估工时：10天
  - 优先级：P0
  - 依赖：TASK-005
  - 交付物：洪水预报模型代码

- [ ] **TASK-007** 预警分析引擎开发
  - 描述：开发预警等级判定逻辑，实现蓝黄橙红四级预警
  - 类型：开发
  - 预估工时：5天
  - 优先级：P0
  - 依赖：TASK-006
  - 交付物：预警分析引擎代码

- [ ] **TASK-008** 预警发布模块开发
  - 描述：开发预警信息发布功能，支持短信、APP、广播多渠道
  - 类型：开发
  - 预估工时：5天
  - 优先级：P0
  - 依赖：TASK-007
  - 交付物：预警发布模块代码

### 阶段3：接口与前端开发
- [ ] **TASK-009** REST API接口开发
  - 描述：开发系统对外提供的REST API接口
  - 类型：开发
  - 预估工时：5天
  - 优先级：P1
  - 依赖：TASK-004
  - 交付物：API接口代码

- [ ] **TASK-010** 前端界面开发
  - 描述：开发用户交互界面，包括数据展示、预警管理等
  - 类型：开发
  - 预估工时：8天
  - 优先级：P1
  - 依赖：TASK-009
  - 交付物：前端应用代码

### 阶段4：测试与部署
- [ ] **TASK-011** 单元测试
  - 描述：编写单元测试用例，确保各模块功能正确
  - 类型：测试
  - 预估工时：5天
  - 优先级：P0
  - 依赖：TASK-008, TASK-010
  - 交付物：单元测试报告

- [ ] **TASK-012** 集成测试
  - 描述：进行系统集成测试，验证各模块协同工作
  - 类型：测试
  - 预估工时：5天
  - 优先级：P0
  - 依赖：TASK-011
  - 交付物：集成测试报告

- [ ] **TASK-013** 性能测试
  - 描述：进行性能测试，验证系统性能指标达标
  - 类型：测试
  - 预估工时：3天
  - 优先级：P1
  - 依赖：TASK-012
  - 交付物：性能测试报告

- [ ] **TASK-014** 系统部署
  - 描述：部署系统到生产环境，配置运维监控
  - 类型：部署
  - 预估工时：3天
  - 优先级：P0
  - 依赖：TASK-013
  - 交付物：部署完成报告

- [ ] **TASK-015** 用户培训
  - 描述：编写用户手册，进行用户培训
  - 类型：文档
  - 预估工时：3天
  - 优先级：P1
  - 依赖：TASK-014
  - 交付物：用户手册、培训材料

## 依赖关系图

```
TASK-001 -> TASK-002 -> TASK-003 -> TASK-004 -> TASK-005 -> TASK-006 -> TASK-007 -> TASK-008
                                    |
                                    v
                              TASK-009 -> TASK-010
                                    |
                                    v
                              TASK-011 -> TASK-012 -> TASK-013 -> TASK-014 -> TASK-015
```

## 里程碑

| 里程碑 | 包含任务 | 预计完成 | 交付物 |
|--------|----------|----------|--------|
| M1-需求设计 | TASK-001,TASK-002,TASK-003 | 第13天 | 需求规格、架构设计、数据模型 |
| M2-核心开发 | TASK-004,TASK-005,TASK-006,TASK-007,TASK-008 | 第41天 | 核心功能模块 |
| M3-接口前端 | TASK-009,TASK-010 | 第54天 | API接口、前端界面 |
| M4-测试部署 | TASK-011,TASK-012,TASK-013,TASK-014,TASK-015 | 第73天 | 测试报告、部署完成 |

## 资源分配

| 角色 | 人数 | 负责阶段 | 主要任务 |
|------|------|----------|----------|
| 项目经理 | 1 | 全程 | TASK-001, TASK-015 |
| 系统架构师 | 1 | 设计阶段 | TASK-002, TASK-003 |
| 后端开发 | 2 | 开发阶段 | TASK-004,TASK-005,TASK-006,TASK-007,TASK-008,TASK-009 |
| 前端开发 | 1 | 开发阶段 | TASK-010 |
| 测试工程师 | 1 | 测试阶段 | TASK-011,TASK-012,TASK-013 |
| 运维工程师 | 1 | 部署阶段 | TASK-014 |
```

【质量要求】
1. 任务粒度控制在1-3天工作量
2. 每个任务都有明确的交付物
3. 依赖关系清晰，避免循环依赖
4. 里程碑设置合理，便于进度跟踪
5. 资源分配合理，考虑并行开发"""

    @staticmethod
    def get_water_checklist_generation_prompt(context: PromptContext) -> str:
        """获取水利项目检查清单生成提示词

        基于规格文档生成详细的验收检查清单。

        Args:
            context: 提示词上下文

        Returns:
            检查清单生成提示词
        """
        existing_str = ""
        if context.existing_content:
            existing_str = f"""
【规格文档内容】
{context.existing_content}

请基于以上规格文档，生成详细的验收检查清单。"""

        return f"""【任务】
请根据以下规格文档生成水利信息系统验收检查清单（checklist.md）。

【用户输入】
{context.user_input}

【领域背景】
{context.domain}{existing_str}

【输出要求】
请按以下 Markdown 格式生成检查清单文档：

```markdown
# [系统名称] - 验收检查清单

## 功能验收检查项

### 数据采集功能
- [ ] **FUNC-001** 雨量站数据接入
  - 检查项：能够实时接收雨量站监测数据
  - 验收标准：数据延迟<5分钟，数据完整性>95%
  - 检查方法：对比数据源和系统接收数据
  - 参考标准：SL 651《水文监测数据通信规约》

- [ ] **FUNC-002** 水位站数据接入
  - 检查项：能够实时接收水位站监测数据
  - 验收标准：数据延迟<5分钟，数据完整性>99%
  - 检查方法：对比数据源和系统接收数据
  - 参考标准：SL 651

- [ ] **FUNC-003** 数据质量检查
  - 检查项：系统能够识别并处理异常数据
  - 验收标准：异常数据识别率>90%，误报率<5%
  - 检查方法：注入异常数据测试

### 洪水预报功能
- [ ] **FUNC-004** 洪水预报精度
  - 检查项：洪水预报结果符合精度要求
  - 验收标准：洪峰流量误差<20%，峰现时间误差<6h
  - 检查方法：使用历史洪水数据回代检验
  - 参考标准：SL 250《洪水预报规范》

- [ ] **FUNC-005** 预报时效性
  - 检查项：预报计算在合理时间内完成
  - 验收标准：24小时预见期预报计算时间<30秒
  - 检查方法：性能测试

### 预警发布功能
- [ ] **FUNC-006** 预警等级判定
  - 检查项：系统能够正确判定预警等级（蓝黄橙红）
  - 验收标准：判定准确率>95%
  - 检查方法：使用历史预警案例测试

- [ ] **FUNC-007** 预警发布时效
  - 检查项：预警从触发到发布的时间
  - 验收标准：预警发布时间<5分钟
  - 检查方法：模拟预警触发，测量发布时间

- [ ] **FUNC-008** 多渠道发布
  - 检查项：支持短信、APP、广播多渠道发布
  - 验收标准：各渠道发布成功率>99%
  - 检查方法：测试各渠道发布功能

## 性能验收检查项

- [ ] **PERF-001** 系统并发能力
  - 检查项：系统能够支持多用户并发访问
  - 验收标准：并发用户数≥100，响应时间<2s
  - 检查方法：压力测试

- [ ] **PERF-002** 数据处理能力
  - 检查项：系统能够处理高频率数据接入
  - 验收标准：支持≥1000个测点同时接入
  - 检查方法：模拟高并发数据接入

- [ ] **PERF-003** 系统可用性
  - 检查项：系统稳定运行时间
  - 验收标准：系统可用性≥99.5%
  - 检查方法：长期运行监测

## 安全验收检查项

- [ ] **SEC-001** 数据传输安全
  - 检查项：敏感数据在传输过程中加密
  - 验收标准：使用HTTPS/TLS 1.2+加密传输
  - 检查方法：网络抓包分析

- [ ] **SEC-002** 访问控制
  - 检查项：系统实现基于角色的权限管理
  - 验收标准：不同角色只能访问授权资源
  - 检查方法：权限测试

- [ ] **SEC-003** 等保合规
  - 检查项：系统符合等保2.0三级要求
  - 验收标准：通过等保测评
  - 检查方法：等保测评报告

## 接口验收检查项

- [ ] **API-001** 接口规范性
  - 检查项：REST API接口符合设计规范
  - 验收标准：接口路径、请求方法、参数、响应符合spec.md定义
  - 检查方法：接口测试

- [ ] **API-002** 接口性能
  - 检查项：API接口响应时间符合要求
  - 验收标准：95%请求响应时间<2s
  - 检查方法：API性能测试

## 数据验收检查项

- [ ] **DATA-001** 数据完整性
  - 检查项：关键水文数据完整性符合要求
  - 验收标准：关键要素完整性≥99%，一般要素≥95%
  - 检查方法：数据质量统计
  - 参考标准：SL 460《水文监测数据完整性评价规范》

- [ ] **DATA-002** 数据准确性
  - 检查项：数据准确性符合要求
  - 验收标准：数据误差在允许范围内
  - 检查方法：数据抽样校验

## 文档验收检查项

- [ ] **DOC-001** 技术文档完整性
  - 检查项：技术文档齐全
  - 验收标准：包含架构设计、接口文档、部署文档
  - 检查方法：文档审核

- [ ] **DOC-002** 用户文档完整性
  - 检查项：用户手册齐全
  - 验收标准：包含用户操作手册、培训材料
  - 检查方法：文档审核

## 验收流程

1. **自测阶段**：开发团队完成自测，确保所有检查项通过
2. **内测阶段**：测试团队进行系统测试，记录问题
3. **整改阶段**：开发团队修复测试发现的问题
4. **验收阶段**：用户/专家组进行最终验收
5. **签字确认**：验收通过后，各方签字确认

## 验收标准汇总

| 类别 | 检查项数量 | 关键项数量 | 通过标准 |
|------|-----------|-----------|---------|
| 功能验收 | 8 | 6 | 100%通过 |
| 性能验收 | 3 | 3 | 100%通过 |
| 安全验收 | 3 | 3 | 100%通过 |
| 接口验收 | 2 | 2 | 100%通过 |
| 数据验收 | 2 | 2 | 100%通过 |
| 文档验收 | 2 | 1 | 100%通过 |
| **总计** | **20** | **17** | **关键项100%通过** |

## 附录

### 参考标准
- SL 250-2000 《洪水预报规范》
- SL 319-2005 《水库调度规程编制导则》
- SL 651-2014 《水文监测数据通信规约》
- SL 460-2009 《水文监测数据完整性评价规范》
- GB/T 22239-2019 《信息安全技术 网络安全等级保护基本要求》
```

【质量要求】
1. 检查项覆盖功能、性能、安全、接口、数据、文档六个维度
2. 每个检查项都有明确的验收标准和检查方法
3. 引用具体的行业标准（SL系列、等保标准）
4. 区分关键项和一般项，关键项必须100%通过
5. 包含完整的验收流程和通过标准"""

    @staticmethod
    def get_spec_section_optimization_prompt(
        file_name: str,
        section_name: str,
        current_content: str,
        feature_context: str = ""
    ) -> str:
        """获取规格章节优化提示词

        Args:
            file_name: 文件名（spec.md/tasks.md/checklist.md）
            section_name: 章节名称
            current_content: 当前内容
            feature_context: 功能上下文

        Returns:
            章节优化提示词
        """
        file_guidance = {
            "spec.md": "技术规格文档，注重需求的完整性和技术方案的可行性",
            "tasks.md": "任务列表文档，注重任务的可执行性和依赖关系的清晰性",
            "checklist.md": "检查清单文档，注重检查项的全面性和可验证性"
        }
        
        guidance = file_guidance.get(file_name, "")

        return f"""【任务】
请优化以下规格文档的章节。

【文件】{file_name}
【章节】{section_name}
【文档类型说明】{guidance}

【当前内容】
{current_content}

【功能上下文】
{feature_context}

【优化要求】
1. 保持原有章节结构
2. 提升内容的专业性和准确性
3. 补充缺失的技术细节
4. 确保内容可执行、可验证
5. 使用规范的技术术语

【输出格式】
直接输出优化后的章节内容，保持 Markdown 格式。
不要添加解释说明，只输出优化后的内容。"""

    # ========== 分析与建议提示词 ==========

    @staticmethod
    def get_completeness_analysis_prompt(
        doc_type: str,
        content: str
    ) -> str:
        """获取完整性分析提示词

        Args:
            doc_type: 文档类型（plan/spec/tasks/checklist）
            content: 文档内容

        Returns:
            完整性分析提示词
        """
        doc_requirements = {
            "plan": """
必要章节：概述、目标、实施步骤、验收标准
检查要点：
- 目标是否具体可衡量
- 步骤是否逻辑清晰、可执行
- 验收标准是否明确可验证
- 是否考虑了风险因素""",
            "spec": """
必要章节：概述、功能需求、技术方案、接口定义、验收标准
检查要点：
- 需求是否完整无歧义
- 技术方案是否可行
- 接口定义是否清晰规范
- 性能指标是否具体可测试""",
            "tasks": """
必要章节：任务分解、依赖关系、时间估算
检查要点：
- 任务是否细化到可执行
- 依赖关系是否清晰
- 时间估算是否合理
- 是否分配了责任人""",
            "checklist": """
必要章节：前置条件、开发检查项、测试检查项、部署检查项、文档检查项
检查要点：
- 检查项是否全面
- 是否覆盖全流程
- 检查项是否可验证
- 是否有明确的验收标准"""
        }

        requirements = doc_requirements.get(doc_type, doc_requirements["plan"])

        return f"""【任务】
请分析以下{doc_type}文档的完整性和质量。

【文档内容】
{content}

【检查要求】
{requirements}

【输出格式】
请以 JSON 格式返回分析结果：

```json
{{
  "completeness_score": 0.85,
  "status": "pass/warning/fail",
  "missing_sections": ["缺失的章节"],
  "missing_items": [
    {{
      "section": "章节名",
      "issue": "问题描述",
      "suggestion": "改进建议"
    }}
  ],
  "strengths": ["文档的优点"],
  "improvements": [
    {{
      "priority": "high/medium/low",
      "description": "改进项描述"
    }}
  ],
  "summary": "总体评价"
}}
```

【评分标准】
- 0.9-1.0：优秀，内容完整、专业
- 0.7-0.9：良好，基本完整，有少量改进空间
- 0.5-0.7：一般，有明显缺失，需要补充
- 0.0-0.5：较差，内容不完整，需要重写"""

    @staticmethod
    def get_task_suggestion_prompt(
        spec_content: str,
        existing_tasks: Optional[str] = None
    ) -> str:
        """获取任务建议提示词

        Args:
            spec_content: 规格文档内容
            existing_tasks: 现有任务列表（可选）

        Returns:
            任务建议提示词
        """
        existing_str = ""
        if existing_tasks:
            existing_str = f"""
【现有任务列表】
{existing_tasks}

请基于现有任务进行补充和优化。"""

        return f"""【任务】
请根据以下规格文档，生成详细的任务分解列表。

【规格文档】
{spec_content}{existing_str}

【输出要求】
请按以下格式生成任务列表：

```markdown
## 任务分解

- [ ] **TASK-001**：[任务名称]
  - 描述：[详细描述]
  - 类型：开发/测试/文档/配置
  - 预估工时：X天
  - 优先级：P0/P1/P2
  - 依赖：无/TASK-XXX
  - 验收标准：[可验证的标准]

- [ ] **TASK-002**：...

## 依赖关系图

```
TASK-001 -> TASK-002 -> TASK-004
TASK-001 -> TASK-003
```

## 里程碑

| 里程碑 | 包含任务 | 预计完成 | 交付物 |
|--------|----------|----------|--------|
| M1 | TASK-001,TASK-002 | 第3天 | [交付物] |
```

【分解原则】
1. 每个任务应该是原子操作，不可再分
2. 任务粒度控制在 1-3 天工作量
3. 明确任务间的依赖关系
4. 每个任务都有明确的验收标准
5. 考虑并行执行的可能性"""

    @staticmethod
    def get_plan_to_spec_transition_prompt(plan_content: str) -> str:
        """获取 Plan 转 Spec 的提示词

        Args:
            plan_content: 规划文档内容

        Returns:
            转换提示词
        """
        return f"""【任务】
请将以下规划文档转换为详细的技术规格文档。

【规划文档】
{plan_content}

【转换要求】
1. 将规划中的"目标"转换为具体的"功能需求"
2. 将"实施步骤"转换为详细的"技术方案"和"任务分解"
3. 将"验收标准"细化为可测试的验收条件
4. 补充技术细节：架构设计、接口定义、数据模型
5. 生成完整的规格文档套装（spec.md、tasks.md、checklist.md）

【输出格式】
请分别输出三个文档的内容，用分隔线区分：

=== spec.md ===
[spec.md 内容]

=== tasks.md ===
[tasks.md 内容]

=== checklist.md ===
[checklist.md 内容]

【注意事项】
- 保持规划的核心目标不变
- 补充技术实现细节
- 确保规格的可执行性
- 使用规范的技术术语"""


# 便捷函数
def get_prompt_for_mode(
    mode: str,
    action: str,
    context: Dict[str, Any]
) -> str:
    """根据模式和动作获取对应的提示词

    Args:
        mode: 模式（plan/spec）
        action: 动作（generate/optimize/analyze）
        context: 上下文数据

    Returns:
        对应的提示词
    """
    prompts = PlanSpecPrompts()
    prompt_context = PromptContext(
        user_input=context.get("user_input", ""),
        domain=context.get("domain", "水利调度"),
        existing_content=context.get("existing_content"),
        constraints=context.get("constraints"),
        references=context.get("references")
    )

    # 支持水利领域专用模式
    if mode == "water_plan":
        if action == "generate":
            prompt_context.water_business_type = context.get("water_business_type")
            prompt_context.use_water_domain_knowledge = context.get("use_water_domain_knowledge", True)
            return prompts.get_water_plan_generation_prompt(prompt_context)
        elif action == "optimize":
            return prompts.get_plan_section_optimization_prompt(
                context.get("section_name", ""),
                context.get("current_content", ""),
                context.get("extra_context", "")
            )
    elif mode == "plan":
        if action == "generate":
            return prompts.get_plan_generation_prompt(prompt_context)
        elif action == "optimize":
            return prompts.get_plan_section_optimization_prompt(
                context.get("section_name", ""),
                context.get("current_content", ""),
                context.get("extra_context", "")
            )
    elif mode == "spec":
        if action == "generate":
            return prompts.get_spec_generation_prompt(prompt_context)
        elif action == "optimize":
            return prompts.get_spec_section_optimization_prompt(
                context.get("file_name", ""),
                context.get("section_name", ""),
                context.get("current_content", ""),
                context.get("feature_context", "")
            )

    if action == "analyze":
        return prompts.get_completeness_analysis_prompt(
            context.get("doc_type", "plan"),
            context.get("content", "")
        )
    elif action == "suggest_tasks":
        return prompts.get_task_suggestion_prompt(
            context.get("spec_content", ""),
            context.get("existing_tasks")
        )
    elif action == "plan_to_spec":
        return prompts.get_plan_to_spec_transition_prompt(
            context.get("plan_content", "")
        )

    return ""


# 导入 json 用于约束条件的序列化
import json
