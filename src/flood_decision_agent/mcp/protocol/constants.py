"""MCP Protocol Constants - 协议常量定义

定义 MCP 协议中使用的各种常量。
"""

# 协议版本
PROTOCOL_VERSION = "1.0.0"

# 默认超时（秒）
DEFAULT_TIMEOUT = 30.0

# 连接超时（秒）
CONNECTION_TIMEOUT = 10.0

# 最大消息大小（字节）
MAX_MESSAGE_SIZE = 10 * 1024 * 1024  # 10MB

# 默认缓冲区大小
DEFAULT_BUFFER_SIZE = 8192

# 心跳间隔（秒）
HEARTBEAT_INTERVAL = 30.0

# 最大重试次数
MAX_RETRY_COUNT = 3

# 重试延迟（秒）
RETRY_DELAY = 1.0

# 标准输入输出编码
STDIO_ENCODING = "utf-8"

# 默认服务器名称前缀
DEFAULT_SERVER_NAME_PREFIX = "flood-agent"

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {
    ".md", ".json", ".txt", ".yaml", ".yml",
    ".docx", ".csv", ".xml",
}

# 默认目录
DEFAULT_PLANS_DIR = "./plans"
DEFAULT_DATA_DIR = "./data"
DEFAULT_OUTPUT_DIR = "./output"

# 环境变量名
ENV_KIMI_API_KEY = "KIMI_API_KEY"
ENV_MCP_LOG_LEVEL = "MCP_LOG_LEVEL"
ENV_MCP_DEBUG = "MCP_DEBUG"

# 日志级别
LOG_LEVEL_DEBUG = "DEBUG"
LOG_LEVEL_INFO = "INFO"
LOG_LEVEL_WARNING = "WARNING"
LOG_LEVEL_ERROR = "ERROR"

# 服务器状态
SERVER_STATUS_UNKNOWN = "unknown"
SERVER_STATUS_INITIALIZING = "initializing"
SERVER_STATUS_READY = "ready"
SERVER_STATUS_ERROR = "error"
SERVER_STATUS_STOPPING = "stopping"
SERVER_STATUS_STOPPED = "stopped"

# 工具类别
TOOL_CATEGORY_FILE = "file_operation"
TOOL_CATEGORY_COMPUTE = "compute"
TOOL_CATEGORY_QUERY = "data_query"
TOOL_CATEGORY_FORMAT = "format"
TOOL_CATEGORY_LOG = "log"
TOOL_CATEGORY_HYDROLOGY = "hydrology"

# HTTP 状态码映射
HTTP_STATUS_OK = 200
HTTP_STATUS_BAD_REQUEST = 400
HTTP_STATUS_NOT_FOUND = 404
HTTP_STATUS_INTERNAL_ERROR = 500
HTTP_STATUS_TIMEOUT = 504
