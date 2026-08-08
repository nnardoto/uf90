# Publicando uma versão

O repositório publica `uf90` no PyPI por GitHub Actions e Trusted Publishing.
Nenhum token PyPI deve ser salvo nos secrets do GitHub.

## Configuração única no PyPI

Como o projeto ainda não existe no PyPI, configure um pending publisher em
<https://pypi.org/manage/account/publishing/> com estes valores exatos:

| Campo | Valor |
|---|---|
| PyPI project name | `uf90` |
| Owner | `nnardoto` |
| Repository name | `uf90` |
| Workflow name | `publish.yml` |
| Environment name | `pypi` |

O pending publisher criará o projeto durante a primeira publicação. Ele não
reserva antecipadamente o nome no PyPI.

## Configuração única no GitHub

Em **Settings → Environments**, crie o ambiente `pypi`. Recomenda-se:

- permitir deploy somente a partir de tags protegidas `v*`;
- adicionar um required reviewer antes da publicação;
- não criar secrets ou tokens PyPI.

Em **Settings → Actions → General**, mantenha as permissões padrão do
`GITHUB_TOKEN` como somente leitura. O workflow concede `id-token: write`
apenas ao job isolado de publicação.

## Checklist de cada release

1. Atualize `__version__` em `src/uf90/__init__.py`.
2. Mova as notas de `Unreleased` para a nova versão em `CHANGELOG.md`.
3. Execute localmente:

   ```bash
   python3 -m pip install -e '.[test]'
   pytest
   python3 examples/run_all.py
   ```

4. Envie a alteração para `main` e aguarde o workflow **CI** passar.
5. Crie uma GitHub Release cuja tag seja exatamente `v<versão>`, por exemplo:

   ```bash
   git tag -s v0.1.1 -m "uf90 0.1.1"
   git push origin v0.1.1
   gh release create v0.1.1 --verify-tag --title "uf90 0.1.1" --notes-from-tag
   ```

6. Aprove o deploy no ambiente `pypi`, caso required reviewers estejam ativos.
7. Confirme a publicação:

   ```bash
   pipx install uf90
   uf90 --version
   fpm-uf90 --version
   ```

O workflow rejeita uma release quando a tag não corresponde exatamente ao
valor de `uf90.__version__`.
