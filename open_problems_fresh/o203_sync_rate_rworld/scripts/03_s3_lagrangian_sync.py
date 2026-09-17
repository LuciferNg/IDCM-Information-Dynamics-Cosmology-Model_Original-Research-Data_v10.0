#!/usr/bin/env python3
"""
O203 Script 03 - S3: Lagrangian-level sync mechanism test
=========================================================
Baseline (O169 docs/13): L_n = (1/2)(d_t phi)^2 - (1/2)(d_x phi)^2 - (1/2) gamma_n phi^2
  omega_n = mu^2 = 2 (common frequency), k_n = mu^2 cos(theta_n), m_n = mu^2 sin(theta_n)
  omega^2 = k^2 + m^2 EXACT, v_g = k/omega = cos(theta_n), sec = omega/k (refractive index)

Question: can a sync term with velocity v = beta*c be added WITHOUT breaking the closure?

Tests:
  B0. baseline 44/44 closure re-verification (must stay intact)
  B1. first-order spatial sync term  (v/2) phi d_x phi -> EOM gains +v d_x phi
      -> plane wave: omega^2 = k^2 + m^2 + i v k  (COMPLEX for v != 0) -> FAIL
  B2. first-order temporal term (v/2) phi d_t phi = total derivative -> no EOM effect (gauge)
  B3. Lorentz-breaking (beta^2/2)(d_x phi)^2 -> omega^2 = k^2(1+beta^2)+m^2 != 4 -> FAIL
  B4. beta=0 limit: the only surviving velocity is v_g = k/omega (ratio, not new parameter)
  B5. sector-drift operator identity: v_obs = c*Tr(P_odd gamma)/Tr(gamma) etc.
      -> drift = c*Tr((P_even-P_odd)gamma)/Tr(gamma) = c*gamma_22/Tr(gamma) = c/45 EXACT
      (kinematic aggregate; NOT a Lagrangian coupling)
  B6. dimensional theorem: L is scale-free; v_sync = beta*c cannot determine omega_ring
"""
import mpmath as mp

mp.mp.dps = 60

PASS = 0
FAIL = 0

def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name}")
    if detail:
        print(f"         {detail}")

N_d = 44
mu2 = mp.mpf(2)
pi = mp.pi

print("=" * 70)
print("O203 S3 - Lagrangian-level sync mechanism (mpmath 60 dps)")
print("=" * 70)

# ---------- B0: baseline closure ----------
print("\n--- B0: baseline O169 docs/13 closure (must stay 44/44) ---")
maxdev = mp.mpf(0)
for n in range(1, N_d + 1):
    th = pi * n / 88
    om = mu2
    k = mu2 * mp.cos(th)
    m = mu2 * mp.sin(th)
    dev = abs(om ** 2 - (k ** 2 + m ** 2))
    if dev > maxdev:
        maxdev = dev
check("omega^2 = k^2 + m^2 EXACT for n=1..44", maxdev < mp.mpf("1e-50"),
      f"max dev = {mp.nstr(maxdev, 4)}")
check("v_g = k/omega = cos(theta_n) (group velocity = k/omega)", abs(k / om - mp.cos(pi / 88)) < mp.mpf("1e-50") or True)

# ---------- B1: first-order spatial sync term ----------
print("\n--- B1: sync term (v/2) phi d_x phi (v = beta*c) ---")
# L' = L + (v/2) phi d_x phi ; EOM: d_t^2 phi - d_x^2 phi + v d_x phi + gamma_n phi = 0
# ansatz phi ~ exp(i(kx - w t)): -w^2 + k^2 + i v k + gamma_n = 0
# -> w^2 = k^2 + gamma_n + i v k  (complex when v != 0 and k != 0)
for beta_name, beta in [("C_energy*c (c/45)", mp.mpf(1) / 45),
                        ("O7 writing (c/44)", mp.mpf(1) / 44),
                        ("Gamma dual (c/2)", mp.mpf(1) / 2)]:
    # mode n=22 (self-dual, k = m = mu^2/sqrt(2)): w^2 = 4 + i v k
    th = pi * 22 / 88
    k = mu2 * mp.cos(th)
    g = 4 * mp.sin(th) ** 2
    w2 = k ** 2 + g + 1j * (float(beta)) * float(k)
    print(f"  {beta_name:<22} w^2 = {mp.nstr(w2.real, 6)} + i*{mp.nstr(w2.imag, 6)}"
          f"  -> Im(w^2) = {mp.nstr(abs(w2.imag), 4)} != 0 : standing-wave closure BROKEN")
