import asyncio
import os
import re

from playwright.async_api import async_playwright
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..config import (CHAPTER_PATTERN, DEFAULT_DOWNLOAD_DIR, DEFAULT_LOG_DIR,
                      DOWNLOAD_DELAY, ERROR_LOG_FILE)
from ..core.scraper_service import get_page_html, save_chapter

console = Console()


def log_error(url: str):
    if not os.path.exists(DEFAULT_LOG_DIR):
        os.makedirs(DEFAULT_LOG_DIR)
    with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{url}\n")


async def run_download(file_list: str, output: str, concurrency: int):
    if not os.path.exists(file_list):
        console.print(f"[red]Lỗi:[/red] File {file_list} không tồn tại.")
        return
    if not os.path.exists(output):
        os.makedirs(output)

    with open(file_list, "r", encoding="utf-8") as f:
        urls = [
            line.strip()
            for line in f
            if line.strip().startswith(("http://", "https://"))
        ]

    if not urls:
        console.print("[yellow]Cảnh báo:[/yellow] Không tìm thấy URL hợp lệ nào.")
        return

    existing_files = os.listdir(output)
    existing_prefixes = {
        re.search(CHAPTER_PATTERN, f).group(1)
        for f in existing_files
        if re.search(CHAPTER_PATTERN, f)
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        semaphore = asyncio.Semaphore(concurrency)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(description="Đang xử lý...", total=len(urls))

            async def download_url(url):
                url_match = re.search(CHAPTER_PATTERN, url)
                prefix = url_match.group(1) if url_match else ""

                async with semaphore:
                    try:
                        if prefix and prefix in existing_prefixes:
                            console.print(
                                f"[yellow]Bỏ qua:[/yellow] {prefix or url[:20]}"
                            )
                            progress.advance(task)
                            return

                        progress.update(
                            task, description=f"Đang tải: {prefix or url[:20]}..."
                        )
                        data = await get_page_html(browser, url)
                        if not data or not data.get("html"):
                            log_error(url)
                            console.print(f"[red]Thất bại:[/red] {url[:30]}...")
                        else:
                            save_chapter(output, data["title"], data["html"], prefix)
                            console.print(
                                f"[green]Thành công:[/green] {prefix or data['title'][:20]}"
                            )

                        await asyncio.sleep(DOWNLOAD_DELAY)
                    except Exception as e:
                        console.print(f"[red]Lỗi:[/red] {prefix or url[:20]} - {e}")
                        log_error(url)
                    finally:
                        progress.advance(task)

            await asyncio.gather(*[download_url(url) for url in urls])
        await browser.close()
