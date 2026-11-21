import re
import shutil
from pathlib import Path

import pytest
from jinja2 import UndefinedError

from site_builder.build import PROJECT_ROOT, Page, Paths, build, make_environment, paragraphs
from site_builder.load import ContentError


@pytest.fixture
def built(tmp_path: Path) -> Path:
    """Build the real site into a temporary folder and return that folder."""
    out = tmp_path / "dist"
    build(Paths(out=out))
    return out


@pytest.fixture
def home(built: Path) -> str:
    return (built / "index.html").read_text()


def copy_content(tmp_path: Path) -> Path:
    """A copy of the real content/ folder that a test can change."""
    content = tmp_path / "content"
    shutil.copytree(PROJECT_ROOT / "content", content)
    return content


def test_build_copies_static_files(built: Path) -> None:
    assert (built / "css" / "site.css").is_file()


def test_every_file_the_css_points_at_exists(built: Path) -> None:
    css_file = built / "css" / "site.css"
    urls = re.findall(r"url\(\s*[\"']?([^\"')]+)[\"']?\s*\)", css_file.read_text())
    local = [url for url in urls if not url.startswith(("http", "data:", "#"))]
    assert local, "expected the CSS to load at least one local file (the fonts)"
    missing = [url for url in local if not (css_file.parent / url).resolve().is_file()]
    assert not missing, f"site.css points at missing files: {missing}"


def test_build_starts_from_scratch(tmp_path: Path) -> None:
    out = tmp_path / "dist"
    out.mkdir()
    (out / "old-page.html").write_text("left over from an earlier build")
    build(Paths(out=out))
    assert not (out / "old-page.html").exists()


def test_home_page_shows_who_and_how_to_reach(home: str) -> None:
    assert '<h1 class="name">Lily MacCormick</h1>' in home
    assert "Software Engineer" in home
    assert 'href="mailto:lily.maccormick@gmail.com"' in home
    assert 'href="https://www.linkedin.com/in/lily-maccormick/"' in home


def test_home_page_links_each_project(home: str) -> None:
    assert 'href="projects/recipository/"' in home
    assert "my favourite" in home


def test_no_photo_shows_initials(home: str) -> None:
    assert 'class="stamp__initials" aria-hidden="true">LM<' in home


def test_experience_section_shows_each_entry(home: str) -> None:
    assert "So far" in home
    assert '<span class="date-stamp">Jul 2021 – now</span>' in home
    assert "Senior Software Engineer · M&amp;T Bank" in home  # & escaped in HTML
    assert "Cornell University" in home


def test_experience_section_hidden_when_empty(tmp_path: Path) -> None:
    content = copy_content(tmp_path)
    site = (content / "site.toml").read_text()
    (content / "site.toml").write_text(site.split("[[experience]]")[0])
    build(Paths(content=content, out=tmp_path / "dist"))
    html = (tmp_path / "dist" / "index.html").read_text()
    assert "So far" not in html


def test_experience_summary_is_optional(home: str) -> None:
    # The Cornell entry has no summary, so its title isn't followed by an empty <p>.
    assert "<h3>B.A. Information Science and History · Cornell University</h3>\n" in home
    assert "<p></p>" not in home


def test_missing_image_stops_the_build(tmp_path: Path) -> None:
    content = copy_content(tmp_path)
    site = (content / "site.toml").read_text()
    # At the top: in TOML, a line after a [[table]] belongs to that table.
    (content / "site.toml").write_text('photo = "img/nope.jpg"\n' + site)
    with pytest.raises(ContentError, match="img/nope.jpg"):
        build(Paths(content=content, out=tmp_path / "dist"))


def test_text_is_escaped(tmp_path: Path) -> None:
    content = copy_content(tmp_path)
    site = (content / "site.toml").read_text()
    (content / "site.toml").write_text(site.replace('"Software Engineer"', '"<b>Engineer</b>"'))
    build(Paths(content=content, out=tmp_path / "dist"))
    html = (tmp_path / "dist" / "index.html").read_text()
    assert "&lt;b&gt;Engineer&lt;/b&gt;" in html


@pytest.fixture
def recipository(built: Path) -> str:
    return (built / "projects" / "recipository" / "index.html").read_text()


def test_each_project_gets_a_page(recipository: str) -> None:
    assert '<h1 class="project-title">Recipository</h1>' in recipository
    assert "<title>Recipository · Lily MacCormick</title>" in recipository
    assert 'href="https://recipository.fly.dev">Visit the site' in recipository
    assert "<dt>Hosting</dt><dd>Fly.io + Supabase</dd>" in recipository


def test_project_page_links_back_home(recipository: str) -> None:
    assert 'href="../../#projects">← All projects' in recipository
    assert 'href="../../css/site.css"' in recipository


def test_features_are_numbered_and_highlights_bold(recipository: str) -> None:
    assert '<span class="date-stamp">01</span>' in recipository
    assert '<span class="date-stamp">03</span>' in recipository
    assert "<strong>A job queue in Postgres.</strong> Uses FOR UPDATE" in recipository


def test_sections_without_content_are_left_out(recipository: str) -> None:
    # No code_url, hero, gallery or "learned" in recipository.toml yet.
    assert "Read the code" not in recipository
    assert 'class="browser"' not in recipository
    assert "More screenshots" not in recipository
    assert "What I learned" not in recipository


def test_previous_and_next_link_the_projects_in_order(tmp_path: Path) -> None:
    content = copy_content(tmp_path)
    (content / "projects" / "zine.toml").write_text(
        'name = "Zine"\nsummary = "A tiny zine."\ntags = []\norder = 2\n'
    )
    out = tmp_path / "dist"
    build(Paths(content=content, out=out))
    first = (out / "projects" / "recipository" / "index.html").read_text()
    second = (out / "projects" / "zine" / "index.html").read_text()
    assert 'href="../../projects/zine/">Zine →' in first
    assert 'href="../../projects/recipository/">← Recipository' in second


def test_paragraphs_split_on_blank_lines() -> None:
    text = "\nOne line.\n\n  Two.\nStill two.\n\n\n"
    assert paragraphs(text) == ["One line.", "Two.\nStill two."]


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


def test_links_are_relative(home: str) -> None:
    """A link starting with "/" would break under lilymac20.github.io/personal-site/."""
    assert 'href="css/site.css"' in home
    assert 'href="/' not in home
    assert 'src="/' not in home


def test_template_typos_fail_loudly() -> None:
    env = make_environment(PROJECT_ROOT / "templates")
    template = env.from_string("Hello {{ nmae }}")
    with pytest.raises(UndefinedError):
        template.render(name="Lily")
