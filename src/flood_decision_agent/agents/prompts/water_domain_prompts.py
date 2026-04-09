"""水利领域专用提示词模块

提供水利智能体特有的领域知识、规则、阈值和验收标准，
支持 Plan/Spec 模式下的专业文档生成。
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


# ========== 数据-要素-指标-决策链条定义 ==========

class ChainStage(str, Enum):
    """链条阶段枚举"""
    DATA_ACQUISITION = "data_acquisition"      # 数据获取
    FEATURE_EXTRACTION = "feature_extraction"  # 要素提取
    INDEX_CALCULATION = "index_calculation"    # 指标计算
    DECISION_SUPPORT = "decision_support"      # 决策支持


@dataclass
class DataSource:
    """数据源定义"""
    name: str                                    # 数据源名称
    type: str                                    # 数据类型：realtime/historical/forecast
    provider: str                                # 数据提供方
    update_frequency: str                        # 更新频率
    quality_requirements: List[str] = field(default_factory=list)  # 质量要求
    access_method: str = ""                      # 访问方式


@dataclass
class FeatureDefinition:
    """要素定义"""
    name: str                                    # 要素名称
    category: str                                # 分类：hydrology/meteorology/engineering
    unit: str                                    # 单位
    calculation_method: str = ""                 # 计算方法
    validation_rules: List[str] = field(default_factory=list)  # 验证规则


@dataclass
class IndexDefinition:
    """指标定义"""
    name: str                                    # 指标名称
    formula: str                                 # 计算公式
    threshold_levels: Dict[str, float] = field(default_factory=dict)  # 阈值等级
    interpretation: str = ""                     # 指标解释


@dataclass
class DecisionRule:
    """决策规则"""
    condition: str                               # 触发条件
    action: str                                  # 执行动作
    priority: int = 1                            # 优先级
    reference: str = ""                          # 参考依据（法规/规程条款）


# ========== 专家规则定义 ==========

class RuleType(str, Enum):
    """规则类型"""
    SCHEDULING = "scheduling"          # 调度规则
    WARNING = "warning"                # 预警规则
    SAFETY = "safety"                  # 安全规则
    EMERGENCY = "emergency"            # 应急规则


@dataclass
class ExpertRule:
    """专家规则"""
    id: str                                      # 规则编号
    type: RuleType                               # 规则类型
    name: str                                    # 规则名称
    condition: str                               # 触发条件
    action: str                                  # 执行动作
    constraint: str                              # 约束条件
    rationale: str                               # 理论依据
    experience_source: str                       # 经验来源
    priority: int = 1                            # 优先级


@dataclass
class HistoricalCase:
    """历史案例"""
    id: str                                      # 案例编号
    name: str                                    # 案例名称
    date: str                                    # 发生时间
    scenario: Dict[str, Any]                     # 场景描述
    decision: str                                # 决策方案
    outcome: str                                 # 实施效果
    lessons: List[str]                           # 经验教训


@dataclass
class Regulation:
    """法规规程条目"""
    code: str                                    # 编号
    name: str                                    # 名称
    article: str                                 # 条款
    content: str                                 # 内容
    application: str                             # 适用场景


@dataclass
class AcceptanceCriterion:
    """验收标准项"""
    id: str                                      # 标准编号
    category: str                                # 类别：功能/性能/安全/合规
    description: str                             # 标准描述
    verification_method: str                     # 验证方法
    pass_criteria: str                           # 通过标准
    reference: str = ""                          # 参考依据
    priority: str = "P1"                         # 优先级 P0/P1/P2


class WaterDomainPrompts:
    """水利领域专用提示词类"""
    
    # ========== 系统角色定义 ==========
    
    WATER_EXPERT_SYSTEM = """你是"水利调度专家"——一个精通水文水资源、水库调度、防洪抗旱的专业AI助手。

【你的专业背景】
- 精通《水库调度规程》《洪水预报规范》等行业标准
- 熟悉长江流域、黄河流域、淮河流域等主要流域的洪水特性
- 掌握水文预报、洪水演进、水库优化调度等核心技术
- 了解大坝安全、闸门控制、应急管理等工程实践

