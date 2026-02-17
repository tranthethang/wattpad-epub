import os

import httpx
from ebooklib import epub
from slugify import slugify

from ..config import EPUB_CSS


def create_epub_book(title: str, author: str, cover_path: str = None):
    book = epub.EpubBook()
    book.set_identifier(slugify(title))
    book.set_title(title)
    book.set_language("vi")
    book.add_author(author)

    # Tạo CSS item dùng chung cho tất cả các chương
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
    if cover_path.startswith(("http://", "https://")):
        try:
            response = httpx.get(cover_path)
            response.raise_for_status()
            book.set_cover("cover.jpg", response.content)
        except Exception as e:
            print(f"Error downloading cover: {e}")
    elif os.path.exists(cover_path):
        book.set_cover("cover.jpg", open(cover_path, "rb").read())


def add_chapter_to_book(book, nav_css, title: str, content: str, index: int):
    chap_id = f"chap_{index:04d}"
    file_name = f"{chap_id}.xhtml"
    chapter = epub.EpubHtml(title=title, file_name=file_name, lang="vi", uid=chap_id)
    chapter.content = f'<h1>{title}</h1><div class="content">{content}</div>'
    chapter.add_item(nav_css)
    book.add_item(chapter)
    return chapter


def finalize_epub(book, output_path: str, chapters: list):
    # Tạo TOC (Table of Contents)
    book.toc = tuple([epub.Link(c.file_name, c.title, c.id) for c in chapters])
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav"] + chapters
    epub.write_epub(output_path, book, {})
