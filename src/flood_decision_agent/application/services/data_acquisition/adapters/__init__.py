"""多模态输入适配器模块

提供对不同输入格式（文本、表格、文件）的统一解析能力。
"""

from src.flood_decision_agent.application.services.data_acquisition.adapters.base import (
    BaseInputAdapter,
)
from src.flood_decision_agent.application.services.data_acquisition.adapters.detector import (
    InputFormatDetector,
)
from src.flood_decision_agent.application.services.data_acquisition.adapters.file import (
    FileInputAdapter,
)
from src.flood_decision_agent.application.services.data_acquisition.adapters.table import (
    TableInputAdapter,
)
from src.flood_decision_agent.application.services.data_acquisition.adapters.text import (
    TextInputAdapter,
)

__all__ = [
    "BaseInputAdapter",
    "TextInputAdapter",
    "TableInputAdapter",
    "FileInputAdapter",
    "InputFormatDetector",
]
