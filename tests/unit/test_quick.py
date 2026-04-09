"""快速测试 MCP 工具和数据池"""

import asyncio
import json
import websockets
import time

async def test():
    uri = "ws://localhost:8001/ws/chat/test_001"
    
    print("=" * 60)
    print("测试 MCP 工具匹配")
    print("=" * 60)
    
    start_time = time.time()
    
    async with websockets.connect(uri, max_size=10_000_000) as ws:
        # 连接
        await ws.recv()
        print(f"✓ 连接成功 ({time.time() - start_time:.1f}s)")
        
        # 发送
        await ws.send(json.dumps({
            "type": "chat_message", 
            "content": "分析金坛降雨情况"
        }))
        print(f"✓ 消息已发送 ({time.time() - start_time:.1f}s)")
        
        # 接收消息，最多30个
        msg_count = 0
        last_msg = None
        
        while msg_count < 30:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=600)
                data = json.loads(msg)
                msg_type = data.get("type")
                msg_count += 1
                
                # 打印关键消息
                print(f"[{msg_count}] {msg_type}: ", end="")
                
                if msg_type == "task_update":
                    task_id = data.get("task_id")
                    status = data.get("status")
                    result = data.get("result")
                    tools = []
                    if result:
                        tools = result.get("metrics", {}).get("tools_used", [])
                    print(f"{task_id} - {status}")
                    print(f"       tools: {tools}")
                    last_msg = data
                    
                elif msg_type == "execution_complete":
                    summary = data.get("summary", {})
                    print(f"完成: {summary.get('total_tasks')} 任务")
                    last_msg = data
                    
                elif msg_type == "assistant_message":
                    content = data.get("content", "")
                    print(f"AI回复: {len(content)} 字符")
                    print(f"       {content}")
                    last_msg = data
                    break
                else:
                    print("(忽略)")
                    
            except asyncio.TimeoutError:
                print(f"\n⏱️ 接收超时 ({time.time() - start_time:.1f}s)")
                break
        
        print(f"\n总消息数: {msg_count}")
        print(f"总耗时: {time.time() - start_time:.1f}s")

if __name__ == "__main__":
    asyncio.run(test())
