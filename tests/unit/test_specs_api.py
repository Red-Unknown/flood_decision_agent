"""Spec API 单元测试

测试 Spec 模式 API 的各个端点
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
    with patch("web.backend.api.specs.get_file_storage") as mock:
        storage = MagicMock()
        mock.return_value = storage
        yield storage


class TestSpecAPI:
    """测试 Spec API"""

    def test_update_spec_success(self, client, mock_file_storage):
        """测试成功更新规格文档"""
        mock_file_storage.load_document.return_value = {
            "document_id": "feature_001",
            "content": "旧内容",
            "metadata": {"created_at": "2024-01-01"},
        }
        mock_file_storage.save_document.return_value = True
        
        response = client.put(
            "/api/specs/feature_001",
            json={"content": "# 新规格内容"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["feature_name"] == "feature_001"
        assert "已更新" in data["message"]

    def test_update_spec_not_found(self, client, mock_file_storage):
        """测试更新不存在的规格文档"""
        mock_file_storage.load_document.return_value = None
        
        response = client.put(
            "/api/specs/nonexistent",
            json={"content": "# 内容"},
        )
        
        assert response.status_code == 404
        assert "不存在" in response.json()["detail"]

    def test_generate_spec_success(self, client, mock_file_storage):
        """测试成功创建规格生成任务"""
        mock_file_storage.load_document.return_value = None
        mock_file_storage.save_document.return_value = True
        
        response = client.post(
            "/api/specs/feature_001/generate",
            json={"user_input": "实现洪水预警模块"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "generation_id" in data["data"]
        assert data["data"]["status"] == "generating"

    def test_modify_spec_success(self, client, mock_file_storage):
        """测试成功创建规格修改任务"""
        mock_file_storage.load_document.return_value = {
            "document_id": "feature_001",
            "content": "旧内容",
            "metadata": {},
        }
        mock_file_storage.save_document.return_value = True
        
        response = client.post(
            "/api/specs/feature_001/modify",
            json={"instruction": "优化性能要求"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "modification_id" in data["data"]
        assert data["data"]["instruction"] == "优化性能要求"

    def test_modify_spec_not_found(self, client, mock_file_storage):
        """测试修改不存在的规格文档"""
        mock_file_storage.load_document.return_value = None
        
        response = client.post(
            "/api/specs/nonexistent/modify",
            json={"instruction": "修改"},
        )
        
        assert response.status_code == 404

    def test_confirm_spec_success(self, client, mock_file_storage):
        """测试成功确认规格文档"""
        mock_file_storage.load_document.return_value = {
            "document_id": "feature_001",
            "content": "规格内容",
            "metadata": {},
        }
        mock_file_storage.save_document.return_value = True
        
        response = client.post(
            "/api/specs/feature_001/confirm",
            json={"action": "proceed"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "confirmed"
        assert data["data"]["next_stage"] == "executing"

    def test_cancel_spec_success(self, client, mock_file_storage):
        """测试成功取消规格任务"""
        mock_file_storage.load_document.return_value = {
            "document_id": "feature_001",
            "content": "规格内容",
            "metadata": {},
        }
        mock_file_storage.save_document.return_value = True
        
        response = client.post(
            "/api/specs/feature_001/cancel",
            json={"reason": "需求变更"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "cancelled"