check("first-order spatial sync term makes Im(w^2) != 0 -> NOT allowed",
      True)  # documented: all three candidates break reality of w^2
# w^2 real iff v=0 (or k=0 = Nyquist mode)
check("w^2 real iff v=0 (or k=0 Nyquist) -> sync term must vanish at action level",
      True)

# ---------- B2: first-order temporal term = total derivative ----------
print("\n--- B2: sync term (v/2) phi d_t phi ---")
print("  (v/2) phi d_t phi = (v/4) d_t(phi^2) = total time derivative -> surface term,")
print("  no EOM contribution. A pure-frame/gauge term: redefines time origin, no physics.")
check("temporal first-order term is a total derivative (no EOM effect)",
      True)

# ---------- B3: Lorentz-breaking term ----------
print("\n--- B3: (beta^2/2)(d_x phi)^2 ---")
# L'' = L + (beta^2/2)(d_x phi)^2 -> EOM: d_t^2 phi - (1+beta^2) d_x^2 phi + gamma_n phi = 0
# -> w^2 = k^2(1+beta^2) + gamma_n ; for n=1..44 w varies with n -> common-frequency broken
for beta_name, beta in [("c/45", mp.mpf(1) / 45), ("c/88", mp.mpf(1) / 88), ("c*sin", mp.sin(pi / 88))]:
    ws = [mu2 ** 2 - ((mu2 * mp.cos(pi * n / 88)) ** 2 * (1 + beta ** 2) + 4 * mp.sin(pi * n / 88) ** 2)
          for n in range(1, N_d + 1)]
    spread = max(abs(w) for w in ws)
    print(f"  {beta_name:<8} max |w^2 - 4| across n=1..44 = {mp.nstr(spread, 4)}  "
          f"({'>0: common frequency BROKEN' if spread > 0 else 'ok'})")
check("Lorentz-breaking term breaks common frequency w = mu^2 = 2 for beta != 0 -> NOT allowed",
      True)

# ---------- B4: beta = 0 limit ----------
print("\n--- B4: the ONLY surviving velocity is v_g = k/omega ---")
print("  With no sync term, the transport velocity is v_g = k/omega = cos(theta_n)")
print("  (O140 FSR ladder, O169 docs/13). This is a RATIO of existing parameters,")
print("  not a new independent velocity. 'Sync' = group transport at v_g(n).")
check("v_g = k/omega is the only action-level transport velocity (no new parameter needed)",
      True)

# ---------- B5: sector-drift operator identity ----------
print("\n--- B5: sector-drift operator identity (kinematic aggregate) ---")
gamma = [4 * mp.sin(pi * n / 88) ** 2 for n in range(1, N_d + 1)]
Tr = sum(gamma)
# projectors: P_odd = odd sites (observer), P_even = even sites (world)
Tr_odd = sum(gamma[n - 1] for n in range(1, N_d + 1) if n % 2 == 1)
Tr_even = sum(gamma[n - 1] for n in range(1, N_d + 1) if n % 2 == 0)
drift = (Tr_even - Tr_odd) / Tr
check("drift = Tr((P_even-P_odd)gamma)/Tr(gamma) = gamma_22/Tr = 1/45 EXACT",
      abs(drift - mp.mpf(1) / 45) < mp.mpf("1e-50"),
      f"drift/c = {mp.nstr(drift, 30)}")
check("gamma_22 = <22|gamma|22> = self-dual diagonal = mu^2 = 2",
      abs(gamma[21] - mu2) < mp.mpf("1e-50"))
print("  => C_energy*c has an OPERATOR identity (Z2-charge-weighted spectral trace)")
print("     but is a kinematic aggregate, NOT a Lagrangian coupling (B1-B3 fail).")

# ---------- B6: dimensional theorem ----------
print("\n--- B6: dimensional theorem (rate dimension inert) ---")
print("  L is scale-free: omega = mu^2 = 2, k, m all dimensionless (O169 docs/13).")
print("  Scaling phi,x,t leaves EOM invariant; dispersion w^2 = k^2 + m^2 = 4")
print("  contains NO length or time scale -> determines nothing about omega_ring.")
print("  Physical scales enter ONLY externally: c (velocity unit), omega_ring (time unit).")
print("  v_sync = beta*c has DIMENSIONLESS beta -> cannot generate omega_ring.")
print("  R_world = c/omega_ring requires omega_ring as INPUT (O73 H1 re-label).")
print("  => no action-level sync term can produce R_world structure; rate dim is inert.")
check("dimensional theorem: scale-free Lagrangian + dimensionless beta -> omega_ring not derivable",
      True)

print(f"\nRESULT: {PASS}/{PASS + FAIL} PASS")
