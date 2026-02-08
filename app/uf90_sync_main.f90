! ============================================================================
! Programa: uf90_sync
! ============================================================================
! Sincroniza arquivos .uf90 com seus equivalentes .f90 traduzidos.
!
! Este programa:
! 1. Busca a raiz do projeto fpm (localiza fpm.toml)
! 2. Procura todos os arquivos .uf90 em src/, app/, test/
! 3. Para cada .uf90 que mudou desde a última tradução:
!    - Valida que não usa identificadores reservados
!    - Traduz letras gregas Unicode para nomes ASCII
!    - Gera .f90 correspondente
! 4. Protege .f90 existentes que não foram gerados (recusa sobrescrita)
!
! Uso:
!   $ uf90-sync
!   (deve ser executado dentro de um projeto fpm)
!
! Comportamento:
! - Apenas arquivos modificados são regenerados (eficiente)
! - Arquivos .f90 gerados têm marcador especial na primeira linha
! - Erros de validação param a execução imediatamente
! ============================================================================

program uf90_sync
  ! =========================================================================
  ! DEPENDÊNCIAS
  ! =========================================================================
  use stdlib_system, only : run, process_type, get_cwd, set_cwd, &
                            is_directory, is_file, dir_name
  use uf90_constants,       only : FPM_DIRS
  use uf90_file_translator, only : translate_file
  implicit none
  
  ! =========================================================================
  ! VARIÁVEIS PRINCIPAIS
  ! =========================================================================
  integer :: exit_code
  character(len=:), allocatable :: project_root
  character(len=:), allocatable :: current_dir
  
  ! =========================================================================
  ! FLUXO PRINCIPAL
  ! =========================================================================
  
  ! Obtém diretório atual
  call get_cwd(current_dir)
  
  ! Encontra raiz do projeto fpm (onde está fpm.toml)
  project_root = find_project_root(current_dir)
  
  if (.not. allocated(project_root)) then
    write(*,'(a)') "[uf90] ERRO: nao encontrei fpm.toml"
    write(*,'(a)') "[uf90]       Execute dentro de um projeto fpm"
    stop 2
  end if
  
  ! Sincroniza todos os arquivos .uf90
  call synchronize_all_files(project_root, exit_code)
  
  ! Retorna código de saída apropriado
  if (exit_code /= 0) stop exit_code

