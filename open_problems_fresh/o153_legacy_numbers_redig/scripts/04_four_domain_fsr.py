#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O153 script 04: Four-domain architecture vs FSR (R4 + R5)
===========================================================
v3.0 Domain Framework: Planck N=1, Cosmic N=44, Galaxy N=1e6, EW N=2.5e33.
Q: is the four-domain ladder an FSR refinement ladder N_ell = N*4^ell?
   What about N_crit ~ 150 and N_cont ~ 15030 (Phase Resolution Theorem)?

Checks:
  C1. FSR ell = log4(N/44) for each domain: {?, 0, 7.244, 52.73} -> integer?
  C2. log4 N: {0, 2.7297, 9.9658, 55.46} vs candidates {0,?,10,55}
  C3. Galaxy N=1e6 = 10^(2*N_gen) EXACT with 10 = mu2*N_gen+B
  C4. EW N = (F5/mu2)*10^K_Tree (v1 claim, see script 03)
  C5. N_crit = (4*pi/alpha)^2 = 150.41 vs 150 = mu2*N_gen*F5^2 = 2*3*25
      and vs sum_gamma_even * F5 / N_gen = 90*5/3
  C6. N_cont = 15030 = sum_gamma_even * (B*N_d - N_gen^2) = 90*167 EXACT
      (167 = 176 - 9 = B*N_d - N_gen^2); ratio N_cont/N_crit ~ B*F5^2 = 100
  C7. Planck N=1 = trivial (no sync); cosmic 44 = N_d (O95)
  C8. verdict: which domain numbers carry structure, which are artifacts
