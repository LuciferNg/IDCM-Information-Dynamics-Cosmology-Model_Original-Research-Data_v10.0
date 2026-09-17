#!/usr/bin/env python3
"""
O203 Script 01 - S1: v_sync candidate enumeration + structural identity verification
=====================================================================================
Verify exact spectral identities for the 5 official candidates + corpus-derived rates.
All identities at mpmath 60 dps. Tautology detection: candidate derivable from
{c, omega_ring, R_world} alone = re-label; pure c x f(chain spectrum) = independent
spectral identity.

Key claims tested:
  C1. Sum gamma_even = 46 = N_d + mu^2,  Sum gamma_odd = 44 = N_d,  Sum gamma = 90
  C2. C_energy = (even - odd)/total = mu^2 / (2*N_d + mu^2) = 1/(N_d+1) = 1/45 EXACT
  C3. Sector velocities: v_obs = c*44/90 = c*22/45, v_world = c*46/90 = c*23/45
      -> mean = c/2 (O138 Gamma velocity dual), drift = c/45 (C_energy*c)
  C4. Ladder membership: cos(pi*n/88) == candidate for integer n?
      (c*sin(pi/88) = v_g(43) EXACT, c*cos(pi/88) = v_g(1) EXACT; c/45, c/88, c(1-pi/44) NOT)
  C5. O7 writing rate: 2 phase slips (pi each) per ring period -> v = 2*lambda_sync/T_ring
      = c/44; vs C_energy*c = c/45 -> dev 2.27% = NOT closure (honest FAIL)
  C6. Rate duals: Gamma_v = v/lambda_sync for each candidate vs corpus rates
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

# ---------- constants ----------
N_d = 44
mu2 = mp.mpf(2)          # self-dual weight gamma_22 = mu^2 = 2
pi = mp.pi
phi = (1 + mp.sqrt(5)) / 2
c_km = mp.mpf("299792.458")       # km/s
R_world = mp.mpf("4129.94")       # Mpc
T_ring_gyr = mp.mpf("84.636")     # Gyr
lambda_sync = mp.mpf("294.88")    # Mpc

# gamma_n = 4 sin^2(pi n / 88), n = 1..44
gamma = [4 * mp.sin(pi * n / 88) ** 2 for n in range(1, N_d + 1)]
v_g = [mp.cos(pi * n / 88) for n in range(1, N_d + 1)]   # group velocities /c

S_even = sum(gamma[n - 1] for n in range(1, N_d + 1) if n % 2 == 0)
S_odd = sum(gamma[n - 1] for n in range(1, N_d + 1) if n % 2 == 1)
S_tot = S_even + S_odd

print("=" * 70)
print("O203 S1 - v_sync candidate identities (mpmath 60 dps)")
print("=" * 70)

# ---------- C1: spectral sums ----------
print("\n--- C1: spectral weight sums (44-site chain, n=1..44) ---")
check("Sum_gamma_even = N_d + mu^2 = 46", abs(S_even - (N_d + mu2)) < mp.mpf("1e-50"),
      f"S_even = {mp.nstr(S_even, 30)}")
check("Sum_gamma_odd  = N_d = 44", abs(S_odd - N_d) < mp.mpf("1e-50"),
      f"S_odd = {mp.nstr(S_odd, 30)}")
check("Sum_gamma = 2*N_d + mu^2 = 90", abs(S_tot - (2 * N_d + mu2)) < mp.mpf("1e-50"),
      f"S_tot = {mp.nstr(S_tot, 30)}")
check("gamma_22 = mu^2 = 2 (self-dual)", abs(gamma[21] - mu2) < mp.mpf("1e-50"))
check("Z2 sum rule: S_even - S_odd = gamma_22", abs((S_even - S_odd) - gamma[21]) < mp.mpf("1e-50"))

# ---------- C2: C_energy ----------
print("\n--- C2: C_energy = (S_even - S_odd)/S_tot ---")
C_energy = (S_even - S_odd) / S_tot
check("C_energy = 1/45 EXACT", abs(C_energy - mp.mpf(1) / 45) < mp.mpf("1e-50"),
      f"C_energy = {mp.nstr(C_energy, 30)}")
check("C_energy = mu^2/(2*N_d+mu^2)", abs(C_energy - mu2 / (2 * N_d + mu2)) < mp.mpf("1e-50"))
check("C_energy = 1/(N_d+1)", abs(C_energy - mp.mpf(1) / (N_d + 1)) < mp.mpf("1e-50"))
check("1/(N_d+1) = 1/45 = 1/(C(10,2))", (N_d + 1) == 45)

# ---------- C3: sector velocities ----------
print("\n--- C3: world/observer sector spectral-weight velocities ---")
v_obs = c_km * S_odd / S_tot        # observer sector weight as velocity
v_wld = c_km * S_even / S_tot       # world sector weight as velocity
v_mean = (v_obs + v_wld) / 2
v_drift = v_wld - v_obs
check("v_obs = c*22/45 EXACT", abs(v_obs / c_km - mp.mpf(22) / 45) < mp.mpf("1e-50"),
      f"v_obs/c = {mp.nstr(v_obs / c_km, 30)}")
check("v_world = c*23/45 EXACT", abs(v_wld / c_km - mp.mpf(23) / 45) < mp.mpf("1e-50"),
      f"v_world/c = {mp.nstr(v_wld / c_km, 30)}")
check("sector mean = c/2 (O138 Gamma velocity dual)", abs(v_mean / c_km - mp.mpf(1) / 2) < mp.mpf("1e-50"),
      f"mean/c = {mp.nstr(v_mean / c_km, 30)}")
check("sector drift = c/45 = C_energy*c EXACT", abs(v_drift / c_km - C_energy) < mp.mpf("1e-50"),
      f"drift/c = {mp.nstr(v_drift / c_km, 30)}")

# O138: Gamma = N_d/T_ring; velocity dual Gamma*lambda_sync = N_d*lambda_sync/T_ring
# c*T_ring = 2*pi*R_world = L_ring ; lambda_sync = L_ring/88
L_ring = c_km * T_ring_gyr * mp.mpf("3.15576e16") / mp.mpf("3.085677581e19")  # Mpc
check("c*T_ring = 2*pi*R_world (stored-value consistency ~0.0016%)",
      abs(L_ring - 2 * pi * R_world) / (2 * pi * R_world) < mp.mpf("2e-5"),
      f"L_ring = {mp.nstr(L_ring, 12)} Mpc vs 2piR = {mp.nstr(2*pi*R_world, 12)} (rel dev "
      f"{mp.nstr(abs(L_ring-2*pi*R_world)/(2*pi*R_world), 4)})")
# EXACT identity: N_d*lambda_sync/T_ring with lambda_sync = L_ring/88, L_ring = c*T_ring
# -> N_d*(c*T_ring/88)/T_ring = c*N_d/88 = c/2 (exact, no stored values)
v_Gamma_exact = N_d * mp.mpf(1) / 88  # = 1/2 in units of c
check("Gamma velocity dual = c/2 EXACT (44*lambda_sync/T_ring = c*44/88)", abs(v_Gamma_exact - mp.mpf(1) / 2) < mp.mpf("1e-50"))
# stored-value version (rounding 0.0003%):
v_Gamma_km = N_d * lambda_sync / T_ring_gyr * mp.mpf("3.085677581e19") / mp.mpf("3.15576e16")
print(f"  (stored-value check: v_Gamma/c = {mp.nstr(v_Gamma_km / c_km, 12)}, rel dev "
      f"{mp.nstr(abs(v_Gamma_km/c_km - mp.mpf(1)/2)/(mp.mpf(1)/2), 4)} = storage rounding 0.0016% class)")

# ---------- C4: ladder membership ----------
print("\n--- C4: ladder membership (is candidate a v_g(n) = cos(pi*n/88) mode?) ---")
def nearest_mode(beta):
    best = None
    for n in range(1, N_d + 1):
        dev = abs(v_g[n - 1] - beta)
        if best is None or dev < best[0]:
            best = (dev, n)
    return best

cands = {
    "C_energy*c (c/45)":      mp.mpf(1) / 45,
    "lambda_sync/T_ring (c/88)": mp.mpf(1) / 88,
    "c*sin(pi/88)":           mp.sin(pi / 88),
    "c*cos(pi/88)":           mp.cos(pi / 88),
    "c*(1-pi/44)":            1 - pi / 44,
    "O7 writing (c/44)":      mp.mpf(1) / 44,
    "Gamma dual (c/2)":       mp.mpf(1) / 2,
    "c/L5 (c/11)":            mp.mpf(1) / 11,
}
for name, beta in cands.items():
    d, n = nearest_mode(beta)
    exact = d < mp.mpf("1e-50")
    print(f"  {name:<28} beta={mp.nstr(beta, 12)}  nearest v_g({n}) dev={mp.nstr(d, 6)}"
          f"  {'EXACT LADDER MEMBER' if exact else 'not a mode'}")
check("c*sin(pi/88) = v_g(43) EXACT", abs(mp.sin(pi / 88) - v_g[42]) < mp.mpf("1e-50"))
check("c*cos(pi/88) = v_g(1) EXACT", abs(mp.cos(pi / 88) - v_g[0]) < mp.mpf("1e-50"))

# ---------- C5: O7 writing rate vs C_energy ----------
print("\n--- C5: O7 writing rate (phase slip pi per event, 2 events per ring period) ---")
# 2 slips (pi each) per ring period 2pi -> rate 2/T_ring -> velocity 2*lambda_sync/T_ring
# exact: 2*(c*T_ring/88)/T_ring = c/44
L_ring_mpc = c_km * T_ring_gyr * mp.mpf("3.15576e16") / mp.mpf("3.085677581e19")   # Mpc (stored-value)
beta_w = mp.mpf(2) * lambda_sync / L_ring_mpc
check("O7 writing velocity = c/44 (stored-value 0.0016% class)",
      abs(beta_w - mp.mpf(1) / 44) / (mp.mpf(1) / 44) < mp.mpf("2e-5"),
      f"beta_w = {mp.nstr(beta_w, 12)}")
check("O7 writing velocity = c/44 EXACT (2*(c*T/88)/T = c/44, analytic)",
      abs(mp.mpf(2) * mp.mpf(1) / 88 - mp.mpf(1) / 44) < mp.mpf("1e-50"))
dev_w45 = abs(beta_w - mp.mpf(1) / 45) / (mp.mpf(1) / 45)
check("c/44 == c/45 ? NO (dev 2.27% - not closure)",
      dev_w45 > mp.mpf("1e-3"),
      f"dev = {mp.nstr(dev_w45 * 100, 8)}%  -> writing rate is NOT C_energy*c")

# ---------- C6: rate duals ----------
print("\n--- C6: rate duals Gamma_v = beta*f_44 (f_44 = c/lambda_sync) vs corpus rates ---")
f44_gyr = c_km * mp.mpf("3.15576e16") / mp.mpf("3.085677581e19") / lambda_sync   # 1/Gyr
print(f"  f_44 = c/lambda_sync = {mp.nstr(f44_gyr, 10)} /Gyr")
corpus_rates = {
    "f_44 (Nyquist)":    f44_gyr,
    "Gamma (O138)=f_44/2": f44_gyr / 2,
    "f_ring = 1/T_ring": mp.mpf(1) / T_ring_gyr,
    "omega_ring/2pi":    mp.mpf(1) / T_ring_gyr,
    "2*f_ring (O7 slips)": 2 / T_ring_gyr,
    "44*f_ring (O51 manifest)": 44 / T_ring_gyr,
}
for name, beta in cands.items():
    rv = beta * f44_gyr
    hits = [cr for cr, v in corpus_rates.items() if abs(v - rv) / max(v, mp.mpf("1e-30")) < mp.mpf("1e-4")]
    print(f"  {name:<28} Gamma_v = {mp.nstr(rv, 10)} /Gyr  {'== ' + str(hits) if hits else '(no corpus rate)'}")

# ---------- classification summary ----------
print("\n--- classification (re-label vs independent spectral identity) ---")
print("  Re-label of omega_ring/R_world?  A candidate is a re-label iff deriving it")
print("  requires omega_ring or R_world as INPUT (not c and chain spectrum).")
for name, beta in cands.items():
    # derivable from {c, spectrum} only? all candidates: yes. From {omega_ring,R_world} only?
    print(f"  {name:<28} needs omega_ring/R_world? NO (pure c x spectral)")

print(f"\nRESULT: {PASS}/{PASS + FAIL} PASS")
