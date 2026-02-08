# ==============================================================================
# Makefile para projetos com arquivos .f90u (Unicode Fortran)
# ==============================================================================
# Este Makefile integra uf90-sync com FPM automaticamente.
#
# Uso:
#   make           # Traduz .f90u e compila
#   make build     # Mesmo que acima
#   make run       # Traduz, compila e executa
#   make test      # Traduz, compila e testa
#   make clean     # Remove build/ e .f90 gerados
#   make sync      # Apenas traduz .f90u → .f90
# ==============================================================================

.PHONY: all build run test clean sync help

# Cores para output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m

# ==============================================================================
# TARGETS PRINCIPAIS
# ==============================================================================

all: build

# Traduz + compila
build: sync
	@echo "$(BLUE)━━━ Building project$(NC)"
	@fpm build
	@echo "$(GREEN)✓ Build complete$(NC)"

# Traduz + compila + executa
run: sync
	@echo "$(BLUE)━━━ Running project$(NC)"
	@fpm run

# Traduz + compila + testa
test: sync
	@echo "$(BLUE)━━━ Running tests$(NC)"
	@fpm test

# Apenas traduz .f90u → .f90
sync:
	@echo "$(BLUE)━━━ Syncing .f90u files$(NC)"
	@if command -v uf90-sync > /dev/null 2>&1; then \
		uf90-sync; \
		echo "$(GREEN)✓ Translation complete$(NC)"; \
	else \
		echo "$(YELLOW)⚠ uf90-sync not found, skipping translation$(NC)"; \
		echo "  Install: fpm install --prefix ~/.local"; \
	fi

# Remove arquivos de build e .f90 gerados
clean:
	@echo "$(BLUE)━━━ Cleaning project$(NC)"
	@rm -rf build/
	@# Remove apenas .f90 gerados (com marcador)
	@find src app test -name "*.f90" -type f 2>/dev/null | while read f; do \
		if head -n1 "$$f" | grep -q "GENERATED FROM .f90u"; then \
			echo "  Removing: $$f"; \
			rm -f "$$f"; \
		fi; \
	done
	@echo "$(GREEN)✓ Clean complete$(NC)"

# Remove tudo (incluindo .f90 manuais - use com cuidado!)
clean-all:
	@echo "$(YELLOW)⚠ Removing ALL .f90 files$(NC)"
	@rm -rf build/
	@find src app test -name "*.f90" -delete 2>/dev/null || true
	@echo "$(GREEN)✓ Deep clean complete$(NC)"

# Instala executáveis no sistema
install: build
	@echo "$(BLUE)━━━ Installing$(NC)"
	@fpm install --prefix ~/.local
	@echo "$(GREEN)✓ Installed to ~/.local/bin$(NC)"
	@echo "  Make sure ~/.local/bin is in your PATH"

# ==============================================================================
# TARGETS DE DESENVOLVIMENTO
# ==============================================================================

# Verifica se há arquivos .f90u não sincronizados
check-sync:
	@echo "$(BLUE)━━━ Checking sync status$(NC)"
	@OUTDATED=0; \
	for f90u in $$(find src app test -name "*.f90u" 2>/dev/null); do \
		f90="$${f90u%.f90u}.f90"; \
		if [ ! -f "$$f90" ]; then \
			echo "  Missing: $$f90"; \
			OUTDATED=1; \
		elif [ "$$f90u" -nt "$$f90" ]; then \
			echo "  Outdated: $$f90"; \
			OUTDATED=1; \
		fi; \
	done; \
	if [ $$OUTDATED -eq 0 ]; then \
		echo "$(GREEN)✓ All files in sync$(NC)"; \
	else \
		echo "$(YELLOW)⚠ Run 'make sync' to update$(NC)"; \
		exit 1; \
	fi

# Mostra estatísticas do projeto
stats:
	@echo "$(BLUE)━━━ Project statistics$(NC)"
	@echo "Files:"
	@echo "  .f90u files: $$(find src app test -name "*.f90u" 2>/dev/null | wc -l)"
	@echo "  .f90 files:  $$(find src app test -name "*.f90" 2>/dev/null | wc -l)"
	@echo "  Modules:     $$(find src -name "*.f90" -o -name "*.f90u" 2>/dev/null | wc -l)"
	@echo ""
	@echo "Lines of code:"
	@find src app test -name "*.f90u" -o -name "*.f90" 2>/dev/null | \
		xargs wc -l 2>/dev/null | tail -n1 || echo "  0 total"

# Formata arquivos (placeholder para futuro formatador)
format:
	@echo "$(YELLOW)⚠ No Fortran formatter configured$(NC)"
	@echo "  Consider: fprettify, findent, or FORD"

# ==============================================================================
# TARGETS DE CI/CD
# ==============================================================================

# Pipeline completo de CI
ci: clean sync build test
	@echo "$(GREEN)✓ CI pipeline complete$(NC)"

# Verifica se nada foi esquecido
ci-check: check-sync
	@echo "$(BLUE)━━━ Checking for uncommitted changes$(NC)"
	@if git diff --quiet src app test; then \
		echo "$(GREEN)✓ No uncommitted changes$(NC)"; \
	else \
		echo "$(YELLOW)⚠ Uncommitted changes detected$(NC)"; \
		git status --short src app test; \
	fi

# ==============================================================================
# HELP
# ==============================================================================

help:
	@echo "$(BLUE)━━━ Available targets$(NC)"
	@echo ""
	@echo "Building:"
	@echo "  make build      - Translate .f90u and compile"
	@echo "  make run        - Translate, compile and run"
	@echo "  make test       - Translate, compile and test"
	@echo "  make sync       - Only translate .f90u → .f90"
	@echo ""
	@echo "Cleaning:"
	@echo "  make clean      - Remove build/ and generated .f90"
	@echo "  make clean-all  - Remove ALL .f90 files (careful!)"
	@echo ""
	@echo "Development:"
	@echo "  make install    - Install to ~/.local/bin"
	@echo "  make check-sync - Check if .f90u files need sync"
	@echo "  make stats      - Show project statistics"
	@echo ""
	@echo "CI/CD:"
	@echo "  make ci         - Run full CI pipeline"
	@echo "  make ci-check   - Check for uncommitted changes"
	@echo ""
	@echo "$(YELLOW)Tip:$(NC) Use 'make -j4 build' for parallel compilation"

# ==============================================================================
# CONFIGURAÇÃO
# ==============================================================================

# Força uso de bash
SHELL := /bin/bash

# Não deleta arquivos intermediários
.SECONDARY:

# Targets que não são arquivos
.PHONY: all build run test clean clean-all sync install \
        check-sync stats format ci ci-check help
