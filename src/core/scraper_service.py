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

        return {"html": await page.content(), "title": await page.title()}
    except Exception as e:
        # Rethrow để commands xử lý log lỗi
        raise e
    finally:
        await context.close()


def save_chapter(output_dir: str, title: str, html_content: str, prefix: str = ""):
    # Kết hợp prefix và title để đảm bảo sắp xếp đúng (e.g., chuong-1-tieu-de.html)
    safe_title = slugify(title)
    if prefix and prefix not in safe_title:
        file_name = f"{prefix}-{safe_title}.html"
    else:
        file_name = f"{safe_title}.html"

    file_path = os.path.join(output_dir, file_name)
    content = extract_main_content(html_content)
    final_html = HTML_TEMPLATE.format(title=title, content=content)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(final_html)
    return file_path
