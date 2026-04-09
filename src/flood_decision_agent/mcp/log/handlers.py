"""MCP 日志处理器

提供日志轮转和其他高级日志处理功能。
"""

import gzip
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, List, Optional


class LogRotationHandler:
    """日志轮转处理器

    负责管理日志文件的轮转、压缩和清理。
    """

    def __init__(
        self,
        log_dir: Path,
        max_size_mb: int = 10,
        retention_days: int = 7,
        compression: bool = True
    ):
        """初始化日志轮转处理器

        Args:
            log_dir: 日志目录
            max_size_mb: 单个日志文件最大大小（MB）
            retention_days: 日志保留天数
            compression: 是否压缩旧日志
        """
        self.log_dir = Path(log_dir)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.retention_days = retention_days
        self.compression = compression
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def should_rotate(self, log_file: Path) -> bool:
        """检查是否需要轮转日志文件

        Args:
            log_file: 日志文件路径

        Returns:
            是否需要轮转
        """
        if not log_file.exists():
            return False

        file_size = log_file.stat().st_size
        return file_size >= self.max_size_bytes

    def rotate(self, log_file: Path, server_name: str) -> Optional[Path]:
        """执行日志轮转

        Args:
            log_file: 当前日志文件路径
            server_name: 服务器名称

        Returns:
            轮转后的日志文件路径
        """
        if not self.should_rotate(log_file):
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rotated_name = f"{log_file.stem}-{timestamp}{log_file.suffix}"
        rotated_file = log_file.parent / rotated_name

        try:
            log_file.rename(rotated_file)

            if self.compression:
                self._compress_log(rotated_file)

            return log_file

        except Exception as e:
            print(f"日志轮转失败: {e}")
            return None

    def _compress_log(self, log_file: Path) -> None:
        """压缩日志文件

        Args:
            log_file: 日志文件路径
        """
        compressed_file = Path(str(log_file) + ".gz")

        try:
            with open(log_file, 'rb') as f_in:
                with gzip.open(compressed_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            log_file.unlink()

        except Exception as e:
            print(f"日志压缩失败: {e}")
            if compressed_file.exists():
                compressed_file.unlink()

    def cleanup_old_logs(self, server_name: Optional[str] = None) -> int:
        """清理过期的日志文件

        Args:
            server_name: 服务器名称，如果为 None 则清理所有服务器日志

        Returns:
            删除的文件数量
        """
        if server_name:
            log_dirs = [self.log_dir / server_name]
        else:
            log_dirs = [d for d in self.log_dir.iterdir() if d.is_dir()]

        deleted_count = 0
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)

        for log_dir in log_dirs:
            if not log_dir.is_dir():
                continue

            for log_file in log_dir.iterdir():
                if log_file.is_file():
                    try:
                        file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                        if file_time < cutoff_date:
                            log_file.unlink()
                            deleted_count += 1
                    except Exception:
                        pass

        return deleted_count

    def get_log_files(self, server_name: str, pattern: str = "*.log*") -> List[Path]:
        """获取指定服务器的日志文件列表

        Args:
            server_name: 服务器名称
            pattern: 文件匹配模式

        Returns:
            日志文件路径列表
        """
        server_log_dir = self.log_dir / server_name
        if not server_log_dir.exists():
            return []

        return sorted(server_log_dir.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)


class LogFilter:
    """日志过滤器

    用于过滤特定类型的日志记录。
    """

    def __init__(
        self,
        min_level: str = "DEBUG",
        include_servers: Optional[List[str]] = None,
        exclude_servers: Optional[List[str]] = None
    ):
        """初始化日志过滤器

        Args:
            min_level: 最低日志级别
            include_servers: 只包含的服务器列表，None 表示所有
            exclude_servers: 排除的服务器列表
        """
        self.level_map = {
            "DEBUG": 10,
            "INFO": 20,
            "WARNING": 30,
            "ERROR": 40,
            "CRITICAL": 50
        }
        self.min_level = self.level_map.get(min_level.upper(), 20)
        self.include_servers = include_servers
        self.exclude_servers = exclude_servers or []

    def should_log(self, level: str, server_name: str) -> bool:
        """判断是否应该记录此日志

        Args:
            level: 日志级别
            server_name: 服务器名称

        Returns:
            是否应该记录
        """
        level_value = self.level_map.get(level.upper(), 20)
        if level_value < self.min_level:
            return False

        if server_name in self.exclude_servers:
            return False

        if self.include_servers and server_name not in self.include_servers:
            return False

        return True


class LogCallbackHandler:
    """日志回调处理器

    用于在日志记录时执行自定义回调函数。
    """

    def __init__(self):
        self.callbacks: List[Callable[[str, str, Any], None]] = []

    def register_callback(self, callback: Callable[[str, str, Any], None]) -> None:
        """注册回调函数

        Args:
            callback: 回调函数，签名为 (level: str, message: str, context: Any) -> None
        """
        self.callbacks.append(callback)

    def trigger(self, level: str, message: str, context: Any = None) -> None:
        """触发所有回调函数

        Args:
            level: 日志级别
            message: 日志消息
            context: 额外上下文
        """
        for callback in self.callbacks:
            try:
                callback(level, message, context)
            except Exception:
                pass

    def clear(self) -> None:
        """清除所有回调函数"""
        self.callbacks.clear()


def create_rotation_handler(
    log_dir: str = "logs/mcp",
    max_size_mb: int = 10,
    retention_days: int = 7
) -> LogRotationHandler:
    """创建日志轮转处理器的便捷函数

    Args:
        log_dir: 日志目录
        max_size_mb: 最大文件大小（MB）
        retention_days: 保留天数

    Returns:
        LogRotationHandler 实例
    """
    return LogRotationHandler(
        log_dir=Path(log_dir),
        max_size_mb=max_size_mb,
        retention_days=retention_days
    )
