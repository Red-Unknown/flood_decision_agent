"""Agent 相关异常"""
from .base import FloodDecisionAgentError


class AgentError(FloodDecisionAgentError):
    """Agent 基础异常"""
    
    def __init__(self, message: str, code: str = "AGENT_ERROR", details: dict = None):
        super().__init__(message, code, details)


class TaskExecutionError(AgentError):
    """任务执行异常"""
    
    def __init__(self, message: str, task_id: str = None, details: dict = None):
        super().__init__(
            message,
            code="TASK_EXECUTION_ERROR",
            details={"task_id": task_id, **(details or {})}
        )
        self.task_id = task_id


class DecisionChainError(AgentError):
    """决策链异常"""
    
    def __init__(self, message: str, chain_id: str = None, details: dict = None):
        super().__init__(
            message,
            code="DECISION_CHAIN_ERROR",
            details={"chain_id": chain_id, **(details or {})}
        )
        self.chain_id = chain_id
