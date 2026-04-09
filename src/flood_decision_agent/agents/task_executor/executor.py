"""单元任务执行 Agent - 支持动态工具选择和自主选用，集成MCP工具"""

from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, List, Optional

from flood_decision_agent.agents.base import BaseAgent
from flood_decision_agent.core.message import BaseMessage, MessageType
from flood_decision_agent.core.shared_data_pool import SharedDataPool
from flood_decision_agent.fusion.decision_fusion import DecisionFusion
from flood_decision_agent.tools.registry import ToolMetadata, ToolRegistry, get_tool_registry
from flood_decision_agent.tools.common_tools import CommonTools

# 数据获取服务集成
from flood_decision_agent.application.services.data_acquisition.service import DataAcquisitionService
from flood_decision_agent.application.services.data_acquisition.models import DataRequest
from flood_decision_agent.application.services.data_acquisition.clarification.manager import ClarificationManager

# MCP客户端集成
from flood_decision_agent.mcp.clients.base import MCPClientManager


# ==================== 工具类型映射 ====================
# 用于将任务类型映射到 MCP 工具，实现智能工具选用
TASK_TYPE_TO_MCP_TOOLS = {
    # 数据查询类任务
    "data_query": [
        "get_current_rainfall",  # rainfall
        "get_rainfall_forecast",  # rainfall
        "get_hydrological_data",  # data_hub
    ],
    "data_collection": [
        "get_current_rainfall",
        "get_hourly_rainfall",
        "get_rainfall_forecast",
        "get_rainfall_by_coords",
    ],
    "rainfall_analysis": [
        "get_rainfall_data",
        "get_current_rainfall",
        "get_hourly_rainfall",
        "get_rainfall_forecast",
        "aggregate_data_sources",
    ],
    # 水文模拟类任务
    "hydrological_simulation": [
        "run_hydrological_model",  # hydrology
    ],
    "flood_simulation": [
        "run_flood_simulation",  # hipims
        "run_hydrological_model",
    ],
    "flood_forecast": [
        "run_flood_simulation",
        "get_rainfall_forecast",
    ],
    # 调度决策类任务
    "dispatch_decision": [
        "create_plan",  # decision_chain
        "update_plan",
    ],
    "scheduling": [
        "create_plan",
        "update_plan",
    ],
    # 文档处理类任务
    "document_processing": [
        "docx_to_markdown",
        "read_docx_content",
    ],
    # 文件操作类任务
    "file_operation": [
        "read_planning_file",
        "write_planning_markdown",
        "read_data_json",
        "write_data_json",
    ],
    # 网络搜索类任务
    "web_search": [
        "web_search",
        "search",
    ],
    # 天气预报类任务
    "weather_forecast": [
        "get_current_rainfall",  # rainfall - 实时天气包含降雨信息
        "get_rainfall_forecast",  # rainfall - 降雨预报
    ],
    "rainfall_forecast": [
        "get_rainfall_forecast",  # rainfall
        "get_hourly_rainfall",    # rainfall
        "get_rainfall_by_coords", # rainfall
    ],
}

# 任务类型友好名称映射（用于前端显示）
TASK_TYPE_FRIENDLY_NAMES = {
    "data_query": "数据查询",
    "data_collection": "数据获取",
    "data_processing": "数据分析",
    "rainfall_analysis": "降雨分析",
    "hydrological_simulation": "水文模拟",
    "flood_simulation": "洪水模拟",
    "flood_forecast": "洪水预报",
    "dispatch_decision": "调度决策",
    "scheduling": "调度计划",
    "reporting": "生成报告",
    "document_processing": "文档处理",
    "file_operation": "文件操作",
    "web_search": "网络搜索",
    "weather_forecast": "天气预报",
    "rainfall_forecast": "降雨预报",
    "analysis": "分析任务",
    "unknown": "未知任务",
}

# MCP 工具友好名称映射（用于前端显示）
MCP_TOOL_FRIENDLY_NAMES = {
    # rainfall 工具
    "get_rainfall_data": "获取降雨数据",
    "get_current_rainfall": "获取当前降雨",
    "get_rainfall_forecast": "获取降雨预报",
    "get_hourly_rainfall": "获取逐小时降雨",
    "get_rainfall_by_coords": "根据坐标获取降雨",
    # data_hub 工具
    "get_hydrological_data": "获取水文数据",
    "aggregate_data_sources": "聚合数据源",
    "check_data_sources_status": "检查数据源状态",
    # hydrology 工具
    "run_hydrological_model": "运行水文模型",
    # hipims 工具
    "run_flood_simulation": "运行洪水模拟",
    # decision_chain 工具
    "create_plan": "创建方案",
    "update_plan": "更新方案",
    "create_spec": "创建规范",
    "read_plan": "读取方案",
    "read_spec": "读取规范",
    # filesystem 工具
    "read_planning_file": "读取规划文件",
    "write_planning_markdown": "写入规划文档",
    "read_data_json": "读取数据文件",
    "write_data_json": "写入数据文件",
    # document 工具
    "docx_to_markdown": "文档转换",
    "read_docx_content": "读取Word文档",
}


