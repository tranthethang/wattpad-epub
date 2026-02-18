"""
Main entry point của ứng dụng wattpad-epub.
Sử dụng Typer để tạo CLI interface cho các tác vụ:
1. Lấy danh sách URL chương từ API.
2. Tải nội dung HTML từ danh sách URL.
3. Chuyển đổi HTML thành file EPUB.
"""

import asyncio

import typer

from .commands.clean import run_clean
from .commands.convert import run_convert
from .commands.download import run_download
from .commands.get_urls import run_get_urls
from .config import (DEFAULT_COVER_IMAGE, DEFAULT_DOWNLOAD_DIR,
                     DEFAULT_EPUB_DIR, DEFAULT_URLS_FILE)

# Khởi tạo Typer app
app = typer.Typer(help="Công cụ tải và chuyển đổi truyện từ Wattpad sang EPUB")


@app.command()
def download(
    file_list: str = typer.Argument(
        DEFAULT_URLS_FILE, help="File .txt chứa danh sách URL các chương"
    ),
    output: str = typer.Option(
        DEFAULT_DOWNLOAD_DIR,
        "--output",
        "-o",
        help="Thư mục lưu trữ các file HTML tải về",
    ),
    concurrency: int = typer.Option(
        4, "--concurrency", "-c", help="Số lượng tiến trình tải đồng thời"
    ),
):
    """
    Tải nội dung HTML từ danh sách URL đã cho.
    Sử dụng Playwright để vượt qua các cơ chế chống bot.
    """
    asyncio.run(run_download(file_list, output, concurrency))


@app.command()
def get_urls(
    api_url: str = typer.Argument(..., help="URL của API lấy danh sách chương"),
    page_from: int = typer.Argument(..., help="Trang bắt đầu lấy dữ liệu"),
    page_to: int = typer.Argument(..., help="Trang kết thúc lấy dữ liệu"),
    output_file: str = typer.Option(
        DEFAULT_URLS_FILE, "--output", "-o", help="Đường dẫn file để lưu danh sách URL"
    ),
):
    """
    Truy vấn API để lấy danh sách URL các chương và lưu vào file text.
    Thường dùng khi truyện có quá nhiều chương và cần lấy URL hàng loạt.
    """
    asyncio.run(run_get_urls(api_url, page_from, page_to, output_file))


@app.command()
def convert(
    input_dir: str = typer.Option(
        DEFAULT_DOWNLOAD_DIR, "--input", "-i", help="Thư mục chứa các file HTML đầu vào"
    ),
    output_file: str | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Đường dẫn và tên file EPUB đầu ra (mặc định dựa trên tiêu đề)",
    ),
    title: str = typer.Option(
        "Wattpad Story", "--title", "-t", help="Tiêu đề của truyện"
    ),
    author: str = typer.Option("Unknown", "--author", "-a", help="Tên tác giả"),
    cover: str = typer.Option(
        DEFAULT_COVER_IMAGE,
        "--cover",
        "-c",
        help="Đường dẫn tới file ảnh bìa (cover image)",
    ),
):
    """
    Tổng hợp các file HTML trong thư mục thành một file EPUB hoàn chỉnh.
    Tự động xử lý thứ tự chương dựa trên tên file.
    """
    run_convert(input_dir, output_file, title, author, cover)


@app.command()
def clean(
    directory: str = typer.Argument(
        DEFAULT_DOWNLOAD_DIR, help="Thư mục chứa các file HTML cần kiểm tra"
    ),
):
    """
    Kiểm tra và xoá các file HTML nếu nội dung <div class="content"> rỗng.
    """
    run_clean(directory)


if __name__ == "__main__":
    # Điểm khởi chạy của chương trình
    app()
