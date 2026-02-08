! ============================================================================
! Módulo: uf90_constants
! ============================================================================
! Define constantes globais usadas pelo sistema uf90 de tradução Unicode→ASCII
!
! Este módulo centraliza todas as constantes do projeto para facilitar
! manutenção e modificações futuras.
! ============================================================================

module uf90_constants
  implicit none
  
  ! Torna apenas as constantes públicas visíveis externamente
  private
  public :: GEN_MARKER, FPM_DIRS
  
  ! ==========================================================================
  ! MARCADOR DE ARQUIVO GERADO
  ! ==========================================================================
  ! Esta string é inserida como primeira linha de todos os arquivos .f90
  ! gerados automaticamente. Serve para:
  ! 1. Identificar arquivos gerados (evita sobrescrita acidental)
  ! 2. Alertar desenvolvedores para não editar o .f90 diretamente
  ! 3. Rastrear a origem do arquivo .f90
  ! ==========================================================================
  character(len=*), parameter :: GEN_MARKER = &
    "! GENERATED FROM .uf90 SOURCE; DO NOT EDIT THIS .f90 FILE DIRECTLY"
  
  ! ==========================================================================
  ! DIRETÓRIOS FPM PADRÃO
  ! ==========================================================================
  ! Lista de diretórios onde o Fortran Package Manager (fpm) coloca
  ! arquivos fonte por convenção. O uf90-sync procura arquivos .uf90
  ! nestes diretórios:
  !
  ! - src/  : Módulos e código de biblioteca
  ! - app/  : Programas executáveis
  ! - test/ : Código de testes
  !
  ! Nota: Os espaços à direita são necessários para arrays de caracteres
  !       de tamanho fixo em Fortran
  ! ==========================================================================
  character(len=4), parameter :: FPM_DIRS(3) = &
    [character(len=4) :: "src ", "app ", "test"]

end module uf90_constants
