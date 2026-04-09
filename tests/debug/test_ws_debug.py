"""测试WebSocket请求 - 带调试输出"""
import asyncio
import json
import websockets

async def test():
    uri = "ws://localhost:8001/ws/chat/test_debug_003"
    async with websockets.connect(uri) as ws:
        msg = await ws.recv()
        print(f"Connected")

        await ws.send(json.dumps({
            "type": "chat_message",
            "content": "查询金坛天气"
        }))

        for i in range(30):
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=10)
                data = json.loads(msg)
                msg_type = data.get('type')
                print(f"Msg {i}: {msg_type}")
                
                if msg_type == 'assistant_message':
                    content = data.get('content', '')
                    print(f"\n=== 最终结果 ===")
                    print(content[:800])
                    break
                    
                if msg_type == 'task_update':
                    result = data.get('result')
                    if result:
                        output = result.get('output', {})
                        print(f"  output: {str(output)[:150]}")
                    else:
                        print(f"  result is None")
                        
            except asyncio.TimeoutError:
                print("Timeout")
                break

asyncio.run(test())
