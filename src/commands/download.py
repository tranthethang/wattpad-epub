"""
Executes the 'download' command to fetch story content from a list of URLs.
Uses Playwright with a Semaphore to control the number of concurrent downloads.
"""

import asyncio
import os

from playwright.async_api import async_playwright
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from slugify import slugify

from ..config import (DEFAULT_DOWNLOAD_DIR, DEFAULT_LOG_DIR, DOWNLOAD_DELAY,
                      ERROR_LOG_FILE)
from ..core.scraper_service import get_page_html, save_chapter

console = Console()


def log_error(url: str):
    """Log failed URLs to a file for later retry."""
    if not os.path.exists(DEFAULT_LOG_DIR):
        os.makedirs(DEFAULT_LOG_DIR)
    with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{url}\n")


def get_existing_indices(output: str) -> set:
    """Identify indices of already downloaded HTML files."""
    if not os.path.exists(output):
        return set()
    files = os.listdir(output)
    return {
        int(f[:4])
        for f in files
        if f.endswith(".html") and len(f) > 4 and f[:4].isdigit()
    }


def generate_filename(index: int, url: str, title: str) -> str:
    """Generate a safe filename based on index, URL, and story title."""
    idx_str = f"{index:04d}"
    url_path = url.split("/")[-1] or url.split("/")[-2]

    if ":" in title:
        sub_title = title.split(":", 1)[1].strip()
        sub_title_slug = slugify(sub_title)
        return f"{idx_str}-{url_path}-{sub_title_slug}.html".lower()

    return f"{idx_str}-{url_path}.html".lower()


def load_urls(file_path: str) -> list[str]:
    """Load and validate URLs from a text file."""
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return [
            line.strip()
            for line in f
            if line.strip().startswith(("http://", "https://"))
        ]


async def handle_download_result(
    index: int, url: str, data: dict | None, output: str, progress, task
) -> bool:
    """Process the fetched data, save it, and report status."""
    if not data or not data.get("html"):
        log_error(url)
        console.print(f"[red]Failed (Page Error):[/red] {url[:30]}...")
        return False

    file_name = generate_filename(index, url, data.get("title", ""))
    res = await save_chapter(output, data.get("title", ""), data["html"], file_name)

    if not res:
        log_error(url)
        console.print(f"[red]Failed (No Content):[/red] {url[:30]}...")
        return False

    console.print(f"[green]Success:[/green] {file_name}")
    return True


async def download_url(
    index: int,
    url: str,
    browser,
    semaphore,
    output: str,
    existing_indices: set,
    progress,
    task,
):
    """Process a single URL: fetch HTML and save it to disk."""
    async with semaphore:
        try:
            if index in existing_indices:
                console.print(f"[yellow]Skipping:[/yellow] Index {index:04d}")
                return

            progress.update(task, description=f"Downloading [{index:04d}]...")
            data = await get_page_html(browser, url)

            await handle_download_result(index, url, data, output, progress, task)
            await asyncio.sleep(DOWNLOAD_DELAY)
        except Exception as e:
            console.print(f"[red]System Error:[/red] {url} - {e}")
            log_error(url)
        finally:
            progress.advance(task)


async def run_download(file_list: str, output: str, concurrency: int):
    """Coordinate the concurrent download of story chapters."""
    urls = load_urls(file_list)
    if not urls:
        console.print(f"[yellow]Warning:[/yellow] No valid URLs found in {file_list}")
        return

    if not os.path.exists(output):
        os.makedirs(output)

    existing_indices = get_existing_indices(output)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        semaphore = asyncio.Semaphore(concurrency)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(description="Preparing...", total=len(urls))
            await asyncio.gather(
                *[
                    download_url(
                        i + 1,
                        url,
                        browser,
                        semaphore,
                        output,
                        existing_indices,
                        progress,
                        task,
                    )
                    for i, url in enumerate(urls)
                ]
            )

        await browser.close()
