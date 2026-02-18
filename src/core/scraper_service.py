"""
Dịch vụ cào dữ liệu (Scraping Service) sử dụng Playwright.
Chịu trách nhiệm tương tác với trình duyệt, giả lập người dùng và trích xuất nội dung từ các trang web.
"""

import asyncio
import os
import httpx
from bs4 import BeautifulSoup

from playwright.async_api import Browser
from playwright_stealth import Stealth
from slugify import slugify

from ..config import (BROWSER_TIMEOUT, HTML_TEMPLATE, SCRAPING_SCROLL_COUNT,
                      SCRAPING_SCROLL_DELAY, USER_AGENT, VIEWPORT)
from ..utils import extract_main_content


async def download_image(client: httpx.AsyncClient, url: str, save_path: str) -> bool:
    """
    Tải một ảnh từ URL và lưu vào đĩa.
    """
    try:
        response = await client.get(url, timeout=30.0)
        if response.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"Lỗi khi tải ảnh {url}: {e}")
    return False


async def get_page_html(browser: Browser, url: str):
    """
    Sử dụng Playwright để truy cập vào một URL và lấy nội dung HTML của trang.
    Áp dụng các kỹ thuật Stealth để tránh bị phát hiện là bot.
    """
    # Tạo một ngữ cảnh duyệt web mới với User Agent và Viewport tùy chỉnh
    context = await browser.new_context(user_agent=USER_AGENT, viewport=VIEWPORT)
    page = await context.new_page()

    # Áp dụng Stealth để giả lập các thuộc tính của trình duyệt người dùng thật
    await Stealth().apply_stealth_async(page)

    try:
        # Điều hướng đến URL và đợi cho đến khi DOM được tải xong
        await page.goto(url, wait_until="domcontentloaded", timeout=BROWSER_TIMEOUT)

        # Giả lập cuộn trang để kích hoạt Lazy Loading (nếu có)
        for _ in range(SCRAPING_SCROLL_COUNT):
            await page.mouse.wheel(0, 1000)
            await asyncio.sleep(SCRAPING_SCROLL_DELAY)

        # Lấy tiêu đề trang để kiểm tra tính hợp lệ
        title = await page.title()
        if not title or "error" in title.lower():
            return None

        # Trả về mã nguồn HTML và tiêu đề trang
        return {"html": await page.content(), "title": title}
    except Exception as e:
        # Chuyển tiếp ngoại lệ để lớp Command xử lý ghi log
        raise e
    finally:
        # Luôn đóng context để giải phóng tài nguyên trình duyệt
        await context.close()


async def save_chapter(output_dir: str, title: str, html_content: str, file_name: str):
    """
    Xử lý nội dung HTML thô, tải ảnh nếu có, và lưu thành file HTML đã được làm sạch.
    """
    file_path = os.path.join(output_dir, file_name)

    # Trích xuất phần nội dung chính từ HTML thô
    content = extract_main_content(html_content)
    if not content:
        return None

    # Kiểm tra xem nội dung có chứa thẻ img không (đã được extract_main_content xử lý)
    if "<img " in content:
        soup = BeautifulSoup(content, "lxml")
        images = soup.find_all("img")
        
        if images:
            # Tạo thư mục images nếu chưa có
            img_dir = os.path.join(output_dir, "images")
            if not os.path.exists(img_dir):
                os.makedirs(img_dir)
            
            # Sử dụng httpx để tải ảnh đồng thời
            async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}, follow_redirects=True) as client:
                tasks = []
                for i, img in enumerate(images):
                    original_src = img.get("src")
                    if not original_src:
                        continue
                    
                    # Tạo tên file ảnh an toàn dựa trên index chương và index ảnh
                    chap_idx = file_name[:4]
                    # Lấy extension từ URL
                    parsed_ext = original_src.split(".")[-1].split("?")[0].lower()
                    if parsed_ext not in ["jpg", "jpeg", "png", "gif", "webp"]:
                        parsed_ext = "png"
                    
                    img_filename = f"{chap_idx}_{i+1:03d}.{parsed_ext}"
                    img_save_path = os.path.join(img_dir, img_filename)
                    
                    # Thêm task tải ảnh
                    tasks.append(download_image(client, original_src, img_save_path))
                    
                    # Cập nhật lại src trong HTML thành đường dẫn tương đối
                    img["src"] = f"images/{img_filename}"
                
                # Chờ tất cả ảnh được tải xong
                if tasks:
                    await asyncio.gather(*tasks)
            
            # Cập nhật lại content sau khi đã thay đổi src của ảnh
            if soup.body:
                content = "".join([str(c) for c in soup.body.contents]).strip()
            else:
                content = str(soup)

    # Bọc nội dung văn bản vào template HTML chuẩn của dự án
    final_html = HTML_TEMPLATE.format(title=title, content=content)

    # Ghi nội dung vào file vật lý
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(final_html)
    return file_path
