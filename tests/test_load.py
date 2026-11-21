from pathlib import Path

import pytest

from site_builder.build import PROJECT_ROOT
from site_builder.load import ContentError, load_content

SITE = """
name = "Ada Lovelace"
role = "Engineer"
intro = "Hello."
email = "ada@example.com"
github = "https://github.com/ada"
linkedin = "https://linkedin.com/in/ada"
skills = ["Python"]
hobbies = []
"""

PROJECT = """
name = "Engine"
summary = "It computes."
tags = ["Brass"]
"""


def make_content(tmp_path: Path, site: str = SITE, **projects: str) -> Path:
    """Write a content/ folder: site.toml plus projects/<name>.toml for each keyword."""
    content = tmp_path / "content"
    (content / "projects").mkdir(parents=True)
    (content / "site.toml").write_text(site)
    for slug, text in projects.items():
        (content / "projects" / f"{slug}.toml").write_text(text)
    return content


def test_the_real_content_loads() -> None:
    content = load_content(PROJECT_ROOT / "content")
    assert content.site.name == "Lily MacCormick"
    assert [project.slug for project in content.projects] == ["recipository"]


def test_reads_every_field(tmp_path: Path) -> None:
    site = SITE + '\n[[experience]]\ndates = "1843"\ntitle = "Notes"\nsummary = "Wrote G."\n'
    content = load_content(make_content(tmp_path, site, engine=PROJECT))

    assert content.site.initials == "AL"
    assert content.site.photo is None
    assert content.site.experience[0].title == "Notes"
    project = content.projects[0]
    assert (project.slug, project.tags, project.featured, project.order) == (
        "engine",
        ("Brass",),
        False,
        100,
    )


def test_experience_summary_is_optional(tmp_path: Path) -> None:
    site = SITE + '\n[[experience]]\ndates = "1835"\ntitle = "Tutoring"\n'
    content = load_content(make_content(tmp_path, site))
    assert content.site.experience[0].summary is None


def test_featured_first_then_order_then_name(tmp_path: Path) -> None:
    content = load_content(
        make_content(
            tmp_path,
            zebra=PROJECT.replace("Engine", "Zebra") + "order = 1",
            apple=PROJECT.replace("Engine", "Apple") + "order = 1",
            star=PROJECT.replace("Engine", "Star") + "featured = true\norder = 9",
        )
    )
    assert [project.name for project in content.projects] == ["Star", "Apple", "Zebra"]


@pytest.mark.parametrize(
    ("site", "message"),
    [
        (SITE.replace('role = "Engineer"', ""), "site.toml: missing 'role'"),
        (SITE.replace('"Engineer"', '"  "'), "site.toml: 'role' is empty"),
        (SITE.replace('"Engineer"', "3"), "'role' must be text, got a whole number"),
        (SITE.replace('["Python"]', "[1]"), "skills[0] must be text"),
        (SITE + 'emial = "x"', "unknown key(s): emial"),
        (SITE + "[[experience]]\ndates = 1\n", "[[experience]] #1: 'dates' must be text"),
        ("name = ", "not valid TOML"),
    ],
)
def test_site_mistakes_name_the_file_and_key(tmp_path: Path, site: str, message: str) -> None:
    with pytest.raises(ContentError) as caught:
        load_content(make_content(tmp_path, site))
    assert message in str(caught.value)


def test_project_typos_are_caught(tmp_path: Path) -> None:
    with pytest.raises(ContentError) as caught:
        load_content(make_content(tmp_path, engine=PROJECT + 'sumary = "x"'))
    assert "projects/engine.toml: unknown key(s): sumary" in str(caught.value)


def test_true_is_not_a_number(tmp_path: Path) -> None:
    with pytest.raises(ContentError) as caught:
        load_content(make_content(tmp_path, engine=PROJECT + "order = true"))
    assert "'order' must be a whole number, got true or false" in str(caught.value)


def test_file_names_must_work_as_addresses(tmp_path: Path) -> None:
    with pytest.raises(ContentError) as caught:
        load_content(make_content(tmp_path, **{"My Project": PROJECT}))
    assert "lowercase letters, digits and dashes" in str(caught.value)