【你的决策原则】
1. 安全第一：大坝安全和人员生命安全是最高优先级
2. 规程约束：所有决策必须符合经审批的调度规程
3. 科学决策：基于数据和模型，结合专家经验
4. 可解释性：每个决策必须说明依据和理由

【输出要求】
- 使用专业术语，符合水利行业规范
- 引用具体的法规条款和技术标准
- 提供量化的指标和阈值
- 说明决策的风险和不确定性"""

    # ========== 数据-要素-指标-决策链条模板 ==========
    
    DATA_CHAIN_TEMPLATES = {
        "flood_warning": {
            "name": "洪水预警分析链条",
            "description": "从数据采集到洪水预警发布的完整处理流程",
            "stages": {
                "data_acquisition": {
                    "description": "获取水文气象实时数据和预报数据",
                    "data_sources": [
                        {"name": "雨量站实时数据", "type": "realtime", "frequency": "5分钟", "quality": "完整性>95%"},
                        {"name": "水位站实时数据", "type": "realtime", "frequency": "5分钟", "quality": "完整性>99%"},
                        {"name": "气象预报数据", "type": "forecast", "frequency": "6小时", "quality": "空间分辨率<10km"},
                    ],
                    "outputs": ["rainfall_data", "water_level_data", "flow_data", "weather_forecast"]
                },
                "feature_extraction": {
                    "description": "提取关键水文气象要素",
                    "features": [
                        {"name": "面雨量", "unit": "mm", "method": "泰森多边形法/反距离加权法"},
                        {"name": "涨水速率", "unit": "m/h", "method": "水位差分/时间差分"},
                        {"name": "洪峰流量", "unit": "m³/s", "method": "水位流量关系曲线"},
                    ],
                    "outputs": ["rainfall_features", "hydrology_features"]
                },
                "index_calculation": {
                    "description": "计算预警指标和风险指标",
                    "indices": [
                        {"name": "洪水预警等级", "formula": "水位/警戒水位", "thresholds": {"蓝色": 0.9, "黄色": 1.0, "橙色": 1.1, "红色": 1.2}},
                        {"name": "降雨强度指数", "formula": "mm/h", "thresholds": {"小雨": 2.5, "中雨": 8.0, "大雨": 16.0, "暴雨": 32.0}},
                    ],
                    "outputs": ["warning_indices", "risk_indices"]
                },
                "decision_support": {
                    "description": "生成预警决策和响应方案",
                    "rules": [
                        {"condition": "预警等级 >= 黄色 AND 涨水速率 > 0.5m/h", "action": "发布洪水预警，启动应急响应", "reference": "《洪水预警发布管理办法》第12条"},
                        {"condition": "预报24h面雨量 > 50mm AND 当前库水位 > 汛限水位-1m", "action": "建议预泄腾库，做好防洪准备", "reference": "《水库调度规程》第15条"},
                    ],
                    "outputs": ["warning_decision", "response_plan"]
                }
            }
        },
        "reservoir_dispatch": {
            "name": "水库优化调度链条",
            "description": "水库防洪与兴利联合优化调度决策流程",
            "stages": {
                "data_acquisition": {
                    "description": "获取入库预报和水库实时工况",
                    "data_sources": [
                        {"name": "入库流量预报", "type": "forecast", "frequency": "6小时", "quality": "预报精度>85%"},
                        {"name": "水库实时工况", "type": "realtime", "frequency": "5分钟", "quality": "数据完整性>99%"},
                    ],
                    "outputs": ["inflow_forecast", "current_state", "constraints"]
                },
                "feature_extraction": {
                    "description": "提取调度关键要素",
                    "features": [
                        {"name": "洪峰流量", "unit": "m³/s", "method": "洪水过程线分析"},
                        {"name": "可用调洪库容", "unit": "万m³", "method": "汛限水位-当前水位对应库容"},
                        {"name": "防洪风险度", "unit": "无量纲", "method": "1 - 调洪能力/需求洪量"},
                    ],
                    "outputs": ["inflow_features", "reservoir_features"]
                },
                "index_calculation": {
                    "description": "计算调度效益指标",
                    "indices": [
                        {"name": "调洪效益指数", "formula": "削峰率 × 错峰时长 / 下游损失", "thresholds": {"优秀": 0.8, "良好": 0.6, "合格": 0.4}},
                        {"name": "兴利损失指数", "formula": "弃水量 / 多年平均供水量", "thresholds": {"可接受": 0.1, "需优化": 0.2, "不可接受": 0.3}},
                    ],
                    "outputs": ["dispatch_indices", "benefit_indices"]
                },
                "decision_support": {
                    "description": "生成调度方案和操作指令",
                    "rules": [
                        {"condition": "防洪风险度 > 0.7 AND 可用调洪库容 < 设计洪量的30%", "action": "启动大洪水调度预案，全开泄洪设施", "reference": "《水库大坝安全管理条例》第18条"},
                        {"condition": "下游安全泄量 < 洪峰流量 AND 可用调洪库容 > 设计洪量的50%", "action": "实施削峰调度，控制出库不超过安全泄量", "reference": "《水库调度规程》第22条"},
                    ],
                    "outputs": ["dispatch_plan", "operation_instructions"]
                }
            }
        }
    }

    # ========== 专家规则库 ==========
    
    EXPERT_RULES = {
        "scheduling": [
            {
                "id": "SCH-001",
                "name": "汛限水位控制",
                "condition": "库水位 >= 汛限水位",
                "action": "开启泄洪设施，控制水位不超汛限",
                "constraint": "出库流量 <= 下游安全泄量",
                "rationale": "确保防洪库容，应对可能洪水",
                "reference": "《水库调度规程》通用原则",
                "priority": 1
            },
            {
                "id": "SCH-002",
                "name": "预泄腾库",
                "condition": "预报24h降雨量 > 50mm AND 库水位 > 汛限水位-2m",
                "action": "提前预泄，降低库水位至汛限水位-3m",
                "constraint": "预泄流量递增，每小时变幅<20%",
                "rationale": "利用洪水预报，提前腾出库容",
                "reference": "2020年长江流域洪水调度经验",
                "priority": 2
            },
            {
                "id": "SCH-003",
                "name": "削峰调度",
                "condition": "预报洪峰流量 > 下游安全泄量 AND 可用调洪库容 > 30%设计洪量",
                "action": "拦蓄洪峰，控制出库=安全泄量",
                "constraint": "最高洪水位 <= 设计洪水位",
                "rationale": "牺牲部分兴利效益，确保下游防洪安全",
                "reference": "1998年洪水调度经典案例",
                "priority": 1
            },
        ],
        "warning": [
            {
                "id": "WARN-001",
                "name": "蓝色预警（Ⅳ级）",
                "condition": "水位 >= 警戒水位×0.9 OR 预报24h面雨量 >= 30mm",
                "action": "发布蓝色预警，加强监测",
                "constraint": "每6小时更新一次预报",
                "reference": "《洪水预警发布管理办法》",
                "priority": 4
            },
            {
                "id": "WARN-002",
                "name": "黄色预警（Ⅲ级）",
                "condition": "水位 >= 警戒水位 OR 预报24h面雨量 >= 50mm",
                "action": "发布黄色预警，启动Ⅳ级响应",
                "constraint": "每3小时更新一次预报",
                "reference": "《洪水预警发布管理办法》",
                "priority": 3
            },
            {
                "id": "WARN-003",
                "name": "橙色预警（Ⅱ级）",
                "condition": "水位 >= 警戒水位×1.1 OR 预报24h面雨量 >= 100mm",
                "action": "发布橙色预警，启动Ⅲ级响应，准备人员转移",
                "constraint": "每小时更新一次预报",
                "reference": "《洪水预警发布管理办法》",
                "priority": 2
            },
            {
                "id": "WARN-004",
                "name": "红色预警（Ⅰ级）",
                "condition": "水位 >= 警戒水位×1.2 OR 预报24h面雨量 >= 150mm",
                "action": "发布红色预警，启动Ⅱ级响应，立即转移人员",
                "constraint": "实时跟踪，30分钟更新",
                "reference": "《洪水预警发布管理办法》",
                "priority": 1
            },
        ],
        "safety": [
            {
                "id": "SAF-001",
                "name": "大坝安全第一",
                "condition": "任何情况下",
                "action": "确保大坝结构安全，禁止超标准运行",
                "constraint": "最高库水位 <= 设计洪水位",
                "rationale": "大坝安全是底线，不可突破",
                "reference": "《水库大坝安全管理条例》第18条",
                "priority": 0
            },
            {
                "id": "SAF-002",
                "name": "水位变幅控制",
                "condition": "库水位日变幅 > 设计允许值",
                "action": "减缓水位变化速率，控制日变幅",
                "constraint": "日水位变幅 <= 设计允许值（通常1-2m）",
                "rationale": "防止坝坡失稳，保护工程安全",
                "reference": "土石坝安全运行经验",
                "priority": 1
            },
        ]
    }

    # ========== 法规规程库 ==========
    
    REGULATIONS = [
        {
            "code": "SL 319-2005",
            "name": "《水库调度规程编制导则》",
            "article": "第4.1条",
            "content": "水库调度应以大坝安全为前提，充分发挥防洪、兴利等综合效益",
            "application": "所有调度决策的首要依据"
        },
        {
            "code": "SL 250-2000",
            "name": "《洪水预报规范》",
            "article": "第3.2条",
            "content": "洪水预报应包括洪峰流量、峰现时间、洪量等要素，预报精度应满足防汛要求",
            "application": "洪水预报功能验收"
        },
        {
            "code": "国务院令第77号",
            "name": "《水库大坝安全管理条例》",
            "article": "第18条",
            "content": "水库调度运用必须服从防汛指挥机构的统一指挥，不得擅自超标准运行",
            "application": "调度权限和安全约束"
        },
        {
            "code": "SL 651-2014",
            "name": "《水文监测数据通信规约》",
            "article": "全文",
            "content": "规定水文监测数据的采集、传输、存储格式和通信协议",
            "application": "数据接口标准化"
        },
    ]

    # ========== 阈值参数库 ==========
    
    THRESHOLDS = {
        "rainfall": {
            "小雨": {"value": 2.5, "unit": "mm", "description": "24h降雨量<2.5mm"},
            "中雨": {"value": 8.0, "unit": "mm", "description": "2.5mm≤24h降雨量<8mm"},
            "大雨": {"value": 16.0, "unit": "mm", "description": "8mm≤24h降雨量<16mm"},
            "暴雨": {"value": 32.0, "unit": "mm", "description": "16mm≤24h降雨量<32mm"},
            "大暴雨": {"value": 64.0, "unit": "mm", "description": "32mm≤24h降雨量<64mm"},
            "特大暴雨": {"value": 100.0, "unit": "mm", "description": "24h降雨量≥64mm"},
        },
        "flood_warning": {
            "蓝色": {"value": 0.9, "unit": "比值", "description": "水位≥警戒水位×0.9"},
            "黄色": {"value": 1.0, "unit": "比值", "description": "水位≥警戒水位"},
            "橙色": {"value": 1.1, "unit": "比值", "description": "水位≥警戒水位×1.1"},
            "红色": {"value": 1.2, "unit": "比值", "description": "水位≥警戒水位×1.2"},
        },
        "dispatch_control": {
            "预泄启动雨量": {"value": 50, "unit": "mm", "description": "24h预报降雨量"},
            "水位日变幅限制": {"value": 2.0, "unit": "m", "description": "土石坝日水位最大变幅"},
            "出库变幅限制": {"value": 20, "unit": "%", "description": "每小时出库流量最大变幅"},
            "调洪库容下限": {"value": 30, "unit": "%", "description": "可用调洪库容占设计洪量比例"},
        },
        "forecast_accuracy": {
            "洪峰流量误差": {"value": 20, "unit": "%", "description": "允许误差范围"},
            "峰现时间误差": {"value": 6, "unit": "h", "description": "允许误差范围"},
            "预报合格率": {"value": 85, "unit": "%", "description": "合格预报占比"},
        },
        "system_performance": {
            "常规方案生成时间": {"value": 30, "unit": "s", "description": "正常情况"},
            "应急方案生成时间": {"value": 10, "unit": "s", "description": "紧急情况"},
            "预警发布时间": {"value": 5, "unit": "min", "description": "从触发到发布"},
            "系统可用率": {"value": 99.5, "unit": "%", "description": "年度可用率"},
        }
    }

    # ========== 验收标准库 ==========
    
    ACCEPTANCE_CRITERIA = {
        "functional": [
            {
                "id": "FUNC-001",
                "category": "功能",
                "description": "数据获取完整性",
                "verification_method": "对比数据源与系统采集数据",
                "pass_criteria": "关键水文要素完整性≥99%，一般要素≥95%",
                "reference": "《水文监测数据完整性评价规范》SL 460",
                "priority": "P0"
            },
            {
                "id": "FUNC-002",
                "category": "功能",
                "description": "洪水预报精度",
                "verification_method": "使用历史洪水数据进行回代检验",
                "pass_criteria": "洪峰流量误差<20%，峰现时间误差<6h",
                "reference": "《洪水预报规范》SL 250",
                "priority": "P0"
            },
            {
                "id": "FUNC-003",
                "category": "功能",
                "description": "决策可解释性",
                "verification_method": "检查决策报告中的依据引用",
                "pass_criteria": "每个决策建议必须引用≥2条依据（法规/数据/模型）",
                "reference": "《水利智能决策系统技术导则》",
                "priority": "P1"
            },
        ],
        "performance": [
            {
                "id": "PERF-001",
                "category": "性能",
                "description": "系统响应时间",
                "verification_method": "压力测试，模拟100并发用户",
                "pass_criteria": "平均响应时间<2s，95分位<5s",
                "reference": "《信息系统性能测试规范》",
                "priority": "P1"
            },
            {
                "id": "PERF-002",
                "category": "性能",
                "description": "模型计算效率",
                "verification_method": "运行洪水演进模型",
                "pass_criteria": "24h预见期洪水预报<30s，方案优化<60s",
                "reference": "《洪水预报模型技术规范》",
                "priority": "P1"
            },
        ],
        "security": [
            {
                "id": "SEC-001",
                "category": "安全",
                "description": "调度指令安全校验",
                "verification_method": "模拟异常指令，测试拦截机制",
                "pass_criteria": "100%拦截超出安全约束的调度指令",
                "reference": "《水库大坝安全管理条例》",
                "priority": "P0"
            },
        ],
        "compliance": [
            {
                "id": "COMP-001",
                "category": "合规",
                "description": "调度规程符合性",
                "verification_method": "专家评审+规程对照检查",
                "pass_criteria": "所有调度规则符合经审批的调度规程",
                "reference": "《水库调度规程编制导则》SL 319",
                "priority": "P0"
            },
        ]
    }

    # ========== 历史案例库 ==========
    
    HISTORICAL_CASES = [
        {
            "id": "CASE-001",
            "name": "2020年长江洪水调度",
            "date": "2020-07",
            "scenario": {
                "流域": "长江流域",
                "洪水等级": "大洪水",
                "最大入库": "75000m³/s",
                "调度难点": "干支流洪水遭遇，多库联合调度"
            },
            "decision": "三峡水库实施削峰调度，联合上游水库群错峰",
            "outcome": "成功降低沙市水位约0.4m，避免荆江分洪",
            "lessons": [
                "多库联合调度效果显著",
                "预报精度是调度成功关键",
                "预泄腾库争取了调度主动权"
            ]
        },
        {
            "id": "CASE-002",
            "name": "2012年北京7·21暴雨",
            "date": "2012-07-21",
            "scenario": {
                "流域": "海河流域",
                "降雨特点": "局地特大暴雨，最大点雨量460mm",
                "灾害": "城市内涝严重，人员伤亡"
            },
            "decision": "山区水库提前预泄，城区泵站全力排水",
            "outcome": "水库发挥拦蓄作用，但城市排水能力不足",
            "lessons": [
                "城市防洪需要工程与非工程措施结合",
                "极端天气预报仍是难点",
                "应急响应速度至关重要"
            ]
        },
    ]

    @classmethod
    def get_data_chain_prompt(cls, chain_type: str) -> str:
        """获取数据链条提示词
        
        Args:
            chain_type: 链条类型，如 flood_warning, reservoir_dispatch
            
        Returns:
            数据链条描述文本
        """
        chain = cls.DATA_CHAIN_TEMPLATES.get(chain_type)
        if not chain:
            return ""
        
        prompt = f"""【数据处理链条：{chain['name']}】
{chain['description']}

