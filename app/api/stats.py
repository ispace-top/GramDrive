from __future__ import annotations

import logging
from fastapi import APIRouter, Depends

from ..core.config import Settings, get_settings
from .. import database

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/api/stats/dashboard")
async def get_dashboard_stats(settings: Settings = Depends(get_settings)):
    """获取仪表板统计数据"""
    stats = database.get_statistics()

    # 格式化文件大小为人类可读格式
    def format_size(bytes_size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} PB"

    stats["total_size_formatted"] = format_size(stats["total_size"])

    # 格式化类型统计中的大小
    for type_name, type_data in stats["by_type"].items():
        type_data["size_formatted"] = format_size(type_data["size"])

    return {
        "status": "success",
        "data": stats
    }


@router.get("/api/stats/local-files")
async def get_local_files_stats(settings: Settings = Depends(get_settings)):
    """获取本地文件列表"""
    local_files = database.get_local_files()
    return {
        "status": "success",
        "count": len(local_files),
        "files": local_files
    }
