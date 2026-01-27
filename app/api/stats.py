from __future__ import annotations

import logging

from fastapi import APIRouter, Depends

from .. import database
from ..core.config import Settings, get_settings
from .common import http_error

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/api/stats/dashboard")
async def get_dashboard_stats(settings: Settings = Depends(get_settings)):
    """获取仪表板统计数据，并适配前端所需格式"""
    try:
        raw_stats = database.get_statistics()

        def format_size(size_in_bytes):
            if size_in_bytes is None:
                return "0 B"
            if size_in_bytes < 1024:
                return f"{size_in_bytes} B"
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size_in_bytes < 1024.0:
                    return f"{size_in_bytes:.2f} {unit}"
                size_in_bytes /= 1024.0
            return f"{size_in_bytes:.2f} PB"

        total_files = raw_stats.get("total_files", 0)
        total_size = raw_stats.get("total_size", 0)

        # 1. 获取总下载次数
        total_downloads = raw_stats.get("total_downloads", 0)

        # 2. 计算平均文件大小
        avg_size = total_size / total_files if total_files > 0 else 0

        # 3. 整理文件类型分布
        file_types = []
        type_labels = {
            'image': '图片',
            'video': '视频',
            'audio': '音频',
            'document': '文档',
            'pdf': 'PDF',
            'text': '文本',
            'other': '其他'
        }
        for type_name, type_data in raw_stats.get("by_type", {}).items():
            file_types.append({
                "type": type_name,
                "type_label": type_labels.get(type_name, '未知'),
                "count": type_data.get("count", 0),
                "size": type_data.get("size", 0),
                "size_formatted": format_size(type_data.get("size", 0))
            })

        # 4. 整理热门文件并格式化大小
        popular_files = []
        for f in raw_stats.get("top_downloads", []):
            f_copy = f.copy()
            f_copy["filesize_formatted"] = format_size(f_copy.get("filesize", 0))
            popular_files.append(f_copy)

        # 5. 组装前端需要的数据结构
        data_for_frontend = {
            "total_count": total_files,
            "total_size": total_size,
            "total_size_formatted": format_size(total_size),
            "total_downloads": total_downloads,
            "avg_size": avg_size,
            "avg_size_formatted": format_size(avg_size),
            "file_types": file_types,
            "popular_files": popular_files,
            "recent_uploads": raw_stats.get("recent_uploads", []),
            "local_files_count": raw_stats.get("local_files_count", 0),
            "total_tags": raw_stats.get("total_tags", 0)
        }

        return {
            "status": "success",
            "data": data_for_frontend
        }
    except Exception as e:
        logger.error("处理仪表板统计数据出错: %s", e, exc_info=True)
        raise http_error(500, "无法加载或处理统计数据。", details=str(e)) from e


@router.get("/api/stats/local-files")
async def get_local_files_stats(settings: Settings = Depends(get_settings)):
    """获取本地文件列表"""
    local_files = database.get_local_files()
    return {
        "status": "success",
        "count": len(local_files),
        "files": local_files
    }
