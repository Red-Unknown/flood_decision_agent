"""测试总结智能体"""

import asyncio
import os
import sys

# 检查环境变量
if not os.environ.get("KIMI_API_KEY"):
    print("需要 kimi_api_key")
    sys.exit(1)

from flood_decision_agent.agents.summarizer import SummarizerAgent
from flood_decision_agent.core.message import BaseMessage

async def test_summarizer():
    """测试总结智能体"""
    print("=" * 60)
    print("测试总结智能体")
    print("=" * 60)
    
    # 创建总结智能体
    summarizer = SummarizerAgent(enable_streaming=True)
    
    # 构建测试数据
    test_payload = {
        "task_request": {
            "input": "分析金坛降雨情况",
            "type": "data_query",
        },
        "execution_summary": {
            "total_tasks": 3,
            "completed_tasks": 3,
            "failed_tasks": 0,
            "total_duration_ms": 8000,
            "task_results": [
                {
                    "node_id": "data_query_000",
                    "task_type": "data_collection",
                    "status": "success",
                    "output": {
                        "rainfall": 50.5,
                        "city": "金坛",
                        "timestamp": "2026-04-07",
                    },
                    "metrics": {
                        "elapsed_time_ms": 100,
                        "tools_used": ["get_rainfall_data"],
                    }
                }
            ]
        },
        "data_pool_snapshot": {
            "rainfall_data": {
                "city": "金坛",
                "rainfall": 50.5,
                "unit": "mm",
            }
        },
        "task_graph": {
            "total_tasks": 3,
            "reliability_score": 1.0,
        },
        "node_results": [
            {
                "node_id": "data_query_000",
                "task_type": "data_collection",
                "status": "success",
                "output": {
                    "rainfall": 50.5,
                    "city": "金坛",
                },
                "metrics": {
                    "elapsed_time_ms": 100,
                    "tools_used": ["get_rainfall_data"],
                }
            }
        ],
    }
    
    # 调用总结智能体
    print("\n调用总结智能体...\n")
    message = BaseMessage(
        type="summary_request",
        sender="test",
        payload=test_payload
    )
    result = summarizer._process(message)
    
    print("\n" + "=" * 60)
    print("总结结果:")
    print("=" * 60)
    print(result.get("summary", "无总结内容"))
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_summarizer())
