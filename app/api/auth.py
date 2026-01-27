import secrets

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .. import database
from ..core.config import get_active_password
from ..core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()

class LoginRequest(BaseModel):
    password: str

COOKIE_NAME = "tgstate_session"

@router.post("/api/auth/login")
async def login(payload: LoginRequest, response: Response):
    active_password = get_active_password()
    # 确保密码比对时处理两端空格，避免复制粘贴带来的隐形字符问题
    input_pwd = payload.password.strip()
    stored_pwd = (active_password or "").strip()

    if input_pwd and input_pwd == stored_pwd:
        # 登录成功，生成会话ID并创建会话
        session_id = secrets.token_urlsafe(32)
        database.create_session(session_id, expires_in_hours=24)

        logger.info(f"【登录】用户登录成功。会话ID: {session_id[:8]}...")
        response = JSONResponse(content={"status": "ok", "message": "登录成功"})
        # 设置 Cookie，存储会话ID而不是密码
        response.set_cookie(
            key=COOKIE_NAME,
            value=session_id,
            httponly=True,
            samesite="Lax",
            path="/",
            secure=False # 兼容非 HTTPS 环境
        )
        return response
    else:
        logger.warning("【登录】登录失败：密码错误")
        return JSONResponse(status_code=401, content={"status": "error", "message": "密码错误"})

@router.post("/api/auth/logout")
async def logout(request: Request):
    # 登出，清除 Cookie 和数据库中的会话
    session_id = request.cookies.get(COOKIE_NAME)
    if session_id:
        database.delete_session(session_id)
        logger.info(f"【登出】用户登出成功。会话ID: {session_id[:8]}...")
    else:
        logger.debug("【登出】登出请求，但无会话信息")

    response = JSONResponse(content={"status": "ok", "message": "已退出登录"})
    response.delete_cookie(key=COOKIE_NAME, path="/", httponly=True, samesite="Lax")
    return response
