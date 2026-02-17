import asyncio

import typer

from .commands.convert import run_convert
from .commands.download import run_download
from .commands.get_urls import run_get_urls
from .config import (DEFAULT_COVER_IMAGE, DEFAULT_DOWNLOAD_DIR,
                     DEFAULT_EPUB_DIR, DEFAULT_URLS_FILE)

app = typer.Typer()


@app.command()
def download(
    file_list: str = typer.Argument(DEFAULT_URLS_FILE, help="File .txt chứa URL"),
    output: str = typer.Option(
        DEFAULT_DOWNLOAD_DIR, "--output", "-o", help="Thư mục lưu HTML"
    ),
    concurrency: int = typer.Option(
        4, "--concurrency", "-c", help="Số lượng luồng tải"
    ),
):
    """Tải nội dung HTML từ Wattpad."""
    asyncio.run(run_download(file_list, output, concurrency))


@app.command()
def get_urls(
    api_url: str = typer.Argument(..., help="URL API"),
    page_from: int = typer.Argument(..., help="Trang bắt đầu"),
    page_to: int = typer.Argument(..., help="Trang kết thúc"),
    output_file: str = typer.Option(
        DEFAULT_URLS_FILE, "--output", "-o", help="File lưu URL"
    ),
):
    """Lấy danh sách URL chương từ API."""
    asyncio.run(run_get_urls(api_url, page_from, page_to, output_file))


@app.command()
def convert(
    input_dir: str = typer.Option(
        DEFAULT_DOWNLOAD_DIR, "--input", "-i", help="Thư mục chứa HTML"
    ),
    output_file: str = typer.Option(None, "--output", "-o", help="Tên file EPUB"),
    title: str = typer.Option("Wattpad Story", "--title", "-t", help="Tiêu đề truyện"),
    author: str = typer.Option("Unknown", "--author", "-a", help="Tác giả"),
    cover: str = typer.Option(
        DEFAULT_COVER_IMAGE, "--cover", "-c", help="Đường dẫn ảnh cover"
    ),
):
    """Chuyển đổi file HTML thành EPUB."""
    run_convert(input_dir, output_file, title, author, cover)


if __name__ == "__main__":
    app()
