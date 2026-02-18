"""
Thực thi lệnh 'get-urls' để lấy danh sách URL chương từ API.
Hỗ trợ lấy dữ liệu từ nhiều trang API cùng lúc (concurrently) và lưu vào file.
"""

import asyncio
from urllib.parse import urlparse

import httpx
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..config import DEFAULT_URLS_FILE
from ..core.url_extractor import build_api_url, fetch_page_urls

# Khởi tạo console để in thông báo
console = Console()


async def run_get_urls(api_url: str, page_from: int, page_to: int, output_file: str):
    """
    Hàm chính điều phối việc gọi API để lấy danh sách URL các chương.
    """
    # Phân tích URL API để lấy domain gốc (dùng cho việc nối URL tương đối)
    parsed_url = urlparse(api_url)
    base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
    all_urls = []

    # Hiển thị thanh tiến trình
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(
            description="Đang lấy danh sách URL...", total=(page_to - page_from + 1)
        )

        # Sử dụng AsyncClient để thực hiện các request không đồng bộ
        async with httpx.AsyncClient() as client:

            async def fetch_page(page):
                """Hàm nội bộ để lấy URL từ một trang API cụ thể."""
                try:
                    # Xây dựng URL API cho trang hiện tại
                    target_url = build_api_url(api_url, page)
                    # Gọi dịch vụ trích xuất URL từ API
                    page_urls = await fetch_page_urls(client, target_url, base_domain)
                    progress.advance(task)
                    return page_urls
                except Exception as e:
                    console.print(f"\n[red]Lỗi khi lấy trang {page}:[/red] {e}")
                    return []

            # Sử dụng Semaphore để giới hạn số lượng request đồng thời tới API (tránh bị block/rate limit)
            semaphore = asyncio.Semaphore(5)

            async def sem_fetch(page):
                async with semaphore:
                    return await fetch_page(page)

            # Khởi chạy song song việc lấy dữ liệu từ các trang
            results = await asyncio.gather(
                *[sem_fetch(p) for p in range(page_from, page_to + 1)]
            )
            # Tổng hợp tất cả URL tìm được
            for res in results:
                all_urls.extend(res)

    # Nếu tìm thấy URL, tiến hành lưu vào file (chế độ append)
    if all_urls:
        with open(output_file, "a", encoding="utf-8") as f:
            for url in all_urls:
                f.write(f"{url}\n")
        console.print(
            f"\n[bold green]✨ Thành công![/bold green] Đã thêm [cyan]{len(all_urls)}[/cyan] URL vào [cyan]{output_file}[/cyan]"
        )
    else:
        console.print("\n[yellow]Cảnh báo:[/yellow] Không tìm thấy URL nào.")
