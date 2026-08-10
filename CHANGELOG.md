# Changelog

All notable changes to `uf90` are documented in this file. The project follows
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Bidirectional source maps for translated text, including explicit UTF-8,
  UTF-16, and UTF-32 LSP position conversion, as the first building block of
  the `uf90-ls` proxy planned for 0.2.0.
- `uf90-ls` executable with validated JSON-RPC framing, transparent
  bidirectional forwarding, safe fortls executable selection, and subprocess
  exit-status propagation.
- Stateful `.f90u` document synchronization for `uf90-ls`, translating URIs
  and full document contents in memory while writing generated `.f90` files
  only after `textDocument/didSave`.
- Read-only LSP navigation translation for hover, definitions, declarations,
  type definitions, implementations, references, document/workspace symbols,
  and diagnostics, including cross-file locations and negotiated position
  encodings.
- Unicode identifier presentation in hover content when the generated ASCII
  name maps unambiguously to one source spelling in the project.
- Pinned `fortls` 3.2.2 integration coverage for cross-file definition,
  references, Unicode hover, unsaved document changes, and clean shutdown
  using the oscillator example.
- Experimental `uf90-ls` setup guides for VS Code and Neovim 0.10/0.11+ in
  English and Brazilian Portuguese.
- `lsp` installation extra and `uf90 editor-config` generator for ready-to-use
  VS Code and Neovim configurations without overwriting existing files by
  default.

## [0.1.1] - 2026-08-07

### Added

- `uf90 fortls-config` command for indexing `.f90u` sources while excluding
  only their generated `.f90` counterparts.
- Tested VS Code and Modern Fortran setup, with current fortls limitations
  documented explicitly.

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

[Unreleased]: https://github.com/nnardoto/uf90/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/nnardoto/uf90/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/nnardoto/uf90/releases/tag/v0.1.0
