import re

from bs4 import BeautifulSoup
from slugify import slugify


def clean_filename(title: str) -> str:
    if not title:
        return "untitled_story"
    return slugify(title)


def process_text_for_line_breaks(text: str) -> str:
    # Normalize multiple spaces to single space
    text = re.sub(r" {2,}", " ", text)
    # Ensure paragraphs are separated by exactly two newlines
    # First, normalize all newlines to single newlines
    text = re.sub(r"\n+", "\n", text)
    # Then, turn every single newline into double newlines for paragraph separation
    text = re.sub(r"\n", "\n\n", text)
    return text.strip()


def text_to_html_paragraphs(text: str) -> str:
    """Chuyển đổi text có xuống dòng \n\n thành các thẻ <p> cho EPUB."""
    paragraphs = text.split("\n\n")
    return "".join(f"<p>{p.strip()}</p>" for p in paragraphs if p.strip())


def extract_main_content(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    # Tìm kiếm cả class 'truyen' (web) và 'content' (file local)
    content_div = soup.find("div", class_=re.compile(r"(truyen|content)"))

    if not content_div:
        return None

    text = content_div.get_text(separator="\n", strip=True)
    return process_text_for_line_breaks(text)
