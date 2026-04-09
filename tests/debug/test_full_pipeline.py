import asyncio
import json
import websockets

async def test_websocket():
    uri = 'ws://127.0.0.1:8001/ws/chat/final_test_001'

    try:
        async with websockets.connect(uri) as websocket:
            print('=' * 60)
            print('开始测试: 查询金坛天气')
            print('=' * 60)

            message = {
                'type': 'chat_message',
                'content': '查询金坛天气'
            }
            await websocket.send(json.dumps(message))

            final_content = None
            task_completed = False

            for i in range(50):
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=30)
                    data = json.loads(response)
                    msg_type = data.get('type')

                    if msg_type == 'connected':
                        print(f'[✓] WebSocket连接成功')
                    elif msg_type == 'user_message_confirm':
                        print(f'[✓] 用户消息确认: {data.get("content")}')
                    elif msg_type == 'intent_parsed':
                        intent = data.get('intent', {})
                        print(f'[✓] 意图解析成功: {intent.get("task_type")}')
                    elif msg_type == 'chain_generation_stage':
                        pass  # 跳过详细阶段输出
                    elif msg_type == 'task_graph_generated':
                        tasks = data.get('tasks', [])
                        print(f'[✓] 任务图生成成功: {len(tasks)}个任务')
                    elif msg_type == 'chain_generated':
                        print(f'[✓] 决策链生成成功')
                    elif msg_type == 'execution_started':
                        total = data.get('total_tasks', 0)
                        print(f'[✓] 任务执行开始: {total}个任务')
                    elif msg_type == 'task_update':
                        task_id = data.get('task_id')
                        status = data.get('status')
                        result = data.get('result', {})
                        if status == 'completed':
                            output = result.get('output', {})
                            print(f'[✓] 任务完成: {task_id}')
                            # 打印MCP返回的数据
                            if output:
                                print(f'    输出数据: {json.dumps(output, ensure_ascii=False)[:200]}...')
                    elif msg_type == 'execution_progress':
                        completed = data.get('completed_count')
                        total = data.get('total_count')
                        print(f'    进度: {completed}/{total}')
                    elif msg_type == 'execution_complete':
                        summary = data.get('summary', {})
                        print(f'[✓] 执行完成: {summary.get("completed_tasks")}/{summary.get("total_tasks")} 任务成功')
                        task_completed = True
                    elif msg_type == 'assistant_message':
                        final_content = data.get('content', '')
                        print(f'\n{"=" * 60}')
                        print('最终总结智能体输出:')
                        print('=' * 60)
                        print(final_content)
                        print('=' * 60)
                        break
                    elif msg_type == 'error':
                        print(f'[✗] 错误: {data.get("message")}')

                except asyncio.TimeoutError:
                    print('超时等待响应')
                    break

            # 验证结果
            print('\n' + '=' * 60)
            print('测试验证结果:')
            print('=' * 60)
            if task_completed and final_content:
                # 检查总结是否包含天气数据关键词
                keywords = ['金坛', '天气', '温度', '降雨', '多云', '晴']
                found_keywords = [k for k in keywords if k in final_content]
                if found_keywords:
                    print(f'✅ 测试通过! 总结包含关键词: {found_keywords}')
                else:
                    print(f'⚠️ 总结未包含预期关键词')
                print(f'✅ 完整链路测试通过!')
            else:
                print(f'❌ 测试未完成')

    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

asyncio.run(test_websocket())
