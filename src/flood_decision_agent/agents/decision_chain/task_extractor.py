"""
任务提取器 - 从 Plan/Spec 文档中提取任务

提供 TaskExtractor 类，用于从规划文档或规格文档中提取可执行的任务列表。
支持多种文档格式和任务提取策略。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from flood_decision_agent.agents.decision_chain.task_decomposer import TaskNodeInfo, TaskType
from flood_decision_agent.infrastructure.logging import get_logger


class DocumentType(str, Enum):
    """文档类型"""
    PLAN = "plan"
    SPEC = "spec"
    UNKNOWN = "unknown"


class ExtractionStrategy(str, Enum):
    """提取策略"""
    REGEX = "regex"           # 正则表达式提取
    STRUCTURED = "structured" # 结构化提取（Markdown）
    LLM_BASED = "llm_based"   # 基于 LLM 的智能提取


@dataclass
class ExtractedTask:
    """提取的任务"""
    name: str
    description: str
    task_type: TaskType
    dependencies: List[str] = field(default_factory=list)
    deliverables: str = ""
    responsible: str = ""
    estimated_time: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractionResult:
    """提取结果"""
    tasks: List[ExtractedTask]
    document_type: DocumentType
    strategy: ExtractionStrategy
    success: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class TaskExtractor:
    """任务提取器
    
    从 Plan/Spec 文档中提取可执行的任务列表。
    支持多种提取策略，自动选择最适合的策略。
    
    Example:
        ```python
        extractor = TaskExtractor()
        
        # 从 Plan 文档提取任务
        result = extractor.extract_from_document(plan_document, DocumentType.PLAN)
        
        if result.success:
            for task in result.tasks:
                print(f"任务: {task.name}, 类型: {task.task_type}")
        ```
    """

    def __init__(self, default_strategy: ExtractionStrategy = ExtractionStrategy.STRUCTURED):
        """初始化任务提取器
        
        Args:
            default_strategy: 默认提取策略
        """
        self._logger = get_logger().bind(name=self.__class__.__name__)
        self._default_strategy = default_strategy

    def extract_from_document(
        self,
        document: str,
        document_type: DocumentType = DocumentType.PLAN,
        strategy: Optional[ExtractionStrategy] = None,
    ) -> ExtractionResult:
        """从文档中提取任务
        
        Args:
            document: 文档内容
            document_type: 文档类型
            strategy: 提取策略，None 时使用默认策略
            
        Returns:
            ExtractionResult: 提取结果
        """
        strategy = strategy or self._default_strategy
        
        self._logger.info(f"开始从 {document_type.value} 文档提取任务，策略: {strategy.value}")
        
        try:
            if strategy == ExtractionStrategy.REGEX:
                tasks = self._extract_by_regex(document)
            elif strategy == ExtractionStrategy.STRUCTURED:
                tasks = self._extract_by_structure(document)
            elif strategy == ExtractionStrategy.LLM_BASED:
                tasks = self._extract_by_llm(document, document_type)
            else:
                raise ValueError(f"未知的提取策略: {strategy}")
            
            if not tasks:
                self._logger.warning("未提取到任何任务")
                return ExtractionResult(
                    tasks=[],
                    document_type=document_type,
                    strategy=strategy,
                    success=False,
                    error_message="未提取到任何任务",
                )
            
            self._logger.info(f"成功提取 {len(tasks)} 个任务")
            
            return ExtractionResult(
                tasks=tasks,
                document_type=document_type,
                strategy=strategy,
                success=True,
                metadata={
                    "task_count": len(tasks),
                    "document_length": len(document),
                },
            )
            
        except Exception as e:
            error_msg = str(e)
            self._logger.error(f"任务提取失败: {error_msg}")
            return ExtractionResult(
                tasks=[],
                document_type=document_type,
                strategy=strategy,
                success=False,
                error_message=error_msg,
            )

    def extract_from_plan(self, plan_document: str) -> ExtractionResult:
        """从 Plan 文档中提取任务
        
        Args:
            plan_document: Plan 文档内容
            
        Returns:
            ExtractionResult: 提取结果
        """
        return self.extract_from_document(plan_document, DocumentType.PLAN)

    def extract_from_spec(self, spec_document: str) -> ExtractionResult:
        """从 Spec 文档中提取任务
        
        Args:
            spec_document: Spec 文档内容
            
        Returns:
            ExtractionResult: 提取结果
        """
        return self.extract_from_document(spec_document, DocumentType.SPEC)

    def _extract_by_structure(self, document: str) -> List[ExtractedTask]:
        """通过文档结构提取任务（Markdown 格式）
        
        支持以下格式：
        1. 数字列表格式：1. **任务名称**（预计耗时）
        2. 标题格式：### 任务名称
        3. 表格格式：| 序号 | 任务名称 | ... |
        
        Args:
            document: 文档内容
            
        Returns:
            List[ExtractedTask]: 提取的任务列表
        """
        tasks = []
        lines = document.split("\n")
        
        # 尝试数字列表格式
        tasks.extend(self._extract_numbered_list(lines))
        
        # 如果没有提取到，尝试标题格式
        if not tasks:
            tasks.extend(self._extract_from_headings(lines))
        
        # 如果还是没有，尝试表格格式
        if not tasks:
            tasks.extend(self._extract_from_table(lines))
        
        return tasks

    def _extract_numbered_list(self, lines: List[str]) -> List[ExtractedTask]:
        """从数字列表中提取任务
        
        格式示例：
        1. **需求分析**（预计耗时：2天）
           - 具体内容：分析用户需求
           - 交付物：需求文档
           - 负责人：产品经理
        """
        tasks = []
        current_task: Optional[ExtractedTask] = None
        
        # 匹配任务标题：1. **任务名称**（预计耗时）
        task_pattern = re.compile(r"^(\d+)\.\s*\*\*(.+?)\*\*\s*(?:\((.+?)\))?")
        
        for line in lines:
            line = line.strip()
            
            # 尝试匹配任务标题
            match = task_pattern.match(line)
            if match:
                # 保存上一个任务
                if current_task:
                    tasks.append(current_task)
                
                task_name = match.group(2).strip()
                estimated_time = match.group(3) if match.group(3) else ""
                
                current_task = ExtractedTask(
                    name=task_name,
                    description="",
                    task_type=self._infer_task_type(task_name, ""),
                    estimated_time=estimated_time,
                )
            
            # 匹配任务详情
            elif current_task and line.startswith("-"):
                if "具体内容" in line or "描述" in line:
                    current_task.description = line.split("：", 1)[-1].strip()
                elif "交付物" in line:
                    current_task.deliverables = line.split("：", 1)[-1].strip()
                elif "负责人" in line:
                    current_task.responsible = line.split("：", 1)[-1].strip()
                elif "依赖" in line:
                    deps = line.split("：", 1)[-1].strip()
                    current_task.dependencies = [d.strip() for d in deps.split(",") if d.strip()]
        
        # 添加最后一个任务
        if current_task:
            tasks.append(current_task)
        
        return tasks

    def _extract_from_headings(self, lines: List[str]) -> List[ExtractedTask]:
        """从标题中提取任务
        
        格式示例：
        ### 1. 需求分析
        
        描述：分析用户需求
        
        交付物：需求文档
        """
        tasks = []
        current_task: Optional[ExtractedTask] = None
        current_section: Optional[str] = None
        
        # 匹配标题：### 1. 任务名称 或 ## 任务名称
        heading_pattern = re.compile(r"^#{2,4}\s*(?:\d+\.\s*)?(.+)$")
        
        for line in lines:
            line = line.strip()
            
            # 尝试匹配标题
            match = heading_pattern.match(line)
            if match:
                # 保存上一个任务
                if current_task:
                    tasks.append(current_task)
                
                task_name = match.group(1).strip()
                current_task = ExtractedTask(
                    name=task_name,
                    description="",
                    task_type=self._infer_task_type(task_name, ""),
                )
                current_section = None
            
            # 匹配任务详情
            elif current_task:
                if line.startswith("描述") or line.startswith("说明"):
                    current_section = "description"
                    current_task.description = line.split("：", 1)[-1].strip()
                elif line.startswith("交付物"):
                    current_section = "deliverables"
                    current_task.deliverables = line.split("：", 1)[-1].strip()
                elif line.startswith("负责人"):
                    current_section = "responsible"
                    current_task.responsible = line.split("：", 1)[-1].strip()
                elif line.startswith("依赖"):
                    deps = line.split("：", 1)[-1].strip()
                    current_task.dependencies = [d.strip() for d in deps.split(",") if d.strip()]
                elif line and current_section == "description":
                    # 继续追加描述
                    current_task.description += " " + line
        
        # 添加最后一个任务
        if current_task:
            tasks.append(current_task)
        
        return tasks

    def _extract_from_table(self, lines: List[str]) -> List[ExtractedTask]:
        """从表格中提取任务
        
        格式示例：
        | 序号 | 任务名称 | 描述 | 交付物 | 负责人 |
        |------|----------|------|--------|--------|
        | 1 | 需求分析 | 分析需求 | 文档 | 产品经理 |
        """
        tasks = []
        in_table = False
        headers: List[str] = []
        
        for line in lines:
            line = line.strip()
            
            # 检测表格开始
            if "|" in line and not in_table:
                headers = [h.strip() for h in line.split("|") if h.strip()]
                in_table = True
                continue
            
            # 跳过表格分隔符行
            if in_table and ("---" in line or "====" in line):
                continue
            
            # 解析表格行
            if in_table and "|" in line:
                cells = [c.strip() for c in line.split("|") if c.strip()]
                if len(cells) >= 2 and cells[0] not in headers:
                    # 创建任务
                    task_data = dict(zip(headers, cells))
                    
                    task = ExtractedTask(
                        name=task_data.get("任务名称", task_data.get("名称", "未命名任务")),
                        description=task_data.get("描述", task_data.get("说明", "")),
                        task_type=self._infer_task_type(
                            task_data.get("任务名称", ""),
                            task_data.get("描述", "")
                        ),
                        deliverables=task_data.get("交付物", ""),
                        responsible=task_data.get("负责人", ""),
                    )
                    tasks.append(task)
            
            # 检测表格结束
            elif in_table and not line:
                in_table = False
        
        return tasks

    def _extract_by_regex(self, document: str) -> List[ExtractedTask]:
        """通过正则表达式提取任务
        
        Args:
            document: 文档内容
            
        Returns:
            List[ExtractedTask]: 提取的任务列表
        """
        tasks = []
        
        # 匹配任务模式：任务名称 + 描述
        # 支持多种格式：- 任务名称：描述 / 1. 任务名称 - 描述 / * 任务名称：描述
        patterns = [
            # 格式：- 任务名称：描述
            r"[-*]\s*(.+?)[:：]\s*(.+?)(?=\n[-*]|\n\d+\.|$)",
            # 格式：1. 任务名称 - 描述
            r"\d+\.\s*(.+?)[-\-]\s*(.+?)(?=\n\d+\.|\n[-*]|$)",
            # 格式：【任务名称】描述
            r"【(.+?)】\s*(.+?)(?=\n【|\n[-*]|\n\d+\.|$)",
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, document, re.DOTALL)
            for match in matches:
                task_name = match.group(1).strip()
                description = match.group(2).strip()
                
                task = ExtractedTask(
                    name=task_name,
                    description=description,
                    task_type=self._infer_task_type(task_name, description),
                )
                tasks.append(task)
            
            # 如果已经提取到任务，不再尝试其他模式
            if tasks:
                break
        
        return tasks

    def _extract_by_llm(self, document: str, document_type: DocumentType) -> List[ExtractedTask]:
        """通过 LLM 智能提取任务
        
        当结构化提取失败时，使用 LLM 进行智能提取。
        
        Args:
            document: 文档内容
            document_type: 文档类型
            
        Returns:
            List[ExtractedTask]: 提取的任务列表
        """
        # TODO: 实现基于 LLM 的任务提取
        # 目前回退到结构化提取
        self._logger.warning("LLM 提取尚未实现，回退到结构化提取")
        return self._extract_by_structure(document)

    def _infer_task_type(self, task_name: str, task_description: str) -> TaskType:
        """推断任务类型
        
        根据任务名称和描述中的关键词推断任务类型。
        
        Args:
            task_name: 任务名称
            task_description: 任务描述
            
        Returns:
            TaskType: 推断的任务类型
        """
        text = (task_name + " " + task_description).lower()
        
        # 关键词映射（只使用 TaskType 中定义的类型）
        keyword_mapping = {
            TaskType.DATA_COLLECTION: ["数据", "采集", "接入", "获取", "收集", "同步", "处理", "清洗", "转换", "加工", "预处理"],
            TaskType.PREDICTION: ["预测", "预报", "模型", "训练", "算法", "AI", "机器学习", "模拟", "仿真", "演练", "推演"],
            TaskType.CALCULATION: ["计算", "分析", "评估", "统计", "核算", "优化", "调优", "改进", "提升"],
            TaskType.DECISION: ["决策", "方案", "调度", "规划", "计划"],
            TaskType.EXECUTION: ["执行", "实施", "开发", "实现", "编码", "部署", "报告", "文档", "汇总", "总结", "汇报"],
            TaskType.VERIFICATION: ["测试", "验证", "检验", "检查", "验收", "评审"],
        }
        
        # 匹配关键词
        for task_type, keywords in keyword_mapping.items():
            if any(kw in text for kw in keywords):
                return task_type
        
        # 默认返回 EXECUTION
        return TaskType.EXECUTION

    def convert_to_task_nodes(self, extracted_tasks: List[ExtractedTask]) -> List[TaskNodeInfo]:
        """将提取的任务转换为 TaskNodeInfo 列表
        
        Args:
            extracted_tasks: 提取的任务列表
            
        Returns:
            List[TaskNodeInfo]: 任务节点列表
        """
        task_nodes = []
        prev_node_id = None
        
        for idx, task in enumerate(extracted_tasks):
            node_id = f"extracted_task_{idx:03d}"
            
            # 构建依赖关系
            dependencies = []
            if prev_node_id:
                dependencies.append(prev_node_id)
            # 添加额外依赖
            dependencies.extend(task.dependencies)
            
            node = TaskNodeInfo(
                task_id=node_id,
                task_type=task.task_type,
                description=f"{task.name}: {task.description}",
                inputs=[],
                outputs=[f"output_{node_id}"],
                dependencies=list(set(dependencies)),  # 去重
                metadata={
                    "task_name": task.name,
                    "deliverables": task.deliverables,
                    "responsible": task.responsible,
                    "estimated_time": task.estimated_time,
                    "source": "extracted",
                },
            )
            task_nodes.append(node)
            prev_node_id = node_id
        
        return task_nodes

    def auto_select_strategy(self, document: str) -> ExtractionStrategy:
        """自动选择提取策略
        
        根据文档内容自动选择最适合的提取策略。
        
        Args:
            document: 文档内容
            
        Returns:
            ExtractionStrategy: 推荐的提取策略
        """
        # 检查是否包含 Markdown 表格
        if "|" in document and "---" in document:
            return ExtractionStrategy.STRUCTURED
        
        # 检查是否包含数字列表
        if re.search(r"^\d+\.", document, re.MULTILINE):
            return ExtractionStrategy.STRUCTURED
        
        # 检查是否包含 Markdown 标题
        if re.search(r"^#{2,4}\s+", document, re.MULTILINE):
            return ExtractionStrategy.STRUCTURED
        
        # 默认使用正则表达式
        return ExtractionStrategy.REGEX
