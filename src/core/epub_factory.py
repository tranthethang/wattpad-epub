"""
Module for creating and structuring EPUB files.
Uses ebooklib to build book content, including metadata, chapters, TOC, and styling.
"""

import logging
import os

import httpx
from bs4 import BeautifulSoup
from ebooklib import epub
from python_slugify import slugify

from ..config import (CHAPTER_ID_PREFIX, CONTENT_DIV_CLASS, DEFAULT_LANGUAGE,
                      EPUB_COVER_FILENAME, EPUB_CSS, HTML_PARSER, HTTP_TIMEOUT,
                      IMAGE_TAG, IMG_SRC_ATTRIBUTE, XHTML_EXTENSION)
from ..utils import is_http_url

logger = logging.getLogger(__name__)


def create_epub_book(title: str, author: str, cover_path: str | None = None):
    """
    Initialize an EPUB book object with basic information.

    This function sets metadata (title, author, language, unique identifier)
    and initializes CSS styling for navigation and content.

    Args:
        title: Title of the story.
        author: Author of the story.
        cover_path: Optional path to a local or remote cover image.

    Returns:
        A tuple of (book_object, navigation_css_object).
    """
    book = epub.EpubBook()
    book.set_identifier(slugify(title))
    book.set_title(title)
    book.set_language(DEFAULT_LANGUAGE)
    book.add_author(author)

    nav_css = epub.EpubItem(
        uid="style_nav",
        file_name="style/nav.css",
        media_type="text/css",
        content=EPUB_CSS,
    )
    book.add_item(nav_css)

    if cover_path:
        add_cover(book, cover_path)

    return book, nav_css


def add_cover(book, cover_path: str):
    """
    Add a cover image to the book.
    """
    if is_http_url(cover_path):
        try:
            response = httpx.get(cover_path, timeout=HTTP_TIMEOUT)
            response.raise_for_status()
            book.set_cover(EPUB_COVER_FILENAME, response.content)
        except Exception as e:
            logger.error(f"Error downloading cover: {e}")
    elif os.path.exists(cover_path):
        try:
            with open(cover_path, "rb") as f:
                book.set_cover(EPUB_COVER_FILENAME, f.read())
        except OSError as e:
            logger.error(f"Error reading cover file {cover_path}: {e}")


def get_image_media_type(ext: str) -> str:
    """Determine image media type from extension.

    Args:
        ext: File extension (e.g., 'jpg', 'png')

    Returns:
        MIME type string for the image format
    """
    mapping = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp",
    }
    return mapping.get(ext, "application/octet-stream")


def _process_single_image(book, img, base_dir: str) -> None:
    """Embed a single image from soup if valid and exists.

    Args:
        book: EpubBook instance
        img: BeautifulSoup image tag
        base_dir: Base directory for resolving relative paths
    """
    src = img.get(IMG_SRC_ATTRIBUTE)
    if not src or is_http_url(src):
        return

    local_img_path = os.path.normpath(os.path.join(base_dir, src))
    if not os.path.exists(local_img_path):
        return

    if any(item.file_name == src for item in book.get_items_of_type(epub.EpubItem)):
        return

    with open(local_img_path, "rb") as f:
        img_data = f.read()

    ext = src.split(".")[-1].lower()
    epub_img = epub.EpubItem(
        uid=f"img_{slugify(src)}",
        file_name=src,
        media_type=get_image_media_type(ext),
        content=img_data,
    )
    book.add_item(epub_img)


def _embed_local_images(book, soup, base_dir: str):
    """
    Internal helper to embed local images into the EPUB book.

    Args:
        book: EpubBook instance
        soup: BeautifulSoup object with content
        base_dir: Base directory for resolving relative image paths

    Returns:
        Updated soup object
    """
    images = soup.find_all(IMAGE_TAG)
    for img in images:
        _process_single_image(book, img, base_dir)
    return soup


def add_chapter_to_book(
    book,
    nav_css,
    title: str,
    content: str,
    index: int,
    base_dir: str | None = None,
    content_class: str = CONTENT_DIV_CLASS,
):
    """
    Create a new chapter and add it to the book.

    This function generates a chapter file inside the EPUB structure,
    embeds any referenced local images from the chapter HTML, and
    sets its title and content.

    Args:
        book: The EpubBook object.
        nav_css: The navigation style item.
        title: Title of the chapter.
        content: The cleaned HTML content of the chapter.
        index: Sorting index for filenames and IDs.
        base_dir: Directory containing downloaded chapter files (used for image resolution).
        content_class: CSS class name for content div.

    Returns:
        The newly created chapter object.
    """
    chap_id = f"{CHAPTER_ID_PREFIX}{index:04d}"
    file_name = f"{chap_id}{XHTML_EXTENSION}"

    if base_dir and f"<{IMAGE_TAG} " in content:
        soup = BeautifulSoup(content, HTML_PARSER)
        soup = _embed_local_images(book, soup, base_dir)
        if soup.body:
            content = "".join([str(c) for c in soup.body.contents]).strip()

    chapter = epub.EpubHtml(
        title=title, file_name=file_name, lang=DEFAULT_LANGUAGE, uid=chap_id
    )
    chapter.content = f'<h1>{title}</h1><div class="{content_class}">{content}</div>'
    chapter.add_item(nav_css)
    book.add_item(chapter)
    return chapter


def finalize_epub(book, output_path: str, chapters: list):
    """
    Finalize book structure and write to file.
    """
    book.toc = tuple([epub.Link(c.file_name, c.title, c.id) for c in chapters])
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav"] + chapters
    epub.write_epub(output_path, book, {})
