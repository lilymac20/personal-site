"""Turn content + templates + static files into a finished site in dist/.

GitHub Pages can only serve finished files, so Python runs here, at build time:
load the content, render every page with Jinja2, copy the static files next to them.
"""

import shutil
import sys
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

from site_builder.load import ContentError, load_content
from site_builder.models import Content

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Paths:
    """Where the build reads from and writes to. Tests point these at temp folders."""

    content: Path = PROJECT_ROOT / "content"
    templates: Path = PROJECT_ROOT / "templates"
    static: Path = PROJECT_ROOT / "static"
    out: Path = PROJECT_ROOT / "dist"


@dataclass(frozen=True)
class Page:
    """One HTML file to write: which template, where it goes, and what it's given."""

    template: str
    path: str  # where it lands inside dist/, e.g. "index.html" or "projects/x/index.html"
    context: dict[str, Any] = field(default_factory=dict)

    @property
    def root(self) -> str:
        """The relative way back to the site root from this page ("" or "../../").

        Every link in a template starts with `{{ root }}`, so links work whether the
        site lives at lilymac20.github.io/personal-site/, localhost:8001 or a custom
        domain, with no setting to change.
        """
        depth = len(Path(self.path).parts) - 1
        return "../" * depth


def make_environment(templates: Path) -> Environment:
    return Environment(
        loader=FileSystemLoader(templates),
        autoescape=select_autoescape(["html"]),
        # A typo like {{ nmae }} raises an error instead of quietly rendering nothing.
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def pages(content: Content) -> Iterator[Page]:
    """Every page on the site."""
    yield Page(
        "index.html",
        "index.html",
        {"site": content.site, "projects": content.projects},
    )


def check_images(content: Content, static: Path) -> None:
    missing = [path for path in content.images() if not (static / path).is_file()]
    if missing:
        raise ContentError(f"image(s) not found in static/: {', '.join(missing)}")


def build(paths: Paths = Paths()) -> list[Path]:
    """Build the whole site from scratch and return the HTML files written."""
    content = load_content(paths.content)
    check_images(content, paths.static)

    if paths.out.exists():
        shutil.rmtree(paths.out)
    shutil.copytree(paths.static, paths.out)

    env = make_environment(paths.templates)
    env.globals["year"] = date.today().year
    written: list[Path] = []
    for page in pages(content):
        html = env.get_template(page.template).render(root=page.root, **page.context)
        target = paths.out / page.path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html, encoding="utf-8")
        written.append(target)
    return written


def main() -> None:
    try:
        written = build()
    except ContentError as exc:
        # A content mistake gets one clear line, not a Python traceback.
        sys.exit(f"Build failed: {exc}")
    print(f"Built {len(written)} page(s) into {Paths().out}")
