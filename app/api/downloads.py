from __future__ import annotations

import logging
import os
from typing import List
import asyncio
import json

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from .. import database
from ..services.download_service import progress_event_queue
from .common import http_error

router = APIRouter()
logger = logging.getLogger(__name__)


# --- Models ---

class DownloadConfig(BaseModel):
    enabled: bool
    download_dir: str
    file_types: str
    max_size: int
    min_size: int

class SaveConfigPayload(BaseModel):
    enabled: bool
    download_dir: str
    file_types: str
    max_size: int
    min_size: int

class DeleteLocalFilePayload(BaseModel):
    file_id: str

# --- Helper ---

def _format_size(size_in_bytes: int) -> str:
    """将字节大小格式化为人类可读的字符串。"""
    if size_in_bytes is None:
        return "N/A"
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.2f} PB"

def _get_local_file_details() -> List[dict]:
    """获取所有本地文件的详细信息，包括文件系统状态。"""
    db_files = database.get_local_files()
    download_dir = database.get_app_settings_from_db().get("DOWNLOAD_DIR", "/app/downloads")
    
    detailed_files = []
    for file_rec in db_files:
        full_path = os.path.join(download_dir, file_rec["local_path"])
        exists = os.path.exists(full_path)
        actual_size = os.path.getsize(full_path) if exists else None
        
        detailed_files.append({
            **file_rec,
            "full_path": full_path,
            "exists": exists,
            "actual_size": actual_size
        })
    return detailed_files


# --- Endpoints ---

@router.get("/api/downloads/config", response_model=dict)
async def get_download_config():
    """获取自动下载配置"""
    try:
        settings = database.get_app_settings_from_db()
        # Remap from DB keys to API keys
        config_data = {
            "enabled": settings.get("AUTO_DOWNLOAD_ENABLED", False),
            "download_dir": settings.get("DOWNLOAD_DIR", "/app/downloads"),
            "file_types": settings.get("DOWNLOAD_FILE_TYPES", "image,video"),
            "max_size": settings.get("DOWNLOAD_MAX_SIZE", 52428800),
            "min_size": settings.get("DOWNLOAD_MIN_SIZE", 0)
        }
        return {"status": "success", "data": config_data}
    except Exception as e:
        logger.error("Error fetching download config: %s", e)
        raise http_error(500, "无法加载下载配置。")


@router.post("/api/downloads/config", response_model=dict)
async def save_download_config(payload: SaveConfigPayload):
    """保存自动下载配置"""
    try:
        current_settings = database.get_app_settings_from_db()
        
        update_data = {
            "AUTO_DOWNLOAD_ENABLED": payload.enabled,
            "DOWNLOAD_DIR": payload.download_dir,
            "DOWNLOAD_FILE_TYPES": payload.file_types,
            "DOWNLOAD_MAX_SIZE": payload.max_size,
            "DOWNLOAD_MIN_SIZE": payload.min_size,
        }
        current_settings.update(update_data)
        
        database.save_app_settings_to_db(current_settings)
        
        return {"status": "success", "message": "配置已保存。"}
    except Exception as e:
        logger.error("Error saving download config: %s", e)
        raise http_error(500, "保存下载配置失败。")


@router.get("/api/downloads/stats", response_model=dict)
async def get_local_stats():
    """获取本地存储统计信息"""
    try:
        local_files = _get_local_file_details()
        
        total_size = sum(f["actual_size"] for f in local_files if f["exists"])
        exists_count = sum(1 for f in local_files if f["exists"])
        
        stats = {
            "total_count": len(local_files),
            "total_size": total_size,
            "total_size_formatted": _format_size(total_size),
            "exists_count": exists_count,
            "missing_count": len(local_files) - exists_count,
        }
        return {"status": "success", "data": stats}
    except Exception as e:
        logger.error("Error getting local file stats: %s", e)
        raise http_error(500, "无法获取本地文件统计。")


@router.get("/api/downloads/local-files", response_model=dict)
async def get_local_files_list():
    """获取本地文件列表及其状态"""
    try:
        detailed_files = _get_local_file_details()
        return {"status": "success", "data": detailed_files}
    except Exception as e:
        logger.error("Error getting local files list: %s", e)
        raise http_error(500, "无法获取本地文件列表。")


@router.delete("/api/downloads/local-file", response_model=dict)
async def delete_local_file(payload: DeleteLocalFilePayload):
    """删除指定的本地文件（不会删除Telegram上的文件）"""
    try:
        file_id = payload.file_id
        db_file = database.get_file_by_id(file_id)

        if not db_file or not db_file.get("local_path"):
            raise http_error(404, "数据库中未找到该文件的本地记录。")

        download_dir = database.get_app_settings_from_db().get("DOWNLOAD_DIR", "/app/downloads")
        full_path = os.path.join(download_dir, db_file["local_path"])

        if os.path.exists(full_path):
            os.remove(full_path)
            logger.info("已从本地删除文件: %s", full_path)
        
        # 无论本地文件是否存在，都清空数据库记录
        database.clear_local_path(file_id)

        return {"status": "success", "message": "本地文件记录已清除。"}
    except Exception as e:
        logger.error("Error deleting local file: %s", e)
        raise http_error(500, "删除本地文件失败。")


@router.get("/api/downloads/progress-stream")
async def download_progress_stream(request: Request):
    """SSE endpoint for streaming download progress."""
    async def event_generator():
        while True:
            if await request.is_disconnected():
                logger.info("Client disconnected from download progress stream.")
                break
            
            try:
                event = await asyncio.wait_for(progress_event_queue.get(), timeout=30)
                yield f"data: {json.dumps(event)}\n\n"
                progress_event_queue.task_done()
            except asyncio.TimeoutError:
                # Send a keep-alive comment every 30s to prevent connection timeout
                yield ": keep-alive\n\n"
            except Exception as e:
                logger.error("Error in download progress stream: %s", e, exc_info=True)
                # Continue the loop
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")