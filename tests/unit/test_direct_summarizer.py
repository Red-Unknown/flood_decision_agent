"""直接测试总结智能体集成 - 带超时"""

import asyncio
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeoutError

# 检查环境变量
if not os.environ.get("KIMI_API_KEY"):
    print("需要 kimi_api_key")
    sys.exit(1)

# 设置项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flood_decision_agent.agents.summarizer import SummarizerAgent
from flood_decision_agent.core.message import BaseMessage, MessageType

def test_summarizer_sync():
    """同步测试总结智能体"""
    print("=" * 60)
    print("直接测试总结智能体（同步）")
    print("=" * 60)
    
    # 创建总结智能体
    summarizer = SummarizerAgent(enable_streaming=False)
    
    # 构建测试数据
    payload = {
        "task_request": {
            "input": "分析金坛降雨情况",
            "type": "data_query",
        },
        "execution_summary": {
            "total_tasks": 3,
            "completed_tasks": 3,
            "failed_tasks": 0,
        },
        "data_pool_snapshot": {},
        "task_graph": {},
        "node_results": [],
    }
    
    # 创建 BaseMessage
    message = BaseMessage(
        type=MessageType.EVENT,
        sender="test",
        payload=payload
    )
    
    print(f"\n调用总结智能体...")
    
    # 调用总结智能体
    result = summarizer._process(message)
    summary_text = result.get("summary", "")
    
    print("\n" + "=" * 60)
    print("总结结果:")
    print("=" * 60)
    print(summary_text[:500] if summary_text else "无结果")
    print("=" * 60)

if __name__ == "__main__":
    # 使用线程池执行带超时 - 延长到120秒
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(test_summarizer_sync)
        try:
            result = future.result(timeout=120)  # 120秒超时
        except FuturesTimeoutError:
            print("总结智能体调用超时（120秒）")
