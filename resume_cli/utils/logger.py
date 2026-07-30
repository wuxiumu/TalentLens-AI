"""
日志工具模块

提供统一的日志配置，支持通过环境变量 LOG_LEVEL 控制日志级别。
"""

import logging
import sys
from typing import Optional

from resume_cli.config import get_settings

_configured = False


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    获取配置好的 logger

    Args:
        name: logger 名称，通常为 __name__

    Returns:
        配置好的 Logger 实例
    """
    global _configured

    settings = get_settings()

    if not _configured:
        # 配置根 logger
        root_logger = logging.getLogger("resume_cli")
        root_logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

        # 控制台输出
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

        # 日志格式
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)

        # 避免重复添加 handler
        root_logger.propagate = False
        _configured = True

    if name:
        # 避免重复前缀（如 __name__ 已经是 resume_cli.xxx）
        if name.startswith("resume_cli"):
            return logging.getLogger(name)
        return logging.getLogger(f"resume_cli.{name}")
    return logging.getLogger("resume_cli")
