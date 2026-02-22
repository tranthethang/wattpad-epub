"""
Executes the 'clean' command to remove HTML files with empty content.
"""

import logging
import os
import re
from pathlib import Path

from bs4 import BeautifulSoup

from ..config import CONTENT_DIV_CLASS, HTML_PARSER, INVISIBLE_CHARS_PATTERN

logger = logging.getLogger(__name__)


def is_empty_content(html_content: str) -> bool:
    """Check if content is empty, handling invisible characters."""
    cleaned = re.sub(INVISIBLE_CHARS_PATTERN, "", html_content)
    return len(cleaned) == 0


def process_file_cleaning(file_path: Path) -> bool:
    """
    Read a file and determine if it should be deleted based on content.

    This function parses the HTML file, finds the 'content' div,
    and checks if it contains visible text or images. If it's effectively
    empty, the file is deleted.

    Args:
        file_path: Path object to the target HTML file.

    Returns:
        True if the file was deleted, False otherwise.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        soup = BeautifulSoup(content, HTML_PARSER)
        content_div = soup.find("div", class_=CONTENT_DIV_CLASS)

        if content_div:
            inner_html = content_div.decode_contents()
            if is_empty_content(inner_html):
                os.remove(file_path)
                return True
    except Exception as e:
        logger.error(f"Error processing {file_path.name}: {e}")
    return False


def run_clean(directory: str):
    """Scan directory and remove empty HTML files."""
    path = Path(directory)
    if not path.exists() or not path.is_dir():
        logger.error(f"Directory {directory} does not exist.")
        return

    html_files = list(path.glob("*.html"))
    if not html_files:
        logger.warning(f"No .html files found in {directory}.")
        return

    logger.info(f"Checking {len(html_files)} files in {directory}...")
    deleted_count = sum(1 for f in html_files if process_file_cleaning(f))

    logger.info(f"Finished! Deleted {deleted_count} files.")
