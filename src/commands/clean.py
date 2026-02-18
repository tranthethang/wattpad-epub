"""
Executes the 'clean' command to remove HTML files with empty content.
"""

import os
import re
from pathlib import Path

from bs4 import BeautifulSoup
from rich.console import Console

from ..config import HTML_PARSER

console = Console()


def is_empty_content(html_content: str) -> bool:
    """Check if content is empty, handling invisible characters."""
    cleaned = re.sub(r"[\s\u200b\u200c\u200d\ufeff]+", "", html_content)
    return len(cleaned) == 0


def process_file_cleaning(file_path: Path) -> bool:
    """
    Read a file and determine if it should be deleted based on content.
    
    This function parses the HTML file, finds the 'content' div, 
    and checks if it contains visible text or images. If it's effectively 
    empty, the file is deleted.
    
    Args:
        file_path: Path object to the target HTML file.
        
    Returns:
        True if the file was deleted, False otherwise.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        soup = BeautifulSoup(content, HTML_PARSER)
        content_div = soup.find("div", class_="content")

        if content_div:
            inner_html = content_div.decode_contents()
            if is_empty_content(inner_html):
                os.remove(file_path)
                return True
    except Exception as e:
        console.print(f"[red]Error processing {file_path.name}: {e}[/red]")
    return False


def run_clean(directory: str):
    """Scan directory and remove empty HTML files."""
    path = Path(directory)
    if not path.exists() or not path.is_dir():
        console.print(f"[red]Directory {directory} does not exist.[/red]")
        return

    html_files = list(path.glob("*.html"))
    if not html_files:
        console.print(f"[yellow]No .html files found in {directory}.[/yellow]")
        return

    console.print(f"Checking {len(html_files)} files in {directory}...")
    deleted_count = sum(1 for f in html_files if process_file_cleaning(f))

    console.print(f"[bold green]Finished! Deleted {deleted_count} files.[/bold green]")
