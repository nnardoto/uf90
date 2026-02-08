#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unicode Fortran Translator (Versão Refatorada)
===============================================

Este módulo traduz código Fortran com caracteres Unicode (principalmente letras
gregas e símbolos matemáticos) para ASCII puro e seguro antes da compilação.

Autor: Refatorado para melhor manutenibilidade
Licença: MIT
"""

import re
import sys
import argparse
from pathlib import Path
from typing import Dict, Tuple, Optional
from dataclasses import dataclass


# ============================================================================
# CONFIGURAÇÃO DE MAPEAMENTOS
# ============================================================================

@dataclass
class UnicodeMapping:
    """
    Representa um mapeamento de um caractere Unicode para ASCII.
    
    Attributes:
        unicode_char: O caractere Unicode original
        ascii_replacement: O substituto ASCII
        description: Descrição do caractere (para documentação)
    """
    unicode_char: str
    ascii_replacement: str
    description: str


class MappingRegistry:
    """
    Registro centralizado de todos os mapeamentos Unicode → ASCII.
    
    Esta classe organiza os mapeamentos por categoria e fornece acesso
    eficiente para operações de tradução.
    """
    
    def __init__(self):
        """Inicializa o registro com todos os mapeamentos suportados."""
        self._mappings: Dict[str, UnicodeMapping] = {}
        self._initialize_mappings()
    
    def _initialize_mappings(self):
        """Configura todos os mapeamentos suportados."""
        
        # Letras gregas minúsculas
        greek_lowercase = [
            ('α', 'alpha', 'alpha'),
            ('β', 'beta', 'beta'),
            ('γ', 'gamma', 'gamma'),
            ('δ', 'delta', 'delta'),
            ('ε', 'epsilon', 'epsilon'),
            ('ζ', 'zeta', 'zeta'),
            ('η', 'eta', 'eta'),
            ('θ', 'theta', 'theta'),
            ('ι', 'iota', 'iota'),
            ('κ', 'kappa', 'kappa'),
            ('λ', 'lambda', 'lambda'),
            ('μ', 'mu', 'mu'),
            ('ν', 'nu', 'nu'),
            ('ξ', 'xi', 'xi'),
            ('ο', 'omicron', 'omicron'),
            ('π', 'pi', 'pi'),
            ('ρ', 'rho', 'rho'),
            ('σ', 'sigma', 'sigma'),
            ('τ', 'tau', 'tau'),
            ('υ', 'upsilon', 'upsilon'),
            ('φ', 'phi', 'phi'),
            ('χ', 'chi', 'chi'),
            ('ψ', 'psi', 'psi'),
            ('ω', 'omega', 'omega'),
        ]
        
        # Letras gregas maiúsculas (prefixo uc_ = uppercase)
        greek_uppercase = [
            ('Α', 'uc_alpha', 'Alpha uppercase'),
            ('Β', 'uc_beta', 'Beta uppercase'),
            ('Γ', 'uc_gamma', 'Gamma uppercase'),
            ('Δ', 'uc_delta', 'Delta uppercase'),
            ('Ε', 'uc_epsilon', 'Epsilon uppercase'),
            ('Ζ', 'uc_zeta', 'Zeta uppercase'),
            ('Η', 'uc_eta', 'Eta uppercase'),
            ('Θ', 'uc_theta', 'Theta uppercase'),
            ('Ι', 'uc_iota', 'Iota uppercase'),
            ('Κ', 'uc_kappa', 'Kappa uppercase'),
            ('Λ', 'uc_lambda', 'Lambda uppercase'),
            ('Μ', 'uc_mu', 'Mu uppercase'),
            ('Ν', 'uc_nu', 'Nu uppercase'),
            ('Ξ', 'uc_xi', 'Xi uppercase'),
            ('Ο', 'uc_omicron', 'Omicron uppercase'),
            ('Π', 'uc_pi', 'Pi uppercase'),
            ('Ρ', 'uc_rho', 'Rho uppercase'),
            ('Σ', 'uc_sigma', 'Sigma uppercase'),
            ('Τ', 'uc_tau', 'Tau uppercase'),
            ('Υ', 'uc_upsilon', 'Upsilon uppercase'),
            ('Φ', 'uc_phi', 'Phi uppercase'),
            ('Χ', 'uc_chi', 'Chi uppercase'),
            ('Ψ', 'uc_psi', 'Psi uppercase'),
            ('Ω', 'uc_omega', 'Omega uppercase'),
        ]
        
        # Símbolos especiais Delta (existem dois codepoints Unicode diferentes)
        delta_symbols = [
            ('∆', 'uc_delta', 'Delta increment (U+2206)'),  # Operador incremento
        ]
        
        # Subscritos numéricos
        subscripts = [
            ('₀', '_0', 'subscript 0'),
            ('₁', '_1', 'subscript 1'),
            ('₂', '_2', 'subscript 2'),
            ('₃', '_3', 'subscript 3'),
            ('₄', '_4', 'subscript 4'),
            ('₅', '_5', 'subscript 5'),
            ('₆', '_6', 'subscript 6'),
            ('₇', '_7', 'subscript 7'),
            ('₈', '_8', 'subscript 8'),
            ('₉', '_9', 'subscript 9'),
        ]
        
        # Sobrescritos numéricos (prefixo _p = power/superscript)
        superscripts = [
            ('⁰', '_p0', 'superscript 0'),
            ('¹', '_p1', 'superscript 1'),
            ('²', '_p2', 'superscript 2'),
            ('³', '_p3', 'superscript 3'),
            ('⁴', '_p4', 'superscript 4'),
            ('⁵', '_p5', 'superscript 5'),
            ('⁶', '_p6', 'superscript 6'),
            ('⁷', '_p7', 'superscript 7'),
            ('⁸', '_p8', 'superscript 8'),
            ('⁹', '_p9', 'superscript 9'),
        ]
        
        # Operadores matemáticos (geralmente em comentários)
        math_operators = [
            ('×', '*', 'times'),
            ('÷', '/', 'divide'),
            ('±', '+/-', 'plus-minus'),
            ('∓', '-/+', 'minus-plus'),
            ('⋅', '*', 'dot product'),
            ('°', '_deg', 'degree'),
        ]
        
        # Símbolos relacionais
        relational_symbols = [
            ('≤', '<=', 'less or equal'),
            ('≥', '>=', 'greater or equal'),
            ('≠', '/=', 'not equal'),
            ('≈', '~', 'approximately'),
            ('∞', 'inf', 'infinity'),
        ]
        
        # Símbolos de cálculo
        calculus_symbols = [
            ('∂', 'd', 'partial derivative'),
            ('∇', 'grad', 'nabla/gradient'),
            ('√', 'sqrt', 'square root'),
        ]
        
        # Setas (principalmente para comentários)
        arrow_symbols = [
            ('→', '->', 'right arrow'),
            ('←', '<-', 'left arrow'),
            ('⇒', '=>', 'implies'),
            ('⇐', '<=', 'implied by'),
        ]
        
        # Registra todos os mapeamentos
        all_categories = [
            greek_lowercase, greek_uppercase, delta_symbols,
            subscripts, superscripts, math_operators,
            relational_symbols, calculus_symbols, arrow_symbols
        ]
        
        for category in all_categories:
            for unicode_char, ascii_rep, desc in category:
                mapping = UnicodeMapping(unicode_char, ascii_rep, desc)
                self._mappings[unicode_char] = mapping
    
    def get_mapping(self, unicode_char: str) -> Optional[UnicodeMapping]:
        """
        Retorna o mapeamento para um caractere Unicode.
        
        Args:
            unicode_char: O caractere Unicode a ser mapeado
            
        Returns:
            O UnicodeMapping correspondente ou None se não existir
        """
        return self._mappings.get(unicode_char)
    
    def get_all_unicode_chars(self) -> list[str]:
        """
        Retorna lista de todos os caracteres Unicode suportados.
        
        Returns:
            Lista ordenada por tamanho (decrescente) para evitar
            substituições parciais durante a tradução
        """
        return sorted(self._mappings.keys(), key=len, reverse=True)
    
    def get_ascii_replacement(self, unicode_char: str) -> Optional[str]:
        """
        Retorna apenas o substituto ASCII para um caractere.
        
        Args:
            unicode_char: O caractere Unicode
            
        Returns:
            O substituto ASCII ou None se não existir mapeamento
        """
        mapping = self.get_mapping(unicode_char)
        return mapping.ascii_replacement if mapping else None


# Instância global do registro de mapeamentos
MAPPING_REGISTRY = MappingRegistry()


# ============================================================================
# PROCESSAMENTO DE SUBSCRITOS COMPOSTOS
# ============================================================================

class SubscriptProcessor:
    """
    Processa sequências de subscritos Unicode compostos.
    
    Exemplo: α₁₂ → alpha_12 (não alpha_1_2)
    """
    
    # Mapeamento de subscritos Unicode para dígitos
    SUBSCRIPT_TO_DIGIT = {
        '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4',
        '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9'
    }
    
    # Padrão regex: captura [identificador][subscritos consecutivos]
    SUBSCRIPT_PATTERN = re.compile(r'([a-zA-Z_]+)([₀₁₂₃₄₅₆₇₈₉]+)')
    
    @classmethod
    def process(cls, text: str) -> str:
        """
        Substitui sequências de subscritos por underscores únicos.
        
        Args:
            text: Texto contendo possíveis subscritos
            
        Returns:
            Texto com subscritos processados
            
        Exemplo:
            >>> SubscriptProcessor.process("α₁₂")
            'α_12'
        """
        def replace_subscripts(match: re.Match) -> str:
            prefix = match.group(1)      # Ex: "U" ou "alpha"
            subscripts = match.group(2)   # Ex: "₁₂"
            
            # Converte cada subscrito para dígito
            digits = ''.join(
                cls.SUBSCRIPT_TO_DIGIT.get(char, char) 
                for char in subscripts
            )
            
            return f"{prefix}_{digits}"
        
        return cls.SUBSCRIPT_PATTERN.sub(replace_subscripts, text)


# ============================================================================
# TRADUTOR PRINCIPAL
# ============================================================================

class UnicodeTranslator:
    """
    Traduz código Fortran com Unicode para ASCII puro.
    
    Esta classe gerencia a lógica de tradução, preservando comentários
    opcionalmente e processando subscritos compostos corretamente.
    """
    
    # Padrão para detectar comentários Fortran
    COMMENT_PATTERN = re.compile(r'!')
    
    def __init__(self, preserve_comments: bool = True):
        """
        Inicializa o tradutor.
        
        Args:
            preserve_comments: Se True, mantém Unicode nos comentários
        """
        self.preserve_comments = preserve_comments
        self.registry = MAPPING_REGISTRY
    
    def translate(self, text: str) -> str:
        """
        Traduz o texto completo de Unicode para ASCII.
        
        Args:
            text: Código Fortran com Unicode
            
        Returns:
            Código traduzido para ASCII
        """
        if self.preserve_comments:
            return self._translate_with_comment_preservation(text)
        else:
            return self._translate_text(text)
    
    def _translate_with_comment_preservation(self, text: str) -> str:
        """
        Traduz o texto preservando Unicode em comentários.
        
        Args:
            text: Texto completo
            
        Returns:
            Texto com código traduzido e comentários preservados
        """
        lines = text.split('\n')
        translated_lines = []
        
        for line in lines:
            # Procura por comentário na linha
            comment_match = self.COMMENT_PATTERN.search(line)
            
            if comment_match:
                # Separa código e comentário
                comment_start = comment_match.start()
                code_part = line[:comment_start]
                comment_part = line[comment_start:]
                
                # Traduz apenas o código
                translated_code = self._translate_text(code_part)
                translated_lines.append(translated_code + comment_part)
            else:
                # Sem comentário, traduz tudo
                translated_lines.append(self._translate_text(line))
        
        return '\n'.join(translated_lines)
    
    def _translate_text(self, text: str) -> str:
        """
        Traduz todo o texto, substituindo Unicode por ASCII.
        
        O processo ocorre em duas etapas:
        1. Processa subscritos compostos (α₁₂ → alpha_12)
        2. Substitui caracteres Unicode individuais
        
        Args:
            text: Texto a ser traduzido
            
        Returns:
            Texto traduzido
        """
        # ETAPA 1: Processa subscritos compostos primeiro
        result = SubscriptProcessor.process(text)
        
        # ETAPA 2: Substitui caracteres individuais
        # Usa lista ordenada para evitar substituições parciais
        for unicode_char in self.registry.get_all_unicode_chars():
            ascii_replacement = self.registry.get_ascii_replacement(unicode_char)
            if ascii_replacement:
                result = result.replace(unicode_char, ascii_replacement)
        
        return result


# ============================================================================
# PROCESSAMENTO DE ARQUIVOS
# ============================================================================

class FileProcessor:
    """
    Gerencia o processamento de arquivos Fortran.
    
    Lida com leitura, tradução e escrita de arquivos, determinando
    automaticamente nomes de saída apropriados.
    """
    
    def __init__(self, translator: UnicodeTranslator, verbose: bool = False):
        """
        Inicializa o processador de arquivos.
        
        Args:
            translator: Instância do tradutor a ser usado
            verbose: Se True, mostra informações detalhadas
        """
        self.translator = translator
        self.verbose = verbose
    
    def process_file(
        self, 
        input_path: str, 
        output_path: Optional[str] = None
    ) -> str:
        """
        Processa um arquivo Fortran completo.
        
        Args:
            input_path: Caminho do arquivo de entrada
            output_path: Caminho do arquivo de saída (opcional)
            
        Returns:
            Caminho do arquivo gerado
            
        Raises:
            FileNotFoundError: Se o arquivo de entrada não existir
        """
        input_file = Path(input_path)
        
        if not input_file.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {input_path}")
        
        # Determina arquivo de saída
        output_file = self._determine_output_path(input_file, output_path)
        
        # Processa arquivo
        if self.verbose:
            print(f"[+] Lendo: {input_file}")
        
        # Lê conteúdo
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Traduz
        translated = self.translator.translate(content)
        
        # Escreve resultado
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(translated)
        
        if self.verbose:
            self._print_statistics(content, output_file)
        
        return str(output_file)
    
    def _determine_output_path(
        self, 
        input_file: Path, 
        output_path: Optional[str]
    ) -> Path:
        """
        Determina o caminho do arquivo de saída.
        
        Args:
            input_file: Arquivo de entrada
            output_path: Caminho explícito (se fornecido)
            
        Returns:
            Path do arquivo de saída
        """
        if output_path:
            return Path(output_path)
        
        # Se já é .f90, adiciona .translated
        if input_file.suffix == '.f90':
            return input_file.with_stem(input_file.stem + '.translated')
        
        # Caso contrário, substitui extensão por .f90
        return input_file.with_suffix('.f90')
    
    def _print_statistics(self, original_content: str, output_file: Path):
        """
        Imprime estatísticas sobre a tradução.
        
        Args:
            original_content: Conteúdo original do arquivo
            output_file: Caminho do arquivo gerado
        """
        unicode_count = sum(
            original_content.count(char) 
            for char in MAPPING_REGISTRY.get_all_unicode_chars()
        )
        
        print(f"[✓] Arquivo salvo: {output_file}")
        
        if unicode_count > 0:
            print(f"[i] Caracteres Unicode traduzidos: {unicode_count}")
        else:
            print(f"[i] Nenhum caractere Unicode encontrado")


# ============================================================================
# UTILITÁRIOS
# ============================================================================

class MappingTableGenerator:
    """Gera tabelas de referência dos mapeamentos."""
    
    @staticmethod
    def generate_table(output_file: Optional[str] = None) -> str:
        """
        Gera arquivo com tabela de mapeamento para referência.
        
        Args:
            output_file: Caminho do arquivo de saída
            
        Returns:
            Caminho do arquivo gerado
        """
        if output_file is None:
            output_file = 'unicode_mapping.txt'
        
        output_path = Path(output_file)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Unicode to ASCII Mapping Table\n")
            f.write("# Para uso em código Fortran\n")
            f.write("# Gerado automaticamente\n\n")
            
            # Categorias de mapeamentos
            categories = {
                'Letras gregas minúsculas': [
                    'α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'ι', 'κ', 
                    'λ', 'μ', 'ν', 'ξ', 'ο', 'π', 'ρ', 'σ', 'τ', 'υ', 
                    'φ', 'χ', 'ψ', 'ω'
                ],
                'Letras gregas maiúsculas': [
                    'Α', 'Β', 'Γ', 'Δ', 'Ε', 'Ζ', 'Η', 'Θ', 'Ι', 'Κ',
                    'Λ', 'Μ', 'Ν', 'Ξ', 'Ο', 'Π', 'Ρ', 'Σ', 'Τ', 'Υ',
                    'Φ', 'Χ', 'Ψ', 'Ω'
                ],
                'Símbolo Delta especial': ['∆'],
                'Subscritos numéricos': ['₀', '₁', '₂', '₃', '₄', '₅', '₆', '₇', '₈', '₉'],
                'Sobrescritos numéricos': ['⁰', '¹', '²', '³', '⁴', '⁵', '⁶', '⁷', '⁸', '⁹'],
                'Operadores matemáticos': ['×', '÷', '±', '∓', '⋅', '°'],
                'Símbolos relacionais': ['≤', '≥', '≠', '≈', '∞'],
                'Símbolos de cálculo': ['∂', '∇', '√'],
                'Setas': ['→', '←', '⇒', '⇐'],
            }
            
            for category_name, chars in categories.items():
                f.write(f"\n## {category_name}\n")
                f.write("-" * 60 + "\n")
                
                for char in chars:
                    mapping = MAPPING_REGISTRY.get_mapping(char)
                    if mapping:
                        f.write(
                            f"{mapping.unicode_char:3s} → "
                            f"{mapping.ascii_replacement:15s} "
                            f"({mapping.description})\n"
                        )
        
        print(f"[✓] Tabela de mapeamento salva: {output_path}")
        return str(output_path)


# ============================================================================
# INTERFACE DE LINHA DE COMANDO
# ============================================================================

def create_argument_parser() -> argparse.ArgumentParser:
    """
    Cria o parser de argumentos da linha de comando.
    
    Returns:
        ArgumentParser configurado
    """
    parser = argparse.ArgumentParser(
        description='Traduz código Fortran com Unicode para ASCII seguro',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  %(prog)s meu_codigo.f90u                  # Gera meu_codigo.f90
  %(prog)s input.f90u -o output.f90         # Especifica saída
  %(prog)s codigo.f90 --no-preserve         # Traduz também comentários
  %(prog)s --generate-table                 # Gera tabela de referência
  %(prog)s --verbose arquivo.f90u           # Modo verboso
        """
    )
    
    parser.add_argument(
        'input_file',
        nargs='?',
        help='Arquivo Fortran com Unicode (.f90u, .f90, etc)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Arquivo de saída (padrão: mesmo nome com .f90)'
    )
    
    parser.add_argument(
        '--no-preserve',
        action='store_true',
        help='Traduz Unicode também nos comentários'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Mostra informações detalhadas durante o processamento'
    )
    
    parser.add_argument(
        '--generate-table',
        action='store_true',
        help='Gera arquivo de referência com todos os mapeamentos'
    )
    
    return parser


def main() -> int:
    """
    Função principal da interface de linha de comando.
    
    Returns:
        Código de saída (0 = sucesso, 1 = erro)
    """
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Gera tabela se solicitado
    if args.generate_table:
        try:
            MappingTableGenerator.generate_table()
            return 0
        except Exception as e:
            print(f"[✗] Erro ao gerar tabela: {e}", file=sys.stderr)
            return 1
    
    # Requer arquivo de entrada
    if not args.input_file:
        parser.print_help()
        return 1
    
    # Processa arquivo
    try:
        translator = UnicodeTranslator(
            preserve_comments=not args.no_preserve
        )
        processor = FileProcessor(translator, verbose=args.verbose)
        
        output_path = processor.process_file(args.input_file, args.output)
        
        if not args.verbose:
            print(f"[✓] Tradução concluída: {output_path}")
        
        return 0
        
    except FileNotFoundError as e:
        print(f"[✗] {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"[✗] Erro: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
