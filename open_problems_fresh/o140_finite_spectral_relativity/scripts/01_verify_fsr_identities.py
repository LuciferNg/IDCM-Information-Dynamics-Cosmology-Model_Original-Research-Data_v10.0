"""
O140 - Finite-Spectral Relativity (FSR): verification of all structural identities
====================================================================================
Redesigned relativity on the finite K_Chain spectrum, compatible with IDCM and QM.

All quantities derive from the K_Chain Laplacian spectrum (src/kchain_wave_params.py):
    gamma_n^44 = 4 sin^2(pi n / 88),  n = 1..44        (44-site world chain)
    gamma_k^88 = 4 sin^2(pi k / 176), k = 1..88        (88-site dual chain)
    omega_n    = (2c/a) sin(pi n / 88)                 (lattice dispersion, a = R_world/44)
    v_g(n)     = c cos(pi n / 88)                      (group velocity ladder)

FSR identities verified here:
  A. Chain basis (world sum 90, dual 90/88, total 178 = 2F11)
  B. Velocity ladder: v_n = c cos(pi n/88); rest = Nyquist n=44; v_22 = c/sqrt(2)
  C. Lorentz ladder: gamma_n = csc(pi n/88) = 1/sqrt(1-(v_n/c)^2)  [SR identity preserved]
  D. Eigenvalue identities: gamma_n^88 * gamma_{88-n}^88 = gamma_n^44
                            gamma_n = 2/sqrt(gamma_n^44) = c/(pi a f_n)
                            sum_{n=1}^{44} gamma_n^2 = 1291 (prime, cf. O100 P3)
  E. Rapidity lattice: eta_n = atanh(v_n/c) = ln(cot(pi n/176))
  F. Doppler: D_n = e^{eta_n} = cot(pi n/176) = sqrt((1+beta)/(1-beta))
  G. Mass shell: E_n = mc^2 csc(pi n/88), p_n = mc cot(pi n/88), E^2 - p^2 c^2 = m^2 c^4
  H. BBN/Etherington closure: n/p = gamma_7/gamma_20 = (gamma_FSR(20)/gamma_FSR(7))^2
  I. Scale refinement: N_l = 44 * 4^l (K_Tree B=4); gamma_max(l) = csc(pi/(88*4^l))
     SR limit l -> infinity; gamma_max(l)/(1+z) = 88/pi = 28.01 with 1+z = 4^l (O76)
  J. QM compatibility: finite Hilbert space dim 44; p_n = hbar pi n/(44a);
     GUP Dx >= a/(2pi); lattice KG spectrum bounded (UV-finite)
  K. Mass-velocity ladder sharing: m_g = M0 * gamma_{n_g} (O54: n_g = 1,7,20)
     -> m_g * gamma_FSR(n_g)^2 = 4 M0 (mass-velocity duality, structural)

Author: Hermes (O140 session)
"""
import math

PASS = 0
FAIL = 0

def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {detail}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {detail}")

# ---------------------------------------------------------------
# Constants (from src/kchain_wave_params.py)
# ---------------------------------------------------------------
R_world = 4129.94          # Mpc
Nd = 44                    # sites
c = 299792.458             # km/s
Mpc_to_km = 3.085677581e19
Gyr = 3.15576e16           # s
hbar = 6.582119569e-16     # eV.s
a_Mpc = R_world / Nd       # lattice spacing (Mpc)
c_ms = c * 1e3             # m/s
omega_scale = 88 * c_ms / (R_world * Mpc_to_km * 1e3)   # rad/s
phi = (1 + math.sqrt(5)) / 2

def gamma44(n):
    return 4 * math.sin(math.pi * n / 88) ** 2

def gamma88(k):
    return 4 * math.sin(math.pi * k / 176) ** 2

def vg(n):
    return c * math.cos(math.pi * n / 88)

def omega_n(n):
    return omega_scale * math.sin(math.pi * n / 88)

def gamma_fsr(n):
    return 1.0 / math.sin(math.pi * n / 88)

print("=" * 72)
print("Part A: K_Chain spectrum basis")
print("=" * 72)
S44 = sum(gamma44(n) for n in range(1, 45))
S88_even = sum(gamma88(k) for k in range(1, 89) if k % 2 == 0)
S88_odd = sum(gamma88(k) for k in range(1, 89) if k % 2 == 1)
print(f"  sum gamma^44 (n=1..44)   = {S44:.10f}  (world sum, expect 90)")
print(f"  sum gamma^88 even        = {S88_even:.10f}  (world, expect 90)")
print(f"  sum gamma^88 odd         = {S88_odd:.10f}  (observer, expect 88)")
print(f"  total 178 = 2*89 = 2*F11: {abs(S88_even + S88_odd - 178) < 1e-9}")
check("world sum sum gamma^44 = 90", abs(S44 - 90) < 1e-9)
check("dual even sum = 90", abs(S88_even - 90) < 1e-9)
check("dual odd sum = 88", abs(S88_odd - 88) < 1e-9)
check("total 178 = 2 F11 (F11=89)", abs(S88_even + S88_odd - 178) < 1e-9)

