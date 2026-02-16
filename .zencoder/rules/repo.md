---
description: Repository Information Overview
alwaysApply: true
---

# wattpad-epub Information

## Summary
The `wattpad-epub` project is a Python-based CLI tool designed to download stories from Wattpad-like websites and convert them into EPUB format. It features chapter URL extraction from APIs, stealthy content scraping using Playwright to bypass protections, and automated EPUB generation.

## Structure
- **src/**: Main source code directory.
  - [**main.py**](./src/main.py): CLI entry point using `Typer` with commands for URL extraction, downloading, and conversion.
  - [**scraper.py**](./src/scraper.py): Asynchronous scraping logic using `Playwright` and `playwright-stealth`.
  - [**utils.py**](./src/utils.py): Utility functions for HTML cleaning and EPUB creation using `ebooklib`.
- **downloads/**: Default directory for downloaded HTML chapter files.
- **epub/**: Default directory for generated EPUB files.
- **requirements.txt**: List of Python dependencies.
- **urls.txt**: Default file for storing extracted chapter URLs.
- **cover.png**: Default cover image used for EPUB generation.

## Language & Runtime
**Language**: Python  
**Package Manager**: `pip`  
**Runtime**: Python 3.x with `playwright`

## Dependencies
**Main Dependencies**:
- `playwright` & `playwright-stealth`: Headless browser automation and bot detection evasion.
- `typer`: CLI framework.
- `rich`: Terminal formatting and progress bars.
- `ebooklib`: EPUB file generation.
- `beautifulsoup4` & `lxml`: HTML parsing and cleaning.
- `httpx`: Asynchronous HTTP client for API requests.
- `python-slugify`: Filename normalization.

## Build & Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium
```

## Usage & Operations

### 1. Extract Chapter URLs
```bash
python -m src.main get-urls "API_URL" PAGE_FROM PAGE_TO --output urls.txt
```

### 2. Download Chapters
```bash
python -m src.main download urls.txt --output downloads
```

### 3. Convert to EPUB
```bash
python -m src.main convert --title "Story Title" --author "Author Name" --cover cover.png
```

## Testing
No formal testing framework (e.g., pytest) is currently configured. Validation is performed manually via CLI output and generated files.
