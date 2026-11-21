from pathlib import Path

import pytest
from jinja2 import UndefinedError

from site_builder.build import PROJECT_ROOT, Page, Paths, build, make_environment


@pytest.fixture
def built(tmp_path: Path) -> Path:
    """Build the real site into a temporary folder and return that folder."""
    out = tmp_path / "dist"
    build(Paths(out=out))
    return out


def test_build_writes_the_home_page(built: Path) -> None:
    html = (built / "index.html").read_text()
    assert "Lily MacCormick" in html


def test_build_copies_static_files(built: Path) -> None:
    assert (built / "css" / "site.css").is_file()


def test_build_starts_from_scratch(tmp_path: Path) -> None:
    out = tmp_path / "dist"
    out.mkdir()
    (out / "old-page.html").write_text("left over from an earlier build")
    build(Paths(out=out))
    assert not (out / "old-page.html").exists()


@pytest.mark.parametrize(
    ("path", "root"),
    [
        ("index.html", ""),
        ("projects/index.html", "../"),
        ("projects/recipository/index.html", "../../"),
    ],
)
def test_root_climbs_back_to_the_site_root(path: str, root: str) -> None:
    assert Page("index.html", path).root == root


def test_links_are_relative(built: Path) -> None:
    """A link starting with "/" would break under lilymac20.github.io/personal-site/."""
    html = (built / "index.html").read_text()
    assert 'href="css/site.css"' in html
    assert 'href="/' not in html


def test_template_typos_fail_loudly() -> None:
    env = make_environment(PROJECT_ROOT / "templates")
    template = env.from_string("Hello {{ nmae }}")
    with pytest.raises(UndefinedError):
        template.render(name="Lily")
