from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    应用程序设置。
    """
    BOT_TOKEN: str | None = None
    CHANNEL_NAME: str | None = None
    PASS_WORD: str | None = None
    PICGO_API_KEY: str | None = None # [可选] PicGo 上传接口的 API 密钥
    BASE_URL: str = "http://127.0.0.1:8000"
    MODE: str = "p" # p 代表公开模式, m 代表私有模式
    FILE_ROUTE: str = "/d/"


@lru_cache
def get_settings() -> Settings:
    """
    获取应用程序设置。

    此函数会被缓存，以避免在每个请求中都从环境中重新读取设置。
    """
    return Settings()

def get_active_password() -> str | None:
    """
    获取当前有效的密码。
    优先从数据库读取，如果为空则回退到环境变量。
    过滤掉常见的占位符值。
    """
    # 定义占位符列表
    PLACEHOLDER_VALUES = {
        "your_secret_password",
        "your_password",
        "password",
        "change_me",
        "changeme",
        "your-password",
    }

    try:
        from .. import database

        db_settings = database.get_app_settings_from_db()
        password = (db_settings.get("PASS_WORD") or "").strip()
        if password and password.lower() not in PLACEHOLDER_VALUES:
            return password
    except Exception:
        pass

    env_password = (get_settings().PASS_WORD or "").strip()
    if env_password and env_password.lower() not in PLACEHOLDER_VALUES:
        return env_password

    return None

def get_app_settings() -> dict:
    """
    获取当前生效的应用设置（数据库优先，环境变量兜底）。
    返回字段: BOT_TOKEN, CHANNEL_NAME, PASS_WORD, PICGO_API_KEY, BASE_URL
    过滤掉常见的占位符值。
    """
    # 定义占位符列表
    TOKEN_PLACEHOLDERS = {
        "your_telegram_bot_token",
        "your_bot_token",
        "bot_token",
        "token",
    }
    CHANNEL_PLACEHOLDERS = {
        "@your_telegram_channel_or_your_id",
        "@your_channel",
        "your_channel",
        "channel_name",
    }
    PASSWORD_PLACEHOLDERS = {
        "your_secret_password",
        "your_password",
        "password",
        "change_me",
        "changeme",
    }
    API_KEY_PLACEHOLDERS = {
        "your_picgo_api_key",
        "your_api_key",
        "api_key",
    }

    def filter_placeholder(value, placeholders):
        """过滤占位符，如果是占位符则返回 None"""
        if not value:
            return None
        value_str = str(value).strip()
        if not value_str or value_str.lower() in placeholders:
            return None
        return value_str

    env = get_settings()
    try:
        from .. import database
        db_settings = database.get_app_settings_from_db()
    except Exception:
        db_settings = {}

    return {
        "BOT_TOKEN": filter_placeholder(
            db_settings.get("BOT_TOKEN") or env.BOT_TOKEN,
            TOKEN_PLACEHOLDERS
        ),
        "CHANNEL_NAME": filter_placeholder(
            db_settings.get("CHANNEL_NAME") or env.CHANNEL_NAME,
            CHANNEL_PLACEHOLDERS
        ),
        "PASS_WORD": filter_placeholder(
            db_settings.get("PASS_WORD") or env.PASS_WORD,
            PASSWORD_PLACEHOLDERS
        ),
        "PICGO_API_KEY": filter_placeholder(
            db_settings.get("PICGO_API_KEY") or env.PICGO_API_KEY,
            API_KEY_PLACEHOLDERS
        ),
        "BASE_URL": (db_settings.get("BASE_URL") or env.BASE_URL),
    }
