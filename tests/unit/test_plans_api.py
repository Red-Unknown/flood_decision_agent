"""Plan API 单元测试

测试 Plan 模式 API 的各个端点
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from web.backend.main import app


@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


@pytest.fixture
def mock_file_storage():
    """模拟文件存储"""
    with patch("web.backend.api.plans.get_file_storage") as mock:
        storage = MagicMock()
        mock.return_value = storage
        yield storage


class TestPlanAPI:
    """测试 Plan API"""

    def test_update_plan_success(self, client, mock_file_storage):
        """测试成功更新规划文档"""
        # 模拟文档存在
        mock_file_storage.load_document.return_value = {
            "document_id": "plan_001",
            "content": "旧内容",
            "metadata": {"created_at": "2024-01-01"},
        }
        mock_file_storage.save_document.return_value = True
        
        response = client.put(
            "/api/plans/plan_001",
            json={"content": "# 新规划内容"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["plan_id"] == "plan_001"
        assert "已更新" in data["message"]

    def test_update_plan_not_found(self, client, mock_file_storage):
        """测试更新不存在的规划文档"""
        mock_file_storage.load_document.return_value = None
        
        response = client.put(
            "/api/plans/nonexistent",
            json={"content": "# 内容"},
        )
        
        assert response.status_code == 404
        assert "不存在" in response.json()["detail"]

    def test_generate_plan_success(self, client, mock_file_storage):
        """测试成功创建规划生成任务"""
        mock_file_storage.load_document.return_value = None
        mock_file_storage.save_document.return_value = True
        
        response = client.post(
            "/api/plans/plan_001/generate",
            json={"user_input": "设计洪水预警系统"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "generation_id" in data["data"]
        assert data["data"]["status"] == "generating"

    def test_modify_plan_success(self, client, mock_file_storage):
        """测试成功创建规划修改任务"""
        mock_file_storage.load_document.return_value = {
            "document_id": "plan_001",
            "content": "旧内容",
            "metadata": {},
        }
        mock_file_storage.save_document.return_value = True
        
        response = client.post(
            "/api/plans/plan_001/modify",
            json={"instruction": "添加更多细节"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "modification_id" in data["data"]
        assert data["data"]["instruction"] == "添加更多细节"

    def test_modify_plan_not_found(self, client, mock_file_storage):
        """测试修改不存在的规划文档"""
        mock_file_storage.load_document.return_value = None
        
        response = client.post(
            "/api/plans/nonexistent/modify",
            json={"instruction": "修改"},
        )
        
        assert response.status_code == 404

    def test_confirm_plan_success(self, client, mock_file_storage):
        """测试成功确认规划文档"""
        mock_file_storage.load_document.return_value = {
            "document_id": "plan_001",
            "content": "规划内容",
            "metadata": {},
        }
        mock_file_storage.save_document.return_value = True
        
        response = client.post(
            "/api/plans/plan_001/confirm",
            json={"action": "proceed"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "confirmed"
        assert data["data"]["next_stage"] == "executing"

    def test_cancel_plan_success(self, client, mock_file_storage):
        """测试成功取消规划任务"""
        mock_file_storage.load_document.return_value = {
            "document_id": "plan_001",
            "content": "规划内容",
            "metadata": {},
        }
        mock_file_storage.save_document.return_value = True
        
        response = client.post(
            "/api/plans/plan_001/cancel",
            json={"reason": "用户取消"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "cancelled"
