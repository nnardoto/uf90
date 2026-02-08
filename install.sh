#!/usr/bin/env bash
# ==============================================================================
# install.sh - Instalador completo do uf90
# ==============================================================================
# Este script instala tanto o uf90-sync quanto o wrapper fpm-unicode
# ==============================================================================

set -e  # Para no primeiro erro

# Cores
if [ -t 1 ]; then
    BLUE='\033[0;34m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    RED='\033[0;31m'
    NC='\033[0m'
else
    BLUE=''
    GREEN=''
    YELLOW=''
    RED=''
    NC=''
fi

print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# ==============================================================================
# Verificações iniciais
# ==============================================================================

print_header "uf90 - Instalador"

# Verifica FPM
if ! command -v fpm &> /dev/null; then
    print_error "FPM não encontrado!"
    echo "Instale FPM: https://fpm.fortran-lang.org/install/"
    exit 1
fi
print_success "FPM encontrado: $(fpm --version 2>&1 | head -1)"

# Verifica compilador Fortran
if command -v gfortran &> /dev/null; then
    COMPILER="gfortran"
    print_success "Compilador: $(gfortran --version | head -1)"
elif command -v ifort &> /dev/null; then
    COMPILER="ifort"
    print_success "Compilador: $(ifort --version | head -1)"
else
    print_error "Compilador Fortran não encontrado!"
    echo "Instale gfortran ou ifort"
    exit 1
fi

# Verifica se estamos no diretório correto
if [ ! -f "fpm.toml" ]; then
    print_error "fpm.toml não encontrado!"
    echo "Execute este script no diretório raiz do uf90"
    exit 1
fi

# Define diretório de instalação
PREFIX="${PREFIX:-$HOME/.local}"
print_info "Diretório de instalação: $PREFIX"

# ==============================================================================
# Etapa 1: Compilar e instalar uf90-sync
# ==============================================================================

print_header "Compilando uf90-sync"

echo "Executando: fpm build"
if fpm build; then
    print_success "Compilação bem-sucedida"
else
    print_error "Falha na compilação"
    exit 1
fi

echo ""
echo "Executando: fpm install --prefix $PREFIX"
if fpm install --prefix "$PREFIX"; then
    print_success "uf90-sync instalado em $PREFIX/bin/"
else
    print_error "Falha na instalação"
    exit 1
fi

# ==============================================================================
# Etapa 2: Instalar fpm-unicode wrapper
# ==============================================================================

print_header "Instalando fpm-unicode wrapper"

if [ ! -f "fpm-unicode" ]; then
    print_error "Arquivo fpm-unicode não encontrado!"
    echo "O wrapper deve estar no diretório raiz do projeto"
    exit 1
fi

# Cria diretório se não existir
mkdir -p "$PREFIX/bin"

# Copia e torna executável
cp fpm-unicode "$PREFIX/bin/"
chmod +x "$PREFIX/bin/fpm-unicode"

if [ -x "$PREFIX/bin/fpm-unicode" ]; then
    print_success "fpm-unicode instalado em $PREFIX/bin/"
else
    print_error "Falha ao instalar fpm-unicode"
    exit 1
fi

# ==============================================================================
# Etapa 3: Verificar PATH
# ==============================================================================

print_header "Verificando configuração do PATH"

if [[ ":$PATH:" == *":$PREFIX/bin:"* ]]; then
    print_success "$PREFIX/bin já está no PATH"
else
    print_info "$PREFIX/bin NÃO está no PATH"
    echo ""
    echo "Adicione ao seu ~/.bashrc ou ~/.zshrc:"
    echo -e "${YELLOW}export PATH=\"$PREFIX/bin:\$PATH\"${NC}"
    echo ""
    echo "Ou execute agora (temporário):"
    echo -e "${YELLOW}export PATH=\"$PREFIX/bin:\$PATH\"${NC}"
fi

# ==============================================================================
# Etapa 4: Testar instalação
# ==============================================================================

print_header "Testando instalação"

# Adiciona temporariamente ao PATH para testes
export PATH="$PREFIX/bin:$PATH"

# Testa uf90-sync
if command -v uf90-sync &> /dev/null; then
    print_success "uf90-sync encontrado: $(which uf90-sync)"
else
    print_error "uf90-sync não encontrado no PATH"
fi

# Testa fpm-unicode
if command -v fpm-unicode &> /dev/null; then
    print_success "fpm-unicode encontrado: $(which fpm-unicode)"
else
    print_error "fpm-unicode não encontrado no PATH"
fi

# ==============================================================================
# Resumo
# ==============================================================================

print_header "Instalação Concluída!"

echo ""
echo "Arquivos instalados:"
echo "  • $PREFIX/bin/uf90-sync"
echo "  • $PREFIX/bin/fpm-unicode"
echo ""

if [[ ":$PATH:" != *":$PREFIX/bin:"* ]]; then
    echo -e "${YELLOW}⚠ Importante:${NC} Adicione ao PATH para usar:"
    echo "  export PATH=\"$PREFIX/bin:\$PATH\""
    echo ""
    echo "Para tornar permanente, adicione ao ~/.bashrc:"
    echo "  echo 'export PATH=\"$PREFIX/bin:\$PATH\"' >> ~/.bashrc"
    echo ""
fi

echo "Como usar:"
echo ""
echo "  ${GREEN}Opção 1: Workflow manual${NC}"
echo "    uf90-sync              # Traduz .f90u → .f90"
echo "    fpm build              # Compila"
echo ""
echo "  ${GREEN}Opção 2: Workflow automático (recomendado)${NC}"
echo "    fpm-unicode build      # Traduz + compila automaticamente"
echo "    fpm-unicode run        # Traduz + executa"
echo "    fpm-unicode test       # Traduz + testa"
echo ""
echo "Documentação: README.md"
echo "Exemplos: examples/"
echo ""

print_success "Tudo pronto! 🚀"
