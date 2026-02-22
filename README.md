# Wattpad EPUB Downloader

A CLI tool to download stories from Wattpad-like websites and convert them into EPUB format. It uses Playwright for stealthy scraping and `ebooklib` for EPUB generation.

## Features

- **Extract URLs**: Retrieve chapter links from API endpoints.
- **Stealth Scraping**: Download chapter content using Playwright with bot detection evasion. Automatically skips already downloaded chapters.
- **EPUB Conversion**: Automatically bundle downloaded HTML chapters into a clean EPUB file with metadata and cover art. Auto-generates filenames based on title and author.
- **Progress Tracking**: Visual progress bars and status updates using Rich.
- **Temporal Workflow Orchestration**: Run the complete EPUB generation pipeline (URL extraction → download → conversion) as a distributed workflow with automatic retry logic and validation.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/tranthethang/wattpad-epub.git
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

Example:
```bash
python -m src.main get-urls "https://wattpad.com.vn/get/listchap/xxxxx?page=1" 1 8 --output urls.txt
```

- **Shortcut**: `-o` for `--output`.

### 2. Download Chapters
Save chapter content as HTML files from the list of URLs. It detects and skips existing chapters in the output directory.

```bash
python -m src.main download urls.txt --output downloads --concurrency 4
```
- **Key Options**:
  - `-o`, `--output`: Directory to save HTML files (default: `downloads`).
  - `-c`, `--concurrency`: Number of concurrent download threads (default: `4`).

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

## Temporal Workflow Mode

Run the complete EPUB generation pipeline as a **distributed workflow** using Temporal. This enables automatic retry logic, validation, and monitoring of the entire process.

### Prerequisites

1. **Set up Temporal Server and UI**:
   Clone and start services from the [docker-shared-services](https://github.com/tranthethang/docker-shared-services) repository:
   ```bash
   git clone https://github.com/tranthethang/docker-shared-services.git
   cd docker-shared-services
   docker compose up -d --build
   ```
   This starts Temporal Server and Temporal-UI at `localhost:7233`

2. **Configure Environment** (optional):
   - `TEMPORAL_HOST`: Temporal server hostname (default: `localhost`)
   - `TEMPORAL_PORT`: Temporal server port (default: `7233`)
   - `TEMPORAL_NAMESPACE`: Temporal namespace (default: `default`)
   - `TEMPORAL_TASK_QUEUE`: Task queue name (default: `epub-queue`)
   - `APP_PORT`: API server port (default: `80` for standalone, `3000` for Docker Compose)

### Starting Services

Use Docker Compose to start both the API and Temporal worker:

```bash
docker compose up -d --build
```

This will start:
- **API Server**: FastAPI application for workflow submission and status checking
- **Temporal Worker**: Automatically processes EPUB generation workflows

The API will be accessible at `http://localhost:3000` (configured via `APP_PORT=3000` in `.env`).

### Submitting Workflows via API

#### Endpoint: Submit Workflow

```bash
curl -X POST http://localhost:3000/make \
  -F "api_url=https://wattpad.com.vn/get/listchap/xxxxx?page=1" \
  -F "page_from=1" \
  -F "page_to=8" \
  -F "title=Story Title" \
  -F "author=Author Name" \
  -F "concurrency=4" \
  -F "max_retries=10" \
  -F "cover_image=@cover.png"
```

**Parameters**:
- `api_url` (required): API endpoint to extract chapter URLs
- `page_from` (required): Starting page number
- `page_to` (required): Ending page number
- `title` (required): Story title
- `author` (required): Author name
- `concurrency` (optional): Number of concurrent downloads (default: `4`)
- `max_retries` (optional): Maximum download retry attempts (default: `10`)
- `cover_image` (optional): Cover image file upload

**Response**:
```json
{
  "workflow_id": "epub-a1b2c3d4e5f6",
  "status": "submitted",
  "message": "Workflow epub-a1b2c3d4e5f6 submitted successfully"
}
```

#### Endpoint: Check Workflow Status

```bash
curl http://localhost:3000/status/epub-a1b2c3d4e5f6
```

**Response**:
```json
{
  "workflow_id": "epub-a1b2c3d4e5f6",
  "status": "COMPLETED",
  "current_step": "completed",
  "result": "/path/to/generated/story.epub",
  "error": null
}
```

**Status Values**:
- `RUNNING`: Workflow is in progress
- `COMPLETED`: Workflow completed successfully
- `FAILED`: Workflow failed
- `NOT_FOUND`: Workflow ID not found

### Workflow Steps

The `EpubGenerationWorkflow` executes three activities in sequence with automatic retry:

1. **Extract URLs Activity**: Fetches chapter URLs from the API and saves them to a file.
2. **Download with Validation Activity**: Downloads chapters with validation and retry logic. If the number of downloaded files doesn't match expected URLs, it retries with exponential backoff.
3. **Convert Activity**: Converts downloaded HTML files to EPUB format with metadata and cover art.

All activities have automatic **exponential backoff retry policy**:
- Initial interval: 2 seconds
- Backoff coefficient: 2.0
- Maximum interval: 60 seconds
- Maximum attempts: 3

## Project Structure

- **src/**: Main source code.
  - `main.py`: CLI entry point with commands.
  - `api.py`: FastAPI REST endpoints for workflow submission and status checking.
  - **core/**: Core business logic.
    - `scraper_service.py`: Playwright scraping logic using stealth mode.
    - `epub_factory.py`: EPUB generation logic.
    - `url_extractor.py`: API URL extraction logic.
  - **commands/**: CLI command implementations.
  - **workflows/**: Temporal workflow definitions.
    - `epub_workflow.py`: Main EPUB generation workflow orchestration.
    - `activities.py`: Workflow activities (URL extraction, download, conversion).
  - `utils.py`: Text cleaning and paragraph conversion utilities.
- **workers/**: Temporal worker implementation.
  - `worker.py`: Starts a Temporal worker to process workflows.
- **downloads/**: Default directory for HTML chapter files.
- **epub/**: Default directory for generated EPUB files.
- **logs/**: Contains `error.log` for failed downloads.
- **urls.txt**: Default storage for extracted URLs.
- **cover.png**: Default cover image for EPUBs.

## Dependencies

- **Playwright & Playwright-Stealth**: Browser automation and bot detection evasion.
- **Typer & Rich**: CLI framework and terminal formatting.
- **EbookLib**: EPUB file generation.
- **BeautifulSoup4 & LXML**: HTML parsing and cleaning.
- **HTTPX**: Asynchronous HTTP client for API requests.
- **Python-Slugify**: Filename normalization.
- **Temporal Python SDK**: Distributed workflow orchestration.
- **FastAPI & Uvicorn**: REST API framework and server for workflow management.
