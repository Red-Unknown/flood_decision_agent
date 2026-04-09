"""真实数据Pipeline - 使用真实API和数据的Pipeline实现

此模块提供不依赖Mock数据的Pipeline实现，用于生产环境。
"""

import os
import sys
from typing import Any, Dict, List, Optional
from datetime import datetime

from loguru import logger

from flood_decision_agent.agents.decision_chain.generator import DecisionChainGeneratorAgent
from flood_decision_agent.agents.node_scheduler.scheduler import NodeSchedulerAgent
from flood_decision_agent.agents.task_executor.executor import UnitTaskExecutionAgent
from flood_decision_agent.agents.summarizer import SummarizerAgent
from flood_decision_agent.core.shared_data_pool import SharedDataPool
from flood_decision_agent.fusion.decision_fusion import DecisionFusion
from flood_decision_agent.tools.registry import get_tool_registry
from flood_decision_agent.application.services.data_acquisition.service import DataAcquisitionService
from flood_decision_agent.application.services.data_acquisition.clarification.manager import ClarificationManager
from flood_decision_agent.application.services.data_acquisition.defaults.provider import DefaultValueProvider


class RealPipelineResult:
    """真实Pipeline执行结果"""
    
    def __init__(
        self,
        success: bool,
        decision_chain: Optional[List[Dict]] = None,
        execution_results: Optional[List[Dict]] = None,
        summary: Optional[str] = None,
        data_pool_snapshot: Optional[Dict] = None,
        execution_time_ms: float = 0.0,
        errors: Optional[List[str]] = None,
    ):
        self.success = success
        self.decision_chain = decision_chain or []
        self.execution_results = execution_results or []
        self.summary = summary or ""
        self.data_pool_snapshot = data_pool_snapshot or {}
        self.execution_time_ms = execution_time_ms
        self.errors = errors or []
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "success": self.success,
            "decision_chain": self.decision_chain,
            "execution_results": self.execution_results,
            "summary": self.summary,
            "data_pool_snapshot": self.data_pool_snapshot,
            "execution_time_ms": self.execution_time_ms,
            "errors": self.errors,
        }


