"""The site's content as plain, read-only Python objects.

`frozen=True` means nothing can change them after loading, `slots=True` makes them
small and catches attribute typos, and `kw_only=True` forces `Job(title=...)` style
calls so fields can't be mixed up by position.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class Job:
    dates: str
    title: str
    summary: str | None  # optional: a degree may not need one


@dataclass(frozen=True, slots=True, kw_only=True)
class Site:
    name: str
    role: str
    intro: str
    email: str
    github: str
    linkedin: str
    photo: str | None
    skills: tuple[str, ...]
    hobbies: tuple[str, ...]
    experience: tuple[Job, ...]

    @property
    def initials(self) -> str:
        return "".join(word[0] for word in self.name.split()).upper()


@dataclass(frozen=True, slots=True, kw_only=True)
class Project:
    slug: str  # from the file name; also the page address
    name: str
    summary: str
    tags: tuple[str, ...]
    url: str | None
    featured: bool
    order: int
    thumbnail: str | None

    def sort_key(self) -> tuple[bool, int, str]:
        # False sorts before True, so "not featured" puts featured projects first.
        return (not self.featured, self.order, self.name.lower())


@dataclass(frozen=True, slots=True, kw_only=True)
class Content:
    site: Site
    projects: tuple[Project, ...]

    def images(self) -> list[str]:
        """Every image path the content points at (relative to static/)."""
        paths = [self.site.photo] + [project.thumbnail for project in self.projects]
        return [path for path in paths if path]
