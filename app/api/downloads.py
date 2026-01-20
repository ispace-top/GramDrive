from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .. import database
from ..core.config import get_app_settings

router = APIRouter()
logger = logging.getLogger(__name__)


class AutoDownloadConfigRequest(BaseModel):
    enabled: bool
    max_size: Optional[int] = None
    file_types: Optional[str] = None
    download_dir: Optional[str] = None


class LocalFileDeleteRequest(BaseModel):
    file_id: str


@router.get("/api/downloads/config")
async def get_download_config():
    """获取自动下载配置"""
    settings = get_app_settings()
    return {
        "status": "success",
        "data": {
            "enabled": settings.get("AUTO_DOWNLOAD_ENABLED", False),
            "max_size": settings.get("DOWNLOAD_MAX_SIZE", 52428800),
            "file_types": settings.get("DOWNLOAD_FILE_TYPES", "image,video"),
            "download_dir": settings.get("DOWNLOAD_DIR", "/app/downloads")
        }
    }


@router.post("/api/downloads/config")
async def update_download_config(config: AutoDownloadConfigRequest):
    """更新自动下载配置"""
    try:
        # 更新数据库中的配置
        if config.enabled is not None:
            database.update_setting("AUTO_DOWNLOAD_ENABLED", str(config.enabled))

        if config.max_size is not None:
            database.update_setting("DOWNLOAD_MAX_SIZE", str(config.max_size))

        if config.file_types is not None:
            database.update_setting("DOWNLOAD_FILE_TYPES", config.file_types)

        if config.download_dir is not None:
            database.update_setting("DOWNLOAD_DIR", config.download_dir)

        return {
            "status": "success",
            "message": "自动下载配置已更新"
        }
    except Exception as e:
        logger.error(f"更新自动下载配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}")


@router.get("/api/downloads/local-files")
async def list_local_files():
    """列出所有已下载到本地的文件"""
    try:
        local_files = database.get_local_files()

        # 验证文件是否仍然存在于文件系统
        for file_info in local_files:
            local_path = file_info.get("local_path")
            if local_path:
                file_info["exists"] = os.path.exists(local_path)
                if file_info["exists"]:
                    file_info["actual_size"] = os.path.getsize(local_path)
            else:
                file_info["exists"] = False

        return {
            "status": "success",
            "data": local_files,
            "total": len(local_files)
        }
    except Exception as e:
        logger.error(f"获取本地文件列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取本地文件失败: {str(e)}")


@router.delete("/api/downloads/local-file")
async def delete_local_file(request: LocalFileDeleteRequest):
    """删除本地下载的文件（不删除Telegram上的文件）"""
    try:
        file_info = database.get_file_by_id(request.file_id)
        if not file_info:
            raise HTTPException(status_code=404, detail="文件记录不存在")

        local_path = file_info.get("local_path")
        if not local_path:
            return {
                "status": "success",
                "message": "该文件未下载到本地"
            }

        # 删除物理文件
        deleted = False
        if os.path.exists(local_path):
            try:
                os.remove(local_path)
                deleted = True
                logger.info(f"已删除本地文件: {local_path}")
            except OSError as e:
                logger.error(f"删除本地文件失败: {e}")
                raise HTTPException(status_code=500, detail=f"删除文件失败: {str(e)}")

        # 更新数据库，清除 local_path
        database.update_local_path(request.file_id, None)

        return {
            "status": "success",
            "message": "本地文件已删除" if deleted else "文件已不存在，数据库记录已清理"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除本地文件时出错: {e}")
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.get("/api/downloads/stats")
async def get_download_stats():
    """获取本地下载统计信息"""
    try:
        settings = get_app_settings()
        download_dir = settings.get("DOWNLOAD_DIR", "/app/downloads")

        local_files = database.get_local_files()

        total_count = len(local_files)
        total_size = 0
        exists_count = 0
        missing_count = 0

        for file_info in local_files:
            local_path = file_info.get("local_path")
            if local_path and os.path.exists(local_path):
                exists_count += 1
                total_size += os.path.getsize(local_path)
            else:
                missing_count += 1

        # 格式化大小
        def format_size(size_bytes):
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size_bytes < 1024.0:
                    return f"{size_bytes:.2f} {unit}"
                size_bytes /= 1024.0
            return f"{size_bytes:.2f} PB"

        return {
            "status": "success",
            "data": {
                "total_count": total_count,
                "exists_count": exists_count,
                "missing_count": missing_count,
                "total_size": total_size,
                "total_size_formatted": format_size(total_size),
                "download_dir": download_dir
            }
        }
    except Exception as e:
        logger.error(f"获取下载统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")
