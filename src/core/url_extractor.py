"""
Module chịu trách nhiệm trích xuất danh sách URL từ API.
Cung cấp các hàm để xây dựng URL API và phân tích cú pháp HTML trả về từ API.
"""

from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import httpx
from bs4 import BeautifulSoup


def build_api_url(base_api_url: str, page: int) -> str:
    """
    Xây dựng URL API với tham số phân trang.
    Tự động cập nhật hoặc thêm tham số 'page' vào URL gốc.
    """
    parsed_url = urlparse(base_api_url)
    query = parse_qs(parsed_url.query)
    # Cập nhật giá trị trang
    query["page"] = [str(page)]
    # Encode lại các tham số truy vấn
    new_query = urlencode(query, doseq=True)
    # Trả về URL hoàn chỉnh đã được cập nhật trang
    return urlunparse(parsed_url._replace(query=new_query))


def extract_urls_from_html(html_content: str, base_domain: str) -> list:
    """
    Phân tích đoạn mã HTML (thường nằm trong JSON response của API) để tìm các thẻ <a>.
    Chuyển đổi các đường dẫn tương đối thành đường dẫn tuyệt đối.
    """
    soup = BeautifulSoup(html_content, "lxml")
    urls = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # Đảm bảo href là chuỗi
        if isinstance(href, list):
            href = "".join(href)
        # Nếu là đường dẫn tương đối, ghép với domain gốc
        if href.startswith("/"):
            href = f"{base_domain}{href}"
        # Chỉ lấy các URL hợp lệ
        if href.startswith(("http://", "https://")):
            urls.append(href)
    return urls


async def fetch_page_urls(
    client: httpx.AsyncClient, url: str, base_domain: str
) -> list:
    """
    Thực hiện request không đồng bộ tới API để lấy danh sách URL.
    Giả định API trả về định dạng JSON có chứa trường 'data' là mã HTML.
    """
    response = await client.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()
    # Trích xuất URL từ trường 'data' trong JSON
    return extract_urls_from_html(data.get("data", ""), base_domain)
