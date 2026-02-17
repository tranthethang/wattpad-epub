import asyncio
import os

from playwright.async_api import Browser
from playwright_stealth import Stealth
from slugify import slugify

from ..config import (BROWSER_TIMEOUT, HTML_TEMPLATE, SCRAPING_SCROLL_COUNT,
                      SCRAPING_SCROLL_DELAY, USER_AGENT, VIEWPORT)
from ..utils import extract_main_content


async def get_page_html(browser: Browser, url: str):
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
        # Rethrow để commands xử lý log lỗi
        raise e
    finally:
        await context.close()


def save_chapter(output_dir: str, title: str, html_content: str, file_name: str):
    file_path = os.path.join(output_dir, file_name)
    content = extract_main_content(html_content)
    if not content:
        return None

    final_html = HTML_TEMPLATE.format(title=title, content=content)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(final_html)
    return file_path
