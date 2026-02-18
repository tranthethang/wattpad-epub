"""
Các hàm tiện ích dùng chung cho toàn bộ dự án.
Bao gồm các hàm xử lý tên file, định dạng văn bản và trích xuất nội dung HTML.
"""

import re

from bs4 import BeautifulSoup
from slugify import slugify


def clean_filename(title: str) -> str:
    """
    Chuyển đổi tiêu đề truyện thành một tên file an toàn (slug).
    Ví dụ: "Truyện Của Tôi" -> "truyen-cua-toi"
    """
    if not title:
        return "untitled_story"
    return slugify(title)


def process_text_for_line_breaks(text: str) -> str:
    """
    Chuẩn hóa xuống dòng và khoảng trắng trong văn bản.
    1. Chuyển nhiều khoảng trắng liên tiếp thành một.
    2. Chuẩn hóa nhiều dấu xuống dòng thành hai dấu (phân cách đoạn văn).
    """
    # Thay thế 2 hoặc nhiều khoảng trắng bằng 1 khoảng trắng
    text = re.sub(r" {2,}", " ", text)
    # Đầu tiên, chuẩn hóa tất cả các cụm xuống dòng thành một dấu xuống dòng duy nhất
    text = re.sub(r"\n+", "\n", text)
    # Sau đó, biến mỗi dấu xuống dòng đơn lẻ thành hai dấu để phân tách đoạn văn rõ ràng
    text = re.sub(r"\n", "\n\n", text)
    return text.strip()


def text_to_html_paragraphs(text: str) -> str:
    """
    Chuyển đổi văn bản thuần túy (với dấu xuống dòng kép) thành các thẻ HTML <p>.
    Dùng để tạo nội dung cho file EPUB.
    """
    # Tách văn bản thành các đoạn dựa trên dấu xuống dòng kép
    paragraphs = text.split("\n\n")
    # Bọc mỗi đoạn trong thẻ <p>
    return "".join(f"<p>{p.strip()}</p>" for p in paragraphs if p.strip())


def extract_main_content(html: str) -> str:
    """
    Sử dụng BeautifulSoup để trích xuất nội dung văn bản hoặc ảnh từ mã HTML.
    Tìm kiếm các thẻ div có class là 'truyen' hoặc 'content'.
    """
    soup = BeautifulSoup(html, "lxml")
    # Tìm thẻ div chứa nội dung truyện (hỗ trợ cả giao diện web và file local)
    content_div = soup.find("div", class_=re.compile(r"(truyen|content)"))

    if not content_div:
        return None

    # Lấy toàn bộ text bên trong, phân cách các thẻ con bằng dấu xuống dòng
    text = content_div.get_text(separator="\n", strip=True)
    processed_text = process_text_for_line_breaks(text)

    # Kiểm tra xem có ảnh không (fallback cho truyện dạng ảnh)
    images = content_div.find_all("img")
    
    # Nếu có ảnh và text quá ngắn hoặc rỗng, ưu tiên lấy ảnh
    # Một số trang có text rác hoặc ký tự đặc biệt làm processed_text không rỗng hoàn toàn
    if images and (not processed_text or len(processed_text) < 50):
        img_tags = []
        for img in images:
            # Ưu tiên data-url (thường dùng cho lazy loading), sau đó đến src
            img_src = img.get("data-url") or img.get("src")
            if img_src:
                # Trả về tag img với src gốc để scraper_service xử lý tải về sau
                img_tags.append(f'<img src="{img_src}" alt="Chapter Image" />')
        
        if img_tags:
            return "\n".join(img_tags)

    # Nếu có text thực sự và không bị ghi đè bởi ảnh
    if processed_text:
        return processed_text

    return None
