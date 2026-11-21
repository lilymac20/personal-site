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
class Shot:
    """A screenshot (path inside static/) and the words under it."""

    image: str
    caption: str


@dataclass(frozen=True, slots=True, kw_only=True)
class Feature:
    title: str
    text: str
    screenshot: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class Highlight:
    title: str  # shown in bold, followed by the text
    text: str


@dataclass(frozen=True, slots=True, kw_only=True)
class Project:
    slug: str  # from the file name; also the page address
    # The card on the home page
    name: str
    summary: str
    tags: tuple[str, ...]
    url: str | None
    featured: bool
    order: int
    thumbnail: str | None
    # The project page (all optional)
    tagline: str | None
    year: str | None
    role: str | None
    stack: tuple[str, ...]
    hosting: str | None
    status: str | None
    code_url: str | None
    hero: Shot | None
    why: str | None
    features: tuple[Feature, ...]
    highlights: tuple[Highlight, ...]
    gallery: tuple[Shot, ...]
    learned: str | None

    def sort_key(self) -> tuple[bool, int, str]:
        # False sorts before True, so "not featured" puts featured projects first.
        return (not self.featured, self.order, self.name.lower())

    @property
    def facts(self) -> list[tuple[str, str]]:
        """The label/value row under the title, skipping anything not filled in."""
        rows = [
            ("Role", self.role),
            ("Stack", ", ".join(self.stack) or None),
            ("Hosting", self.hosting),
            ("Status", self.status),
        ]
        return [(label, value) for label, value in rows if value]

    def images(self) -> list[str]:
        paths = [self.thumbnail, self.hero.image if self.hero else None]
        paths += [feature.screenshot for feature in self.features]
        paths += [shot.image for shot in self.gallery]
        return [path for path in paths if path]


@dataclass(frozen=True, slots=True, kw_only=True)
class Content:
    site: Site
    projects: tuple[Project, ...]

    def images(self) -> list[str]:
        """Every image path the content points at (relative to static/)."""
        paths = [self.site.photo] if self.site.photo else []
        for project in self.projects:
            paths += project.images()
        return paths
