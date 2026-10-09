#!/usr/bin/env python3
"""A tiny web crawler example using only Python's standard library."""

from html.parser import HTMLParser
from urllib.parse import urljoin
from urllib.request import Request, urlopen
import argparse


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.links = []
        self._inside_title = False

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self._inside_title = True
            return

        if tag == "a":
            attrs_dict = dict(attrs)
            href = attrs_dict.get("href")
            if href:
                self.links.append(href)

    def handle_endtag(self, tag):
        if tag == "title":
            self._inside_title = False

    def handle_data(self, data):
        if self._inside_title:
            self.title += data.strip()


def fetch_page(url, timeout):
    request = Request(
        url,
        headers={"User-Agent": "SimplePythonCrawler/1.0"},
    )
    with urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        body = response.read()
        status = getattr(response, "status", None) or "local file"
        return status, response.url, body.decode(charset, errors="replace")


def main():
    parser = argparse.ArgumentParser(description="Fetch a page and list its links.")
    parser.add_argument("url", help="Page URL to crawl, for example: https://example.com")
    parser.add_argument("--limit", type=int, default=10, help="Maximum links to print")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout in seconds")
    args = parser.parse_args()

    status, final_url, html = fetch_page(args.url, args.timeout)

    page = PageParser()
    page.feed(html)

    print(f"URL: {final_url}")
    print(f"Status: {status}")
    print(f"Title: {page.title or '(no title found)'}")
    print(f"Size: {len(html)} characters")
    print("Links:")

    for index, link in enumerate(page.links[: args.limit], start=1):
        print(f"{index}. {urljoin(final_url, link)}")

    if not page.links:
        print("(no links found)")


if __name__ == "__main__":
    main()