"""
        for stage_name, stage_info in chain['stages'].items():
            prompt += f"""
=== {stage_name.upper()} ===
{stage_info['description']}

输入：{', '.join(stage_info.get('inputs', []))}
输出：{', '.join(stage_info.get('outputs', []))}
"""
            if 'data_sources' in stage_info:
                prompt += "\n数据源：\n"
                for ds in stage_info['data_sources']:
                    prompt += f"- {ds['name']}（{ds['type']}，{ds['frequency']}）\n"
            
            if 'features' in stage_info:
                prompt += "\n要素定义：\n"
                for f in stage_info['features']:
                    prompt += f"- {f['name']}：{f['unit']}，{f['method']}\n"
            
            if 'indices' in stage_info:
                prompt += "\n指标计算：\n"
                for idx in stage_info['indices']:
                    prompt += f"- {idx['name']}：{idx['formula']}\n"
            
            if 'rules' in stage_info:
                prompt += "\n决策规则：\n"
                for rule in stage_info['rules']:
                    prompt += f"- IF {rule['condition']} THEN {rule['action']}\n"
                    if 'reference' in rule:
                        prompt += f"  依据：{rule['reference']}\n"
        
        return prompt

    @classmethod
    def get_expert_rules_prompt(cls, rule_type: str = None) -> str:
        """获取专家规则提示词
        
        Args:
            rule_type: 规则类型，如 scheduling/warning/safety，None表示全部
            
        Returns:
            专家规则描述文本
        """
        prompt = "【水利专家经验规则】\n\n"
        
        types = [rule_type] if rule_type else cls.EXPERT_RULES.keys()
        
        for rt in types:
            if rt not in cls.EXPERT_RULES:
                continue
            prompt += f"=== {rt.upper()} RULES ===\n"
            for rule in cls.EXPERT_RULES[rt]:
                prompt += f"""
