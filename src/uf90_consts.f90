module uf90_consts
  implicit none
  private
  public :: GEN_MARKER, FPM_DIRS

  character(len=*), parameter :: GEN_MARKER = &
    "! GENERATED FROM .uf90; DO NOT EDIT .f90 DIRECTLY"

  character(len=4), parameter :: FPM_DIRS(3) = [character(len=4) :: "src ", "app ", "test"]
end module uf90_consts