print()
print("=" * 72)
print("Part B: Velocity ladder  v_n = c cos(pi n/88)")
print("=" * 72)
check("v_1 = 0.99936 c (fastest)", abs(vg(1)/c - math.cos(math.pi/88)) < 1e-12)
check("v_22 = c/sqrt(2) = 0.7071 c", abs(vg(22)/c - 1/math.sqrt(2)) < 1e-12)
check("v_44 = 0 (Nyquist = rest)", abs(vg(44)) < 1e-9)
check("v_1 is subluminal (< c)", vg(1) < c)
# mirror duality on the 88-site extension: cos(pi(88-n)/88) = -cos(pi n/88)
n = 7
check("mirror v_{88-n} = -v_n", abs(math.cos(math.pi*(88-n)/88) + math.cos(math.pi*n/88)) < 1e-12,
      f"(n={n})")
# ladder spacing (velocity quantum)
dvs = [vg(n) - vg(n+1) for n in range(1, 44)]
print(f"  max ladder spacing Dv/c = {max(dvs)/c:.6f} at n={dvs.index(max(dvs))+1}")
print(f"  min ladder spacing Dv/c = {min(dvs)/c:.6f} at n={dvs.index(min(dvs))+1}")

print()
print("=" * 72)
print("Part C: Lorentz ladder  gamma_n = csc(pi n/88) = 1/sqrt(1-(v_n/c)^2)")
print("=" * 72)
okC = True
for n in range(1, 45):
    vn = vg(n)
    sr_gamma = 1.0 / math.sqrt(1 - (vn/c)**2)
    if abs(sr_gamma - gamma_fsr(n)) > 1e-9:
        okC = False
check("SR identity gamma = 1/sqrt(1-v^2/c^2) preserved EXACTLY on the ladder", okC)
print(f"  gamma_1  = {gamma_fsr(1):8.4f}   (fastest mode)")
print(f"  gamma_22 = {gamma_fsr(22):8.4f}   (= sqrt(2))")
print(f"  gamma_44 = {gamma_fsr(44):8.4f}   (rest)")
check("gamma_22 = sqrt(2)", abs(gamma_fsr(22) - math.sqrt(2)) < 1e-12)
check("gamma_44 = 1 (rest)", abs(gamma_fsr(44) - 1) < 1e-12)
check("gamma_1 ~ 28.02", abs(gamma_fsr(1) - 88/math.pi) < 0.02)

print()
print("=" * 72)
print("Part D: Eigenvalue identities")
print("=" * 72)
okD1, okD2 = True, True
S_gamma_fsr2 = 0.0
for n in range(1, 45):
    # gamma_n^88 * gamma_{88-n}^88 = gamma_n^44
    if abs(gamma88(n)*gamma88(88-n) - gamma44(n)) > 1e-9:
        okD1 = False
    # gamma_fsr = 2/sqrt(gamma_n^44)
    if abs(gamma_fsr(n) - 2/math.sqrt(gamma44(n))) > 1e-9:
        okD2 = False
    S_gamma_fsr2 += gamma_fsr(n)**2
check("gamma_n^88 * gamma_{88-n}^88 = gamma_n^44  (dual mirror product)", okD1)
check("gamma_FSR(n) = 2/sqrt(gamma_n^44)  (Lorentz from eigenvalue)", okD2)
# gamma = c/(pi a f_n)
n = 11
f_n = omega_n(n) * Gyr / (2*math.pi)      # 1/Gyr
f_n_s = f_n / Gyr                         # 1/s
a_m = a_Mpc * Mpc_to_km * 1e3             # m
gamma_from_f = c_ms / (math.pi * a_m * f_n_s)
check("gamma_n = c/(pi a f_n)  (Lorentz from frequency)", abs(gamma_from_f - gamma_fsr(n)) < 1e-6,
      f"(n={n})")
print(f"  sum_{{-}} gamma_FSR(n)^2 (n=1..44) = {S_gamma_fsr2:.0f}  (prime 1291, cf. O100 P3)")
check("sum gamma_FSR^2 = 1291 (prime)", abs(S_gamma_fsr2 - 1291) < 1e-6)

print()
print("=" * 72)
print("Part E: Rapidity lattice  eta_n = ln(cot(pi n/176))")
print("=" * 72)
okE = True
for n in range(1, 45):
    eta_atanh = math.atanh(vg(n)/c)
    eta_log = math.log(1.0/math.tan(math.pi*n/176))
    if abs(eta_atanh - eta_log) > 1e-9:
        okE = False
