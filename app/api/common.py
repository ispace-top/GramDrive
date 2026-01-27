from __future__ import annotations

import logging
from typing import Any

from fastapi import HTTPException, Request

from .. import database
from ..core.config import get_active_password
from .auth import COOKIE_NAME

logger = logging.getLogger(__name__)


def error_payload(message: str, *, code: str = "error", details: Any | None = None) -> dict:
    payload = {"status": "error", "code": code, "message": message}
    if details is not None:
        payload["details"] = details
    return payload


def http_error(status_code: int, message: str, *, code: str = "error", details: Any | None = None) -> HTTPException:
    return HTTPException(status_code=status_code, detail=error_payload(message, code=code, details=details))


def ensure_upload_auth(request: Request, app_settings: dict, submitted_key: str | None) -> None:
    picgo_api_key = app_settings.get("PICGO_API_KEY")
    web_password_set = bool(app_settings.get("PASS_WORD") or get_active_password())

    # 检查会话认证
    session_id = request.cookies.get(COOKIE_NAME)
    is_authenticated_via_session = session_id and database.get_session(session_id)

    # 检查 API Key 认证
    is_authenticated_via_api_key = picgo_api_key and (picgo_api_key == submitted_key)

    # 场景 1: 完全开放 (无密码, 无 PicGo API Key)
    if not web_password_set and not picgo_api_key:
        return

    # 场景 2: 已通过会话认证 (优先考虑)
    if is_authenticated_via_session:
        return

    # 场景 3: 已通过 API Key 认证
    if is_authenticated_via_api_key:
        return

    # 如果到达这里，说明会话和 API Key 认证都未通过
    # 根据配置，抛出特定的错误
    if web_password_set: # 如果设置了网页密码，但未通过会话认证
        raise http_error(401, "需要网页登录", code="login_required")

    if picgo_api_key: # 如果设置了 PicGo API Key，但未通过 API Key 认证
        raise http_error(401, "无效的 API 密钥", code="invalid_api_key")

    # 默认 fallback，理论上不应该到达这里，除非既没有密码也没有 API Key (已在场景1处理)
    # 或者配置有问题
    raise http_error(401, "未经授权的上传请求", code="unauthorized_upload")


