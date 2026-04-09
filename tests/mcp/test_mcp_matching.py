"""测试 MCP 工具匹配"""

import asyncio
import json
import websockets

async def test_websocket():
    uri = "ws://localhost:8002/ws/chat/test_mcp_001"
    
    print("=" * 60)
    print("测试 MCP 工具匹配")
    print("=" * 60)
    print(f"连接: {uri}")
    
    async with websockets.connect(uri) as ws:
        # 等待连接确认
        response = await ws.recv()
        data = json.loads(response)
        print(f"✓ 连接成功: {data.get('conversation_id')}")
        
        # 发送降雨分析请求
        message = {
            "type": "chat_message",
            "content": "分析金坛降雨情况",
            "timestamp": 1234567890,
        }
        await ws.send(json.dumps(message))
        print(f"✓ 发送消息: {message['content']}")
        
        # 接收所有消息
        task_updates = []
        
        while True:
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=120.0)
                data = json.loads(response)
                msg_type = data.get("type", "unknown")
                
                if msg_type == "task_update":
                    task_info = {
                        "task_id": data.get("task_id"),
                        "friendly_task_name": data.get("friendly_task_name"),
                        "task_type": data.get("task_type"),
                        "friendly_task_type": data.get("friendly_task_type"),
                        "status": data.get("status"),
                        "result": data.get("result", {}),
                    }
                    task_updates.append(task_info)
                    
                    # 打印任务信息
                    print(f"\n--- 任务更新 ---")
                    print(f"  task_id: {task_info['task_id']}")
                    print(f"  friendly_task_name: {task_info['friendly_task_name']}")
                    print(f"  task_type: {task_info['task_type']}")
                    print(f"  friendly_task_type: {task_info['friendly_task_type']}")
                    print(f"  status: {task_info['status']}")
                    
                    # 打印使用的工具
                    result = task_info.get("result", {})
                    if result:
                        metrics = result.get("metrics", {})
                        tools_used = metrics.get("tools_used", [])
                        print(f"  使用的工具: {tools_used}")
                        
                        # 打印 MCP 工具信息
                        if result.get("data", {}):
                            print(f"  MCP工具返回数据: {json.dumps(result.get('data', {}), ensure_ascii=False)[:200]}...")
                
                elif msg_type == "execution_complete":
                    print(f"\n--- 执行完成 ---")
                    print(f"  summary: {data.get('summary')}")
                    print(f"  results count: {len(data.get('results', []))}")
                
                elif msg_type == "assistant_message":
                    print(f"\n--- AI 回复 ---")
                    content = data.get("content", "")
                    print(f"  内容: {content[:300]}...")
                    break
                    
            except asyncio.TimeoutError:
                print("\n超时")
                break

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    
    # 总结
    print(f"\n任务更新数量: {len(task_updates)}")
    for i, task in enumerate(task_updates):
        print(f"\n任务 {i+1}:")
        print(f"  - friendly_task_name: {task['friendly_task_name']}")
        print(f"  - status: {task['status']}")
        tools = task.get("result", {}).get("metrics", {}).get("tools_used", [])
        print(f"  - tools_used: {tools}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
