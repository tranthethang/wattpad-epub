"""
Executes the 'get-urls' command to retrieve chapter URLs from an API.
"""

import asyncio
import logging
from urllib.parse import urlparse

import httpx

from ..config import API_SEMAPHORE_LIMIT, DEFAULT_URLS_FILE
from ..core.url_extractor import build_api_url, fetch_page_urls

logger = logging.getLogger(__name__)


async def fetch_urls_from_page(
    client: httpx.AsyncClient,
    api_url: str,
    page: int,
    base_domain: str,
):
    """Fetch chapter URLs from a specific API page."""
    try:
        target_url = build_api_url(api_url, page)
        page_urls = await fetch_page_urls(client, target_url, base_domain)
        return page_urls
    except Exception as e:
        logger.error(f"Error fetching page {page}: {e}")
        return []


async def run_get_urls(api_url: str, page_from: int, page_to: int, output_file: str):
    """Main function to coordinate chapter URL extraction from an API."""
    parsed_url = urlparse(api_url)
    base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"

    async with httpx.AsyncClient() as client:
        semaphore = asyncio.Semaphore(API_SEMAPHORE_LIMIT)

        async def sem_fetch(page):
            async with semaphore:
                return await fetch_urls_from_page(client, api_url, page, base_domain)

        results = await asyncio.gather(
            *[sem_fetch(p) for p in range(page_from, page_to + 1)]
        )
        all_urls = [url for sublist in results for url in sublist]

    if all_urls:
        with open(output_file, "w", encoding="utf-8") as f:
            for url in all_urls:
                f.write(f"{url}\n")
        logger.info(f"Success! Added {len(all_urls)} URLs to {output_file}")
    else:
        logger.warning("No URLs found.")
