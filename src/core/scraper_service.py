"""
Scraping Service using Playwright.
Responsible for interacting with the browser and extracting content from pages.
"""

import asyncio
import logging
import os

import httpx
from bs4 import BeautifulSoup
from playwright.async_api import Browser
from playwright_stealth import Stealth

from ..config import (BROWSER_TIMEOUT, HTML_PARSER, HTML_TEMPLATE, IMAGE_TAG,
                      IMAGES_SUBDIR, IMG_SRC_ATTRIBUTE, SCRAPING_SCROLL_COUNT,
                      SCRAPING_SCROLL_DELAY, SUPPORTED_IMAGE_EXTENSIONS,
                      USER_AGENT, VIEWPORT)
from ..utils import ensure_directory_exists, extract_main_content
from .image_downloader import download_image

logger = logging.getLogger(__name__)


async def scroll_page(page) -> None:
    """Perform scrolling to handle lazy-loaded content.

    Args:
        page: Playwright page object
    """
    for _ in range(SCRAPING_SCROLL_COUNT):
        await page.mouse.wheel(0, 1000)
        await asyncio.sleep(SCRAPING_SCROLL_DELAY)


async def get_page_html(browser: Browser, url: str) -> dict[str, str] | None:
    """
    Visit a URL and retrieve its HTML content with stealth and scrolling.

    This function uses playwright-stealth to bypass bot detection by mimicking
    real user behavior and browser fingerprints. It also handles lazy-loaded
    content by scrolling down the page.

    Args:
        browser: The Playwright browser instance.
        url: The target URL to scrape.

    Returns:
        Dictionary with 'html' and 'title' keys, or None if an error occurs.
    """
    context = await browser.new_context(user_agent=USER_AGENT, viewport=VIEWPORT)
    page = await context.new_page()
    await Stealth().apply_stealth_async(page)

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=BROWSER_TIMEOUT)
        await scroll_page(page)

        title = await page.title()
        if not title or "error" in title.lower():
            return None

        return {"html": await page.content(), "title": title}
    finally:
        await context.close()


def prepare_image_save_path(
    img_dir: str, chap_idx: str, index: int, original_src: str
) -> tuple[str, str]:
    """Generate local filename and full save path for an image."""
    parsed_ext = original_src.split(".")[-1].split("?")[0].lower()
    if parsed_ext not in SUPPORTED_IMAGE_EXTENSIONS:
        parsed_ext = "png"

    img_filename = f"{chap_idx}_{index+1:03d}.{parsed_ext}"
    return img_filename, os.path.join(img_dir, img_filename)


async def download_chapter_images(
    client: httpx.AsyncClient, images: list, img_dir: str, chap_idx: str
):
    """Create and execute download tasks for a list of images."""
    tasks = []
    for i, img in enumerate(images):
        original_src = img.get(IMG_SRC_ATTRIBUTE)
        if not original_src:
            continue

        filename, save_path = prepare_image_save_path(
            img_dir, chap_idx, i, original_src
        )
        tasks.append(download_image(client, original_src, save_path))
        img[IMG_SRC_ATTRIBUTE] = f"{IMAGES_SUBDIR}/{filename}"

    if tasks:
        await asyncio.gather(*tasks)


async def process_chapter_images(soup: BeautifulSoup, output_dir: str, chap_idx: str):
    """Identify and coordinate the download of all images in the chapter soup."""
    images = soup.find_all(IMAGE_TAG)
    if not images:
        return soup

    img_dir = os.path.join(output_dir, IMAGES_SUBDIR)
    try:
        ensure_directory_exists(img_dir)
    except OSError as e:
        logger.error(f"Failed to create images directory {img_dir}: {str(e)}")
        return soup

    async with httpx.AsyncClient(
        headers={"User-Agent": USER_AGENT}, follow_redirects=True
    ) as client:
        await download_chapter_images(client, images, img_dir, chap_idx)

    return soup


async def save_chapter(
    output_dir: str, title: str, html_content: str, file_name: str
) -> str | None:
    """
    Process raw HTML content, handle images, and save to a clean HTML file.

    This function cleans the raw HTML, downloads images, updates their sources
    to local paths, and wraps the content in a consistent HTML template for
    EPUB conversion.

    Args:
        output_dir: Directory where the chapter file will be saved.
        title: The title of the chapter.
        html_content: The raw HTML content from the scraper.
        file_name: The name of the file to save (e.g., "0001-chap-1.html").

    Returns:
        The full path to the saved file, or None if no valid content was found.

    Raises:
        ValueError: If parameters are invalid
    """
    if not output_dir or not isinstance(output_dir, str):
        raise ValueError("output_dir must be a non-empty string")
    if not title or not isinstance(title, str):
        raise ValueError("title must be a non-empty string")
    if not html_content or not isinstance(html_content, str):
        raise ValueError("html_content must be a non-empty string")
    if not file_name or not isinstance(file_name, str):
        raise ValueError("file_name must be a non-empty string")

    file_path = os.path.join(output_dir, file_name)
    content = extract_main_content(html_content)
    if not content:
        return None

    if f"<{IMAGE_TAG} " in content:
        soup = BeautifulSoup(content, HTML_PARSER)
        chap_idx = file_name[:4]
        soup = await process_chapter_images(soup, output_dir, chap_idx)

        if soup.body:
            content = "".join([str(c) for c in soup.body.contents]).strip()
        else:
            content = str(soup)

    final_html = HTML_TEMPLATE.format(title=title, content=content)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(final_html)
    return file_path
