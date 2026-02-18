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


def extract_main_content(html: str) -> str:
    """
    Extract text or image content from HTML using BeautifulSoup.
    Looks for div tags with 'truyen' or 'content' classes.
    """
    soup = BeautifulSoup(html, HTML_PARSER)
    # Find the div containing story content (supports web UI and local files)
    content_div = soup.find("div", class_=re.compile(r"(truyen|content)"))

    if not content_div:
        return None

    # Get all inner text, separating child tags with newlines
    text = content_div.get_text(separator="\n", strip=True)
    processed_text = process_text_for_line_breaks(text)

    # Check for images (fallback for image-based chapters)
    images = content_div.find_all("img")

    # If images exist and text is very short/empty, prioritize images
    if images and (not processed_text or len(processed_text) < MIN_TEXT_LENGTH):
        img_tags = []
        for img in images:
            # Prioritize data-url (for lazy loading), then src
            img_src = img.get("data-url") or img.get("src")
            if img_src:
                # Return img tag for scraper_service to handle later
                img_tags.append(f'<img src="{img_src}" alt="Chapter Image" />')

        if img_tags:
            return "\n".join(img_tags)

    # If actual text is found and not overridden by images
    if processed_text:
        return processed_text

    return None
