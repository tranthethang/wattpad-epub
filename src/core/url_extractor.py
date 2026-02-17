from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import httpx
from bs4 import BeautifulSoup


def build_api_url(base_api_url: str, page: int) -> str:
    parsed_url = urlparse(base_api_url)
    query = parse_qs(parsed_url.query)
    query["page"] = [str(page)]
    new_query = urlencode(query, doseq=True)
    return urlunparse(parsed_url._replace(query=new_query))


def extract_urls_from_html(html_content: str, base_domain: str) -> list:
    soup = BeautifulSoup(html_content, "lxml")
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
    response = await client.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()
    return extract_urls_from_html(data.get("data", ""), base_domain)
