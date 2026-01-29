import os
import random
import sqlite3
import string
import threading
from datetime import datetime, timedelta

from .core.logging_config import get_logger

# 使用绝对路径，确保 Docker 环境正常工作
DATA_DIR = os.getenv("DATA_DIR", "/app/data")
os.makedirs(DATA_DIR, exist_ok=True)
DATABASE_URL = os.path.join(DATA_DIR, "file_metadata.db")

logger = get_logger(__name__)

# 使用线程锁来确保多线程环境下的数据库访问安全
db_lock = threading.Lock()

def get_db_connection() -> sqlite3.Connection:
    """获取数据库连接。"""
    conn = sqlite3.connect(DATABASE_URL, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def generate_short_id(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def init_db() -> None:
    """初始化数据库，创建表。"""
    with db_lock:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    file_id TEXT NOT NULL UNIQUE,
                    filesize INTEGER NOT NULL,
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    short_id TEXT UNIQUE,
                    local_path TEXT,
                    download_count INTEGER DEFAULT 0,
                    mime_type TEXT
                );
            """)

            # 检查新列是否存在，不存在则添加
            cursor.execute("PRAGMA table_info(files)")
            columns = [info[1] for info in cursor.fetchall()]

            if "short_id" not in columns:
                logger.info("数据库迁移: 正在添加 short_id 列...")
                try:
                    cursor.execute("ALTER TABLE files ADD COLUMN short_id TEXT")
                except Exception as e:
                    logger.error("迁移警告：添加 short_id 列失败: %s", e)

            if "local_path" not in columns:
                logger.info("数据库迁移: 正在添加 local_path 列...")
                try:
                    cursor.execute("ALTER TABLE files ADD COLUMN local_path TEXT")
                except Exception as e:
                    logger.error("迁移警告：添加 local_path 列失败: %s", e)

            if "download_count" not in columns:
                logger.info("数据库迁移: 正在添加 download_count 列...")
                try:
                    cursor.execute("ALTER TABLE files ADD COLUMN download_count INTEGER DEFAULT 0")
                except Exception as e:
                    logger.error("迁移警告：添加 download_count 列失败: %s", e)

            if "mime_type" not in columns:
                logger.info("数据库迁移: 正在添加 mime_type 列...")
                try:
                    cursor.execute("ALTER TABLE files ADD COLUMN mime_type TEXT")
                except Exception as e:
                    logger.error("迁移警告：添加 mime_type 列失败: %s", e)

            # 确保唯一索引存在
            try:
                cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_files_short_id ON files(short_id)")
            except Exception as e:
                logger.error("迁移警告：创建索引 idx_files_short_id 失败: %s", e)

            # 创建文件标签表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS file_tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id TEXT NOT NULL,
                    tag TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(file_id, tag),
                    FOREIGN KEY(file_id) REFERENCES files(file_id) ON DELETE CASCADE
                );
            """)

            # 创建标签索引以便快速查询
            try:
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_file_tags_tag ON file_tags(tag)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_file_tags_file_id ON file_tags(file_id)")
            except Exception as e:
                logger.error("创建标签索引失败: %s", e)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS app_settings (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    bot_token TEXT,
                    channel_name TEXT,
                    pass_word TEXT,
                    picgo_api_key TEXT,
                    base_url TEXT,
                    auto_download_enabled INTEGER DEFAULT 1,
                    download_dir TEXT DEFAULT '/app/downloads',
                    download_file_types TEXT DEFAULT 'image,video',
                    download_max_size INTEGER DEFAULT 52428800,
                    download_min_size INTEGER DEFAULT 0
                );
            """)

            # 检查app_settings新列
            cursor.execute("PRAGMA table_info(app_settings)")
            settings_columns = [info[1] for info in cursor.fetchall()]

            if "auto_download_enabled" not in settings_columns:
                logger.info("正在将 auto_download_enabled 添加到 app_settings...")
                try:
                    cursor.execute("ALTER TABLE app_settings ADD COLUMN auto_download_enabled INTEGER DEFAULT 1")
                    # 更新现有记录为启用状态
                    cursor.execute("UPDATE app_settings SET auto_download_enabled = 1 WHERE auto_download_enabled IS NULL")
                except Exception as e:
                    logger.error("添加 auto_download_enabled 失败: %s", e)

            if "download_dir" not in settings_columns:
                logger.info("正在将 download_dir 添加到 app_settings...")
                try:
                    cursor.execute("ALTER TABLE app_settings ADD COLUMN download_dir TEXT DEFAULT '/app/downloads'")
                except Exception as e:
                    logger.error("添加 download_dir 失败: %s", e)

            if "download_file_types" not in settings_columns:
                logger.info("正在将 download_file_types 添加到 app_settings...")
                try:
                    cursor.execute("ALTER TABLE app_settings ADD COLUMN download_file_types TEXT DEFAULT 'image,video'")
                except Exception as e:
                    logger.error("添加 download_file_types 失败: %s", e)

            if "download_max_size" not in settings_columns:
                logger.info("正在将 download_max_size 添加到 app_settings...")
                try:
                    cursor.execute("ALTER TABLE app_settings ADD COLUMN download_max_size INTEGER DEFAULT 52428800")
                except Exception as e:
                    logger.error("添加 download_max_size 失败: %s", e)

            if "download_min_size" not in settings_columns:
                logger.info("正在将 download_min_size 添加到 app_settings...")
                try:
                    cursor.execute("ALTER TABLE app_settings ADD COLUMN download_min_size INTEGER DEFAULT 0")
                except Exception as e:
                    logger.error("添加 download_min_size 失败: %s", e)

            if "download_threads" not in settings_columns:
                logger.info("正在将 download_threads 添加到 app_settings...")
                try:
                    cursor.execute("ALTER TABLE app_settings ADD COLUMN download_threads INTEGER DEFAULT 4")
                except Exception as e:
                    logger.error("添加 download_threads 失败: %s", e)

            # 确保存在单行设置记录，并默认启用自动下载
            cursor.execute("INSERT OR IGNORE INTO app_settings (id, auto_download_enabled) VALUES (1, 1)")
            # 如果记录已存在但 auto_download_enabled 为 NULL 或 0，更新为 1
            cursor.execute("UPDATE app_settings SET auto_download_enabled = 1 WHERE id = 1 AND auto_download_enabled = 0")

            # 创建会话表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL
                );
            """)

            # 创建过期时间索引以便快速清理过期会话
            try:
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at)")
            except Exception as e:
                logger.error("创建索引 idx_sessions_expires_at 失败: %s", e)

            conn.commit()
            logger.info("数据库已成功初始化")
        finally:
            conn.close()

