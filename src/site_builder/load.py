"""Read the TOML files in content/ into the dataclasses in models.py.

tomllib (built into Python 3.11+) turns TOML into plain dicts of Any. `Table` checks
each value's type as it's read and remembers which keys were used, so a typo like
"sumary" is reported instead of silently ignored.
"""

import re
import tomllib
from pathlib import Path
from typing import Any

from site_builder.models import Content, Job, Project, Site

SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")

_TYPE_NAMES: dict[type, str] = {
    str: "text",
    int: "a whole number",
    bool: "true or false",
    list: "a list",
}


class ContentError(Exception):
    """A content file is broken. The message says which file and which key."""


class Table:
    """One TOML table, read with type checks."""

    def __init__(self, data: dict[str, Any], where: str) -> None:
        self._data = data
        self._where = where
        self._used: set[str] = set()

    def error(self, message: str) -> ContentError:
        return ContentError(f"{self._where}: {message}")

    def _take[T](self, key: str, kind: type[T]) -> T | None:
        """The value at `key` if it has type `kind`, None if the key is absent.

        `[T]` makes this a generic function (Python 3.12+ syntax): ask for `str` and
        mypy knows you get `str | None` back, ask for `int` and you get `int | None`.
        """
        self._used.add(key)
        if key not in self._data:
            return None
        value = self._data[key]
        # bool is a subclass of int in Python, so `true` would pass as a number.
        is_bool_as_int = kind is int and isinstance(value, bool)
        if not isinstance(value, kind) or is_bool_as_int:
            got = _TYPE_NAMES.get(type(value), type(value).__name__)
            raise self.error(f"{key!r} must be {_TYPE_NAMES[kind]}, got {got}")
        return value

    def text(self, key: str) -> str:
        value = self._take(key, str)
        if value is None:
            raise self.error(f"missing {key!r}")
        if not value.strip():
            raise self.error(f"{key!r} is empty")
        return value.strip()

    def optional_text(self, key: str) -> str | None:
        value = self._take(key, str)
        return value.strip() if value and value.strip() else None

    def flag(self, key: str, default: bool = False) -> bool:
        value = self._take(key, bool)
        return default if value is None else value

    def number(self, key: str, default: int) -> int:
        value = self._take(key, int)
        return default if value is None else value

    def texts(self, key: str) -> tuple[str, ...]:
        items = self._take(key, list) or []
        for index, item in enumerate(items):
            if not isinstance(item, str):
                raise self.error(f"{key}[{index}] must be text")
        return tuple(item.strip() for item in items)

    def tables(self, key: str) -> list["Table"]:
        """An array of tables: the [[key]] blocks in TOML."""
        items = self._take(key, list) or []
        result = []
        for index, item in enumerate(items, start=1):
            if not isinstance(item, dict):
                raise self.error(f"{key} #{index} must be a [[{key}]] table")
            result.append(Table(item, f"{self._where} [[{key}]] #{index}"))
        return result

    def finish(self) -> None:
        """Call after reading everything: any key never asked for is probably a typo."""
        unknown = sorted(set(self._data) - self._used)
        if unknown:
            raise self.error(f"unknown key(s): {', '.join(unknown)}")


def read_table(path: Path, where: str) -> Table:
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ContentError(f"{where}: file not found") from exc
    except tomllib.TOMLDecodeError as exc:
        raise ContentError(f"{where}: not valid TOML ({exc})") from exc
    return Table(data, where)


def _job(table: Table) -> Job:
    job = Job(
        dates=table.text("dates"),
        title=table.text("title"),
        summary=table.optional_text("summary"),
    )
    table.finish()
    return job


def load_site(path: Path, where: str) -> Site:
    table = read_table(path, where)
    site = Site(
        name=table.text("name"),
        role=table.text("role"),
        intro=table.text("intro"),
        email=table.text("email"),
        github=table.text("github"),
        linkedin=table.text("linkedin"),
        photo=table.optional_text("photo"),
        skills=table.texts("skills"),
        hobbies=table.texts("hobbies"),
        experience=tuple(_job(job) for job in table.tables("experience")),
    )
    table.finish()
    return site


def load_project(path: Path, where: str) -> Project:
    slug = path.stem
    if not SLUG.fullmatch(slug):
        raise ContentError(
            f"{where}: file names become page addresses, so use lowercase letters, "
            "digits and dashes (e.g. my-project.toml)"
        )
    table = read_table(path, where)
    project = Project(
        slug=slug,
        name=table.text("name"),
        summary=table.text("summary"),
        tags=table.texts("tags"),
        url=table.optional_text("url"),
        featured=table.flag("featured"),
        order=table.number("order", default=100),
        thumbnail=table.optional_text("thumbnail"),
    )
    table.finish()
    return project


def load_content(content_dir: Path) -> Content:
    def where(path: Path) -> str:
        return str(path.relative_to(content_dir.parent))

    site_file = content_dir / "site.toml"
    site = load_site(site_file, where(site_file))
    project_files = sorted((content_dir / "projects").glob("*.toml"))
    projects = sorted(
        (load_project(path, where(path)) for path in project_files),
        key=Project.sort_key,
    )
    return Content(site=site, projects=tuple(projects))
