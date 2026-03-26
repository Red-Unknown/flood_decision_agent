"""端到端测试脚本.

测试Web端完整流程，包括：
1. 健康检查
2. 创建对话
3. 发送消息并接收流式响应
4. 验证过程性事件
5. 获取消息历史
"""

import json
import time
import requests

BASE_URL = "http://localhost:8006"

def test_health():
    """测试健康检查接口."""
    print("=" * 60)
    print("测试1: 健康检查")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✓ 健康检查通过\n")

def test_create_conversation():
    """测试创建对话."""
    print("=" * 60)
    print("测试2: 创建对话")
    print("=" * 60)
    
    response = requests.post(
        f"{BASE_URL}/api/conversations",
        json={"title": "测试对话"}
    )
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    assert response.status_code == 200
    assert "id" in data
    print("✓ 创建对话通过\n")
    return data["id"]

def test_send_message_stream(conversation_id):
    """测试发送消息（流式响应）."""
    print("=" * 60)
    print("测试3: 发送消息（流式响应）")
    print("=" * 60)
    
    message = "分析当前降雨情况"
    print(f"用户输入: {message}")
    print("-" * 60)
    
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "message": message,
            "conversation_id": conversation_id,
            "stream": True
        },
        stream=True
    )
    
    assert response.status_code == 200
    
    # 解析SSE流
    process_events = []
    content_chunks = []
    
    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                try:
                    data = json.loads(line_str[6:])
                    
                    if data.get('type') == 'process_event':
                        process_events.append(data)
                        print(f"📋 [过程事件] {data['stage']}: {data['data'].get('message', '')}")
                        
                        # 如果是任务列表事件，打印任务详情
                        if data['stage'] == 'task_list_generated' and 'tasks' in data['data']:
                            print(f"   任务数量: {data['data']['total_count']}")
                            for task in data['data']['tasks'][:3]:  # 只打印前3个
                                print(f"   - {task['task_name']} ({task['task_type']})")
                            if len(data['data']['tasks']) > 3:
                                print(f"   ... 还有 {len(data['data']['tasks']) - 3} 个任务")
                                
                    elif data.get('type') == 'chunk':
                        content_chunks.append(data['content'])
                        
                    elif data.get('type') == 'complete':
                        print(f"\n✓ 响应完成，内容长度: {len(data['content'])} 字符")
                        
                except json.JSONDecodeError:
                    pass
    
    print(f"\n📊 统计:")
    print(f"   - 过程性事件: {len(process_events)} 个")
    print(f"   - 内容块: {len(content_chunks)} 个")
    
    # 验证关键事件
    stages = [e['stage'] for e in process_events]
    print(f"\n📋 事件类型: {', '.join(stages)}")
    
    assert len(process_events) > 0, "应该收到过程性事件"
    assert 'task_accepted' in stages, "应该有任务接取事件"
    
    print("✓ 流式响应测试通过\n")
    return process_events

def test_get_messages(conversation_id):
    """测试获取消息历史."""
    print("=" * 60)
    print("测试4: 获取消息历史")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/api/conversations/{conversation_id}/messages")
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"消息数量: {len(data)}")
    
    for i, msg in enumerate(data):
        role = msg['role']
        content_preview = msg['content'][:100] + '...' if len(msg['content']) > 100 else msg['content']
        print(f"  [{i+1}] {role}: {content_preview}")
    
    assert response.status_code == 200
    assert len(data) >= 2, "应该有用户消息和AI回复"
    print("✓ 获取消息历史通过\n")

def test_get_process_events(conversation_id):
    """测试获取过程性事件."""
    print("=" * 60)
    print("测试5: 获取过程性事件")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/api/conversations/{conversation_id}/process-events")
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"事件数量: {len(data)}")
    
    for i, event in enumerate(data):
        print(f"  [{i+1}] {event['stage']}: {event['data'].get('message', '')}")
    
    assert response.status_code == 200
    assert len(data) > 0, "应该有过事件"
    print("✓ 获取过程性事件通过\n")

def main():
    """主函数."""
    print("\n" + "=" * 60)
    print("水利智脑 Web端 - 端到端测试")
    print("=" * 60 + "\n")
    
    try:
        # 测试1: 健康检查
        test_health()
        
        # 测试2: 创建对话
        conversation_id = test_create_conversation()
        
        # 测试3: 发送消息（流式响应）
        process_events = test_send_message_stream(conversation_id)
        
        # 测试4: 获取消息历史
        test_get_messages(conversation_id)
        
        # 测试5: 获取过程性事件
        test_get_process_events(conversation_id)
        
        print("=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n✗ 连接失败，请确保后端服务已启动")
        print(f"  后端地址: {BASE_URL}")
        return 1
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
