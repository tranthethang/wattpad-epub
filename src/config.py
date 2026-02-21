"""
Centralized configuration file for the wattpad-epub application.
Contains paths, browser settings, regex patterns, and HTML/CSS templates.
"""

import os

from dotenv import load_dotenv
from playwright.async_api import ViewportSize

load_dotenv()

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
# Browser headless mode
BROWSER_HEADLESS = True
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
CHAPTER_TITLE_LABEL = "Chương"
# Default image filename inside EPUB
EPUB_COVER_FILENAME = "cover.jpg"
# Directory for images inside the download folder
IMAGES_SUBDIR = "images"

# --- HTML & Parsing Configuration ---
# Default BeautifulSoup parser
HTML_PARSER = "lxml"
# Minimum text length to consider a chapter as text-based (vs image-based)
MIN_TEXT_LENGTH = 50
# CSS class name for chapter content
CONTENT_DIV_CLASS = "content"
# HTTP schemes for URL validation
HTTP_SCHEMES = ("http://", "https://")
# Maximum backoff wait time for exponential backoff (seconds)
MAX_BACKOFF_WAIT_TIME = 300
# Image tag identifier in content
IMAGE_TAG = "img"
# Image source attribute
IMG_SRC_ATTRIBUTE = "src"
# Image data-url attribute (fallback)
IMG_DATA_URL_ATTRIBUTE = "data-url"
# Image alt text default
IMAGE_ALT_TEXT = "Chapter Image"
# Invisible character patterns for content validation
INVISIBLE_CHARS_PATTERN = r"[\s\u200b\u200c\u200d\ufeff]+"

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

# --- File Naming & Indexing ---
# Length of file index prefix (e.g., "0001" in "0001-chapter.html")
FILE_INDEX_PREFIX_LENGTH = 4
# Length of UUID hex identifier for workflow IDs
WORKFLOW_ID_HEX_LENGTH = 12
# Timeout for closing browser/client (seconds)
CLOSE_TIMEOUT = 10

# --- Temporal Configuration ---
try:
    TEMPORAL_HOST = os.getenv("TEMPORAL_HOST", "localhost")
    TEMPORAL_PORT = int(os.getenv("TEMPORAL_PORT", "7233"))
except ValueError:
    raise ValueError("TEMPORAL_PORT must be a valid integer")

try:
    TEMPORAL_NAMESPACE = os.getenv("TEMPORAL_NAMESPACE", "default")
    TEMPORAL_TASK_QUEUE = os.getenv("TEMPORAL_TASK_QUEUE", "epub-queue")
except ValueError:
    raise ValueError("TEMPORAL configuration values are invalid")

# --- Override Directory Configuration from Environment ---
DEFAULT_DOWNLOAD_DIR = os.getenv("DOWNLOADS_DIR", DEFAULT_DOWNLOAD_DIR)
DEFAULT_EPUB_DIR = os.getenv("EPUB_OUTPUT_DIR", DEFAULT_EPUB_DIR)
DEFAULT_LOG_DIR = os.getenv("LOG_DIR", DEFAULT_LOG_DIR)
COVER_UPLOAD_DIR = os.getenv("COVER_UPLOAD_DIR", "cover")
ERROR_LOG_FILE = os.path.join(DEFAULT_LOG_DIR, "error.log")

# --- Override Download Settings from Environment ---
try:
    DEFAULT_CONCURRENCY = int(os.getenv("DEFAULT_CONCURRENCY", "4"))
    DOWNLOAD_MAX_RETRIES = int(os.getenv("DOWNLOAD_MAX_RETRIES", "10"))
except ValueError:
    raise ValueError("Download configuration values must be valid integers")

try:
    DOWNLOAD_RETRY_BACKOFF = float(os.getenv("DOWNLOAD_RETRY_BACKOFF", "2.0"))
    DOWNLOAD_DELAY = float(os.getenv("DOWNLOAD_DELAY", "2.0"))
except ValueError:
    raise ValueError("Download delay values must be valid floats")

# --- Image Download Retry Configuration ---
try:
    IMAGE_DOWNLOAD_MAX_RETRIES = int(os.getenv("IMAGE_DOWNLOAD_MAX_RETRIES", "3"))
    IMAGE_DOWNLOAD_INITIAL_BACKOFF = float(
        os.getenv("IMAGE_DOWNLOAD_INITIAL_BACKOFF", "1.0")
    )
except ValueError:
    raise ValueError("Image download configuration values must be valid numbers")
