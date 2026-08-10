# Design proposal: fortls proxy for uf90 0.2

[Português (Brasil)](../pt-BR/design/fortls-proxy-v0.2.md)

Status: implementation in progress on the 0.2 development branch.

This document records the intended direction for editor support after uf90
0.1.1. It is meant to provide enough context to start implementation in a new
development session.

## Goal

Use fortls to analyze the generated ASCII `.f90` files while users continue to
open and edit `.f90u` files. A small language-server proxy translates document
URIs and positions in both directions:

```text
VS Code or another LSP client (.f90u)
                  <->
               uf90-ls
       translate text, URIs and ranges
                  <->
              fortls (.f90)
```

The proxy should make hover, definitions, references and diagnostics work for
identifiers that fortls cannot currently resolve directly in `.f90u`, including
names that begin with Greek letters.

## Starting point in 0.1.1

The 0.1.1 integration adds `.f90u` to the fortls suffixes and excludes paired
generated `.f90` files. Testing with Modern Fortran 4.0.0 and fortls 3.2.2
showed that:

- parsing, document symbols and diagnostics work on `.f90u`;
- navigation works for identifiers such as `E₀`, which begin with ASCII;
- hover, definitions and references do not resolve names beginning with Greek
  letters, such as `α` and `Δt`;
- indexing both a `.f90u` source and its generated `.f90` can make navigation
  jump to the generated file.

The current setup remains useful as a documented partial integration. The
proxy is a separate feature proposed for 0.2, not a correction to be hidden in
the 0.1.1 scope.

## Proposed integration

Package an executable named `uf90-ls`. Modern Fortran can launch it through its
existing server-path setting:

```json
{
  "files.associations": {
    "*.f90u": "FortranFreeForm"
  },
  "fortran.fortls.path": "uf90-ls",
  "fortran.linter.compiler": "Disabled"
}
```

`uf90-ls` speaks JSON-RPC/LSP over standard input and output and starts the real
`fortls` process behind it. It must forward fortls command-line arguments and
provide an explicit way to select the underlying executable without recursively
launching itself, for example `UF90_FORTLS_PATH`.

This design is editor-independent. VS Code is the first tested client, but the
translation belongs in the proxy rather than a VS Code-only extension.

## Document lifecycle

At startup, the proxy should synchronize the project so fortls can index a
complete ASCII workspace. For each paired file:

```text
src/model.f90u <-> src/model.f90
```

The first implementation can follow this lifecycle:

1. Run the equivalent of `uf90 sync` before starting fortls.
2. Convert `textDocument/didOpen` from the `.f90u` URI and text to the paired
   `.f90` URI and translated text.
3. Translate the complete in-memory document on `textDocument/didChange`.
   Full-document synchronization is preferable for the first version.
4. Write the generated `.f90` on `textDocument/didSave` so the file used by
   fpm matches the saved `.f90u` source.
5. Forward `textDocument/didClose` using the paired URI.

Unsaved editor contents should be sent to fortls in memory. They should not
silently become compiler input before the `.f90u` document is saved.

Handwritten `.f90` files have no paired `.f90u` source and pass through the
proxy unchanged.

To receive complete documents, the proxy must adjust the `textDocumentSync`
capability returned during `initialize`, even if fortls advertises incremental
synchronization to the proxy.

## Source maps

Translation preserves physical line boundaries, so line numbers normally stay
the same. Character offsets do not:

```text
.f90u: real :: α
.f90:  real :: uc_alpha
```

The translator must therefore produce a source map at the same time as the
ASCII text. Reconstructing positions afterward is fragile. For every translated
line, store mappings between source and generated character boundaries, as well
as the paired source and generated URIs.

LSP positions use a negotiated position encoding. VS Code commonly uses UTF-16,
while Python string indexes count Unicode code points. Conversion utilities
must explicitly handle the negotiated encoding rather than assuming that a
Python index is an LSP character offset.

The existing `translate_text()` API should remain compatible. A new internal
API can return a structure similar to:

```python
TranslationResult(
    text=generated_text,
    source_map=source_map,
)
```

Mappings must support both directions and define how a position inside an
expanded token maps back to the original Unicode token.

## LSP message translation

Client-to-server messages must replace `.f90u` URIs with paired `.f90` URIs and
map incoming positions or ranges to generated coordinates. Server-to-client
messages must perform the inverse transformation.

The transformation should be implemented with typed, method-specific handlers,
not unrestricted replacement of every object containing `uri`, `line` or
`character`. Different LSP methods attach different semantics to those fields.

### Milestone 1: read-only navigation

The first useful milestone should cover:

- initialization and shutdown forwarding;
- open, full change, save and close notifications;
- hover;
- definition, declaration, type definition and implementation;
- references;
- document and workspace symbols;
- diagnostics published by fortls.

