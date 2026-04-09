"""数据可信度评级模块

提供数据可信度评级功能，根据数据来源自动评估数据可靠性。
"""

from .rater import ConfidenceRater

__all__ = ["ConfidenceRater"]
