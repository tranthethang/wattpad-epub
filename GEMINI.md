---
description: Repository Information Overview
alwaysApply: true
---

# wattpad-epub Information

## Summary
The `wattpad-epub` project is a Python-based CLI tool designed to download stories from Wattpad-like websites and convert them into EPUB format. It features chapter URL extraction from APIs, stealthy content scraping using Playwright to bypass protections, automated EPUB generation, and content cleaning utilities.

## Structure
- **src/**: Main source code directory.
  - [**main.py**](./src/main.py): CLI entry point using `Typer` with commands for URL extraction, downloading, cleaning, and conversion.
  - [**config.py**](./src/config.py): Centralized configuration for directories, browser settings, regex patterns, and HTML/CSS templates.
  - **core/**: Core business logic.
    - [**scraper_service.py**](./src/core/scraper_service.py): Playwright scraping logic using stealth mode and lazy-loading handling.
    - [**epub_factory.py**](./src/core/epub_factory.py): EPUB generation logic using `ebooklib`.
    - [**url_extractor.py**](./src/core/url_extractor.py): API-based chapter URL extraction.
  - **commands/**: CLI command implementations (`download`, `get_urls`, `convert`, `clean`).
  - [**utils.py**](./src/utils.py): Utility functions for HTML cleaning and text processing.
- **bin/**: Shell scripts for project maintenance.
  - [**format.sh**](./bin/format.sh): Formats code using `black` and `isort`.
  - [**test.sh**](./bin/test.sh): Script for running tests (currently references `pytest`).
- **downloads/**: Default directory for downloaded HTML chapter files.
- **epub/**: Default directory for generated EPUB files.
- **logs/**: Application logs, including [**error.log**](./logs/error.log) for failed downloads.
- **cover/**: Directory for story cover images.
- **requirements.txt**: List of Python dependencies.

## Language & Runtime
**Language**: Python  
**Package Manager**: `pip`  
**Runtime**: Python 3.x with `playwright`

## Dependencies
**Main Dependencies**:
- `playwright` & `playwright-stealth`: Headless browser automation and bot detection evasion.
- `typer` & `rich`: CLI framework and terminal formatting with progress tracking.
- `ebooklib`: EPUB file generation.
- `beautifulsoup4` & `lxml`: HTML parsing and cleaning.
- `httpx`: Asynchronous HTTP client for API requests.
- `python-slugify`: Filename normalization.
- `black` & `isort`: Code formatting and import sorting.

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
python -m src.main download urls.txt --output downloads --concurrency 4
```

### 3. Clean Empty Chapters
```bash
# Removes HTML files with empty content blocks
python -m src.main clean downloads
```

### 4. Convert to EPUB
```bash
python -m src.main convert --title "Story Title" --author "Author Name" --cover cover.png
```
- **Key Options**:
  - `-i`, `--input`: Directory containing HTML files (default: `downloads`).
  - `-o`, `--output`: Output EPUB filename (default: `epub/Author_Title.epub`).
  - `-t`, `--title`: Story title.
  - `-a`, `--author`: Author name.
  - `-c`, `--cover`: Path to cover image.

### 5. Code Formatting
```bash
./bin/format.sh
```

## Testing
A [**test.sh**](./bin/test.sh) script exists but formal tests in a `tests/` directory were not found in the current source. Validation is primarily performed via manual CLI output and generated artifacts.

## Coding Standards
- **Function Atomicity**: Break down processing into multiple small functions. Each function must handle only a single atomic logic that cannot be further subdivided.
- **File Constraints**: Maximum of **200 lines** per file, including whitespace and comments.
- **Language**: All comments and text within the source code (variable names, docstrings, log messages) must be in **English**.
