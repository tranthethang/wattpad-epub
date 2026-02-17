# Report - Filter URLs in get-urls command

## What was implemented
Modified the `get_urls` command in `src/main.py` to ensure that only absolute URLs starting with `http://` or `https://` are saved to the output file. Relative URLs (starting with `/`) are converted to absolute URLs before this check. Any other non-URL strings (like `javascript:...`) are now excluded.

## How the solution was tested
1. Ran the `get-urls` command using a sample API URL:
   ```bash
   python -m src.main get-urls "https://wattpad.com.vn/get/listchap/85995?page=1" 1 1 --output test_urls.txt
   ```
2. Inspected `test_urls.txt` and verified that all 100 entries were valid absolute `https://` URLs.

## Biggest issues or challenges encountered
None. The task was straightforward and the implementation followed the existing patterns in the codebase.
