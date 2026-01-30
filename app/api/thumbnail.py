import logging

import httpx
from fastapi import APIRouter, Depends, Query, Response

from .. import database
from ..core.http_client import get_http_client
from ..services.telegram_service import get_telegram_service
from ..services.thumbnail_service import get_thumbnail_service
from .common import http_error

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/api/thumbnail/{file_id}")
async def get_thumbnail(
    file_id: str,
    size: str = Query("medium", pattern="^(small|medium|large)$"),
    client: httpx.AsyncClient = Depends(get_http_client),
):
    """
    获取文件缩略图

    Args:
        file_id: 文件ID（可以是composite ID或short_id）
        size: 缩略图尺寸 (small=150x150, medium=300x300, large=600x600)
    """

    # 查询文件元数据
    file_meta = database.get_file_by_id(file_id)
    if not file_meta:
        raise http_error(404, "文件不存在", code="file_not_found")

    # 检查是否为图片类型
    mime_type = file_meta.get("mime_type", "")
    if not mime_type or not mime_type.startswith("image/"):
        # 如果没有mime_type或不是图片，则认为是图片（兜底）
        # 因为Telegram的photo类型可能没有mime_type
        logger.warning(f"文件 {file_id} mime_type={mime_type}，假定为图片类型")
        # 不再抛出错误，直接尝试生成缩略图

    # 获取服务
    thumbnail_service = get_thumbnail_service()

    # 检查缓存
    cached_thumbnail = thumbnail_service.get_cached_thumbnail(file_meta["file_id"], size)
    if cached_thumbnail:
        return Response(
            content=cached_thumbnail,
            media_type="image/jpeg",
            headers={
                "Cache-Control": "public, max-age=86400",  # 缓存1天
                "X-Thumbnail-Cache": "hit"
            }
        )

    # 缓存未命中，生成缩略图
    try:
        telegram_service = get_telegram_service()
    except Exception as e:
        raise http_error(503, "Telegram服务不可用", code="telegram_unavailable") from e

    # 获取原图下载链接
    try:
        _, real_file_id = file_meta["file_id"].split(":", 1)
    except ValueError:
        real_file_id = file_meta["file_id"]

    download_url = await telegram_service.get_download_url(real_file_id)
    if not download_url:
        raise http_error(404, "无法获取文件下载链接", code="download_url_failed")

    # 生成缩略图
    thumbnail_data = await thumbnail_service.generate_thumbnail(
        file_meta["file_id"],
        download_url,
        size,
        client
    )

    if not thumbnail_data:
        raise http_error(500, "缩略图生成失败", code="thumbnail_generation_failed")

    return Response(
        content=thumbnail_data,
        media_type="image/jpeg",
        headers={
            "Cache-Control": "public, max-age=86400",
            "X-Thumbnail-Cache": "miss"
        }
    )


@router.delete("/api/thumbnail/{file_id}")
async def delete_thumbnail_cache(file_id: str):
    """删除指定文件的缩略图缓存"""
    thumbnail_service = get_thumbnail_service()
    thumbnail_service.clear_cache(file_id)
    return {"status": "ok", "message": f"已清除文件 {file_id} 的缩略图缓存"}


@router.post("/api/thumbnail/clear-all")
async def clear_all_thumbnails():
    """清除所有缩略图缓存"""
    thumbnail_service = get_thumbnail_service()
    thumbnail_service.clear_cache()
    return {"status": "ok", "message": "已清除所有缩略图缓存"}
