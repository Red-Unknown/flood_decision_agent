"""
简化版 WebSocket 测试
"""

import asyncio
import json
import websockets


async def test_chat():
    """测试聊天消息"""
    uri = "ws://localhost:8001/ws/chat/test_simple"
    
    print("连接到 WebSocket...")
    async with websockets.connect(uri) as ws:
        # 等待连接确认
        response = await ws.recv()
        data = json.loads(response)
        print(f"[连接] {data}")
        
        # 发送聊天消息
        print("\n发送聊天消息...")
        await ws.send(json.dumps({
            "type": "chat_message",
            "content": "查询今日水位",
        }))
        
        # 接收响应（最多10条消息或30秒）
        print("\n等待响应...")
        for i in range(10):
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                data = json.loads(response)
                print(f"[消息 {i+1}] type={data.get('type')}")
                
                if data.get("type") == "error":
                    print(f"  错误: {data.get('message')}")
                    break
                elif data.get("type") == "assistant_message":
                    print(f"  内容: {data.get('content')[:100]}...")
                    break
            except asyncio.TimeoutError:
                print(f"[消息 {i+1}] 超时")
                break
        
        print("\n测试完成")


if __name__ == "__main__":
    asyncio.run(test_chat())
