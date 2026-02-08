! ============================================================================
! Módulo: uf90_translation_rules
! ============================================================================
! Implementa as regras de tradução de identificadores Unicode para ASCII.
!
! Este módulo contém:
! - Mapeamentos de letras gregas (minúsculas e maiúsculas)
! - Validação de identificadores reservados
! - Lógica de inserção automática de underscores
! - Funções auxiliares para processamento de strings
!
! Convenções de tradução:
! - Letras gregas minúsculas: α → alpha
! - Letras gregas maiúsculas: Α → uc_alpha (prefixo uc_ = uppercase)
! - Delta especial: ∆ (U+2206) e Δ (U+0394) → uc_delta
! ============================================================================

module uf90_translation_rules
  use stdlib_strings, only : replace_all
  implicit none
  
  ! Torna apenas as interfaces públicas visíveis
  private
  public :: translate_identifier
  public :: check_reserved_ascii_token
  
  ! ==========================================================================
  ! TABELA DE NOMES GREGOS
  ! ==========================================================================
  ! Array de nomes das letras gregas em ordem alfabética.
  ! Usado para validação de identificadores reservados.
  !
  ! GNAME_LEN = 8 é suficiente para o nome mais longo ("epsilon", "upsilon")
  ! ==========================================================================
  integer, parameter :: GNAME_LEN = 8
  
  character(len=GNAME_LEN), parameter :: GREEK_NAMES(24) = [ &
    character(len=GNAME_LEN) :: &
    "alpha   ", "beta    ", "gamma   ", "delta   ", &
    "epsilon ", "zeta    ", "eta     ", "theta   ", &
    "iota    ", "kappa   ", "lambda  ", "mu      ", &
    "nu      ", "xi      ", "omicron ", "pi      ", &
    "rho     ", "sigma   ", "tau     ", "upsilon ", &
    "phi     ", "chi     ", "psi     ", "omega   " &
  ]

