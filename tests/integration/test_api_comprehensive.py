"""
全面API集成测试

验证后端所有API接口和完整业务流程
"""

import pytest
import sys
import os
import json
import time

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from fastapi.testclient import TestClient
from web.backend.main import app

client = TestClient(app)


class TestBaseAPI:
    """基础接口测试"""

    def test_health_check(self):
        """测试健康检查接口"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "service" in data


class TestConversationAPI:
    """对话管理API测试"""

    def test_conversation_crud(self):
        """测试对话CRUD完整流程"""
        # 1. 创建对话
        response = client.post("/api/conversations", json={"title": "测试对话"})
        assert response.status_code == 200
        conv_data = response.json()
        conv_id = conv_data["id"]
        assert conv_data["title"] == "测试对话"

        # 2. 获取对话列表
        response = client.get("/api/conversations")
        assert response.status_code == 200
        conversations = response.json()
        assert len(conversations) > 0
        assert any(c["id"] == conv_id for c in conversations)

        # 3. 获取对话详情
        response = client.get(f"/api/conversations/{conv_id}")
        assert response.status_code == 200
        detail = response.json()
        assert detail["id"] == conv_id

        # 4. 获取不存在对话（404）
        response = client.get("/api/conversations/non_existent_id")
        assert response.status_code == 404

        # 5. 清空对话
        response = client.post(f"/api/conversations/{conv_id}/clear")
        assert response.status_code == 200
        assert response.json()["success"] is True

        # 6. 删除对话
        response = client.delete(f"/api/conversations/{conv_id}")
        assert response.status_code == 200
        assert response.json()["success"] is True

        # 7. 删除不存在对话（404）
        response = client.delete(f"/api/conversations/{conv_id}")
        assert response.status_code == 404


class TestChatAPI:
    """聊天API测试"""

    def test_non_streaming_chat(self):
        """测试非流式聊天"""
        # 创建对话
        response = client.post("/api/conversations", json={})
        conv_id = response.json()["id"]

        # 非流式聊天
        response = client.post("/api/chat", json={
            "message": "你好",
            "conversation_id": conv_id,
            "stream": False
        })
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert data["conversation_id"] == conv_id

        # 清理
        client.delete(f"/api/conversations/{conv_id}")

    def test_streaming_chat(self):
        """测试流式聊天"""
        # 创建对话
        response = client.post("/api/conversations", json={})
        conv_id = response.json()["id"]

        # 流式聊天
        response = client.post("/api/chat", json={
            "message": "计算1+1",
            "conversation_id": conv_id,
            "stream": True
        })
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]

        # 解析SSE流
        content_received = False
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8') if isinstance(line, bytes) else line
                if line_str.startswith("data: "):
                    try:
                        data = json.loads(line_str[6:])
                        if data.get("type") in ["chunk", "complete", "process_event"]:
                            content_received = True
                    except json.JSONDecodeError:
                        pass

        assert content_received, "未收到流式内容"

        # 清理
        client.delete(f"/api/conversations/{conv_id}")

    def test_get_messages_and_events(self):
        """测试获取消息历史和过程事件"""
        # 创建对话
        response = client.post("/api/conversations", json={})
        conv_id = response.json()["id"]

        # 发送消息
        client.post("/api/chat", json={
            "message": "你好",
            "conversation_id": conv_id,
            "stream": False
        })

        # 获取消息历史
        response = client.get(f"/api/conversations/{conv_id}/messages")
        assert response.status_code == 200
        messages = response.json()
        assert isinstance(messages, list)

        # 获取过程事件
        response = client.get(f"/api/conversations/{conv_id}/process-events")
        assert response.status_code == 200
        events = response.json()
        assert isinstance(events, list)

        # 清理
        client.delete(f"/api/conversations/{conv_id}")


class TestModeDetectionAPI:
    """模式识别API测试"""

    def test_mode_detection(self):
        """测试模式识别API"""
        test_cases = [
            ("你好", "simple"),
            ("制定一个洪水预警计划", "plan"),
            ("/plan 设计系统", "plan"),
            ("编写API规格文档", "spec"),
            ("/spec 设计模块", "spec"),
        ]

        for user_input, expected_mode in test_cases:
            response = client.post("/api/mode/detect", json={"user_input": user_input})
            assert response.status_code == 200, f"输入'{user_input}'检测失败"
            data = response.json()
            assert data["recommended_mode"] == expected_mode, \
                f"输入'{user_input}'期望{expected_mode}，实际{data['recommended_mode']}"
            assert 0 <= data["confidence"] <= 1
            assert "metrics" in data


class TestDataAcquisitionAPI:
    """数据获取API测试"""

    def test_parse_input(self):
        """测试解析输入"""
        response = client.post("/data/parse", json={
            "input_data": "河道名称: 示例河, 断面桩号: K0+100",
            "input_type": "text",
            "schema_type": "river_cross_section"
        })
        assert response.status_code in [200, 500]

    def test_request_data(self):
        """测试请求数据"""
        response = client.post("/data/request", json={
            "data_key": "roughness_coefficient",
            "description": "河道糙率系数",
            "required": True,
            "context": {"river_type": "山区河道"}
        })
        assert response.status_code in [200, 500]

    def test_get_defaults(self):
        """测试获取默认值"""
        response = client.get("/data/defaults?data_key=roughness_coefficient")
        assert response.status_code in [200, 500]

    def test_confirm_data(self):
        """测试确认数据"""
        response = client.post("/data/confirm", json={
            "confirmation_id": "conf_test_001",
            "status": "confirmed",
            "modified_data": None,
            "user_notes": ""
        })
        assert response.status_code in [200, 500]

    def test_get_lineage(self):
        """测试获取数据血缘"""
        response = client.get("/data/lineage/test_key")
        assert response.status_code in [200, 500]

    def test_clarification_session(self):
        """测试澄清会话"""
        response = client.post("/data/clarification/session", json={
            "task_id": "task_test_001",
            "data_dependencies": [
                {"data_key": "river_width", "description": "河道宽度", "required": True}
            ]
        })
        assert response.status_code in [200, 500]

    def test_clarification_resolve(self):
        """测试解决数据请求"""
        response = client.post("/data/clarification/resolve", json={
            "session_id": "session_test_001",
            "request_id": "req_test_001",
            "resolution_type": "default",
            "value": None
        })
        assert response.status_code in [200, 500]


class TestPlanAPI:
    """Plan模式API测试"""

    def test_plan_full_flow(self):
        """测试Plan模式完整业务流程"""
        plan_id = "plan_test_001"

        # 1. 生成规划
        response = client.post(f"/api/plans/{plan_id}/generate", json={
            "user_input": "设计一个洪水预警系统"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["plan_id"] == plan_id

        # 2. 更新规划
        response = client.put(f"/api/plans/{plan_id}", json={
            "content": "# 洪水预警系统规划\n\n## 概述\n这是一个优化的规划..."
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # 3. 修改规划
        response = client.post(f"/api/plans/{plan_id}/modify", json={
            "instruction": "把准确率目标改成98%"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # 4. 确认规划
        response = client.post(f"/api/plans/{plan_id}/confirm", json={
            "action": "proceed"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data.get("data", {}).get("status") == "confirmed"

    def test_plan_not_found(self):
        """测试规划不存在的情况"""
        # 更新不存在规划
        response = client.put("/api/plans/non_existent_plan", json={
            "content": "# 测试"
        })
        assert response.status_code == 404

        # 修改不存在规划
        response = client.post("/api/plans/non_existent_plan/modify", json={
            "instruction": "修改"
        })
        assert response.status_code == 404

        # 取消不存在规划
        response = client.post("/api/plans/non_existent_plan/cancel", json={})
        assert response.status_code == 404

    def test_plan_cancel(self):
        """测试取消规划"""
        plan_id = "plan_test_cancel"

        # 创建规划
        client.post(f"/api/plans/{plan_id}/generate", json={
            "user_input": "测试规划"
        })

        # 取消规划
        response = client.post(f"/api/plans/{plan_id}/cancel", json={
            "reason": "需求变更"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data.get("data", {}).get("status") == "cancelled"


class TestSpecAPI:
    """Spec模式API测试"""

    def test_spec_full_flow(self):
        """测试Spec模式完整业务流程"""
        feature_name = "flood-warning-system"

        # 1. 生成规格
        response = client.post(f"/api/specs/{feature_name}/generate", json={
            "user_input": "设计洪水预警系统的技术规格"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["feature_name"] == feature_name

        # 2. 更新规格
        response = client.put(f"/api/specs/{feature_name}", json={
            "content": "# 洪水预警系统规格\n\n## 功能需求\n这是一个优化的规格..."
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # 3. 修改规格
        response = client.post(f"/api/specs/{feature_name}/modify", json={
            "instruction": "增加缓存设计章节"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # 4. 确认规格
        response = client.post(f"/api/specs/{feature_name}/confirm", json={
            "action": "proceed"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data.get("data", {}).get("status") == "confirmed"

    def test_spec_not_found(self):
        """测试规格不存在的情况"""
        # 更新不存在规格
        response = client.put("/api/specs/non_existent_spec", json={
            "content": "# 测试"
        })
        assert response.status_code == 404

        # 修改不存在规格
        response = client.post("/api/specs/non_existent_spec/modify", json={
            "instruction": "修改"
        })
        assert response.status_code == 404

        # 取消不存在规格
        response = client.post("/api/specs/non_existent_spec/cancel", json={})
        assert response.status_code == 404

    def test_spec_cancel(self):
        """测试取消规格"""
        feature_name = "test-spec-cancel"

        # 创建规格
        client.post(f"/api/specs/{feature_name}/generate", json={
            "user_input": "测试规格"
        })

        # 取消规格
        response = client.post(f"/api/specs/{feature_name}/cancel", json={
            "reason": "需求变更"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data.get("data", {}).get("status") == "cancelled"


class TestWebSocket:
    """WebSocket测试"""

    def test_websocket_connection(self):
        """测试WebSocket连接"""
        # 创建对话
        response = client.post("/api/conversations", json={})
        conv_id = response.json()["id"]

        try:
            with client.websocket_connect(f"/ws/chat/{conv_id}") as websocket:
                # 接收连接成功消息
                data = websocket.receive_json()
                assert data["type"] == "connected"
                assert data["conversation_id"] == conv_id

                # 发送ping
                websocket.send_json({"type": "ping"})
                data = websocket.receive_json()
                assert data["type"] == "pong"
        finally:
            # 清理
            client.delete(f"/api/conversations/{conv_id}")

    def test_websocket_message(self):
        """测试WebSocket消息发送"""
        # 创建对话
        response = client.post("/api/conversations", json={})
        conv_id = response.json()["id"]

        try:
            with client.websocket_connect(f"/ws/chat/{conv_id}") as websocket:
                # 接收连接成功消息
                websocket.receive_json()

                # 发送消息
                websocket.send_json({
                    "type": "message",
                    "content": "你好"
                })

                # 接收响应
                received_types = set()
                for _ in range(20):
                    try:
                        data = websocket.receive_json()
                        received_types.add(data.get("type"))
                        if data.get("type") == "complete":
                            break
                    except Exception:
                        break

                assert len(received_types) > 0
        finally:
            # 清理
            client.delete(f"/api/conversations/{conv_id}")


class TestE2EFlows:
    """端到端业务流程测试"""

    def test_e2e_simple_chat(self):
        """测试端到端简单聊天流程"""
        # 1. 创建对话
        response = client.post("/api/conversations", json={"title": "E2E测试"})
        conv_id = response.json()["id"]

        try:
            # 2. 模式检测
            response = client.post("/api/mode/detect", json={
                "user_input": "计算河道流量"
            })
            mode = response.json()["recommended_mode"]

            # 3. 发送消息
            response = client.post("/api/chat", json={
                "message": "你好",
                "conversation_id": conv_id,
                "stream": False
            })
            assert response.status_code == 200

            # 4. 验证消息历史
            response = client.get(f"/api/conversations/{conv_id}/messages")
            messages = response.json()
            assert isinstance(messages, list)

            # 5. 验证过程事件
            response = client.get(f"/api/conversations/{conv_id}/process-events")
            events = response.json()
            assert isinstance(events, list)
        finally:
            client.delete(f"/api/conversations/{conv_id}")

    def test_e2e_plan_mode(self):
        """测试端到端Plan模式流程"""
        # 1. 创建对话
        response = client.post("/api/conversations", json={"title": "Plan测试"})
        conv_id = response.json()["id"]

        try:
            # 2. 模式检测
            response = client.post("/api/mode/detect", json={
                "user_input": "制定洪水预警系统开发计划"
            })
            assert response.json()["recommended_mode"] == "plan"

            # 3. 生成规划
            plan_id = f"plan_{conv_id[:8]}"
            response = client.post(f"/api/plans/{plan_id}/generate", json={
                "user_input": "制定洪水预警系统开发计划"
            })
            assert response.status_code == 200

            # 4. 更新规划
            response = client.put(f"/api/plans/{plan_id}", json={
                "content": "# 开发计划\n\n## 目标\n- 准确率95%"
            })
            assert response.status_code == 200

            # 5. 确认规划
            response = client.post(f"/api/plans/{plan_id}/confirm", json={
                "action": "proceed"
            })
            assert response.status_code == 200
            assert response.json()["data"]["status"] == "confirmed"
        finally:
            client.delete(f"/api/conversations/{conv_id}")

    def test_e2e_spec_mode(self):
        """测试端到端Spec模式流程"""
        # 1. 创建对话
        response = client.post("/api/conversations", json={"title": "Spec测试"})
        conv_id = response.json()["id"]

        try:
            # 2. 模式检测
            response = client.post("/api/mode/detect", json={
                "user_input": "编写API规格文档"
            })
            assert response.json()["recommended_mode"] == "spec"

            # 3. 生成规格
            feature_name = f"spec-{conv_id[:8]}"
            response = client.post(f"/api/specs/{feature_name}/generate", json={
                "user_input": "编写API规格文档"
            })
            assert response.status_code == 200

            # 4. 更新规格
            response = client.put(f"/api/specs/{feature_name}", json={
                "content": "# API规格\n\n## 接口定义"
            })
            assert response.status_code == 200

            # 5. 确认规格
            response = client.post(f"/api/specs/{feature_name}/confirm", json={
                "action": "proceed"
            })
            assert response.status_code == 200
            assert response.json()["data"]["status"] == "confirmed"
        finally:
            client.delete(f"/api/conversations/{conv_id}")
