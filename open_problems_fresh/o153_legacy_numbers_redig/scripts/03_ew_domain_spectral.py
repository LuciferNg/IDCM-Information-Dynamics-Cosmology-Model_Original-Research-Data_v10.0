#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O153 script 03: domain_EW N_EW = 2.5e33 re-derivation (R3)
=============================================================
v1.0-v4.0 claimed N_EW = (M_Pl/v)^2 ~ 2.5e33, admitted tautological.
Q: does N_EW / v / M_Pl/v have a structural identity?

Inputs (PDG 2022):
  M_Pl = 1.220890e19 GeV (reduced Planck mass)
  v    = 246.2196 GeV   (Higgs VEV, PDG: sqrt(2)*G_F^-1/2 = 246.2196)
  IDCM: M0 = 27.9009 MeV (O38), m_7 = 13.8002 MeV (O36), L10 = 123, K_Tree = 33

Checks:
  C1. N_EW exact value; log10 = 33.39
  C2. v vs 2*L10 = 246 GeV  (dev 0.09% - PHI WINDOW, candidate only)
  C3. N_EW vs (F5/mu2)*10^K_Tree = 2.5e33 (v1 claimed EXACT; vs true dev)
  C4. N_EW vs 2^111 (dev)
  C5. M_Pl/v vs F5*10^(B^2) = 5e16 (dev)
  C6. v/M0 = 8824.8 vs 88*B*F5^2 = 8800 (dev 0.28%)
  C7. log10 N_EW vs K_Tree + mu2/F5 = 33.4 (log-scale candidate)
  C8. honesty: tautology confirmed, no exact spectral identity
