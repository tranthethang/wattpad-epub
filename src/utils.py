"""
Common utility functions for the project.
Includes filename cleaning, text formatting, and HTML content extraction.
"""

import os
import re
import unicodedata

from bs4 import BeautifulSoup, Tag

from .config import (DEFAULT_STORY_FILENAME, HTML_PARSER, HTTP_SCHEMES,
                     IMAGE_ALT_TEXT, IMAGE_TAG, IMG_DATA_URL_ATTRIBUTE,
                     IMG_SRC_ATTRIBUTE, INVISIBLE_CHARS_PATTERN,
                     MIN_TEXT_LENGTH)


def slugify(text: str) -> str:
    """
    Convert text to a URL-safe slug format.
    - Converts to lowercase
    - Replaces spaces with hyphens
    - Removes special characters
    - Normalizes unicode to ASCII
    """
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text).strip()
    text = re.sub(r"[-\s]+", "-", text)
    return text.lower()


def is_http_url(url: str | None) -> bool:
    """Check if a string is a valid HTTP(S) URL."""
    return bool(url and isinstance(url, str) and url.startswith(HTTP_SCHEMES))


def ensure_directory_exists(directory: str) -> None:
    """Create directory if it doesn't exist.

    Args:
        directory: Path to directory to create

    Raises:
        OSError: If directory creation fails
    """
    try:
        os.makedirs(directory, exist_ok=True)
    except OSError as e:
        raise OSError(f"Failed to create directory {directory}: {str(e)}") from e


def clean_filename(title: str) -> str:
    """
    Convert a story title to a safe filename slug.
    Example: "My Story" -> "my-story"
    """
    if not title:
        return DEFAULT_STORY_FILENAME
    return slugify(title)


def process_text_for_line_breaks(text: str) -> str:
    """
    Normalize line breaks and whitespace in text.
    1. Replace multiple spaces with a single space.
    2. Normalize multiple newlines into a single newline.
    3. Convert each single newline into double newlines for paragraph separation.
    """
    # Replace 2 or more spaces with 1 space
    text = re.sub(r" {2,}", " ", text)
    # First, normalize all newline sequences to a single newline
    text = re.sub(r"\n+", "\n", text)
    # Then, turn each single newline into two to clearly separate paragraphs
    text = re.sub(r"\n", "\n\n", text)
    return text.strip()


def text_to_html_paragraphs(text: str) -> str:
    """
    Convert plain text (with double newlines) into HTML <p> tags.
    Used for creating EPUB content.

    Args:
        text: Plain text with double newlines as paragraph separators

    Returns:
        HTML string with content wrapped in <p> tags
    """
    paragraphs = text.split("\n\n")
    return "".join(f"<p>{p.strip()}</p>" for p in paragraphs if p.strip())


def get_content_div(soup: BeautifulSoup) -> Tag | None:
    """Find the div containing story content.

    Args:
        soup: BeautifulSoup object

    Returns:
        Content div tag or None if not found
    """
    for div in soup.find_all("div"):
        classes = div.get("class") or []
        if any(cls in ("truyen", "content") for cls in classes):
            return div
    return None


def extract_text_from_div(content_div: Tag) -> str:
    """Extract and process text from a content div.

    Args:
        content_div: BeautifulSoup Tag containing content

    Returns:
        Processed text with normalized line breaks
    """
    text = content_div.get_text(separator="\n", strip=True)
    return process_text_for_line_breaks(text)


def extract_images_from_div(content_div: Tag) -> str | None:
    """Extract image tags from a content div as a fallback.

    Args:
        content_div: BeautifulSoup Tag containing images

    Returns:
        HTML string with img tags or None if no images found
    """
    images = content_div.find_all(IMAGE_TAG)
    if not images:
        return None

    img_tags = []
    for img in images:
        img_src = img.get(IMG_DATA_URL_ATTRIBUTE) or img.get(IMG_SRC_ATTRIBUTE)
        if img_src:
            img_tags.append(f'<img src="{img_src}" alt="{IMAGE_ALT_TEXT}" />')

    return "\n".join(img_tags) if img_tags else None


def extract_main_content(html: str) -> str | None:
    """
    Extract text or image content from HTML based on quality checks.

    This function finds the content container and extracts either text
    or images. If images exist and the text is too short, it prioritizes
    returning the images, which is common in comic/manga chapters.

    Args:
        html: The raw HTML content from a chapter page.

    Returns:
        Processed string content (text or image tags) or None if no content is found.
    """
    soup = BeautifulSoup(html, HTML_PARSER)
    content_div = get_content_div(soup)

    if not content_div:
        return None

    processed_text = extract_text_from_div(content_div)
    img_content = extract_images_from_div(content_div)

    # If images exist and text is too short, prioritize images
    if img_content and (not processed_text or len(processed_text) < MIN_TEXT_LENGTH):
        return img_content

    return processed_text if processed_text else None


def extract_chapter_title(html: str) -> str | None:
    """
    Extract and clean the chapter title from HTML content.
    1. Look for <h1>, then fallback to <title>.
    2. If a colon exists, take the part after it.
    3. Return the cleaned title string or None.
    """
    soup = BeautifulSoup(html, HTML_PARSER)
    # Check <h1> first (from our template), then <title>
    title_tag = soup.find("h1") or soup.find("title")
    if not title_tag:
        return None

    title_text = title_tag.get_text(strip=True)
    if ":" in title_text:
        # Split by last colon and take the second part (right-hand side)
        title_text = title_text.rsplit(":", 1)[-1].strip()

    return title_text
