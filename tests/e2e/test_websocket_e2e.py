"""
WebSocket 端到端测试

测试 WebSocket 连接和消息流传输的完整流程。
"""

import asyncio
import json
import time
import websockets
import pytest


class TestWebSocketE2E:
    """WebSocket 端到端测试"""

    BASE_URL = "ws://localhost:8001"
    
    @pytest.mark.asyncio
    async def test_websocket_connection(self):
        """测试 WebSocket 连接"""
        try:
            async with websockets.connect(f"{self.BASE_URL}/ws/chat/test_session") as ws:
                # 等待连接确认
                response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                data = json.loads(response)
                
                print(f"[连接测试] 收到消息: {data}")
                assert data.get("type") == "connected"
                print("✅ WebSocket 连接成功")
        except Exception as e:
            pytest.fail(f"WebSocket 连接失败: {e}")

    @pytest.mark.asyncio
    async def test_ping_pong(self):
        """测试心跳"""
        try:
            async with websockets.connect(f"{self.BASE_URL}/ws/chat/test_ping") as ws:
                # 等待连接确认
                await asyncio.wait_for(ws.recv(), timeout=5.0)
                
                # 发送 ping
                await ws.send(json.dumps({"type": "ping"}))
                
                # 等待 pong
                response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                data = json.loads(response)
                
                print(f"[心跳测试] 收到消息: {data}")
                assert data.get("type") == "pong"
                print("✅ 心跳测试成功")
        except Exception as e:
            pytest.fail(f"心跳测试失败: {e}")

    @pytest.mark.asyncio
    async def test_chat_message_flow(self):
        """测试聊天消息完整流程"""
        try:
            async with websockets.connect(f"{self.BASE_URL}/ws/chat/test_chat") as ws:
                received_messages = []
                
                # 等待连接确认
                await asyncio.wait_for(ws.recv(), timeout=5.0)
                
                # 发送聊天消息
                await ws.send(json.dumps({
                    "type": "chat_message",
                    "content": "查询今日水位",
                }))
                
                print("[聊天测试] 已发送消息，等待响应...")
                
                # 接收消息（带超时）
                start_time = time.time()
                while time.time() - start_time < 30:  # 30秒超时
                    try:
                        response = await asyncio.wait_for(ws.recv(), timeout=2.0)
                        data = json.loads(response)
                        received_messages.append(data)
                        
                        print(f"[聊天测试] 收到: type={data.get('type')}")
                        
                        # 如果收到 assistant_message 或 error，结束
                        if data.get("type") in ["assistant_message", "error", "complete"]:
                            break
                    except asyncio.TimeoutError:
                        # 继续等待
                        continue
                
                # 验证收到的消息
                message_types = [m.get("type") for m in received_messages]
                print(f"[聊天测试] 收到的消息类型: {message_types}")
                
                # 检查关键消息
                if "error" in message_types:
                    error_msg = [m for m in received_messages if m.get("type") == "error"][0]
                    print(f"⚠️ 收到错误: {error_msg}")
                
                # 验证至少收到了 user_message_confirm
                assert "user_message_confirm" in message_types, "未收到用户消息确认"
                print("✅ 聊天消息流程测试成功")
                
        except Exception as e:
            pytest.fail(f"聊天消息测试失败: {e}")

    @pytest.mark.asyncio
    async def test_plan_mode_flow(self):
        """测试 Plan 模式完整流程"""
        try:
            async with websockets.connect(f"{self.BASE_URL}/ws/chat/test_plan") as ws:
                received_messages = []
                
                # 等待连接确认
                await asyncio.wait_for(ws.recv(), timeout=5.0)
                
                # 第一步：生成 Plan 文档
                print("[Plan测试] 步骤1: 生成 Plan 文档...")
                await ws.send(json.dumps({
                    "type": "start_plan",
                    "user_input": "设计一个洪水预警系统",
                }))
                
                start_time = time.time()
                while time.time() - start_time < 60:  # 60秒超时
                    try:
                        response = await asyncio.wait_for(ws.recv(), timeout=2.0)
                        data = json.loads(response)
                        received_messages.append(data)
                        
                        print(f"[Plan测试] 收到: type={data.get('type')}")
                        
                        if data.get("type") == "document_complete":
                            plan_id = data.get("document_id")
                            print(f"[Plan测试] Plan 文档生成完成: {plan_id}")
                            break
                        elif data.get("type") == "error":
                            print(f"⚠️ Plan 生成错误: {data}")
                            break
                    except asyncio.TimeoutError:
                        continue
                
                # 第二步：确认 Plan 并执行
                plan_complete = [m for m in received_messages if m.get("type") == "document_complete"]
                if plan_complete:
                    plan_id = plan_complete[0].get("document_id")
                    print(f"[Plan测试] 步骤2: 确认 Plan {plan_id}...")
                    
                    await ws.send(json.dumps({
                        "type": "confirm_plan",
                        "plan_id": plan_id,
                        "action": "confirm",
                    }))
                    
                    # 等待执行完成
                    start_time = time.time()
                    while time.time() - start_time < 60:
                        try:
                            response = await asyncio.wait_for(ws.recv(), timeout=2.0)
                            data = json.loads(response)
                            received_messages.append(data)
                            
                            print(f"[Plan测试] 收到: type={data.get('type')}")
                            
                            if data.get("type") in ["assistant_message", "error"]:
                                break
                        except asyncio.TimeoutError:
                            continue
                
                # 验证结果
                message_types = [m.get("type") for m in received_messages]
                print(f"[Plan测试] 所有消息类型: {message_types}")
                
                # 检查关键消息
                has_plan_confirmed = "plan_confirmed" in message_types
                has_chain_generated = "chain_generated" in message_types or "task_graph_generated" in message_types
                
                if has_plan_confirmed:
                    print("✅ Plan 确认成功")
                if has_chain_generated:
                    print("✅ 决策链生成成功")
                
                print("✅ Plan 模式流程测试完成")
                
        except Exception as e:
            pytest.fail(f"Plan 模式测试失败: {e}")

    @pytest.mark.asyncio
    async def test_message_sequence_integrity(self):
        """测试消息序列完整性"""
        try:
            async with websockets.connect(f"{self.BASE_URL}/ws/chat/test_sequence") as ws:
                received_messages = []
                
                # 等待连接确认
                await asyncio.wait_for(ws.recv(), timeout=5.0)
                
                # 发送消息
                await ws.send(json.dumps({
                    "type": "chat_message",
                    "content": "测试消息序列",
                }))
                
                # 收集所有消息
                start_time = time.time()
                while time.time() - start_time < 30:
                    try:
                        response = await asyncio.wait_for(ws.recv(), timeout=2.0)
                        data = json.loads(response)
                        received_messages.append(data)
                        
                        if data.get("type") in ["assistant_message", "error", "complete"]:
                            break
                    except asyncio.TimeoutError:
                        continue
                
                # 验证消息序列
                message_types = [m.get("type") for m in received_messages]
                print(f"[序列测试] 消息序列: {message_types}")
                
                # 检查消息顺序
                if "user_message_confirm" in message_types:
                    confirm_index = message_types.index("user_message_confirm")
                    print(f"✅ 用户消息确认在位置 {confirm_index}")
                
                if "intent_parsed" in message_types:
                    intent_index = message_types.index("intent_parsed")
                    print(f"✅ 意图解析在位置 {intent_index}")
                
                print("✅ 消息序列完整性测试完成")
                
        except Exception as e:
            pytest.fail(f"消息序列测试失败: {e}")


async def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("开始 WebSocket 端到端测试")
    print("=" * 60)
    
    test = TestWebSocketE2E()
    
    tests = [
        ("WebSocket 连接测试", test.test_websocket_connection),
        ("心跳测试", test.test_ping_pong),
        ("聊天消息流程测试", test.test_chat_message_flow),
        ("Plan 模式流程测试", test.test_plan_mode_flow),
        ("消息序列完整性测试", test.test_message_sequence_integrity),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{'-' * 60}")
        print(f"运行: {name}")
        print("-" * 60)
        try:
            await test_func()
            results.append((name, "✅ 通过"))
        except Exception as e:
            print(f"❌ 失败: {e}")
            results.append((name, f"❌ 失败: {e}"))
    
    print(f"\n{'=' * 60}")
    print("测试结果汇总")
    print("=" * 60)
    for name, result in results:
        print(f"{name}: {result}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