class RealPipeline:
    """真实数据Pipeline
    
    使用真实API和数据的Pipeline实现，不依赖Mock数据。
    """
    
    def __init__(
        self,
        enable_data_acquisition: bool = True,
        enable_clarification: bool = True,
    ):
        """初始化Pipeline
        
        Args:
            enable_data_acquisition: 是否启用数据获取服务
            enable_clarification: 是否启用渐进式澄清
        """
        # 检查API Key
        self.api_key = os.environ.get("KIMI_API_KEY")
        if not self.api_key:
            logger.error("需要kimi_api_key")
            sys.exit(1)
        
        logger.info("初始化真实数据Pipeline...")
        
        # 初始化数据获取服务
        self.data_service: Optional[DataAcquisitionService] = None
        self.clarification_manager: Optional[ClarificationManager] = None
        
        if enable_data_acquisition:
            self.data_service = DataAcquisitionService()
            default_provider = DefaultValueProvider()
            self.clarification_manager = ClarificationManager(
                self.data_service,
                default_provider
            )
            logger.info("数据获取服务已初始化")
        
        # 初始化Agent
        self._init_agents()
        
        logger.info("Pipeline初始化完成")
    
    def _init_agents(self) -> None:
        """初始化所有Agent"""
        # 决策链生成Agent
        self.chain_generator = DecisionChainGeneratorAgent()
        logger.info("决策链生成Agent已初始化")
        
        # 节点调度Agent
        self.node_scheduler = NodeSchedulerAgent()
        logger.info("节点调度Agent已初始化")
        
        # 任务执行Agent - 使用真实数据服务
        self.task_executor = UnitTaskExecutionAgent(
            data_acquisition_service=self.data_service,
            clarification_manager=self.clarification_manager,
        )
        logger.info("任务执行Agent已初始化")
        
        # 总结Agent
        self.summarizer = SummarizerAgent()
        logger.info("总结Agent已初始化")
    
    def run(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> RealPipelineResult:
        """运行Pipeline
        
        Args:
            user_input: 用户输入
            context: 上下文信息
            
        Returns:
            Pipeline执行结果
        """
        start_time = datetime.now()
        errors: List[str] = []
        
        try:
            logger.info(f"开始执行Pipeline，用户输入: {user_input[:100]}...")
            
            # Step 1: 生成决策链
            logger.info("Step 1: 生成决策链...")
            decision_chain = self._generate_decision_chain(user_input, context)
            if not decision_chain:
                errors.append("决策链生成失败")
                return RealPipelineResult(
                    success=False,
                    errors=errors,
                    execution_time_ms=self._calculate_execution_time(start_time),
                )
            logger.info(f"决策链生成完成，共 {len(decision_chain)} 个节点")
            
            # Step 2: 执行决策链
            logger.info("Step 2: 执行决策链...")
            execution_results = self._execute_decision_chain(decision_chain)
            logger.info(f"决策链执行完成，共 {len(execution_results)} 个结果")
            
            # Step 3: 生成总结
            logger.info("Step 3: 生成总结...")
            summary = self._generate_summary(user_input, execution_results)
            
            # 计算执行时间
            execution_time_ms = self._calculate_execution_time(start_time)
            
            return RealPipelineResult(
                success=True,
                decision_chain=decision_chain,
                execution_results=execution_results,
                summary=summary,
                execution_time_ms=execution_time_ms,
            )
            
        except Exception as e:
            logger.error(f"Pipeline执行失败: {e}")
            errors.append(str(e))
            return RealPipelineResult(
                success=False,
                errors=errors,
                execution_time_ms=self._calculate_execution_time(start_time),
            )
    
    def _generate_decision_chain(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """生成决策链
        
        Args:
            user_input: 用户输入
            context: 上下文
            
        Returns:
            决策链节点列表
        """
        # 使用决策链生成Agent
        from flood_decision_agent.core.message import BaseMessage, MessageType
        
        message = BaseMessage(
            type=MessageType.TASK_REQUEST,
            payload={
                "input": user_input,
                "input_type": "natural_language",
                "context": context or {},
            },
            sender="Pipeline",
            receiver="DecisionChainGenerator",
        )
        
        result = self.chain_generator.execute(message)
        
        if result and isinstance(result, BaseMessage):
            # 从消息payload中提取task_graph
            payload = result.payload
            if "task_graph" in payload:
                task_graph = payload["task_graph"]
                # 将TaskGraph转换为节点列表
                # TaskGraph使用_nodes字典存储节点
                if hasattr(task_graph, '_nodes'):
                    return [
                        {
                            "node_id": node.node_id,
                            "task_type": node.task_type,
                            "context": {},
                        }
                        for node in task_graph._nodes.values()
                    ]
        return []
    
    def _execute_decision_chain(
        self,
        decision_chain: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """执行决策链
        
        Args:
            decision_chain: 决策链节点列表
            
        Returns:
            执行结果列表
        """
        results = []
        
        # 创建共享数据池
        data_pool = SharedDataPool()
        
        # 逐个执行节点
        for i, node_info in enumerate(decision_chain):
            node_id = node_info.get("node_id", f"node_{i}")
            task_type = node_info.get("task_type", "default")
            
            logger.info(f"执行节点 {node_id} (类型: {task_type})")
            
            try:
                # 使用节点调度Agent执行
                from flood_decision_agent.core.message import BaseMessage, MessageType
                from flood_decision_agent.core.task_graph import Node
                
                # 创建Node对象
                node = Node(
                    node_id=node_id,
                    task_type=task_type,
                )
                
                # 发送符合NodeScheduler期望的消息格式
                message = BaseMessage(
                    type=MessageType.NODE_EXECUTE,
                    payload={
                        "node": node,
                        "data_pool": data_pool,
                    },
                    sender="Pipeline",
                    receiver="NodeScheduler",
                )
                
                result = self.node_scheduler.execute(message)
                
                if result:
                    results.append({
                        "node_id": node_id,
                        "task_type": task_type,
                        "status": "success",
                        "result": result,
                    })
                    
                    # 将结果存入数据池
                    if isinstance(result, dict) and "output" in result:
                        data_pool.set(f"{node_id}_output", result["output"])
                else:
                    results.append({
                        "node_id": node_id,
                        "task_type": task_type,
                        "status": "failed",
                        "error": "执行返回空结果",
                    })
                    
            except Exception as e:
                logger.error(f"节点 {node_id} 执行失败: {e}")
                import traceback
                traceback.print_exc()
                results.append({
                    "node_id": node_id,
                    "task_type": task_type,
                    "status": "failed",
                    "error": str(e),
                })
        
        return results
    
    def _generate_summary(
        self,
        user_input: str,
        execution_results: List[Dict[str, Any]],
    ) -> str:
        """生成执行总结
        
        Args:
            user_input: 用户输入
            execution_results: 执行结果列表
            
        Returns:
            总结文本
        """
        # 使用总结Agent
        from flood_decision_agent.core.message import BaseMessage, MessageType
        
        message = BaseMessage(
            type=MessageType.TASK_REQUEST,
            payload={
                "user_input": user_input,
                "execution_results": execution_results,
            },
            sender="Pipeline",
            receiver="Summarizer",
        )
        
        result = self.summarizer.execute(message)
        
        if result and "summary" in result:
            return result["summary"]
        
        # 默认总结
        success_count = sum(1 for r in execution_results if r.get("status") == "success")
        total_count = len(execution_results)
        return f"执行完成: {success_count}/{total_count} 个节点成功"
    
    def _calculate_execution_time(self, start_time: datetime) -> float:
        """计算执行时间
        
        Args:
            start_time: 开始时间
            
        Returns:
            执行时间（毫秒）
        """
        end_time = datetime.now()
        return (end_time - start_time).total_seconds() * 1000


def run_real_pipeline(
    user_input: str,
    context: Optional[Dict[str, Any]] = None,
) -> RealPipelineResult:
    """便捷函数：运行真实数据Pipeline
    
    Args:
        user_input: 用户输入
        context: 上下文信息
        
    Returns:
        Pipeline执行结果
    """
    pipeline = RealPipeline()
    return pipeline.run(user_input, context)


if __name__ == "__main__":
    # 测试Pipeline
    test_input = "分析未来3天的降雨情况并给出调度建议"
    result = run_real_pipeline(test_input)
    
    print("\n" + "="*60)
    print("Pipeline执行结果")
    print("="*60)
    print(f"成功: {result.success}")
    print(f"执行时间: {result.execution_time_ms:.2f} ms")
    print(f"决策链节点数: {len(result.decision_chain)}")
    print(f"执行结果数: {len(result.execution_results)}")
    print(f"\n总结:\n{result.summary}")
    
    if result.errors:
        print(f"\n错误:\n" + "\n".join(result.errors))
