# Neovim e uf90-ls

[English](../../editors/neovim.md)

O proxy não depende do editor e funciona com o cliente LSP nativo do Neovim.
Primeiro, instale a versão em desenvolvimento e o fortls fixado:

```bash
pipx install --force --editable .
pipx inject uf90 fortls==3.2.2
uf90-ls --version
```

## Neovim 0.11 ou mais recente

Adicione isto ao `init.lua`:

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

Essa configuração usa as APIs nativas `vim.lsp.config()` e
`vim.lsp.enable()`, introduzidas no Neovim 0.11. O `nvim-lspconfig` não é
necessário para essa definição personalizada. Se você já habilita a
configuração `fortls` dele, desabilite-a para que apenas um servidor de
linguagem se conecte aos buffers Fortran.

Se `uf90-ls` não estiver no `PATH` do Neovim, substitua-o em `cmd` pelo caminho
absoluto mostrado por `command -v uf90-ls`.

## Neovim 0.10

O Neovim 0.10 pode iniciar o proxy diretamente para buffers Fortran:

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

Recomenda-se atualizar para o Neovim 0.11 ou mais recente; a API legada
`require('lspconfig').fortls.setup()` está depreciada pelo nvim-lspconfig.

## Verificar a conexão

Abra o exemplo do oscilador a partir da raiz do projeto:

```bash
cd examples/06_oscillator
nvim app/main.f90u
```

Depois verifique:

```vim
:set filetype?
:checkhealth vim.lsp
:lua vim.lsp.buf.hover()
:lua vim.lsp.buf.definition()
:lua vim.lsp.buf.references()
```

O filetype deve ser `fortran`, e o cliente ativo deve ser `uf90_ls`. Resultados
de navegação para pares gerados devem abrir `.f90u`. Aplicam-se os mesmos
recursos e limites de segurança descritos no [guia do VS Code](vscode.md).

Referências: [documentação LSP do Neovim](https://neovim.io/doc/user/lsp) e
[guia de migração do nvim-lspconfig](https://github.com/neovim/nvim-lspconfig).
