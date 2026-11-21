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

## Adding a project

Add `content/projects/<name>.toml` (copy `recipository.toml`; every page field is optional)
and put its screenshots in `static/img/projects/<name>/`. The file name becomes the address:
`projects/<name>/`.

## Deploying

Every push to `main` runs `.github/workflows/pages.yml`: `make check`, `make build`, then
publishes `dist/` to GitHub Pages at https://lilymac20.github.io/personal-site/. Pull requests
run the checks without deploying.
