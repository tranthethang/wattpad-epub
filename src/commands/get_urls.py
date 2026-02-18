"""
Executes the 'get-urls' command to retrieve chapter URLs from an API.
"""

import asyncio
from urllib.parse import urlparse

import httpx
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..config import API_SEMAPHORE_LIMIT, DEFAULT_URLS_FILE
from ..core.url_extractor import build_api_url, fetch_page_urls

console = Console()


async def fetch_urls_from_page(
    client: httpx.AsyncClient, api_url: str, page: int, base_domain: str, progress, task
):
    """Fetch chapter URLs from a specific API page."""
    try:
        target_url = build_api_url(api_url, page)
        page_urls = await fetch_page_urls(client, target_url, base_domain)
        progress.advance(task)
        return page_urls
    except Exception as e:
        console.print(f"\n[red]Error fetching page {page}:[/red] {e}")
        return []


async def run_get_urls(api_url: str, page_from: int, page_to: int, output_file: str):
    """Main function to coordinate chapter URL extraction from an API."""
    parsed_url = urlparse(api_url)
    base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(
            description="Fetching URL list...", total=(page_to - page_from + 1)
        )

        async with httpx.AsyncClient() as client:
            semaphore = asyncio.Semaphore(API_SEMAPHORE_LIMIT)

            async def sem_fetch(page):
                async with semaphore:
                    return await fetch_urls_from_page(
                        client, api_url, page, base_domain, progress, task
                    )

            results = await asyncio.gather(
                *[sem_fetch(p) for p in range(page_from, page_to + 1)]
            )
            all_urls = [url for sublist in results for url in sublist]

    if all_urls:
        with open(output_file, "a", encoding="utf-8") as f:
            for url in all_urls:
                f.write(f"{url}\n")
        console.print(
            f"\n[bold green]✨ Success![/bold green] Added [cyan]{len(all_urls)}[/cyan] URLs to [cyan]{output_file}[/cyan]"
        )
    else:
        console.print("\n[yellow]Warning:[/yellow] No URLs found.")
