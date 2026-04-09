"""WebSocket 实时测试脚本

测试 WebSocket 连接和功能
"""

import asyncio
import websockets
import json


async def test_websocket():
    uri = 'ws://localhost:8000/ws/chat/test_conv_001'
    print('连接 WebSocket...')
    
    async with websockets.connect(uri) as websocket:
        # 接收连接成功消息
        response = await websocket.recv()
        data = json.loads(response)
        print(f'连接响应: {data}')
        
        # 发送 ping
        await websocket.send(json.dumps({'type': 'ping', 'timestamp': 1234567890}))
        response = await websocket.recv()
        data = json.loads(response)
        print(f'Ping 响应: {data}')
        
        # 发送聊天消息
        await websocket.send(json.dumps({
            'type': 'chat_message',
            'content': '你好',
            'role': 'user',
        }))
        
        # 接收响应
        for _ in range(5):
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                data = json.loads(response)
                print(f"消息类型: {data.get('type')}")
                if data.get('type') == 'complete':
                    break
            except asyncio.TimeoutError:
                break
        
        print('WebSocket 测试完成!')


if __name__ == '__main__':
    asyncio.run(test_websocket())
