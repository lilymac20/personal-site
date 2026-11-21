# personal-site

Lily MacCormick's personal site, built with a small Python static site generator
(Jinja2 templates + content files) and hosted on GitHub Pages.

## Run it locally

Needs [uv](https://docs.astral.sh/uv/).

```sh
make serve   # build, then preview at http://localhost:8001
make check   # lint, type check and tests
```

## How it works

`src/site_builder/build.py` renders the templates in `templates/` into `dist/` and
copies `static/` next to them. GitHub Pages can only serve finished files, so Python
runs at build time, not while someone is visiting.
