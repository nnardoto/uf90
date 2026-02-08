! ============================================================================
! Exemplo de código com Unicode que será traduzido
! ============================================================================
! Este arquivo demonstra o uso de letras gregas e outros símbolos Unicode
! que serão automaticamente traduzidos para identificadores ASCII válidos.
! ============================================================================

program exemplo_completo
  implicit none
  
  ! ==========================================================================
  ! DECLARAÇÕES COM LETRAS GREGAS
  ! ==========================================================================
  
  ! Letras gregas minúsculas
  real :: alpha, beta, gamma, delta, epsilon
  real :: lambda, mu, pi, sigma, omega
  
  ! Letras gregas maiúsculas (traduzidas com prefixo uc_)
  real :: uc_delta, uc_sigma, uc_omega
  real :: uc_theta, uc_phi, uc_psi
  
  ! Variáveis com subscritos
  real :: x_1, x_2, x_3
  real :: v_0, v_10, v_100
  
  ! Variáveis compostas
  real :: alpha_max, beta_min
  real :: uc_deltax, uc_deltay, uc_deltat
  
  ! ==========================================================================
  ! CONSTANTES FÍSICAS
  ! ==========================================================================
  
  ! Constantes matemáticas
  pi = 3.14159265358979_8
  
  ! Ângulos (em radianos)
  alpha = pi / 4.0_8    ! 45 graus
  beta = pi / 6.0_8    ! 30 graus
  gamma = pi / 3.0_8    ! 60 graus
  
  ! ==========================================================================
  ! CÁLCULOS TRIGONOMÉTRICOS
  ! ==========================================================================
  
  ! Identidades trigonométricas: sin²(θ) + cos²(θ) = 1
  uc_theta = alpha
  sigma = sin(uc_theta)**2 + cos(uc_theta)**2
  
  write(*,'(a,f10.6)') "sin_p2(theta) + cos_p2(theta) = ", sigma
  
  ! ==========================================================================
  ! OPERAÇÕES COM VETORES
  ! ==========================================================================
  
  ! Componentes de velocidade
  v_0 = 10.0_8      ! Velocidade inicial
  v_10 = 15.0_8     ! Velocidade em t=10
  v_100 = 20.0_8    ! Velocidade em t=100
  
  ! Incrementos
  uc_deltax = v_10 - v_0
  uc_deltay = v_100 - v_10
  
  write(*,'(a,f10.2)') "uc_deltav (0->10):   ", uc_deltax
  write(*,'(a,f10.2)') "uc_deltav (10->100): ", uc_deltay
  
  ! ==========================================================================
  ! ESTATÍSTICA
  ! ==========================================================================
  
  ! Média (μ) e desvio padrão (σ)
  mu = (alpha + beta + gamma) / 3.0_8
  sigma = sqrt(((alpha-mu)**2 + (beta-mu)**2 + (gamma-mu)**2) / 3.0_8)
  
  write(*,'(a,f10.6)') "Média (mu):          ", mu
  write(*,'(a,f10.6)') "Desvio padrão (sigma):  ", sigma
  
  ! ==========================================================================
  ! SOMATÓRIOS
  ! ==========================================================================
  
  ! Somatório: Σ = x₁ + x₂ + x₃
  x_1 = 1.0_8
  x_2 = 2.0_8
  x_3 = 3.0_8
  
  uc_sigma = x_1 + x_2 + x_3
  
  write(*,'(a,f10.2)') "uc_sigmaxᵢ = ", uc_sigma
  
  ! ==========================================================================
  ! ANÁLISE DE LIMITES
  ! ==========================================================================
  
  ! Valores extremos
  alpha_max = max(alpha, beta, gamma)
  beta_min = min(alpha, beta, gamma)
  
  write(*,'(a,f10.6)') "Valor máximo:  ", alpha_max
  write(*,'(a,f10.6)') "Valor mínimo:  ", beta_min
  
  ! ==========================================================================
  ! COMPRIMENTO DE ONDA E FREQUÊNCIA
  ! ==========================================================================
  
  ! λ = c/ν (comprimento de onda = velocidade/frequência)
  real :: c, nu
  
  c = 3.0e8_8      ! Velocidade da luz (m/s)
  nu = 5.0e14_8     ! Frequência (Hz)
  
  lambda = c / nu
  
  write(*,'(a,es12.4,a)') "lambda = ", lambda, " m"
  
  ! ==========================================================================
  ! EQUAÇÕES FÍSICAS
  ! ==========================================================================
  
  ! Energia cinética: E = ½mv²
  real :: m, v, E
  
  m = 2.0_8        ! Massa (kg)
  v = 10.0_8       ! Velocidade (m/s)
  
  E = 0.5_8 * m * v**2
  
  write(*,'(a,f10.2,a)') "Energia cinética: ", E, " J"
  
  ! ==========================================================================
  ! ÂNGULOS SÓLIDOS
  ! ==========================================================================
  
  ! Ângulo sólido de uma esfera: Ω = 4π
  uc_omega = 4.0_8 * pi
  
  write(*,'(a,f10.6,a)') "Ângulo sólido de esfera: ", uc_omega, " sr"
  
  ! ==========================================================================
  ! COMENTÁRIOS COM UNICODE SÃO PRESERVADOS
  ! ==========================================================================
  
  ! Símbolos matemáticos em comentários são mantidos:
  ! • α, β, γ permanecem como estão
  ! • ∞ é infinito
  ! • ≈ significa aproximadamente
  ! • ± é mais ou menos
  ! • → indica transformação
  ! • Δx → variação de x
  
  write(*,*)
  write(*,'(a)') "=========================================="
  write(*,'(a)') "Exemplo concluído com sucesso!"
  write(*,'(a)') "Todos os símbolos Unicode foram traduzidos"
  write(*,'(a)') "=========================================="

end program exemplo_completo