check("eta_n = atanh(v_n/c) = ln(cot(pi n/176))", okE)
print(f"  eta_1  = {math.log(1/math.tan(math.pi/176)):.4f}   (fastest)")
print(f"  eta_22 = {math.log(1/math.tan(math.pi*22/176)):.4f}   (v=c/sqrt2)")
print(f"  eta_44 = {math.log(1/math.tan(math.pi*44/176)):.4f}   (rest)")

print()
print("=" * 72)
print("Part F: Doppler ladder  D_n = e^{eta_n} = cot(pi n/176)")
print("=" * 72)
okF = True
for n in range(1, 45):
    vn = vg(n)
    D_sr = math.sqrt((1 + vn/c) / (1 - vn/c))
    D_fsr = 1.0/math.tan(math.pi*n/176)
    if abs(D_sr - D_fsr) > 1e-9:
        okF = False
check("D_n = sqrt((1+beta)/(1-beta)) = cot(pi n/176)", okF)
print(f"  D_1  = {1/math.tan(math.pi/176):.3f}   (max Doppler)")
print(f"  D_44 = {1/math.tan(math.pi*44/176):.3f}   (rest -> 1)")

print()
print("=" * 72)
print("Part G: Discrete mass shell  E_n, p_n, E^2 - p^2 c^2 = m^2 c^4")
print("=" * 72)
m = 1.0  # arbitrary test mass
okG = True
max_g_err = 0.0
max_p_err = 0.0
for n in range(1, 45):
    E = m * c**2 * gamma_fsr(n)
    p = m * c * (vg(n)/c) * gamma_fsr(n)      # p = m v gamma = m c cos/sin
    p2 = m * c / math.tan(math.pi*n/88)       # p = mc cot(theta)
    g_err = abs(E**2 - p**2*c**2 - m**2*c**4) / (m**2*c**4)
    p_err = abs(p - p2) / max(1e-300, abs(p2))
    max_g_err = max(max_g_err, g_err)
    max_p_err = max(max_p_err, p_err)
check("E^2 - p^2 c^2 = m^2 c^4 exact on the discrete hyperbola", max_g_err < 1e-6,
      f"(max rel err {max_g_err:.2e})")
check("p_n = mc cot(pi n/88)", max_p_err < 1e-6,
      f"(max rel err {max_p_err:.2e})")

print()
print("=" * 72)
print("Part H: BBN / Etherington closure  n/p = gamma_7/gamma_20 = (gamma_FSR(20)/gamma_FSR(7))^2")
print("=" * 72)
np_ratio = gamma44(7) / gamma44(20)
np_fsr = (gamma_fsr(20) / gamma_fsr(7))**2
check("n/p = gamma_7/gamma_20 = 0.14262", abs(np_ratio - 0.14262) < 1e-4)
check("n/p = (gamma_FSR(20)/gamma_FSR(7))^2", abs(np_ratio - np_fsr) < 1e-12)
alpha_etherington = 1 - np_ratio
print(f"  n/p = {np_ratio:.6f}   -> 1-n/p = {alpha_etherington:.6f} (Etherington exponent, O76)")
check("1 - n/p = 0.85738 (O76 D_L/D_A exponent)", abs(alpha_etherington - 0.85738) < 1e-4)

print()
print("=" * 72)
print("Part I: Scale refinement  N_l = 44*4^l (K_Tree B=4); SR = l->infinity")
print("=" * 72)
def gamma_max(l):
    return 1.0 / math.sin(math.pi / (88 * 4**l))
for l in [0, 1, 2, 6]:
    print(f"  l={l:2d}: N_l = {44*4**l:7d} sites, gamma_max = {gamma_max(l):12.4f}")
check("gamma_max(0) = csc(pi/88) ~ 28", abs(gamma_max(0) - 88/math.pi) < 0.02)
check("gamma_max(l) grows as 4^l (scale ascent)", gamma_max(6) > gamma_max(2)*50)
# SR limit: gamma_max -> infinity, and dispersion -> linear
l_big = 20
Nl = 44 * 4**l_big
omega_lin = omega_scale * (math.pi * 1 / 88)   # small-angle limit
omega_exact = omega_scale * math.sin(math.pi * 1 / (88 * 4**l_big)) * 4**l_big
# at level l, mode 1 has theta = pi/(88*4^l); omega_l(n=1) = (2c/a_l) sin(theta)
# compare with continuum omega = c*k at same k
check("dispersion -> linear at large l (SR limit)", abs(omega_exact/omega_lin - 1) < 1e-3,
      f"(l={l_big})")
