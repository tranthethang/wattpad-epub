# Wattpad EPUB Downloader

A CLI tool to download stories from Wattpad-like websites and convert them into EPUB format. It uses Playwright for stealthy scraping and `ebooklib` for EPUB generation.

## Features

- **Extract URLs**: Retrieve chapter links from API endpoints.
- **Stealth Scraping**: Download chapter content using Playwright with bot detection evasion. Automatically skips already downloaded chapters.
- **EPUB Conversion**: Automatically bundle downloaded HTML chapters into a clean EPUB file with metadata and cover art. Auto-generates filenames based on title and author.
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
Fetch chapter links from the story API and save them to a file.

```bash
python -m src.main get-urls "API_URL" PAGE_FROM PAGE_TO --output urls.txt
```
- **Shortcut**: `-o` for `--output`.

### 2. Download Chapters
Save chapter content as HTML files from the list of URLs. It detects and skips existing chapters in the output directory.

```bash
python -m src.main download urls.txt --output downloads
```
- **Shortcut**: `-o` for `--output`.

### 3. Convert to EPUB
Generate an EPUB file from the downloaded HTML chapters.

```bash
python -m src.main convert --title "Story Title" --author "Author Name" --cover cover.png
```
- **Key Options**:
  - `-i`, `--input`: Directory containing HTML files (default: `downloads`).
  - `-o`, `--output`: Output EPUB filename. If omitted, it defaults to `epub/Author_Title.epub`.
  - `-t`, `--title`: Story title (default: `Wattpad Story`).
  - `-a`, `--author`: Author name (default: `Unknown`).
  - `-c`, `--cover`: Path or URL to cover image (default: `cover.png`).

## Project Structure

- **src/**: Main source code.
  - `main.py`: CLI entry point with commands for URL extraction, downloading, and conversion.
  - `scraper.py`: Playwright scraping logic using stealth mode.
  - `utils.py`: HTML cleaning and EPUB creation utilities.
- **downloads/**: Default directory for HTML chapter files.
- **epub/**: Default directory for generated EPUB files.
- **logs/**: Contains `error.log` for failed downloads.
- **urls.txt**: Default storage for extracted URLs.

## Dependencies

- **Playwright & Playwright-Stealth**: Browser automation and bot detection evasion.
- **Typer & Rich**: CLI framework and terminal formatting.
- **EbookLib**: EPUB file generation.
- **BeautifulSoup4 & LXML**: HTML parsing and cleaning.
- **HTTPX**: Asynchronous HTTP client for API requests.
- **Python-Slugify**: Filename normalization.
