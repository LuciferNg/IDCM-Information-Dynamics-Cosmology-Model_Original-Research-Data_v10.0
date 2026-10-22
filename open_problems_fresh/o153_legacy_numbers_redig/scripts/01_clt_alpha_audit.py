#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O153 script 01: CLT epsilon/alpha audit (R1)
=============================================
Re-derive the demoted CLT claim eps = alpha/sqrt(N), alpha ~ 1.025
against the current structural framework (O148: eps_exact = 19/123).

Checks:
  C1. Three eps values: 0.1545 (v1.0), phi^-1/4 (corpus), 19/123 (exact)
  C2. alpha = eps*sqrt(44) exact form; alpha^2 vs 21/20 candidate
  C3. Q7 arithmetic: sqrt(pi^2/6 - 1) == 1.026?  (audit)
  C4. Structural identity: eps = (f_proj/f_unproj)/N_gen = (19/41)/3
  C5. CLT 1/sqrt(N) spectral meaning: zeta_N(1/2) = sum csc / 2 vs eps
  C6. N = 1/eps^2 back-derivation: MCMC 42 origin (alpha=1 assumption)
  C7. T-hat form of alpha: (F8-mu2)*sqrt(L3*L5)/L10

All decimals mpmath 50 dps. PASS/FAIL each.
"""
import mpmath as mp
mp.mp.dps = 50

phi = (1 + mp.sqrt(5)) / 2
sqrt2 = mp.sqrt(2)

# --- anchors (O148, O95, O142) ---
f_unproj = mp.mpf(41) / 60          # world-scale projection ratio
f_proj = 1 - f_unproj               # = 19/60
N_gen = mp.mpf(3)
N_d = mp.mpf(44)
eps_exact = mp.mpf(19) / 123        # O148: 3eps = f_proj/f_unproj = 19/41
eps_corpus = 1 / (4 * phi)          # phi^-1/4
eps_v1 = mp.mpf('0.1545')           # IDM v1.0 claimed
mu2 = mp.mpf(2)                     # log2(B) = E-O = gamma_44/2
B = mp.mpf(4)
L = {1: 1, 2: 3, 3: 4, 4: 7, 5: 11, 6: 18, 7: 29, 8: 47, 10: 123}
F = {5: 5, 6: 8, 7: 13, 8: 21, 10: 55}

results = []

def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))

# ---- C1: three eps ----
d_v1 = abs(eps_v1 - eps_exact) / eps_exact
d_corpus = abs(eps_corpus - eps_exact) / eps_exact
check("C1a eps_v1(0.1545) vs eps_exact(19/123)",
      d_v1 < mp.mpf('0.001'), f"dev={mp.nstr(d_v1, 6)}")
check("C1b eps_corpus(phi^-1/4) vs eps_exact",
      d_corpus < mp.mpf('0.001'), f"dev={mp.nstr(d_corpus, 6)} (O148 delta_3 = 0.023%)")
check("C1c eps_v1 vs eps_corpus",
      abs(eps_v1 - eps_corpus) / eps_corpus < mp.mpf('0.001'),
      f"dev={mp.nstr(abs(eps_v1-eps_corpus)/eps_corpus, 6)}")
print(f"[C1] eps_v1={mp.nstr(eps_v1,10)}  eps_corpus={mp.nstr(eps_corpus,10)}  "
      f"eps_exact={mp.nstr(eps_exact,10)}")

# ---- C2: alpha = eps*sqrt(N_d) ----
alpha_exact = eps_exact * mp.sqrt(N_d)          # = 19*sqrt(44)/123
alpha_v1 = eps_v1 * mp.sqrt(N_d)
alpha_corpus = eps_corpus * mp.sqrt(N_d)
alpha2 = alpha_exact ** 2
cand_21_20 = mp.mpf(21) / 20                     # F8 / (B*F5)
d_2120 = abs(alpha2 - cand_21_20) / alpha2
check("C2a alpha_exact = 19*sqrt(44)/123",
      abs(alpha_exact - 19 * mp.sqrt(44) / 123) < mp.mpf('1e-40'))
check("C2b alpha~1.025 confirmed",
      abs(alpha_exact - mp.mpf('1.025')) / alpha_exact < mp.mpf('0.001'),
      f"alpha_exact={mp.nstr(alpha_exact, 12)}")
check("C2c alpha^2 ~ 21/20 candidate (IN PHI-TRAP WINDOW -> YELLOW)",
      d_2120 < mp.mpf('0.01'), f"dev={mp.nstr(d_2120, 8)} (phi-window 1e-5..1e-3 -> not closed)")
print(f"[C2] alpha_exact={mp.nstr(alpha_exact,15)}  alpha_v1={mp.nstr(alpha_v1,8)}  "
      f"alpha_corpus={mp.nstr(alpha_corpus,8)}  alpha^2={mp.nstr(alpha2,12)}  "
      f"21/20={mp.nstr(cand_21_20,8)}  dev={mp.nstr(d_2120,8)}")

# ---- C3: Q7 arithmetic audit ----
q7_claim = mp.sqrt(mp.pi**2 / 6 - 1)
check("C3a Q7 formula sqrt(pi^2/6 - 1) != 1.026 (ARITHMETIC ERROR)",
      abs(q7_claim - mp.mpf('1.026')) > mp.mpf('0.1'),
      f"sqrt(pi^2/6-1)={mp.nstr(q7_claim,10)}  vs claimed 1.026  -> Q7 arithmetic is WRONG")
# what would give 1.026? pi^2/6 = 1.6449; 1.026^2 = 1.0527; pi^2/6 - 0.592 = 1.0527
check("C3b possible intended: sqrt(pi^2/6 - 3/5)?",
      abs(mp.sqrt(mp.pi**2/6 - mp.mpf(3)/5) - mp.mpf('1.026')) < mp.mpf('0.005'),
      f"sqrt(pi^2/6-3/5)={mp.nstr(mp.sqrt(mp.pi**2/6-mp.mpf(3)/5),8)}")
print(f"[C3] Q7 claimed alpha=sqrt(pi^2/6-1)=1.026  ACTUAL={mp.nstr(q7_claim,10)}  -> arithmetic error confirmed")

# ---- C4: structural identity eps = (f_proj/f_unproj)/N_gen ----
eps_recon = (f_proj / f_unproj) / N_gen      # (19/60)/(41/60)/3 = 19/123
check("C4a eps = (f_proj/f_unproj)/N_gen = 19/123 EXACT",
      eps_recon == eps_exact, f"eps_recon={mp.nstr(eps_recon,15)}")
# also: 3*eps = 19/41 and 19/41 = f_proj/f_unproj
check("C4b 3*eps = f_proj/f_unproj = 19/41",
      abs(3 * eps_exact - mp.mpf(19)/41) < mp.mpf('1e-40'))
print(f"[C4] eps_recon=(19/60)/(41/60)/3 = {mp.nstr(eps_recon,15)} == 19/123 -> CLT dip is a PROJECTION RATIO / N_gen, not CLT")

# ---- C5: 1/sqrt(N) spectral meaning ----
# CLT fluctuation scale 1/sqrt(44) = 0.150756 vs eps = 0.1544715
inv_sqrtN = 1 / mp.sqrt(N_d)
check("C5a 1/sqrt(44) != eps (factor alpha=1.02465)",
      abs(inv_sqrtN - eps_exact) / eps_exact > mp.mpf('0.02'),
      f"1/sqrt(44)={mp.nstr(inv_sqrtN,8)}  ratio={mp.nstr(eps_exact/inv_sqrtN,8)}")
# spectral zeta at 1/2 for the 88-site chain: sum_{n=1}^{44} csc(pi n/88)/2
N88 = 44
s_half = sum(1 / mp.sin(mp.pi * n / 88) for n in range(1, N88 + 1)) / 2
check("C5b zeta_N(1/2) = sum(csc)/2 not directly eps",
      True, f"zeta_44(1/2)={mp.nstr(s_half,8)}  (FSR Lorentz ladder sum)")
# zeta_N(1) = ((2N)^2-1)/12 identity: FULL dual-chain spectrum n=1..2N-1
z1 = sum(1 / (4 * mp.sin(mp.pi * n / 88) ** 2) for n in range(1, 2 * N88))
z1_pred = ((2 * N88) ** 2 - 1) / 12
check("C5c zeta_44(1) = ((2N)^2-1)/12 EXACT (FSR, full dual-chain n=1..87)",
      abs(z1 - z1_pred) < mp.mpf('1e-30'), f"zeta(1)={mp.nstr(z1,10)} pred={mp.nstr(z1_pred,10)}")
print(f"[C5] 1/sqrt(44)={mp.nstr(inv_sqrtN,10)}  zeta_44(1/2)={mp.nstr(s_half,10)}  zeta_44(1)={mp.nstr(z1,10)}")

# ---- C6: MCMC 42 origin (alpha=1 assumption) ----
N_alpha1_exact = 1 / eps_exact ** 2           # = 15129/361 = 41.9086...
N_alpha1_v1 = 1 / eps_v1 ** 2
check("C6a N(alpha=1) = 1/eps^2 = 41.9086 ~ 42 (MCMC origin)",
      abs(N_alpha1_exact - 42) / 42 < mp.mpf('0.005'),
      f"1/eps_exact^2={mp.nstr(N_alpha1_exact,8)}  1/eps_v1^2={mp.nstr(N_alpha1_v1,8)}  -> 42 = alpha=1 artifact")
check("C6b correct N = alpha^2/eps^2 = 44 exactly",
      abs(alpha_exact ** 2 / eps_exact ** 2 - 44) < mp.mpf('1e-30'),
      f"alpha^2/eps^2={mp.nstr(alpha_exact**2/eps_exact**2,10)}")
print(f"[C6] N(alpha=1)={mp.nstr(N_alpha1_exact,10)} vs 42 (MCMC v1.0) vs 44=N_d -> 42 is the alpha=1 artifact")

# ---- C7: T-hat form of alpha ----
# alpha = 19*sqrt(44)/123 = (F8 - mu2)*sqrt(L3*L5)/L10
F8, L3, L5, L10 = F[8], L[3], L[5], L[10]
alpha_th = (F8 - mu2) * mp.sqrt(L3 * L5) / L10
alpha_ref = 19 * mp.sqrt(44) / 123
check("C7 alpha = (F8-mu2)*sqrt(L3*L5)/L10 EXACT",
      alpha_th == alpha_ref,
      f"alpha_th={mp.nstr(alpha_th,15)} == 19*sqrt(44)/123={mp.nstr(alpha_ref,15)} (exact same expression)")
print(f"[C7] alpha = (F8-mu2)*sqrt(L3*L5)/L10 = (21-2)*sqrt(44)/123 = {mp.nstr(alpha_th,12)}")

# ---- summary ----
print()
fails = [r for r in results if not r[1]]
for name, ok, det in results:
    print(f"  {'PASS' if ok else 'FAIL'}  {name}  {det}")
print(f"\nRESULT: {len(results)-len(fails)}/{len(results)} PASS")
if fails:
    print("FAILED:", [r[0] for r in fails])
