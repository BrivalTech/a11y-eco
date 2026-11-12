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
- Report eco-design indicators (requests, resources, hosts, DOM size) and checks based on
  the RWEB, the French web eco-design reference ("115 best practices").
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
a11y-eco audit page.html --lang en       # report in English
```

Reports are written in English or French. The language is taken from `--lang`,
otherwise from the system (`LANG`, `LC_ALL`…), and French is used by default.

| Exit status | Meaning                                                        |
|-------------|----------------------------------------------------------------|
| `0`         | No finding reaches the `--fail-on` severity (default: `error`) |
| `1`         | At least one finding reaches it                                |
| `2`         | Invalid arguments, or the page could not be loaded             |

Colours are used only in an interactive terminal, and never when `NO_COLOR` is set.

## Eco-design rules and credits

Eco-design rules refer to the practices of the **RWEB** (*Référentiel d'écoconception web*,
5th edition), by their identifier, for example `RWEB_0047`. The RWEB is published by
GreenIT.fr as part of the work of the Collectif conception numérique responsable, under
the [Creative Commons BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/)
licence: <https://collectif.greenit.fr> · <https://www.ecoconceptionweb.com> ·
<https://rweb.greenit.fr>.

a11y-eco does not reproduce the content of the RWEB: messages are written for this tool,
and only the identifiers of the practices and the limits of their validation rules are used.

## Limits of an automated audit

- Only the HTML sent by the server is read: no JavaScript is run, and stylesheets and
  scripts are not downloaded.
- Request and resource counts are therefore **minimum values**. An eco-design rule reports
  a problem only when this minimum already exceeds the limit of the practice: a page that
  respects a practice is never reported, but some problems are not detected.
- Most RWEB practices concern design, servers or content, and cannot be checked from the
  HTML. The same goes for most RGAA criteria. An automated audit never replaces a manual one.

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
