"""模拟用户查询金坛天气 - 测试日志和数据池"""

import asyncio
import json
import websockets
import os

URI = "ws://localhost:8001/ws/chat/test_logging_001"


async def test_weather_query():
    """测试查询金坛天气"""
    print(f"连接到: {URI}")
    
    async with websockets.connect(URI) as ws:
        print("✅ WebSocket 连接成功")
        
        hello_msg = await ws.recv()
        print(f"📥 系统消息: {json.loads(hello_msg)[:200] if len(hello_msg) > 200 else hello_msg}")
        
        query = "查询金坛天气"
        print(f"\n📤 发送消息: {query}")
        
        await ws.send(json.dumps({
            "type": "chat_message",
            "content": query
        }))
        
        messages = []
        max_messages = 50
        timeout = 60
        
        while len(messages) < max_messages:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=timeout)
                data = json.loads(msg)
                messages.append(data)
                
                msg_type = data.get("type", "unknown")
                content = data.get("content", "")
                
                if msg_type == "chat_message":
                    print(f"\n📥 AI回复: {content[:500]}...")
                elif msg_type == "task_update":
                    print(f"\n📥 任务更新: {content[:200]}...")
                elif msg_type == "error":
                    print(f"\n❌ 错误: {content}")
                elif msg_type == "done":
                    print(f"\n✅ 完成")
                    break
                else:
                    print(f"\n📥 消息类型: {msg_type}")
                    
            except asyncio.TimeoutError:
                print(f"\n⏱️ 等待超时 (已收到 {len(messages)} 条消息)")
                break
        
        print(f"\n\n📊 总共收到 {len(messages)} 条消息")
        
        print("\n\n=== 完整消息列表 ===")
        for i, msg in enumerate(messages):
            print(f"\n--- 消息 {i+1} ---")
            print(f"类型: {msg.get('type')}")
            if msg.get('content'):
                content = str(msg.get('content'))[:500]
                print(f"内容: {content}")


if __name__ == "__main__":
    try:
        asyncio.run(test_weather_query())
    except KeyboardInterrupt:
        print("\n\n👋 测试结束")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
