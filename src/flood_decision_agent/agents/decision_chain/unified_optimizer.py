"""统一链路优化器

合并 SimpleOptimizer、PlanOptimizer、SpecOptimizer 的功能，
接入 LLM 提示词进行智能优化。

支持三种优化策略：
- simple: 轻量级优化，1个备选链，可靠性阈值0.6
- plan: Plan模式优化，3个备选链，可靠性阈值0.75，2次迭代
- spec: Spec模式优化，6个备选链，可靠性阈值0.85，3次迭代
"""

from __future__ import annotations

import os
import yaml
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field

from flood_decision_agent.agents.decision_chain.task_decomposer import TaskNodeInfo, TaskType
from flood_decision_agent.agents.prompts import ChainGenerationPrompts
from flood_decision_agent.infrastructure.llm.kimi_client import KimiClient
from flood_decision_agent.infra.logging import get_logger


@dataclass
class AlternativeChain:
    """备选链数据类"""
    chain_id: str
    strategy: str
    nodes: List[TaskNodeInfo]
    reliability_score: float = 0.0
    optimization_info: Dict[str, Any] = field(default_factory=dict)


class UnifiedOptimizer:
    """统一链路优化器

    根据策略类型（simple/plan/spec）执行不同级别的优化：
    - 动态调整备选链数量
    - 使用LLM进行迭代优化
    - 生成符合TaskNodeInfo格式的任务链
    """

    # 优化策略配置（与ChainGenerationPrompts保持一致）
    STRATEGIES = {
        "simple": {
            "name": "轻量级优化",
            "alternatives": 1,
            "reliability_threshold": 0.6,
            "iterations": 0,
            "description": "快速响应，1个备用链路，无迭代优化",
        },
        "plan": {
            "name": "Plan模式优化",
            "alternatives": 3,
            "reliability_threshold": 0.75,
            "iterations": 2,
            "description": "平衡质量和速度，3个备选方案，2次迭代",
        },
        "spec": {
            "name": "Spec模式优化",
            "alternatives": 6,
            "reliability_threshold": 0.85,
            "iterations": 3,
            "description": "确保功能完善，6个备选方案，3次迭代",
        },
    }

    def __init__(
        self,
        strategy: str = "plan",
        api_key: Optional[str] = None,
    ):
        """初始化统一优化器

        Args:
            strategy: 优化策略（simple/plan/spec）
            api_key: API Key（可选，默认从环境变量读取）
        """
        self.strategy_name = strategy
        self.strategy = self.STRATEGIES.get(strategy, self.STRATEGIES["plan"])
        self.api_key = api_key or os.environ.get("KIMI_API_KEY")
        self._logger = get_logger().bind(name=f"UnifiedOptimizer[{strategy}]")
        
        # 初始化LLM客户端
        self._llm_client = None
        if self.api_key:
            try:
                self._llm_client = KimiClient(api_key=self.api_key)
                self._logger.info("LLM客户端初始化成功")
            except Exception as e:
                self._logger.warning(f"LLM客户端初始化失败: {e}，将使用规则库优化")

    def optimize(
        self,
        task_nodes: List[TaskNodeInfo],
        user_input: str = "",
        business_type: str = "flood_warning",
        execution_type: str = "chain",
        entities: Optional[Dict[str, Any]] = None,
        mcp_tools: Optional[List[Dict[str, Any]]] = None,
        available_tools: Optional[Set[str]] = None,
    ) -> Dict[str, Any]:
        """执行统一优化

        Args:
            task_nodes: 初始任务节点列表（来自规则库）
            user_input: 用户输入
            business_type: 业务类型
            execution_type: 执行类型
            entities: 提取的实体
            mcp_tools: 可用的MCP工具
            available_tools: 可用工具集合（用于可靠性评估）

        Returns:
            优化结果字典
        """
        self._logger.info(
            f"开始{self.strategy['name']}: "
            f"备选链={self.strategy['alternatives']}, "
            f"阈值={self.strategy['reliability_threshold']}, "
            f"迭代={self.strategy['iterations']}"
        )

        if not task_nodes:
            return self._empty_result("任务节点列表为空")

        # 1. 使用LLM生成/优化决策链（如果LLM可用）
        if self._llm_client and self.strategy["iterations"] > 0:
            llm_result = self._optimize_with_llm(
                task_nodes=task_nodes,
                user_input=user_input,
                business_type=business_type,
                execution_type=execution_type,
                entities=entities or {},
                mcp_tools=mcp_tools or [],
            )
            if llm_result:
                return llm_result

        # 2. 回退到规则库优化
        return self._optimize_with_rules(
            task_nodes=task_nodes,
            available_tools=available_tools,
        )

    def _optimize_with_llm(
        self,
        task_nodes: List[TaskNodeInfo],
        user_input: str,
        business_type: str,
        execution_type: str,
        entities: Dict[str, Any],
        mcp_tools: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """使用LLM进行优化

        Args:
            task_nodes: 规则库生成的任务节点
            user_input: 用户输入
            business_type: 业务类型
            execution_type: 执行类型
            entities: 实体
            mcp_tools: MCP工具

        Returns:
            优化结果，失败返回None
        """
        try:
            # 转换任务节点为YAML格式
            rule_based_tasks = self._tasks_to_yaml(task_nodes)

            # 生成提示词
            prompt = ChainGenerationPrompts.get_chain_generation_prompt(
                user_input=user_input,
                business_type=business_type,
                execution_type=execution_type,
                entities=entities,
                mcp_tools=mcp_tools,
                optimizer_strategy=self.strategy_name,
                rule_based_tasks=rule_based_tasks,
            )

            # 调用LLM
            self._logger.info("调用LLM生成决策链...")
            response = self._llm_client.complete(
                prompt=prompt,
                system_message=ChainGenerationPrompts.CHAIN_GENERATION_SYSTEM,
                temperature=0.7,
                max_tokens=6000,
            )

            # 解析YAML响应
            chain_data = self._parse_yaml_response(response)
            if not chain_data:
                self._logger.warning("LLM响应解析失败，回退到规则库")
                return None

            self._logger.debug(f"解析后的chain_data类型: {type(chain_data)}, 键: {list(chain_data.keys()) if isinstance(chain_data, dict) else 'N/A'}")

            # 获取chain部分（LLM可能返回整个文档或仅chain部分）
            if "chain" in chain_data:
                chain_root = chain_data["chain"]
                self._logger.debug("使用chain_data['chain']作为根")
            else:
                chain_root = chain_data
                self._logger.debug("使用chain_data作为根")

            self._logger.debug(f"chain_root类型: {type(chain_root)}, 键: {list(chain_root.keys()) if isinstance(chain_root, dict) else 'N/A'}")

            # 获取primary tasks
            primary_section = chain_root.get("primary", {})
            if isinstance(primary_section, dict):
                primary_tasks = primary_section.get("tasks", [])
            else:
                primary_tasks = chain_root.get("tasks", [])
            
            self._logger.debug(f"主链任务数: {len(primary_tasks)}")

            # 转换为TaskNodeInfo
            primary_nodes = self._yaml_to_tasks(primary_tasks)
            
            # 获取alternatives
            alternatives_data = chain_root.get("alternatives", [])
            self._logger.debug(f"备选链数量: {len(alternatives_data)}")
            
            # 生成备选链
            alternatives = []
            for alt_data in alternatives_data[:self.strategy["alternatives"]]:
                alt_nodes = self._yaml_to_tasks(alt_data.get("tasks", []))
                alternatives.append(AlternativeChain(
                    chain_id=alt_data.get("name", "unknown"),
                    strategy=alt_data.get("strategy", "default"),
                    nodes=alt_nodes,
                    reliability_score=0.0,  # 稍后评估
                ))

            # 评估可靠性
            for alt in alternatives:
                score, issues, _ = self._evaluate_reliability(alt.nodes)
                alt.reliability_score = score
                alt.optimization_info["issues"] = issues

            # 迭代优化（如果配置）
            if self.strategy["iterations"] > 0:
                alternatives = self._iterate_optimization(
                    alternatives,
                    self.strategy["iterations"],
                )

            # 选择最佳链
            best_alt = max(alternatives, key=lambda x: x.reliability_score) if alternatives else None

            passed = best_alt and best_alt.reliability_score >= self.strategy["reliability_threshold"]

            self._logger.info(
                f"LLM优化完成: 生成{len(alternatives)}个备选链, "
                f"最佳可靠性={best_alt.reliability_score if best_alt else 0:.2f}, "
                f"通过={passed}"
            )

            return {
                "original_nodes": task_nodes,
                "primary_nodes": primary_nodes,
                "alternatives": alternatives,
                "best_alternative": best_alt,
                "reliability_score": best_alt.reliability_score if best_alt else 0.0,
                "issues": best_alt.optimization_info.get("issues", []) if best_alt else [],
                "passed": passed,
                "iterations": self.strategy["iterations"],
                "strategy": self.strategy_name,
                "source": "llm",
            }

        except Exception as e:
            self._logger.error(f"LLM优化失败: {e}")
            return None

    def _optimize_with_rules(
        self,
        task_nodes: List[TaskNodeInfo],
        available_tools: Optional[Set[str]] = None,
    ) -> Dict[str, Any]:
        """使用规则库进行优化

        Args:
            task_nodes: 任务节点
            available_tools: 可用工具

        Returns:
            优化结果
        """
        self._logger.info("使用规则库优化...")

        # 生成简单的备选链（修改部分参数）
        alternatives = []
        strategies = ["default", "conservative", "fast"]
        
        for i in range(min(self.strategy["alternatives"], len(strategies))):
            # 复制原始节点
            alt_nodes = self._copy_nodes(task_nodes)
            
            # 应用策略修改
            if strategies[i] == "conservative":
                # 保守策略：增加安全检查
                for node in alt_nodes:
                    if node.task_type == TaskType.EXECUTION:
                        node.metadata["safety_check"] = True
            elif strategies[i] == "fast":
                # 快速策略：减少预估时间
                for node in alt_nodes:
                    node.metadata["fast_mode"] = True

            alternatives.append(AlternativeChain(
                chain_id=f"{self.strategy_name}_alt_{i+1}",
                strategy=strategies[i],
                nodes=alt_nodes,
            ))

        # 评估可靠性
        for alt in alternatives:
            score, issues, _ = self._evaluate_reliability(alt.nodes, available_tools)
            alt.reliability_score = score
            alt.optimization_info["issues"] = issues

        # 选择最佳链
        best_alt = max(alternatives, key=lambda x: x.reliability_score) if alternatives else None
        passed = best_alt and best_alt.reliability_score >= self.strategy["reliability_threshold"]

        self._logger.info(
            f"规则库优化完成: 生成{len(alternatives)}个备选链, "
            f"最佳可靠性={best_alt.reliability_score if best_alt else 0:.2f}"
        )

        return {
            "original_nodes": task_nodes,
            "alternatives": alternatives,
            "best_alternative": best_alt,
            "reliability_score": best_alt.reliability_score if best_alt else 0.0,
            "issues": best_alt.optimization_info.get("issues", []) if best_alt else [],
            "passed": passed,
            "iterations": 0,
            "strategy": self.strategy_name,
            "source": "rules",
        }

    def _iterate_optimization(
        self,
        alternatives: List[AlternativeChain],
        max_iterations: int,
    ) -> List[AlternativeChain]:
        """迭代优化备选链

        Args:
            alternatives: 备选链列表
            max_iterations: 最大迭代次数

        Returns:
            优化后的备选链
        """
        if not self._llm_client or max_iterations <= 0:
            return alternatives

        for iteration in range(1, max_iterations + 1):
            self._logger.info(f"第{iteration}/{max_iterations}次迭代优化...")

            for alt in alternatives:
                issues = alt.optimization_info.get("issues", [])
                if not issues:
                    continue

                # 生成优化提示词
                current_chain = self._chain_to_yaml(alt)
                prompt = ChainGenerationPrompts.get_chain_optimization_prompt(
                    current_chain=current_chain,
                    issues=issues,
                    iteration=iteration,
                    max_iterations=max_iterations,
                )

                try:
                    response = self._llm_client.complete(
                        prompt=prompt,
                        system_message=ChainGenerationPrompts.CHAIN_GENERATION_SYSTEM,
                        temperature=0.5,
                        max_tokens=4000,
                    )

                    # 解析优化后的链
                    optimized_data = self._parse_yaml_response(response)
                    if optimized_data:
                        # 获取tasks（新的提示词格式直接返回tasks列表）
                        tasks_data = optimized_data.get("tasks", [])
                        if tasks_data:
                            # 更新节点
                            alt.nodes = self._yaml_to_tasks(tasks_data)
                            # 重新评估
                            score, new_issues, _ = self._evaluate_reliability(alt.nodes)
                            alt.reliability_score = score
                            alt.optimization_info["issues"] = new_issues
                            alt.optimization_info[f"iteration_{iteration}"] = "optimized"
                            
                            # 记录优化信息
                            opt_info = optimized_data.get("optimization", {})
                            if opt_info:
                                alt.optimization_info[f"changes_{iteration}"] = opt_info.get("changes", [])
                                alt.optimization_info[f"improvement_{iteration}"] = opt_info.get("improvement", "")
                                
                            self._logger.debug(f"迭代{iteration}优化成功，新可靠性评分: {score:.2f}")
                        else:
                            self._logger.warning(f"迭代{iteration}返回的tasks为空，跳过更新")

                except Exception as e:
                    self._logger.warning(f"迭代优化失败: {e}")
                    continue

        return alternatives

    def _evaluate_reliability(
        self,
        task_nodes: List[TaskNodeInfo],
        available_tools: Optional[Set[str]] = None,
    ) -> Tuple[float, List[str], Dict[str, Any]]:
        """评估链路可靠性

        Args:
            task_nodes: 任务节点
            available_tools: 可用工具

        Returns:
            (可靠性评分, 问题列表, 详细信息)
        """
        if not task_nodes:
            return 0.0, ["任务节点为空"], {}

        issues = []
        details = {
            "node_count": len(task_nodes),
            "dependency_check": True,
            "tool_availability": True,
        }

        # 1. 检查依赖关系
        task_ids = {node.task_id for node in task_nodes}
        for node in task_nodes:
            for dep in node.dependencies:
                if dep not in task_ids:
                    issues.append(f"任务{node.task_id}依赖{dep}不存在")
                    details["dependency_check"] = False

        # 2. 检查工具可用性
        if available_tools:
            for node in task_nodes:
                tool = node.metadata.get("tool")
                if tool and tool not in available_tools:
                    issues.append(f"任务{node.task_id}依赖工具{tool}不可用")
                    details["tool_availability"] = False

        # 3. 检查数据流完整性
        all_outputs = set()
        for node in task_nodes:
            all_outputs.update(node.outputs)

        for node in task_nodes:
            for input_key in node.inputs:
                if input_key not in all_outputs and not any(
                    input_key in n.outputs for n in task_nodes if n.task_id in node.dependencies
                ):
                    issues.append(f"任务{node.task_id}输入{input_key}来源不明确")

        # 计算评分
        base_score = 1.0
        issue_penalty = len(issues) * 0.1
        score = max(0.0, base_score - issue_penalty)

        return score, issues, details

    def _tasks_to_yaml(self, task_nodes: List[TaskNodeInfo]) -> List[Dict[str, Any]]:
        """将TaskNodeInfo转换为YAML格式"""
        return [
            {
                "task_id": node.task_id,
                "task_type": node.task_type.value,
                "description": node.description,
                "inputs": node.inputs,
                "outputs": node.outputs,
                "dependencies": node.dependencies,
                "metadata": node.metadata,
            }
            for node in task_nodes
        ]

    def _yaml_to_tasks(self, yaml_tasks: List[Dict[str, Any]]) -> List[TaskNodeInfo]:
        """将YAML格式转换为TaskNodeInfo"""
        nodes = []
        for task in yaml_tasks:
            try:
                node = TaskNodeInfo(
                    task_id=task["task_id"],
                    task_type=TaskType(task["task_type"]),
                    description=task.get("description", ""),
                    inputs=task.get("inputs", []),
                    outputs=task.get("outputs", []),
                    dependencies=task.get("dependencies", []),
                    metadata=task.get("metadata", {}),
                )
                nodes.append(node)
            except Exception as e:
                self._logger.warning(f"转换任务失败: {e}")
                continue
        return nodes

    def _parse_yaml_response(self, response: str) -> Optional[Dict[str, Any]]:
        """解析LLM的YAML响应"""
        try:
            # 提取YAML内容
            if "```yaml" in response:
                yaml_content = response.split("```yaml")[1].split("```")[0]
            elif "```" in response:
                yaml_content = response.split("```")[1].split("```")[0]
            else:
                yaml_content = response

            return yaml.safe_load(yaml_content)
        except Exception as e:
            self._logger.error(f"YAML解析失败: {e}")
            return None

    def _chain_to_yaml(self, chain: AlternativeChain) -> Dict[str, Any]:
        """将备选链转换为YAML格式"""
        return {
            "name": chain.chain_id,
            "strategy": chain.strategy,
            "tasks": self._tasks_to_yaml(chain.nodes),
            "reliability_score": chain.reliability_score,
        }

    def _copy_nodes(self, task_nodes: List[TaskNodeInfo]) -> List[TaskNodeInfo]:
        """复制任务节点"""
        return [
            TaskNodeInfo(
                task_id=node.task_id,
                task_type=node.task_type,
                description=node.description,
                inputs=node.inputs.copy(),
                outputs=node.outputs.copy(),
                dependencies=node.dependencies.copy(),
                metadata=node.metadata.copy(),
            )
            for node in task_nodes
        ]

    def _empty_result(self, reason: str) -> Dict[str, Any]:
        """返回空结果"""
        return {
            "original_nodes": [],
            "alternatives": [],
            "best_alternative": None,
            "reliability_score": 0.0,
            "issues": [reason],
            "passed": False,
            "iterations": 0,
            "strategy": self.strategy_name,
            "source": "none",
        }

    def quick_evaluate(
        self,
        task_nodes: List[TaskNodeInfo],
        available_tools: Optional[Set[str]] = None,
    ) -> Tuple[float, List[str]]:
        """快速评估"""
        score, issues, _ = self._evaluate_reliability(task_nodes, available_tools)
        return score, issues

    def is_reliable(
        self,
        task_nodes: List[TaskNodeInfo],
        available_tools: Optional[Set[str]] = None,
    ) -> bool:
        """检查是否可靠"""
        score, _ = self.quick_evaluate(task_nodes, available_tools)
        return score >= self.strategy["reliability_threshold"]

    def get_strategy_info(self) -> Dict[str, Any]:
        """获取策略信息"""
        return {
            "name": self.strategy_name,
            **self.strategy,
            "llm_enabled": self._llm_client is not None,
        }


# 向后兼容的别名
SimpleOptimizer = UnifiedOptimizer
PlanOptimizer = UnifiedOptimizer

# 导出
__all__ = [
    "UnifiedOptimizer",
    "AlternativeChain",
    "SimpleOptimizer",
    "PlanOptimizer",
]
