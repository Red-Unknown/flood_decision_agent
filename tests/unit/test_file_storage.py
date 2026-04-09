"""文件存储模块单元测试

测试 FileStorage 类的各个功能
"""

import pytest
import json
import os
import shutil
from pathlib import Path

from src.flood_decision_agent.infrastructure.persistence.file_storage import (
    FileStorage,
    get_file_storage,
)


@pytest.fixture
def temp_storage(tmp_path):
    """创建临时存储实例"""
    storage = FileStorage(base_path=str(tmp_path / "test_data"))
    yield storage
    # 清理
    if (tmp_path / "test_data").exists():
        shutil.rmtree(tmp_path / "test_data")


class TestFileStorage:
    """测试 FileStorage 类"""

    def test_init_creates_directories(self, temp_storage):
        """测试初始化创建目录"""
        assert (Path(temp_storage.base_path) / "documents").exists()
        assert (Path(temp_storage.base_path) / "conversations").exists()
        assert (Path(temp_storage.base_path) / "sessions").exists()

    def test_save_and_load_document(self, temp_storage):
        """测试保存和加载文档"""
        doc_id = "test_doc_001"
        content = "# 测试文档\n\n这是测试内容"
        metadata = {"author": "test", "version": 1}
        
        # 保存文档
        result = temp_storage.save_document(doc_id, content, metadata)
        assert result is True
        
        # 加载文档
        doc = temp_storage.load_document(doc_id)
        assert doc is not None
        assert doc["document_id"] == doc_id
        assert doc["content"] == content
        assert doc["metadata"]["author"] == "test"

    def test_load_nonexistent_document(self, temp_storage):
        """测试加载不存在的文档"""
        doc = temp_storage.load_document("nonexistent_doc")
        assert doc is None

    def test_delete_document(self, temp_storage):
        """测试删除文档"""
        doc_id = "test_doc_delete"
        temp_storage.save_document(doc_id, "内容", {})
        
        # 删除文档
        result = temp_storage.delete_document(doc_id)
        assert result is True
        
        # 确认已删除
        doc = temp_storage.load_document(doc_id)
        assert doc is None

    def test_save_and_load_conversation(self, temp_storage):
        """测试保存和加载对话"""
        conv_id = "test_conv_001"
        messages = [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好！"},
        ]
        metadata = {"title": "测试对话"}
        
        # 保存对话
        result = temp_storage.save_conversation(conv_id, messages, metadata)
        assert result is True
        
        # 加载对话
        conv = temp_storage.load_conversation(conv_id)
        assert conv is not None
        assert conv["conversation_id"] == conv_id
        assert len(conv["messages"]) == 2
        assert conv["metadata"]["title"] == "测试对话"

    def test_list_conversations(self, temp_storage):
        """测试列出所有对话"""
        # 创建多个对话
        for i in range(3):
            temp_storage.save_conversation(
                f"conv_{i}",
                [{"role": "user", "content": f"消息{i}"}],
                {"title": f"对话{i}"}
            )
        
        # 列出对话
        conversations = temp_storage.list_conversations()
        assert len(conversations) == 3

    def test_save_and_load_tasks(self, temp_storage):
        """测试保存和加载任务"""
        session_id = "test_session_001"
        tasks = [
            {"id": "task_1", "status": "completed"},
            {"id": "task_2", "status": "running"},
        ]
        events = [{"stage": "start", "timestamp": 1234567890}]
        context = {"user_input": "测试输入"}
        
        # 保存任务
        result = temp_storage.save_tasks(session_id, tasks, events, context)
        assert result is True
        
        # 加载任务
        task_data = temp_storage.load_tasks(session_id)
        assert task_data is not None
        assert task_data["session_id"] == session_id
        assert len(task_data["tasks"]) == 2
        assert len(task_data["events"]) == 1
        assert task_data["context"]["user_input"] == "测试输入"

    def test_update_task_status(self, temp_storage):
        """测试更新任务状态"""
        session_id = "test_session_update"
        tasks = [
            {"id": "task_1", "status": "pending"},
        ]
        temp_storage.save_tasks(session_id, tasks)
        
        # 更新状态
        result = temp_storage.update_task_status(
            session_id, "task_1", "completed", {"result": "成功"}
        )
        assert result is True
        
        # 验证更新
        task_data = temp_storage.load_tasks(session_id)
        assert task_data["tasks"][0]["status"] == "completed"
        assert task_data["tasks"][0]["result"]["result"] == "成功"

    def test_update_nonexistent_task(self, temp_storage):
        """测试更新不存在的任务"""
        result = temp_storage.update_task_status(
            "nonexistent_session", "task_1", "completed"
        )
        assert result is False


class TestGetFileStorage:
    """测试 get_file_storage 函数"""

    def test_singleton_pattern(self):
        """测试单例模式"""
        storage1 = get_file_storage()
        storage2 = get_file_storage()
        assert storage1 is storage2

    def test_default_base_path(self):
        """测试默认基础路径"""
        storage = get_file_storage()
        assert storage.base_path.name == "data"
