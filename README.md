# a11y-eco

[![CI](https://github.com/brivaltech/a11y-eco/actions/workflows/ci.yml/badge.svg)](https://github.com/brivaltech/a11y-eco/actions/workflows/ci.yml)

🇫🇷 [Lire en français](https://github.com/brivaltech/a11y-eco/blob/main/README.fr.md)

Audit a web page for **accessibility** and **eco-design** issues, from the command line,
with **zero runtime dependencies**.

> **Status: alpha.** The rules and the JSON format may still change before 1.0.

## Installation

Requires Python 3.12 or newer. a11y-eco has no dependencies.

```sh
pipx install a11y-eco        # recommended for a command-line tool
python -m pip install a11y-eco
```

On macOS, the `python3` command provided by the system may be too old. Install a recent
Python (from [python.org](https://www.python.org/downloads/) or Homebrew), then tell
pipx which one to use:

```sh
pipx install --python python3.12 a11y-eco
```

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
a11y-eco audit https://example.com --fetch-resources                     # real network measures
a11y-eco audit https://example.com --fetch-resources --include-external  # third parties too
a11y-eco audit https://example.com --format json                       # for programs
a11y-eco audit https://example.com --format html --output a11y-eco-report.html
```

Reports are written in English or French. The language is taken from `--lang`,
otherwise from the system (`LANG`, `LC_ALL`…), and French is used by default.

| Exit status | Meaning                                                        |
|-------------|----------------------------------------------------------------|
| `0`         | No finding reaches the `--fail-on` severity (default: `error`) |
| `1`         | At least one finding reaches it                                |
| `2`         | Invalid arguments, or the page could not be loaded             |

Colours are used only in an interactive terminal, and never when `NO_COLOR` is set.

### Network measures

By default, only the HTML of the page is downloaded. With `--fetch-resources`, a11y-eco
also downloads the page again and the files it loads, at most 50, four at a time, the way
a browser asks for them: announcing gzip and Brotli, without decompressing anything, so
that the counted bytes are the bytes really transferred. Nothing is executed.

The report then gets a separate "Network measures (real values)" section, and four more
rules check compression (`RWEB_0076`), cache headers (`RWEB_0075`), cookies on static
files (`RWEB_0081`) and redirections (`RWEB_0112`).

Files from other hosts (CDN, fonts, analytics, ads) are left out unless
`--include-external` is added: downloading them shows your IP address to those third
parties. A local file has no host, so its relative addresses cannot be downloaded and
all its absolute addresses count as other hosts: with a local file,
`--fetch-resources` measures nothing without `--include-external`.

### Report formats

`--format` chooses the report: `console` (default), `json` or `html`. Reports go to the
standard output, or to a UTF-8 file with `--output FILE`. `--fail-on` applies whatever
the format, so a CI job can keep a report and fail in a single command.

The **HTML report** is one self-contained page, without JavaScript or external files. It
is checked by a11y-eco itself in the test suite, and everything that comes from the
audited page is escaped.

The **JSON report** is meant for programs. Its keys are stable within a
`schema_version`:

| Key | Content |
|---|---|
| `schema_version` | Version of the structure, increased on every breaking change |
| `tool` | `name` and `version` of a11y-eco |
| `language` | Language of the `message` fields (`en` or `fr`) |
| `page` | `location` (path or URL) and `size` in bytes |
| `summary` | Number of findings for `error`, `warning` and `info` |
| `metrics` | Measures read from the HTML (minimum values), or `null` |
| `network` | Measures taken with `--fetch-resources`, with the list of `downloads`, or `null` |
| `findings` | `rule_id`, `severity`, `reference`, `message`, `line`, `column`, `snippet`, `details` |

Only `message` is translated. `line` and `column` are `null` when a finding has no
position in the HTML, and `details` holds raw numbers such as `count` and `limit`.
HTTP headers are never included: they may hold session cookies.

The full list of rules is in [docs/rules.md](https://github.com/brivaltech/a11y-eco/blob/main/docs/rules.md)
(or run `a11y-eco rules`), and the JSON report is described by a
[JSON Schema](https://github.com/brivaltech/a11y-eco/blob/main/schema/report-v1.schema.json).

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

- Only the HTML sent by the server is read: no JavaScript is run. Stylesheets and
  scripts are downloaded only with `--fetch-resources`, and are never interpreted:
  resources loaded by them (fonts declared in CSS, files requested by scripts) stay
  invisible.
- Request and resource counts are therefore **minimum values**. An eco-design rule reports
  a problem only when this minimum already exceeds the limit of the practice: a page that
  respects a practice is never reported, but some problems are not detected.
- Most RWEB practices concern design, servers or content, and cannot be checked from the
  HTML. The same goes for most RGAA criteria. An automated audit never replaces a manual one.
- Third-party tools (analytics, social buttons, carousels, animation libraries) are
  recognised from a list of known tools: a tool missing from the list is not detected.
- Network rules see the answers of the servers only: cookies set by JavaScript are not
  detected, and a chain of redirections counts as one.

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

[MIT](https://github.com/brivaltech/a11y-eco/blob/main/LICENSE)
