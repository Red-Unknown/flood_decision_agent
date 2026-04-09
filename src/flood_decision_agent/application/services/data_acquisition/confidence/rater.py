"""数据可信度评级器

根据数据来源自动评估数据可信度，并提供可视化支持。
"""

from typing import Any, Dict, Optional

from ..models import DataConfidenceLevel, DataSource


class ConfidenceRater:
    """数据可信度评级器

    根据数据来源自动评估数据可信度，支持可信度升级和可视化展示。
    """

    def __init__(self) -> None:
        """初始化可信度评级器"""
        self._confidence_scores: Dict[DataConfidenceLevel, float] = {
            DataConfidenceLevel.MEASURED: 1.0,
            DataConfidenceLevel.CALCULATED: 0.8,
            DataConfidenceLevel.REFERENCE: 0.6,
            DataConfidenceLevel.ESTIMATED: 0.4,
            DataConfidenceLevel.ASSUMED: 0.2,
        }
        self._confidence_colors: Dict[DataConfidenceLevel, str] = {
            DataConfidenceLevel.MEASURED: "green",
            DataConfidenceLevel.CALCULATED: "blue",
            DataConfidenceLevel.REFERENCE: "cyan",
            DataConfidenceLevel.ESTIMATED: "orange",
            DataConfidenceLevel.ASSUMED: "red",
        }
        self._confidence_icons: Dict[DataConfidenceLevel, str] = {
            DataConfidenceLevel.MEASURED: "✓",
            DataConfidenceLevel.CALCULATED: "🧮",
            DataConfidenceLevel.REFERENCE: "📚",
            DataConfidenceLevel.ESTIMATED: "🔍",
            DataConfidenceLevel.ASSUMED: "⚠",
        }

    def rate_confidence(
        self,
        value: Any,
        source: DataSource,
        metadata: Optional[Dict] = None,
    ) -> DataConfidenceLevel:
        """根据数据来源自动评级可信度

        评级规则：
        - measured: 实测数据，最可靠
        - file_upload/table_paste 有原始文件 → measured
        - formula_calculation → calculated
        - standard_lookup → reference
        - similar_project → estimated
        - llm_extraction/estimated → estimated
        - 使用默认值 → assumed

        Args:
            value: 数据值
            source: 数据来源
            metadata: 额外元数据，用于判断是否有原始文件等

        Returns:
            数据可信度级别
        """
        metadata = metadata or {}

        if source == DataSource.USER_INPUT:
            return DataConfidenceLevel.MEASURED

        if source in (DataSource.FILE_UPLOAD, DataSource.TABLE_PASTE):
            has_original_file = metadata.get("has_original_file", True)
            if has_original_file:
                return DataConfidenceLevel.MEASURED
            return DataConfidenceLevel.ESTIMATED

        if source == DataSource.FORMULA_CALCULATION:
            return DataConfidenceLevel.CALCULATED

        if source == DataSource.STANDARD_LOOKUP:
            return DataConfidenceLevel.REFERENCE

        if source == DataSource.SIMILAR_PROJECT:
            return DataConfidenceLevel.ESTIMATED

        if source == DataSource.LLM_EXTRACTION:
            return DataConfidenceLevel.ESTIMATED

        return DataConfidenceLevel.ASSUMED

    def get_confidence_score(self, level: DataConfidenceLevel) -> float:
        """获取可信度分数

        Args:
            level: 可信度级别

        Returns:
            可信度分数（0.0-1.0）
        """
        return self._confidence_scores.get(level, 0.0)

    def get_confidence_color(self, level: DataConfidenceLevel) -> str:
        """获取可信度可视化颜色

        Args:
            level: 可信度级别

        Returns:
            颜色名称（用于前端展示）
        """
        return self._confidence_colors.get(level, "gray")

    def get_confidence_icon(self, level: DataConfidenceLevel) -> str:
        """获取可信度图标标识

        Args:
            level: 可信度级别

        Returns:
            图标字符
        """
        return self._confidence_icons.get(level, "?")

    def upgrade_confidence(
        self,
        current_level: DataConfidenceLevel,
        new_source: DataSource,
    ) -> DataConfidenceLevel:
        """根据新的获取方式升级可信度

        如果新的数据来源更可靠，则返回更高级别的可信度。

        Args:
            current_level: 当前可信度级别
            new_source: 新的数据来源

        Returns:
            升级后的可信度级别
        """
        new_level = self.rate_confidence(None, new_source)

        if new_level.is_more_reliable_than(current_level):
            return new_level

        return current_level

    def should_request_confirmation(self, level: DataConfidenceLevel) -> bool:
        """判断是否需要用户确认

        assumed 和 estimated 级别的数据需要用户确认。

        Args:
            level: 可信度级别

        Returns:
            是否需要用户确认
        """
        return level in (DataConfidenceLevel.ASSUMED, DataConfidenceLevel.ESTIMATED)
