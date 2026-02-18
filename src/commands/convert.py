"""
Thực thi lệnh 'convert' để chuyển đổi các file HTML đã tải thành file EPUB.
Xử lý sắp xếp chương, trích xuất nội dung và đóng gói vào định dạng EPUB.
"""

import os
import re

from rich.console import Console

from ..config import (CHAPTER_NUMBER_PATTERN, DEFAULT_COVER_IMAGE,
                      DEFAULT_DOWNLOAD_DIR, DEFAULT_EPUB_DIR,
                      SAFE_FILENAME_PATTERN)
from ..core.epub_factory import (add_chapter_to_book, create_epub_book,
                                 finalize_epub)
from ..utils import extract_main_content, text_to_html_paragraphs

# Khởi tạo console để in thông báo có màu sắc và định dạng
console = Console()


def run_convert(
    input_dir: str, output_file: str | None, title: str, author: str, cover: str
):
    """
    Hàm chính xử lý quá trình chuyển đổi từ thư mục HTML sang file EPUB.
    """
    # Kiểm tra sự tồn tại của thư mục chứa HTML đầu vào
    if not os.path.exists(input_dir):
        console.print(f"[red]Lỗi:[/red] Thư mục {input_dir} không tồn tại.")
        return

    # Nếu không chỉ định tên file đầu ra, tự động tạo tên dựa trên tác giả và tiêu đề
    if not output_file:
        safe_author = re.sub(SAFE_FILENAME_PATTERN, "", author)
        safe_title = re.sub(SAFE_FILENAME_PATTERN, "", title)
        output_file = os.path.join(DEFAULT_EPUB_DIR, f"{safe_author}_{safe_title}.epub")

    # Tạo thư mục lưu file EPUB nếu chưa có
    if not os.path.exists(DEFAULT_EPUB_DIR):
        os.makedirs(DEFAULT_EPUB_DIR)

    # Lấy danh sách các file HTML trong thư mục đầu vào
    html_files = [f for f in os.listdir(input_dir) if f.endswith(".html")]
    if not html_files:
        console.print(
            f"[yellow]Cảnh báo:[/yellow] Không tìm thấy file HTML nào trong {input_dir}."
        )
        return

    def extract_chapter_number(filename):
        """Hàm helper trích xuất số chương từ tên file (ví dụ: chuong-1 -> 1)."""
        match = re.search(CHAPTER_NUMBER_PATTERN, filename)
        return int(match.group(1)) if match else 0

    def extract_file_index(filename):
        """Hàm helper trích xuất index từ đầu tên file (4 chữ số đầu) để sắp xếp."""
        if len(filename) > 4 and filename[:4].isdigit():
            return int(filename[:4])
        # Fallback về số chương nếu không có index prefix
        return extract_chapter_number(filename)

    # Sắp xếp các file theo index prefix (0001, 0002, ...) để đảm bảo đúng thứ tự
    html_files.sort(key=extract_file_index)

    # Khởi tạo đối tượng sách EPUB
    book, nav_css = create_epub_book(title, author, cover)
    epub_chapters = []

    # Duyệt qua từng file HTML để xử lý và thêm vào sách
    for i, file_name in enumerate(html_files):
        file_path = os.path.join(input_dir, file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Xác định tiêu đề chương và trích xuất nội dung chính
        chapter_title = f"Chương {extract_chapter_number(file_name)}"
        raw_content = extract_main_content(html_content)
        
        # Nếu nội dung chứa thẻ img, không cần bọc <p> (đã có sẵn tag)
        if raw_content and "<img " in raw_content:
            html_content_processed = raw_content
        else:
            # Chuyển đổi văn bản thuần sang các thẻ <p>
            html_content_processed = text_to_html_paragraphs(raw_content)

        # Thêm chương vào đối tượng sách
        chapter = add_chapter_to_book(
            book, nav_css, chapter_title, html_content_processed, i + 1, base_dir=input_dir
        )
        epub_chapters.append(chapter)

    # Hoàn thiện và ghi file EPUB
    finalize_epub(book, output_file, epub_chapters)
    console.print(
        f"\n[bold green]✨ Hoàn thành![/bold green] Đã lưu EPUB tại [cyan]{output_file}[/cyan]"
    )
