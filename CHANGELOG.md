# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-11-17

### Added

- Project skeleton: `src` layout, `pyproject.toml` (hatchling), Ruff, pytest with coverage.
- Minimal command-line interface: `a11y-eco --version` and `python -m a11y_eco`.
- Stable exit codes: `0` OK, `1` findings above threshold, `2` usage error.
- Continuous integration: lint, tests on Python 3.12 and 3.13 (Linux, Windows, macOS),
  package build and smoke test, aggregate `CI OK` check required on `main`.
- English and French README, MIT license.
- Language-neutral data model: `Severity` (ordered by rank, never alphabetically),
  `Location` (1-based line and column) and immutable `Finding`.
- Lightweight DOM built on the standard library `html.parser`: lowercase names,
  attributes without value read as empty strings, first duplicated attribute wins,
  void elements, source position and original start tag of every element.
- Browser-like error recovery: omitted end tags (`li`, `p`, `td`, `th`, `tr`, `option`,
  `dt`, `dd`), unclosed elements and stray end tags.
- - `a11y-eco audit <file|url>` command, with `--fail-on error|warning|info|never`
  and `--timeout`.
- Page loader for local files and `http`/`https` URLs: browser-like encoding detection
  (byte order mark, `Content-Type` header, `<meta charset>`, Latin-1 read as
  Windows-1252), 10 MB limit, HTML content type check, clear error messages.
- First accessibility rules: `A11Y-LANG-MISSING` (RGAA 8.3) and `A11Y-LANG-INVALID`
  (RGAA 8.4).
- Accessible console report: severity always written in full, colours only in an
  interactive terminal, `NO_COLOR` honoured, `file:line:column` positions.
- Strict type checking with mypy in continuous integration.
- - `A11Y-IMG-ALT` (RGAA 1.1): images, image map links and image buttons without
  a text alternative; decorative images (`alt=""`, `aria-hidden`, `role="presentation"`)
  are accepted.
- Heading structure rules (RGAA 9.1), covering `h1`–`h6` and `role="heading"`:
  `A11Y-HEADING-SKIP` and `A11Y-HEADING-EMPTY` (errors), `A11Y-HEADING-H1-MISSING`
  (warning), `A11Y-HEADING-H1-MULTIPLE` (info).
- Simplified accessible name computation, following the order of the W3C
  specification: `aria-labelledby`, `aria-label`, native alternative, content, `title`.
- `A11Y-LINK-NAME` (RGAA 6.2) and `A11Y-BUTTON-NAME` (RGAA 11.9): links and buttons
  without an accessible name.
- `A11Y-ARIA-LABELLEDBY` (RGAA 8.2): `aria-labelledby` referring to an id that does
  not exist.
- Reports, help and error messages in English and French, with `--lang en|fr`.
- Language detected from the `LANGUAGE`, `LC_ALL`, `LC_MESSAGES` and `LANG` environment
  variables; French is used when none names a supported language.
- French typography: singular for 0 ("0 erreur"), narrow non-breaking space between
  thousands, non-breaking space before colons.
- Command-line options can no longer be abbreviated (`--fail` for `--fail-on`), so that
  adding an option never breaks existing scripts.
- pre-commit hooks running Ruff and mypy before each commit, and the tests before each push.
- - Inventory of the resources referenced by the HTML (stylesheets, scripts, images, fonts,
  audio and video, embedded content), each address counted once, on-demand resources apart.
- Sobriety measures in the report: requests when the page loads, resources by type,
  resources loaded on demand or served by another host, domains, DOM elements
  (minimum values, read from the HTML only).
- Eco-design rules based on the RWEB (5th edition), never reported as errors:
  `ECO-REQUESTS` (RWEB_0047), `ECO-STYLESHEETS` (RWEB_0035), `ECO-DOMAINS` (RWEB_0082),
  `ECO-INLINE-CODE` (RWEB_0042), `ECO-MEDIA-AUTOLOAD` (RWEB_0106),
  `ECO-LAZY-LOADING` (RWEB_0051), `ECO-EMBEDDED-DOCUMENT` (RWEB_0033), `ECO-GIF` (RWEB_0099),
  `ECO-WEB-FONTS` (RWEB_0032), `ECO-CANVAS` (RWEB_0055).
- Messages of findings can show values, such as a count and the recommended maximum.
- Credits of the RWEB and limits of an automated audit in the README.
- - Rules on the head of the page: `ECO-VIEWPORT` (RWEB_0004), `ECO-TITLE` and
  `ECO-META-DESCRIPTION` (RWEB_0011).
- Known tools recognised by signatures (loaded addresses, inline scripts, CSS classes,
  element names), kept in lists that can grow without changing any rule.
- Rules on third-party tools and visuals: `ECO-ANALYTICS` (RWEB_0111),
  `ECO-SOCIAL-BUTTONS` (RWEB_0059), `ECO-CAROUSEL` (RWEB_0010), `ECO-ANIMATIONS`
  (RWEB_0009), `ECO-SVG-METADATA` (RWEB_0100).
- - `A11Y-PAGE-TITLE` (RGAA 8.5): page without a title, or with an empty one, as an error;
  it shares its detection with `ECO-TITLE`.
- `--fetch-resources`: downloads the page and the files it loads (at most 50, four at a
  time, 10 MB each), announcing gzip and Brotli and counting the transferred bytes
  without decompressing them. Same-host files only, unless `--include-external` is given.
- "Network measures (real values)" section in the console report: requests, failed
  downloads, transferred bytes ("at least" when files were skipped or cut short).
- Network rules, run only with `--fetch-resources`: `ECO-COMPRESSION` (RWEB_0076),
  `ECO-CACHE-HEADERS` (RWEB_0075), `ECO-COOKIE-DOMAINS` (RWEB_0081),
  `ECO-REDIRECTS` (RWEB_0112).
- `--format console|json|html` and `--output FILE`; reports written to a file are UTF-8
  and never coloured, and `--fail-on` applies whatever the format.
- JSON report with a `schema_version`: stable English keys, raw numbers in `details`,
  translated `message`, network downloads without their HTTP headers.
- HTML report: one self-contained page without JavaScript, semantic headings and lists,
  severity always written in full, contrast of at least 4.5:1 in light and dark themes,
  print styles. Content of the audited page is escaped, and the report passes its own audit.
- Reporters share one protocol and one registry: a new format is a module and one line.
- `a11y-eco rules` lists every rule (console, JSON or Markdown), in English or French;
  `docs/rules.md` and `docs/rules.fr.md` are generated from it and checked by the tests.
- JSON Schema of the report (`schema/report-v1.schema.json`), checked against real
  reports in the tests.
- Package metadata for PyPI: classifiers, project links, absolute links in the README.
- Release workflow: a GitHub release goes to TestPyPI, then to PyPI after approval,
  with Trusted Publishing and attestations.
- Tests on Python 3.14; the smoke test runs a real audit from the built wheel.


[Unreleased]: https://github.com/brivaltech/a11y-eco/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/brivaltech/a11y-eco/releases/tag/v0.1.0
