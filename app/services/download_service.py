import asyncio
import logging
import os
import httpx
import time
from typing import Dict, Any, List, Optional

from .. import database
from ..core.config import get_app_settings
from ..services.telegram_service import TelegramService

logger = logging.getLogger(__name__)

class DownloadService:
    def __init__(self, telegram_service: TelegramService):
        self.telegram_service = telegram_service
        self.running = False
        self.download_task = None
        self.download_queue: asyncio.Queue = asyncio.Queue()
        logger.info("DownloadService initialized.")

    async def start(self):
        if self.running:
            logger.warning("DownloadService is already running.")
            return
        logger.info("Starting DownloadService...")
        self.running = True
        self.download_task = asyncio.create_task(self._monitor_and_download())
        logger.info("DownloadService started.")

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
            async with semaphore:
                file_id = file_info['file_id']
                filename = file_info['filename']
                logger.info("Attempting to download %s (ID: %s)", filename, file_id)
                
                try:
                    # Get download URL from TelegramService
                    download_url = await self.telegram_service.get_download_url(file_id.split(':', 1)[1]) # Use actual_file_id
                    if not download_url:
                        logger.warning("Could not get download URL for %s. Skipping.", filename)
                        return

                    # Create target directory
                    target_dir = os.path.join(settings['download_dir'], database._get_file_category_from_mime(file_info.get('mime_type')))
                    os.makedirs(target_dir, exist_ok=True)
                    local_filepath = os.path.join(target_dir, filename)

                    # Download file using httpx
                    async with httpx.AsyncClient(timeout=60.0) as client:
                        async with client.stream("GET", download_url) as response:
                            response.raise_for_status()
                            with open(local_filepath, "wb") as f:
                                async for chunk in response.aiter_bytes():
                                    f.write(chunk)

                    # Update database with local path
                    relative_local_path = os.path.relpath(local_filepath, start=settings['download_dir'])
                    database.update_local_path(file_id, relative_local_path)
                    logger.info("Successfully downloaded %s to %s", filename, local_filepath)
                except Exception as e:
                    logger.error("Failed to download %s (ID: %s): %s", filename, file_id, e)

        tasks = []
        while not self.download_queue.empty():
            file_info = await self.download_queue.get()
            tasks.append(download_worker(file_info))
        
        await asyncio.gather(*tasks)
        logger.info("Finished processing download queue.")


async def get_download_service(telegram_service: TelegramService = None) -> DownloadService:
    if not hasattr(get_download_service, "_instance"):
        if telegram_service is None:
            raise ValueError("TelegramService instance must be provided on first call.")
        get_download_service._instance = DownloadService(telegram_service)
    return get_download_service._instance

