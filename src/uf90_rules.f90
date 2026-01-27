module uf90_rules
  use stdlib_strings, only : replace_all
  implicit none
  private
  public :: translate_identifier, check_reserved_ascii_token

  integer, parameter :: GNAME_LEN = 8  ! "epsilon" e "omicron" têm 7, "upsilon" 7
  character(len=GNAME_LEN), parameter :: greek_names(24) = [character(len=GNAME_LEN) :: &
    "alpha   ","beta    ","gamma   ","delta   ","epsilon ","zeta    ","eta     ","theta   ","iota    ", &
    "kappa   ","lambda  ","mu      ","nu      ","xi      ","omicron ","pi      ","rho     ","sigma   ","tau     ", &
    "upsilon ","phi     ","chi     ","psi     ","omega   " ]


contains

  pure logical function is_reserved(name)
    character(len=*), intent(in) :: name
    integer :: i
    character(len=:), allocatable :: n
    n = to_lower_ascii(trim(name))
    is_reserved = .false.
    do i = 1, size(greek_names)
      if (n == trim(greek_names(i))) then
        is_reserved = .true.; return
      end if
      if (n == trim("uc_"//greek_names(i))) then
        is_reserved = .true.; return
      end if
    end do
  end function is_reserved

  pure function to_lower_ascii(s) result(out)
    character(len=*), intent(in) :: s
    character(len=len(s)) :: out
    integer :: i, c
    out = s
    do i = 1, len(s)
      c = iachar(out(i:i))
      if (c >= iachar('A') .and. c <= iachar('Z')) out(i:i) = achar(c + 32)
    end do
  end function to_lower_ascii

  ! Regra rígida: se um token ASCII do .uf90 for "alpha", "beta", ... ou "uc_alpha", etc -> erro
  subroutine check_reserved_ascii_token(tok, ok)
    character(len=*), intent(in) :: tok
    logical, intent(out) :: ok
    ok = .not. is_reserved(tok)
  end subroutine check_reserved_ascii_token

  pure logical function needs_uscore_neighbor(ch)
    character(len=1), intent(in) :: ch
    integer :: c
    c = iachar(ch)
    needs_uscore_neighbor = ( (c >= iachar('A') .and. c <= iachar('Z')) .or. &
                              (c >= iachar('a') .and. c <= iachar('z')) .or. &
                              (c == iachar('_')) )
  end function needs_uscore_neighbor

  function translate_identifier(ident) result(out)
    character(len=*), intent(in) :: ident
    character(len=:), allocatable :: out
    integer :: i, n
    character(len=:), allocatable :: acc, repl
    character(len=1) :: prevc, nextc
    integer :: keylen

    acc = ""
    n = len_trim(ident)
    i = 1
    do while (i <= n)
      if (match_greek_at(ident, i, repl, keylen)) then
        prevc = achar(0); nextc = achar(0)
        if (i > 1) prevc = ident(i-1:i-1)
        if (i + keylen <= n) nextc = ident(i+keylen:i+keylen)

        if (needs_uscore_neighbor(prevc)) then
          if (len(acc) > 0) then
            if (acc(len(acc):len(acc)) /= "_") acc = acc // "_"
          end if
        end if

        acc = acc // repl

        if (needs_uscore_neighbor(nextc)) acc = acc // "_"

        i = i + keylen
      else
        acc = acc // ident(i:i)
        i = i + 1
      end if
    end do
    out = acc
  end function translate_identifier

  logical function match_greek_at(s, pos, repl, keylen)
    character(len=*), intent(in) :: s
    integer, intent(in) :: pos
    character(len=:), allocatable, intent(out) :: repl
    integer, intent(out) :: keylen

    match_greek_at = .true.

    ! Delta: Δ (U+0394) e ∆ (U+2206) -> uc_delta
    if (starts_with(s, pos, "∆")) then; repl="uc_delta"; keylen=len("∆"); return; end if
    if (starts_with(s, pos, "Δ")) then; repl="uc_delta"; keylen=len("Δ"); return; end if

    ! Maiúsculas (uc_)
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

    ! Minúsculas (sem prefixo)
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

    match_greek_at = .false.
    repl = ""; keylen = 0
  end function match_greek_at

  pure logical function starts_with(s, pos, key)
    character(len=*), intent(in) :: s, key
    integer, intent(in) :: pos
    integer :: n, k
    n = len_trim(s); k = len(key)
    if (pos + k - 1 > n) then
      starts_with = .false.
    else
      starts_with = (s(pos:pos+k-1) == key)
    end if
  end function starts_with

end module uf90_rules

