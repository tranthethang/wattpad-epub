"""
Module chịu trách nhiệm tạo và cấu trúc file EPUB.
Sử dụng thư viện ebooklib để xây dựng nội dung sách, bao gồm metadata, chương, TOC và file định dạng.
"""

import os
import httpx
from ebooklib import epub
from slugify import slugify
from bs4 import BeautifulSoup

from ..config import EPUB_CSS


def create_epub_book(title: str, author: str, cover_path: str | None = None):
    """
    Khởi tạo một đối tượng sách EPUB với các thông tin cơ bản.
    Trả về đối tượng book và file CSS dùng chung.
    """
    book = epub.EpubBook()
    # Thiết lập các metadata cơ bản
    book.set_identifier(slugify(title))
    book.set_title(title)
    book.set_language("vi")
    book.add_author(author)

    # Khởi tạo và thêm file CSS để định dạng hiển thị cho các chương
    nav_css = epub.EpubItem(
        uid="style_nav",
        file_name="style/nav.css",
        media_type="text/css",
        content=EPUB_CSS,
    )
    book.add_item(nav_css)

    # Thêm ảnh bìa nếu có đường dẫn
    if cover_path:
        add_cover(book, cover_path)

    return book, nav_css


def add_cover(book, cover_path: str):
    """
    Thêm ảnh bìa vào sách. Hỗ trợ cả đường dẫn local và URL từ internet.
    """
    if cover_path.startswith(("http://", "https://")):
        try:
            # Tải ảnh từ URL nếu cover_path là một link
            response = httpx.get(cover_path)
            response.raise_for_status()
            book.set_cover("cover.jpg", response.content)
        except Exception as e:
            print(f"Lỗi khi tải ảnh bìa từ URL: {e}")
    elif os.path.exists(cover_path):
        # Đọc file từ bộ nhớ local nếu tồn tại
        book.set_cover("cover.jpg", open(cover_path, "rb").read())


def add_chapter_to_book(book, nav_css, title: str, content: str, index: int, base_dir: str | None = None):
    """
    Tạo một chương mới (file XHTML) và thêm vào đối tượng sách.
    Nếu nội dung có chứa ảnh nội bộ (local path), sẽ tự động nhúng ảnh vào EPUB.
    """
    # Đánh mã chương dựa trên chỉ số để đảm bảo thứ tự
    chap_id = f"chap_{index:04d}"
    file_name = f"{chap_id}.xhtml"

    # Kiểm tra và xử lý ảnh nếu có
    if base_dir and "<img " in content:
        soup = BeautifulSoup(content, "lxml")
        images = soup.find_all("img")
        for img in images:
            src = img.get("src")
            if src and not src.startswith(("http://", "https://")):
                # Đây là một ảnh local, cần nhúng vào EPUB
                # Giả định src là đường dẫn tương đối từ base_dir (thường là images/...)
                local_img_path = os.path.normpath(os.path.join(base_dir, src))
                
                if os.path.exists(local_img_path):
                    # Tạo item ảnh cho EPUB
                    # ebooklib yêu cầu file_name trong EPUB (thường là images/...)
                    img_id = f"img_{slugify(src)}"
                    
                    # Kiểm tra xem ảnh đã được thêm vào book chưa (tránh trùng lặp)
                    is_already_added = False
                    for item in book.get_items():
                        if item.file_name == src:
                            is_already_added = True
                            break
                    
                    if not is_already_added:
                        with open(local_img_path, "rb") as f:
                            img_data = f.read()
                        
                        # Xác định media type dựa trên extension
                        ext = src.split(".")[-1].lower()
                        media_type = f"image/{ext}"
                        if ext == "jpg" or ext == "jpeg": media_type = "image/jpeg"
                        elif ext == "png": media_type = "image/png"
                        elif ext == "gif": media_type = "image/gif"
                        elif ext == "webp": media_type = "image/webp"
                        
                        epub_img = epub.EpubItem(
                            uid=img_id,
                            file_name=src,
                            media_type=media_type,
                            content=img_data
                        )
                        book.add_item(epub_img)
        
        # Cập nhật lại content sau khi đã parse (đảm bảo XHTML valid cho EPUB)
        if soup.body:
            content = "".join([str(c) for c in soup.body.contents]).strip()

    # Khởi tạo đối tượng chương HTML
    chapter = epub.EpubHtml(title=title, file_name=file_name, lang="vi", uid=chap_id)
    # Gán nội dung HTML cho chương
    chapter.content = f'<h1>{title}</h1><div class="content">{content}</div>'
    # Gắn CSS vào chương
    chapter.add_item(nav_css)
    # Thêm chương vào sách
    book.add_item(chapter)
    return chapter


def finalize_epub(book, output_path: str, chapters: list):
    """
    Hoàn thiện cấu trúc sách: tạo mục lục (TOC), định nghĩa thứ tự đọc (spine) và ghi ra file.
    """
    # Xây dựng danh sách liên kết cho mục lục
    book.toc = tuple([epub.Link(c.file_name, c.title, c.id) for c in chapters])

    # Thêm các file điều hướng tiêu chuẩn của EPUB
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Định nghĩa spine (xương sống của sách - quyết định thứ tự lật trang)
    # 'nav' là trang mục lục mặc định
    book.spine = ["nav"] + chapters

    # Ghi toàn bộ dữ liệu ra file EPUB vật lý
    epub.write_epub(output_path, book, {})
