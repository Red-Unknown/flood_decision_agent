"""总结智能体提示词模块

提供专业的总结提示词模板，用于生成任务执行总结报告。
"""

from typing import Any, Dict


# ==================== 系统提示词 ====================

SUMMARIZER_SYSTEM_PROMPT = """你是一位水利调度专家，需要对任务执行过程和结果进行专业总结。

你的职责：
1. 分析任务执行数据和结果
2. 提取关键发现和洞察
3. 生成结构化的专业总结报告
4. 提供可操作的建议

输出要求：
- 使用专业的水利术语
- 数据准确、逻辑清晰
- 建议具有可操作性
- 篇幅适中（300-800 字）"""


# ==================== 总结报告模板 ====================

SUMMARY_REPORT_TEMPLATE = """请对以下水利调度任务执行过程和结果进行总结：

【用户请求】
{user_input}

【任务类型】
{task_type}

【执行统计】
- 总任务数：{total_tasks}
- 成功完成：{completed_tasks}
- 失败任务：{failed_tasks}
- 总耗时：{duration_ms:.2f}ms

【节点执行详情】
{node_details}

【数据池关键数据】
{data_pool_snapshot}

【任务图结构】
{task_graph_info}

请生成一份专业的执行总结报告，必须包含以下部分：

## 一、任务执行概况
简要说明任务类型、执行时间、成功率等基本信息。

## 二、关键数据发现
详细列出从 MCP 工具调用中获取的重要数据，例如：
- 降雨数据：城市、降雨量、降雨时段等
- 水文数据：流量、水位、流速等
- 模拟结果：洪峰流量、淹没范围、演进时间等
- 调度方案：出库流量、水位控制、调度措施等

## 三、趋势预测和风险评估
基于执行结果分析：
- 当前状况评估
- 未来趋势预测
- 潜在风险识别
- 预警级别建议

## 四、调度建议和行动指南
提供具体可操作的建议：
- 立即采取的措施
- 短期（24-72 小时）行动计划
- 中长期监控重点
- 需要关注的风险点

注意：
1. 如果有具体的降雨、水文数据，请在"关键数据发现"部分详细列出
2. 如果数据表明存在风险，请在"风险评估"部分明确说明
3. 所有建议必须基于实际执行结果，具有针对性"""


# ==================== 备用总结模板（LLM 不可用时） ====================

FALLBACK_SUMMARY_TEMPLATE = """【执行总结】

本次任务共包含 {total_tasks} 个子任务，其中 {completed_tasks} 个成功完成，{failed_tasks} 个失败，总耗时 {duration_ms:.2f}ms。

【任务执行列表】
{task_list}

【执行结果】
各阶段执行{"顺利" if failed_tasks == 0 else "存在失败"}，数据已采集并处理完毕。

【建议】
建议持续关注水情变化，根据实际情况调整调度策略。"""


# ==================== 提示词构建函数 ====================

def build_summary_prompt(
    user_input: str,
    task_type: str,
    total_tasks: int,
    completed_tasks: int,
    failed_tasks: int,
    duration_ms: float,
    node_details: list,
    data_pool_snapshot: Dict[str, Any],
    task_graph_info: Dict[str, Any],
) -> str:
    """构建总结提示词
    
    Args:
        user_input: 用户输入
        task_type: 任务类型
        total_tasks: 总任务数
        completed_tasks: 完成任务数
        failed_tasks: 失败任务数
        duration_ms: 总耗时（毫秒）
        node_details: 节点执行详情列表
        data_pool_snapshot: 数据池快照
        task_graph_info: 任务图信息
        
    Returns:
        构建好的提示词
    """
    # 格式化节点详情
    if node_details:
        node_details_text = "\n".join(node_details)
    else:
        node_details_text = "无详细节点信息"
    
    # 格式化数据池快照（限制长度）
    import json
    data_pool_text = json.dumps(data_pool_snapshot, ensure_ascii=False, indent=2)
    if len(data_pool_text) > 1000:
        data_pool_text = data_pool_text[:1000] + "...（数据过长，已截断）"
    
    # 格式化任务图信息
    if task_graph_info:
        task_graph_text = f"任务数：{task_graph_info.get('total_tasks', 0)}, " \
                         f"可靠性评分：{task_graph_info.get('reliability_score', 0):.2f}"
    else:
        task_graph_text = "无任务图信息"
    
    return SUMMARY_REPORT_TEMPLATE.format(
        user_input=user_input,
        task_type=task_type,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        failed_tasks=failed_tasks,
        duration_ms=duration_ms,
        node_details=node_details_text,
        data_pool_snapshot=data_pool_text,
        task_graph_info=task_graph_text,
    )


