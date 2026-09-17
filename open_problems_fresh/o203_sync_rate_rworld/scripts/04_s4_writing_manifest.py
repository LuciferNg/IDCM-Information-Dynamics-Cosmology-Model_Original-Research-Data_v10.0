#!/usr/bin/env python3
"""
O203 Script 04 - S4: manifest/writing rate family (O7 + O51 + O138)
==================================================================
The ring has 88 sites, period T_ring (phase 2pi). Every writing/manifest process
is an integer count of events per ring period. Velocity dual of a rate R = m/T_ring:
  v = m * lambda_sync / T_ring = (m/88) * c   (lambda_sync = L_ring/88, L_ring = c*T_ring)

Family (m = events per period):
  m=1   -> c/88 : single site refresh per period (candidate #2's own identity)
  m=2   -> c/44 : O7 phase-slip writing (2 slips of pi per 2pi period)
  m=44  -> c/2  : O138 Gamma = N_d/T_ring = f_44/2 (Z2 pairing / manifest full-scan)
  m=88  -> c    : f_44 Nyquist (88 site-visits per period)

Question: does C_energy*c = c/45 belong to this family? 45 is NOT a valid event count
(45 > 88/2... check: m must be integer; 45 gives 45/88 = 0.5114c ~ v_world = 23/45
near-miss 0.05% = trap window). c/45 is a SPECTRAL drift, not a per-period rate.
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
T_ring = mp.mpf("84.636")          # Gyr
lambda_sync = mp.mpf("294.88")     # Mpc
c_km = mp.mpf("299792.458")
c_mpcgyr = c_km * mp.mpf("3.15576e16") / mp.mpf("3.085677581e19")  # Mpc/Gyr

print("=" * 70)
print("O203 S4 - manifest/writing rate family (mpmath 60 dps)")
print("=" * 70)

# ---------- process-rate family ----------
print("\n--- process-rate family: v(m) = m*lambda_sync/T_ring = (m/88)*c ---")
family = [(1, "1 site/period (seed refresh)"),
          (2, "O7 phase-slip writing (2*pi per 2pi)"),
          (44, "O138 Gamma = N_d/T_ring = f_44/2 (Z2 pairing/full manifest)"),
          (88, "f_44 Nyquist (88 site-visits/period)")]
for m, desc in family:
    beta = mp.mpf(m) / 88
    print(f"  m={m:<3} {desc:<52} v/c = {mp.nstr(beta, 10)}")

check("m=2 -> c/44 EXACT (O7)", abs(mp.mpf(2) / 88 - mp.mpf(1) / 44) < mp.mpf("1e-50"))
check("m=44 -> c/2 EXACT (O138 Gamma)", abs(mp.mpf(44) / 88 - mp.mpf(1) / 2) < mp.mpf("1e-50"))
check("m=88 -> c EXACT (f_44)", abs(mp.mpf(88) / 88 - 1) < mp.mpf("1e-50"))

# ---------- numerical verification of rates ----------
print("\n--- numerical rates (1/Gyr) ---")
f_ring = mp.mpf(1) / T_ring
f44_gyr = c_mpcgyr / lambda_sync
Gamma_gyr = N_d / T_ring
w_rate = mp.mpf(2) / T_ring
print(f"  f_ring   = 1/T_ring        = {mp.nstr(f_ring, 10)} /Gyr")
print(f"  2*f_ring (O7 writing)      = {mp.nstr(w_rate, 10)} /Gyr")
print(f"  Gamma    = N_d/T_ring (O138)= {mp.nstr(Gamma_gyr, 10)} /Gyr")
print(f"  f_44     = c/lambda_sync    = {mp.nstr(f44_gyr, 10)} /Gyr")
check("Gamma = N_d/T_ring = 44*f_ring", abs(Gamma_gyr - 44 * f_ring) / (44 * f_ring) < mp.mpf("1e-9"))
check("f_44 = 88*f_ring (stored-value 0.0016% class)",
      abs(f44_gyr - 88 * f_ring) / (88 * f_ring) < mp.mpf("2e-5"),
      f"dev = {mp.nstr(abs(f44_gyr-88*f_ring)/(88*f_ring), 4)}")
check("Gamma = f_44/2 (stored-value class)",
      abs(Gamma_gyr - f44_gyr / 2) / (f44_gyr / 2) < mp.mpf("2e-5"))

# ---------- C_energy rate dual ----------
print("\n--- C_energy*c rate dual vs family ---")
C_rate = (mp.mpf(1) / 45) * f44_gyr
print(f"  C_energy*c rate dual = f_44/45 = {mp.nstr(C_rate, 10)} /Gyr")
print(f"  vs family rates: f_ring={mp.nstr(f_ring,8)}, 2f_ring={mp.nstr(2*f_ring,8)},"
      f" Gamma={mp.nstr(Gamma_gyr,8)}, f_44={mp.nstr(f44_gyr,8)}")
check("f_44/45 is NOT any family rate (no corpus match)",
      all(abs(C_rate - r) / r > mp.mpf("1e-4") for r in [f_ring, 2 * f_ring, Gamma_gyr, f44_gyr]))

# ---------- m=45 near-miss ----------
print("\n--- m=45 interpretation check ---")
beta45m = mp.mpf(45) / 88
v_world = mp.mpf(23) / 45
dev = abs(beta45m - v_world) / v_world
check("45/88 ~ v_world = 23/45 near-miss 0.05% = trap window (NOT closure)",
      dev > mp.mpf("1e-4") and dev < mp.mpf("1e-2"),
      f"45/88 = {mp.nstr(beta45m, 10)}, 23/45 = {mp.nstr(v_world, 10)}, rel dev = {mp.nstr(dev*100, 5)}%")
print("  (45/88 - 23/45 = (2025-2024)/(88*45) = 1/3960: pure rational near-miss)")

# ---------- synthesis ----------
print("\n--- synthesis ---")
print("  Writing/manifest rates ALL belong to m/88 family (integer events per period):")
print("    c/88 (1), c/44 (2), c/2 (44), c (88)")
print("  C_energy*c = c/45 is a SPECTRAL DRIFT (world-observer weight imbalance),")
print("  NOT a per-period process rate: 45 is not an event count tied to T_ring.")
print("  => c/45 rejected as v_sync (no process), retained as spectral identity.")

print(f"\nRESULT: {PASS}/{PASS + FAIL} PASS")
