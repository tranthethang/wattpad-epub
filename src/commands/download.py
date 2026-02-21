"""
Executes the 'download' command to fetch story content from a list of URLs.
Uses Playwright with a Semaphore to control the number of concurrent downloads.
"""

import asyncio
import logging
import os

from playwright.async_api import async_playwright

from ..config import (BROWSER_HEADLESS, DEFAULT_DOWNLOAD_DIR, DEFAULT_LOG_DIR,
                      DOWNLOAD_DELAY, ERROR_LOG_FILE, FILE_INDEX_PREFIX_LENGTH)
from ..core.scraper_service import get_page_html, save_chapter
from ..utils import ensure_directory_exists, slugify

logger = logging.getLogger(__name__)


def log_error(url: str):
    """Log failed URLs to a file for later retry."""
    try:
        ensure_directory_exists(DEFAULT_LOG_DIR)
    except OSError as e:
        logger.error(f"Failed to create log directory: {str(e)}")
        return
    try:
        with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{url}\n")
    except OSError as e:
        logger.error(f"Failed to write error log: {str(e)}")


def get_existing_indices(output: str) -> set[int]:
    """Identify indices of already downloaded HTML files.

    Extracts file index from the first FILE_INDEX_PREFIX_LENGTH characters.

    Args:
        output: Directory containing HTML files

    Returns:
        Set of integer indices found in filenames
    """
    if not os.path.exists(output):
        return set()
    files = os.listdir(output)
    return {
        int(f[:FILE_INDEX_PREFIX_LENGTH])
        for f in files
        if f.endswith(".html")
        and len(f) > FILE_INDEX_PREFIX_LENGTH
        and f[:FILE_INDEX_PREFIX_LENGTH].isdigit()
    }


def generate_filename(index: int, url: str, title: str) -> str:
    """Generate a safe filename based on index, URL, and story title."""
    idx_str = f"{index:04d}"
    url_path = url.split("/")[-1] or url.split("/")[-2]

    if ":" in title:
        sub_title = title.split(":", 1)[1].strip()
        sub_title_slug = slugify(sub_title)
        return f"{idx_str}-{url_path}-{sub_title_slug}.html".lower()

    return f"{idx_str}-{url_path}.html".lower()


def load_urls(file_path: str) -> list[str]:
    """Load and validate URLs from a text file."""
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return [
            line.strip()
            for line in f
            if line.strip().startswith(("http://", "https://"))
        ]


async def handle_download_result(
    index: int, url: str, data: dict | None, output: str
) -> bool:
    """Process the fetched data, save it, and report status."""
    if not data or not data.get("html"):
        log_error(url)
        logger.error(f"Failed (Page Error): {url}")
        return False

    title = data.get("title") or f"Chapter {index}"
    file_name = generate_filename(index, url, title)
    res = await save_chapter(output, title, data["html"], file_name)

    if not res:
        log_error(url)
        logger.error(f"Failed (No Content): {url}")
        return False

    logger.info(f"Success: {file_name}")
    return True


async def download_url(
    index: int,
    url: str,
    browser,
    semaphore,
    output: str,
    existing_indices: set,
):
    """
    Process a single URL: fetch HTML and save it to disk.

    This function manages the concurrent request limit using a semaphore
    and skips already downloaded chapters.

    Args:
        index: The sequence number of the chapter.
        url: The chapter URL.
        browser: The Playwright browser instance.
        semaphore: Asyncio semaphore for concurrency control.
        output: Directory where files will be saved.
        existing_indices: A set of already downloaded chapter numbers.
    """
    async with semaphore:
        try:
            if index in existing_indices:
                logger.info(f"Skipping index {index:04d}")
                return

            data = await get_page_html(browser, url)
            await handle_download_result(index, url, data, output)
            await asyncio.sleep(DOWNLOAD_DELAY)
        except Exception as e:
            logger.error(f"System Error: {url} - {e}")
            log_error(url)


async def execute_download_tasks(urls, browser, semaphore, output, existing_indices):
    """Run all download tasks concurrently."""
    logger.info(f"Starting download of {len(urls)} URLs")
    await asyncio.gather(
        *[
            download_url(
                i + 1,
                url,
                browser,
                semaphore,
                output,
                existing_indices,
            )
            for i, url in enumerate(urls)
        ]
    )


async def run_download(file_list: str, output: str, concurrency: int):
    """Coordinate the concurrent download of story chapters."""
    urls = load_urls(file_list)
    if not urls:
        logger.warning(f"No valid URLs found in {file_list}")
        return

    try:
        ensure_directory_exists(output)
    except OSError as e:
        logger.error(f"Failed to create output directory: {str(e)}")
        return

    existing_indices = get_existing_indices(output)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=BROWSER_HEADLESS)
        semaphore = asyncio.Semaphore(concurrency)
        await execute_download_tasks(urls, browser, semaphore, output, existing_indices)
        await browser.close()