contains

  ! ==========================================================================
  ! FUNÇÃO: translate_identifier
  ! ==========================================================================
  ! Traduz um identificador Unicode para ASCII válido em Fortran.
  !
  ! Algoritmo:
  ! 1. Percorre o identificador caractere por caractere
  ! 2. Quando encontra letra grega, substitui pelo nome ASCII
  ! 3. Insere underscores automaticamente quando necessário para evitar
  !    colisão sintática (ex: "αβ" → "alpha_beta")
  !
  ! Parâmetros:
  !   ident : Identificador original (pode conter Unicode)
  !
  ! Retorna:
  !   Identificador traduzido para ASCII puro
  !
  ! Exemplos:
  !   α       → alpha
  !   Δ       → uc_delta
  !   αβ      → alpha_beta
  !   var_α   → var_alpha
  !   α_max   → alpha_max
  ! ==========================================================================
  function translate_identifier(ident) result(out)
    character(len=*), intent(in) :: ident
    character(len=:), allocatable :: out
    
    ! Variáveis de controle do loop
    integer :: i, n
    
    ! Acumulador para o identificador traduzido
    character(len=:), allocatable :: acc
    
    ! String de substituição para letra grega encontrada
    character(len=:), allocatable :: greek_replacement
    
    ! Caracteres vizinhos (para análise de contexto)
    character(len=1) :: prev_char, next_char
    
    ! Comprimento da chave Unicode encontrada
    integer :: key_length
    
    ! Inicializa acumulador vazio
    acc = ""
    n = len_trim(ident)
    i = 1
    
    ! Loop principal: processa cada posição do identificador
    do while (i <= n)
      
      ! Tenta encontrar letra grega na posição atual
      if (match_greek_at(ident, i, greek_replacement, key_length)) then
        
        ! === ANÁLISE DE CONTEXTO: Inserção automática de underscores ===
        !
        ! Underscores são necessários para separar:
        ! 1. Letras ASCII adjacentes de nomes gregos
        ! 2. Múltiplos nomes gregos consecutivos
        !
        ! Exemplos:
        !   "αx"  precisa virar "alpha_x"  (não "alphax")
        !   "xα"  precisa virar "x_alpha"  (não "xalpha")
        !   "αβ"  precisa virar "alpha_beta" (não "alphabeta")
        
        ! Inicializa caracteres vizinhos
        prev_char = achar(0)  ! null char (indica início de string)
        next_char = achar(0)  ! null char (indica fim de string)
        
        ! Pega caractere anterior se existir
        if (i > 1) prev_char = ident(i-1:i-1)
        
        ! Pega caractere seguinte se existir
        if (i + key_length <= n) next_char = ident(i+key_length:i+key_length)
        
        ! --- Undercore ANTES (se necessário) ---
        ! Insere underscore se:
        ! - Há um caractere anterior que é letra/underscore
        ! - E o acumulador não termina com underscore já
        if (needs_underscore_neighbor(prev_char)) then
          if (len(acc) > 0) then
            if (acc(len(acc):len(acc)) /= "_") then
              acc = acc // "_"
            end if
          end if
        end if
        
        ! --- Adiciona o nome grego ---
        acc = acc // greek_replacement
        
        ! --- Underscore DEPOIS (se necessário) ---
        ! Insere underscore se o próximo caractere é letra/underscore
        if (needs_underscore_neighbor(next_char)) then
          acc = acc // "_"
        end if
        
        ! Avança para depois da letra grega
        i = i + key_length
        
      else
        ! Não é letra grega, copia caractere normalmente
        acc = acc // ident(i:i)
        i = i + 1
      end if
      
    end do
    
    ! Retorna identificador traduzido
    out = acc
    
  end function translate_identifier

  ! ==========================================================================
  ! FUNÇÃO: match_greek_at
  ! ==========================================================================
  ! Tenta encontrar uma letra grega Unicode na posição especificada.
  !
  ! Parâmetros:
  !   s      : String sendo analisada
  !   pos    : Posição atual na string
  !   repl   : [OUT] Nome ASCII da letra grega encontrada
  !   keylen : [OUT] Número de bytes da letra grega Unicode
  !
  ! Retorna:
  !   .true.  se encontrou letra grega
  !   .false. caso contrário
  !
  ! Notas:
  ! - Verifica primeiro letras especiais (Delta com dois codepoints)
  ! - Depois maiúsculas (prefixo uc_)
  ! - Por fim minúsculas (sem prefixo)
  ! ==========================================================================
  logical function match_greek_at(s, pos, repl, keylen)
    character(len=*), intent(in) :: s
    integer, intent(in) :: pos
    character(len=:), allocatable, intent(out) :: repl
    integer, intent(out) :: keylen
    
    ! Assume sucesso (será alterado se não encontrar nada)
    match_greek_at = .true.
    
    ! ========================================================================
    ! SÍMBOLOS ESPECIAIS: Delta
    ! ========================================================================
    ! Existem dois codepoints Unicode diferentes para Delta:
    ! - Δ (U+0394): Letra grega maiúscula Delta
    ! - ∆ (U+2206): Operador de incremento Delta
    ! Ambos são traduzidos para "uc_delta"
    ! ========================================================================
    
    if (starts_with(s, pos, "∆")) then
      repl = "uc_delta"
      keylen = len("∆")
      return
    end if
    
    if (starts_with(s, pos, "Δ")) then
      repl = "uc_delta"
      keylen = len("Δ")
      return
    end if
    
    ! ========================================================================
    ! LETRAS GREGAS MAIÚSCULAS
    ! ========================================================================
    ! Convenção: Prefixo "uc_" (uppercase) para distinguir de minúsculas
    ! Exemplo: Α → uc_alpha (diferente de α → alpha)
    ! ========================================================================
    
    if (starts_with(s, pos, "Α")) then; repl="uc_alpha";   keylen=len("Α"); return; end if
    if (starts_with(s, pos, "Β")) then; repl="uc_beta";    keylen=len("Β"); return; end if
    if (starts_with(s, pos, "Γ")) then; repl="uc_gamma";   keylen=len("Γ"); return; end if
    if (starts_with(s, pos, "Ε")) then; repl="uc_epsilon"; keylen=len("Ε"); return; end if
    if (starts_with(s, pos, "Ζ")) then; repl="uc_zeta";    keylen=len("Ζ"); return; end if
    if (starts_with(s, pos, "Η")) then; repl="uc_eta";     keylen=len("Η"); return; end if
    if (starts_with(s, pos, "Θ")) then; repl="uc_theta";   keylen=len("Θ"); return; end if
    if (starts_with(s, pos, "Ι")) then; repl="uc_iota";    keylen=len("Ι"); return; end if
    if (starts_with(s, pos, "Κ")) then; repl="uc_kappa";   keylen=len("Κ"); return; end if
    if (starts_with(s, pos, "Λ")) then; repl="uc_lambda";  keylen=len("Λ"); return; end if
    if (starts_with(s, pos, "Μ")) then; repl="uc_mu";      keylen=len("Μ"); return; end if
    if (starts_with(s, pos, "Ν")) then; repl="uc_nu";      keylen=len("Ν"); return; end if
    if (starts_with(s, pos, "Ξ")) then; repl="uc_xi";      keylen=len("Ξ"); return; end if
    if (starts_with(s, pos, "Ο")) then; repl="uc_omicron"; keylen=len("Ο"); return; end if
    if (starts_with(s, pos, "Π")) then; repl="uc_pi";      keylen=len("Π"); return; end if
    if (starts_with(s, pos, "Ρ")) then; repl="uc_rho";     keylen=len("Ρ"); return; end if
    if (starts_with(s, pos, "Σ")) then; repl="uc_sigma";   keylen=len("Σ"); return; end if
    if (starts_with(s, pos, "Τ")) then; repl="uc_tau";     keylen=len("Τ"); return; end if
    if (starts_with(s, pos, "Υ")) then; repl="uc_upsilon"; keylen=len("Υ"); return; end if
    if (starts_with(s, pos, "Φ")) then; repl="uc_phi";     keylen=len("Φ"); return; end if
    if (starts_with(s, pos, "Χ")) then; repl="uc_chi";     keylen=len("Χ"); return; end if
    if (starts_with(s, pos, "Ψ")) then; repl="uc_psi";     keylen=len("Ψ"); return; end if
    if (starts_with(s, pos, "Ω")) then; repl="uc_omega";   keylen=len("Ω"); return; end if
    
    ! ========================================================================
    ! LETRAS GREGAS MINÚSCULAS
    ! ========================================================================
    ! Sem prefixo: α → alpha, β → beta, etc.
    ! ========================================================================
    
    if (starts_with(s, pos, "α")) then; repl="alpha";   keylen=len("α"); return; end if
    if (starts_with(s, pos, "β")) then; repl="beta";    keylen=len("β"); return; end if
    if (starts_with(s, pos, "γ")) then; repl="gamma";   keylen=len("γ"); return; end if
    if (starts_with(s, pos, "δ")) then; repl="delta";   keylen=len("δ"); return; end if
    if (starts_with(s, pos, "ε")) then; repl="epsilon"; keylen=len("ε"); return; end if
    if (starts_with(s, pos, "ζ")) then; repl="zeta";    keylen=len("ζ"); return; end if
    if (starts_with(s, pos, "η")) then; repl="eta";     keylen=len("η"); return; end if
    if (starts_with(s, pos, "θ")) then; repl="theta";   keylen=len("θ"); return; end if
    if (starts_with(s, pos, "ι")) then; repl="iota";    keylen=len("ι"); return; end if
    if (starts_with(s, pos, "κ")) then; repl="kappa";   keylen=len("κ"); return; end if
    if (starts_with(s, pos, "λ")) then; repl="lambda";  keylen=len("λ"); return; end if
    if (starts_with(s, pos, "μ")) then; repl="mu";      keylen=len("μ"); return; end if
    if (starts_with(s, pos, "ν")) then; repl="nu";      keylen=len("ν"); return; end if
    if (starts_with(s, pos, "ξ")) then; repl="xi";      keylen=len("ξ"); return; end if
    if (starts_with(s, pos, "ο")) then; repl="omicron"; keylen=len("ο"); return; end if
    if (starts_with(s, pos, "π")) then; repl="pi";      keylen=len("π"); return; end if
    if (starts_with(s, pos, "ρ")) then; repl="rho";     keylen=len("ρ"); return; end if
    if (starts_with(s, pos, "σ")) then; repl="sigma";   keylen=len("σ"); return; end if
    if (starts_with(s, pos, "τ")) then; repl="tau";     keylen=len("τ"); return; end if
    if (starts_with(s, pos, "υ")) then; repl="upsilon"; keylen=len("υ"); return; end if
    if (starts_with(s, pos, "φ")) then; repl="phi";     keylen=len("φ"); return; end if
    if (starts_with(s, pos, "χ")) then; repl="chi";     keylen=len("χ"); return; end if
    if (starts_with(s, pos, "ψ")) then; repl="psi";     keylen=len("ψ"); return; end if
    if (starts_with(s, pos, "ω")) then; repl="omega";   keylen=len("ω"); return; end if
    
    ! Nenhuma letra grega encontrada
    match_greek_at = .false.
    repl = ""
    keylen = 0
    
  end function match_greek_at

  ! ==========================================================================
  ! SUBROTINA: check_reserved_ascii_token
  ! ==========================================================================
  ! Verifica se um token ASCII é um identificador reservado.
  !
  ! Identificadores reservados são os nomes gerados pela tradução:
  ! - "alpha", "beta", ..., "omega"
  ! - "uc_alpha", "uc_beta", ..., "uc_omega"
  !
  ! Se um usuário tentar usar esses nomes diretamente em código .uf90,
  ! causaria ambiguidade (não saberíamos se é letra grega ou nome ASCII).
  ! Portanto, rejeitamos esses identificadores explicitamente.
  !
  ! Parâmetros:
  !   tok : Token a ser verificado
  !   ok  : [OUT] .true. se o token é permitido, .false. se é reservado
  ! ==========================================================================
  subroutine check_reserved_ascii_token(tok, ok)
    character(len=*), intent(in) :: tok
    logical, intent(out) :: ok
    
    ! Token é válido se NÃO for reservado
    ok = .not. is_reserved(tok)
    
  end subroutine check_reserved_ascii_token

  ! ==========================================================================
  ! FUNÇÃO: is_reserved (PRIVADA)
  ! ==========================================================================
  ! Verifica se um nome é reservado (usado na tradução de letras gregas).
  !
  ! Parâmetros:
  !   name : Nome a ser verificado
  !
  ! Retorna:
  !   .true. se o nome é reservado
  ! ==========================================================================
  pure logical function is_reserved(name)
    character(len=*), intent(in) :: name
    integer :: i
    character(len=:), allocatable :: normalized_name
    
    ! Normaliza para lowercase para comparação case-insensitive
    normalized_name = to_lower_ascii(trim(name))
    
    is_reserved = .false.
    
    ! Verifica contra todos os nomes gregos
    do i = 1, size(GREEK_NAMES)
      
      ! Verifica nome minúscula (ex: "alpha")
      if (normalized_name == trim(GREEK_NAMES(i))) then
        is_reserved = .true.
        return
      end if
      
      ! Verifica nome maiúscula (ex: "uc_alpha")
      if (normalized_name == trim("uc_"//GREEK_NAMES(i))) then
        is_reserved = .true.
        return
      end if
      
    end do
    
  end function is_reserved

  ! ==========================================================================
  ! FUNÇÃO: to_lower_ascii (PRIVADA)
  ! ==========================================================================
  ! Converte string ASCII para minúsculas.
  !
  ! Nota: Apenas caracteres ASCII são convertidos (A-Z → a-z).
  !       Caracteres Unicode são preservados.
  ! ==========================================================================
  pure function to_lower_ascii(s) result(out)
    character(len=*), intent(in) :: s
    character(len=len(s)) :: out
    integer :: i, char_code
    
    out = s
    
    do i = 1, len(s)
      char_code = iachar(out(i:i))
      
      ! Se é maiúscula ASCII (A-Z), converte para minúscula
      if (char_code >= iachar('A') .and. char_code <= iachar('Z')) then
        out(i:i) = achar(char_code + 32)  ! Diferença entre 'A' e 'a'
      end if
    end do
    
  end function to_lower_ascii

  ! ==========================================================================
  ! FUNÇÃO: needs_underscore_neighbor (PRIVADA)
  ! ==========================================================================
  ! Determina se um caractere requer underscore como separador.
  !
  ! Retorna .true. para:
  ! - Letras ASCII (a-z, A-Z)
  ! - Underscore (_)
  !
  ! Parâmetros:
  !   ch : Caractere a ser verificado
  !
  ! Retorna:
  !   .true. se precisa de underscore como vizinho
  ! ==========================================================================
  pure logical function needs_underscore_neighbor(ch)
    character(len=1), intent(in) :: ch
    integer :: char_code
    
    char_code = iachar(ch)
    
    ! É letra ASCII maiúscula, minúscula ou underscore
    needs_underscore_neighbor = &
      (char_code >= iachar('A') .and. char_code <= iachar('Z')) .or. &
      (char_code >= iachar('a') .and. char_code <= iachar('z')) .or. &
      (char_code == iachar('_'))
      
  end function needs_underscore_neighbor

  ! ==========================================================================
  ! FUNÇÃO: starts_with (PRIVADA)
  ! ==========================================================================
  ! Verifica se uma string começa com determinada chave na posição dada.
  !
  ! Parâmetros:
  !   s   : String sendo analisada
  !   pos : Posição onde verificar
  !   key : Chave a ser procurada
  !
  ! Retorna:
  !   .true. se s[pos:pos+len(key)-1] == key
  ! ==========================================================================
  pure logical function starts_with(s, pos, key)
    character(len=*), intent(in) :: s, key
    integer, intent(in) :: pos
    integer :: str_len, key_len
    
    str_len = len_trim(s)
    key_len = len(key)
    
    ! Verifica se há espaço suficiente
    if (pos + key_len - 1 > str_len) then
      starts_with = .false.
    else
      ! Compara substring com a chave
      starts_with = (s(pos:pos+key_len-1) == key)
    end if
    
  end function starts_with

end module uf90_translation_rules
