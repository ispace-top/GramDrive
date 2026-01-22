import logging
import httpx
from contextlib import asynccontextmanager
from fastapi import FastAPI
import asyncio

# 导入应用所需的其他模块
from .. import database
from ..bot_handler import create_bot_app
from ..core.config import get_app_settings
from ..services.download_service import DownloadService, get_download_service # New import
from ..services.telegram_service import get_telegram_service # New import, needed for DownloadService

logger = logging.getLogger(__name__)

# 这个变量将持有我们全局共享的客户端实例
http_client: httpx.AsyncClient | None = None

def _is_bot_ready(app_settings: dict) -> bool:
    return bool((app_settings.get("BOT_TOKEN") or "").strip() and (app_settings.get("CHANNEL_NAME") or "").strip())

async def _stop_bot(app: FastAPI) -> None:
    if hasattr(app.state, "bot_app") and app.state.bot_app:
        logger.info("正在停止机器人...")
        try:
            # shutdown() 是一个全面的清理方法，它应该会处理好 updater 和其他组件
            await app.state.bot_app.shutdown()
            logger.info("机器人已成功关闭")
        except Exception as e:
            # 如果关闭失败，记录详细错误，这对于调试至关重要
            logger.error("停止机器人时发生错误: %s", e, exc_info=True)
        finally:
            # 无论成功与否，都清理掉状态
            app.state.bot_app = None

async def _start_bot(app: FastAPI, app_settings: dict) -> None:
    await _stop_bot(app)
    bot_app = create_bot_app(app_settings)
    app.state.bot_app = bot_app
    try:
        await bot_app.initialize()

        # 强制删除webhook和清理旧连接
        logger.info("正在清理Telegram Bot旧连接...")
        await bot_app.bot.delete_webhook(drop_pending_updates=True)

        # 等待2秒让Telegram服务器完全清理
        import asyncio
        await asyncio.sleep(2)

        await bot_app.start()
        await bot_app.updater.start_polling(drop_pending_updates=True)
        logger.info("机器人已在后台启动并开始轮询。")
        app.state.bot_error = None
        app.state.bot_ready = True
    except Exception as e:
        logger.error(f"启动机器人失败: {e}", exc_info=True)
        app.state.bot_error = str(e)
        app.state.bot_app = None
        app.state.bot_ready = False
        if "Conflict" in str(e):
            logger.warning("Bot 启动冲突！可能的原因：")
            logger.warning("1. 有多个应用实例在运行")
            logger.warning("2. 旧的Bot实例还没有完全关闭")
            logger.warning("3. 在其他地方（如开发环境）也在运行同一个Bot")
            logger.warning("建议：停止所有容器，等待10秒后重新启动")

async def apply_runtime_settings(app: FastAPI, *, start_bot: bool = True) -> None:
    async with app.state.settings_lock:
        current = get_app_settings()
        app.state.app_settings = current
        bot_ready = _is_bot_ready(current)
        app.state.bot_ready = bot_ready
        app.state.bot_error = None

        if not start_bot:
            return

        if bot_ready:
            try:
                await _start_bot(app, current)
            except Exception as e:
                logger.error("应用配置已应用，但启动机器人失败: %s", e)
                app.state.bot_error = str(e)
                await _stop_bot(app)
        else:
            await _stop_bot(app)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理器。
    在应用启动时：
    1. 初始化数据库。
    2. 创建并启动 Telegram Bot。
    3. 创建一个共享的、支持高并发的 httpx.AsyncClient。
    在应用关闭时：
    1. 优雅地关闭 httpx.AsyncClient。
    2. 优雅地停止 Telegram Bot。
    """
    # --- 启动逻辑 ---
    logger.info("应用启动")
    
    # 1. 初始化数据库
    database.init_db()
    logger.info("数据库已初始化")

    app.state.settings_lock = asyncio.Lock()
    app.state.app_settings = get_app_settings()
    app.state.bot_ready = _is_bot_ready(app.state.app_settings)

    # 2. 创建共享的 httpx.AsyncClient
    global http_client
    limits = httpx.Limits(max_connections=500, max_keepalive_connections=100)  # 增加连接池大小
    http_client = httpx.AsyncClient(timeout=300.0, limits=limits)
    logger.info("共享的 HTTP 客户端已创建")

    # 3. 启动 Telegram Bot（仅在 BOT_TOKEN + CHANNEL_NAME 都存在时）
    if app.state.bot_ready:
        try:
            await _start_bot(app, app.state.app_settings)
        except Exception as e:
            logger.error("启动机器人失败: %s", e)
            app.state.bot_app = None
            app.state.bot_error = str(e)

    # 4. 初始化并启动 DownloadService (只要配置了 Bot 就可以启动)
    if app.state.bot_ready:
        try:
            telegram_service = get_telegram_service()
            download_service_instance = await get_download_service(telegram_service, http_client)
            app.state.download_service = download_service_instance
            await download_service_instance.start()
            logger.info("【下载服务】已启动，使用共享的 HTTP 连接池")
        except Exception as e:
            logger.error("启动 DownloadService 失败: %s", e, exc_info=True)
            app.state.download_service = None

    yield # 应用在此处运行

    # --- 关闭逻辑 ---
    logger.info("应用关闭")

    # 1. 关闭共享的 httpx.AsyncClient
    if http_client:
        await http_client.aclose()
        logger.info("共享的 HTTP 客户端已关闭")

    # 2. 停止 DownloadService
    if hasattr(app.state, "download_service") and app.state.download_service:
        await app.state.download_service.stop()

    # 3. 停止 Telegram Bot
    await _stop_bot(app)


def get_http_client() -> httpx.AsyncClient:
    """
    一个 FastAPI 依赖项，用于获取共享的 httpx 客户端实例。
    """
    if http_client is None:
        raise RuntimeError("HTTP client is not initialized. Is the app lifespan configured correctly?")
    return http_client
