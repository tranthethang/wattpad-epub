import asyncio
import logging
import os

from temporalio import activity

from ..commands.convert import run_convert
from ..commands.download import run_download
from ..commands.get_urls import run_get_urls
from ..config import DOWNLOAD_MAX_RETRIES, DOWNLOAD_RETRY_BACKOFF
from .utils import (DownloadValidationError, ValidationError,
                    validate_concurrency, validate_page_range,
                    validate_retries, validate_string)

logger = logging.getLogger(__name__)

MAX_BACKOFF_WAIT_TIME = 300


@activity.defn
async def extract_urls_activity(
    api_url: str, page_from: int, page_to: int, urls_file: str
) -> str:
    """Extract chapter URLs from API and save to file.

    Args:
        api_url: API endpoint URL
        page_from: Starting page number
        page_to: Ending page number
        urls_file: Output file path for URLs

    Returns:
        Path to the file containing extracted URLs

    Raises:
        ValidationError: If input parameters are invalid
    """
    validate_string(api_url, "api_url")
    validate_page_range(page_from, page_to)

    logger.info(f"Extracting URLs from {api_url} (pages {page_from}-{page_to})")
    await run_get_urls(api_url, page_from, page_to, urls_file)
    logger.info(f"URLs extracted to {urls_file}")
    return urls_file


def _count_urls(urls_file: str) -> int:
    """Count valid HTTP(S) URLs in file."""
    if not os.path.exists(urls_file):
        return 0
    with open(urls_file, "r", encoding="utf-8") as f:
        return sum(1 for line in f if line.strip().startswith(("http://", "https://")))


def _count_html_files(output_dir: str) -> int:
    """Count HTML files in directory."""
    if not os.path.exists(output_dir):
        return 0
    return sum(1 for f in os.listdir(output_dir) if f.endswith(".html"))


@activity.defn
async def download_with_validation_activity(
    urls_file: str,
    output_dir: str,
    concurrency: int,
    max_retries: int,
) -> str:
    """Download chapters with validation retry logic.

    Compares expected URLs count with downloaded HTML files count.
    Retries with exponential backoff if mismatch detected.

    Args:
        urls_file: Path to file containing chapter URLs
        output_dir: Directory to save downloaded HTML files
        concurrency: Number of concurrent downloads
        max_retries: Maximum retry attempts

    Returns:
        Path to output directory with downloaded files

    Raises:
        ValidationError: If input parameters are invalid
        DownloadValidationError: If validation fails after retries
    """
    if not os.path.exists(urls_file):
        raise ValidationError(f"URLs file not found: {urls_file}")

    validate_concurrency(concurrency)
    validate_retries(max_retries)

    urls_count = _count_urls(urls_file)
    logger.info(f"Found {urls_count} URLs to download")

    for attempt in range(max_retries):
        logger.info(
            f"Download attempt {attempt + 1}/{max_retries} "
            f"(concurrency={concurrency})"
        )
        await run_download(urls_file, output_dir, concurrency)

        html_files_count = _count_html_files(output_dir)
        logger.info(f"Downloaded {html_files_count} files, expected {urls_count}")

        if html_files_count == urls_count:
            logger.info("Download validation passed")
            return output_dir

        if attempt < max_retries - 1:
            exponential_wait = int(DOWNLOAD_RETRY_BACKOFF**attempt)
            wait_time = min(exponential_wait, MAX_BACKOFF_WAIT_TIME)
            logger.warning(f"Mismatch detected, retrying in {wait_time} seconds...")
            await asyncio.sleep(wait_time)

    raise DownloadValidationError(
        f"Failed after {max_retries} attempts: "
        f"expected {urls_count} URLs, got {html_files_count} files"
    )


@activity.defn
async def convert_activity(
    input_dir: str,
    output_file: str,
    title: str,
    author: str,
    cover_path: str | None,
) -> str:
    """Convert downloaded HTML files to EPUB format.

    Args:
        input_dir: Directory containing HTML chapter files
        output_file: Output EPUB file path
        title: Story title
        author: Story author
        cover_path: Optional path to cover image

    Returns:
        Path to the generated EPUB file

    Raises:
        ValidationError: If input parameters are invalid
    """
    validate_string(input_dir, "input_dir")
    validate_string(output_file, "output_file")
    validate_string(title, "title")
    validate_string(author, "author")

    logger.info(
        f"Converting EPUB from {input_dir} to {output_file} "
        f"(title={title}, author={author})"
    )

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None, run_convert, input_dir, output_file, title, author, cover_path
    )

    if cover_path and os.path.exists(cover_path):
        logger.info(f"Removing cover image: {cover_path}")
        try:
            os.remove(cover_path)
        except OSError as e:
            logger.warning(f"Failed to remove cover: {str(e)}")

    logger.info(f"EPUB conversion completed: {output_file}")
    return output_file
