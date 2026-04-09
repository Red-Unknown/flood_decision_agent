"""MCP 结果解释提示词模板

为不同复杂度 MCP 工具的结果解释提供 LLM 提示词模板。
"""

from typing import Optional


# =============================================================================
# HiPIMS 洪水模拟结果解释提示词
# =============================================================================

HIPIMS_INTERPRETATION_PROMPT = """你是一位资深水利专家，正在向决策者解释 HiPIMS 2D 洪水模拟结果。

【模拟结果】
{simulation_results}

【要求】
1. 一句话概括最关键的发现
2. 指出最严重的风险点
3. 给出明确的行动建议
4. 说明置信度

【输出格式】
一句话总结: [最关键发现]
主要风险: [风险点]
建议行动: [具体措施]
数据可靠性: [高/中/低]
"""


# =============================================================================
# 水文模型结果解释提示词
# =============================================================================

HYDROLOGY_INTERPRETATION_PROMPT = """你是一位水文专家，正在解释水文模型计算结果。

【计算结果】
{calculation_results}

【要求】
1. 解释计算结果的含义
2. 分析当前水文状况
3. 预测未来趋势
4. 给出预警级别

【输出格式】
结果解读: [结果含义]
当前状况: [水文状况分析]
趋势预测: [未来变化趋势]
预警级别: [红/橙/黄/蓝/无]
"""


# =============================================================================
# 降雨数据分析提示词
# =============================================================================

RAINFALL_INTERPRETATION_PROMPT = """你是一位气象水文专家，正在分析降雨数据。

【降雨数据】
{rainfall_data}

【要求】
1. 总结降雨特征（强度、持续时间、范围）
2. 评估对洪水风险的影响
3. 给出监测建议

【输出格式】
降雨特征: [特征描述]
洪水风险: [高/中/低]
监测建议: [具体建议]
"""


# =============================================================================
# 调度方案解释提示词
# =============================================================================

DISPATCH_INTERPRETATION_PROMPT = """你是一位水库调度专家，正在解释调度方案。

【调度方案】
{dispatch_plan}

【要求】
1. 解释调度策略的核心思路
2. 评估方案效果
3. 指出注意事项
4. 给出执行建议

【输出格式】
方案核心: [策略思路]
预期效果: [效果评估]
注意事项: [风险提醒]
执行建议: [操作建议]
"""


# =============================================================================
# 通用数据解释提示词
# =============================================================================

GENERAL_DATA_INTERPRETATION_PROMPT = """你是一位数据分析专家，正在解释数据查询结果。

【查询结果】
{data_result}

【要求】
1. 提炼关键信息
2. 给出简洁总结

【输出格式】
关键信息: [要点]
总结: [一句话总结]
"""


# =============================================================================
# 提示词管理器
# =============================================================================

class PromptManager:
    """提示词管理器
    
    根据工具类型和复杂度返回对应的提示词模板。
    """
    
    # 工具类型到提示词的映射
    PROMPT_MAP = {
        # 高复杂度工具 - 需要详细解释
        "hipims": HIPIMS_INTERPRETATION_PROMPT,
        "hydrology": HYDROLOGY_INTERPRETATION_PROMPT,
        "flood_simulation": HIPIMS_INTERPRETATION_PROMPT,
        "hydrological_model": HYDROLOGY_INTERPRETATION_PROMPT,
        "dispatch": DISPATCH_INTERPRETATION_PROMPT,
        "reservoir_dispatch": DISPATCH_INTERPRETATION_PROMPT,
        
        # 中复杂度工具 - 简要解释
        "rainfall": RAINFALL_INTERPRETATION_PROMPT,
        "weather": RAINFALL_INTERPRETATION_PROMPT,
        
        # 低复杂度工具 - 通用解释
        "data_hub": GENERAL_DATA_INTERPRETATION_PROMPT,
        "data_query": GENERAL_DATA_INTERPRETATION_PROMPT,
    }
    
    @classmethod
    def get_prompt(cls, tool_name: str) -> Optional[str]:
        """获取工具对应的提示词模板
        
        Args:
            tool_name: 工具名称
            
        Returns:
            提示词模板，如果没有则返回 None
        """
        # 精确匹配
        if tool_name in cls.PROMPT_MAP:
            return cls.PROMPT_MAP[tool_name]
        
        # 模糊匹配（前缀匹配）
        tool_name_lower = tool_name.lower()
        for key, prompt in cls.PROMPT_MAP.items():
            if key in tool_name_lower or tool_name_lower in key:
                return prompt
        
        return None
    
    @classmethod
    def format_prompt(cls, tool_name: str, **kwargs) -> Optional[str]:
        """格式化提示词
        
        Args:
            tool_name: 工具名称
            **kwargs: 提示词模板变量
            
        Returns:
            格式化后的提示词，如果没有模板则返回 None
        """
        prompt_template = cls.get_prompt(tool_name)
        if prompt_template is None:
            return None
        
        try:
            return prompt_template.format(**kwargs)
        except KeyError as e:
            # 如果缺少必要的变量，返回原始模板
            return prompt_template
    
    @classmethod
    def is_complex_tool(cls, tool_name: str) -> bool:
        """判断工具是否为高复杂度工具（需要 LLM 解释）
        
        Args:
            tool_name: 工具名称
            
        Returns:
            是否为高复杂度工具
        """
        complex_tools = {
            "hipims", "hydrology", "flood_simulation",
            "hydrological_model", "dispatch", "reservoir_dispatch",
        }
        
        tool_name_lower = tool_name.lower()
        
        # 精确匹配
        if tool_name_lower in complex_tools:
            return True
        
        # 模糊匹配
        for complex_tool in complex_tools:
            if complex_tool in tool_name_lower:
                return True
        
        return False
    
    @classmethod
    def is_simple_tool(cls, tool_name: str) -> bool:
        """判断工具是否为简单工具（直接透传，无需解释）
        
        Args:
            tool_name: 工具名称
            
        Returns:
            是否为简单工具
        """
        simple_tools = {
            "data_hub", "data_query", "query", "get", "fetch",
            "filesystem", "file", "document", "doc",
        }
        
        tool_name_lower = tool_name.lower()
        
        # 精确匹配
        if tool_name_lower in simple_tools:
            return True
        
        # 模糊匹配
        for simple_tool in simple_tools:
            if simple_tool in tool_name_lower:
                return True
        
        return False


# 简单任务无需提示词
NO_PROMPT_NEEDED = None
