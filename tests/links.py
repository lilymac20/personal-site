"""Find every link and image in a built site and report the ones that go nowhere."""

from collections.abc import Iterator
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


class LinkCollector(HTMLParser):
    """Collects href/src values. HTMLParser calls handle_starttag for every opening tag."""

    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name in ("href", "src") and value:
                self.links.append(value)


def links_in(html: str) -> list[str]:
    collector = LinkCollector()
    collector.feed(html)
    return collector.links


def is_external(link: str) -> bool:
    return urlsplit(link).scheme in ("http", "https", "mailto", "tel", "data")


def target_of(page: Path, link: str) -> Path | None:
    """The file an internal link opens, or None for a same-page link like "#top"."""
    path = unquote(urlsplit(link).path)  # drops "#fragment" and "?query"
    if not path:
        return None
    target = (page.parent / path).resolve()
    # A folder link like "projects/x/" serves that folder's index.html.
    return target / "index.html" if path.endswith("/") or target.is_dir() else target


def broken_links(site: Path) -> Iterator[str]:
    """Yield "page: link" for every internal link or image whose file doesn't exist."""
    for page in sorted(site.rglob("*.html")):
        for link in links_in(page.read_text(encoding="utf-8")):
            if is_external(link):
                continue
            target = target_of(page, link)
            if target is None:
                continue
            if site.resolve() not in target.parents or not target.is_file():
                yield f"{page.relative_to(site)}: {link}"
