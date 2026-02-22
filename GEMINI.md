---
description: Repository Information Overview
alwaysApply: true
---

# wattpad-epub Information

## Summary
The `wattpad-epub` project is a Python-based EPUB generation platform with dual interfaces: a **CLI tool** for direct story downloading and a **FastAPI REST API** backed by **Temporal workflows** for distributed, fault-tolerant EPUB generation. It extracts chapter URLs from APIs, uses Playwright with stealth mode for content scraping, and automatically converts chapters to EPUB format with support for cover images and metadata.

## Structure
- **src/**: Main source code directory.
  - [**main.py**](./src/main.py): CLI entry point using `Typer` with commands (`get-urls`, `download`, `convert`, `clean`).
  - [**api.py**](./src/api.py): FastAPI application with endpoints for workflow submission (`POST /make`) and status checking (`GET /status/{workflow_id}`).
  - [**api_helpers.py**](./src/api_helpers.py): Temporal client utilities, response models, and workflow input builders.
  - [**config.py**](./src/config.py): Centralized configuration for directories, browser settings, Temporal server details, and templates.
  - **core/**: Core business logic.
    - [**scraper_service.py**](./src/core/scraper_service.py): Playwright automation with stealth mode and lazy-loading.
    - [**epub_factory.py**](./src/core/epub_factory.py): EPUB generation using `ebooklib`.
    - [**url_extractor.py**](./src/core/url_extractor.py): API-based chapter URL extraction.
  - **commands/**: CLI command implementations.
  - **workflows/**: Temporal workflow definitions.
    - [**epub_workflow.py**](./src/workflows/epub_workflow.py): Main `EpubGenerationWorkflow` orchestrating URL extraction, download, and conversion activities.
    - [**activities.py**](./src/workflows/activities.py): Three Temporal activities with retry logic and validation.
    - [**models.py**](./src/workflows/models.py): Workflow and activity input/output data models.
    - [**utils.py**](./src/workflows/utils.py): Workflow utility functions and validation.
  - [**utils.py**](./src/utils.py): Text processing and HTML cleaning utilities.
- **workers/**: Temporal worker implementation.
  - [**worker.py**](./workers/worker.py): Standalone Temporal worker connecting to task queue and processing workflows.
- **bin/**: Shell scripts for maintenance and operations.
- **Dockerfile**: Multi-stage Docker build for FastAPI app with Playwright dependencies.
- **docker-compose.yml**: Services for API app and worker with shared volumes and Temporal networking.

## Language & Runtime
**Language**: Python 3.10  
**Package Manager**: `pip`  
**Runtime**: FastAPI + Uvicorn server, Temporal worker, Playwright browser automation

## Dependencies
**Core Dependencies**:
- `fastapi>=0.104.0` & `uvicorn>=0.24.0`: REST API framework and ASGI server.
- `temporalio>=1.4.0`: Temporal Python SDK for workflow orchestration.
- `pydantic>=2.0.0`: Data validation and API response models.
- `playwright` & `playwright-stealth`: Browser automation and bot detection evasion.
- `ebooklib`: EPUB file generation.
- `typer` & `rich`: CLI framework and terminal formatting.
- `beautifulsoup4` & `lxml`: HTML parsing and cleaning.
- `httpx`: Asynchronous HTTP client.
- `python-slugify`: Filename normalization.
- `python-dotenv>=1.0.0`: Environment variable loading.

**Development**:
- `black` & `isort`: Code formatting and import sorting.

## Build & Installation
```bash
pip install -r requirements.txt
playwright install chromium
```

## Docker
**Dockerfile**: Multi-stage build (Python 3.10-slim base)
- Stage 1: Installs dependencies to `/install`
- Stage 2: Runtime with Playwright system dependencies and non-root user `agent`
- Default command: `uvicorn src.api:app --host 0.0.0.0 --port 80 --reload`

**docker-compose.yml**:
- **app**: FastAPI service on port 80 (configurable via `APP_PORT`)
- **worker**: Temporal worker service (depends on app)
- **Environment**: Connects to external `dev_tools` network; volumes for `cover/`, `downloads/`, `epub/`, `logs/`
- **Temporal**: Configured via env vars (`TEMPORAL_HOST`, `TEMPORAL_PORT`, `TEMPORAL_NAMESPACE`, `TEMPORAL_TASK_QUEUE`)

## Usage & Operations

### CLI Mode (Standalone)

```bash
# 1. Extract URLs
python -m src.main get-urls "API_URL" PAGE_FROM PAGE_TO --output urls.txt

# 2. Download chapters
python -m src.main download urls.txt --output downloads --concurrency 4

# 3. Clean empty chapters
python -m src.main clean downloads

# 4. Convert to EPUB
python -m src.main convert --title "Story Title" --author "Author Name" --cover cover.png
```

### API + Temporal Workflow Mode

**Start API server**:
```bash
uvicorn src.api:app --host 0.0.0.0 --port 80 --reload
```

**Start Temporal worker** (in separate terminal):
```bash
python workers/worker.py
```

**Submit workflow via API**:
```bash
curl -X POST http://localhost/make \
  -F "api_url=https://api.example.com/chapters" \
  -F "page_from=1" \
  -F "page_to=8" \
  -F "title=Story Title" \
  -F "author=Author Name" \
  -F "concurrency=4" \
  -F "max_retries=10" \
  -F "cover_image=@cover.png"
```

**Check workflow status**:
```bash
curl http://localhost/status/epub-<workflow_id>
```

**Docker Compose** (includes Temporal networking):
```bash
docker-compose up
```

## Main Entry Points
- **CLI**: `src.main:app` (Typer application)
- **API**: `src.api:app` (FastAPI application, port 80)
- **Worker**: `workers.worker:run_worker()` (Temporal worker)

## Workflow Architecture
The `EpubGenerationWorkflow` executes three Temporal activities with exponential backoff retry (2s initial, 2.0x coefficient, 60s max, 3 max attempts):
1. **extract_urls_activity**: Fetches chapter URLs from API
2. **download_with_validation_activity**: Downloads with fallback retry if file count mismatches expected URLs
3. **convert_activity**: Converts HTML to EPUB with metadata and cover

## Coding Standards
- **Function Atomicity**: Each function handles single atomic logic
- **File Constraints**: Maximum **200 lines** per file
- **Language**: English for all code, comments, and docstrings
