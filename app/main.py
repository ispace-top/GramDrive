import logging
import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.middleware.proxy_fix import ProxyFixMiddleware

# 导入我们的新生命周期管理器和路由
from .core.http_client import lifespan
from .api import routes as api_routes
from .pages import router as pages_router
from .core.config import get_active_password, get_app_settings
from .api.common import error_payload
from . import database

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

# 使用集成的 lifespan 管理器创建 FastAPI 应用
app = FastAPI(
    lifespan=lifespan,
    title="Gram Drive",
    description="一个基于 Telegram 的个人网盘服务。",
    version="2.0.0"
)

# 添加 ProxyFixMiddleware - 这必须是第一个中间件，用于正确处理反向代理的请求
# 这个中间件会读取 X-Forwarded-* 头信息并修复请求对象中的 scheme、client、host 等
app.add_middleware(
    ProxyFixMiddleware,
    trusted_hosts=["*"],  # 在生产环境中建议限制具体的主机
)

COOKIE_NAME = "tgstate_session"

@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """
    Add security headers to all responses.
    """
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    
    # 简单的 Permissions-Policy
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=(), payment=(), usb=()"
    
    # Strict-Transport-Security (HSTS)
    # Only if HTTPS
    if request.url.scheme == "https" or request.headers.get("x-forwarded-proto") == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
    return response

@app.middleware("http")
async def check_configured_middleware(request: Request, call_next):
    """
    中间件 1: 检查应用是否已配置
    如果未配置（即未设置密码），则强制所有流量到引导页面。
    """
    settings = get_app_settings()
    has_password = bool((settings.get("PASS_HASH") or settings.get("PASS_WORD") or "").strip())
    
    request_path = request.url.path

    # 如果没有设置密码，说明是首次运行或重置了
    if not has_password:
        # 允许访问引导页、设置页以及其所需的 API 和静态资源
        logging.info(f"【配置检查】没有设置密码，说明是首次运行或重置了.请求Path: {request.url.path}")
        allowed_paths = ["/welcome", "/settings", "/static", "/api/auth/login", "/api/app-config/apply", "/api/set-password", "/favicon.ico"]
        if not any(request_path.startswith(p) for p in allowed_paths):
            logging.info(f"【重定向】未配置的请求 {request_path} -> /welcome")
            return RedirectResponse(url="/welcome", status_code=307)
    
    # 如果已经设置了密码，此中间件不做任何事情，直接传递给下一个中间件处理会话认证
    return await call_next(request)


@app.middleware("http")
async def session_auth_middleware(request: Request, call_next):
    """
    中间件 2: 处理用户会话认证
    这个中间件只在应用已经配置好密码后才起作用。
    """
    settings = get_app_settings()
    has_password = bool((settings.get("PASS_HASH") or settings.get("PASS_WORD") or "").strip())

    # 如果没设置密码，则这个中间件不做任何事
    if not has_password:
        logging.info(f"【用户会话认证】没有设置密码，这个中间件不做任何事.请求Path: {request.url.path}")
        return await call_next(request)

    request_path = request.url.path
    
    # 定义需要认证才能访问的 API 路由
    protected_api_prefixes = (
        "/api/upload", 
        "/api/delete", 
        "/api/files", 
        "/api/batch_delete", 
        "/api/app-config", 
        "/api/reset-config",
        "/api/set-password",
        "/api/stats",
        "/api/downloads"
    )

    # 定义需要认证才能访问的页面
    protected_pages = ["/", "/image_hosting", "/settings", "/stats", "/downloads"]
    
    # 检查会话 cookie
    session_id = request.cookies.get(COOKIE_NAME)
    is_authenticated = False
    if session_id and database.get_session(session_id):
        is_authenticated = True

    # 如果已登录用户访问登录页，重定向到主页
    if is_authenticated and (request_path == "/login" or request_path == "/pwd"):
        logging.info(f"【重定向】已登录用户访问登录页 {request_path} -> /")
        return RedirectResponse(url="/", status_code=307)

    # 如果未登录用户访问受保护的 API
    if not is_authenticated and any(request_path.startswith(prefix) for prefix in protected_api_prefixes):
        # PicGo API key 是个例外，允许通过 key 进行认证
        if request_path.startswith('/api/upload') and request.headers.get('x-api-key'):
             pass # 让后续的依赖注入去处理 key 的验证
        else:
            return JSONResponse(
                status_code=401,
                content={"detail": error_payload("需要网页登录", code="login_required")},
            )

    # 如果未登录用户访问受保护的页面
    if not is_authenticated and request_path in protected_pages:
        logging.info(f"【重定向】未登录用户访问受保护页面 {request_path} -> /login")
        return RedirectResponse(url="/login", status_code=307)
        
    return await call_next(request)

# 挂载静态文件目录
# 注意：这个路径是相对于项目根目录的
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 设置模板目录
# 注意：这个路径也是相对于项目根目录的
templates = Jinja2Templates(directory="app/templates")

# 包含 API 和页面路由
app.include_router(api_routes.router)
app.include_router(pages_router)