class UnitTaskExecutionAgent(BaseAgent):
    """单元任务执行 Agent
    
    特性：
    1. 优先使用上游Agent指定的工具列表
    2. 上游未指定时，可从常用工具库自主选用
    3. 支持多种执行策略：single/parallel/fallback/auto
    4. 集成MCP工具自动选择和调用
    """

    def __init__(
        self,
        agent_id: str = "UnitTaskExecutor",
        fusion: Optional[DecisionFusion] = None,
        tool_registry: Optional[ToolRegistry] = None,
        enable_common_tools: bool = True,
        handlers: Optional[Dict[str, Any]] = None,  # 向后兼容参数
        data_acquisition_service: Optional[DataAcquisitionService] = None,
        clarification_manager: Optional[ClarificationManager] = None,
        enable_mcp: bool = True,  # 启用MCP集成
        mcp_config_path: Optional[str] = None,  # MCP配置文件路径
    ):
        super().__init__(agent_id)
        self.fusion = fusion or DecisionFusion()
        self.tool_registry = tool_registry or get_tool_registry()
        self.tool_registry.set_logger(self.logger)
        
        # 数据获取服务
        self.data_service = data_acquisition_service
        self.clarification_manager = clarification_manager
        
        # 数据依赖缓存
        self._data_cache: Dict[str, Any] = {}
        self._pending_data_requests: List[DataRequest] = []
        
        # MCP客户端管理器
        self._mcp_manager: Optional[MCPClientManager] = None
        self._mcp_enabled = enable_mcp
        self._mcp_config_path = mcp_config_path or "configs/mcp/servers.yaml"
        self._mcp_tools_cache: Dict[str, Dict[str, Any]] = {}  # 缓存MCP工具信息
        
        # 向后兼容：注册旧式 handlers 为工具
        if handlers:
            self._register_legacy_handlers(handlers)
        
        # 注册常用工具（使用当前注册表）
        if enable_common_tools:
            CommonTools.register_all(self.tool_registry)
            self.logger.info(f"常用工具已注册，共 {len(self.tool_registry.list_tools())} 个")
    
    def _register_legacy_handlers(self, handlers: Dict[str, Any]) -> None:
        """注册旧式 handlers 为工具（向后兼容）"""
        from flood_decision_agent.tools.registry import ToolMetadata
        
        for name, handler in handlers.items():
            # 包装旧式 handler 为新式 tool
            def wrapper(data_pool, config, handler=handler):
                return handler(data_pool)
            
            self.tool_registry.register(
                name,
                wrapper,
                ToolMetadata(
                    name=name,
                    description=f"Legacy handler: {name}",
                    task_types={"legacy"},
                    priority=50,
                )
            )
            self.logger.debug(f"注册旧式 handler: {name}")

    async def initialize_mcp(self) -> bool:
        """初始化MCP客户端管理器并连接所有服务
        
        Returns:
            是否成功初始化
        """
        if not self._mcp_enabled:
            self.logger.debug("MCP集成已禁用")
            return False
        
        if self._mcp_manager is not None:
            self.logger.debug("MCP管理器已初始化")
            return True
        
        try:
            self.logger.info("初始化MCP客户端管理器...")
            self._mcp_manager = MCPClientManager()
            
            # 从配置加载服务器
            self._mcp_manager.load_from_config(self._mcp_config_path)
            
            # 连接所有服务器
            connected = await self._mcp_manager.connect_all()
            self.logger.info(f"MCP服务器连接完成: {connected} 个")
            
            # 缓存所有可用工具
            await self._cache_mcp_tools()
            
            return connected > 0
            
        except Exception as e:
            self.logger.error(f"MCP初始化失败: {e}")
            self._mcp_manager = None
            return False
    
    async def _cache_mcp_tools(self) -> None:
        """缓存所有MCP服务器的工具信息"""
        if not self._mcp_manager:
            return
        
        self._mcp_tools_cache = {}
        
        for server_name, client in self._mcp_manager.clients.items():
            if not client._connected:
                continue
            
            tools = client.tools if hasattr(client, 'tools') else []
            for tool in tools:
                # 处理 MCPToolInfo 对象（使用属性访问）或字典（使用 get 方法）
                if hasattr(tool, 'name'):
                    # MCPToolInfo 对象
                    tool_name = tool.name
                    tool_info = {
                        'name': tool.name,
                        'description': tool.description,
                        'input_schema': tool.input_schema,
                    }
                else:
                    # 字典格式
                    tool_name = tool.get('name', '')
                    tool_info = tool
                
                if tool_name:
                    self._mcp_tools_cache[tool_name] = {
                        'server_name': server_name,
                        'tool_info': tool_info,
                    }
        
        self.logger.info(f"已缓存 {len(self._mcp_tools_cache)} 个MCP工具")
    
    def _find_mcp_tools_for_task(self, task_type: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """根据任务类型查找相关的MCP工具
        
        Args:
            task_type: 任务类型
            context: 上下文信息
            
        Returns:
            匹配的MCP工具列表
        """
        if not self._mcp_tools_cache:
            return []
        
        matched_tools = []
        
        # 方法1：使用预定义的工具映射表
        preferred_tools = TASK_TYPE_TO_MCP_TOOLS.get(task_type, [])
        for tool_name in preferred_tools:
            if tool_name in self._mcp_tools_cache:
                tool_info = self._mcp_tools_cache[tool_name]
                matched_tools.append({
                    "tool_name": tool_name,
                    "server_name": tool_info.get("server_name", ""),
                    "tool_info": tool_info.get("tool_info", {}),
                })
        
        # 如果通过映射表找到工具，直接返回
        if matched_tools:
            self.logger.info(f"通过工具映射找到 MCP 工具: {[t['tool_name'] for t in matched_tools]}")
            return matched_tools
        
        # 方法2：使用关键词匹配作为后备
        task_tool_mapping = {
            'data_collection': ['rain', 'weather', 'data', 'query', 'get'],
            'simulation': ['hydro', 'flood', 'model', 'simulation', 'predict'],
            'calculation': ['calc', 'compute', 'analysis', 'hydro'],
            'decision': ['dispatch', 'plan', 'decision', 'optimize'],
            'execution': ['execute', 'control', 'operate'],
            'verification': ['verify', 'check', 'validate', 'report'],
            'flood_dispatch': ['rain', 'hydro', 'flood', 'dispatch', 'inflow'],
            'hydrological_model': ['hydro', 'rain', 'inflow', 'runoff'],
            'reservoir_dispatch': ['dispatch', 'reservoir', 'flood', 'plan'],
        }
        
        # 从上下文中提取额外关键词
        context_text = context.get('description', '') + ' ' + context.get('user_input', '')
        
        # 获取匹配关键词
        keywords = task_tool_mapping.get(task_type, [task_type.lower()])
        
        # 在上下文中查找额外关键词
        additional_keywords = []
        if 'rain' in context_text.lower() or '降雨' in context_text:
            additional_keywords.append('rain')
        if 'flood' in context_text.lower() or '洪水' in context_text:
            additional_keywords.append('flood')
        if 'dispatch' in context_text.lower() or '调度' in context_text:
            additional_keywords.append('dispatch')
        if 'inflow' in context_text.lower() or '入库' in context_text:
            additional_keywords.append('inflow')
        
        keywords.extend(additional_keywords)
        
        # 查找匹配的工具
        matched_tools = []
        for tool_name, tool_cache in self._mcp_tools_cache.items():
            tool_info = tool_cache['tool_info']
            # 统一使用字典方式访问工具信息
            if isinstance(tool_info, dict):
                tool_desc = tool_info.get('description', '').lower()
            else:
                # MCPToolInfo 对象
                tool_desc = getattr(tool_info, 'description', '').lower()
            tool_name_lower = tool_name.lower()
            
            # 检查是否匹配任何关键词
            for keyword in keywords:
                if keyword in tool_name_lower or keyword in tool_desc:
                    matched_tools.append({
                        'tool_name': tool_name,
                        'server_name': tool_cache['server_name'],
                        'tool_info': tool_info,
                        'matched_keyword': keyword,
                    })
                    break
        
        return matched_tools
    
    async def _execute_mcp_tool(
        self,
        tool_spec: Dict[str, Any],
        data_pool: SharedDataPool,
    ) -> Dict[str, Any]:
        """执行MCP工具
        
        Args:
            tool_spec: 工具规格，包含 tool_name, server_name, tool_config
            data_pool: 数据池
            
        Returns:
            执行结果
        """
        tool_name = tool_spec['tool_name']
        server_name = tool_spec.get('server_name')
        tool_config = tool_spec.get('tool_config', {})
        
        self.logger.debug(f"_execute_mcp_tool: tool_name={tool_name}, server_name={server_name}")
        
        if not self._mcp_manager or not server_name:
            return {
                'tool_name': tool_name,
                'success': False,
                'error': 'MCP管理器未初始化或服务器名称缺失',
            }
        
        try:
            # 构建工具参数
            arguments = self._build_mcp_tool_params(tool_name, tool_config, data_pool)
            self.logger.debug(f"MCP tool arguments: {arguments}")
            
            # 调用MCP工具
            result = await self._mcp_manager.call_tool(
                server_name=server_name,
                tool_name=tool_name,
                arguments=arguments
            )
            self.logger.debug(f"MCP tool {tool_name} raw result: {result}")
            
            return {
                'tool_name': tool_name,
                'success': True,
                'data': result,
                'server': server_name,
            }
            
        except Exception as e:
            self.logger.error(f"MCP工具 {tool_name} 执行失败: {e}")
            return {
                'tool_name': tool_name,
                'success': False,
                'error': str(e),
                'server': server_name,
            }
    
    def _build_mcp_tool_params(
        self,
        tool_name: str,
        tool_config: Dict[str, Any],
        data_pool: SharedDataPool,
    ) -> Dict[str, Any]:
        """构建MCP工具参数
        
        根据工具名称和数据池内容智能构建参数
        """
        params = dict(tool_config)
        
        # 常见参数映射
        if 'city' not in params:
            # 尝试从数据池获取城市信息
            city = data_pool.get('city') or data_pool.get('station')
            if city:
                params['city'] = city
                self.logger.debug(f"从data_pool获取city: {city}")
            else:
                params['city'] = '北京'  # 默认值
                self.logger.debug(f"data_pool中无city，使用默认值: 北京")
        
        if 'days' not in params and 'forecast' in tool_name.lower():
            params['days'] = 3  # 默认预报3天
        
        if 'station' not in params:
            station = data_pool.get('station') or data_pool.get('reservoir')
            if station:
                params['station'] = station
        
        return params

    def _process(self, message: BaseMessage) -> Dict[str, Any]:
        """处理单元任务执行请求（同步入口）

        注意：如果启用了MCP，此方法会创建事件循环来运行异步逻辑
        """
        # 如果需要MCP支持，使用异步处理
        if self._mcp_enabled:
            self.logger.info(f"[DEBUG] MCP enabled=True, 缓存工具数: {len(self._mcp_tools_cache)}")
            try:
                # 检查是否有运行中的事件循环
                loop = asyncio.get_running_loop()
                # 有事件循环在运行，使用线程池来执行异步代码
                # 避免嵌套事件循环问题
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                    future = pool.submit(asyncio.run, self._process_async(message))
                    return future.result(timeout=120)  # 2分钟超时
            except RuntimeError:
                # 没有事件循环在运行，可以直接使用 asyncio.run
                return asyncio.run(self._process_async(message))
        else:
            # 不使用MCP，使用传统同步处理
            return self._process_sync(message)
    
    async def _process_async(self, message: BaseMessage) -> Dict[str, Any]:
        """异步处理单元任务执行请求（支持MCP工具）"""
        # 确保MCP已初始化
        if self._mcp_enabled and not self._mcp_manager:
            await self.initialize_mcp()
        
        return self._process_sync(message, use_mcp=True)
    
    def _process_sync(self, message: BaseMessage, use_mcp: bool = False) -> Dict[str, Any]:
        """处理单元任务执行请求"""
        payload = message.payload
        
        # 1. 解析消息
        node_id = payload.get("node_id", "unknown")
        task_type = payload.get("task_type", "default")
        tools_spec = payload.get("tools", [])  # 上游指定的工具列表
        execution_strategy = payload.get("execution_strategy", "auto")
        data_pool = payload.get("data_pool")
        context = payload.get("context", {})
        data_dependencies = payload.get("data_dependencies", [])  # 数据依赖定义
        
        if not data_pool:
            raise ValueError("消息 payload 必须包含 'data_pool'")
        
        self.logger.info(f"[节点 {node_id}] 开始执行，任务类型: {task_type}, 策略: {execution_strategy}")
        
        # 2. 检查数据依赖
        if data_dependencies and self.data_service:
            missing_data = self._check_data_dependencies(data_dependencies, data_pool)
            if missing_data:
                self.logger.info(f"[节点 {node_id}] 发现缺失数据: {[d.data_key for d in missing_data]}")
                # 返回数据请求状态，暂停执行
                return {
                    "node_id": node_id,
                    "task_type": task_type,
                    "status": "waiting_for_data",
                    "pending_data_requests": [
                        {
                            "data_key": d.data_key,
                            "description": d.description,
                            "required": d.required,
                        }
                        for d in missing_data
                    ],
                    "message": "任务执行需要补充数据",
                }
        
        # 3. 工具选择决策（包含MCP工具）
        selected_tools = self._select_tools(tools_spec, task_type, context, use_mcp=use_mcp)
        
        if not selected_tools:
            raise ValueError(f"未找到适合任务类型 '{task_type}' 的工具")
        
        self.logger.info(f"选定工具: {[t['tool_name'] for t in selected_tools]}")
        
        # 4. 确定执行策略
        strategy = self._determine_strategy(execution_strategy, selected_tools, task_type)
        self.logger.info(f"执行策略: {strategy}")
        
        # 5. 执行任务
        start_time = time.time()
        results = self._execute_with_strategy(selected_tools, data_pool, strategy, use_mcp=use_mcp)
        elapsed_ms = (time.time() - start_time) * 1000
        
        # 6. 结果处理
        if len(results) > 1 and strategy in ("parallel", "auto"):
            # 多结果融合
            fused_result = self._fuse_results(results)
        else:
            fused_result = results[0] if results else {}
        
        # 7. 检查是否有工具执行失败（检查原始results列表，不依赖融合后的结果）
        self.logger.debug(f"[DEBUG] _process_sync results: {[(r.get('tool_name'), r.get('success')) for r in results]}")
        has_failure = any(r.get("success", True) == False for r in results)
        if has_failure:
            failed_tools = [r.get("tool_name") for r in results if r.get("success", True) == False]
            error_info = "; ".join([r.get("error", "Unknown error") for r in results if r.get("success", True) == False])
            self.logger.warning(f"[节点 {node_id}] 部分工具执行失败: {failed_tools}, 错误: {error_info}")
        
        # 8. 构建响应
        self.logger.info(f"[DEBUG] MCP执行结果: {fused_result}")
        response = {
            "node_id": node_id,
            "task_type": task_type,
            "status": "failed" if has_failure else "success",
            "output": fused_result,
            "error": error_info if has_failure else None,
            "metrics": {
                "elapsed_time_ms": elapsed_ms,
                "tools_used": [t['tool_name'] for t in selected_tools],
                "execution_strategy": strategy,
                "tool_count": len(selected_tools),
            }
        }
        
        self.logger.info(f"[节点 {node_id}] 执行完成，耗时: {elapsed_ms:.2f}ms")
        return response

    def _check_data_dependencies(
        self,
        data_dependencies: List[Dict[str, Any]],
        data_pool: SharedDataPool,
    ) -> List[DataRequest]:
        """检查任务所需数据是否已获取。
        
        Args:
            data_dependencies: 数据依赖定义列表
            data_pool: 数据池
            
        Returns:
            缺失的数据请求列表
        """
        missing_requests = []
        
        for dep in data_dependencies:
            data_key = dep.get("data_key")
            
            # 检查数据池中是否已有该数据
            if data_pool.has(data_key):
                continue
            
            # 检查本地缓存
            if data_key in self._data_cache:
                # 将缓存数据放入数据池
                data_pool.set(data_key, self._data_cache[data_key])
                continue
            
            # 构建数据请求
            request = DataRequest(
                data_key=data_key,
                description=dep.get("description", ""),
                required=dep.get("required", True),
                value_schema=dep.get("value_schema"),
                default_value=dep.get("default_value"),
                validation_rules=dep.get("validation_rules"),
            )
            missing_requests.append(request)
        
        return missing_requests

    def request_data_during_execution(
        self,
        data_key: str,
        context: Dict[str, Any],
        allow_defaults: bool = True,
    ) -> Optional[Any]:
        """执行中请求数据。
        
        Args:
            data_key: 数据键名
            context: 上下文信息
            allow_defaults: 是否允许使用默认值
            
        Returns:
            数据值，获取失败返回 None
        """
        if not self.data_service:
            self.logger.warning("数据获取服务未初始化")
            return None
        
        # 构建数据请求
        request = DataRequest(
            data_key=data_key,
            description=context.get("description", ""),
            required=context.get("required", True),
        )
        
        # 请求数据
        response = self.data_service.request_data(request)
        
        if response.value is not None:
            # 缓存数据
            self._data_cache[data_key] = response.value
            return response.value
        
        # 尝试获取默认值
        if allow_defaults and self.clarification_manager:
            suggestions = self.clarification_manager.provide_default_suggestions(
                data_key, context
            )
            if suggestions:
                # 使用最佳默认值
                best = suggestions[0]
                self.logger.info(f"使用默认值: {data_key} = {best.value}")
                self._data_cache[data_key] = best.value
                return best.value
        
        return None

    def _select_tools(
        self,
        tools_spec: List[Dict[str, Any]],
        task_type: str,
        context: Dict[str, Any],
        use_mcp: bool = False,
    ) -> List[Dict[str, Any]]:
        """工具选择决策 - 补充策略（支持MCP工具）
        
        核心逻辑：
        1. 优先使用上游指定的工具
        2. 当上游工具不足时，从常用工具库自主选用补充
        3. 如果启用MCP，同时查找并选用MCP工具
        
        补充触发条件：
        - 上游未指定任何工具
        - 上游指定的工具部分不可用
        - 上游指定的工具数量不足以完成任务
        """
        allow_auto_select = context.get("allow_auto_select", True)
        selected_tools = []
        mcp_tools_added = []
        
        # 步骤1：验证并使用上游指定的工具
        if tools_spec:
            for tool in tools_spec:
                tool_name = tool.get("tool_name")
                if self.tool_registry.is_available(tool_name):
                    selected_tools.append(tool)
                    self.logger.debug(f"上游指定工具 '{tool_name}' 验证通过")
                else:
                    self.logger.warning(f"上游指定工具 '{tool_name}' 不可用，将从常用工具库选用补充")
        
        # 步骤2：检查是否需要自主选用补充
        need_supplement = False
        
        if not selected_tools:
            # 情况A：上游未指定，或指定的全部不可用
            self.logger.info("上游未提供可用工具，将自主选用")
            need_supplement = True
        elif len(selected_tools) < self._get_min_tools_required(task_type):
            # 情况B：工具数量不足
            self.logger.info(f"上游工具数量不足（{len(selected_tools)} < {self._get_min_tools_required(task_type)}），将补充选用")
            need_supplement = True
        
        # 步骤3：自主选用补充（本地工具 + MCP工具）
        if need_supplement and allow_auto_select:
            # 3.1 选用本地工具
            supplement_tools = self._auto_select_tools(task_type, exclude_names={t["tool_name"] for t in selected_tools})
            if supplement_tools:
                self.logger.info(f"自主选用补充工具: {[t['tool_name'] for t in supplement_tools]}")
                selected_tools.extend(supplement_tools)
            
            # 3.2 选用MCP工具（如果启用）
            if use_mcp and self._mcp_enabled and self._mcp_tools_cache:
                mcp_tools = self._find_mcp_tools_for_task(task_type, context)
                if mcp_tools:
                    # 转换为工具规格格式
                    for mcp_tool in mcp_tools[:2]:  # 最多选2个MCP工具
                        mcp_tool_spec = {
                            "tool_name": mcp_tool["tool_name"],
                            "tool_config": {},
                            "server_name": mcp_tool["server_name"],
                            "is_mcp_tool": True,  # 标记为MCP工具
                            "priority": 80,  # MCP工具优先级较高
                        }
                        mcp_tools_added.append(mcp_tool_spec)
                    
                    self.logger.info(f"自主选用MCP工具: {[t['tool_name'] for t in mcp_tools_added]}")
                    selected_tools.extend(mcp_tools_added)
        
        # 步骤4：如果没有选到任何工具，尝试使用MCP工具（即使不需要补充）
        if not selected_tools and use_mcp and self._mcp_enabled and self._mcp_tools_cache:
            mcp_tools = self._find_mcp_tools_for_task(task_type, context)
            if mcp_tools:
                for mcp_tool in mcp_tools[:2]:
                    mcp_tool_spec = {
                        "tool_name": mcp_tool["tool_name"],
                        "tool_config": {},
                        "server_name": mcp_tool["server_name"],
                        "is_mcp_tool": True,
                        "priority": 80,
                    }
                    selected_tools.append(mcp_tool_spec)
                self.logger.info(f"使用MCP工具: {[t['tool_name'] for t in selected_tools]}")
        
        return selected_tools
    
    def _get_min_tools_required(self, task_type: str) -> int:
        """根据任务类型判断最少需要多少工具"""
        # 简单启发式规则，可根据实际需求调整
        multi_tool_tasks = {
            "hydrological_model": 2,  # 通常需要数据获取+计算
            "reservoir_dispatch": 2,  # 通常需要计算+方案生成
            "data_query": 1,
            "format": 1,
            "compute": 1,
            "log": 1,
        }
        return multi_tool_tasks.get(task_type, 1)

    def _auto_select_tools(
        self, 
        task_type: str,
        exclude_names: Optional[set] = None
    ) -> List[Dict[str, Any]]:
        """根据任务类型从常用工具库选择工具
        
        Args:
            task_type: 任务类型
            exclude_names: 需要排除的工具名称集合（避免重复选择上游已指定的工具）
        """
        exclude_names = exclude_names or set()
        matching_tools = self.tool_registry.find_by_task_type(task_type)
        
        if not matching_tools:
            # 尝试更宽泛的任务类型匹配
            broad_types = self._get_broad_task_types(task_type)
            for broad_type in broad_types:
                matching_tools = self.tool_registry.find_by_task_type(broad_type)
                if matching_tools:
                    break
        
        if not matching_tools:
            return []
        
        # 过滤掉已排除的工具，选择优先级最高的前3个
        selected = [
            tool for tool in matching_tools 
            if tool.name not in exclude_names
        ][:3]
        
        return [
            {
                "tool_name": tool.name,
                "tool_config": {},
                "priority": tool.priority,
            }
            for tool in selected
        ]

    def _get_broad_task_types(self, task_type: str) -> List[str]:
        """获取更宽泛的任务类型"""
        # 任务类型层次结构
        hierarchy = {
            "hydrological_model": ["compute", "data_query"],
            "reservoir_dispatch": ["compute", "log"],
            "data_query": ["data_query"],
            "format": ["format"],
        }
        return hierarchy.get(task_type, ["data_query"])

    def _determine_strategy(
        self,
        execution_strategy: str,
        tools: List[Dict[str, Any]],
        task_type: str,
    ) -> str:
        """确定执行策略"""
        if execution_strategy != "auto":
            return execution_strategy
        
        # auto策略的决策逻辑
        tool_count = len(tools)
        
        if tool_count == 1:
            return "single"
        
        # 某些任务类型适合并行
        parallel_friendly = {"compute", "statistics", "data_query"}
        if task_type in parallel_friendly:
            return "parallel"
        
        # 需要可靠性的任务使用fallback
        reliability_required = {"reservoir_dispatch", "flood_warning"}
        if task_type in reliability_required:
            return "fallback"
        
        # 默认使用parallel
        return "parallel"

    def _execute_with_strategy(
        self,
        tools: List[Dict[str, Any]],
        data_pool: SharedDataPool,
        strategy: str,
        use_mcp: bool = False,
    ) -> List[Dict[str, Any]]:
        """按策略执行工具（支持MCP工具）"""
        self.logger.debug(f"[DEBUG] _execute_with_strategy 开始，策略: {strategy}, use_mcp: {use_mcp}, tools: {[t.get('tool_name') for t in tools]}")
        if strategy == "single":
            tool = tools[0]
            result = self._execute_single_tool(tool, data_pool, use_mcp=use_mcp)
            return [result]
        
        elif strategy == "parallel":
            return self._execute_parallel(tools, data_pool, use_mcp=use_mcp)
        
        elif strategy == "fallback":
            return self._execute_fallback(tools, data_pool, use_mcp=use_mcp)
        
        elif strategy == "ensemble":
            # 集成策略：并行执行所有工具并合并结果
            return self._execute_parallel(tools, data_pool, use_mcp=use_mcp)
        
        elif strategy == "no_handler":
            # 无处理程序策略：返回空结果
            self.logger.warning(f"策略为 'no_handler'，无可用工具执行")
            return [{
                "tool_name": "none",
                "success": True,
                "data": {},
                "message": "No handler available for this task",
            }]
        
        else:
            raise ValueError(f"未知的执行策略: {strategy}")

    def _execute_single_tool(
        self,
        tool_spec: Dict[str, Any],
        data_pool: SharedDataPool,
        use_mcp: bool = False,
    ) -> Dict[str, Any]:
        """执行单个工具（支持MCP工具）"""
        tool_name = tool_spec["tool_name"]
        tool_config = tool_spec.get("tool_config", {})
        is_mcp_tool = tool_spec.get("is_mcp_tool", False)

        # 如果是MCP工具且启用了MCP
        if is_mcp_tool and use_mcp and self._mcp_manager:
            try:
                # 使用 nest_asyncio 来允许嵌套事件循环
                import nest_asyncio
                nest_asyncio.apply()
                
                # 现在可以安全地使用 asyncio.run
                return asyncio.run(self._execute_mcp_tool(tool_spec, data_pool))
            except ImportError:
                # 如果没有 nest_asyncio，使用线程池
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                    future = pool.submit(
                        asyncio.run,
                        self._execute_mcp_tool(tool_spec, data_pool)
                    )
                    return future.result(timeout=60)
            except Exception as e:
                self.logger.error(f"MCP工具 {tool_name} 执行失败: {e}")
                return {
                    "tool_name": tool_name,
                    "success": False,
                    "error": str(e),
                    "is_mcp": True,
                }

        # 执行本地工具
        try:
            result = self.tool_registry.execute(tool_name, data_pool, tool_config)
            return {
                "tool_name": tool_name,
                "success": True,
                "data": result,
                "is_mcp": False,
            }
        except Exception as e:
            self.logger.error(f"工具 {tool_name} 执行失败: {e}")
            return {
                "tool_name": tool_name,
                "success": False,
                "error": str(e),
                "is_mcp": False,
            }

    def _execute_parallel(
        self,
        tools: List[Dict[str, Any]],
        data_pool: SharedDataPool,
        use_mcp: bool = False,
    ) -> List[Dict[str, Any]]:
        """并行执行多个工具（支持MCP工具）"""
        self.logger.debug(f"[DEBUG] _execute_parallel 开始执行，工具数: {len(tools)}, use_mcp: {use_mcp}")
        results = []
        
        # 使用线程池或异步执行
        # 这里简化为顺序执行，实际可优化为并发
        for tool in tools:
            self.logger.debug(f"[DEBUG] _execute_parallel 执行工具: {tool.get('tool_name')}, is_mcp_tool: {tool.get('is_mcp_tool')}")
            result = self._execute_single_tool(tool, data_pool, use_mcp=use_mcp)
            results.append(result)
        
        return results

    def _execute_fallback(
        self,
        tools: List[Dict[str, Any]],
        data_pool: SharedDataPool,
        use_mcp: bool = False,
    ) -> List[Dict[str, Any]]:
        """降级策略：按优先级依次尝试（支持MCP工具）"""
        # 按优先级排序
        sorted_tools = sorted(tools, key=lambda t: t.get("priority", 100))
        
        for tool in sorted_tools:
            result = self._execute_single_tool(tool, data_pool, use_mcp=use_mcp)
            if result["success"]:
                return [result]
        
        # 全部失败，返回最后一个错误
        return [result] if result else []

    def _fuse_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """融合多个工具的执行结果"""
        # 添加详细日志
        self.logger.info(f"[DEBUG] _fuse_results 收到 {len(results)} 个结果:")
        for i, r in enumerate(results):
            self.logger.info(f"  结果 {i}: tool={r.get('tool_name')}, success={r.get('success')}, keys={list(r.get('data', {}).keys()) if isinstance(r.get('data'), dict) else type(r.get('data'))}")
        
        successful = [r for r in results if r.get("success")]
        
        if not successful:
            # 全部失败
            return {
                "success": False,
                "errors": [r.get("error") for r in results],
            }
        
        if len(successful) == 1:
            return successful[0]["data"]
        
        # 使用决策融合模块
        candidates = [s["data"] for s in successful]
        fused = self.fusion.fuse(candidates)
        
        return fused.value if hasattr(fused, 'value') else fused

    def execute_task(
        self,
        node_id: str,
        task_type: str,
        data_pool: SharedDataPool,
        tools: Optional[List[Dict[str, Any]]] = None,
        execution_strategy: str = "auto",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """便捷方法：直接执行任务（无需构造消息）"""
        message = BaseMessage(
            type=MessageType.NODE_EXECUTE,
            payload={
                "node_id": node_id,
                "task_type": task_type,
                "tools": tools or [],
                "execution_strategy": execution_strategy,
                "data_pool": data_pool,
                "context": context or {},
            },
            sender="direct_call",
        )
        return self.execute(message)

    def list_available_tools(self) -> List[str]:
        """列出所有可用工具"""
        return self.tool_registry.list_tools()

    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """获取工具信息"""
        meta = self.tool_registry.get_metadata(tool_name)
        if meta:
            return {
                "name": meta.name,
                "description": meta.description,
                "task_types": list(meta.task_types),
                "priority": meta.priority,
                "required_keys": list(meta.required_keys),
                "output_keys": list(meta.output_keys),
            }
        return None


def build_default_handlers(mock_generator: Any) -> Dict[str, HandlerFn]:
    """构建默认处理器（向后兼容）"""
    import pandas as pd

    def get_rainfall_forecast(data_pool: SharedDataPool) -> dict[str, Any]:
        rainfall = mock_generator.generate_rainfall_forecast()
        report = mock_generator.validate_rainfall_forecast(rainfall)
        if not report.ok:
            raise ValueError("; ".join(report.errors))
        return {"rainfall_forecast": rainfall}

    def get_inflow_forecast(data_pool: SharedDataPool) -> dict[str, Any]:
        rainfall: pd.DataFrame = data_pool.get("rainfall_forecast")
        inflow = mock_generator.generate_inflow_forecast(rainfall)
        report = mock_generator.validate_inflow_forecast(inflow)
        if not report.ok:
            raise ValueError("; ".join(report.errors))
        alignment = mock_generator.validate_pair_alignment(rainfall, inflow)
        if not alignment.ok:
            raise ValueError("; ".join(alignment.errors))
        return {"inflow_forecast": inflow}

    def compute_dispatch_plan(data_pool: SharedDataPool) -> dict[str, Any]:
        inflow: pd.DataFrame = data_pool.get("inflow_forecast")
        peak = float(inflow["inflow_m3s"].max())
        target_peak = 19000.0
        gate_ratio = min(1.0, target_peak / max(peak, 1.0))
        plan = {
            "strategy": "conventional",
            "peak_inflow_m3s": peak,
            "gate_ratio": gate_ratio,
        }
        return {"dispatch_plan": plan}

    def generate_dispatch_order(data_pool: SharedDataPool) -> dict[str, Any]:
        plan: dict[str, Any] = data_pool.get("dispatch_plan")
        text = (
            "调令草稿：\n"
            f"- 策略：{plan['strategy']}\n"
            f"- 预测入库洪峰：{plan['peak_inflow_m3s']:.1f} m3/s\n"
            f"- 建议闸门系数：{plan['gate_ratio']:.3f}\n"
        )
        return {"dispatch_order_text": text}

    return {
        "get_rainfall_forecast": get_rainfall_forecast,
        "get_inflow_forecast": get_inflow_forecast,
        "compute_dispatch_plan": compute_dispatch_plan,
        "generate_dispatch_order": generate_dispatch_order,
    }
