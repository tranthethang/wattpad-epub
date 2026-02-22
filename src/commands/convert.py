"""
Executes the 'convert' command to transform downloaded HTML files into an EPUB file.
Handles chapter sorting, content extraction, and EPUB packaging.
"""

import logging
import os
import re

from ..config import (CHAPTER_NUMBER_PATTERN, CHAPTER_TITLE_LABEL,
                      CONTENT_DIV_CLASS, DEFAULT_EPUB_DIR, IMAGE_TAG)
from ..core.epub_factory import (add_chapter_to_book, create_epub_book,
                                 finalize_epub)
from ..utils import (clean_filename, ensure_directory_exists,
                     extract_chapter_title, extract_main_content,
                     text_to_html_paragraphs)

logger = logging.getLogger(__name__)


def extract_chapter_number(filename: str) -> int:
    """Extract chapter number from filename (e.g., chuong-1 -> 1).

    Args:
        filename: HTML filename

    Returns:
        Chapter number or 0 if not found
    """
    match = re.search(CHAPTER_NUMBER_PATTERN, filename)
    return int(match.group(1)) if match else 0


def extract_file_index(filename: str) -> int:
    """Extract sorting index (first 4 digits) from filename.

    Args:
        filename: HTML filename

    Returns:
        Integer index for sorting
    """
    if len(filename) > 4 and filename[:4].isdigit():
        return int(filename[:4])
    return extract_chapter_number(filename)


def get_sorted_html_files(input_dir: str) -> list[str]:
    """Retrieve and sort HTML files from the input directory.

    Args:
        input_dir: Directory containing HTML files

    Returns:
        List of sorted HTML filenames
    """
    html_files = [f for f in os.listdir(input_dir) if f.endswith(".html")]
    html_files.sort(key=extract_file_index)
    return html_files


def process_chapter_content(html_content: str) -> str:
    """Extract main content and format it for EPUB (handling text/images).

    Args:
        html_content: Raw HTML content

    Returns:
        Formatted HTML or text content
    """
    raw_content = extract_main_content(html_content)
    if raw_content and f"<{IMAGE_TAG} " in raw_content:
        return raw_content
    return text_to_html_paragraphs(raw_content or "")


def get_output_path(output_file: str | None, author: str, title: str) -> str:
    """Generate a safe output path for the EPUB file."""
    if output_file:
        return output_file
    safe_author = clean_filename(author)
    safe_title = clean_filename(title)
    return os.path.join(DEFAULT_EPUB_DIR, f"{safe_author}_{safe_title}.epub")


def process_and_add_chapter(book, nav_css, input_dir, file_name, index, epub_chapters):
    """Read HTML, process content, and add as a chapter to the book."""
    file_path = os.path.join(input_dir, file_name)
    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    chap_num = extract_chapter_number(file_name)
    desc_title = extract_chapter_title(html_content)

    if desc_title:
        chapter_title = f"{CHAPTER_TITLE_LABEL} {chap_num}: {desc_title}"
    else:
        chapter_title = f"{CHAPTER_TITLE_LABEL} {chap_num}"

    processed_content = process_chapter_content(html_content)

    chapter = add_chapter_to_book(
        book,
        nav_css,
        chapter_title,
        processed_content,
        index,
        base_dir=input_dir,
        content_class=CONTENT_DIV_CLASS,
    )
    epub_chapters.append(chapter)


def run_convert(
    input_dir: str, output_file: str | None, title: str, author: str, cover: str | None
):
    """Main function to handle conversion from HTML directory to EPUB file."""
    if not os.path.exists(input_dir):
        logger.error(f"Directory {input_dir} does not exist.")
        return

    output_file = get_output_path(output_file, author, title)
    try:
        ensure_directory_exists(DEFAULT_EPUB_DIR)
    except OSError as e:
        logger.error(f"Failed to create EPUB output directory: {str(e)}")
        return

    html_files = get_sorted_html_files(input_dir)
    if not html_files:
        logger.warning(f"No HTML files found in {input_dir}.")
        return

    book, nav_css = create_epub_book(title, author, cover)
    epub_chapters = []

    for i, file_name in enumerate(html_files):
        process_and_add_chapter(
            book, nav_css, input_dir, file_name, i + 1, epub_chapters
        )

    finalize_epub(book, output_file, epub_chapters)
    logger.info(f"Done! EPUB saved at {output_file}")