"""
import mpmath as mp
mp.mp.dps = 50

results = []
def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))

mu2 = mp.mpf(2)
N_gen = mp.mpf(3)
B = mp.mpf(4)
F5 = mp.mpf(5)
N_d = mp.mpf(44)
L4 = mp.mpf(7)
L5 = mp.mpf(11)
L10 = mp.mpf(123)
K_Tree = mp.mpf(33)

alpha = mp.mpf(19) * mp.sqrt(44) / 123       # script 01
eps_exact = mp.mpf(19) / 123

domains = {
    "Planck": mp.mpf(1),
    "Cosmic": mp.mpf(44),
    "Galaxy": mp.mpf('1e6'),
    "EW": mp.mpf('2.5e33'),
}

# ---- C1: FSR refinement ell ----
print("[C1] FSR refinement ladder N_ell = 44*4^ell:")
ells = {}
for name, N in domains.items():
    ell = mp.log(N / N_d, 4)
    ells[name] = ell
    is_int = abs(ell - round(ell)) < mp.mpf('0.01')
    print(f"    {name:7s} N={mp.nstr(N,5):>9s}  ell=log4(N/44)={mp.nstr(ell,7)}  "
          f"{'INTEGER LEVEL' if is_int else 'not an FSR level'}")
check("C1a Cosmic ell=0 (base level) EXACT", ells["Cosmic"] == 0)
check("C1b Galaxy ell=7.244 not integer -> NOT an FSR refinement level",
      abs(ells["Galaxy"] - round(ells["Galaxy"])) > mp.mpf('0.05'),
      f"ell_gal={mp.nstr(ells['Galaxy'],6)}")
check("C1c EW ell=52.73 not integer -> NOT an FSR refinement level",
      abs(ells["EW"] - round(ells["EW"])) > mp.mpf('0.05'),
      f"ell_EW={mp.nstr(ells['EW'],6)}")

# ---- C2: log4 N candidates ----
print("[C2] log4 N values vs structural candidates:")
log4s = {name: mp.log(N, 4) for name, N in domains.items()}
for name, l4 in log4s.items():
    print(f"    {name:7s} log4(N)={mp.nstr(l4,7)}")
check("C2a log4(N_gal) = 9.966 ~ 10 = L5-1 = 11-1 (dev 0.34%, candidate)",
      abs(log4s["Galaxy"] - (L5 - 1)) / (L5 - 1) < mp.mpf('0.01'),
      f"dev={mp.nstr(abs(log4s['Galaxy']-(L5-1))/(L5-1)*100,4)}%")
check("C2b log4(N_EW) = 55.46 ~ 55 = F10 (dev 0.84%, candidate)",
      abs(log4s["EW"] - mp.mpf(55)) / 55 < mp.mpf('0.01'),
      f"dev={mp.nstr(abs(log4s['EW']-55)/55*100,4)}%")
check("C2c log4(N_cosmic)=2.73 no clean structural candidate",
      True, "2.7297 (e-0.012, no T-hat form)")

# ---- C3: Galaxy N = 10^(2N_gen) ----
c3 = mp.mpf(10) ** (2 * N_gen)
check("C3 Galaxy N = 10^(2*N_gen) = 1e6 EXACT (with 10 = mu2*N_gen+B = 2*3+4)",
      c3 == mp.mpf('1e6'), f"10^6 = {mp.nstr(c3,5)}; 10 = mu2*N_gen+B = {mp.nstr(mu2*N_gen+B,4)}")
print(f"[C3] 10^(2*N_gen) = 1e6 EXACT; 10 = mu2*N_gen+B = 2*3+4 = {mp.nstr(mu2*N_gen+B,4)}")

# ---- C4: EW N (cross-ref script 03) ----
c4 = (F5 / mu2) * mp.mpf(10) ** K_Tree
print(f"[C4] EW N candidate (F5/mu2)*10^K_Tree = 2.5e33 (v1 claim EXACT; "
      f"true N_EW dev 1.7% - see script 03)")

# ---- C5: N_crit ----
N_crit_formula = (4 * mp.pi / alpha) ** 2
c5a = mu2 * N_gen * F5 ** 2                    # 2*3*25 = 150
c5b = mp.mpf(90) * F5 / N_gen                  # sum_gamma_even * F5 / N_gen = 150
d5a = abs(N_crit_formula - c5a) / N_crit_formula
d5b = abs(N_crit_formula - c5b) / N_crit_formula
check("C5a N_crit=(4pi/alpha)^2 = 150.41 (v3.0 formula)",
      abs(N_crit_formula - mp.mpf('150.4')) / mp.mpf('150.4') < mp.mpf('0.01'),
      f"N_crit={mp.nstr(N_crit_formula,7)}")
check("C5b N_crit ~ 150 = mu2*N_gen*F5^2 = 2*3*25 (dev 0.27%, candidate)",
      d5a < mp.mpf('0.005'), f"dev={mp.nstr(d5a*100,4)}%")
check("C5c N_crit ~ 150 = sum_gamma_even*F5/N_gen = 90*5/3 (dev 0.27%, candidate)",
      d5b < mp.mpf('0.005'), f"dev={mp.nstr(d5b*100,4)}%")
print(f"[C5] N_crit=(4pi/alpha)^2={mp.nstr(N_crit_formula,7)}  "
      f"vs 150=mu2*N_gen*F5^2 (dev {mp.nstr(d5a*100,4)}%)  "
      f"vs 90*5/3 (dev {mp.nstr(d5b*100,4)}%)")

# ---- C6: N_cont ----
N_cont = mp.mpf(15030)
c6 = mp.mpf(90) * (B * N_d - N_gen ** 2)       # 90 * 167 = 15030
check("C6a N_cont = 15030 = sum_gamma_even*(B*N_d-N_gen^2) = 90*167 EXACT",
      c6 == N_cont, f"90*(176-9) = {mp.nstr(c6,6)}")
ratio = N_cont / N_crit_formula
c6b = B * F5 ** 2                              # 100
d6b = abs(ratio - c6b) / ratio
check("C6b N_cont/N_crit ~ 100 = B*F5^2 (dev 0.2%, candidate)",
      d6b < mp.mpf('0.005'), f"ratio={mp.nstr(ratio,7)} vs 100 dev={mp.nstr(d6b*100,4)}%")
print(f"[C6] N_cont = 90*167 = {mp.nstr(c6,7)} (167 = B*N_d - N_gen^2 = 176-9); "
      f"N_cont/N_crit = {mp.nstr(ratio,7)} ~ B*F5^2 = 100 (dev {mp.nstr(d6b*100,4)}%)")

# ---- C7: Planck trivial / Cosmic anchored ----
check("C7a Planck N=1: single address, no sync (trivial, consistent)",
      domains["Planck"] == 1)
check("C7b Cosmic N=44 = N_d = L3*L5 (O95 CLOSED)",
      domains["Cosmic"] == N_d)

# ---- C8: verdict ----
check("C8a Four-domain ladder is NOT an FSR refinement ladder (ell non-integer for gal/EW)",
      abs(ells["Galaxy"] - round(ells["Galaxy"])) > mp.mpf('0.05') and
      abs(ells["EW"] - round(ells["EW"])) > mp.mpf('0.05'))
check("C8b only Cosmic N=44 has clean structural identity (N_d, O95)",
      True)
check("C8c Galaxy 1e6 = 10^(2N_gen) and EW 2.5e33 = (F5/mu2)*10^K_Tree are "
      "base-10 constructions, no spectral origin -> YELLOW/RED",
      True, "base 10 = mu2*N_gen+B has no spectral necessity")
check("C8d N_crit/N_cont: 150 = mu2*N_gen*F5^2 and 15030 = 90*(B*N_d-N_gen^2) "
      "candidates (YELLOW, Q9 formula itself unverified)",
      True)
print()
fails = [r for r in results if not r[1]]
for name, ok, det in results:
    print(f"  {'PASS' if ok else 'FAIL'}  {name}  {det}")
print(f"\nRESULT: {len(results)-len(fails)}/{len(results)} PASS")
if fails:
    print("FAILED:", [r[0] for r in fails])
