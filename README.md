# Wattpad EPUB Downloader

A command-line tool to fetch story URLs from an API and download chapter content as HTML files, which can then be used for EPUB conversion.

## Features

- **Extract URLs**: Automatically retrieve chapter links from a specified API endpoint across multiple pages.
- **Download Content**: Scrape chapter content using Playwright with stealth mode to avoid detection.
- **Progress Tracking**: Visual progress bars and status updates using Rich.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/thangtran/wattpad-epub.git
   cd wattpad-epub
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

## Usage

### 1. Extract Chapter URLs
Use the `get-urls` command to fetch chapter links from the story API.

```bash
python -m src.main get-urls "https://wattpad.com.vn/get/listchap/85995?page=1" 1 5 --output urls.txt
```

- `api_url`: The base API URL for listing chapters.
- `page_from`: Starting page number.
- `page_to`: Ending page number.
- `--output` / `-o`: (Optional) The file to save URLs to (default: `urls.txt`).

### 2. Download Chapters
Use the `download` command to save the content of each URL as an HTML file.

```bash
python -m src.main download urls.txt --output downloads
```

- `file_list`: Path to the text file containing URLs.
- `--output` / `-o`: (Optional) The directory to save HTML files in (default: `downloads`).

## Dependencies

- **Playwright**: Headless browser automation.
- **httpx**: Asynchronous HTTP client for API requests.
- **BeautifulSoup4**: HTML parsing and cleaning.
- **Typer**: Professional CLI creation.
- **Rich**: Terminal formatting and progress bars.