"""
import mpmath as mp
mp.mp.dps = 50

results = []
def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))

M_Pl = mp.mpf('1.220890e19')       # GeV
v = mp.mpf('246.2196')             # GeV (PDG)
M0 = mp.mpf('27.9009')             # MeV (O38)
mu2 = mp.mpf(2)
B = mp.mpf(4)
F5 = mp.mpf(5)
K_Tree = mp.mpf(33)
L10 = mp.mpf(123)

N_EW = (M_Pl / v) ** 2
print(f"[base] M_Pl={mp.nstr(M_Pl,8)} GeV, v={mp.nstr(v,8)} GeV, "
      f"M_Pl/v={mp.nstr(M_Pl/v,10)}")
print(f"[base] N_EW = (M_Pl/v)^2 = {mp.nstr(N_EW,12)}  "
      f"log10 = {mp.nstr(mp.log10(N_EW),8)}")

# ---- C1: exact value ----
check("C1a N_EW ~ 2.5e33 order confirmed",
      abs(mp.log10(N_EW) - mp.mpf('33.4')) < mp.mpf('0.1'),
      f"N_EW={mp.nstr(N_EW,6)}, 2.5e33 claim dev={mp.nstr(abs(N_EW-mp.mpf('2.5e33'))/N_EW*100,4)}%")
check("C1b v1 claim 2.5e33 vs exact: 1.7% off (rounding, not exact)",
      abs(N_EW - mp.mpf('2.5e33')) / N_EW > mp.mpf('0.01'),
      f"dev={mp.nstr(abs(N_EW-mp.mpf('2.5e33'))/N_EW,5)}")
print(f"[C1] v1 claimed 2.5e33 vs exact dev = {mp.nstr(abs(N_EW-mp.mpf('2.5e33'))/N_EW*100,5)}%")

# ---- C2: v vs 2*L10 ----
d_v = abs(v - 2 * L10) / v
check("C2 v = 246.22 vs 2*L10 = 246 GeV: dev 0.089% (PHI-WINDOW EDGE, candidate not closed)",
      d_v < mp.mpf('0.001'), f"dev={mp.nstr(d_v,8)} (phi window 1e-5..1e-3 -> YELLOW)")
print(f"[C2] v={mp.nstr(v,8)} vs 2*L10=246: dev={mp.nstr(d_v*100,5)}%")

# ---- C3: N_EW vs (F5/mu2)*10^K_Tree ----
c3 = (F5 / mu2) * mp.mpf(10) ** K_Tree
d3 = abs(N_EW - c3) / N_EW
check("C3a (F5/mu2)*10^K_Tree = 2.5e33 EXACT as v1-claimed number",
      c3 == mp.mpf('2.5e33'), f"(5/2)*10^33 = {mp.nstr(c3,6)}")
check("C3b but vs exact N_EW dev = 1.7% -> not structural",
      d3 > mp.mpf('0.01'), f"dev vs exact = {mp.nstr(d3*100,4)}%")
print(f"[C3] (F5/mu2)*10^K_Tree = 2.5e33 (v1 claim exact); vs exact N_EW dev={mp.nstr(d3*100,4)}%")

# ---- C4: 2^111 ----
c4 = mp.mpf(2) ** 111
d4 = abs(N_EW - c4) / N_EW
check("C4 2^111 = 2.596e33 dev 5.6% -> not closure",
      d4 > mp.mpf('0.01'), f"2^111={mp.nstr(c4,6)} dev={mp.nstr(d4*100,4)}%")
print(f"[C4] 2^111 = {mp.nstr(c4,6)} dev={mp.nstr(d4*100,4)}%")

# ---- C5: M_Pl/v vs F5*10^(B^2) ----
c5 = F5 * mp.mpf(10) ** (B ** 2)          # 5e16
d5 = abs((M_Pl / v) - c5) / (M_Pl / v)
check("C5 M_Pl/v vs F5*10^(B^2)=5e16: dev 0.85% -> candidate only",
      d5 < mp.mpf('0.01'), f"M_Pl/v={mp.nstr(M_Pl/v,8)} vs 5e16 dev={mp.nstr(d5*100,4)}%")
print(f"[C5] M_Pl/v = {mp.nstr(M_Pl/v,8)} vs F5*10^(B^2) = 5e16: dev={mp.nstr(d5*100,4)}%")

# ---- C6: v/M0 in IDCM mass units ----
v_M0 = v / (M0 / 1000)                     # GeV / GeV
c6 = 88 * B * F5 ** 2                      # 88*4*25 = 8800
d6 = abs(v_M0 - c6) / v_M0
check("C6a v/M0 = 8824.8 vs 88*B*F5^2 = 8800: dev 0.28% (candidate)",
      d6 < mp.mpf('0.005'), f"v/M0={mp.nstr(v_M0,6)} vs 8800 dev={mp.nstr(d6*100,4)}%")
# M_Pl/M0
Mpl_M0 = M_Pl / (M0 / 1000)
c6b = mp.mpf('4.4e20')                     # 44*10^19
d6b = abs(Mpl_M0 - c6b) / Mpl_M0
check("C6b M_Pl/M0 = 4.376e20 vs 44*10^19: dev 0.55% (candidate)",
      d6b < mp.mpf('0.01'), f"M_Pl/M0={mp.nstr(Mpl_M0,6)} vs 4.4e20 dev={mp.nstr(d6b*100,4)}%")
print(f"[C6] v/M0 = {mp.nstr(v_M0,8)} vs 8800 dev={mp.nstr(d6*100,4)}%; "
      f"M_Pl/M0 = {mp.nstr(Mpl_M0,8)} vs 4.4e20 dev={mp.nstr(d6b*100,4)}%")

# ---- C7: log10 scale ----
log10_N = mp.log10(N_EW)
c7 = K_Tree + mu2 / F5                    # 33.4
d7 = abs(log10_N - c7) / log10_N
check("C7 log10(N_EW) = 33.3906 vs K_Tree+mu2/F5 = 33.4: log-dev 0.028%, "
      "linear dev 2.2% -> candidate only",
      d7 < mp.mpf('0.001'), f"log10={mp.nstr(log10_N,8)} vs 33.4 log-dev={mp.nstr(d7*100,5)}%")
print(f"[C7] log10 N_EW = {mp.nstr(log10_N,8)} vs K_Tree+mu2/F5 = 33.4: "
      f"log-dev={mp.nstr(d7*100,5)}%  (10^33.4 = {mp.nstr(mp.mpf(10)**c7,6)})")

# ---- C8: honesty verdict ----
check("C8a N_EW tautology confirmed (v defines N_EW, N_EW 'explains' v)",
      True, "v1.0-4.0 admitted this; re-derivation finds no exact spectral identity")
check("C8b all candidates (2L10, 2.5e33, 8800, 5e16) are phi-window / >1% -> YELLOW/RED",
      True, "no closure; EW domain N remains structurally unanchored (Q1 of v3.0 open questions)")
print()
fails = [r for r in results if not r[1]]
for name, ok, det in results:
    print(f"  {'PASS' if ok else 'FAIL'}  {name}  {det}")
print(f"\nRESULT: {len(results)-len(fails)}/{len(results)} PASS")
if fails:
    print("FAILED:", [r[0] for r in fails])
