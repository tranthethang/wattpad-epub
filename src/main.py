import asyncio
import os
import re
import typer
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from slugify import slugify
from playwright.async_api import async_playwright
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from .scraper import get_page_html
from .utils import extract_main_content, format_html_template, create_epub

app = typer.Typer()
console = Console()

def log_error(url: str):
    """Ghi lỗi vào logs/error.log"""
    if not os.path.exists("logs"):
        os.makedirs("logs")
    with open("logs/error.log", "a", encoding="utf-8") as f:
        f.write(f"{url}\n")

@app.command()
def download(
    file_list: str = typer.Argument(..., help="Đường dẫn tới file .txt chứa danh sách URL"),
    output: str = typer.Option("downloads", "--output", "-o", help="Thư mục lưu file HTML")
):
    """
    Ứng dụng CLI tải nội dung HTML từ Wattpad giả lập người dùng.
    """
    if not os.path.exists(file_list):
        console.print(f"[red]Lỗi:[/red] File {file_list} không tồn tại.")
        raise typer.Exit()

    if not os.path.exists(output):
        os.makedirs(output)

    with open(file_list, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip().startswith(("http://", "https://"))]

    if not urls:
        console.print("[yellow]Cảnh báo:[/yellow] Không tìm thấy URL hợp lệ nào trong file.")
        raise typer.Exit()

    async def run_scraping():
        # Lấy danh sách prefix đã tải để bỏ qua
        existing_files = os.listdir(output)
        existing_prefixes = set()
        for f in existing_files:
            match = re.search(r'(chuong-\d+)', f)
            if match:
                existing_prefixes.add(match.group(1))

        async with async_playwright() as p:
            # Chạy Chrome ngầm (headless=True). Nếu bị chặn, hãy đổi thành False để debug
            browser = await p.chromium.launch(headless=True)

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task(description="Đang xử lý...", total=len(urls))

                for url in urls:
                    # Lấy chapter prefix để hiển thị trạng thái
                    url_match = re.search(r'(chuong-\d+)', url)
                    prefix = url_match.group(1) if url_match else url[:30]

                    try:
                        # Kiểm tra prefix xem đã tải chưa
                        if url_match:
                            if prefix in existing_prefixes:
                                console.print(f"[yellow]Bỏ qua:[/yellow] {prefix} (Đã tồn tại)")
                                progress.advance(task)
                                continue

                        progress.update(task, description=f"Đang tải: {prefix}...")
                        data = await get_page_html(browser, url)

                        if not data or not data.get('html'):
                            console.print(f"[red]Thất bại:[/red] {prefix} (Không lấy được nội dung)")
                            log_error(url)
                            progress.advance(task)
                            continue

                        file_name = f"{slugify(data['title'])}.html"
                        file_path = os.path.join(output, file_name)

                        # Trích xuất và xử lý nội dung từ <div class="truyen">
                        content = extract_main_content(data['html'])
                        # Bọc vào template HTML để dễ đọc hơn
                        final_html = format_html_template(data['title'], content)

                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(final_html)

                        console.print(f"[green]Thành công:[/green] {prefix}")
                        progress.advance(task)
                        # Nghỉ một khoảng ngẫu nhiên để tránh bị Wattpad nghi ngờ
                        await asyncio.sleep(2)
                    except Exception as e:
                        console.print(f"[red]Lỗi:[/red] {prefix} - {e}")
                        log_error(url)
                        progress.advance(task)

            await browser.close()
            console.print(f"\n[bold green]✨ Hoàn thành![/bold green] Đã lưu vào thư mục: [cyan]{output}[/cyan]")

    asyncio.run(run_scraping())

