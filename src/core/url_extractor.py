"""
Module for extracting chapter URLs from an API.
Provides functions to build API URLs and parse HTML content returned by the API.
"""

from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import httpx
from bs4 import BeautifulSoup

from ..config import HTML_PARSER, HTTP_TIMEOUT


def build_api_url(base_api_url: str, page: int) -> str:
    """
    Construct an API URL with pagination parameters.
    """
    parsed_url = urlparse(base_api_url)
    query = parse_qs(parsed_url.query)
    query["page"] = [str(page)]
    new_query = urlencode(query, doseq=True)
    return urlunparse(parsed_url._replace(query=new_query))


def extract_urls_from_html(html_content: str, base_domain: str) -> list:
    """
    Parse HTML content to find <a> tags and convert relative paths to absolute URLs.
    
    This function extracts links from the API's HTML data, ensuring each link
    is converted to a full absolute URL using the provided base domain.
    
    Args:
        html_content: The HTML string containing chapter links.
        base_domain: The story's root domain for relative URLs.
        
    Returns:
        A list of absolute chapter URLs.
    """
    soup = BeautifulSoup(html_content, HTML_PARSER)
    urls = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if isinstance(href, list):
            href = "".join(href)
        if href.startswith("/"):
            href = f"{base_domain}{href}"
        if href.startswith(("http://", "https://")):
            urls.append(href)
    return urls


async def fetch_page_urls(
    client: httpx.AsyncClient, url: str, base_domain: str
) -> list:
    """
    Perform an asynchronous request to the API to retrieve a list of URLs.
    """
    response = await client.get(url, timeout=HTTP_TIMEOUT)
    response.raise_for_status()
    data = response.json()
    return extract_urls_from_html(data.get("data", ""), base_domain)
