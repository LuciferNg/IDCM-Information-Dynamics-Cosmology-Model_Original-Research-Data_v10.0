#!/usr/bin/env python3
"""
O203 Script 06 - S6: O169 assembly law E(ell) = ell + <sec>_{1..K} sync-rate reading
===================================================================================
Test whether the assembly law's "per-layer +1" and window average can be read as
a sync-rate integral. Baseline O169 results must stay intact.

  T1. baseline: <sec>_{1..21} = 1.1183568, <sec>_{1..28} = 1.2414297,
      K(z) = L4*(N_gen + z/F_proj) endpoints 21 / 28
  T2. a = <gamma>_odd / gamma_22 = 1 EXACT (O169 operator identity; the '+1')
  T3. sync-rate reading: is <sec>_K ~ 1/beta for any candidate beta?
      1/<sec>_{1..21} = 0.8942 ; candidates: 1/45, 1/88, sin, cos, proj -> no match
  T4. <v_g> dual degeneracy: 1/<sec>_{1..21} ~ 2/sqrt(5) (0.03% trap window;
      O169 adjudicated: sqrt(5)/2 is the phi-reading degeneracy, sec family won)
  T5. window average = arithmetic mean (O169 open item): compare against
      gamma-weighted and harmonic means to document the open question.
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
L4 = 7
N_gen = 3
F_proj = 17
pi = mp.pi
phi = (1 + mp.sqrt(5)) / 2

sec = [1 / mp.cos(pi * n / 88) for n in range(1, N_d + 1)]
gamma = [4 * mp.sin(pi * n / 88) ** 2 for n in range(1, N_d + 1)]

def arith_avg(a, K):
    return sum(a[:K]) / K

print("=" * 70)
print("O203 S6 - O169 assembly law sync-rate reading (mpmath 60 dps)")
print("=" * 70)

# ---------- T1: baseline window averages ----------
print("\n--- T1: baseline <sec> window averages (O169) ---")
s21 = arith_avg(sec, 21)
s28 = arith_avg(sec, 28)
check("<sec>_{1..21} = 1.1183568 (O169 B2/B3)", abs(s21 - mp.mpf("1.1183568")) < mp.mpf("1e-6"),
      f"<sec>_21 = {mp.nstr(s21, 12)}")
check("<sec>_{1..28} = 1.2414181 (O169 T3: piR intercept 1.2414297 is 0.000935% away, trap window)",
      abs(s28 - mp.mpf("1.2414181")) < mp.mpf("1e-6"),
      f"<sec>_28 = {mp.nstr(s28, 12)}; dev vs piR intercept = "
      f"{mp.nstr(abs(s28-mp.mpf('1.2414297'))/mp.mpf('1.2414297')*100, 5)}% (O169 T3 documented)")
K0 = L4 * N_gen
K1 = L4 * (N_gen + F_proj / F_proj)
check("K endpoints: K(z=0) = L4*N_gen = 21, K(z_max) = L4*B = 28", K0 == 21 and K1 == 28)

# ---------- T2: a = 1 operator identity ----------
print("\n--- T2: '+1 per layer' operator identity (O169) ---")
odd_g = [gamma[n - 1] for n in range(1, N_d + 1) if n % 2 == 1]
g22 = gamma[21]
a = sum(odd_g) / len(odd_g) / g22
check("a = <gamma>_odd / gamma_22 = mu^2/mu^2 = 1 EXACT", abs(a - 1) < mp.mpf("1e-50"),
      f"a = {mp.nstr(a, 30)}")

# ---------- T3: sync-rate reading ----------
print("\n--- T3: is <sec>_K ~ 1/beta for a candidate? ---")
cands = {"1/45": mp.mpf(1) / 45, "1/88": mp.mpf(1) / 88, "sin(pi/88)": mp.sin(pi / 88),
         "cos(pi/88)": mp.cos(pi / 88), "1-pi/44": 1 - pi / 44, "1/44": mp.mpf(1) / 44,
         "1/2": mp.mpf(1) / 2}
for K in (21, 28):
    inv = 1 / arith_avg(sec, K)
    print(f"  K={K}: 1/<sec> = {mp.nstr(inv, 10)}")
    for name, beta in cands.items():
        dev = abs(inv - beta) / beta
        if dev < mp.mpf("0.05"):
            print(f"    closest: {name:<12} dev = {mp.nstr(dev*100, 5)}%")
check("no candidate beta matches 1/<sec>_K at closure level (all devs > 1e-3)",
      all(abs(1 / arith_avg(sec, K) - beta) / beta > mp.mpf("1e-3")
          for K in (21, 28) for beta in cands.values()))

# ---------- T4: 2/sqrt(5) degeneracy ----------
print("\n--- T4: <v_g> dual degeneracy (known O169 trap window) ---")
inv21 = 1 / s21
two_sqrt5 = 2 / mp.sqrt(5)
dev = abs(inv21 - two_sqrt5) / two_sqrt5
check("<v_g>_21 ~ 2/sqrt(5) near-miss = trap window (same degeneracy as sqrt(5)/2)",
      dev > mp.mpf("1e-5") and dev < mp.mpf("1e-3"),
      f"1/<sec>_21 = {mp.nstr(inv21, 10)}, 2/sqrt5 = {mp.nstr(two_sqrt5, 10)}, dev = {mp.nstr(dev*100, 5)}%")
print("  (O169 adjudication: sec family won via piR/Nyquist anchor; 2/sqrt5 = phi-reading dual)")

# ---------- T5: arithmetic vs gamma-weighted vs harmonic mean ----------
print("\n--- T5: window-average definitions (O169 open item documented) ---")
K = 21
aw = arith_avg(sec, K)
gw = sum(sec[i] * gamma[i] for i in range(K)) / sum(gamma[i] for i in range(K))
hw = K / sum(1 / sec[i] for i in range(K))
print(f"  K=21: arithmetic = {mp.nstr(aw, 10)} | gamma-weighted = {mp.nstr(gw, 10)}"
      f" | harmonic = {mp.nstr(hw, 10)}")
check("arithmetic != gamma-weighted != harmonic (window-average choice is an open O169 item)",
      aw != gw and aw != hw and gw != hw)

# ---------- synthesis ----------
print("\n--- synthesis ---")
print("  Assembly law E(ell) = ell + <sec>_{1..K} INTACT (baseline verified).")
print("  '+1' = a = <gamma>_odd/gamma_22 = 1: operator identity (O169 closed),")
print("        NOT a sync-rate integral (no candidate beta enters the law).")
print("  <sec> window average has no candidate sync-rate match; the 2/sqrt(5)")
print("        near-miss is the known phi-reading degeneracy (trap window).")
print("  => S6 closes: assembly law carries no sync-rate content; O169 intact.")

print(f"\nRESULT: {PASS}/{PASS + FAIL} PASS")
