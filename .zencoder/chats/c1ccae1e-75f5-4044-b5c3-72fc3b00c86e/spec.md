# Technical Specification - Filter URLs in get-urls command

## Technical Context
- **Language**: Python
- **CLI Framework**: Typer
- **HTTP Client**: httpx
- **HTML Parsing**: BeautifulSoup4 (lxml)

## Implementation Approach
Modify the `get_urls` command in `src/main.py` to validate URLs before adding them to the list. A URL is considered valid if it starts with `http://` or `https://`.

1. Locate the loop that extracts `href` from `<a>` tags in `src/main.py`.
2. Ensure relative URLs starting with `/` are converted to absolute URLs using the `base_domain`.
3. Add a check to only append URLs that start with `http://` or `https://`.
4. Skip any other `href` values (e.g., `javascript:void(0)`, `#`, etc.).

## Source Code Structure Changes
- **Modified**: [./src/main.py](./src/main.py)

## Data model / API / interface changes
None. This is an internal logic improvement for the `get-urls` command.

## Verification Approach
1. Run `get-urls` with a sample API URL.
2. Verify that the output file (e.g., `urls.txt`) only contains valid HTTP/HTTPS URLs.
3. Manually check if any invalid strings (like `javascript:...`) were previously included and are now excluded.
