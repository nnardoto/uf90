#!/usr/bin/env bash
set -euo pipefail

# Helper de uso rápido (opcional):
# - instala o pacote em modo editable
# - expõe comandos idiomáticos:
#     uf90 sync
#     uf90 check
#     uf90 translate
#     uf90 fpm ...

ROOT="${1:-.}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Erro: python3 não encontrado." >&2
  exit 127
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

python3 -m pip install -e "${SCRIPT_DIR}"
shift || true

# Se você chamar: ./uf90.sh . fpm build
# ele vira: uf90 fpm --root . build
if [[ "${1:-}" == "fpm" ]]; then
  shift
  exec uf90 fpm --root "${ROOT}" "$@"
fi

# default: roda sync
exec uf90 sync "${ROOT}" "$@"
