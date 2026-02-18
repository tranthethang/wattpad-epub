import os
import re
from pathlib import Path

from bs4 import BeautifulSoup
from rich.console import Console

console = Console()


def is_empty_content(html_content: str) -> bool:
    """
    Kiểm tra xem nội dung HTML có thực sự rỗng hay không,
    kể cả khi có các ký tự đặc biệt như zero-width space.
    """
    # Loại bỏ các ký tự khoảng trắng thông thường và các ký tự vô hình phổ biến
    # \u200b: zero width space
    # \u200c: zero width non-joiner
    # \u200d: zero width joiner
    # \ufeff: zero width no-break space (BOM)
    cleaned = re.sub(r'[\s\u200b\u200c\u200d\ufeff]+', '', html_content)
    return len(cleaned) == 0


def run_clean(directory: str):
    """
    Xoá các file .html nếu <div class="content"> rỗng.
    """
    path = Path(directory)
    if not path.exists() or not path.is_dir():
        console.print(f"[red]Thư mục {directory} không tồn tại.[/red]")
        return

    html_files = list(path.glob("*.html"))
    if not html_files:
        console.print(f"[yellow]Không tìm thấy file .html nào trong {directory}.[/yellow]")
        return

    console.print(f"Đang kiểm tra {len(html_files)} file trong {directory}...")

    deleted_count = 0
    for file_path in html_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            soup = BeautifulSoup(content, "lxml")
            content_div = soup.find("div", class_="content")

            should_delete = False
            if not content_div:
                # Nếu không tìm thấy tag content, có thể coi là lỗi/rỗng tùy quan điểm
                # Ở đây ta chỉ xóa nếu nó tồn tại nhưng innerHtml rỗng sau khi trim
                pass
            else:
                # innerHtml rỗng sau khi loại bỏ khoảng trắng và ký tự vô hình
                inner_html = content_div.decode_contents()
                if is_empty_content(inner_html):
                    should_delete = True

            if should_delete:
                os.remove(file_path)
                console.print(f"[green]Đã xoá file rỗng:[/green] {file_path.name}")
                deleted_count += 1

        except Exception as e:
            console.print(f"[red]Lỗi khi xử lý {file_path.name}: {e}[/red]")

    console.print(f"[bold green]Hoàn thành! Đã xoá {deleted_count} file.[/bold green]")
