# a11y-eco

[![CI](https://github.com/brivaltech/a11y-eco/actions/workflows/ci.yml/badge.svg)](https://github.com/brivaltech/a11y-eco/actions/workflows/ci.yml)

🇫🇷 [Lire en français](README.fr.md)

Audit a web page for **accessibility** and **eco-design** issues, from the command line,
with **zero runtime dependencies**.

> **Status: pre-alpha.** The project is under active development, one sprint at a time.
> Nothing is published on PyPI yet.

## Goals

- Detect the most common accessibility defects in static HTML: missing image alternatives,
  broken heading hierarchy, missing page language, links and buttons without an accessible name.
  Each rule references the matching [RGAA](https://accessibilite.numerique.gouv.fr/) criterion.
- Report eco-design indicators: page weight, number of resources, and checks inspired by the
  [115 web eco-design best practices](https://github.com/cnumr/best-practices).
- Output reports to the console, as JSON (for CI and tooling) or as a standalone HTML page.
- Run in English or French.

## Out of scope

- JavaScript rendering: only the HTML sent by the server is analysed.
- A full RGAA audit: automated checks cover a small subset of the criteria and never replace
  a manual audit.

## Usage

```sh
a11y-eco audit page.html                 # a local file
a11y-eco audit https://example.com       # a web page
a11y-eco audit page.html --fail-on warning
```

| Exit status | Meaning                                                        |
|-------------|----------------------------------------------------------------|
| `0`         | No finding reaches the `--fail-on` severity (default: `error`) |
| `1`         | At least one finding reaches it                                |
| `2`         | Invalid arguments, or the page could not be loaded             |

Colours are used only in an interactive terminal, and never when `NO_COLOR` is set.

## Development

Requires Python 3.12 or later and pip 25.1 or later.

```sh
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install --group dev -e .
pre-commit install                 # run lint, format and type checks before each commit

python -m pytest --cov             # tests and coverage
ruff check . && ruff format .      # lint and format
a11y-eco --version
```

## License

[MIT](LICENSE)
