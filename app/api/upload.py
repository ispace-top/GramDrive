from __future__ import annotations

import contextlib
import os
import shutil
import tempfile

from fastapi import APIRouter, Depends, File, Form, Header, Request, UploadFile

from ..core.config import Settings, get_app_settings, get_settings
from ..core.logging_config import get_logger
from ..services.telegram_service import get_telegram_service
from .common import ensure_upload_auth, http_error

router = APIRouter()
logger = get_logger(__name__)



@router.post("/api/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    key: str | None = Form(None),
    token: str | None = Form(None),
    settings: Settings = Depends(get_settings),
    x_api_key: str | None = Header(None),
    authorization: str | None = Header(None),
):
    app_settings = get_app_settings()
    if not (app_settings.get("BOT_TOKEN") or "").strip() or not (app_settings.get("CHANNEL_NAME") or "").strip():
        logger.error("【上传】缺少配置：BOT_TOKEN 或 CHANNEL_NAME")
        raise http_error(503, "缺少 BOT_TOKEN 或 CHANNEL_NAME，无法上传", code="cfg_missing")

    submitted_key = x_api_key or key or token
    if not submitted_key and authorization and authorization.startswith("Bearer "):
        submitted_key = authorization.split(" ", 1)[1]

    ensure_upload_auth(request, app_settings, submitted_key)
    logger.info(f"【上传】开始上传文件。文件名: {file.filename}，大小: {file.size or '未知'} 字节")

    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)

        telegram_service = get_telegram_service()
        file_id = await telegram_service.upload_file(temp_file_path, file.filename)
    except Exception as e:
        logger.error(f"【上传】上传失败。文件名: {file.filename}，错误: {str(e)}", exc_info=e)
        raise http_error(500, "文件上传失败。", code="upload_failed", details=str(e)) from e
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            with contextlib.suppress(OSError):
                os.unlink(temp_file_path)

    if not file_id:
        logger.error(f"【上传】上传失败：未返回 file_id。文件名: {file.filename}")
        raise http_error(500, "文件上传失败。", code="upload_failed")

    # 构造短链 URL: /d/{short_id}
    # 这里的 file_id 实际上是 short_id
    file_path = f"/d/{file_id}"

    # 始终返回相对路径，前端负责拼接 origin
    full_url = file_path

    logger.info(f"【上传】上传成功。文件名: {file.filename} -> ID: {file_id}")
    return {
        "file_id": file_id,          # 这里的 file_id 是用于分享的 ID (即 short_id)
        "short_id": file_id,         # 兼容旧字段
        "download_path": file_path,  # 用户要求的字段
        "path": file_path,           # 兼容旧字段
        "url": str(full_url)         # 兼容旧字段
    }

