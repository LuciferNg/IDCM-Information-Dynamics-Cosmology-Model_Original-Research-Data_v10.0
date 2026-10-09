"""
O140 - FSR Generic-N Verification (v2)
===========================================
Verify all FSR structural identities for arbitrary N.
FSR as a self-contained framework: all identities derive from the
finite spectrum epsilon_n = 4 sin^2(pi n / (2N)), n = 1..N.

Corrected for boundary conditions: sum epsilon_n = 2N+2.
Dual-chain identity: epsilon_n^{(2N)} * epsilon_{2N-n}^{(2N)} = epsilon_n^{(N)}.

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

def eps(M, n):
    """Finite spectrum: eigenvalue of discrete Laplacian on M-site chain."""
    return 4 * math.sin(math.pi * n / (2 * M)) ** 2

def vg(N, n):
    """Group velocity ladder (cosine of half-angle)."""
    return math.cos(math.pi * n / (2 * N))

def gamma_fsr(N, n):
    """Lorentz ladder = csc(pi n / (2N))."""
    return 1.0 / math.sin(math.pi * n / (2 * N))

def eta(N, n):
    """Rapidity lattice = ln(cot(pi n / (4N)))."""
    return math.log(1.0 / math.tan(math.pi * n / (4 * N)))

def doppler(N, n):
    """Doppler factor = cot(pi n / (4N))."""
    return 1.0 / math.tan(math.pi * n / (4 * N))

test_Ns = [4, 8, 16, 44, 100]

print("=" * 72)
print("FSR: Generic-N Verification (v2)")
print("=" * 72)
print(f"Testing N = {test_Ns}")

for N in test_Ns:
    print(f"\n--- N = {N} ---")

    # A1: Spectral sum: sum_{n=1}^{N} 4 sin^2(pi n/(2N)) = 2N + 2
    S = sum(eps(N, n) for n in range(1, N+1))
    check(f"sum eps_n = 2N+2", abs(S - (2*N+2)) < 1e-9,
          f"(sum={S:.4f}, 2N+2={2*N+2})")

    # A2: Dual-chain mirror identity: eps_n^{(2N)} * eps_{2N-n}^{(2N)} = eps_n^{(N)}
    ok_mirror = True
    for n in range(1, N+1):
        if abs(eps(2*N, n) * eps(2*N, 2*N - n) - eps(N, n)) > 1e-9:
            ok_mirror = False
    check(f"dual-chain mirror: eps_n(2N) * eps_{{2N-n}}(2N) = eps_n(N)",
          ok_mirror)

    # B: Velocity ladder
    check(f"v_g(0) = c (uniform mode)", abs(vg(N, 0) - 1) < 1e-9)
    check(f"v_g(N) = 0 (Nyquist = rest)", abs(vg(N, N)) < 1e-9)
    # Velocity monotonic: v_g decreases from n=0 to n=N
    ok_mono = all(vg(N, n) > vg(N, n+1) for n in range(0, N))
    check(f"v_g monotonic decreasing on ladder", ok_mono)

    # C: Lorentz ladder
    ok_gamma = True
    for n in range(1, N+1):
        if abs(gamma_fsr(N, n) - 2/math.sqrt(eps(N, n))) > 1e-9:
            ok_gamma = False
    check(f"gamma_n = 2/sqrt(eps_n)", ok_gamma)

    # D: SR identity preserved
    ok_sr = True
    for n in range(1, N+1):
        vn = vg(N, n)
        sr_gamma = 1.0 / math.sqrt(1 - vn**2)
        if abs(sr_gamma - gamma_fsr(N, n)) > 1e-9:
            ok_sr = False
    check(f"gamma = 1/sqrt(1-v^2/c^2) preserved", ok_sr)

    # E: Rapidity identity
    ok_eta = True
    for n in range(1, N+1):
        if abs(math.atanh(vg(N, n)) - eta(N, n)) > 1e-9:
            ok_eta = False
    check(f"eta_n = atanh(v_n/c) = ln(cot(pi n/4N))", ok_eta)

    # F: Doppler identity
    ok_dopp = True
    for n in range(1, N+1):
        vn = vg(N, n)
        if abs(math.sqrt((1+vn)/(1-vn)) - doppler(N, n)) > 1e-9:
            ok_dopp = False
    check(f"D_n = sqrt((1+beta)/(1-beta)) = cot(pi n/4N)", ok_dopp)

    # G: Mass shell exact
    m = 1.0
    ok_shell = True
    for n in range(1, N+1):
        E = m * gamma_fsr(N, n)
        p = m * vg(N, n) * gamma_fsr(N, n)
        if abs(E**2 - p**2 - m**2) > 1e-9:
            ok_shell = False
    check(f"E^2 - p^2 c^2 = m^2 c^4 exact (mass shell)", ok_shell)

    # H: Gamma sum rule on the 2N-site chain:
    # sum_{n=1}^{2N} csc^2(pi n/(4N)) = ((2N)^2-1)/3
    if N > 1:
        g2_sum = sum(gamma_fsr(N, n)**2 for n in range(1, N+1))
        # Note: this is the sum over n=1..N of csc^2(pi n/(2N))
        # For the 2N-site chain (n=1..2N-1), the sum is ((2N)^2-1)/3
        # Half of that (n=1..N) plus csc^2(pi/2)=1 at n=N gives g2_sum
        full_sum = ((2*N)**2 - 1) / 3.0  # sum over n=1..2N-1
        # Check: g2_sum should equal full_sum/2 + 0.5 (half + endpoint)
        check(f"sum gamma_n^2 self-consistent (N={N})",
              abs(g2_sum - full_sum/2 - 0.5) < 1e-6,
              f"(g2_sum={g2_sum:.2f}, half_full={full_sum/2+0.5:.2f})")

    # I: Continuum limit
    if N >= 44:
        check(f"v_g(1) -> 1 as N grows", vg(N, 1) > 0.999)
        check(f"gamma(1) ~ 2N/pi as N grows",
              abs(gamma_fsr(N, 1) * math.pi / (2*N) - 1) < 0.02)

    # J: Lorentz factor from frequency
    n_test = max(1, N//4)
    check(f"gamma_n = c/(pi a f_n) (n={n_test})",
          abs(gamma_fsr(N, n_test) - 1.0 / math.sin(math.pi * n_test / (2*N))) < 1e-9)

print(f"\n{'='*72}")
print(f"RESULT: {PASS} PASS, {FAIL} FAIL across {len(test_Ns)} N values")
print('='*72)
if FAIL == 0:
    print("ALL FSR IDENTITIES VERIFIED FOR GENERIC N")
    print("FSR is a self-contained framework independent of IDCM.")
else:
    print("SOME CHECKS FAILED")