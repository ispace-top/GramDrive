from fastapi import APIRouter, Response, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from ..core.config import get_active_password

router = APIRouter()

class LoginRequest(BaseModel):
    password: str

COOKIE_NAME = "tgstate_session"

@router.post("/api/auth/login")
async def login(payload: LoginRequest, response: Response):
    active_password = get_active_password()
    if payload.password == active_password:
        # 登录成功，设置 Cookie
        response = JSONResponse(content={"status": "ok", "message": "Login successful"})
        response.set_cookie(
            key=COOKIE_NAME,
            value=payload.password,
            httponly=True,
            samesite="Lax",
            path="/",
            # secure=True # 如果是 HTTPS 环境应该加上
        )
        return response
    else:
        return JSONResponse(status_code=401, content={"status": "error", "message": "Invalid password"})

@router.post("/api/auth/logout")
async def logout(response: Response):
    # 登出，清除 Cookie
    # 返回 204 No Content
    response = Response(status_code=204)
    response.delete_cookie(key=COOKIE_NAME, path="/", httponly=True, samesite="Lax")
    return response
