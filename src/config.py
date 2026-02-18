"""
Centralized configuration file for the wattpad-epub application.
Contains paths, browser settings, regex patterns, and HTML/CSS templates.
"""

import os

from playwright.async_api import ViewportSize

# --- Directory Configuration ---
# Default directory for downloaded HTML files
DEFAULT_DOWNLOAD_DIR = "downloads"
# Default directory for generated EPUB files
DEFAULT_EPUB_DIR = "epub"
# Application log directory
DEFAULT_LOG_DIR = "logs"
# Error log file path
ERROR_LOG_FILE = os.path.join(DEFAULT_LOG_DIR, "error.log")

# --- File Configuration ---
# Default file containing the list of URLs to download
DEFAULT_URLS_FILE = "urls.txt"
# Default cover image for the EPUB
DEFAULT_COVER_IMAGE = "cover.png"

# --- Browser Configuration (Playwright) ---
# User Agent to mimic a real browser and avoid bot detection
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
# Simulated browser viewport size
VIEWPORT: ViewportSize = {"width": 1280, "height": 720}
# Maximum timeout for browser actions (ms)
BROWSER_TIMEOUT = 60000
# Number of times to scroll for lazy loading
SCRAPING_SCROLL_COUNT = 3
# Delay between scrolls (seconds)
SCRAPING_SCROLL_DELAY = 1.5
# Delay between chapter downloads (seconds)
DOWNLOAD_DELAY = 1.0
# Default concurrency for downloading
DEFAULT_CONCURRENCY = 4

# --- API & Network Configuration ---
# Timeout for HTTP requests (seconds)
HTTP_TIMEOUT = 30.0
# Maximum concurrent requests to the API
API_SEMAPHORE_LIMIT = 5
# Supported image extensions
SUPPORTED_IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "gif", "webp"]

# --- Regex Patterns ---
# Identifies chapters in URLs or filenames
CHAPTER_PATTERN = r"(chuong-\d+)"
# Extracts chapter numbers from strings
CHAPTER_NUMBER_PATTERN = r"chuong-(\d+)"
# Invalid characters for filenames
SAFE_FILENAME_PATTERN = r'[\\/*?:"<>|]'

# --- EPUB & Content Configuration ---
# Default language for the EPUB
DEFAULT_LANGUAGE = "vi"
# Default title if none is provided
DEFAULT_STORY_TITLE = "Wattpad Story"
# Default author if none is provided
DEFAULT_STORY_AUTHOR = "Unknown"
# Default filename for untitled stories
DEFAULT_STORY_FILENAME = "untitled_story"
# Prefix for chapter IDs in EPUB
CHAPTER_ID_PREFIX = "chap_"
# Extension for EPUB internal XHTML files
XHTML_EXTENSION = ".xhtml"
# Label for chapter titles
CHAPTER_TITLE_LABEL = "Chapter"
# Default image filename inside EPUB
EPUB_COVER_FILENAME = "cover.jpg"
# Directory for images inside the download folder
IMAGES_SUBDIR = "images"

# --- HTML & Parsing Configuration ---
# Default BeautifulSoup parser
HTML_PARSER = "lxml"
# Minimum text length to consider a chapter as text-based (vs image-based)
MIN_TEXT_LENGTH = 50

# Template for intermediate HTML files
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

# CSS styling for story content inside the EPUB
EPUB_CSS = (
    'body { font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; margin: 20px; } '
    "h1 { text-align: center; color: #ff6600; } "
    "p { margin-bottom: 0.8em; text-indent: 1em; text-align: justify; }"
)
