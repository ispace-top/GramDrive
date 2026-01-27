"""Download accelerator for multi-threaded concurrent downloads."""

import asyncio
from collections.abc import AsyncGenerator

import httpx


class DownloadAccelerator:
    """Multi-threaded download accelerator using concurrent Range requests."""

    def __init__(self, http_client: httpx.AsyncClient, thread_count: int = 4):
        """Initialize the download accelerator.

        Args:
            http_client: Async HTTP client for making requests
            thread_count: Number of concurrent download threads (1-16)
        """
        self.client = http_client
        self.thread_count = max(1, min(thread_count, 16))

    async def supports_range_requests(self, url: str) -> tuple[bool, int]:
        """Check if the URL supports Range requests and get content length.

        Args:
            url: The URL to check

        Returns:
            Tuple of (supports_ranges, content_length)
        """
        try:
            resp = await self.client.head(url, follow_redirects=True)
            accepts_ranges = resp.headers.get("Accept-Ranges") == "bytes"
            content_length = int(resp.headers.get("Content-Length", 0))
            return accepts_ranges and content_length > 0, content_length
        except Exception:
            return False, 0

    async def download_chunk(
        self, url: str, start: int, end: int, chunk_id: int
    ) -> tuple[int, bytes]:
        """Download a specific byte range from the URL.

        Args:
            url: The URL to download from
            start: Start byte position
            end: End byte position (inclusive)
            chunk_id: Chunk identifier for ordering

        Returns:
            Tuple of (chunk_id, chunk_data)
        """
        headers = {"Range": f"bytes={start}-{end}"}
        async with self.client.stream("GET", url, headers=headers, follow_redirects=True) as resp:
            resp.raise_for_status()
            data = await resp.aread()
            return chunk_id, data

    async def accelerated_download(
        self, url: str, file_size: int
    ) -> AsyncGenerator[bytes, None]:
        """Download file using multiple concurrent threads.

        Args:
            url: The URL to download from
            file_size: Total file size in bytes

        Yields:
            Chunks of file data in order
        """
        chunk_size = file_size // self.thread_count

        tasks = []
        for i in range(self.thread_count):
            start = i * chunk_size
            end = start + chunk_size - 1 if i < self.thread_count - 1 else file_size - 1
            tasks.append(self.download_chunk(url, start, end, i))

        # Execute concurrently and return in order
        results = await asyncio.gather(*tasks)
        results.sort(key=lambda x: x[0])

        for _, chunk_data in results:
            yield chunk_data
