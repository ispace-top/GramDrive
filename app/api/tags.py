from __future__ import annotations

import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..core.config import Settings, get_settings
from .. import database
from .common import http_error

router = APIRouter()
logger = logging.getLogger(__name__)


class TagRequest(BaseModel):
    file_id: str
    tag: str


class TagsRequest(BaseModel):
    file_id: str
    tags: list[str]


@router.post("/api/tags/add")
async def add_tag(request: TagRequest, settings: Settings = Depends(get_settings)):
    """为文件添加单个标签"""
    success = database.add_file_tag(request.file_id, request.tag)
    if not success:
        raise http_error(400, "标签已存在或文件不存在", code="tag_exists")
    return {"status": "success", "message": "标签添加成功"}


@router.post("/api/tags/batch-add")
async def batch_add_tags(request: TagsRequest, settings: Settings = Depends(get_settings)):
    """为文件批量添加标签"""
    added = []
    failed = []
    for tag in request.tags:
        if database.add_file_tag(request.file_id, tag):
            added.append(tag)
        else:
            failed.append(tag)

    return {
        "status": "success",
        "added": added,
        "failed": failed,
        "message": f"成功添加 {len(added)} 个标签"
    }


@router.delete("/api/tags/remove")
async def remove_tag(request: TagRequest, settings: Settings = Depends(get_settings)):
    """移除文件的标签"""
    success = database.remove_file_tag(request.file_id, request.tag)
    if not success:
        raise http_error(404, "标签不存在", code="tag_not_found")
    return {"status": "success", "message": "标签移除成功"}


@router.get("/api/tags/file/{file_id}")
async def get_file_tags(file_id: str, settings: Settings = Depends(get_settings)):
    """获取文件的所有标签"""
    tags = database.get_file_tags(file_id)
    return {"file_id": file_id, "tags": tags}


@router.get("/api/tags/all")
async def get_all_tags(settings: Settings = Depends(get_settings)):
    """获取所有标签及其使用次数"""
    tags = database.get_all_tags()
    return {"tags": tags}


@router.get("/api/tags/search/{tag}")
async def search_by_tag(tag: str, settings: Settings = Depends(get_settings)):
    """根据标签搜索文件"""
    file_ids = database.get_files_by_tag(tag)

    files = []
    for file_id in file_ids:
        file_data = database.get_file_by_id(file_id)
        if file_data:
            file_data["tags"] = database.get_file_tags(file_id)
            files.append(file_data)

    return {
        "tag": tag,
        "count": len(files),
        "files": files
    }