@app.command()
def get_urls(
    api_url: str = typer.Argument(..., help="URL API (ví dụ: https://wattpad.com.vn/get/listchap/85995?page=1)"),
    page_from: int = typer.Argument(..., help="Trang bắt đầu"),
    page_to: int = typer.Argument(..., help="Trang kết thúc"),
    output_file: str = typer.Option("urls.txt", "--output", "-o", help="File lưu danh sách URL")
):
    """
    Lấy danh sách URL chương từ API và lưu vào file.
    """
    parsed_url = urlparse(api_url)
    base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
    query = parse_qs(parsed_url.query)

    all_urls = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(description="Đang lấy danh sách URL...", total=(page_to - page_from + 1))

        for page in range(page_from, page_to + 1):
            query['page'] = [str(page)]
            new_query = urlencode(query, doseq=True)
            target_url = urlunparse(parsed_url._replace(query=new_query))

            try:
                progress.update(task, description=f"Đang lấy page {page}...")
                response = httpx.get(target_url, timeout=30)
                response.raise_for_status()
                data = response.json()
                html_content = data.get('data', '')

                soup = BeautifulSoup(html_content, 'lxml')
                page_urls = []
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if href.startswith('/'):
                        href = f"{base_domain}{href}"
                    page_urls.append(href)
                
                all_urls.extend(page_urls)
                progress.advance(task)
            except Exception as e:
                console.print(f"\n[red]Lỗi khi lấy page {page}:[/red] {e}")

    if all_urls:
        with open(output_file, "a", encoding="utf-8") as f:
            for url in all_urls:
                f.write(f"{url}\n")
        console.print(f"\n[bold green]✨ Hoàn thành![/bold green] Đã thêm [cyan]{len(all_urls)}[/cyan] URL vào [cyan]{output_file}[/cyan]")
    else:
        console.print("\n[yellow]Cảnh báo:[/yellow] Không tìm thấy URL nào.")

@app.command()
def convert(
    input_dir: str = typer.Option("downloads", "--input", "-i", help="Thư mục chứa file HTML"),
    output_file: str = typer.Option(None, "--output", "-o", help="Tên file EPUB đầu ra (mặc định: tác-gia_ten-sach.epub)"),
    title: str = typer.Option("Wattpad Story", "--title", "-t", help="Tiêu đề truyện"),
    author: str = typer.Option("Unknown", "--author", "-a", help="Tác giả"),
    cover: str = typer.Option("cover.png", "--cover", "-c", help="Đường dẫn hoặc URL ảnh cover")
):
    """
    Chuyển đổi các file HTML trong thư mục thành file EPUB.
    """
    if not os.path.exists(input_dir):
        console.print(f"[red]Lỗi:[/red] Thư mục {input_dir} không tồn tại.")
        raise typer.Exit()

    # Tự động tạo tên file nếu không cung cấp
    if not output_file:
        # Giữ nguyên tên gốc, chỉ thay khoảng trắng/ký tự đặc biệt nếu cần để an toàn cho file system
        safe_author = re.sub(r'[\\/*?:"<>|]', "", author)
        safe_title = re.sub(r'[\\/*?:"<>|]', "", title)
        output_file = f"{safe_author}_{safe_title}.epub"
    
    # Đảm bảo file được lưu vào thư mục ./epub
    epub_dir = "epub"
    if not os.path.exists(epub_dir):
        os.makedirs(epub_dir)
    
    # Nếu output_file chỉ là tên file, nối với thư mục epub
    if not os.path.dirname(output_file):
        output_file = os.path.join(epub_dir, output_file)

    html_files = [f for f in os.listdir(input_dir) if f.endswith(".html")]
    if not html_files:
        console.print(f"[yellow]Cảnh báo:[/yellow] Không tìm thấy file HTML nào trong {input_dir}.")
        raise typer.Exit()

    # Sắp xếp các file theo số chương
    def extract_chapter_number(filename):
        match = re.search(r'chuong-(\d+)', filename)
        return int(match.group(1)) if match else 0

    html_files.sort(key=extract_chapter_number)

    chapters = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(description="Đang đọc các chương...", total=len(html_files))

        for filename in html_files:
            file_path = os.path.join(input_dir, filename)
            progress.update(task, description=f"Đang xử lý: {filename}")
            
            with open(file_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), 'lxml')
                # Lấy title từ thẻ h1 hoặc title
                h1 = soup.find('h1')
                chapter_title = h1.get_text() if h1 else filename
                
                # Nội dung nằm trong div.content
                content_div = soup.find('div', class_='content')
                if content_div:
                    chapter_content = str(content_div)
                else:
                    chapter_content = soup.prettify()

                chapters.append({
                    'title': chapter_title,
                    'content': chapter_content
                })
            progress.advance(task)

    console.print(f"Đang tạo file EPUB: [cyan]{output_file}[/cyan]...")
    try:
        create_epub(output_file, title, author, chapters, cover)
        console.print(f"[bold green]✨ Hoàn thành![/bold green] Đã tạo file: [cyan]{output_file}[/cyan]")
    except Exception as e:
        console.print(f"[red]Lỗi khi tạo EPUB:[/red] {e}")

if __name__ == "__main__":
    app()
