"""
Executes the 'convert' command to transform downloaded HTML files into an EPUB file.
Handles chapter sorting, content extraction, and EPUB packaging.
"""

import os
import re

from rich.console import Console

from ..config import (CHAPTER_NUMBER_PATTERN, CHAPTER_TITLE_LABEL,
                      DEFAULT_COVER_IMAGE, DEFAULT_DOWNLOAD_DIR,
                      DEFAULT_EPUB_DIR, SAFE_FILENAME_PATTERN)
from ..core.epub_factory import (add_chapter_to_book, create_epub_book,
                                 finalize_epub)
from ..utils import extract_main_content, text_to_html_paragraphs

console = Console()


def extract_chapter_number(filename: str) -> int:
    """Extract chapter number from filename (e.g., chuong-1 -> 1)."""
    match = re.search(CHAPTER_NUMBER_PATTERN, filename)
    return int(match.group(1)) if match else 0


def extract_file_index(filename: str) -> int:
    """Extract sorting index (first 4 digits) from filename."""
    if len(filename) > 4 and filename[:4].isdigit():
        return int(filename[:4])
    return extract_chapter_number(filename)


def get_sorted_html_files(input_dir: str) -> list:
    """Retrieve and sort HTML files from the input directory."""
    html_files = [f for f in os.listdir(input_dir) if f.endswith(".html")]
    html_files.sort(key=extract_file_index)
    return html_files


def process_chapter_content(html_content: str) -> str:
    """Extract main content and format it for EPUB (handling text/images)."""
    raw_content = extract_main_content(html_content)
    if raw_content and "<img " in raw_content:
        return raw_content
    return text_to_html_paragraphs(raw_content)


def get_output_path(output_file: str | None, author: str, title: str) -> str:
    """Generate a safe output path for the EPUB file."""
    if output_file:
        return output_file
    safe_author = re.sub(SAFE_FILENAME_PATTERN, "", author)
    safe_title = re.sub(SAFE_FILENAME_PATTERN, "", title)
    return os.path.join(DEFAULT_EPUB_DIR, f"{safe_author}_{safe_title}.epub")


def process_and_add_chapter(
    book, nav_css, input_dir, file_name, index, epub_chapters
):
    """Read HTML, process content, and add as a chapter to the book."""
    file_path = os.path.join(input_dir, file_name)
    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    chapter_title = f"{CHAPTER_TITLE_LABEL} {extract_chapter_number(file_name)}"
    processed_content = process_chapter_content(html_content)

    chapter = add_chapter_to_book(
        book, nav_css, chapter_title, processed_content, index, base_dir=input_dir
    )
    epub_chapters.append(chapter)


def run_convert(
    input_dir: str, output_file: str | None, title: str, author: str, cover: str
):
    """Main function to handle conversion from HTML directory to EPUB file."""
    if not os.path.exists(input_dir):
        console.print(f"[red]Error:[/red] Directory {input_dir} does not exist.")
        return

    output_file = get_output_path(output_file, author, title)
    if not os.path.exists(DEFAULT_EPUB_DIR):
        os.makedirs(DEFAULT_EPUB_DIR)

    html_files = get_sorted_html_files(input_dir)
    if not html_files:
        console.print(f"[yellow]Warning:[/yellow] No HTML files found in {input_dir}.")
        return

    book, nav_css = create_epub_book(title, author, cover)
    epub_chapters = []

    for i, file_name in enumerate(html_files):
        process_and_add_chapter(book, nav_css, input_dir, file_name, i + 1, epub_chapters)

    finalize_epub(book, output_file, epub_chapters)
    console.print(
        f"\n[bold green]✨ Done![/bold green] EPUB saved at [cyan]{output_file}[/cyan]"
    )