Returned `Location`, `LocationLink`, `Range`, `DocumentSymbol` and related
structures must point back to `.f90u` only when a known source/generated pair
exists. Locations in handwritten Fortran or external libraries remain `.f90`.

### Milestone 2: completions and signatures

Completion labels, inserted text and `TextEdit` ranges may contain generated
ASCII identifiers such as `uc_alpha`. Converting them back requires a project
symbol map in addition to positional source maps. Signature help and hover text
may need the same presentation conversion.

### Milestone 3: editing operations

Rename, code actions and workspace edits can modify several files. They should
remain disabled or pass through only for handwritten `.f90` files until every
edit can be translated safely back to `.f90u`. No operation may edit a generated
`.f90` while presenting that edit as successful on the Unicode source.

## Name identity and collisions

The proxy exposes a pre-existing translation concern: distinct Unicode and
ASCII identifiers may normalize to the same Fortran name. Positional maps are
enough for navigation to an existing occurrence, but completion and rename
need an unambiguous symbol identity.

Before enabling editing operations, uf90 should detect collisions across each
Fortran scope or conservatively across the project. Relevant cases include a
Unicode identifier and a handwritten ASCII identifier that both produce the
same normalized spelling.

## Generated-file policy

The recommended initial implementation should reuse the adjacent `.f90` files
already consumed by fpm. This avoids maintaining a second shadow workspace and
keeps module discovery consistent with the build.

A separate cache such as `.uf90/lsp/` should be considered only if writing
adjacent files creates concrete editor or concurrency problems. A shadow tree
would also need handwritten sources, include paths and project layout to be
mirrored correctly.

When the proxy is active, fortls should index generated `.f90` files rather
than `.f90u`. The 0.1.1 `fortls-config` behavior is therefore not the final
configuration for proxy mode.

## Failure behavior

- If translation fails, publish a diagnostic on the `.f90u` document and do
  not send stale generated text as if it were current.
- If fortls is missing or exits, surface a clear error and preserve its exit
  status where possible.
- Protocol logs must go to standard error or a file; standard output is
  reserved for JSON-RPC messages.
- The proxy must prevent an executable-resolution loop when locating fortls.
- Cancellation requests and request IDs must pass through without being
  reordered.

## Acceptance tests for 0.2.0

Use both a deterministic fake LSP server and a pinned fortls compatibility job.
At minimum, verify:

- URI conversion for paired `.f90u`/`.f90` files;
- unchanged URIs for handwritten and external `.f90` files;
- position mapping before, inside and after Greek, subscript and superscript
  expansions;
- UTF-16 positions, including non-BMP characters in surrounding comments or
  strings;
- cross-file definition and references for identifiers beginning with Greek;
- diagnostic ranges mapped back to `.f90u`;
- unsaved full-document changes without updating compiler input on disk;
- clean shutdown, cancellation and a crashed fortls subprocess;
- Linux, macOS and Windows execution through the packaged `uf90-ls` entry point.

The existing oscillator example is a good end-to-end fixture because it has
Greek-starting members (`ω`, `Δt`) and ASCII-starting identifiers with Unicode
subscripts (`E₀`).

## Non-goals for the first release

- implementing a new Fortran parser or language server;
- forking fortls;
- replacing Modern Fortran;
- providing compiler diagnostics directly on unsaved `.f90u` text;
- supporting rename or arbitrary workspace edits before bidirectional edits
  are proven safe;
- depending on LLVM or MLIR.

## Open decisions

Resolve these during the first implementation spike:

1. Whether full-document synchronization is sufficient for 0.2.0 or whether
   incremental synchronization is required later.
2. The exact configuration mechanism for selecting the real fortls executable.
3. Whether hover and completion text should expose Unicode names in 0.2.0 or
   initially guarantee only correct navigation and ranges.
4. How strict collision detection must be before completion and rename are
   enabled.
5. Whether proxy mode replaces `uf90 fortls-config` or is introduced as a
   separate explicit editor mode during the transition.

## Suggested implementation order

1. Refactor translation to optionally emit bidirectional source maps and test
   them independently of LSP.
2. Implement JSON-RPC framing and transparent fortls process forwarding.
3. Add URI rewriting and full-document synchronization.
4. Add hover, definition, references, symbols and diagnostics one method at a
   time.
5. Add a real fortls end-to-end test using the oscillator example.
6. Document the experimental VS Code setting and package `uf90-ls` through the
   existing pipx distribution.
7. Consider completion, signatures and rename only after the read-only layer is
   stable.

Relevant references:

- [Language Server Protocol](https://microsoft.github.io/language-server-protocol/)
- [VS Code Language Server Extension Guide](https://code.visualstudio.com/api/language-extensions/language-server-extension-guide)
- [fortls configuration options](https://fortls.fortran-lang.org/options.html)