# 辅助函数，用于将 mime 类型映射到分类
def _get_file_category_from_mime(mime_type: str | None, filename: str | None = None) -> str:
    """
    根据 mime_type 或文件名推断文件类型。
    如果 mime_type 为空，尝试从文件扩展名推断。

    Returns:
        文件类别（英文）: "image", "video", "audio", "document", "other"
    """
    # 先尝试从 mime_type 推断
    if mime_type:
        if mime_type.startswith("image/"):
            return "image"
        if mime_type.startswith("video/"):
            return "video"
        if mime_type.startswith("audio/"):
            return "audio"
        if mime_type in ["application/pdf", "application/msword",
                        "application/vnd.ms-excel", "application/vnd.ms-powerpoint",
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        "application/vnd.openxmlformats-officedocument.presentationml.presentation"]:
            return "document"

    # 如果 mime_type 为空或无法识别，尝试从文件扩展名推断
    if filename:
        filename_lower = filename.lower()
        # 图片扩展名
        if any(filename_lower.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.ico']):
            return "image"
        # 视频扩展名
        if any(filename_lower.endswith(ext) for ext in ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.webm', '.m4v', '.3gp', '.3g2']):
            return "video"
        # 音频扩展名
        if any(filename_lower.endswith(ext) for ext in ['.mp3', '.wav', '.aac', '.flac', '.ogg', '.wma', '.m4a', '.opus']):
            return "audio"
        # 文档扩展名
        if any(filename_lower.endswith(ext) for ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']):
            return "document"

    return "other"


def get_all_files(category: str | None = None, sort_by: str | None = None, sort_order: str | None = None, local_only: bool = False) -> list[dict]:
    """
    从数据库中获取所有文件的元数据，支持按类别、排序字段和排序顺序过滤。

    Args:
        category: 文件类别，支持英文（image, video, audio, document, other）或中文（图片, 视频, 音频, 文档, 其他）
        sort_by: 排序字段（filename, filesize, upload_date）
        sort_order: 排序顺序（asc, desc）
        local_only: 是否只返回本地已下载的文件（默认 False，显示所有文件）
    """
    with db_lock:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()

            query = "SELECT filename, file_id, filesize, upload_date, short_id, mime_type, local_path FROM files"
            params = []

            where_clauses = []

            # 本地优先：只返回已下载的文件
            if local_only:
                where_clauses.append("local_path IS NOT NULL AND local_path != '' AND local_path NOT LIKE '__%%'")

            if category:
                # 支持英文和中文 category 参数
                category_lower = category.lower()

                if category_lower in ("image", "图片"):
                    where_clauses.append("mime_type LIKE 'image/%'")
                elif category_lower in ("video", "视频"):
                    where_clauses.append("mime_type LIKE 'video/%'")
                elif category_lower in ("audio", "音频"):
                    where_clauses.append("mime_type LIKE 'audio/%'")
                elif category_lower in ("document", "文档"):
                    where_clauses.append("mime_type IN ('application/pdf', 'application/msword', 'application/vnd.ms-excel', 'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.openxmlformats-officedocument.presentationml.presentation')")
                elif category_lower in ("other", "其他"):
                    # For 'other', filter out known types that have specific categories
                    known_mime_types = [
                        "image/%", "video/%", "audio/%", "application/pdf", "application/msword",
                        "application/vnd.ms-excel", "application/vnd.ms-powerpoint",
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        "application/vnd.openxmlformats-officedocument.presentationml.presentation"
                    ]
                    # Construct NOT LIKE and NOT IN clauses
                    not_like_clauses = [f"mime_type NOT LIKE '{mt}'" for mt in ["image/%", "video/%", "audio/%"]]
                    not_in_clauses = [f"mime_type NOT IN ({', '.join(['?' for _ in known_mime_types[3:]])})"]
                    where_clauses.append(f"(mime_type IS NULL OR ({' AND '.join(not_like_clauses)} AND {not_in_clauses[0]}))")
                    params.extend(known_mime_types[3:])


            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)

            order_map = {
                "filename": "filename",
                "filesize": "filesize",
                "upload_date": "upload_date"
            }
            # Default sort_by and sort_order if not provided
            safe_sort_by = order_map.get(sort_by, "upload_date")
            safe_sort_order = "DESC" # Default

            if sort_order and sort_order.lower() == "asc":
                safe_sort_order = "ASC"
            # else remains "DESC"

            query += f" ORDER BY {safe_sort_by} {safe_sort_order}"

            cursor.execute(query, params)
            files = []
            for row in cursor.fetchall():
                d = dict(row)
                files.append(d)
            return files
        finally:
            conn.close()

def add_file_metadata(filename: str, file_id: str, filesize: int, mime_type: str = None) -> str:
    """
    向数据库中添加一个新的文件元数据记录。
    如果 file_id 已存在，则忽略。
    返回: short_id
    """
    with db_lock:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()

            # 尝试生成唯一的 short_id
            for attempt in range(5):
                short_id = generate_short_id()
                try:
                    cursor.execute(
                        "INSERT INTO files (filename, file_id, filesize, short_id, mime_type) VALUES (?, ?, ?, ?, ?)",
                        (filename, file_id, filesize, short_id, mime_type)
                    )
                    conn.commit()
                    logger.info(f"【数据库】文件元数据已添加。文件名: {filename}，short_id: {short_id}，文件大小: {filesize} bytes")
                    return short_id
                except sqlite3.IntegrityError as e:
                    if "short_id" in str(e):
                        logger.debug(f"【数据库】short_id 冲突，重试 (尝试 {attempt + 1}/5)。生成的ID: {short_id}")
                        continue # 冲突重试
                    # 可能是 file_id 冲突，如果是这样，查询现有的 short_id
                    cursor.execute("SELECT short_id FROM files WHERE file_id = ?", (file_id,))
                    row = cursor.fetchone()
                    if row and row[0]:
                        logger.info(f"【数据库】文件已存在，返回现有的 short_id: {row[0]}")
                        return row[0]
                    # 如果有记录但没 short_id (旧数据)，更新它
                    if row:
                        short_id = generate_short_id()
                        cursor.execute("UPDATE files SET short_id = ? WHERE file_id = ?", (short_id, file_id))
                        conn.commit()
                        logger.info(f"【数据库】为旧记录补充 short_id。文件名: {filename}，short_id: {short_id}")
                        return short_id
                    logger.error(f"【数据库】file_id 冲突但记录不存在。file_id: {file_id}")
                    raise e

            # 如果多次重试失败（极低概率），抛错
            logger.error(f"【数据库】生成唯一 short_id 失败，已重试 5 次。文件名: {filename}")
            raise Exception("Failed to generate unique short_id")

        finally:
            conn.close()

def get_file_by_id(identifier: str) -> dict | None:
    """通过 file_id 或 short_id 从数据库中获取单个文件元数据。"""
    with db_lock:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            logger.debug(f"【数据库】查询文件。标识符: {identifier}")
            cursor.execute("SELECT filename, filesize, upload_date, file_id, short_id FROM files WHERE short_id = ? OR file_id = ?", (identifier, identifier))
            result = cursor.fetchone()
            if result:
                logger.debug(f"【数据库】文件查询成功。文件名: {result['filename']}，file_id: {result['file_id'][:20]}...，short_id: {result['short_id']}")
                return {
                    "filename": result["filename"],
                    "filesize": result["filesize"],
                    "upload_date": result["upload_date"],
                    "file_id": result["file_id"],
                    "short_id": result["short_id"]
                }
            logger.debug(f"【数据库】文件未找到。标识符: {identifier}")
            return None
        finally:
            conn.close()

def delete_file_metadata(file_id: str) -> bool:
    """
    根据 file_id 从数据库中删除文件元数据。
    返回: 如果成功删除了一行，则为 True，否则为 False。
    """
    with db_lock:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            # 先查询文件信息用于日志
            cursor.execute("SELECT filename FROM files WHERE file_id = ?", (file_id,))
            file_row = cursor.fetchone()
            filename = file_row['filename'] if file_row else 'unknown'

            cursor.execute("DELETE FROM files WHERE file_id = ?", (file_id,))
            conn.commit()
            # cursor.rowcount 会返回受影响的行数
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"【数据库】文件元数据已删除。文件名: {filename}，file_id: {file_id[:20]}...")
            else:
                logger.warning(f"【数据库】文件元数据删除失败（未找到）。file_id: {file_id[:20]}...")
            return deleted
        finally:
            conn.close()

def delete_file_by_message_id(message_id: int) -> str | None:
    """
    根据 message_id 从数据库中删除文件元数据，并返回其 file_id。
    因为一个消息ID只对应一个文件，所以我们可以这样做。
    """
    file_id_to_delete = None
    with db_lock:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            # 首先，根据 message_id 找到对应的 file_id
            # 我们使用 LIKE 操作符，因为 file_id 是 "message_id:actual_file_id" 的格式
            cursor.execute("SELECT file_id FROM files WHERE file_id LIKE ?", (f"{message_id}:%",))
            result = cursor.fetchone()
            if result:
                file_id_to_delete = result[0]
                # 然后，删除这条记录
                cursor.execute("DELETE FROM files WHERE file_id = ?", (file_id_to_delete,))
                conn.commit()
                logger.info("已从数据库中删除与消息ID %s 关联的文件: %s", message_id, file_id_to_delete)
            return file_id_to_delete
        finally:
            conn.close()

def get_app_settings_from_db() -> dict:
    """获取应用设置（从数据库单行配置）。"""
    with db_lock:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT bot_token, channel_name, pass_word, picgo_api_key, base_url,
                       auto_download_enabled, download_dir, download_file_types, download_max_size, download_min_size,
                       download_threads
                FROM app_settings WHERE id = 1
            """)
            row = cursor.fetchone()
            if not row:
                return {}
            return {
                "BOT_TOKEN": row[0],
                "CHANNEL_NAME": row[1],
                "PASS_WORD": row[2],
                "PICGO_API_KEY": row[3],
                "BASE_URL": row[4],
                "AUTO_DOWNLOAD_ENABLED": bool(row[5]) if row[5] is not None else False,
                "DOWNLOAD_DIR": row[6] or "/app/downloads",
                "DOWNLOAD_FILE_TYPES": row[7] or "image,video",
                "DOWNLOAD_MAX_SIZE": row[8] or 10737418240,  # 10GB
                "DOWNLOAD_MIN_SIZE": row[9] or 0,
                "DOWNLOAD_THREADS": row[10] or 4,
            }
        finally:
            conn.close()

def save_app_settings_to_db(payload: dict) -> None:
    """保存应用设置到数据库（单行更新）。"""
    with db_lock:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            def norm(v):
                if v is None:
                    return None
                if isinstance(v, str):
                    s = v.strip()
                    return s if s else None
                return v

            cursor.execute(
                """
                UPDATE app_settings
                SET bot_token = ?, channel_name = ?, pass_word = ?, picgo_api_key = ?, base_url = ?,
                    auto_download_enabled = ?, download_dir = ?, download_file_types = ?, download_max_size = ?, download_min_size = ?,
                    download_threads = ?
                WHERE id = 1
                """,
                (
                    norm(payload.get("BOT_TOKEN")),
                    norm(payload.get("CHANNEL_NAME")),
                    norm(payload.get("PASS_WORD")),
                    norm(payload.get("PICGO_API_KEY")),
                    norm(payload.get("BASE_URL")),
                    1 if payload.get("AUTO_DOWNLOAD_ENABLED") else 0,
                    norm(payload.get("DOWNLOAD_DIR")) or "/app/downloads",
                    norm(payload.get("DOWNLOAD_FILE_TYPES")) or "image,video",
                    payload.get("DOWNLOAD_MAX_SIZE") if payload.get("DOWNLOAD_MAX_SIZE") is not None else 10737418240,  # 10GB
                    payload.get("DOWNLOAD_MIN_SIZE") if payload.get("DOWNLOAD_MIN_SIZE") is not None else 0,
                    payload.get("DOWNLOAD_THREADS") if payload.get("DOWNLOAD_THREADS") is not None else 4,
                )
            )
            conn.commit()
        finally:
            conn.close()

def reset_app_settings_in_db() -> None:
    """重置应用设置（清空配置）。"""
    logger.info("【数据库】开始重置应用设置")
    save_app_settings_to_db(
        {
            "BOT_TOKEN": None,
            "CHANNEL_NAME": None,
            "PASS_WORD": None,
            "PICGO_API_KEY": None,
            "BASE_URL": None,
            "AUTO_DOWNLOAD_ENABLED": True,  # 默认启用自动下载
            "DOWNLOAD_DIR": "/app/downloads",
            "DOWNLOAD_FILE_TYPES": "image,video",
            "DOWNLOAD_MAX_SIZE": 10737418240,  # 10GB
            "DOWNLOAD_MIN_SIZE": 0,
        }
    )
    logger.info("【数据库】应用设置已重置")

# ==================== 会话管理 ====================

def create_session(session_id: str, expires_in_hours: int = 24) -> None:
    """
    创建一个新的会话。

    Args:
        session_id: 会话ID
        expires_in_hours: 会话过期时间（小时），默认24小时
    """
    with db_lock:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            expires_at = datetime.now() + timedelta(hours=expires_in_hours)
            cursor.execute(
                "INSERT OR REPLACE INTO sessions (session_id, expires_at) VALUES (?, ?)",
                (session_id, expires_at.isoformat())
            )
            conn.commit()
            logger.info(f"【数据库】会话已创建。会话ID: {session_id[:8]}...，过期时间: {expires_at}")
        finally:
            conn.close()

def get_session(session_id: str) -> dict | None:
    """
    获取会话信息。如果会话不存在或已过期，返回 None。

    Args:
        session_id: 会话ID

    Returns:
        会话字典（包含 session_id, created_at, expires_at）或 None
    """
    with db_lock:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT session_id, created_at, expires_at FROM sessions WHERE session_id = ?",
                (session_id,)
            )
            row = cursor.fetchone()
            if not row:
                logger.debug(f"【数据库】会话未找到。会话ID: {session_id[:8]}...")
                return None

            # 检查会话是否过期
            expires_at = datetime.fromisoformat(row["expires_at"])
            if datetime.now() > expires_at:
                # 会话已过期，删除它
                cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
                conn.commit()
                logger.info(f"【数据库】会话已过期并被删除。会话ID: {session_id[:8]}...")
                return None

            logger.debug(f"【数据库】会话有效。会话ID: {session_id[:8]}...，过期时间: {row['expires_at']}")
            return {
                "session_id": row["session_id"],
                "created_at": row["created_at"],
                "expires_at": row["expires_at"]
            }
        finally:
            conn.close()

def delete_session(session_id: str) -> bool:
    """
    删除指定的会话。

    Args:
        session_id: 会话ID

    Returns:
        如果成功删除了会话，返回 True，否则返回 False
    """
    with db_lock:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            conn.commit()
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info("已删除会话: %s", session_id)
            return deleted
        finally:
            conn.close()

def cleanup_expired_sessions() -> int:
    """
    清理所有过期的会话。

    Returns:
        删除的会话数量
    """
    with db_lock:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            cursor.execute("DELETE FROM sessions WHERE expires_at < ?", (now,))
            conn.commit()
            deleted_count = cursor.rowcount
            if deleted_count > 0:
                logger.info("已清理 %d 个过期会话", deleted_count)
            return deleted_count
        finally:
            conn.close()

# ==================== 标签管理 ====================

def add_file_tag(file_id: str, tag: str) -> bool:
    """
    为文件添加标签。

    Args:
        file_id: 文件ID
        tag: 标签名称

    Returns:
        是否成功添加
    """
    with db_lock:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO file_tags (file_id, tag) VALUES (?, ?)",
                    (file_id, tag.strip().lower())
                )
                conn.commit()
                logger.info("为文件 %s 添加标签: %s", file_id, tag)
                return True
            except sqlite3.IntegrityError:
                logger.warning("标签已存在: %s -> %s", file_id, tag)
                return False
        finally:
            conn.close()

def remove_file_tag(file_id: str, tag: str) -> bool:
    """
    移除文件的标签。

    Args:
        file_id: 文件ID
        tag: 标签名称

    Returns:
        是否成功移除
    """
    with db_lock:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM file_tags WHERE file_id = ? AND tag = ?",
                (file_id, tag.strip().lower())
            )
            conn.commit()
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info("移除文件标签: %s -> %s", file_id, tag)
            return deleted
        finally:
            conn.close()

def get_file_tags(file_id: str) -> list[str]:
    """
    获取文件的所有标签。

    Args:
        file_id: 文件ID

    Returns:
        标签列表
    """
    with db_lock:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT tag FROM file_tags WHERE file_id = ? ORDER BY created_at",
                (file_id,)
            )
            return [row[0] for row in cursor.fetchall()]
        finally:
            conn.close()

def get_all_tags() -> list[dict]:
    """
    获取所有标签及其使用次数。

    Returns:
        [{"tag": "标签名", "count": 使用次数}, ...]
    """
    with db_lock:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT tag, COUNT(*) as count
                FROM file_tags
                GROUP BY tag
                ORDER BY count DESC, tag ASC
            """)
            return [{"tag": row[0], "count": row[1]} for row in cursor.fetchall()]
        finally:
            conn.close()

