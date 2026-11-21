"""Turn templates + static files into a finished site in dist/.

GitHub Pages can only serve finished files, so Python runs here, at build time:
render every page with Jinja2, copy the static files next to them, done.
"""

import shutil
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Paths:
    """Where the build reads from and writes to. Tests point these at temp folders."""

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
        site lives at lilymac20.github.io/personal-site/, localhost:8000 or a custom
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


def pages() -> Iterator[Page]:
    """Every page on the site. Step 2 fills this from the content files."""
    yield Page("index.html", "index.html", {"name": "Lily MacCormick"})


def build(paths: Paths = Paths()) -> list[Path]:
    """Build the whole site from scratch and return the HTML files written."""
    if paths.out.exists():
        shutil.rmtree(paths.out)
    shutil.copytree(paths.static, paths.out)

    env = make_environment(paths.templates)
    written: list[Path] = []
    for page in pages():
        html = env.get_template(page.template).render(root=page.root, **page.context)
        target = paths.out / page.path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html, encoding="utf-8")
        written.append(target)
    return written


def main() -> None:
    written = build()
    print(f"Built {len(written)} page(s) into {Paths().out}")
