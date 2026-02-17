import asyncio
from urllib.parse import urlparse

import httpx
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..config import DEFAULT_URLS_FILE
from ..core.url_extractor import build_api_url, fetch_page_urls

console = Console()


async def run_get_urls(api_url: str, page_from: int, page_to: int, output_file: str):
    parsed_url = urlparse(api_url)
    base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
    all_urls = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(
            description="Đang lấy URL...", total=(page_to - page_from + 1)
        )

        async with httpx.AsyncClient() as client:

            async def fetch_page(page):
                try:
                    target_url = build_api_url(api_url, page)
                    page_urls = await fetch_page_urls(client, target_url, base_domain)
                    progress.advance(task)
                    return page_urls
                except Exception as e:
                    console.print(f"\n[red]Lỗi khi lấy page {page}:[/red] {e}")
                    return []

            # Sử dụng gather để lấy dữ liệu song song (giới hạn 5 pages cùng lúc để tránh bị block)
            semaphore = asyncio.Semaphore(5)

            async def sem_fetch(page):
                async with semaphore:
                    return await fetch_page(page)

            results = await asyncio.gather(
                *[sem_fetch(p) for p in range(page_from, page_to + 1)]
            )
            for res in results:
                all_urls.extend(res)

    if all_urls:
        with open(output_file, "a", encoding="utf-8") as f:
            for url in all_urls:
                f.write(f"{url}\n")
        console.print(
            f"\n[bold green]✨ Thành công![/bold green] Đã thêm [cyan]{len(all_urls)}[/cyan] URL vào [cyan]{output_file}[/cyan]"
        )
    else:
        console.print("\n[yellow]Cảnh báo:[/yellow] Không tìm thấy URL nào.")