def build_fallback_summary(
    total_tasks: int,
    completed_tasks: int,
    failed_tasks: int,
    duration_ms: float,
    task_list: list,
) -> str:
    """构建备用总结（LLM 不可用时）
    
    Args:
        total_tasks: 总任务数
        completed_tasks: 完成任务数
        failed_tasks: 失败任务数
        duration_ms: 总耗时（毫秒）
        task_list: 任务列表
        
    Returns:
        备用总结文本
    """
    # 格式化任务列表
    if task_list:
        task_list_text = "\n".join([
            f"- {task.get('node_id', 'unknown')} ({task.get('task_type', 'unknown')}): "
            f"{task.get('status', 'unknown')}"
            for task in task_list
        ])
    else:
        task_list_text = "无任务信息"
    
    return FALLBACK_SUMMARY_TEMPLATE.format(
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        failed_tasks=failed_tasks,
        duration_ms=duration_ms,
        task_list=task_list_text,
    )


# ==================== 领域特定总结模板 ====================

# 降雨数据查询总结模板
RAINFALL_SUMMARY_TEMPLATE = """【降雨数据分析】

根据实时监测数据，{city}地区当前降雨情况如下：

- 当前天气状况：{weather_description}
- 温度：{temperature}°C
- 湿度：{humidity}%
- 气压：{pressure}hPa

【降雨量统计】
- 过去 1 小时降雨量：{rain_1h}mm
- 过去 3 小时降雨量：{rain_3h}mm

【趋势分析】
{trend_analysis}

【建议】
{suggestions}"""


# 洪水模拟总结模板
FLOOD_SIMULATION_SUMMARY_TEMPLATE = """【洪水模拟结果】

模拟时长：{duration}秒
模拟区域：{area}
最大淹没深度：{max_depth}m
最大流速：{max_velocity}m/s

【风险评估】
- 高风险区域：{high_risk_areas}
- 受影响人口：{affected_population}
- 关键基础设施：{critical_infrastructure}

【建议措施】
{suggestions}"""


# ==================== 提示词管理工具 ====================

class SummaryPromptManager:
    """总结提示词管理器"""
    
    @staticmethod
    def get_system_prompt() -> str:
        """获取系统提示词"""
        return SUMMARIZER_SYSTEM_PROMPT
    
    @staticmethod
    def get_template(template_type: str = "default") -> str:
        """获取指定类型的模板
        
        Args:
            template_type: 模板类型（default/rainfall/flood_simulation）
            
        Returns:
            模板字符串
        """
        templates = {
            "default": SUMMARY_REPORT_TEMPLATE,
            "rainfall": RAINFALL_SUMMARY_TEMPLATE,
            "flood_simulation": FLOOD_SIMULATION_SUMMARY_TEMPLATE,
        }
        return templates.get(template_type, SUMMARY_REPORT_TEMPLATE)
    
    @staticmethod
    def is_complex_tool(server_name: str) -> bool:
        """判断工具是否为复杂工具（需要 LLM 解释）
        
        Args:
            server_name: 服务器名称
            
        Returns:
            是否为复杂工具
        """
        complex_servers = {"hydrology", "hipims", "decision_chain"}
        return server_name.lower() in complex_servers
