"""
Thực thi lệnh 'download' để tải nội dung truyện từ danh sách URL.
Sử dụng Playwright với cơ chế Semaphore để kiểm soát số lượng luồng tải đồng thời.
Hỗ trợ bỏ qua các chương đã tải và ghi log lỗi.
"""

import asyncio
import os
import re

from playwright.async_api import async_playwright
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..config import (DEFAULT_DOWNLOAD_DIR, DEFAULT_LOG_DIR, DOWNLOAD_DELAY,
                      ERROR_LOG_FILE)
from ..core.scraper_service import get_page_html, save_chapter

# Khởi tạo console để in thông báo
console = Console()


def log_error(url: str):
    """
    Ghi lại các URL bị lỗi vào file log để người dùng có thể tải lại sau.
    """
    if not os.path.exists(DEFAULT_LOG_DIR):
        os.makedirs(DEFAULT_LOG_DIR)
    with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{url}\n")


async def run_download(file_list: str, output: str, concurrency: int):
    """
    Hàm chính điều phối quá trình tải danh sách URL.
    """
    # Kiểm tra file danh sách URL và thư mục đầu ra
    if not os.path.exists(file_list):
        console.print(f"[red]Lỗi:[/red] File {file_list} không tồn tại.")
        return
    if not os.path.exists(output):
        os.makedirs(output)

    # Đọc danh sách URL hợp lệ từ file
    with open(file_list, "r", encoding="utf-8") as f:
        urls = [
            line.strip()
            for line in f
            if line.strip().startswith(("http://", "https://"))
        ]

    if not urls:
        console.print("[yellow]Cảnh báo:[/yellow] Không tìm thấy URL hợp lệ nào.")
        return

    # Lấy danh sách các index đã tải để thực hiện cơ chế skip (không tải lại)
    existing_files = os.listdir(output)
    existing_indices = set()
    for f in existing_files:
        # Kiểm tra file có prefix là 4 chữ số (ví dụ: 0001-...)
        if f.endswith(".html") and len(f) > 4 and f[:4].isdigit():
            existing_indices.add(int(f[:4]))

    # Khởi tạo trình duyệt Playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Sử dụng Semaphore để giới hạn số lượng request đồng thời (concurrency)
        semaphore = asyncio.Semaphore(concurrency)

        # Hiển thị thanh tiến trình (progress bar)
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(description="Đang chuẩn bị...", total=len(urls))

            async def download_url(index, url):
                """Hàm nội bộ để xử lý tải một URL đơn lẻ."""
                # Trích xuất phần cuối URL để định danh chương
                url_path = url.split("/")[-1]
                if not url_path:
                    url_path = url.split("/")[-2]

                # Chờ cho đến khi có slot trống trong semaphore
                async with semaphore:
                    try:
                        # Nếu index đã tồn tại thì bỏ qua
                        if index in existing_indices:
                            console.print(f"[yellow]Bỏ qua:[/yellow] Index {index:04d}")
                            progress.advance(task)
                            return

                        progress.update(
                            task, description=f"Đang tải [{index:04d}]: {url_path}..."
                        )

                        # Gọi dịch vụ scraper để lấy nội dung trang
                        data = await get_page_html(browser, url)
                        if not data or not data.get("html"):
                            log_error(url)
                            console.print(
                                f"[red]Thất bại (Lỗi trang):[/red] {url[:30]}..."
                            )
                        else:
                            # Xử lý đặt tên file dựa trên tiêu đề và URL
                            title = data.get("title", "")
                            from slugify import slugify

                            # Format index thành 4 chữ số
                            idx_str = f"{index:04d}"

                            if ":" in title:
                                # Nếu tiêu đề có dạng "Chương X: Tên Chương", trích xuất "Tên Chương"
                                sub_title = title.split(":", 1)[1].strip()
                                sub_title_slug = slugify(sub_title)
                                file_name = f"{idx_str}-{url_path}-{sub_title_slug}.html".lower()
                            else:
                                file_name = f"{idx_str}-{url_path}.html".lower()

                            # Lưu nội dung chương vào file HTML
                            res = await save_chapter(output, title, data["html"], file_name)
                            if not res:
                                log_error(url)
                                console.print(
                                    f"[red]Thất bại (Không có nội dung):[/red] {url[:30]}..."
                                )
                            else:
                                console.print(f"[green]Thành công:[/green] {file_name}")

                        # Nghỉ một khoảng thời gian nhỏ để tránh spam server
                        await asyncio.sleep(DOWNLOAD_DELAY)
                    except Exception as e:
                        console.print(f"[red]Lỗi hệ thống:[/red] {url_path} - {e}")
                        log_error(url)
                    finally:
                        # Cập nhật tiến trình sau khi hoàn tất (dù lỗi hay thành công)
                        progress.advance(task)

            # Khởi chạy đồng thời tất cả các task tải
            await asyncio.gather(
                *[download_url(i + 1, url) for i, url in enumerate(urls)]
            )

        # Đóng trình duyệt sau khi hoàn thành tất cả các URL
        await browser.close()
