"""完整测试端到端功能"""

import asyncio
import json
import websockets
import sys

async def test():
    uri = "ws://localhost:8002/ws/chat/test_e2e_001"
    
    print("=" * 60)
    print("完整端到端测试")
    print("=" * 60)
    
    try:
        async with websockets.connect(uri) as ws:
            # 连接
            await ws.recv()
            print("✓ 连接成功")
            
            # 发送消息
            await ws.send(json.dumps({
                "type": "chat_message", 
                "content": "分析金坛降雨情况"
            }))
            print("✓ 消息已发送: 分析金坛降雨情况")
            
            # 接收消息
            messages = []
            while len(messages) < 30:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=120)
                    data = json.loads(msg)
                    messages.append(data)
                    msg_type = data.get("type")
                    
                    # 打印关键消息
                    if msg_type == "task_update":
                        print(f"\n📋 任务更新:")
                        print(f"   task_id: {data.get('task_id')}")
                        print(f"   friendly_task_name: {data.get('friendly_task_name')}")
                        print(f"   task_type: {data.get('task_type')}")
                        print(f"   status: {data.get('status')}")
                        result = data.get("result")
                        if result:
                            tools = result.get("metrics", {}).get("tools_used", [])
                            print(f"   tools: {tools}")
                    
                    elif msg_type == "execution_complete":
                        print(f"\n✅ 执行完成")
                        summary = data.get("summary", {})
                        print(f"   总任务数: {summary.get('total_tasks')}")
                        print(f"   成功: {summary.get('completed_tasks')}")
                        print(f"   失败: {summary.get('failed_tasks')}")
                    
                    elif msg_type == "assistant_message":
                        content = data.get("content", "")
                        print(f"\n🤖 AI回复:")
                        print(f"   长度: {len(content)} 字符")
                        print(f"   内容: {content[:200]}...")
                        break
                        
                except asyncio.TimeoutError:
                    print("\n⏱️ 接收超时")
                    break
    
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)
    
    # 总结
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    
    # 分析消息
    task_updates = [m for m in messages if m.get("type") == "task_update"]
    print(f"\n任务更新数量: {len(task_updates)}")
    
    for t in task_updates:
        task_id = t.get("task_id")
        friendly = t.get("friendly_task_name")
        status = t.get("status")
        tools = []
        if t.get("result"):
            tools = t.get("result", {}).get("metrics", {}).get("tools_used", [])
        
        # 检查是否有 MCP 工具
        mcp_tools = [x for x in tools if x in ["get_rainfall_data", "get_current_rainfall", "get_weather_forecast"]]
        
        print(f"  - {task_id} ({friendly}): {status}")
        if mcp_tools:
            print(f"    🔧 MCP工具: {mcp_tools}")

if __name__ == "__main__":
    asyncio.run(test())
