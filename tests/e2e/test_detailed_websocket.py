"""
详细版 WebSocket 测试 - 查看完整消息流
"""

import asyncio
import json
import websockets


async def test_chat_detailed():
    """测试聊天消息 - 详细版"""
    uri = "ws://localhost:8001/ws/chat/test_detailed"
    
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
        
        # 接收所有响应（最多20条消息或60秒）
        print("\n等待响应...")
        messages = []
        for i in range(20):
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=3.0)
                data = json.loads(response)
                messages.append(data)
                
                msg_type = data.get('type')
                print(f"[消息 {i+1}] type={msg_type}")
                
                # 打印关键信息
                if msg_type == "intent_parsed":
                    print(f"  意图: {data.get('intent', {})}")
                elif msg_type == "chain_generation_stage":
                    print(f"  阶段: {data.get('stage')}, 进度: {data.get('progress')}")
                elif msg_type == "task_graph_generated":
                    print(f"  任务数: {data.get('total_count')}")
                elif msg_type == "chain_generated":
                    print(f"  生成ID: {data.get('generation_id')}")
                elif msg_type == "execution_started":
                    print(f"  执行ID: {data.get('execution_id')}, 总任务: {data.get('total_tasks')}")
                elif msg_type == "task_update":
                    print(f"  任务: {data.get('task_id')}, 状态: {data.get('status')}")
                elif msg_type == "execution_complete":
                    print(f"  执行完成: success={data.get('success')}")
                elif msg_type == "assistant_message":
                    print(f"  AI回复: {data.get('content', '')[:100]}...")
                    break
                elif msg_type == "error":
                    print(f"  错误: {data.get('message')}")
                    break
                    
            except asyncio.TimeoutError:
                print(f"[消息 {i+1}] 超时，停止接收")
                break
        
        print(f"\n总共收到 {len(messages)} 条消息")
        print("\n消息类型序列:")
        for i, msg in enumerate(messages):
            print(f"  {i+1}. {msg.get('type')}")


if __name__ == "__main__":
    asyncio.run(test_chat_detailed())
