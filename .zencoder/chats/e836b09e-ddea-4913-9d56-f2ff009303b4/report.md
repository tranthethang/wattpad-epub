# Report: Fix Excessive Line Spacing in EPUB

## What was implemented
- **Reduced Aggressive Text Processing**: Modified `src/utils.py`'s `process_text_for_line_breaks` to remove regex patterns that split sentences into separate paragraphs. This prevents sentences from being wrapped in individual `<p>` tags, which was the primary cause of excessive line spacing.
- **Simplified Line Break Normalization**: Updated the normalization logic to only turn block-level separators (single newlines) into double newlines for paragraph separation, while collapsing multiple spaces and redundant newlines.
- **Improved EPUB CSS**: Removed `white-space: pre-wrap` from `src/config.py`'s `EPUB_CSS` and added standard paragraph styling (`margin-bottom`, `text-indent`, `text-align: justify`) to ensure a professional reading experience without redundant line breaks.

## How the solution was tested
- **Reproduction Script**: Created a script (`repro_issue.py`) to test the processing of multi-sentence and multi-paragraph strings. The script confirmed that:
    - Sentences within a single paragraph now stay in the same paragraph (one `<p>` tag).
    - Original paragraph breaks (represented as newlines) are correctly preserved as separate paragraphs.
- **Manual Verification**: Inspected the HTML output of the processing functions before and after the fix to verify the structure changes.

## Biggest issues or challenges encountered
- **Balancing Extraction vs Formatting**: Ensuring that turning single newlines into double newlines (to create paragraphs) didn't accidentally split text that wasn't intended to be split. However, since BS4's `get_text(separator="\n")` is used, single newlines are generally reliable indicators of block-level separation in the source HTML.
- **Existing Downloads**: Downloaded HTML files with the old logic already contain extra `\n\n`. The updated `convert` command re-processes these files and normalizes the excessive newlines, fixing existing downloads during conversion.
