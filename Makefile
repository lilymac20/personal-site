.PHONY: build serve clean test lint format typecheck check

# 8000 is Recipository's local app; use another port with: make serve PORT=8080
PORT ?= 8001

build:         ## Build the site into dist/
	uv run python -m site_builder

serve: build   ## Build, then preview at http://localhost:8001
	uv run python -m http.server --directory dist $(PORT)

clean:         ## Delete the built site
	rm -rf dist

test:          ## Run the test suite
	uv run pytest

lint:          ## Check code style
	uv run ruff check .
	uv run ruff format --check .

format:        ## Fix code style automatically
	uv run ruff check --fix .
	uv run ruff format .

typecheck:     ## Check type hints
	uv run mypy

check: lint typecheck test   ## Everything CI runs
