# Neovim and uf90-ls

[Português (Brasil)](../pt-BR/editors/neovim.md)

The proxy is editor-independent and works with Neovim's built-in LSP client.
Install the development version and pinned fortls first:

```bash
pipx install --force --editable .
pipx inject uf90 fortls==3.2.2
uf90-ls --version
```

## Neovim 0.11 and newer

Add this to `init.lua`:

```lua
vim.filetype.add({
  extension = {
    f90u = 'fortran',
  },
})

vim.lsp.config('uf90_ls', {
  cmd = { 'uf90-ls', '--disable_autoupdate' },
  filetypes = { 'fortran' },
  root_markers = { 'fpm.toml', '.git' },
})

vim.lsp.enable('uf90_ls')
```

This uses the native `vim.lsp.config()` and `vim.lsp.enable()` APIs introduced
in Neovim 0.11. `nvim-lspconfig` is not required for this custom definition. If
you already enable its `fortls` configuration, disable that configuration so
only one language server attaches to Fortran buffers.

If `uf90-ls` is not on Neovim's `PATH`, replace it in `cmd` with the absolute
path printed by `command -v uf90-ls`.

## Neovim 0.10

Neovim 0.10 can start the proxy directly for Fortran buffers:

```lua
vim.filetype.add({
  extension = {
    f90u = 'fortran',
  },
})

vim.api.nvim_create_autocmd('FileType', {
  pattern = 'fortran',
  callback = function(args)
    local root = vim.fs.root(args.buf, { 'fpm.toml', '.git' })
      or vim.fs.dirname(vim.api.nvim_buf_get_name(args.buf))

    vim.lsp.start({
      name = 'uf90_ls',
      cmd = { 'uf90-ls', '--disable_autoupdate' },
      root_dir = root,
    }, {
      bufnr = args.buf,
    })
  end,
})
```

Upgrading to Neovim 0.11 or newer is recommended; the legacy
`require('lspconfig').fortls.setup()` API is deprecated by nvim-lspconfig.

## Verify the connection

Open the oscillator example from its project root:

```bash
cd examples/06_oscillator
nvim app/main.f90u
```

Then check:

```vim
:set filetype?
:checkhealth vim.lsp
:lua vim.lsp.buf.hover()
:lua vim.lsp.buf.definition()
:lua vim.lsp.buf.references()
```

The filetype should be `fortran`, and the active client should be `uf90_ls`.
Navigation results for generated pairs should open `.f90u`. The same feature
and safety limitations described in the [VS Code guide](vscode.md) apply.

References: [Neovim LSP documentation](https://neovim.io/doc/user/lsp) and
[nvim-lspconfig migration guide](https://github.com/neovim/nvim-lspconfig).
