import hashlib
import logging
from io import BytesIO
from pathlib import Path

import httpx
from PIL import Image

from ..core.config import get_app_settings

logger = logging.getLogger(__name__)


class ThumbnailService:
    """缩略图生成和缓存服务"""

    def __init__(self, cache_dir: str = "/app/data/thumbnails"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # 缩略图尺寸配置
        self.sizes = {
            "小": (150, 150),
            "中": (300, 300),
            "大": (600, 600),
        }

    def _get_cache_path(self, file_id: str, size: str = "medium") -> Path:
        """生成缓存文件路径"""
        # 使用文件ID的hash作为文件名，避免特殊字符问题
        file_hash = hashlib.md5(file_id.encode()).hexdigest()
        return self.cache_dir / f"{file_hash}_{size}.jpg"

    def get_cached_thumbnail(self, file_id: str, size: str = "medium") -> bytes | None:
        """获取已缓存的缩略图"""
        cache_path = self._get_cache_path(file_id, size)

        if cache_path.exists():
            try:
                with open(cache_path, 'rb') as f:
                    logger.debug(f"缓存命中: {file_id} ({size})")
                    return f.read()
            except Exception as e:
                logger.error(f"读取缓存失败: {cache_path}, {e}")
                return None

        return None

    async def generate_thumbnail(
        self,
        file_id: str,
        source: str,
        size: str = "medium",
        client: httpx.AsyncClient | None = None,
        is_local_file: bool = False
    ) -> bytes | None:
        """生成并缓存缩略图

        Args:
            file_id: 文件ID
            source: 下载URL（is_local_file=False）或本地文件路径（is_local_file=True）
            size: 缩略图尺寸
            client: HTTP客户端（仅当is_local_file=False时使用）
            is_local_file: 是否为本地文件路径
        """

        # 检查尺寸是否有效
        if size not in self.sizes:
            logger.warning(f"无效的缩略图尺寸: {size}，使用默认值 'medium'")
            size = "medium"

        target_size = self.sizes[size]
        cache_path = self._get_cache_path(file_id, size)

        # 如果缓存存在，直接返回
        cached = self.get_cached_thumbnail(file_id, size)
        if cached:
            return cached

        try:
            # 如果是本地文件，直接读取
            if is_local_file:
                logger.info(f"从本地文件生成缩略图: {file_id} ({size})")
                try:
                    with open(source, 'rb') as f:
                        image_data = f.read()
                except Exception as e:
                    logger.error(f"读取本地文件失败: {source}, {e}")
                    return None
            else:
                # 从URL下载原图
                close_client = False
                if client is None:
                    client = httpx.AsyncClient(timeout=30.0)
                    close_client = True

                try:
                    logger.info(f"从URL生成缩略图: {file_id} ({size})")
                    response = await client.get(source)
                    response.raise_for_status()
                    image_data = response.content
                finally:
                    if close_client:
                        await client.aclose()

            # 生成缩略图
            thumbnail_data = self._create_thumbnail(image_data, target_size)

            if thumbnail_data:
                # 保存到缓存
                with open(cache_path, 'wb') as f:
                    f.write(thumbnail_data)
                logger.info(f"缩略图已缓存: {cache_path}")
                return thumbnail_data

        except httpx.RequestError as e:
            logger.error(f"下载图片失败: {source}, {e}")
            return None
        except Exception as e:
            logger.error(f"生成缩略图失败: {file_id}, {e}", exc_info=True)
            return None

    def _create_thumbnail(self, image_data: bytes, size: tuple[int, int]) -> bytes | None:
        """使用PIL创建缩略图"""
        try:
            img = Image.open(BytesIO(image_data))

            # 转换RGBA到RGB（处理透明背景）
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # 生成缩略图（保持宽高比）
            img.thumbnail(size, Image.Resampling.LANCZOS)

            # 保存为JPEG
            output = BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            return output.getvalue()

        except Exception as e:
            logger.error(f"PIL处理图片失败: {e}", exc_info=True)
            return None

    def clear_cache(self, file_id: str | None = None):
        """清除缓存"""
        if file_id:
            # 清除特定文件的所有缩略图
            file_hash = hashlib.md5(file_id.encode()).hexdigest()
            for size in self.sizes:
                cache_path = self.cache_dir / f"{file_hash}_{size}.jpg"
                if cache_path.exists():
                    cache_path.unlink()
                    logger.info(f"已删除缓存: {cache_path}")
        else:
            # 清除所有缓存
            for cache_file in self.cache_dir.glob("*.jpg"):
                cache_file.unlink()
            logger.info("已清除所有缩略图缓存")


# 单例实例
_thumbnail_service: ThumbnailService | None = None


def get_thumbnail_service() -> ThumbnailService:
    """获取缩略图服务单例"""
    global _thumbnail_service
    if _thumbnail_service is None:
        settings = get_app_settings()
        cache_dir = settings.get("THUMBNAIL_CACHE_DIR", "/app/data/thumbnails")
        _thumbnail_service = ThumbnailService(cache_dir=cache_dir)
    return _thumbnail_service
