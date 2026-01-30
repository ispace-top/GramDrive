import asyncio
import json
import os
import time
import uuid
from typing import Any

import httpx

from .. import database
from ..core.logging_config import get_logger
from ..events import file_update_queue
from ..services.telegram_service import TelegramService

logger = get_logger(__name__)

# 为广播事件添加一个简单的内存队列。
# 在多工作进程设置中，这需要被替换为像 Redis Pub/Sub 这样的机制。
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
            logger.warning("DownloadService 未运行。")
            return
        logger.info("正在停止 DownloadService...")
        self.running = False
        if self.download_task:
            self.download_task.cancel()
            try:
                await self.download_task
            except asyncio.CancelledError:
                logger.info("DownloadService 任务已取消。")
            except Exception as e:
                logger.error("停止 DownloadService 任务出错: %s", e)
        logger.info("DownloadService 已停止。")

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
                logger.error("DownloadService _monitor_and_download 过程中出错: %s", e)

            await asyncio.sleep(settings.get('polling_interval', 60)) # Poll every minute by default

    async def _get_download_settings(self) -> dict[str, Any]:
        # 在线程池中执行同步数据库调用
        settings = await asyncio.to_thread(database.get_app_settings_from_db)
        return {
            'enabled': settings.get('AUTO_DOWNLOAD_ENABLED', False),
            'download_dir': settings.get('DOWNLOAD_DIR', '/app/downloads'),
            'file_types': [ft.strip().lower() for ft in settings.get('DOWNLOAD_FILE_TYPES', 'image,video').split(',')],
            'max_size': settings.get('DOWNLOAD_MAX_SIZE', 10 * 1024 * 1024 * 1024), # Default 10GB
            'min_size': settings.get('DOWNLOAD_MIN_SIZE', 0), # Default 0MB
            'threads': settings.get('DOWNLOAD_THREADS', 3), # Default 3 threads
            'polling_interval': settings.get('DOWNLOAD_POLLING_INTERVAL', 60), # Default 60 seconds
            'max_retries': settings.get('DOWNLOAD_MAX_RETRIES', 5), # Default 5 retries
        }

    async def _fetch_and_queue_files_for_download(self, settings: dict[str, Any]):
        logger.info("【下载服务】正在获取待下载文件...")
        # 下载服务需要扫描所有文件（包括未下载的），所以使用 local_only=False
        # 使用 asyncio.to_thread 在线程池中执行同步的数据库调用，避免阻塞事件循环
        all_files = await asyncio.to_thread(database.get_all_files, local_only=False)

        # Filter files that are not yet local and match criteria
        files_to_download = []
        for file_info in all_files:
            # Check if already downloaded or currently downloading
            local_path = file_info.get('local_path')
            if local_path:
                # Skip if already downloaded or has a placeholder (downloading/error)
                if not local_path.startswith('__'):
                    logger.debug(f"【下载服务】文件已下载，跳过。文件名: {file_info['filename']}")
                    continue
                # If placeholder is error marker, we'll skip for now to avoid infinite retries
                if local_path.startswith('__error_'):
                    retry_count = file_info.get('retry_count', 0)
                    last_retry_time_str = file_info.get('last_retry_time')

                    # 使用配置的最大重试次数
                    max_retries = settings.get('max_retries', 5)
                    if retry_count >= max_retries:
                        logger.debug(f"【下载服务】文件已达最大重试次数，跳过。文件名: {file_info['filename']}，重试次数: {retry_count}")
                        continue

                    # 计算指数退避延迟：30s * (2 ^ retry_count)
                    # retry_count=0: 30s, 1: 60s, 2: 120s, 3: 240s, 4: 480s
                    base_delay = 30  # 基础延迟（秒）
                    delay_seconds = base_delay * (2 ** retry_count)

                    # 检查是否应该重试（距离上次重试已过足够时间）
                    if last_retry_time_str:
                        from datetime import datetime, timezone
                        try:
                            # SQLite CURRENT_TIMESTAMP 格式为 'YYYY-MM-DD HH:MM:SS'
                            last_retry_time = datetime.strptime(last_retry_time_str, '%Y-%m-%d %H:%M:%S')
                            # 假设数据库时间为 UTC（根据实际情况调整）
                            last_retry_time = last_retry_time.replace(tzinfo=timezone.utc)
                            elapsed_seconds = (datetime.now(timezone.utc) - last_retry_time).total_seconds()

                            if elapsed_seconds < delay_seconds:
                                remaining = int(delay_seconds - elapsed_seconds)
                                logger.debug(f"【下载服务】文件等待重试中。文件名: {file_info['filename']}，重试次数: {retry_count}，剩余等待时间: {remaining}秒")
                                continue
                            else:
                                logger.info(f"【下载服务】文件达到重试时间，将重试。文件名: {file_info['filename']}，重试次数: {retry_count}，延迟: {delay_seconds}秒")
                        except Exception as e:
                            logger.error(f"【下载服务】解析重试时间失败。文件名: {file_info['filename']}，错误: {e}")
                            # 解析失败，立即重试
                    else:
                        # 首次失败，立即重试
                        logger.info(f"【下载服务】文件首次失败，立即重试。文件名: {file_info['filename']}")
                    # 继续处理，将文件加入下载队列
                # If placeholder is downloading marker, check if it's stale (>10 minutes)
                if local_path.startswith('__downloading_'):
                    import re
                    import time
                    match = re.search(r'__downloading_(\d+)', local_path)
                    if match:
                        timestamp = int(match.group(1))
                        if time.time() - timestamp < 600:  # 10 minutes
                            logger.debug(f"【下载服务】文件正在下载中，跳过。文件名: {file_info['filename']}")
                            continue
                        else:
                            logger.warning(f"【下载服务】检测到陈旧的下载标记，将重试。文件名: {file_info['filename']}")

            # Check file size
            if file_info['filesize'] > settings['max_size'] or file_info['filesize'] < settings['min_size']:
                size_mb = file_info['filesize'] / 1024 / 1024
                max_mb = settings['max_size'] / 1024 / 1024
                min_mb = settings['min_size'] / 1024 / 1024
                logger.debug(f"【下载服务】文件大小不符合要求，跳过。文件名: {file_info['filename']}，大小: {size_mb:.2f}MB（范围: {min_mb:.2f}-{max_mb:.2f}MB）")
                continue

            # Check file type
            file_category = database._get_file_category_from_mime(file_info.get('mime_type'), file_info.get('filename'))
            if 'all' not in settings['file_types'] and file_category not in settings['file_types']:
                logger.debug(f"【下载服务】文件类型不匹配，跳过。文件名: {file_info['filename']}，类型: {file_category}（允许: {','.join(settings['file_types'])}）")
                continue

            # Add to queue if not already there
            if file_info['file_id'] not in [qf['file_id'] for qf in list(self.download_queue._queue)]:
                files_to_download.append(file_info)

        for file_info in files_to_download:
            await self.download_queue.put(file_info)

        logger.info(f"【下载服务】已排队 {len(files_to_download)} 个文件待下载")


    async def _process_download_queue(self, settings: dict[str, Any]):
        if self.download_queue.empty():
            logger.debug("Download queue is empty.")
            return

        logger.info("正在处理下载队列，共 %d 个项目...", self.download_queue.qsize())

        # Create a semaphore to limit concurrent downloads
        semaphore = asyncio.Semaphore(settings['threads'])

        async def download_worker(file_info: dict[str, Any]):
            task_id = str(uuid.uuid4())
            async with semaphore:
                file_id = file_info['file_id']
                filename = file_info['filename']
                total_size = file_info.get('filesize', 0)
                logger.info("尝试下载 %s (ID: %s)", filename, file_id)

                # 在开始下载前先标记为"正在下载"，避免重复排队
                downloading_marker = f"__downloading_{int(time.time())}"
                await asyncio.to_thread(database.update_local_path, file_id, downloading_marker)

                try:
                    # Announce start
                    await progress_event_queue.put({
                        "task_id": task_id, "file_id": file_id, "filename": filename,
                        "total_size": total_size, "status": "starting"
                    })

                    actual_file_id = file_id.split(':', 1)[-1]
                    download_url = await self.telegram_service.get_download_url(actual_file_id)
                    if not download_url:
                        raise Exception("无法获取下载 URL")

                    # 优化的目录结构：/download_dir/类型/日期/文件名
                    import datetime
                    current_time = datetime.datetime.now()
                    date_str = current_time.strftime("%Y-%m-%d")  # YYYY-MM-DD

                    file_category = database._get_file_category_from_mime(file_info.get('mime_type'), file_info.get('filename'))
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
                    download_success = False
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
                                            "downloaded": bytes_downloaded, "total_size": total_size, "progress": (bytes_downloaded / total_size) if total_size > 0 else 0
                                        })
                                        last_update_time = current_time
                        download_success = True
                    finally:
                        # 如果使用了临时客户端，需要关闭它
                        if not self.http_client and client:
                            await client.aclose()

                    # 检查下载是否完整
                    if download_success and os.path.exists(local_filepath):
                        actual_file_size = os.path.getsize(local_filepath)
                        if actual_file_size != total_size:
                            logger.warning(f"【下载服务】文件大小不匹配，标记为错误。文件名: {filename}，预期: {total_size} bytes，实际: {actual_file_size} bytes")
                            # 标记为错误状态，并增加重试计数
                            await asyncio.to_thread(database.update_local_path, file_id, f"__error_size_mismatch")
                            await asyncio.to_thread(database.increment_retry_count, file_id)
                            await progress_event_queue.put({
                                "task_id": task_id, "file_id": file_id, "filename": filename,
                                "status": "error", "error": "文件大小不匹配"
                            })
                            # 删除不完整的文件
                            if os.path.exists(local_filepath):
                                os.remove(local_filepath)

                            # 广播文件状态更新
                            updated_file = await asyncio.to_thread(database.get_file_by_id, file_id)
                            if updated_file:
                                await file_update_queue.publish(json.dumps({
                                    "action": "update",
                                    **updated_file
                                }))
                        else:
                            relative_local_path = os.path.relpath(local_filepath, start=settings['download_dir'])
                            result = await asyncio.to_thread(database.update_local_path, file_id, relative_local_path)
                            if result:
                                logger.info(f"【下载服务】文件下载完成。文件名: {filename}，路径: {relative_local_path}")
                                await progress_event_queue.put({
                                    "task_id": task_id, "file_id": file_id, "filename": filename,
                                    "status": "completed"
                                })

                                # 广播文件状态更新
                                updated_file = await asyncio.to_thread(database.get_file_by_id, file_id)
                                if updated_file:
                                    await file_update_queue.publish(json.dumps({
                                        "action": "update",
                                        **updated_file
                                    }))
                            else:
                                logger.error(f"【下载服务】数据库更新失败，标记为错误。文件名: {filename}，file_id: {file_id}")
                                await asyncio.to_thread(database.update_local_path, file_id, f"__error_db_update")
                                await asyncio.to_thread(database.increment_retry_count, file_id)
                                await progress_event_queue.put({
                                    "task_id": task_id, "file_id": file_id, "filename": filename,
                                    "status": "error", "error": "数据库更新失败"
                                })

                                # 广播文件状态更新
                                updated_file = await asyncio.to_thread(database.get_file_by_id, file_id)
                                if updated_file:
                                    await file_update_queue.publish(json.dumps({
                                        "action": "update",
                                        **updated_file
                                    }))
                    else:
                        logger.error(f"【下载服务】文件下载失败，标记为错误。文件名: {filename}，路径: {local_filepath}")
                        await asyncio.to_thread(database.update_local_path, file_id, f"__error_download_failed")
                        await asyncio.to_thread(database.increment_retry_count, file_id)
                        await progress_event_queue.put({
                            "task_id": task_id, "file_id": file_id, "filename": filename,
                            "status": "error", "error": "文件下载失败或不存在"
                        })
                        # 清理可能存在的不完整文件
                        if os.path.exists(local_filepath):
                            os.remove(local_filepath)

                        # 广播文件状态更新
                        updated_file = await asyncio.to_thread(database.get_file_by_id, file_id)
                        if updated_file:
                            await file_update_queue.publish(json.dumps({
                                "action": "update",
                                **updated_file
                            }))

                except Exception as e:
                    logger.error("下载文件 %s (ID: %s) 失败: %s", filename, file_id, e)
                    # 标记为错误，并增加重试计数
                    await asyncio.to_thread(database.update_local_path, file_id, f"__error_exception")
                    await asyncio.to_thread(database.increment_retry_count, file_id)
                    await progress_event_queue.put({
                        "task_id": task_id, "file_id": file_id, "filename": filename,
                        "status": "error", "error": str(e)
                    })
                    # 清理可能存在的不完整文件
                    if 'local_filepath' in locals() and os.path.exists(local_filepath):
                        try:
                            os.remove(local_filepath)
                        except Exception:
                            pass

                    # 广播文件状态更新
                    updated_file = await asyncio.to_thread(database.get_file_by_id, file_id)
                    if updated_file:
                        await file_update_queue.publish(json.dumps({
                            "action": "update",
                            **updated_file
                        }))

        tasks = []
        while not self.download_queue.empty():
            file_info = await self.download_queue.get()
            tasks.append(download_worker(file_info))

        await asyncio.gather(*tasks)
        logger.info("下载队列处理完毕。")


async def get_download_service(telegram_service: TelegramService = None, http_client: httpx.AsyncClient = None) -> DownloadService:
    if not hasattr(get_download_service, "_instance"):
        if telegram_service is None:
            raise ValueError("TelegramService instance must be provided on first call.")
        get_download_service._instance = DownloadService(telegram_service, http_client)
    return get_download_service._instance

