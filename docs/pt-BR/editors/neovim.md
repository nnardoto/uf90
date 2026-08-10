# Neovim e uf90-ls

[English](../../editors/neovim.md)

O proxy não depende do editor e funciona com o cliente LSP nativo do Neovim.
Primeiro, instale a versão em desenvolvimento e o fortls fixado:

```bash
pipx install --force --editable '.[lsp]'
uf90-ls --version
```

Depois da publicação da versão 0.2, use `pipx install 'uf90[lsp]'` para a
versão de lançamento.

## Neovim 0.11 ou mais recente

Gere um módulo Lua e carregue-o pelo `init.lua`:

```bash
uf90 editor-config neovim -o ~/.config/nvim/lua/uf90.lua
```

```lua
require('uf90')
```

O gerador detecta o caminho de `uf90-ls` e se recusa a substituir um arquivo
existente. Use `uf90 editor-config neovim` sem `-o` para imprimir a configuração
ou `--server /caminho/personalizado/uf90-ls` para selecionar o executável. O
módulo gerado contém:

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

vim.api.nvim_create_autocmd('LspAttach', {
  callback = function(args)
    local client = vim.lsp.get_client_by_id(args.data.client_id)
    if client and client.name == 'uf90_ls' then
      vim.lsp.completion.enable(true, client.id, args.buf, { autotrigger = true })
      vim.keymap.set('i', '<C-Space>', vim.lsp.completion.get, { buffer = args.buf })
    end
  end,
})

vim.lsp.enable('uf90_ls')
```

Essa configuração usa as APIs nativas `vim.lsp.config()` e
`vim.lsp.enable()`, introduzidas no Neovim 0.11. O `nvim-lspconfig` não é
necessário para essa definição personalizada. Se você já habilita a
configuração `fortls` dele, desabilite-a para que apenas um servidor de
linguagem se conecte aos buffers Fortran.

O caminho absoluto gerado também funciona quando o Neovim não herda o `PATH` do
shell.

Em um buffer `.f90u`, digite `\alpha` e selecione o item `α` com `Ctrl+Y`.
Digitar `\` abre automaticamente o menu; `Ctrl+Space` abre a conclusão
manualmente. `\partial` e `\nabla` inserem `∂` e `∇`; comandos com inicial
maiúscula, como `\Delta`, inserem letras gregas maiúsculas.

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