def get_files_by_tag(tag: str) -> list[str]:
    """
    根据标签查询文件ID列表。

    Args:
        tag: 标签名称

    Returns:
        文件ID列表
    """
    with db_lock:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT file_id FROM file_tags WHERE tag = ? ORDER BY created_at DESC",
                (tag.strip().lower(),)
            )
            return [row[0] for row in cursor.fetchall()]
        finally:
            conn.close()

# ==================== 本地文件管理 ====================

def update_local_path(file_id: str, local_path: str) -> bool:
    """
    更新文件的本地路径。

    Args:
        file_id: 文件ID
        local_path: 本地文件路径

    Returns:
        是否成功更新
    """
    with db_lock:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE files SET local_path = ? WHERE file_id = ?",
                (local_path, file_id)
            )
            conn.commit()
            updated = cursor.rowcount > 0
            if updated:
                logger.info("更新文件本地路径: %s -> %s", file_id, local_path)
            return updated
        finally:
            conn.close()

def get_local_files() -> list[dict]:
    """
    获取所有已下载到本地的文件。

    Returns:
        文件列表
    """
    with db_lock:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT filename, file_id, filesize, upload_date, short_id, local_path
                FROM files
                WHERE local_path IS NOT NULL AND local_path != ''
                ORDER BY upload_date DESC
            """)
            files = []
            for row in cursor.fetchall():
                files.append({
                    "filename": row["filename"],
                    "file_id": row["file_id"],
                    "filesize": row["filesize"],
                    "upload_date": row["upload_date"],
                    "short_id": row["short_id"],
                    "local_path": row["local_path"]
                })
            return files
        finally:
            conn.close()

def clear_local_path(file_id: str) -> bool:
    """
    清空文件的本地路径字段。

    Args:
        file_id: 文件ID

    Returns:
        是否成功更新
    """
    with db_lock:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE files SET local_path = NULL WHERE file_id = ?",
                (file_id,)
            )
            conn.commit()
            updated = cursor.rowcount > 0
            if updated:
                logger.info("已清空文件本地路径: %s", file_id)
            return updated
        finally:
            conn.close()


def clear_error_markers() -> int:
    """
    清除所有错误标记（__error_* 和陈旧的 __downloading_* 标记），以便重试下载。

    Returns:
        清除的标记数量
    """
    with db_lock:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            # 清除所有以 __ 开头的占位符标记（错误标记和下载标记）
            cursor.execute(
                "UPDATE files SET local_path = NULL WHERE local_path LIKE '__%%'"
            )
            conn.commit()
            cleared_count = cursor.rowcount
            if cleared_count > 0:
                logger.info(f"【数据库】已清除 {cleared_count} 个错误/下载标记，可重新下载")
            return cleared_count
        finally:
            conn.close()

# ==================== 下载统计 ====================

def increment_download_count(file_id: str) -> bool:
    """
    增加文件的下载计数。

    Args:
        file_id: 文件ID

    Returns:
        是否成功更新
    """
    with db_lock:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE files SET download_count = download_count + 1 WHERE file_id = ?",
                (file_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

# ==================== 统计查询 ====================

def get_statistics() -> dict:
    """
    获取系统统计信息。

    Returns:
        统计数据字典
    """
    with db_lock:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()

            # 总文件数、总大小、总下载次数
            cursor.execute("SELECT COUNT(*), COALESCE(SUM(filesize), 0), COALESCE(SUM(download_count), 0) FROM files")
            row = cursor.fetchone()
            total_files = row[0]
            total_size = row[1]
            total_downloads = row[2]

            # 按MIME类型分类统计
            cursor.execute("""
                SELECT
                    CASE
                        WHEN mime_type LIKE 'image/%' THEN 'image'
                        WHEN mime_type LIKE 'video/%' THEN 'video'
                        WHEN mime_type LIKE 'audio/%' THEN 'audio'
                        WHEN mime_type LIKE 'application/pdf' THEN 'pdf'
                        WHEN mime_type LIKE 'text/%' THEN 'text'
                        ELSE 'other'
                    END as type,
                    COUNT(*) as count,
                    COALESCE(SUM(filesize), 0) as size
                FROM files
                WHERE mime_type IS NOT NULL
                GROUP BY type
            """)
            by_type = {}
            for row in cursor.fetchall():
                by_type[row[0]] = {"count": row[1], "size": row[2]}

            # 最近7天上传趋势
            cursor.execute("""
                SELECT DATE(upload_date) as date, COUNT(*) as count
                FROM files
                WHERE upload_date >= datetime('now', '-7 days')
                GROUP BY DATE(upload_date)
                ORDER BY date DESC
            """)
            recent_uploads = [
                {"date": row[0], "count": row[1]}
                for row in cursor.fetchall()
            ]

            # Top 10 下载文件
            cursor.execute("""
                SELECT filename, file_id, short_id, download_count, filesize
                FROM files
                WHERE download_count > 0
                ORDER BY download_count DESC
                LIMIT 10
            """)
            top_downloads = []
            for row in cursor.fetchall():
                top_downloads.append({
                    "filename": row[0],
                    "file_id": row[1],
                    "short_id": row[2],
                    "download_count": row[3],
                    "filesize": row[4]
                })

            # 本地已下载文件数
            cursor.execute("SELECT COUNT(*) FROM files WHERE local_path IS NOT NULL AND local_path != ''")
            local_files_count = cursor.fetchone()[0]

            # 标签总数
            cursor.execute("SELECT COUNT(DISTINCT tag) FROM file_tags")
            total_tags = cursor.fetchone()[0]

            return {
                "total_files": total_files,
                "total_size": total_size,
                "total_downloads": total_downloads,
                "by_type": by_type,
                "recent_uploads": recent_uploads,
                "top_downloads": top_downloads,
                "local_files_count": local_files_count,
                "total_tags": total_tags
            }
        finally:
            conn.close()
