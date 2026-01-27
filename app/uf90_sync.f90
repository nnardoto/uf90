program uf90_sync
  use stdlib_system, only : run, process_type, get_cwd, set_cwd, is_directory, is_file, dir_name
  use stdlib_io,     only : open, get_line
  use uf90_consts,   only : GEN_MARKER, FPM_DIRS
  use uf90_rules,    only : translate_identifier, check_reserved_ascii_token
  implicit none

  integer :: ec
  character(len=:), allocatable :: root, cwd

  call get_cwd(cwd)
  root = find_root(cwd)
  if (.not. allocated(root)) then
    write(*,'(a)') "[uf90] ERRO: nao achei fpm.toml (rode dentro de um projeto fpm)"
    stop 2
  end if

  call sync_all(root, ec)
  if (ec /= 0) stop ec

contains

  function find_root(start) result(root)
    character(len=*), intent(in) :: start
    character(len=:), allocatable :: root
    character(len=:), allocatable :: cur

    cur = trim(start)
    do
      if (is_file(cur//"/fpm.toml")) then
        root = cur
        return
      end if
      if (cur == "/") exit
      cur = dir_name(cur)
      if (len_trim(cur) == 0) exit
    end do
  end function find_root

  subroutine sync_all(root, ec)
    character(len=*), intent(in) :: root
    integer, intent(out) :: ec

    integer :: i
    character(len=:), allocatable :: files
    integer :: updated

    ec = 0
    updated = 0

    call set_cwd(root)

    files = ""
    do i = 1, size(FPM_DIRS)
      if (is_directory(trim(FPM_DIRS(i)))) then
        files = files // list_uf90(trim(FPM_DIRS(i)))
      end if
    end do

    if (len_trim(files) == 0) then
      write(*,'(a)') "[uf90] nenhum .uf90 encontrado"
      call set_cwd(cwd)
      return
    end if

    call foreach_line(files, updated, ec)
    if (ec == 0) write(*,'(a,i0)') "[uf90] arquivos atualizados: ", updated

    call set_cwd(cwd)
  end subroutine sync_all

  function list_uf90(dir) result(out)
    character(len=*), intent(in) :: dir
    character(len=:), allocatable :: out
    type(process_type) :: p
    p = run("find " // trim(dir) // " -type f -name '*.uf90' -print", want_stdout=.true.)
    out = p%stdout
    if (len_trim(out) > 0) out = trim(out)//new_line('a')
  end function list_uf90

  subroutine foreach_line(text, updated, ec)
    character(len=*), intent(in) :: text
    integer, intent(inout) :: updated
    integer, intent(out) :: ec

    integer :: pos, n, nl
    character(len=:), allocatable :: ln
    character(len=:), allocatable :: uf, f90

    ec = 0
    pos = 1
    n = len_trim(text)

    do while (pos <= n)
      nl = index(text(pos:), new_line('a'))
      if (nl == 0) then
        ln = trim(text(pos:))
        pos = n + 1
      else
        ln = trim(text(pos:pos+nl-2))
        pos = pos + nl
      end if

      if (len_trim(ln) == 0) cycle

      uf = ln
      f90 = replace_suffix(uf, ".uf90", ".f90")

      if (needs_regen(uf, f90)) then
        call transpile_file(uf, f90, ec)
        if (ec /= 0) return
        updated = updated + 1
        write(*,'(a,1x,a,1x,a)') "[uf90] ok:", trim(uf), "-> "//trim(f90)
      end if
    end do
  end subroutine foreach_line

  logical function needs_regen(uf, f90)
    character(len=*), intent(in) :: uf, f90
    integer :: stat

    if (.not. is_file(f90)) then
      needs_regen = .true.
      return
    end if

    call execute_command_line("[ '"//trim(uf)//"' -nt '"//trim(f90)//"' ]", exitstat=stat)
    needs_regen = (stat == 0)
  end function needs_regen

  subroutine transpile_file(uf, f90, ec)
    character(len=*), intent(in) :: uf, f90
    integer, intent(out) :: ec

    integer :: iu, ou, ios
    character(len=:), allocatable :: ln, outln
    character(len=4096) :: first

    ec = 0

    if (is_file(f90)) then
      call read_first_line(f90, first)
      if (trim(first) /= GEN_MARKER) then
        write(*,'(a)') "[uf90] ERRO: recusando sobrescrever .f90 nao-gerado: "//trim(f90)
        ec = 2
        return
      end if
    end if

    iu = open(uf, "r", iostat=ios)
    if (ios /= 0) then
      write(*,'(a)') "[uf90] ERRO: nao consegui ler "//trim(uf)
      ec = 2; return
    end if

    ou = open(f90, "w", iostat=ios)
    if (ios /= 0) then
      write(*,'(a)') "[uf90] ERRO: nao consegui escrever "//trim(f90)
      ec = 2; return
    end if

    write(ou,'(a)') GEN_MARKER
    write(ou,'(a)') "! SOURCE: "//trim(uf)

    do
      call get_line(iu, ln, iostat=ios)
      if (ios /= 0) exit

      call enforce_reserved_ascii(ln, uf, ec)
      if (ec /= 0) exit

      outln = transpile_line(ln)
      write(ou,'(a)') trim(outln)
    end do

    close(iu); close(ou)
  end subroutine transpile_file

  ! IMPORTANT: Fortran does NOT guarantee short-circuit evaluation of .and./.or.
  ! So NEVER write conditions that index line(j:j) inside a logical expression that might be out of bounds.
  subroutine enforce_reserved_ascii(line, uf, ec)
    character(len=*), intent(in) :: line, uf
    integer, intent(out) :: ec
    integer :: i, n, j
    logical :: in_s, in_d
    character(len=:), allocatable :: tok
    logical :: ok

    ec = 0
    in_s = .false.; in_d = .false.
    n = len(line)
    i = 1

    do while (i <= n)

      if (.not. in_s .and. .not. in_d) then
        if (line(i:i) == "!") exit
      end if

      if (.not. in_d .and. line(i:i) == "'") then
        in_s = .not. in_s
        i = i + 1
        cycle
      end if

      if (.not. in_s .and. line(i:i) == '"') then
        in_d = .not. in_d
        i = i + 1
        cycle
      end if

      if (.not. in_s .and. .not. in_d) then
        if (is_ascii_ident_start(line(i:i))) then
          j = i + 1
          do while (j <= n)
            if (.not. is_ascii_ident_body(line(j:j))) exit
            j = j + 1
          end do

          tok = line(i:min(j-1, n))   ! clamp
          call check_reserved_ascii_token(tok, ok)

          if (.not. ok) then
            write(*,'(a)') "[uf90] ERRO: identificador ASCII reservado no dialeto em "//trim(uf)//": "//trim(tok)
            ec = 2
            return
          end if

          i = j
          cycle
        end if
      end if

      i = i + 1
    end do
  end subroutine enforce_reserved_ascii

  function transpile_line(line) result(out)
    character(len=*), intent(in) :: line
    character(len=:), allocatable :: out
    integer :: i, n, j
    logical :: in_s, in_d
    character(len=:), allocatable :: acc, ident

    acc = ""
    in_s = .false.; in_d = .false.
    n = len(line)
    i = 1

    do while (i <= n)

      if (.not. in_s .and. .not. in_d) then
        if (line(i:i) == "!") then
          acc = acc // line(i:n)
          exit
        end if
      end if

      if (.not. in_d .and. line(i:i) == "'") then
        in_s = .not. in_s
        acc = acc // line(i:i)
        i = i + 1
        cycle
      end if

      if (.not. in_s .and. line(i:i) == '"') then
        in_d = .not. in_d
        acc = acc // line(i:i)
        i = i + 1
        cycle
      end if

      if (.not. in_s .and. .not. in_d) then
        if (is_ident_start(line(i:i))) then
          j = i + 1
          do while (j <= n)
            if (.not. is_ident_body(line(j:j))) exit
            j = j + 1
          end do
          ident = line(i:min(j-1, n))
          acc = acc // translate_identifier(ident)
          i = j
          cycle
        end if
      end if

      acc = acc // line(i:i)
      i = i + 1
    end do

    out = acc
  end function transpile_line

  pure logical function is_ascii_ident_start(ch)
    character(len=1), intent(in) :: ch
    integer :: c
    c = iachar(ch)
    is_ascii_ident_start = ((c >= iachar('A') .and. c <= iachar('Z')) .or. &
                            (c >= iachar('a') .and. c <= iachar('z')) .or. &
                            (c == iachar('_')))
  end function is_ascii_ident_start

  pure logical function is_ascii_ident_body(ch)
    character(len=1), intent(in) :: ch
    integer :: c
    c = iachar(ch)
    is_ascii_ident_body = is_ascii_ident_start(ch) .or. (c >= iachar('0') .and. c <= iachar('9'))
  end function is_ascii_ident_body

  pure logical function is_ident_start(ch)
    character(len=1), intent(in) :: ch
    is_ident_start = is_ascii_ident_start(ch) .or. (ch /= achar(0) .and. .not. (iachar(ch) < 128))
  end function is_ident_start

  pure logical function is_ident_body(ch)
    character(len=1), intent(in) :: ch
    is_ident_body = is_ascii_ident_body(ch) .or. (ch /= achar(0) .and. .not. (iachar(ch) < 128))
  end function is_ident_body

  function replace_suffix(path, a, b) result(out)
    character(len=*), intent(in) :: path, a, b
    character(len=:), allocatable :: out
    integer :: la, lp
    la = len_trim(a); lp = len_trim(path)
    if (lp >= la .and. path(lp-la+1:lp) == a) then
      out = path(1:lp-la)//b
    else
      out = path
    end if
  end function replace_suffix

  subroutine read_first_line(path, line)
    character(len=*), intent(in) :: path
    character(len=*), intent(out) :: line
    integer :: u, ios
    character(len=:), allocatable :: ln
    line = ""
    u = open(path, "r", iostat=ios)
    if (ios /= 0) return
    call get_line(u, ln, iostat=ios)
    if (ios == 0) line = trim(ln)
    close(u)
  end subroutine read_first_line

end program uf90_sync