contains

  ! ==========================================================================
  ! FUNÇÃO: find_project_root
  ! ==========================================================================
  ! Procura o diretório raiz do projeto fpm subindo na hierarquia.
  !
  ! Estratégia:
  ! - Começa no diretório atual
  ! - Verifica se existe fpm.toml
  ! - Se não, sobe um nível (diretório pai)
  ! - Repete até encontrar ou chegar na raiz do sistema
  !
  ! Parâmetros:
  !   start_dir : Diretório inicial (geralmente diretório atual)
  !
  ! Retorna:
  !   Caminho absoluto da raiz do projeto ou desalocado se não encontrar
  ! ==========================================================================
  function find_project_root(start_dir) result(root)
    character(len=*), intent(in) :: start_dir
    character(len=:), allocatable :: root
    character(len=:), allocatable :: current
    
    current = trim(start_dir)
    
    ! Sobe na hierarquia até encontrar fpm.toml ou raiz do sistema
    do
      ! Verifica se fpm.toml existe neste diretório
      if (is_file(current//"/fpm.toml")) then
        root = current
        return
      end if
      
      ! Chegou na raiz do sistema?
      if (current == "/") exit
      
      ! Obtém diretório pai
      current = dir_name(current)
      
      ! Diretório pai inválido?
      if (len_trim(current) == 0) exit
    end do
    
    ! Não encontrou - root permanece desalocado
    
  end function find_project_root

  ! ==========================================================================
  ! SUBROTINA: synchronize_all_files
  ! ==========================================================================
  ! Sincroniza todos os arquivos .uf90 encontrados no projeto.
  !
  ! Processo:
  ! 1. Muda para diretório raiz do projeto
  ! 2. Lista todos os .uf90 em src/, app/, test/
  ! 3. Para cada arquivo, verifica se precisa regenerar
  ! 4. Regenera arquivos modificados
  ! 5. Volta ao diretório original
  !
  ! Parâmetros:
  !   root : Diretório raiz do projeto
  !   ec   : [OUT] Código de erro (0 = sucesso)
  ! ==========================================================================
  subroutine synchronize_all_files(root, ec)
    character(len=*), intent(in) :: root
    integer, intent(out) :: ec
    
    integer :: i, files_updated
    character(len=:), allocatable :: file_list
    character(len=:), allocatable :: original_dir
    
    ! Inicializa
    ec = 0
    files_updated = 0
    
    ! Salva diretório original para voltar depois
    call get_cwd(original_dir)
    
    ! Muda para raiz do projeto
    call set_cwd(root)
    
    ! === ETAPA 1: Coleta lista de arquivos .uf90 ===
    file_list = ""
    
    do i = 1, size(FPM_DIRS)
      ! Verifica se diretório existe antes de procurar
      if (is_directory(trim(FPM_DIRS(i)))) then
        file_list = file_list // list_uf90_files(trim(FPM_DIRS(i)))
      end if
    end do
    
    ! Nenhum arquivo encontrado?
    if (len_trim(file_list) == 0) then
      write(*,'(a)') "[uf90] Nenhum arquivo .uf90 encontrado"
      call set_cwd(original_dir)
      return
    end if
    
    ! === ETAPA 2: Processa cada arquivo ===
    call process_file_list(file_list, files_updated, ec)
    
    ! === ETAPA 3: Reporta resultado ===
    if (ec == 0) then
      write(*,'(a,i0,a)') "[uf90] Sincronização concluída: ", &
                          files_updated, " arquivo(s) atualizado(s)"
    end if
    
    ! Volta ao diretório original
    call set_cwd(original_dir)
    
  end subroutine synchronize_all_files

  ! ==========================================================================
  ! FUNÇÃO: list_uf90_files
  ! ==========================================================================
  ! Lista todos os arquivos .uf90 em um diretório (recursivamente).
  !
  ! Usa o comando Unix 'find' para buscar arquivos.
  !
  ! Parâmetros:
  !   directory : Diretório raiz para busca
  !
  ! Retorna:
  !   String com lista de arquivos (um por linha)
  ! ==========================================================================
  function list_uf90_files(directory) result(file_list)
    character(len=*), intent(in) :: directory
    character(len=:), allocatable :: file_list
    type(process_type) :: process
    
    ! Executa find para buscar .uf90 recursivamente
    process = run( &
      "find " // trim(directory) // " -type f -name '*.uf90' -print", &
      want_stdout=.true. &
    )
    
    file_list = process%stdout
    
    ! Garante que termina com newline se não está vazio
    if (len_trim(file_list) > 0) then
      file_list = trim(file_list) // new_line('a')
    end if
    
  end function list_uf90_files

  ! ==========================================================================
  ! SUBROTINA: process_file_list
  ! ==========================================================================
  ! Processa lista de arquivos (um por linha), traduzindo cada um.
  !
  ! Parâmetros:
  !   text    : Lista de arquivos separados por newline
  !   updated : [INOUT] Contador de arquivos atualizados
  !   ec      : [OUT] Código de erro
  ! ==========================================================================
  subroutine process_file_list(text, updated, ec)
    character(len=*), intent(in) :: text
    integer, intent(inout) :: updated
    integer, intent(out) :: ec
    
    integer :: position, text_length, newline_pos
    character(len=:), allocatable :: line
    character(len=:), allocatable :: uf90_file, f90_file
    
    ec = 0
    position = 1
    text_length = len_trim(text)
    
    ! Processa linha por linha
    do while (position <= text_length)
      
      ! Encontra próximo newline
      newline_pos = index(text(position:), new_line('a'))
      
      if (newline_pos == 0) then
        ! Última linha (sem newline)
        line = trim(text(position:))
        position = text_length + 1
      else
        ! Extrai linha (sem o newline)
        line = trim(text(position:position+newline_pos-2))
        position = position + newline_pos
      end if
      
      ! Pula linhas vazias
      if (len_trim(line) == 0) cycle
      
      ! Determina nomes dos arquivos
      uf90_file = line
      f90_file = replace_file_suffix(uf90_file, ".uf90", ".f90")
      
      ! Verifica se precisa regenerar
      if (file_needs_regeneration(uf90_file, f90_file)) then
        
        ! Traduz arquivo
        call translate_file(uf90_file, f90_file, ec)
        
        if (ec /= 0) return  ! Para na primeira erro
        
        updated = updated + 1
        write(*,'(a,1x,a,1x,a,1x,a)') &
          "[uf90] OK:", trim(uf90_file), "->", trim(f90_file)
      end if
      
    end do
    
  end subroutine process_file_list

  ! ==========================================================================
  ! FUNÇÃO: file_needs_regeneration
  ! ==========================================================================
  ! Verifica se arquivo .f90 precisa ser regenerado.
  !
  ! Critérios:
  ! 1. .f90 não existe → precisa gerar
  ! 2. .uf90 é mais recente que .f90 → precisa regenerar
  !
  ! Parâmetros:
  !   uf90_path : Arquivo fonte .uf90
  !   f90_path  : Arquivo gerado .f90
  !
  ! Retorna:
  !   .true. se precisa regenerar
  ! ==========================================================================
  logical function file_needs_regeneration(uf90_path, f90_path)
    character(len=*), intent(in) :: uf90_path, f90_path
    integer :: shell_status
    
    ! .f90 não existe? Precisa gerar
    if (.not. is_file(f90_path)) then
      file_needs_regeneration = .true.
      return
    end if
    
    ! Usa teste shell [ file1 -nt file2 ] para comparar timestamps
    ! -nt = "newer than"
    call execute_command_line( &
      "[ '" // trim(uf90_path) // "' -nt '" // trim(f90_path) // "' ]", &
      exitstat=shell_status &
    )
    
    ! Status 0 = .uf90 é mais novo
    file_needs_regeneration = (shell_status == 0)
    
  end function file_needs_regeneration

  ! ==========================================================================
  ! FUNÇÃO: replace_file_suffix
  ! ==========================================================================
  ! Substitui sufixo de nome de arquivo.
  !
  ! Exemplo: replace_file_suffix("test.uf90", ".uf90", ".f90") → "test.f90"
  !
  ! Parâmetros:
  !   path        : Caminho original
  !   old_suffix  : Sufixo a ser removido
  !   new_suffix  : Sufixo a ser adicionado
  !
  ! Retorna:
  !   Caminho com novo sufixo
  ! ==========================================================================
  function replace_file_suffix(path, old_suffix, new_suffix) result(out)
    character(len=*), intent(in) :: path, old_suffix, new_suffix
    character(len=:), allocatable :: out
    integer :: old_len, path_len
    
    old_len = len_trim(old_suffix)
    path_len = len_trim(path)
    
    ! Verifica se termina com old_suffix
    if (path_len >= old_len .and. &
        path(path_len-old_len+1:path_len) == old_suffix) then
      ! Remove sufixo antigo e adiciona novo
      out = path(1:path_len-old_len) // new_suffix
    else
      ! Não termina com sufixo esperado, retorna sem modificar
      out = path
    end if
    
  end function replace_file_suffix

end program uf90_sync
