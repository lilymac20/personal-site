from pathlib import Path

from site_builder.build import Paths, build
from tests.links import broken_links, links_in, target_of


def test_no_broken_links_anywhere_on_the_site(tmp_path: Path) -> None:
    out = tmp_path / "dist"
    build(Paths(out=out))
    assert list(broken_links(out)) == []


def test_links_in_finds_hrefs_and_srcs() -> None:
    html = '<a href="a/">x</a><img src="b.png" alt=""><link rel="stylesheet" href="c.css">'
    assert links_in(html) == ["a/", "b.png", "c.css"]


def test_folder_links_open_index_html(tmp_path: Path) -> None:
    page = tmp_path / "projects" / "x" / "index.html"
    assert target_of(page, "../../") == (tmp_path / "index.html").resolve()
    assert target_of(page, "../../#projects") == (tmp_path / "index.html").resolve()
    assert target_of(page, "#top") is None


def test_the_checker_catches_a_broken_link(tmp_path: Path) -> None:
    (tmp_path / "index.html").write_text('<a href="missing/">x</a><img src="gone.png" alt="">')
    assert list(broken_links(tmp_path)) == ["index.html: missing/", "index.html: gone.png"]


def test_links_may_not_escape_the_site(tmp_path: Path) -> None:
    site = tmp_path / "site"
    site.mkdir()
    (tmp_path / "secret.html").write_text("outside the site")
    (site / "index.html").write_text('<a href="../secret.html">x</a>')
    assert list(broken_links(site)) == ["index.html: ../secret.html"]
