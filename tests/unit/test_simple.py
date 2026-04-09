"""简单测试 MCP 工具匹配"""

import asyncio
import json
import websockets

async def test():
    uri = "ws://localhost:8002/ws/chat/test_001"
    
    async with websockets.connect(uri) as ws:
        # 连接
        await ws.recv()
        
        # 发送
        await ws.send(json.dumps({
            "type": "chat_message", 
            "content": "分析金坛降雨情况"
        }))
        
        # 接收
        results = []
        while len(results) < 10:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=900)  # 15分钟超时
                data = json.loads(msg)
                msg_type = data.get("type")
                print(f"{msg_type}: {data.get('task_id', data.get('summary', ''))}")
                
                if msg_type == "task_update":
                    results.append(data)
                elif msg_type == "assistant_message":
                    # 打印 AI 回复
                    content = data.get("content", "")
                    print(f"\n=== AI 回复 ===")
                    print(content[:500] if content else "(空)")
                    print("=" * 30)
                    break
                elif msg_type == "execution_complete":
                    print(f"执行完成: {data.get('summary')}")
                    
            except asyncio.TimeoutError:
                print("接收超时")
                break
        
        # 打印结果
        print("\n" + "="*50)
        print("任务结果:")
        for r in results:
            task_id = r.get("task_id")
            status = r.get("status")
            friendly_name = r.get("friendly_task_name", "")
            task_type = r.get("task_type", "")
            result = r.get("result")
            tools = []
            if result:
                tools = result.get("metrics", {}).get("tools_used", [])
            print(f"  {task_id} ({friendly_name}): {status}")
            print(f"    task_type: {task_type}")
            print(f"    tools: {tools}")

if __name__ == "__main__":
    asyncio.run(test())
