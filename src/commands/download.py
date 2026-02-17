import asyncio
import os
import re

from playwright.async_api import async_playwright
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..config import (DEFAULT_DOWNLOAD_DIR, DEFAULT_LOG_DIR,
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
    existing_chapter_nums = set()
    from ..config import CHAPTER_NUMBER_PATTERN
    for f in existing_files:
        if match := re.search(CHAPTER_NUMBER_PATTERN, f):
            existing_chapter_nums.add(match.group(1))

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
                # Lấy phần cuối cùng của URL làm base name
                url_path = url.split("/")[-1]
                if not url_path:
                    url_path = url.split("/")[-2]
                
                # Check skip based on chapter number
                match = re.search(CHAPTER_NUMBER_PATTERN, url_path)
                chapter_num = match.group(1) if match else None

                async with semaphore:
                    try:
                        if chapter_num and chapter_num in existing_chapter_nums:
                            console.print(
                                f"[yellow]Bỏ qua:[/yellow] Chương {chapter_num}"
                            )
                            progress.advance(task)
                            return

                        progress.update(
                            task, description=f"Đang tải: {url_path}..."
                        )
                        data = await get_page_html(browser, url)
                        if not data or not data.get("html"):
                            log_error(url)
                            console.print(f"[red]Thất bại (Page Error):[/red] {url[:30]}...")
                        else:
                            # Xử lý tên file mới từ title
                            title = data.get("title", "")
                            from slugify import slugify
                            
                            if ":" in title:
                                sub_title = title.split(":", 1)[1].strip()
                                sub_title_slug = slugify(sub_title)
                                file_name = f"{url_path}-{sub_title_slug}.html".lower()
                            else:
                                file_name = f"{url_path}.html".lower()

                            res = save_chapter(output, title, data["html"], file_name)
                            if not res:
                                log_error(url)
                                console.print(f"[red]Thất bại (No Content):[/red] {url[:30]}...")
                            else:
                                console.print(
                                    f"[green]Thành công:[/green] {file_name}"
                                )

                        await asyncio.sleep(DOWNLOAD_DELAY)
                    except Exception as e:
                        console.print(f"[red]Lỗi:[/red] {file_name} - {e}")
                        log_error(url)
                    finally:
                        progress.advance(task)

            await asyncio.gather(*[download_url(url) for url in urls])
        await browser.close()
