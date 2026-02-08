! ============================================================================
! Módulo: uf90_file_translator
! ============================================================================
! Implementa a tradução completa de arquivos .uf90 para .f90.
!
! Este módulo contém:
! - Lógica de tradução linha por linha
! - Validação de identificadores reservados
! - Parsing de strings e comentários
! - Proteção contra sobrescrita de arquivos manuais
! ============================================================================

module uf90_file_translator
  use stdlib_io,              only : open, get_line
  use stdlib_system,          only : is_file
  use uf90_constants,         only : GEN_MARKER
  use uf90_translation_rules, only : translate_identifier, &
                                      check_reserved_ascii_token
  implicit none
  
  private
  public :: translate_file

contains

  ! ==========================================================================
  ! SUBROTINA: translate_file
  ! ==========================================================================
  ! Traduz um arquivo .uf90 completo para .f90.
  !
  ! Processo:
  ! 1. Se .f90 existe, verifica se foi gerado (proteção contra sobrescrita)
  ! 2. Abre ambos os arquivos
  ! 3. Escreve marcador de geração automática
  ! 4. Processa linha por linha:
  !    a. Valida identificadores ASCII (não podem ser reservados)
  !    b. Traduz identificadores Unicode
  ! 5. Fecha arquivos
  !
  ! Parâmetros:
  !   uf90_path : Arquivo fonte .uf90
  !   f90_path  : Arquivo destino .f90
  !   ec        : [OUT] Código de erro (0 = sucesso, 2 = erro)
  ! ==========================================================================
  subroutine translate_file(uf90_path, f90_path, ec)
    character(len=*), intent(in) :: uf90_path, f90_path
    integer, intent(out) :: ec
    
    integer :: input_unit, output_unit, io_status
    character(len=:), allocatable :: line, translated_line
    character(len=4096) :: first_line_buffer
    
    ec = 0
    
    ! === ETAPA 1: Proteção contra sobrescrita ===
    ! Se .f90 existe e não foi gerado por nós, recusa sobrescrever
    if (is_file(f90_path)) then
      call read_first_line(f90_path, first_line_buffer)
      
      if (trim(first_line_buffer) /= GEN_MARKER) then
        write(*,'(a)') "[uf90] ERRO: recusando sobrescrever .f90 nao-gerado:"
        write(*,'(a)') "       " // trim(f90_path)
        write(*,'(a)') "       (primeira linha nao tem marcador de geracao)"
        ec = 2
        return
      end if
    end if
    
    ! === ETAPA 2: Abre arquivos ===
    
    input_unit = open(uf90_path, "r", iostat=io_status)
    if (io_status /= 0) then
      write(*,'(a)') "[uf90] ERRO: nao consegui abrir para leitura:"
      write(*,'(a)') "       " // trim(uf90_path)
      ec = 2
      return
    end if
    
    output_unit = open(f90_path, "w", iostat=io_status)
    if (io_status /= 0) then
      write(*,'(a)') "[uf90] ERRO: nao consegui abrir para escrita:"
      write(*,'(a)') "       " // trim(f90_path)
      close(input_unit)
      ec = 2
      return
    end if
    
    ! === ETAPA 3: Escreve cabeçalho no .f90 ===
    
    write(output_unit,'(a)') GEN_MARKER
    write(output_unit,'(a)') "! SOURCE: " // trim(uf90_path)
    write(output_unit,'(a)') ""  ! Linha em branco para legibilidade
    
    ! === ETAPA 4: Processa linha por linha ===
    
    do
      ! Lê próxima linha do .uf90
      call get_line(input_unit, line, iostat=io_status)
      if (io_status /= 0) exit  ! EOF ou erro
      
      ! Valida que não usa identificadores reservados
      call validate_no_reserved_identifiers(line, uf90_path, ec)
      if (ec /= 0) exit  ! Erro de validação
      
      ! Traduz Unicode para ASCII
      translated_line = translate_line(line)
      
      ! Escreve linha traduzida
      write(output_unit,'(a)') trim(translated_line)
    end do
    
    ! === ETAPA 5: Fecha arquivos ===
    
    close(input_unit)
    close(output_unit)
    
  end subroutine translate_file

  ! ==========================================================================
  ! SUBROTINA: validate_no_reserved_identifiers
  ! ==========================================================================
  ! Valida que uma linha não contém identificadores ASCII reservados.
  !
  ! Identificadores reservados são: alpha, beta, ..., uc_alpha, uc_beta, ...
  ! Estes são gerados pela tradução, então não podem aparecer no .uf90.
  !
  ! IMPORTANTE: Esta função implementa parsing completo de Fortran para:
  ! - Ignorar conteúdo dentro de strings ('...' ou "...")
  ! - Ignorar comentários (! ...)
  ! - Detectar corretamente identificadores
  !
  ! AVISO CRÍTICO DE FORTRAN:
  ! Fortran NÃO garante avaliação short-circuit de .and./.or.
  ! Portanto, NUNCA escreva:
  !   if (j <= n .and. line(j:j) == 'x')  ! PERIGOSO!
  ! Pois line(j:j) pode ser avaliado mesmo se j > n (erro de runtime)
  !
  ! Parâmetros:
  !   line      : Linha a ser validada
  !   file_path : Caminho do arquivo (para mensagens de erro)
  !   ec        : [OUT] Código de erro (0 = OK, 2 = erro)
  ! ==========================================================================
  subroutine validate_no_reserved_identifiers(line, file_path, ec)
    character(len=*), intent(in) :: line, file_path
    integer, intent(out) :: ec
    
    integer :: i, line_length, token_end
    logical :: inside_single_quote, inside_double_quote
    character(len=:), allocatable :: token
    logical :: token_is_valid
    
    ec = 0
    inside_single_quote = .false.
    inside_double_quote = .false.
    line_length = len(line)
    i = 1
    
    ! Percorre linha caractere por caractere
    do while (i <= line_length)
      
      ! === Detecta comentário (fora de strings) ===
      if (.not. inside_single_quote .and. .not. inside_double_quote) then
        if (line(i:i) == "!") then
          ! Resto da linha é comentário, pode parar
          exit
        end if
      end if
      
      ! === Detecta aspas simples ===
      if (.not. inside_double_quote .and. line(i:i) == "'") then
        inside_single_quote = .not. inside_single_quote
        i = i + 1
        cycle
      end if
      
      ! === Detecta aspas duplas ===
      if (.not. inside_single_quote .and. line(i:i) == '"') then
        inside_double_quote = .not. inside_double_quote
        i = i + 1
        cycle
      end if
      
      ! === Processa identificadores (fora de strings) ===
      if (.not. inside_single_quote .and. .not. inside_double_quote) then
        
        if (is_ascii_identifier_start(line(i:i))) then
          ! Início de identificador, encontra onde termina
          token_end = i + 1
          
          ! Avança enquanto for parte de identificador
          ! SEGURO: verifica bounds antes de acessar line(j:j)
          do while (token_end <= line_length)
            if (.not. is_ascii_identifier_body(line(token_end:token_end))) exit
            token_end = token_end + 1
          end do
          
          ! Extrai token (usa min para garantir que não passa do fim)
          token = line(i:min(token_end-1, line_length))
          
          ! Valida token
          call check_reserved_ascii_token(token, token_is_valid)
          
          if (.not. token_is_valid) then
            write(*,'(a)') "[uf90] ERRO: identificador ASCII reservado usado em:"
            write(*,'(a)') "       " // trim(file_path)
            write(*,'(a)') "       Token: " // trim(token)
            write(*,'(a)') ""
            write(*,'(a)') "       Identificadores reservados: alpha, beta, ..., omega,"
            write(*,'(a)') "       uc_alpha, uc_beta, ..., uc_omega"
            write(*,'(a)') "       Use letras gregas Unicode no .uf90 ao invés de nomes ASCII"
            ec = 2
            return
          end if
          
          ! Avança para depois do token
          i = token_end
          cycle
        end if
      end if
      
      ! Próximo caractere
      i = i + 1
    end do
    
  end subroutine validate_no_reserved_identifiers

  ! ==========================================================================
  ! FUNÇÃO: translate_line
  ! ==========================================================================
  ! Traduz uma linha completa, convertendo identificadores Unicode.
  !
  ! Preserva:
  ! - Strings literais ('...' e "...")
  ! - Comentários (! ...)
  !
  ! Traduz apenas identificadores fora de strings/comentários.
  !
  ! Parâmetros:
  !   line : Linha original com possível Unicode
  !
  ! Retorna:
  !   Linha traduzida (ASCII puro)
  ! ==========================================================================
  function translate_line(line) result(out)
    character(len=*), intent(in) :: line
    character(len=:), allocatable :: out
    
    integer :: i, line_length, identifier_end
    logical :: inside_single_quote, inside_double_quote
    character(len=:), allocatable :: accumulator, identifier
    
    accumulator = ""
    inside_single_quote = .false.
    inside_double_quote = .false.
    line_length = len(line)
    i = 1
    
    ! Processa linha caractere por caractere
    do while (i <= line_length)
      
      ! === Detecta comentário (preserva Unicode) ===
      if (.not. inside_single_quote .and. .not. inside_double_quote) then
        if (line(i:i) == "!") then
          ! Resto da linha é comentário, copia sem traduzir
          accumulator = accumulator // line(i:line_length)
          exit
        end if
      end if
      
      ! === Detecta e preserva aspas simples ===
      if (.not. inside_double_quote .and. line(i:i) == "'") then
        inside_single_quote = .not. inside_single_quote
        accumulator = accumulator // line(i:i)
        i = i + 1
        cycle
      end if
      
      ! === Detecta e preserva aspas duplas ===
      if (.not. inside_single_quote .and. line(i:i) == '"') then
        inside_double_quote = .not. inside_double_quote
        accumulator = accumulator // line(i:i)
        i = i + 1
        cycle
      end if
      
      ! === Traduz identificadores (fora de strings/comentários) ===
      if (.not. inside_single_quote .and. .not. inside_double_quote) then
        
        if (is_identifier_start(line(i:i))) then
          ! Início de identificador, encontra onde termina
          identifier_end = i + 1
          
          do while (identifier_end <= line_length)
            if (.not. is_identifier_body(line(identifier_end:identifier_end))) exit
            identifier_end = identifier_end + 1
          end do
          
          ! Extrai identificador
          identifier = line(i:min(identifier_end-1, line_length))
          
          ! Traduz e adiciona ao acumulador
          accumulator = accumulator // translate_identifier(identifier)
          
          ! Avança para depois do identificador
          i = identifier_end
          cycle
        end if
      end if
      
      ! Caractere normal, copia
      accumulator = accumulator // line(i:i)
      i = i + 1
    end do
    
    out = accumulator
    
  end function translate_line

  ! ==========================================================================
  ! FUNÇÕES DE CLASSIFICAÇÃO DE CARACTERES
  ! ==========================================================================
  ! Estas funções determinam se um caractere pode ser parte de identificador.
  ! ==========================================================================

  ! Início de identificador ASCII: A-Z, a-z, _
  pure logical function is_ascii_identifier_start(ch)
    character(len=1), intent(in) :: ch
    integer :: code
    
    code = iachar(ch)
    is_ascii_identifier_start = &
      ((code >= iachar('A') .and. code <= iachar('Z')) .or. &
       (code >= iachar('a') .and. code <= iachar('z')) .or. &
       (code == iachar('_')))
  end function is_ascii_identifier_start

  ! Corpo de identificador ASCII: A-Z, a-z, _, 0-9
  pure logical function is_ascii_identifier_body(ch)
    character(len=1), intent(in) :: ch
    integer :: code
    
    code = iachar(ch)
    is_ascii_identifier_body = &
      is_ascii_identifier_start(ch) .or. &
      (code >= iachar('0') .and. code <= iachar('9'))
  end function is_ascii_identifier_body

  ! Início de identificador (ASCII ou Unicode)
  pure logical function is_identifier_start(ch)
    character(len=1), intent(in) :: ch
    
    ! ASCII ou caractere Unicode (código >= 128)
    is_identifier_start = &
      is_ascii_identifier_start(ch) .or. &
      (ch /= achar(0) .and. .not. (iachar(ch) < 128))
  end function is_identifier_start

  ! Corpo de identificador (ASCII ou Unicode)
  pure logical function is_identifier_body(ch)
    character(len=1), intent(in) :: ch
    
    is_identifier_body = &
      is_ascii_identifier_body(ch) .or. &
      (ch /= achar(0) .and. .not. (iachar(ch) < 128))
  end function is_identifier_body

  ! ==========================================================================
  ! SUBROTINA: read_first_line
  ! ==========================================================================
  ! Lê apenas a primeira linha de um arquivo.
  !
  ! Usado para verificar marcador de geração automática.
  !
  ! Parâmetros:
  !   file_path : Caminho do arquivo
  !   line      : [OUT] Buffer para a linha (tamanho fixo)
  ! ==========================================================================
  subroutine read_first_line(file_path, line)
    character(len=*), intent(in) :: file_path
    character(len=*), intent(out) :: line
    
    integer :: unit, io_status
    character(len=:), allocatable :: line_dynamic
    
    ! Inicializa com string vazia
    line = ""
    
    ! Abre arquivo
    unit = open(file_path, "r", iostat=io_status)
    if (io_status /= 0) return
    
    ! Lê primeira linha
    call get_line(unit, line_dynamic, iostat=io_status)
    if (io_status == 0) line = trim(line_dynamic)
    
    ! Fecha arquivo
    close(unit)
    
  end subroutine read_first_line

end module uf90_file_translator
