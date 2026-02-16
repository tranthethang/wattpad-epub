import re
import os
import httpx
from bs4 import BeautifulSoup
from slugify import slugify
from ebooklib import epub

def clean_filename(title: str) -> str:
    """
    Tạo tên file an toàn từ tiêu đề truyện.
    """
    if not title:
        return "untitled_story"
    # Dùng slugify để chuyển "Truyện Của Tôi" -> "truyen-cua-toi"
    return slugify(title)

def process_text_for_line_breaks(text: str) -> str:
    """
    Thêm logic xử lý text để xuống dòng, phân biệt bằng dấu chấm câu hoặc dấu nháy kép.
    """
    # 0. Thay thế nhiều khoảng trắng bằng một khoảng trắng
    text = re.sub(r' {2,}', ' ', text)

    # 1. Thêm xuống dòng sau dấu chấm, chấm hỏi, chấm than nếu theo sau là chữ hoa
    text = re.sub(r'([.!?])\s+(?=[A-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠƯ])', r'\1\n\n', text)
    
    # 2. Thêm xuống dòng trước dấu nháy kép bắt đầu câu thoại 
    text = re.sub(r'([.!?])\s+("(?=[A-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠƯ]))', r'\1\n\n\2', text)
    
    # 3. Thêm xuống dòng sau dấu nháy kép kết thúc câu thoại
    text = re.sub(r'([.!?]")\s+(?=[A-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠƯ])', r'\1\n\n', text)
    
    # 4. Thêm xuống dòng giữa hai câu thoại sát nhau (ví dụ: "Chào!" "Chào bạn.")
    text = re.sub(r'(")\s+(")', r'\1\n\n\2', text)

    # 5. Xử lý trường hợp đặc biệt cho các dấu đối thoại khác như dấu gạch ngang
    text = re.sub(r'([.!?])\s+(- )', r'\1\n\n\2', text)
    
    # Dọn dẹp các dòng trống dư thừa
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def extract_main_content(html: str) -> str:
    """
    Trích xuất nội dung từ <div class="truyen"> và xử lý xuống dòng.
    """
    soup = BeautifulSoup(html, 'lxml')
    content_div = soup.find('div', class_='truyen')
    
    if not content_div:
        # Fallback nếu không tìm thấy div.truyen
        return "Không tìm thấy nội dung truyện."
    
    # Lấy text từ element, dùng khoảng trắng làm phân cách giữa các thẻ con
    text = content_div.get_text(separator=' ', strip=True)
    
    # Xử lý xuống dòng cho text
    return process_text_for_line_breaks(text)

def format_html_template(title: str, content: str) -> str:
    """
    Bọc nội dung vào một template HTML cơ bản để khi mở file offline
    vẫn có font chữ dễ đọc.
    """
    return f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <title>{title}</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; max-width: 800px; margin: 40px auto; padding: 20px; color: #333; }}
            h1 {{ text-align: center; color: #ff6600; }}
            .content {{ white-space: pre-wrap; }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        <div class="content">
            {content}
        </div>
    </body>
    </html>
    """

def create_epub(output_path: str, title: str, author: str, chapters: list, cover_path: str = None):
    """
    Tạo file EPUB từ danh sách các chương.
    chapters: list of dict {'title': str, 'content': str}
    """
    book = epub.EpubBook()

    # Thiết lập metadata
    book.set_identifier(slugify(title))
    book.set_title(title)
    book.set_language('vi')
    book.add_author(author)

    # Thêm cover nếu có
    if cover_path:
        if cover_path.startswith(('http://', 'https://')):
            try:
                response = httpx.get(cover_path)
                response.raise_for_status()
                book.set_cover("cover.jpg", response.content)
            except Exception as e:
                print(f"Không thể tải ảnh cover từ URL: {e}")
        elif os.path.exists(cover_path):
            book.set_cover("cover.jpg", open(cover_path, 'rb').read())

    # Thêm stylesheet cơ bản
    style = 'body { font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; margin: 20px; } ' \
            'h1 { text-align: center; color: #ff6600; } ' \
            '.content { white-space: pre-wrap; }'
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)

    # Danh sách các item EpubHtml
    epub_chapters = []
    for i, chap in enumerate(chapters):
        chap_id = f'chap_{i+1}'
        # Thêm uid rõ ràng cho mỗi chương
        c = epub.EpubHtml(title=chap['title'], file_name=f'{chap_id}.xhtml', lang='vi', uid=chap_id)
        c.add_item(nav_css)
        
        # Đảm bảo nội dung là HTML hợp lệ và có cấu trúc tốt
        inner_content = chap['content']
        
        # Nếu nội dung đã là một trang HTML đầy đủ, chúng ta chỉ lấy phần body hoặc giữ nguyên nếu cần
        if '<html>' not in inner_content.lower():
            if 'class="content"' not in inner_content:
                inner_content = f'<div class="content">{inner_content}</div>'
            c.content = f'<html><head><title>{chap["title"]}</title></head><body><h1>{chap["title"]}</h1>{inner_content}</body></html>'
        else:
            c.content = inner_content
            
        book.add_item(c)
        epub_chapters.append(c)

    # Thiết lập Table of Contents (TOC) dùng tuple của các Link
    book.toc = tuple([epub.Link(c.file_name, c.title, c.id) for c in epub_chapters])

    # Thêm các file mặc định
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Thiết lập Spine (thứ tự các chương)
    # Apple Books thường yêu cầu 'nav' đứng trước các chương
    book.spine = ['nav'] + epub_chapters

    # Lưu file
    epub.write_epub(output_path, book, {})
