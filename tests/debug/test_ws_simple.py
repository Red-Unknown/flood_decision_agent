"""测试WebSocket请求"""
import asyncio
import json
import websockets

async def test():
    uri = "ws://localhost:8001/ws/chat/test_debug_001"
    async with websockets.connect(uri) as ws:
        # 接收连接消息
        msg = await ws.recv()
        print(f"Connected: {msg[:100]}")

        # 发送查询
        await ws.send(json.dumps({
            "type": "chat_message",
            "content": "查询金坛天气"
        }))

        # 接收消息
        for i in range(30):
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=5)
                data = json.loads(msg)
                print(f"Msg {i}: {data.get('type')}")
                if data.get('type') == 'assistant_message':
                    print(f"Result: {data.get('content', '')[:500]}")
                    break
            except asyncio.TimeoutError:
                break

asyncio.run(test())
