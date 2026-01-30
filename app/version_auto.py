"""
GramDrive 版本信息（支持从 GitHub Release 自动获取）
"""

import asyncio
import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

# 默认版本信息
__version__ = "1.0.0"
__author__ = "ispace"
__email__ = "kindom162@gmail.com"
__github__ = "https://github.com/ispace-top"
__repository__ = "https://github.com/ispace-top/GramDrive"
__license__ = "MIT"
__description__ = "基于 Telegram 的永久在线私有云存储和媒体中心"

# 缓存的最新版本信息
_latest_version: Optional[str] = None
_version_check_time: Optional[float] = None


async def get_latest_version_from_github() -> Optional[str]:
    """
    从 GitHub API 获取最新 Release 版本号

    Returns:
        最新版本号，如果获取失败返回 None
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                "https://api.github.com/repos/ispace-top/GramDrive/releases/latest"
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("tag_name", "").lstrip("v")
            else:
                logger.warning(f"获取 GitHub Release 失败: {response.status_code}")
                return None
    except Exception as e:
        logger.warning(f"获取 GitHub Release 失败: {e}")
        return None


async def get_version(force_refresh: bool = False) -> str:
    """
    获取当前版本号（优先从 GitHub 获取，失败则使用默认版本）

    Args:
        force_refresh: 是否强制刷新版本信息

    Returns:
        版本号字符串
    """
    global _latest_version, _version_check_time

    import time
    current_time = time.time()

    # 如果有缓存且未强制刷新且缓存未过期（24小时），直接返回
    if not force_refresh and _latest_version and _version_check_time:
        if current_time - _version_check_time < 86400:  # 24小时
            return _latest_version

    # 尝试从 GitHub 获取最新版本
    latest = await get_latest_version_from_github()
    if latest:
        _latest_version = latest
        _version_check_time = current_time
        logger.info(f"从 GitHub 获取到最新版本: {latest}")
        return latest

    # 如果有旧缓存，返回旧缓存
    if _latest_version:
        logger.warning("GitHub API 获取失败，使用缓存版本")
        return _latest_version

    # 否则返回默认版本
    logger.warning("无法获取 GitHub 版本信息，使用默认版本")
    return __version__


def get_version_sync() -> str:
    """
    同步获取版本号（用于非异步上下文）
    """
    global _latest_version
    if _latest_version:
        return _latest_version
    return __version__


# 版本历史
VERSION_HISTORY = [
    {
        "version": "1.0.0",
        "date": "2024-01",
        "changes": [
            "智能自动下载功能，支持文件类型过滤和大小限制",
            "缩略图自动生成与缓存（小、中、大三种尺寸）",
            "本地文件优先策略，减少 Telegram API 调用",
            "现代化 UI 设计，支持深色模式",
            "统计仪表板，实时监控文件状态",
            "文件标签系统，方便分类管理",
            "密码保护和会话管理",
            "PicGo API 支持，无缝集成图床功能"
        ]
    }
]
