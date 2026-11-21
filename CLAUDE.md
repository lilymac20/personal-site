# personal-site: notes for Claude

## What this is
Lily MacCormick's personal site / portfolio. A small Python static site generator
(Jinja2) builds HTML into `dist/`; GitHub Pages hosts it at
https://lilymac20.github.io/personal-site/ (repo github.com/lilymac20/personal-site, public).

## How to work with Lily
- She wants to understand every step. Work in small chunks (one feature at a time).
- Before writing code for a chunk: explain the approach and list the files you'll touch.
  After: explain what each piece does and why, and point out advanced Python concepts.
- Run `make check` (ruff, mypy strict, pytest) before every commit. Add tests with each feature.
- Small, focused commits with clear messages. Ask before pushing.

## Design
Design "E · Index Cards" from the mockup canvas
https://claude.ai/artifact/A5DK1Vvzu7nwxtaxd3tho4 (home page + project pages + template).
Cream background, cream "index cards" (pink rule under titles, faint blue ruled lines),
red accent #C23B22, postage-stamp photo frame, yellow wavy "say hi!" sticker, rubber-stamp
dates. Fonts (2026-11-21): name = Citta Novela Text Used (self-hosted, `--font-name`);
section headings = Going Alone (self-hosted handwriting, `--font-heading`); body text and
bold text = Jost (Google Fonts, Futura-style, 400/500/700, `--font-body`); labels = Space
Mono; Bricolage Grotesque still for the stamp initials, badge and sticker. Lily wanted body
text "a classic sans serif, a little unique and retro". Body fonts she tried and rejected:
Andika, Bitstream Vera Sans, TA Modern Times (too thin; its ligatures also mangled ".m"). Credits and licence notes in
`static/fonts/FONTS.md`.
Phone-first, touch targets at least 44px, text contrast at least 4.5:1.

## Conventions
- Python 3.13, uv, src layout (`src/site_builder/`), mypy strict, Ruff (line length 100).
- Every link in a template starts with `{{ root }}` (relative path back to the site root),
  never "/": the site lives under /personal-site/.
- CSS in `static/css/site.css`, organised tokens -> base -> layout -> components -> pages.
  Use the tokens.
- Jinja uses StrictUndefined: a missing variable is an error, not an empty string.

## Plan
1. Scaffold + tooling (done)
2. Content files (TOML) + dataclasses + home page
3. Project pages (one per TOML file) + template
4. GitHub Actions: build + deploy to Pages
5. Real Recipository screenshots (Playwright, channel="chrome")

## About Lily (for the site's content)
Software Engineer. Email lily.maccormick@gmail.com,
LinkedIn https://www.linkedin.com/in/lily-maccormick/, GitHub lilymac20.
Main project: Recipository (https://recipository.fly.dev), sibling folder ../Recipository.
