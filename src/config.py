"""
File cấu hình tập trung cho toàn bộ ứng dụng.
Chứa các hằng số về đường dẫn, cấu hình trình duyệt, regex pattern và template HTML/CSS.
"""

import os

from playwright.async_api import ViewportSize

# --- Cấu hình thư mục ---
# Thư mục mặc định để lưu các file HTML tải về
DEFAULT_DOWNLOAD_DIR = "downloads"
# Thư mục mặc định để lưu file EPUB sau khi chuyển đổi
DEFAULT_EPUB_DIR = "epub"
# Thư mục lưu trữ log của ứng dụng
DEFAULT_LOG_DIR = "logs"
# File lưu trữ thông tin lỗi trong quá trình chạy
ERROR_LOG_FILE = os.path.join(DEFAULT_LOG_DIR, "error.log")

# --- Cấu hình file ---
# File mặc định chứa danh sách URL cần tải
DEFAULT_URLS_FILE = "urls.txt"
# Ảnh bìa mặc định cho file EPUB
DEFAULT_COVER_IMAGE = "cover.png"

# --- Cấu hình trình duyệt (Playwright) ---
# User Agent giả lập trình duyệt Chrome trên Windows để tránh bị chặn
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
# Kích thước màn hình trình duyệt giả lập
VIEWPORT: ViewportSize = {"width": 1280, "height": 720}
# Thời gian chờ tối đa cho các tác vụ trình duyệt (ms)
BROWSER_TIMEOUT = 60000
# Số lần cuộn trang để tải thêm nội dung (Lazy loading)
SCRAPING_SCROLL_COUNT = 3
# Thời gian chờ giữa các lần cuộn trang (giây)
SCRAPING_SCROLL_DELAY = 1.5
# Thời gian nghỉ giữa các lần tải chương để tránh bị giới hạn tần suất (giây)
DOWNLOAD_DELAY = 1.0

# --- Các mẫu biểu thức chính quy (Regex) ---
# Nhận diện chương trong URL hoặc tên file
CHAPTER_PATTERN = r"(chuong-\d+)"
# Trích xuất số chương từ chuỗi
CHAPTER_NUMBER_PATTERN = r"chuong-(\d+)"
# Các ký tự không hợp lệ trong tên file (cần loại bỏ)
SAFE_FILENAME_PATTERN = r'[\\/*?:"<>|]'

# --- HTML Templates ---
# Template cho các file HTML trung gian sau khi tải về
HTML_TEMPLATE = """
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

# Định dạng CSS cho nội dung truyện bên trong file EPUB
EPUB_CSS = (
    'body { font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; margin: 20px; } '
    "h1 { text-align: center; color: #ff6600; } "
    "p { margin-bottom: 0.8em; text-indent: 1em; text-align: justify; }"
)
