import os

# Directories
DEFAULT_DOWNLOAD_DIR = "downloads"
DEFAULT_EPUB_DIR = "epub"
DEFAULT_LOG_DIR = "logs"
ERROR_LOG_FILE = os.path.join(DEFAULT_LOG_DIR, "error.log")

# Files
DEFAULT_URLS_FILE = "urls.txt"
DEFAULT_COVER_IMAGE = "cover.png"

# Browser Configuration
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
VIEWPORT = {"width": 1280, "height": 720}
BROWSER_TIMEOUT = 60000
SCRAPING_SCROLL_COUNT = 3
SCRAPING_SCROLL_DELAY = 1.5
DOWNLOAD_DELAY = 1.0

# Patterns
CHAPTER_PATTERN = r"(chuong-\d+)"
CHAPTER_NUMBER_PATTERN = r"chuong-(\d+)"
SAFE_FILENAME_PATTERN = r'[\\/*?:"<>|]'

# HTML Templates
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

EPUB_CSS = (
    'body { font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; margin: 20px; } '
    "h1 { text-align: center; color: #ff6600; } "
    ".content { white-space: pre-wrap; }"
)
