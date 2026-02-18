"""
Main entry point for the wattpad-epub application.
Provides a CLI interface for:
1. Extracting chapter URLs from an API.
2. Downloading HTML content from URLs.
3. Converting HTML content to EPUB.
4. Cleaning empty content.
"""

import asyncio

import typer

from .commands.clean import run_clean
from .commands.convert import run_convert
from .commands.download import run_download
from .commands.get_urls import run_get_urls
from .config import (DEFAULT_CONCURRENCY, DEFAULT_COVER_IMAGE,
                     DEFAULT_DOWNLOAD_DIR, DEFAULT_STORY_AUTHOR,
                     DEFAULT_STORY_TITLE, DEFAULT_URLS_FILE)

# Initialize Typer app
app = typer.Typer(help="Tool for downloading and converting stories to EPUB")


@app.command()
def download(
    file_list: str = typer.Argument(
        DEFAULT_URLS_FILE, help="Path to the .txt file containing chapter URLs"
    ),
    output: str = typer.Option(
        DEFAULT_DOWNLOAD_DIR,
        "--output",
        "-o",
        help="Directory to save downloaded HTML files",
    ),
    concurrency: int = typer.Option(
        DEFAULT_CONCURRENCY,
        "--concurrency",
        "-c",
        help="Number of concurrent download processes",
    ),
):
    """
    Download HTML content from a list of URLs.
    Uses Playwright to bypass bot protection.
    """
    asyncio.run(run_download(file_list, output, concurrency))


@app.command()
def get_urls(
    api_url: str = typer.Argument(..., help="API URL to fetch the chapter list"),
    page_from: int = typer.Argument(..., help="Starting page number"),
    page_to: int = typer.Argument(..., help="Ending page number"),
    output_file: str = typer.Option(
        DEFAULT_URLS_FILE, "--output", "-o", help="File to save the extracted URLs"
    ),
):
    """
    Fetch chapter URLs from an API and save them to a text file.
    Useful for stories with a large number of chapters.
    """
    asyncio.run(run_get_urls(api_url, page_from, page_to, output_file))


@app.command()
def convert(
    input_dir: str = typer.Option(
        DEFAULT_DOWNLOAD_DIR,
        "--input",
        "-i",
        help="Directory containing input HTML files",
    ),
    output_file: str | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Path for the output EPUB file (default based on title)",
    ),
    title: str = typer.Option(
        DEFAULT_STORY_TITLE, "--title", "-t", help="Title of the story"
    ),
    author: str = typer.Option(
        DEFAULT_STORY_AUTHOR, "--author", "-a", help="Author of the story"
    ),
    cover: str = typer.Option(
        DEFAULT_COVER_IMAGE,
        "--cover",
        "-c",
        help="Path to the cover image file",
    ),
):
    """
    Bundle HTML files from a directory into a complete EPUB file.
    Automatically sorts chapters based on filenames.
    """
    run_convert(input_dir, output_file, title, author, cover)


@app.command()
def clean(
    directory: str = typer.Argument(
        DEFAULT_DOWNLOAD_DIR, help="Directory containing HTML files to check"
    ),
):
    """
    Check and remove HTML files where <div class="content"> is empty.
    """
    run_clean(directory)


if __name__ == "__main__":
    app()
