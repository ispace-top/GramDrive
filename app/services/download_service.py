import asyncio
import logging
import os
import httpx
import time
import uuid
from typing import Dict, Any, List, Optional

from .. import database
from ..core.config import get_app_settings
from ..core.logging_config import get_logger
from ..services.telegram_service import TelegramService

logger = get_logger(__name__)

# Add a simple, in-memory queue for broadcasting events.
# In a multi-worker setup, this would need to be replaced with something like Redis Pub/Sub.
progress_event_queue = asyncio.Queue()

class DownloadService:
    def __init__(self, telegram_service: TelegramService, http_client: httpx.AsyncClient = None):
        self.telegram_service = telegram_service
        self.http_client = http_client  # 使用共享的 HTTP 客户端
        self.running = False
        self.download_task = None
        self.download_queue: asyncio.Queue = asyncio.Queue()
        logger.info("【下载服务】已初始化")

    async def start(self):
        if self.running:
            logger.warning("【下载服务】已在运行，无法重复启动")
            return
        logger.info("【下载服务】正在启动...")
        self.running = True
        self.download_task = asyncio.create_task(self._monitor_and_download())
        logger.info("【下载服务】已启动")

    async def stop(self):
        if not self.running:
            logger.warning("DownloadService is not running.")
            return
        logger.info("Stopping DownloadService...")
        self.running = False
        if self.download_task:
            self.download_task.cancel()
            try:
                await self.download_task
            except asyncio.CancelledError:
                logger.info("DownloadService task cancelled.")
            except Exception as e:
                logger.error("Error stopping DownloadService task: %s", e)
        logger.info("DownloadService stopped.")

    async def _monitor_and_download(self):
        while self.running:
            try:
                settings = await self._get_download_settings()
                if not settings['enabled']:
                    logger.debug("Auto-download is disabled. Waiting...")
                    await asyncio.sleep(settings.get('polling_interval', 60))
                    continue

                await self._fetch_and_queue_files_for_download(settings)
                await self._process_download_queue(settings)

            except Exception as e:
                logger.error("Error in DownloadService _monitor_and_download: %s", e)
            
            await asyncio.sleep(settings.get('polling_interval', 60)) # Poll every minute by default

    async def _get_download_settings(self) -> Dict[str, Any]:
        settings = database.get_app_settings_from_db()
        return {
            'enabled': settings.get('AUTO_DOWNLOAD_ENABLED', False),
            'download_dir': settings.get('DOWNLOAD_DIR', '/app/downloads'),
            'file_types': [ft.strip().lower() for ft in settings.get('DOWNLOAD_FILE_TYPES', 'image,video').split(',')],
            'max_size': settings.get('DOWNLOAD_MAX_SIZE', 50 * 1024 * 1024), # Default 50MB
            'min_size': settings.get('DOWNLOAD_MIN_SIZE', 0), # Default 0MB
            'threads': settings.get('DOWNLOAD_THREADS', 3), # Default 3 threads
            'polling_interval': settings.get('DOWNLOAD_POLLING_INTERVAL', 60), # Default 60 seconds
        }

    async def _fetch_and_queue_files_for_download(self, settings: Dict[str, Any]):
        logger.debug("Fetching files to check for downloads...")
        # For simplicity, we assume get_all_files returns all files and we filter here.
        # In a real scenario, you might want to query Telegram for new files.
        all_files = database.get_all_files() 
        
        # Filter files that are not yet local and match criteria
        files_to_download = []
        for file_info in all_files:
            # Check if already downloaded
            if file_info.get('local_path'):
                continue
            
            # Check file size
            if file_info['filesize'] > settings['max_size'] or file_info['filesize'] < settings['min_size']:
                continue
            
            # Check file type
            file_category = database._get_file_category_from_mime(file_info.get('mime_type'))
            if 'all' not in settings['file_types'] and file_category not in settings['file_types']:
                continue
            
            # Add to queue if not already there
            if file_info['file_id'] not in [qf['file_id'] for qf in list(self.download_queue._queue)]:
                files_to_download.append(file_info)
        
        for file_info in files_to_download:
            await self.download_queue.put(file_info)
        
        logger.debug("Queued %d files for download.", len(files_to_download))


    async def _process_download_queue(self, settings: Dict[str, Any]):
        if self.download_queue.empty():
            logger.debug("Download queue is empty.")
            return

        logger.info("Processing download queue with %d items...", self.download_queue.qsize())
        
        # Create a semaphore to limit concurrent downloads
        semaphore = asyncio.Semaphore(settings['threads'])
        
        async def download_worker(file_info: Dict[str, Any]):
            task_id = str(uuid.uuid4())
            async with semaphore:
                file_id = file_info['file_id']
                filename = file_info['filename']
                total_size = file_info.get('filesize', 0)
                logger.info("Attempting to download %s (ID: %s)", filename, file_id)

                try:
                    # Announce start
                    await progress_event_queue.put({
                        "task_id": task_id, "file_id": file_id, "filename": filename,
                        "total_size": total_size, "status": "starting"
                    })

                    actual_file_id = file_id.split(':', 1)[-1]
                    download_url = await self.telegram_service.get_download_url(actual_file_id)
                    if not download_url:
                        raise Exception("Could not get download URL")

                    # 优化的目录结构：/download_dir/类型/日期/文件名
                    import datetime
                    current_time = datetime.datetime.now()
                    date_str = current_time.strftime("%Y-%m-%d")  # YYYY-MM-DD

                    file_category = database._get_file_category_from_mime(file_info.get('mime_type'))
                    target_dir = os.path.join(settings['download_dir'], file_category, date_str)
                    os.makedirs(target_dir, exist_ok=True)

                    # 处理文件名冲突（添加时间戳后缀）
                    base_name, ext = os.path.splitext(filename)
                    local_filepath = os.path.join(target_dir, filename)

                    if os.path.exists(local_filepath):
                        timestamp_str = current_time.strftime("%H%M%S")
                        new_filename = f"{base_name}_{timestamp_str}{ext}"
                        local_filepath = os.path.join(target_dir, new_filename)

                    bytes_downloaded = 0
                    last_update_time = time.time()

                    # 使用共享的 HTTP 客户端，而不是创建新的
                    client = self.http_client if self.http_client else httpx.AsyncClient(timeout=300.0)
                    try:
                        async with client.stream("GET", download_url) as response:
                            response.raise_for_status()
                            with open(local_filepath, "wb") as f:
                                async for chunk in response.aiter_bytes():
                                    f.write(chunk)
                                    bytes_downloaded += len(chunk)

                                    # Throttle progress updates to about once per second
                                    current_time = time.time()
                                    if current_time - last_update_time > 1:
                                        await progress_event_queue.put({
                                            "task_id": task_id, "file_id": file_id, "status": "downloading",
                                            "downloaded": bytes_downloaded, "progress": (bytes_downloaded / total_size) if total_size > 0 else 0
                                        })
                                        last_update_time = current_time
                    finally:
                        # 如果使用了临时客户端，需要关闭它
                        if not self.http_client and client:
                            await client.aclose()

                    relative_local_path = os.path.relpath(local_filepath, start=settings['download_dir'])
                    database.update_local_path(file_id, relative_local_path)
                    
                    await progress_event_queue.put({"task_id": task_id, "file_id": file_id, "status": "completed"})
                    logger.info("Successfully downloaded %s to %s", filename, local_filepath)

                except Exception as e:
                    logger.error("Failed to download %s (ID: %s): %s", filename, file_id, e)
                    await progress_event_queue.put({
                        "task_id": task_id, "file_id": file_id, "filename": filename,
                        "status": "error", "error": str(e)
                    })

        tasks = []
        while not self.download_queue.empty():
            file_info = await self.download_queue.get()
            tasks.append(download_worker(file_info))
        
        await asyncio.gather(*tasks)
        logger.info("Finished processing download queue.")


async def get_download_service(telegram_service: TelegramService = None, http_client: httpx.AsyncClient = None) -> DownloadService:
    if not hasattr(get_download_service, "_instance"):
        if telegram_service is None:
            raise ValueError("TelegramService instance must be provided on first call.")
        get_download_service._instance = DownloadService(telegram_service, http_client)
    return get_download_service._instance

