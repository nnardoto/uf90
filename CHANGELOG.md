# Changelog

All notable changes to `uf90` are documented in this file. The project follows
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-08-07

### Added

- Native `fpm-uf90` plugin entry point for `fpm uf90 build`, `run`, and `test`.
- Alphanumeric Unicode subscripts, including `Eₙ`, `Aᵢⱼ`, and mixed forms.
- Six progressive, executable `fpm` example projects.
- Comprehensive mapping, lexer, synchronization, file, and plugin test coverage.

### Fixed

- Preserve Unicode inside strings and comments during normal translation.
- Correctly handle exclamation marks and doubled quotes inside string literals.
- Regenerate a cached output when its generated `.f90` file has been removed.
- Forward command-line arguments from compatibility entry points.

[Unreleased]: https://github.com/nnardoto/uf90/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/nnardoto/uf90/releases/tag/v0.1.0