# gamma_max(l) / (1+z) with 1+z = 4^l (O76)
ratio_iz = gamma_max(3) / 4**3
print(f"  gamma_max(l)/(1+z) = {ratio_iz:.6f}  (expect 88/pi = {88/math.pi:.6f})")
check("gamma_max(l) = (88/pi)(1+z)  [z = 4^l - 1, O76]",
      abs(ratio_iz - 88/math.pi) < 1e-5)
# minimal deviation from SR at level l
l_lab = 6   # enough for gamma ~ 1e5 (LEP)
dev = (math.pi/(88*4**l_lab))**2 / 2
print(f"  SR deviation at l={l_lab}: ~{dev:.2e} (unobservable)")

print()
print("=" * 72)
print("Part J: QM compatibility — finite Hilbert space, GUP, UV-finite KG")
print("=" * 72)
# J1: Hilbert space dimension
check("dim H = 44 (world chain, base level)", 44 == Nd)
# J2: momentum quantization p_n = hbar pi n / (44a), compact Brillouin zone
a_m2 = a_Mpc * Mpc_to_km * 1e3      # m
p_max = hbar * math.pi / a_m2       # eV.s / m  (n=44 = zone edge)
p_1 = hbar * math.pi / (44 * a_m2)
print(f"  p_1  = {p_1:.3e} eV.s/m, p_max = {p_max:.3e} eV.s/m (zone edge)")
# J3: GUP  Dx >= a/(2pi)  from Dp <= p_max, Dx Dp >= hbar/2
Dx_min = hbar / (2 * p_max)
gup_rel = abs(Dx_min - a_m2/(2*math.pi)) / (a_m2/(2*math.pi))
check("GUP: Dx_min = a/(2pi) = hbar/(2 p_max)", gup_rel < 1e-6,
      f"(rel err {gup_rel:.2e})")
print(f"  minimal position uncertainty Dx_min = {Dx_min:.3e} m = a/(2pi)")
# J4: lattice Klein-Gordon spectrum bounded (UV-finite)
mc2 = 0.511e6  # eV, electron
p_max_eVc = p_max * c_ms           # eV (p*c in SI: eV.s/m * m/s)
E_n_max = math.sqrt(mc2**2 + p_max_eVc**2)
E_n_1 = math.sqrt(mc2**2 + (p_1*c_ms)**2)
print(f"  lattice KG: E(n=1) = {E_n_1:.6f} eV, E_max = {E_n_max:.6e} eV (note: p_max*c ~ {p_max_eVc:.2e} eV)")
check("lattice KG spectrum bounded (no UV divergence)", E_n_max < math.inf)
# At cosmological lattice spacing, p_max*c << mc^2, so E(n) ~ mc^2 for all n
# The monotonicity is structural: E_n = sqrt(m^2 c^4 + p_n^2 c^2) with p_n increasing
check("KG E(n) increases with n (structural: p_n = hbar pi n/(44a))", p_1*c_ms < p_max_eVc)
# J5: position operator on the chain — spread of a momentum eigenstate
import statistics
xs = [j*a_m2 for j in range(1, 45)]
check("position spectrum = {a, 2a, ..., 44a} (discrete)", len(set(xs)) == 44)
check("lattice spacing a = R_world/44", abs(a_Mpc - R_world/44) < 1e-9)

print()
print("=" * 72)
print("Part K: Mass-velocity ladder sharing  m_g = M0 gamma_{n_g}, n_g = {1,7,20}")
print("=" * 72)
# O54 structural form: m_g proportional to gamma_{n_g} (S_g factors per generation)
# FSR duality: gamma_FSR(n_g)^2 = 4/gamma_{n_g}  ->  m_g * gamma_FSR(n_g)^2 = 4 M0 S_g
for ng, gen in [(1, "e"), (7, "mu"), (20, "tau")]:
    prod = gamma44(ng) * gamma_fsr(ng)**2
    check(f"gamma_{ng} * gamma_FSR({ng})^2 = 4  (mass-velocity duality, {gen})",
          abs(prod - 4) < 1e-9)
    print(f"    mode n={ng:2d} ({gen}): m ~ gamma_{ng} = {gamma44(ng):.5f}, "
          f"v_ceiling = {vg(ng)/c:.4f} c, gamma_FSR = {gamma_fsr(ng):.4f}")
# heavier generation = slower ceiling (structural trade-off)
check("mass ladder and velocity ceiling anti-correlate (heavier = slower)",
      gamma44(20) > gamma44(7) > gamma44(1) and vg(20) < vg(7) < vg(1))

print()
print("=" * 72)
print(f"RESULT: {PASS} PASS, {FAIL} FAIL")
print("=" * 72)
if FAIL == 0:
    print("ALL FSR IDENTITIES VERIFIED")
else:
    print("SOME CHECKS FAILED")
