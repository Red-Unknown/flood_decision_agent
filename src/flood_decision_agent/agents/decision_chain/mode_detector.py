"""模式识别器模块.

用于自动判断用户输入的问题复杂度（simple/plan/spec）。
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set


class ModeType(Enum):
    """模式类型枚举."""

    SIMPLE = "simple"
    PLAN = "plan"
    SPEC = "spec"


@dataclass
class ComplexityMetrics:
    """复杂度指标数据类."""

    char_count: int
    sentence_count: int
    technical_term_count: int
    has_multiple_goals: bool
    has_architecture_terms: bool
    has_module_references: bool


class ModeDetector:
    """模式识别器类.

    基于问题长度、关键词、复杂度指标自动判断用户输入的问题复杂度。

    判断逻辑:
    - simple: 短问题(<50字)、查询类、无技术术语
    - plan: 中等长度(50-200字)、涉及系统设计、有多个目标
    - spec: 长问题(>200字)、复杂架构、多模块、详细需求
    """

    # 技术术语关键词
    TECHNICAL_TERMS: Set[str] = {
        "架构", "设计模式", "接口", "API", "数据库", "缓存", "消息队列",
        "微服务", "分布式", "并发", "异步", "同步", "负载均衡", "集群",
        "容器", "Docker", "Kubernetes", "K8s", "云原生", "中间件",
        "算法", "数据结构", "优化", "性能", "吞吐量", "延迟", "QPS",
        "架构", "architecture", "design pattern", "interface", "database",
        "cache", "message queue", "microservice", "distributed", "concurrent",
        "async", "synchronous", "load balance", "cluster", "container",
        "algorithm", "data structure", "optimization", "performance",
    }

    # 架构相关术语
    ARCHITECTURE_TERMS: Set[str] = {
        "系统", "架构", "模块", "组件", "服务", "层", " tier", "layer",
        "前端", "后端", "服务端", "客户端", "网关", "代理", "system",
        "architecture", "module", "component", "service", "frontend",
        "backend", "server", "client", "gateway", "proxy",
    }

    # 模块引用关键词
    MODULE_REFERENCES: Set[str] = {
        "模块", "子系统", "单元", "组件", "服务", "module", "subsystem",
        "unit", "component", "service",
    }

    # 多目标指示词
    MULTI_GOAL_INDICATORS: Set[str] = {
        "和", "与", "以及", "同时", "另外", "并且", "还", "需要",
        "and", "also", "additionally", "furthermore", "moreover",
        "besides", "plus", "together with",
    }

    # 查询类关键词（simple模式指示词）
    QUERY_TERMS: Set[str] = {
        "是什么", "什么是", "怎么", "如何", "为什么", "多少", "哪里",
        "谁", "什么时候", "列举", "列出", "告诉我", "查询",
        "what", "how", "why", "when", "where", "who", "which",
        "list", "show", "tell me", "explain", "what is",
    }

    def __init__(
        self,
        simple_threshold: int = 50,
        plan_threshold: int = 200,
        technical_weight: float = 1.5,
        architecture_weight: float = 2.0,
    ):
        """初始化模式识别器.

        Args:
            simple_threshold: simple模式字数阈值（默认50字）
            plan_threshold: plan模式字数阈值（默认200字）
            technical_weight: 技术术语权重
            architecture_weight: 架构术语权重
        """
        self.simple_threshold = simple_threshold
        self.plan_threshold = plan_threshold
        self.technical_weight = technical_weight
        self.architecture_weight = architecture_weight

    def detect(self, user_input: str) -> str:
        """检测用户输入的问题复杂度模式.

        Args:
            user_input: 用户输入文本

        Returns:
            模式类型: "simple" | "plan" | "spec"
        """
        if not user_input or not user_input.strip():
            return ModeType.SIMPLE.value

        metrics = self._calculate_metrics(user_input)
        scores = self._calculate_scores(metrics)

        return self._determine_mode(scores, metrics)

    def _calculate_metrics(self, user_input: str) -> ComplexityMetrics:
        """计算复杂度指标.

        Args:
            user_input: 用户输入文本

        Returns:
            复杂度指标数据类
        """
        # 字符数（不含空格）
        char_count = len(user_input.replace(" ", "").replace("　", ""))

        # 句子数（基于标点符号）
        sentence_endings = re.findall(r"[。！？.!?;；\n]+", user_input)
        sentence_count = max(1, len(sentence_endings))

        # 技术术语数量
        technical_term_count = self._count_technical_terms(user_input)

        # 是否有多个目标
        has_multiple_goals = self._has_multiple_goals(user_input)

        # 是否有架构术语
        has_architecture_terms = self._has_architecture_terms(user_input)

        # 是否有模块引用
        has_module_references = self._has_module_references(user_input)

        return ComplexityMetrics(
            char_count=char_count,
            sentence_count=sentence_count,
            technical_term_count=technical_term_count,
            has_multiple_goals=has_multiple_goals,
            has_architecture_terms=has_architecture_terms,
            has_module_references=has_module_references,
        )

    def _count_technical_terms(self, text: str) -> int:
        """统计技术术语数量.

        Args:
            text: 输入文本

        Returns:
            技术术语出现次数
        """
        text_lower = text.lower()
        count = 0
        for term in self.TECHNICAL_TERMS:
            count += text_lower.count(term.lower())
        return count

    def _has_multiple_goals(self, text: str) -> bool:
        """检查是否有多个目标.

        Args:
            text: 输入文本

        Returns:
            是否包含多个目标指示词
        """
        text_lower = text.lower()
        indicator_count = 0
        for indicator in self.MULTI_GOAL_INDICATORS:
            if indicator.lower() in text_lower:
                indicator_count += 1
        # 出现多个连接词或问号/需求词组合表示多目标
        return indicator_count >= 2 or (
            indicator_count >= 1 and ("?" in text or "？" in text or "需要" in text)
        )

    def _has_architecture_terms(self, text: str) -> bool:
        """检查是否包含架构术语.

        Args:
            text: 输入文本

        Returns:
            是否包含架构相关术语
        """
        text_lower = text.lower()
        return any(term.lower() in text_lower for term in self.ARCHITECTURE_TERMS)

    def _has_module_references(self, text: str) -> bool:
        """检查是否包含模块引用.

        Args:
            text: 输入文本

        Returns:
            是否包含模块引用
        """
        text_lower = text.lower()
        return any(term.lower() in text_lower for term in self.MODULE_REFERENCES)

    def _is_query_type(self, text: str) -> bool:
        """检查是否为查询类型问题.

        Args:
            text: 输入文本

        Returns:
            是否为查询类问题
        """
        text_lower = text.lower()
        return any(term.lower() in text_lower for term in self.QUERY_TERMS)

    def _calculate_scores(self, metrics: ComplexityMetrics) -> Dict[str, float]:
        """计算各模式得分.

        Args:
            metrics: 复杂度指标

        Returns:
            各模式得分字典
        """
        # 基础分数
        simple_score = 0.0
        plan_score = 0.0
        spec_score = 0.0

        # 基于长度评分
        if metrics.char_count < self.simple_threshold:
            simple_score += 3.0
        elif metrics.char_count < self.plan_threshold:
            plan_score += 2.0
        else:
            spec_score += 3.0

        # 基于句子数评分
        if metrics.sentence_count <= 2:
            simple_score += 1.0
        elif metrics.sentence_count <= 5:
            plan_score += 1.0
        else:
            spec_score += 2.0

        # 基于技术术语评分
        if metrics.technical_term_count == 0:
            simple_score += 2.0
        elif metrics.technical_term_count <= 3:
            plan_score += metrics.technical_term_count * self.technical_weight
        else:
            spec_score += metrics.technical_term_count * self.technical_weight

        # 基于复杂度特征评分
        if metrics.has_multiple_goals:
            plan_score += 1.5
            spec_score += 1.0

        if metrics.has_architecture_terms:
            plan_score += self.architecture_weight
            spec_score += self.architecture_weight * 1.5

        if metrics.has_module_references:
            plan_score += 1.0
            spec_score += 2.0

        return {
            ModeType.SIMPLE.value: simple_score,
            ModeType.PLAN.value: plan_score,
            ModeType.SPEC.value: spec_score,
        }

    def _determine_mode(self, scores: Dict[str, float], metrics: ComplexityMetrics) -> str:
        """根据得分确定最终模式.

        Args:
            scores: 各模式得分
            metrics: 复杂度指标

        Returns:
            最终确定的模式类型
        """
        # 特殊规则：超长文本(>=plan_threshold)强制为spec，无论内容如何
        if metrics.char_count >= self.plan_threshold:
            return ModeType.SPEC.value

        # 特殊规则：包含详细需求描述（模块引用+架构术语）强制为spec
        if (
            metrics.char_count > 100
            and metrics.has_module_references
            and metrics.has_architecture_terms
        ):
            return ModeType.SPEC.value

        # 特殊规则：中等长度+多目标+架构术语为plan
        if (
            metrics.char_count >= self.simple_threshold
            and metrics.has_architecture_terms
        ):
            return ModeType.PLAN.value

        # 特殊规则：包含技术术语+架构术语为plan
        if metrics.has_architecture_terms and metrics.technical_term_count > 0:
            return ModeType.PLAN.value

        # 默认选择得分最高的模式
        max_score = max(scores.values())
        for mode, score in scores.items():
            if score == max_score:
                return mode

        return ModeType.SIMPLE.value

    def get_metrics(self, user_input: str) -> ComplexityMetrics:
        """获取复杂度指标（用于调试和分析）.

        Args:
            user_input: 用户输入文本

        Returns:
            复杂度指标数据类
        """
        if not user_input or not user_input.strip():
            return ComplexityMetrics(
                char_count=0,
                sentence_count=0,
                technical_term_count=0,
                has_multiple_goals=False,
                has_architecture_terms=False,
                has_module_references=False,
            )
        return self._calculate_metrics(user_input)

    def get_detection_details(self, user_input: str) -> Dict:
        """获取检测详情（用于调试和分析）.

        Args:
            user_input: 用户输入文本

        Returns:
            包含检测结果详情的字典
        """
        if not user_input or not user_input.strip():
            return {
                "mode": ModeType.SIMPLE.value,
                "metrics": None,
                "scores": None,
                "reason": "Empty input",
            }

        metrics = self._calculate_metrics(user_input)
        scores = self._calculate_scores(metrics)
        mode = self.detect(user_input)

        # 确定原因
        reasons = []
        if metrics.char_count < self.simple_threshold:
            reasons.append(f"短文本({metrics.char_count}字)")
        elif metrics.char_count >= self.plan_threshold:
            reasons.append(f"长文本({metrics.char_count}字)")
        else:
            reasons.append(f"中等长度({metrics.char_count}字)")

        if metrics.technical_term_count > 0:
            reasons.append(f"含{metrics.technical_term_count}个技术术语")
        if metrics.has_multiple_goals:
            reasons.append("多目标")
        if metrics.has_architecture_terms:
            reasons.append("含架构术语")
        if metrics.has_module_references:
            reasons.append("含模块引用")

        return {
            "mode": mode,
            "metrics": {
                "char_count": metrics.char_count,
                "sentence_count": metrics.sentence_count,
                "technical_term_count": metrics.technical_term_count,
                "has_multiple_goals": metrics.has_multiple_goals,
                "has_architecture_terms": metrics.has_architecture_terms,
                "has_module_references": metrics.has_module_references,
            },
            "scores": scores,
            "reason": "; ".join(reasons) if reasons else "默认判断",
        }
