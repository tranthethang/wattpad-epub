"""
Scraping Service using Playwright.
Responsible for interacting with the browser and extracting content from pages.
"""

import asyncio
import os

import httpx
from bs4 import BeautifulSoup
from playwright.async_api import Browser
from playwright_stealth import Stealth

from ..config import (BROWSER_TIMEOUT, HTML_PARSER, HTML_TEMPLATE,
                      HTTP_TIMEOUT, IMAGES_SUBDIR, SCRAPING_SCROLL_COUNT,
                      SCRAPING_SCROLL_DELAY, SUPPORTED_IMAGE_EXTENSIONS,
                      USER_AGENT, VIEWPORT)
from ..utils import extract_main_content


async def download_image(client: httpx.AsyncClient, url: str, save_path: str) -> bool:
    """
    Download an image from a URL and save it to disk.
    """
    try:
        response = await client.get(url, timeout=HTTP_TIMEOUT)
        if response.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"Error downloading image {url}: {e}")
    return False


async def get_page_html(browser: Browser, url: str):
    """
    Use Playwright to visit a URL and retrieve its HTML content.
    Applies stealth techniques to avoid bot detection.
    """
    context = await browser.new_context(user_agent=USER_AGENT, viewport=VIEWPORT)
    page = await context.new_page()

    await Stealth().apply_stealth_async(page)

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=BROWSER_TIMEOUT)

        for _ in range(SCRAPING_SCROLL_COUNT):
            await page.mouse.wheel(0, 1000)
            await asyncio.sleep(SCRAPING_SCROLL_DELAY)

        title = await page.title()
        if not title or "error" in title.lower():
            return None

        return {"html": await page.content(), "title": title}
    except Exception as e:
        raise e
    finally:
        await context.close()


def prepare_image_save_path(img_dir: str, chap_idx: str, index: int, original_src: str) -> tuple[str, str]:
    """Generate local filename and full save path for an image."""
    parsed_ext = original_src.split(".")[-1].split("?")[0].lower()
    if parsed_ext not in SUPPORTED_IMAGE_EXTENSIONS:
        parsed_ext = "png"

    img_filename = f"{chap_idx}_{index+1:03d}.{parsed_ext}"
    return img_filename, os.path.join(img_dir, img_filename)


async def download_chapter_images(client: httpx.AsyncClient, images: list, img_dir: str, chap_idx: str):
    """Create and execute download tasks for a list of images."""
    tasks = []
    for i, img in enumerate(images):
        original_src = img.get("src")
        if not original_src:
            continue

        filename, save_path = prepare_image_save_path(img_dir, chap_idx, i, original_src)
        tasks.append(download_image(client, original_src, save_path))
        img["src"] = f"{IMAGES_SUBDIR}/{filename}"

    if tasks:
        await asyncio.gather(*tasks)


async def process_chapter_images(soup: BeautifulSoup, output_dir: str, chap_idx: str):
    """Identify and coordinate the download of all images in the chapter soup."""
    images = soup.find_all("img")
    if not images:
        return soup

    img_dir = os.path.join(output_dir, IMAGES_SUBDIR)
    os.makedirs(img_dir, exist_ok=True)

    async with httpx.AsyncClient(
        headers={"User-Agent": USER_AGENT}, follow_redirects=True
    ) as client:
        await download_chapter_images(client, images, img_dir, chap_idx)

    return soup


async def save_chapter(output_dir: str, title: str, html_content: str, file_name: str):
    """
    Process raw HTML content, handle images, and save to a clean HTML file.
    """
    file_path = os.path.join(output_dir, file_name)
    content = extract_main_content(html_content)
    if not content:
        return None

    if "<img " in content:
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
