"""
Common utility functions for the project.
Includes filename cleaning, text formatting, and HTML content extraction.
"""

import re

from bs4 import BeautifulSoup
from slugify import slugify

from .config import DEFAULT_STORY_FILENAME, HTML_PARSER, MIN_TEXT_LENGTH


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
    """
    # Split text into paragraphs based on double newlines
    paragraphs = text.split("\n\n")
    # Wrap each paragraph in <p> tags
    return "".join(f"<p>{p.strip()}</p>" for p in paragraphs if p.strip())


def get_content_div(soup: BeautifulSoup) -> BeautifulSoup | None:
    """Find the div containing story content."""
    return soup.find("div", class_=re.compile(r"(truyen|content)"))


def extract_text_from_div(content_div: BeautifulSoup) -> str:
    """Extract and process text from a content div."""
    text = content_div.get_text(separator="\n", strip=True)
    return process_text_for_line_breaks(text)


def extract_images_from_div(content_div: BeautifulSoup) -> str | None:
    """Extract image tags from a content div as a fallback."""
    images = content_div.find_all("img")
    if not images:
        return None

    img_tags = []
    for img in images:
        img_src = img.get("data-url") or img.get("src")
        if img_src:
            img_tags.append(f'<img src="{img_src}" alt="Chapter Image" />')

    return "\n".join(img_tags) if img_tags else None


def extract_main_content(html: str) -> str | None:
    """Extract text or image content from HTML."""
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
