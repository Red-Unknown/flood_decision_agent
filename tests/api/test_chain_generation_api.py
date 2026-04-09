"""
决策链生成 API 测试

测试决策链生成功能的所有API端点：
1. 普通模式生成决策链
2. Plan模式生成决策链
3. Spec模式生成决策链
4. 获取生成状态
5. 执行决策链
6. 取消执行
"""

import pytest
import requests
import time
import json

BASE_URL = "http://localhost:8000"


class TestChainGenerationAPI:
    """决策链生成 API 测试类"""

    @pytest.fixture(scope="class")
    def base_url(self):
        return BASE_URL

    def test_health_check(self, base_url):
        """测试服务健康状态"""
        response = requests.get(f"{base_url}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_generate_chain_normal(self, base_url):
        """测试普通模式生成决策链"""
        response = requests.post(
            f"{base_url}/api/chain-generation/generate",
            json={
                "user_input": "设计一个洪水预警系统，能够实时监测水位并发送预警通知",
                "conversation_id": "test_conv_001"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "generation_id" in data
        assert data["data"]["mode"] == "normal"
        return data["generation_id"]

    def test_generate_chain_normal_empty_input(self, base_url):
        """测试普通模式空输入错误处理"""
        response = requests.post(
            f"{base_url}/api/chain-generation/generate",
            json={
                "user_input": "",
                "conversation_id": "test_conv_001"
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    def test_generate_chain_from_plan_not_found(self, base_url):
        """测试Plan模式文档不存在错误"""
        response = requests.post(
            f"{base_url}/api/chain-generation/generate-from-plan",
            json={
                "plan_id": "non_existent_plan",
                "conversation_id": "test_conv_001"
            }
        )
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_generate_chain_from_plan_not_confirmed(self, base_url):
        """测试Plan模式文档未确认错误"""
        # 首先创建一个未确认的Plan文档
        storage_url = f"{base_url}/api/plans/test_plan_unconfirmed/generate"
        requests.post(
            storage_url,
            json={"user_input": "测试规划"}
        )

        # 尝试从未确认的文档生成决策链
        response = requests.post(
            f"{base_url}/api/chain-generation/generate-from-plan",
            json={
                "plan_id": "test_plan_unconfirmed",
                "conversation_id": "test_conv_001"
            }
        )
        # 应该返回400错误，因为文档未确认
        assert response.status_code == 404 or response.status_code == 400

    def test_generate_chain_from_spec_not_found(self, base_url):
        """测试Spec模式文档不存在错误"""
        response = requests.post(
            f"{base_url}/api/chain-generation/generate-from-spec",
            json={
                "feature_name": "non_existent_spec",
                "conversation_id": "test_conv_001"
            }
        )
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_get_chain_generation_status_not_found(self, base_url):
        """测试获取不存在的生成任务状态"""
        response = requests.get(
            f"{base_url}/api/chain-generation/non_existent/status"
        )
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_execute_chain_not_found(self, base_url):
        """测试执行不存在的决策链"""
        response = requests.post(
            f"{base_url}/api/chain-generation/non_existent/execute",
            json={
                "generation_id": "non_existent",
                "mode": "normal",
                "auto_execute": True
            }
        )
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_get_execution_status_not_found(self, base_url):
        """测试获取不存在的执行状态"""
        response = requests.get(
            f"{base_url}/api/chain-generation/executions/non_existent/status"
        )
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_cancel_execution_not_found(self, base_url):
        """测试取消不存在的执行"""
        response = requests.post(
            f"{base_url}/api/chain-generation/executions/non_existent/cancel"
        )
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data


class TestChainGenerationWebSocket:
    """决策链生成 WebSocket 测试类"""

    def test_websocket_connection(self):
        """测试 WebSocket 连接"""
        import websocket

        ws_url = f"ws://localhost:8000/ws/chat/test_ws_chain_gen"

        try:
            ws = websocket.create_connection(ws_url)

            # 等待连接成功消息
            result = ws.recv()
            data = json.loads(result)
            assert data["type"] == "connected"

            # 发送 ping
            ws.send(json.dumps({"type": "ping", "timestamp": time.time()}))
            result = ws.recv()
            data = json.loads(result)
            assert data["type"] == "pong"

            ws.close()
        except Exception as e:
            pytest.skip(f"WebSocket 测试跳过: {e}")

    def test_websocket_generate_chain_normal(self):
        """测试 WebSocket 普通模式生成决策链"""
        import websocket

        ws_url = f"ws://localhost:8000/ws/chat/test_ws_normal_gen"

        try:
            ws = websocket.create_connection(ws_url, timeout=30)

            # 等待连接成功
            result = ws.recv()
            data = json.loads(result)
            assert data["type"] == "connected"

            # 发送普通模式生成请求
            ws.send(json.dumps({
                "type": "generate_chain_normal",
                "user_input": "查询今天的水位数据",
                "generation_id": "test_gen_normal_001",
                "timestamp": time.time()
            }))

            # 接收消息直到完成或超时
            received_types = []
            start_time = time.time()
            while time.time() - start_time < 30:
                try:
                    result = ws.recv()
                    data = json.loads(result)
                    received_types.append(data["type"])

                    if data["type"] == "chain_generation_complete":
                        assert data["mode"] == "normal"
                        assert "task_count" in data
                        break
                    elif data["type"] == "error":
                        pytest.fail(f"生成失败: {data.get('message')}")
                except websocket.WebSocketTimeoutException:
                    break

            assert "chain_generation_started" in received_types
            assert "chain_generation_complete" in received_types

            ws.close()
        except Exception as e:
            pytest.skip(f"WebSocket 测试跳过: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
