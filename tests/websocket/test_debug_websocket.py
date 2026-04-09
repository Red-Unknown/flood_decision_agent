"""调试 WebSocket 消息处理"""

import asyncio
import json
import websockets

async def test_websocket():
    uri = "ws://localhost:8002/ws/chat/test_debug_001"
    
    async with websockets.connect(uri) as ws:
        # 等待连接确认
        response = await ws.recv()
        print(f"连接确认：{json.loads(response)}")
        
        # 发送消息
        message = {
            "type": "chat_message",
            "content": "分析金坛降雨情况",
            "timestamp": 1234567890,
        }
        await ws.send(json.dumps(message))
        
        # 接收所有消息
        while True:
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=120.0)
                data = json.loads(response)
                msg_type = data.get("type", "unknown")
                
                if msg_type == "execution_complete":
                    print("\n=== execution_complete 消息 ===")
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                    print("=== END ===\n")
                
                if msg_type == "assistant_message":
                    print("\n=== assistant_message 消息 ===")
                    print(data.get("content", "")[:500])
                    print("=== END ===\n")
                    break
                    
            except asyncio.TimeoutError:
                print("超时")
                break

if __name__ == "__main__":
    asyncio.run(test_websocket())
