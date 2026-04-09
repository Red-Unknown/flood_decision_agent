"""简化版真实数据 WebSocket 测试 - 单场景

只测试文件系统操作场景，快速验证 WebSocket 流程。
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def check_api_key():
    """检查 KIMI_API_KEY 环境变量"""
    api_key = os.environ.get("KIMI_API_KEY")
    if not api_key:
        print("=" * 60)
        print("错误: 需要 KIMI_API_KEY 环境变量")
        print("=" * 60)
        sys.exit(1)
    return api_key


async def test_filesystem():
    """测试文件系统场景"""
    import websockets
    
    uri = "ws://localhost:8001/ws/chat/test_fs"
    print(f"\n[连接] {uri}")
    
    try:
        async with websockets.connect(uri) as ws:
            # 等待连接确认
            response = await asyncio.wait_for(ws.recv(), timeout=5.0)
            data = json.loads(response)
            print(f"[连接确认] type={data.get('type')}")
            
            # 发送消息
            message = {
                "type": "chat_message",
                "content": "列出当前目录下的文件"
            }
            print(f"\n[发送] {message['content']}")
            await ws.send(json.dumps(message))
            
            # 接收事件
            print("\n[接收事件]")
            events = []
            for i in range(15):
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=10.0)
                    data = json.loads(response)
                    event_type = data.get('type', 'unknown')
                    events.append(event_type)
                    print(f"  [{i+1}] {event_type}")
                    
                    # 打印关键事件详情
                    if event_type == 'intent_parsed':
                        intent = data.get('intent', {})
                        print(f"      task_type: {intent.get('task_type')}")
                    elif event_type == 'task_update':
                        detail = data.get('detail', {})
                        print(f"      task: {data.get('task_name')}, status: {data.get('status')}")
                        print(f"      detail.stage: {detail.get('stage')}")
                    elif event_type == 'execution_complete':
                        print(f"      success: {data.get('success')}")
                    elif event_type == 'assistant_message':
                        content = data.get('content', '')
                        print(f"      content: {content[:100]}...")
                    
                    # 结束条件
                    if event_type in ['assistant_message', 'error']:
                        break
                        
                except asyncio.TimeoutError:
                    print(f"  [{i+1}] 超时")
                    break
            
            print(f"\n[完成] 共接收 {len(events)} 个事件")
            print(f"事件序列: {events}")
            
            # 验证
            expected = ['user_message_confirm', 'intent_parsed', 'chain_generation_stage', 
                       'task_graph_generated', 'chain_generated', 'execution_started',
                       'task_update', 'execution_progress', 'execution_complete', 'assistant_message']
            
            missing = [e for e in expected if e not in events]
            if missing:
                print(f"\n[警告] 缺少事件: {missing}")
            else:
                print("\n[成功] 所有预期事件已接收")
            
            return len(missing) == 0
            
    except Exception as e:
        print(f"\n[错误] {e}")
        return False


async def main():
    """主程序"""
    print("=" * 60)
    print("真实数据 WebSocket 测试 - 文件系统场景")
    print("=" * 60)
    
    api_key = check_api_key()
    print(f"\n✓ API Key 已配置: {api_key[:10]}...")
    
    success = await test_filesystem()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ 测试通过")
    else:
        print("✗ 测试失败")
    print("=" * 60)
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
