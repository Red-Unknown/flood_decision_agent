"""对话聊天API.

提供流式对话功能，集成现有Pipeline执行逻辑。
将Pipeline结果转换为友好的流式文本输出，包含完整的过程性输出。
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from typing import AsyncGenerator, Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

from flood_decision_agent.app.visualized_pipeline import VisualizedPipeline

router = APIRouter()


class ChatRequest(BaseModel):
    """聊天请求."""

    message: str = Field(..., description="用户消息")
    conversation_id: Optional[str] = Field(default=None, description="对话ID")
    stream: bool = Field(default=True, description="是否流式返回")


class ChatMessage(BaseModel):
    """聊天消息."""

    role: str = Field(..., description="消息角色：user/assistant")
    content: str = Field(..., description="消息内容")
    timestamp: float = Field(..., description="时间戳")


class ProcessStage(str, Enum):
    """处理阶段."""
    TASK_ACCEPTED = "task_accepted"           # 任务接取
    TASK_LIST_GENERATED = "task_list_generated"  # 任务列表生成
    NODE_STARTED = "node_started"             # 节点开始
    NODE_COMPLETED = "node_completed"         # 节点完成
    NODE_FAILED = "node_failed"               # 节点失败
    AGENT_CALLED = "agent_called"             # Agent调用
    PIPELINE_COMPLETED = "pipeline_completed" # 流程完成


@dataclass
class ProcessEvent:
    """过程性事件."""
    stage: ProcessStage
    timestamp: float
    data: Dict[str, Any] = field(default_factory=dict)


# 内存存储
_messages: Dict[str, List[ChatMessage]] = {}
_process_events: Dict[str, List[ProcessEvent]] = {}  # 过程性事件存储


class WebEventCollector:
    """Web端事件收集器 - 收集过程性事件供前端展示.
    
    不继承BaseVisualizer，独立实现，避免抽象方法约束。
    """

    def __init__(self, conversation_id: str, stream_callback: Optional[Callable] = None):
        self.conversation_id = conversation_id
        self.stream_callback = stream_callback
        self.events: List[ProcessEvent] = []
        self.task_infos: List[Dict] = []
        self.agent_calls: List[Dict] = []
        self.execution_summary = None
        self._task_info_map: Dict[str, Dict] = {}
        self._is_running = False

    def _add_event(self, stage: ProcessStage, data: Dict[str, Any]):
        """添加事件并发送到前端."""
        event = ProcessEvent(
            stage=stage,
            timestamp=time.time(),
            data=data
        )
        self.events.append(event)

        # 存储到全局
        if self.conversation_id not in _process_events:
            _process_events[self.conversation_id] = []
        _process_events[self.conversation_id].append(event)

        # 通过回调发送到前端
        if self.stream_callback:
            self.stream_callback({
                "type": "process_event",
                "stage": stage.value,
                "data": data,
                "timestamp": event.timestamp
            })

    def on_pipeline_start(self, context: Optional[Dict] = None):
        """流程开始."""
        self._is_running = True
        self._task_info_map.clear()
        self.events = []
        
        self._add_event(ProcessStage.TASK_ACCEPTED, {
            "message": "📋 任务分析",
            "user_input": context.get("user_input", "") if context else "",
            "task_type": context.get("task_type", "") if context else ""
        })

    def on_task_graph_created(self, task_graph):
        """任务图创建完成."""
        # 提取任务信息
        nodes = task_graph.get_all_nodes()
        tasks = []
        for node_id, node in nodes.items():
            # 处理 task_type
            task_type_value = node.task_type
            if hasattr(task_type_value, 'value'):
                task_type_value = task_type_value.value

            # 生成可读的任务名称
            task_name = self._generate_task_name(node_id, task_type_value)

            task_info = {
                "task_id": node_id,
                "task_name": task_name,
                "task_type": task_type_value,
                "dependencies": list(node.dependencies) if hasattr(node, 'dependencies') else [],
                "status": node.status.value if hasattr(node.status, 'value') else str(node.status)
            }
            tasks.append(task_info)
            self._task_info_map[node_id] = task_info

        self._add_event(ProcessStage.TASK_LIST_GENERATED, {
            "message": "📋 决策链任务列表",
            "tasks": tasks,
            "total_count": len(tasks)
        })

    def _generate_task_name(self, node_id: str, task_type: str) -> str:
        """生成可读的任务名称."""
        try:
            from flood_decision_agent.core.task_types import (
                BusinessTaskType,
                ExecutionTaskType,
                get_business_type_description,
                get_execution_type_description,
            )

            description = task_type
            try:
                business_type = BusinessTaskType(task_type)
                description = get_business_type_description(business_type)
            except ValueError:
                try:
                    exec_type = ExecutionTaskType(task_type)
                    description = get_execution_type_description(exec_type)
                except ValueError:
                    description = task_type

            return f"{description}"
        except ImportError:
            return f"{task_type} ({node_id})"

    def on_node_started(self, node_id: str, agent_id: str, task_info=None):
        """节点开始执行."""
        if node_id in self._task_info_map:
            self._task_info_map[node_id]["status"] = "running"

        task_name = self._task_info_map.get(node_id, {}).get("task_name", node_id)
        self._add_event(ProcessStage.NODE_STARTED, {
            "message": f"▶️ 开始执行任务: {task_name}",
            "node_id": node_id,
            "agent_id": agent_id,
            "task_name": task_name
        })

    def on_node_completed(self, node_id: str, agent_id: str, duration_ms: float,
                          output_summary: str = "", task_info=None):
        """节点执行完成."""
        if node_id in self._task_info_map:
            self._task_info_map[node_id]["status"] = "completed"
            self._task_info_map[node_id]["duration_ms"] = duration_ms

        task_name = self._task_info_map.get(node_id, {}).get("task_name", node_id)
        self._add_event(ProcessStage.NODE_COMPLETED, {
            "message": f"✅ 任务完成: {task_name}",
            "node_id": node_id,
            "agent_id": agent_id,
            "duration_ms": duration_ms,
            "output_summary": output_summary,
            "task_name": task_name
        })

    def on_node_failed(self, node_id: str, agent_id: str, error_message: str,
                       retry_count: int = 0, task_info=None):
        """节点执行失败."""
        if node_id in self._task_info_map:
            self._task_info_map[node_id]["status"] = "failed"
            self._task_info_map[node_id]["error_message"] = error_message

        task_name = self._task_info_map.get(node_id, {}).get("task_name", node_id)
        self._add_event(ProcessStage.NODE_FAILED, {
            "message": f"❌ 任务失败: {task_name}",
            "node_id": node_id,
            "agent_id": agent_id,
            "error_message": error_message,
            "retry_count": retry_count,
            "task_name": task_name
        })

    def on_agent_called(self, caller_agent: str, callee_agent: str,
                        input_summary: str = "", output_summary: str = ""):
        """Agent调用."""
        self._add_event(ProcessStage.AGENT_CALLED, {
            "message": f"🔄 {caller_agent} → {callee_agent}",
            "caller_agent": caller_agent,
            "callee_agent": callee_agent,
            "input_summary": input_summary,
            "output_summary": output_summary
        })

    def on_pipeline_completed(self, success: bool = True, summary=None):
        """流程完成."""
        self._is_running = False
        
        data = {
            "message": "✅ 流程执行完成" if success else "❌ 流程执行失败",
            "success": success
        }
        
        if summary:
            data["execution_summary"] = {
                "total_tasks": getattr(summary, 'total_tasks', 0),
                "completed_tasks": getattr(summary, 'completed_tasks', 0),
                "failed_tasks": getattr(summary, 'failed_tasks', 0),
                "total_duration_ms": getattr(summary, 'total_duration_ms', 0)
            }
        
        self._add_event(ProcessStage.PIPELINE_COMPLETED, data)


def format_pipeline_result_to_markdown(result: Dict, user_input: str, events: List[ProcessEvent]) -> str:
    """将Pipeline结果和过程性事件转换为友好的Markdown格式文本."""
    lines = []

    # 获取数据池快照
    snapshot = result.get("data_pool_snapshot", {})
    execution_summary = result.get("execution_summary", {})

    # 1. 任务分析
    lines.append("## 📋 任务分析")
    lines.append("")
    lines.append(f"**用户输入**: {user_input}")
    lines.append("")

    # 2. 决策链任务列表
    task_list_event = None
    for event in events:
        if event.stage == ProcessStage.TASK_LIST_GENERATED:
            task_list_event = event
            break

    if task_list_event:
        lines.append("## 📋 决策链任务列表")
        lines.append("")
        tasks = task_list_event.data.get("tasks", [])
        for task in tasks:
            task_id = task.get("task_id", "")
            task_name = task.get("task_name", "")
            task_type = task.get("task_type", "")
            deps = task.get("dependencies", [])
            deps_str = f" [依赖: {', '.join(deps)}]" if deps else ""
            lines.append(f"- **{task_name}** ({task_type}){deps_str}")
        lines.append("")

    # 3. 执行过程
    lines.append("## 🔧 执行过程")
    lines.append("")

    # Agent调用链
    agent_calls = [e for e in events if e.stage == ProcessStage.AGENT_CALLED]
    if agent_calls:
        lines.append("**Agent调用链**:")
        for call in agent_calls:
            caller = call.data.get("caller_agent", "")
            callee = call.data.get("callee_agent", "")
            input_sum = call.data.get("input_summary", "")
            lines.append(f"- {caller} → {callee} {f'({input_sum})' if input_sum else ''}")
        lines.append("")

    # 任务执行详情
    node_events = [e for e in events if e.stage in (ProcessStage.NODE_STARTED, ProcessStage.NODE_COMPLETED, ProcessStage.NODE_FAILED)]
    if node_events:
        lines.append("**任务执行详情**:")
        lines.append("")

        # 按节点分组，只显示完成/失败的事件
        node_map = {}
        for event in node_events:
            node_id = event.data.get("node_id", "")
            if event.stage in (ProcessStage.NODE_COMPLETED, ProcessStage.NODE_FAILED):
                node_map[node_id] = event

        for node_id, event in node_map.items():
            task_name = event.data.get("task_name", node_id)

            if event.stage == ProcessStage.NODE_COMPLETED:
                duration = event.data.get("duration_ms", 0)
                if duration < 1000:
                    duration_str = f"{duration:.0f}ms"
                else:
                    duration_str = f"{duration/1000:.2f}s"
                output = event.data.get("output_summary", "")
                lines.append(f"- ✅ **{task_name}**: 完成 ({duration_str}) {f'→ {output}' if output else ''}")
            elif event.stage == ProcessStage.NODE_FAILED:
                error = event.data.get("error_message", "未知错误")
                lines.append(f"- ❌ **{task_name}**: 失败 - {error}")

        lines.append("")

    # 4. 执行结果
    if "tool_name" in snapshot:
        lines.append("## 📊 执行结果")
        lines.append("")

        tool_name = snapshot.get("tool_name", "")
        success = snapshot.get("success", False)

        if tool_name == "verification":
            data = snapshot.get("data", {})
            checks = data.get("checks", [])
            all_passed = data.get("all_passed", False)
            overall_score = data.get("overall_score", 0)
            status = data.get("status", "")

            score_emoji = "✅" if all_passed else "⚠️"
            lines.append(f"{score_emoji} **总体评分**: {overall_score:.2f}")
            lines.append(f"**状态**: {status}")
            lines.append("")

            if checks:
                lines.append("**详细检查结果**:")
                lines.append("")
                for check in checks:
                    item = check.get("item", "")
                    passed = check.get("passed", False)
                    score = check.get("score", 0)
                    emoji = "✅" if passed else "❌"
                    status_text = "通过" if passed else "未通过"
                    lines.append(f"- {emoji} **{item}**: {status_text} (得分: {score:.2f})")
                lines.append("")

        elif tool_name == "dispatch":
            data = snapshot.get("data", {})
            dispatch_text = data.get("dispatch_order_text", "")
            if dispatch_text:
                lines.append("**调度指令**:")
                lines.append("```")
                lines.append(dispatch_text)
                lines.append("```")
                lines.append("")

        elif tool_name == "report":
            data = snapshot.get("data", {})
            report_content = data.get("report_content", "")
            if report_content:
                lines.append(report_content)
                lines.append("")

    # 5. 执行统计
    lines.append("## 📊 执行统计")
    lines.append("")

    total_tasks = execution_summary.get("total_tasks", 0)
    completed_tasks = execution_summary.get("completed_tasks", 0)
    failed_tasks = execution_summary.get("failed_tasks", 0)
    total_duration_ms = execution_summary.get("total_duration_ms", 0)

    lines.append(f"- **总任务数**: {total_tasks}")
    lines.append(f"- **成功**: {completed_tasks} ✅")
    if failed_tasks > 0:
        lines.append(f"- **失败**: {failed_tasks} ❌")

    if total_duration_ms < 1000:
        duration_str = f"{total_duration_ms:.0f}ms"
    else:
        duration_str = f"{total_duration_ms / 1000:.2f}s"
    lines.append(f"- **总耗时**: {duration_str}")
    lines.append("")

    # 6. 结论
    success = result.get("success", False)
    lines.append("## 📝 结论")
    lines.append("")
    if success:
        lines.append("✅ 任务执行成功！")
    else:
        error = snapshot.get("error", "未知错误")
        lines.append(f"❌ 任务执行失败: {error}")
    lines.append("")

    return "\n".join(lines)


async def stream_chat_response(
    message: str,
    conversation_id: Optional[str] = None,
) -> AsyncGenerator[str, None]:
    """流式生成聊天响应."""
    import uuid

    # 生成或获取对话ID
    if not conversation_id:
        from web.backend.api.conversations import _conversations, generate_title
        conversation_id = str(uuid.uuid4())
        _conversations[conversation_id] = type('obj', (object,), {
            'id': conversation_id,
            'title': generate_title(),
            'created_at': time.time(),
            'updated_at': time.time(),
            'message_count': 0,
        })()

    # 初始化过程性事件存储
    _process_events[conversation_id] = []

    # 保存用户消息
    user_message = ChatMessage(
        role="user",
        content=message,
        timestamp=time.time(),
    )
    if conversation_id not in _messages:
        _messages[conversation_id] = []
    _messages[conversation_id].append(user_message)

    # 发送用户消息确认
    yield f"data: {json.dumps({'type': 'user_message', 'content': message, 'conversation_id': conversation_id}, ensure_ascii=False)}\n\n"

    # 执行Pipeline
    try:
        # 创建事件收集器
        process_events = []

        def stream_callback(data):
            """流式回调，实时发送过程性事件到前端."""
            process_events.append(data)

        event_collector = WebEventCollector(
            conversation_id=conversation_id,
            stream_callback=stream_callback
        )

        # 创建Pipeline - 使用事件收集器作为visualizer
        # 注意：VisualizedPipeline期望的visualizer需要特定接口
        # 我们创建一个简单的包装器
        class VisualizerWrapper:
            """可视化器包装器 - 适配Pipeline需要的接口."""
            
            def __init__(self, collector):
                self.collector = collector
                self.enabled = True
                self._execution_stats = {
                    "total_tasks": 0,
                    "completed_tasks": 0,
                    "failed_tasks": 0,
                    "total_duration_ms": 0,
                }

            def on_pipeline_start(self, context=None):
                self._execution_stats = {
                    "total_tasks": 0,
                    "completed_tasks": 0,
                    "failed_tasks": 0,
                    "total_duration_ms": 0,
                }
                self.collector.on_pipeline_start(context)

            def on_task_graph_created(self, task_graph):
                nodes = task_graph.get_all_nodes()
                self._execution_stats["total_tasks"] = len(nodes)
                self.collector.on_task_graph_created(task_graph)

            def on_node_started(self, node_id, agent_id, task_info=None):
                self.collector.on_node_started(node_id, agent_id, task_info)

            def on_node_completed(self, node_id, agent_id, duration_ms, output_summary="", task_info=None):
                self._execution_stats["completed_tasks"] += 1
                self._execution_stats["total_duration_ms"] += duration_ms
                self.collector.on_node_completed(node_id, agent_id, duration_ms, output_summary, task_info)

            def on_node_failed(self, node_id, agent_id, error_message, retry_count=0, task_info=None):
                self._execution_stats["failed_tasks"] += 1
                self.collector.on_node_failed(node_id, agent_id, error_message, retry_count, task_info)

            def on_agent_called(self, caller_agent, callee_agent, input_summary="", output_summary=""):
                self.collector.on_agent_called(caller_agent, callee_agent, input_summary, output_summary)

            def on_pipeline_completed(self, success=True, summary=None):
                self.collector.on_pipeline_completed(success, summary)

            def get_execution_summary(self):
                """获取执行汇总 - Pipeline需要的方法."""
                from types import SimpleNamespace
                return SimpleNamespace(**self._execution_stats)

        visualizer_wrapper = VisualizerWrapper(event_collector)

        pipeline = VisualizedPipeline(
            visualizer=visualizer_wrapper,
            seed=42,
            enable_visualization=True,
        )

        # 执行Pipeline
        try:
            result = pipeline.run({
                "type": "natural_language",
                "input": message,
            })
        except Exception as pipeline_error:
            print(f"[ERROR] Pipeline执行异常: {pipeline_error}")
            import traceback
            traceback.print_exc()
            # 创建一个失败的结果
            from types import SimpleNamespace
            result = SimpleNamespace(
                success=False,
                data_pool_snapshot={"error": str(pipeline_error), "raw_user_input": message, "input_type": "natural_language"},
                execution_summary={"total_tasks": 0, "completed_tasks": 0, "failed_tasks": 1, "total_duration_ms": 0}
            )

        # 发送所有过程性事件
        for event_data in process_events:
            yield f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.01)

        # 将结果转换为友好的Markdown格式
        response_text = format_pipeline_result_to_markdown(
            {
                "data_pool_snapshot": result.data_pool_snapshot,
                "execution_summary": result.execution_summary,
                "success": result.success,
            },
            message,
            event_collector.events
        )

        # 流式发送最终响应（按行发送）
        lines = response_text.split('\n')
        accumulated_content = ""

        for line in lines:
            chunk = line + '\n'
            accumulated_content += chunk

            yield f"data: {json.dumps({'type': 'chunk', 'content': chunk, 'accumulated': accumulated_content}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.02)

        # 保存AI回复
        assistant_message = ChatMessage(
            role="assistant",
            content=response_text,
            timestamp=time.time(),
        )
        _messages[conversation_id].append(assistant_message)

        # 更新对话消息计数
        from web.backend.api.conversations import update_conversation_message_count
        update_conversation_message_count(conversation_id, len(_messages[conversation_id]))

        # 发送完成事件
        yield f"data: {json.dumps({'type': 'complete', 'content': response_text, 'conversation_id': conversation_id}, ensure_ascii=False)}\n\n"

    except Exception as e:
        import traceback
        error_message = f"处理出错: {str(e)}"
        print(f"Error: {error_message}")
        print(traceback.format_exc())
        yield f"data: {json.dumps({'type': 'error', 'content': error_message}, ensure_ascii=False)}\n\n"


@router.post("/chat")
async def chat(request: ChatRequest):
    """发送消息并获取回复."""
    if request.stream:
        return StreamingResponse(
            stream_chat_response(request.message, request.conversation_id),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    else:
        # 非流式响应
        full_content = ""
        conversation_id = None

        async for chunk in stream_chat_response(request.message, request.conversation_id):
            if chunk.startswith("data: "):
                data = json.loads(chunk[6:])
                if data.get("type") == "complete":
                    full_content = data.get("content", "")
                    conversation_id = data.get("conversation_id")
                elif data.get("type") == "error":
                    raise HTTPException(status_code=500, detail=data.get("content"))

        return {
            "content": full_content,
            "conversation_id": conversation_id,
        }


@router.get("/conversations/{conversation_id}/messages")
async def get_messages(conversation_id: str) -> List[Dict]:
    """获取对话消息历史."""
    messages = _messages.get(conversation_id, [])
    return [
        {
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.timestamp,
        }
        for msg in messages
    ]


@router.get("/conversations/{conversation_id}/process-events")
async def get_process_events(conversation_id: str) -> List[Dict]:
    """获取对话的过程性事件."""
    events = _process_events.get(conversation_id, [])
    return [
        {
            "stage": e.stage.value,
            "timestamp": e.timestamp,
            "data": e.data,
        }
        for e in events
    ]


@router.post("/conversations/{conversation_id}/clear")
async def clear_messages(conversation_id: str) -> dict:
    """清空对话消息."""
    if conversation_id in _messages:
        _messages[conversation_id] = []

    if conversation_id in _process_events:
        _process_events[conversation_id] = []

    return {"success": True, "message": "对话已清空"}
