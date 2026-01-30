"""
统一的日志配置模块
提供结构化的日志输出，便于运行状态跟踪和问题排查
"""

import logging
import os
import sys

# 日志级别映射
LOG_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

# 获取日志级别
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
NUMERIC_LOG_LEVEL = LOG_LEVEL_MAP.get(LOG_LEVEL, logging.INFO)

# 颜色定义（用于控制台输出）
class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器，用于控制台输出"""

    COLORS = {
        "DEBUG": "\033[36m",      # 青色
        "INFO": "\033[32m",       # 绿色
        "WARNING": "\033[33m",    # 黄色
        "ERROR": "\033[31m",      # 红色
        "CRITICAL": "\033[41m",   # 红色背景
    }
    RESET = "\033[0m"

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


def get_logger(name: str) -> logging.Logger:
    """
    获取配置好的 logger 实例

    Args:
        name: logger 名称，通常使用 __name__

    Returns:
        配置好的 logger 实例
    """
    logger = logging.getLogger(name)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    logger.setLevel(NUMERIC_LOG_LEVEL)

    # 控制台处理器（带颜色）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(NUMERIC_LOG_LEVEL)

    # 格式化器
    console_formatter = ColoredFormatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # 文件处理器（可选）
    log_file = os.getenv("LOG_FILE")
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)  # 文件记录所有级别

            file_formatter = logging.Formatter(
                fmt="%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"无法创建日志文件: {e}")

    return logger


def setup_logging():
    """初始化全局日志配置"""
    # 配置根 logger
    root_logger = logging.getLogger()
    root_logger.setLevel(NUMERIC_LOG_LEVEL)

    # 如果没有 handler，添加一个
    if not root_logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(NUMERIC_LOG_LEVEL)

        console_formatter = ColoredFormatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)


# 日志工具函数
def log_request(logger: logging.Logger, method: str, path: str, client_ip: str = None):
    """记录 HTTP 请求"""
    client_info = f" from {client_ip}" if client_ip else ""
    logger.info(f"【请求】{method} {path}{client_info}")


def log_response(logger: logging.Logger, method: str, path: str, status_code: int, duration_ms: float = None):
    """记录 HTTP 响应"""
    duration_info = f" ({duration_ms:.2f}ms)" if duration_ms else ""
    status_emoji = "✓" if 200 <= status_code < 300 else "✗" if status_code >= 400 else "→"
    logger.info(f"【响应】{status_emoji} {status_code} {method} {path}{duration_info}")


def log_error(logger: logging.Logger, error_type: str, message: str, exc_info: Exception = None):
    """记录错误信息"""
    if exc_info:
        logger.error(f"【错误】{error_type}: {message}", exc_info=exc_info)
    else:
        logger.error(f"【错误】{error_type}: {message}")


def log_database(logger: logging.Logger, operation: str, details: str = None):
    """记录数据库操作"""
    details_info = f" - {details}" if details else ""
    logger.debug(f"【数据库】{operation}{details_info}")


def log_service(logger: logging.Logger, service_name: str, action: str, details: str = None):
    """记录服务操作"""
    details_info = f" - {details}" if details else ""
    logger.info(f"【{service_name}】{action}{details_info}")


def log_config(logger: logging.Logger, key: str, value: str = None, masked: bool = False):
    """记录配置信息"""
    if masked and value:
        value = "*" * (len(str(value)) - 4) + str(value)[-4:]
    value_info = f": {value}" if value else ""
    logger.debug(f"【配置】{key}{value_info}")
