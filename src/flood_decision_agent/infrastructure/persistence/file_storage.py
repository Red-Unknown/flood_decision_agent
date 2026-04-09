"""
文件存储模块

提供基于文件系统的数据持久化功能
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime


class FileStorage:
    """文件存储类"""
    
    def __init__(self, base_path: str = "data"):
        """
        初始化文件存储
        
        Args:
            base_path: 数据存储根目录
        """
        self.base_path = Path(base_path)
        self.ensure_directories()
    
    def ensure_directories(self):
        """确保目录结构存在"""
        directories = [
            self.base_path / "documents",
            self.base_path / "conversations",
            self.base_path / "sessions",
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    # ==================== 文档存储 ====================
    
    def save_document(self, document_id: str, content: str, 
                      metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        保存文档
        
        Args:
            document_id: 文档ID
            content: 文档内容（Markdown格式）
            metadata: 文档元数据
            
        Returns:
            是否保存成功
        """
        try:
            doc_dir = self.base_path / "documents" / document_id
            doc_dir.mkdir(parents=True, exist_ok=True)
            
            # 保存内容
            content_path = doc_dir / "content.md"
            with open(content_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            # 保存元数据
            meta = metadata or {}
            meta.update({
                "document_id": document_id,
                "updated_at": datetime.now().isoformat(),
            })
            
            metadata_path = doc_dir / "metadata.json"
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"保存文档失败: {e}")
            return False
    
    def load_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        加载文档
        
        Args:
            document_id: 文档ID
            
        Returns:
            文档数据，包含 content 和 metadata
        """
        try:
            doc_dir = self.base_path / "documents" / document_id
            
            content_path = doc_dir / "content.md"
            metadata_path = doc_dir / "metadata.json"
            
            if not content_path.exists():
                return None
            
            # 读取内容
            with open(content_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 读取元数据
            metadata = {}
            if metadata_path.exists():
                with open(metadata_path, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
            
            return {
                "document_id": document_id,
                "content": content,
                "metadata": metadata,
            }
        except Exception as e:
            print(f"加载文档失败: {e}")
            return None
    
    def delete_document(self, document_id: str) -> bool:
        """
        删除文档
        
        Args:
            document_id: 文档ID
            
        Returns:
            是否删除成功
        """
        try:
            import shutil
            doc_dir = self.base_path / "documents" / document_id
            if doc_dir.exists():
                shutil.rmtree(doc_dir)
            return True
        except Exception as e:
            print(f"删除文档失败: {e}")
            return False
    
    def list_documents(self, document_type: Optional[str] = None,
                       status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        列出所有文档
        
        Args:
            document_type: 文档类型过滤（如 'plan', 'spec'）
            status: 状态过滤
            
        Returns:
            文档列表
        """
        documents = []
        try:
            docs_dir = self.base_path / "documents"
            if not docs_dir.exists():
                return documents
            
            for doc_id_dir in docs_dir.iterdir():
                if doc_id_dir.is_dir():
                    doc_id = doc_id_dir.name
                    doc_data = self.load_document(doc_id)
                    if doc_data:
                        metadata = doc_data.get("metadata", {})
                        
                        # 类型过滤
                        if document_type:
                            # 检查plan_id或feature_name前缀
                            if document_type == "plan" and not doc_id.startswith("plan_"):
                                continue
                            if document_type == "spec" and doc_id.startswith("plan_"):
                                continue
                        
                        # 状态过滤
                        if status and metadata.get("status") != status:
                            continue
                        
                        documents.append({
                            "document_id": doc_id,
                            "metadata": metadata,
                            "created_at": metadata.get("created_at"),
                            "updated_at": metadata.get("updated_at"),
                        })
            
            # 按更新时间倒序排列
            documents.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
            return documents
        except Exception as e:
            print(f"列出文档失败: {e}")
            return []
    
    # ==================== 对话存储 ====================
    
    def save_conversation(self, conversation_id: str, 
                          messages: List[Dict[str, Any]],
                          metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        保存对话
        
        Args:
            conversation_id: 对话ID
            messages: 消息列表
            metadata: 对话元数据
            
        Returns:
            是否保存成功
        """
        try:
            conv_dir = self.base_path / "conversations" / conversation_id
            conv_dir.mkdir(parents=True, exist_ok=True)
            
            # 保存消息
            messages_path = conv_dir / "messages.json"
            with open(messages_path, "w", encoding="utf-8") as f:
                json.dump(messages, f, ensure_ascii=False, indent=2)
            
            # 保存元数据
            meta = metadata or {}
            meta.update({
                "conversation_id": conversation_id,
                "updated_at": datetime.now().isoformat(),
                "message_count": len(messages),
            })
            
            metadata_path = conv_dir / "metadata.json"
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"保存对话失败: {e}")
            return False
    
    def load_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        加载对话
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            对话数据，包含 messages 和 metadata
        """
        try:
            conv_dir = self.base_path / "conversations" / conversation_id
            
            messages_path = conv_dir / "messages.json"
            metadata_path = conv_dir / "metadata.json"
            
            # 读取消息
            messages = []
            if messages_path.exists():
                with open(messages_path, "r", encoding="utf-8") as f:
                    messages = json.load(f)
            
            # 读取元数据
            metadata = {}
            if metadata_path.exists():
                with open(metadata_path, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
            
            return {
                "conversation_id": conversation_id,
                "messages": messages,
                "metadata": metadata,
            }
        except Exception as e:
            print(f"加载对话失败: {e}")
            return None
    
    def list_conversations(self) -> List[Dict[str, Any]]:
        """
        列出所有对话
        
        Returns:
            对话列表
        """
        conversations = []
        try:
            conv_dir = self.base_path / "conversations"
            if not conv_dir.exists():
                return conversations
            
            for conv_id_dir in conv_dir.iterdir():
                if conv_id_dir.is_dir():
                    conv_id = conv_id_dir.name
                    conv_data = self.load_conversation(conv_id)
                    if conv_data:
                        conversations.append({
                            "id": conv_id,
                            "title": conv_data["metadata"].get("title", f"对话 {conv_id}"),
                            "created_at": conv_data["metadata"].get("created_at"),
                            "updated_at": conv_data["metadata"].get("updated_at"),
                            "message_count": len(conv_data["messages"]),
                        })
            
            # 按更新时间倒序排列
            conversations.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
            return conversations
        except Exception as e:
            print(f"列出对话失败: {e}")
            return []
    
    # ==================== 任务状态存储 ====================
    
    def save_tasks(self, session_id: str, 
                   tasks: List[Dict[str, Any]],
                   events: Optional[List[Dict[str, Any]]] = None,
                   context: Optional[Dict[str, Any]] = None) -> bool:
        """
        保存任务状态
        
        Args:
            session_id: 会话ID
            tasks: 任务列表
            events: 事件列表
            context: 执行上下文
            
        Returns:
            是否保存成功
        """
        try:
            session_dir = self.base_path / "sessions" / session_id
            session_dir.mkdir(parents=True, exist_ok=True)
            
            # 保存任务
            tasks_path = session_dir / "tasks.json"
            with open(tasks_path, "w", encoding="utf-8") as f:
                json.dump(tasks, f, ensure_ascii=False, indent=2)
            
            # 保存事件
            if events is not None:
                events_path = session_dir / "events.json"
                with open(events_path, "w", encoding="utf-8") as f:
                    json.dump(events, f, ensure_ascii=False, indent=2)
            
            # 保存上下文
            if context is not None:
                context_path = session_dir / "context.json"
                with open(context_path, "w", encoding="utf-8") as f:
                    json.dump(context, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"保存任务状态失败: {e}")
            return False
    
    def load_tasks(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        加载任务状态
        
        Args:
            session_id: 会话ID
            
        Returns:
            任务数据，包含 tasks、events 和 context
        """
        try:
            session_dir = self.base_path / "sessions" / session_id
            
            tasks_path = session_dir / "tasks.json"
            events_path = session_dir / "events.json"
            context_path = session_dir / "context.json"
            
            result = {"session_id": session_id}
            
            # 读取任务
            if tasks_path.exists():
                with open(tasks_path, "r", encoding="utf-8") as f:
                    result["tasks"] = json.load(f)
            else:
                result["tasks"] = []
            
            # 读取事件
            if events_path.exists():
                with open(events_path, "r", encoding="utf-8") as f:
                    result["events"] = json.load(f)
            else:
                result["events"] = []
            
            # 读取上下文
            if context_path.exists():
                with open(context_path, "r", encoding="utf-8") as f:
                    result["context"] = json.load(f)
            else:
                result["context"] = {}
            
            return result
        except Exception as e:
            print(f"加载任务状态失败: {e}")
            return None
    
    def update_task_status(self, session_id: str, task_id: str, 
                           status: str, result: Optional[Dict] = None) -> bool:
        """
        更新单个任务状态
        
        Args:
            session_id: 会话ID
            task_id: 任务ID
            status: 新状态
            result: 任务结果
            
        Returns:
            是否更新成功
        """
        try:
            task_data = self.load_tasks(session_id)
            if not task_data:
                return False
            
            tasks = task_data.get("tasks", [])
            for task in tasks:
                if task.get("id") == task_id:
                    task["status"] = status
                    if result is not None:
                        task["result"] = result
                    task["updated_at"] = datetime.now().isoformat()
                    break
            
            return self.save_tasks(
                session_id, 
                tasks, 
                task_data.get("events"),
                task_data.get("context")
            )
        except Exception as e:
            print(f"更新任务状态失败: {e}")
            return False


# 全局文件存储实例
_file_storage: Optional[FileStorage] = None


def get_file_storage() -> FileStorage:
    """获取全局文件存储实例"""
    global _file_storage
    if _file_storage is None:
        _file_storage = FileStorage()
    return _file_storage
