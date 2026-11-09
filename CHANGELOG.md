# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
