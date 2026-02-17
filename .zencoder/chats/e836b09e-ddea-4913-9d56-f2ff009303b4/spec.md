# Technical Specification: Fix Excessive Line Spacing in EPUB

## Technical Context
- Language: Python
- Dependencies: `ebooklib`, `beautifulsoup4`, `lxml`
- Affected Modules: `src/utils.py`, `src/config.py`

## Implementation Approach
1. **Remove Aggressive Sentence Splitting**: The current `process_text_for_line_breaks` function in `src/utils.py` uses regular expressions to insert double newlines (`\n\n`) after every sentence ending with `.`, `!`, or `?`. This causes each sentence to be treated as a separate paragraph by `text_to_html_paragraphs`, leading to excessive spacing in the EPUB output.
2. **Normalize Paragraph Breaks**: Simplify the function to only normalize existing whitespace and ensure that block-level separations (extracted as `\n` by BeautifulSoup) are converted to double newlines (`\n\n`) for proper paragraph wrapping.
3. **Refine EPUB CSS**: Remove the redundant `white-space: pre-wrap` from the EPUB CSS in `src/config.py` since we are now using semantic `<p>` tags. Add standard paragraph styling (margin, indentation, justification) to improve readability.

## Source Code Structure Changes
- `src/utils.py`: Modify `process_text_for_line_breaks` to remove sentence splitting regex.
- `src/config.py`: Update `EPUB_CSS` to remove `pre-wrap` and add paragraph styles.

## Data Model / API / Interface Changes
- None.

## Verification Approach
- Use a reproduction script to compare original text and processed HTML output, ensuring sentences remain within the same paragraph.
- Manually run the `convert` command to verify the generated EPUB (if possible in the environment) or verify the logic through unit-test-like scripts.
