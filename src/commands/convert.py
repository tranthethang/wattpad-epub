import os
import re

from rich.console import Console

from ..config import (CHAPTER_NUMBER_PATTERN, DEFAULT_COVER_IMAGE,
                      DEFAULT_DOWNLOAD_DIR, DEFAULT_EPUB_DIR,
                      SAFE_FILENAME_PATTERN)
from ..core.epub_factory import (add_chapter_to_book, create_epub_book,
                                 finalize_epub)
from ..utils import extract_main_content, text_to_html_paragraphs

console = Console()


def run_convert(input_dir: str, output_file: str, title: str, author: str, cover: str):
    if not os.path.exists(input_dir):
        console.print(f"[red]Lỗi:[/red] Thư mục {input_dir} không tồn tại.")
        return

    if not output_file:
        safe_author = re.sub(SAFE_FILENAME_PATTERN, "", author)
        safe_title = re.sub(SAFE_FILENAME_PATTERN, "", title)
        output_file = os.path.join(DEFAULT_EPUB_DIR, f"{safe_author}_{safe_title}.epub")

    if not os.path.exists(DEFAULT_EPUB_DIR):
        os.makedirs(DEFAULT_EPUB_DIR)

    html_files = [f for f in os.listdir(input_dir) if f.endswith(".html")]
    if not html_files:
        console.print(
            f"[yellow]Cảnh báo:[/yellow] Không tìm thấy file HTML nào trong {input_dir}."
        )
        return

    def extract_chapter_number(filename):
        match = re.search(CHAPTER_NUMBER_PATTERN, filename)
        return int(match.group(1)) if match else 0

    html_files.sort(key=extract_chapter_number)

    book, nav_css = create_epub_book(title, author, cover)
    epub_chapters = []

    for i, file_name in enumerate(html_files):
        file_path = os.path.join(input_dir, file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        chapter_title = f"Chương {extract_chapter_number(file_name)}"
        raw_text = extract_main_content(html_content)
        html_paragraphs = text_to_html_paragraphs(raw_text)

        chapter = add_chapter_to_book(
            book, nav_css, chapter_title, html_paragraphs, i + 1
        )
        epub_chapters.append(chapter)

    finalize_epub(book, output_file, epub_chapters)
    console.print(
        f"\n[bold green]✨ Hoàn thành![/bold green] Đã lưu EPUB tại [cyan]{output_file}[/cyan]"
    )