[{rule['id']}] {rule['name']}（优先级：{rule['priority']}）
条件：{rule['condition']}
动作：{rule['action']}
约束：{rule.get('constraint', '无')}
依据：{rule.get('rationale', '')}（{rule.get('reference', '')}）
"""
        return prompt

    @classmethod
    def get_regulations_prompt(cls) -> str:
        """获取法规规程提示词"""
        prompt = "【适用法规规程】\n\n"
        for reg in cls.REGULATIONS:
            prompt += f"""
[{reg['code']}] {reg['name']} {reg['article']}
内容：{reg['content']}
适用：{reg['application']}
"""
        return prompt

    @classmethod
    def get_thresholds_prompt(cls, category: str = None) -> str:
        """获取阈值参数提示词
        
        Args:
            category: 阈值类别，None表示全部
        """
        prompt = "【关键阈值参数】\n\n"
        
        categories = [category] if category else cls.THRESHOLDS.keys()
        
        for cat in categories:
            if cat not in cls.THRESHOLDS:
                continue
            prompt += f"=== {cat.upper()} ===\n"
            for name, info in cls.THRESHOLDS[cat].items():
                prompt += f"- {name}：{info['value']}{info['unit']}（{info['description']}）\n"
        return prompt

    @classmethod
    def get_acceptance_criteria_prompt(cls, category: str = None) -> str:
        """获取验收标准提示词"""
        prompt = "【项目验收标准】\n\n"
        
        categories = [category] if category else cls.ACCEPTANCE_CRITERIA.keys()
        
        for cat in categories:
            if cat not in cls.ACCEPTANCE_CRITERIA:
                continue
            prompt += f"=== {cat.upper()} ===\n"
            for criterion in cls.ACCEPTANCE_CRITERIA[cat]:
                prompt += f"""
[{criterion['id']}] {criterion['description']}（{criterion['priority']}）
验证方法：{criterion['verification_method']}
通过标准：{criterion['pass_criteria']}
参考：{criterion['reference']}
"""
        return prompt
