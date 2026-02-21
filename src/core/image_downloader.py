"""Image downloading functionality with retry logic."""

import asyncio
import logging

import httpx

from ..config import (HTTP_TIMEOUT, IMAGE_DOWNLOAD_INITIAL_BACKOFF,
                      IMAGE_DOWNLOAD_MAX_RETRIES)

logger = logging.getLogger(__name__)


async def download_image(client: httpx.AsyncClient, url: str, save_path: str) -> bool:
    """
    Download an image with exponential backoff retry logic.

    Args:
        client: HTTP async client
        url: Image URL to download
        save_path: Local path where image will be saved

    Returns:
        True if download successful, False otherwise
    """
    wait_time = IMAGE_DOWNLOAD_INITIAL_BACKOFF

    for attempt in range(IMAGE_DOWNLOAD_MAX_RETRIES):
        try:
            response = await client.get(url, timeout=HTTP_TIMEOUT)
            if response.status_code == 200:
                with open(save_path, "wb") as f:
                    f.write(response.content)
                return True
            elif response.status_code >= 400:
                logger.warning(f"HTTP {response.status_code} downloading {url}")
                return False
        except Exception as e:
            if attempt < IMAGE_DOWNLOAD_MAX_RETRIES - 1:
                logger.debug(
                    f"Retry {attempt + 1}/{IMAGE_DOWNLOAD_MAX_RETRIES} downloading {url}: {e}"
                )
                await asyncio.sleep(wait_time)
                wait_time *= 2
            else:
                logger.error(
                    f"Failed to download image {url} after {IMAGE_DOWNLOAD_MAX_RETRIES} attempts: {e}"
                )
    return False
