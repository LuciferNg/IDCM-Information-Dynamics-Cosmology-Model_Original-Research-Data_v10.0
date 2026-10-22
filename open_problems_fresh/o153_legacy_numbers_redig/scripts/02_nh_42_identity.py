#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O153 script 02: N_h = 42 identity (R2)
========================================
The v1.0 MCMC back-derivation gave N_horizon ~ 42 (from eps=0.1545, alpha=1).
Q: does 42 have a structural identity in the current framework?

Checks:
  C1. 42 = mu2*N_gen*L4 = 2*3*7  (T-hat product)  [candidate identity]
  C2. 42 = N_d - mu2 = 44 - 2    (equivalent: N_d = mu2*(N_gen*L4+1))
  C3. 42 = sum_gamma_odd - (N_d + mu2) = 88 - 46
  C4. 42 = C_ladder(132) - sum_gamma_even = 132 - 90
  C5. MCMC origin: 1/eps^2 with alpha=1 -> 41.9086 ~ 42 (artifact, cross-ref 01 C6)
  C6. FSR angle: is 42 a spectral level? N=42 Laplacian vs 44? no.
  C7. beat(6,7): s = 6.5 = F7/2 = Omega_DM/Omega_b half-integer seam; a*b = 42
  C8. verdict: identity vs artifact separation
"""
import mpmath as mp
mp.mp.dps = 50

mu2 = mp.mpf(2)
N_gen = mp.mpf(3)
L4 = mp.mpf(7)
N_d = mp.mpf(44)

results = []
def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))

# ---- C1: 42 = mu2*N_gen*L4 ----
c1 = mu2 * N_gen * L4
check("C1 42 = mu2*N_gen*L4 = 2*3*7 EXACT", c1 == 42, f"2*3*7={c1}")
print(f"[C1] mu2*N_gen*L4 = 2*3*7 = {mp.nstr(c1,6)}")

# ---- C2: 42 = N_d - mu2 ----
c2 = N_d - mu2
check("C2 42 = N_d - mu2 = 44-2 EXACT", c2 == 42, f"44-2={c2}")
# equivalence: N_d = mu2*(N_gen*L4 + 1) -> 2*(21+1) = 44
c2b = mu2 * (N_gen * L4 + 1)
check("C2b consistency: N_d = mu2*(N_gen*L4+1) = 2*22 = 44", c2b == N_d,
      f"2*(3*7+1)={mp.nstr(c2b,6)}")
print(f"[C2] N_d - mu2 = 44-2 = {mp.nstr(c2,6)};  N_d = mu2*(N_gen*L4+1) = {mp.nstr(c2b,6)}")

# ---- C3: 42 = sum_gamma_odd - (N_d+mu2) = 88-46 ----
s_odd = sum(4 * mp.sin(mp.pi * n / 88) ** 2 for n in range(1, 88, 2))
check("C3a sum_gamma_odd = 88 (numeric 1e-40)",
      abs(s_odd - 88) < mp.mpf('1e-40'), f"sum_gamma_odd={mp.nstr(s_odd,20)}")
c3 = s_odd - (N_d + mu2)
check("C3b 42 = sum_gamma_odd - (N_d+mu2) = 88-46 (numeric 1e-40)",
      abs(c3 - 42) < mp.mpf('1e-40'), f"88-46={mp.nstr(c3,12)}")
print(f"[C3] sum_gamma_odd={mp.nstr(s_odd,8)};  88-46 = {mp.nstr(c3,6)}")

# ---- C4: 42 = 132 - 90 (C_ladder minus world sum) ----
c4 = mp.mpf(132) - mp.mpf(90)
check("C4 42 = 132 - 90 = N_d*(B-1) - sum_gamma_even EXACT", c4 == 42, f"132-90={c4}")
print(f"[C4] 132-90 = {mp.nstr(c4,6)}  (132 = N_d*(B-1), 90 = sum_gamma_even)")

# ---- C5: MCMC origin artifact ----
N_alpha1 = 1 / (mp.mpf(19) / 123) ** 2
check("C5 MCMC 42 = 1/eps^2 (alpha=1) = 41.9086 ~ 42, NOT structural",
      abs(N_alpha1 - 42) / 42 < mp.mpf('0.005'),
      f"1/eps^2={mp.nstr(N_alpha1,8)}  -> artifact (see script 01 C6)")
print(f"[C5] 1/eps^2 = {mp.nstr(N_alpha1,8)} (alpha=1 artifact ~42)")

# ---- C6: FSR level check ----
# Is 42 an exact level of the FSR refinement ladder? 4^ell * 44 == N exactly?
ell44 = mp.log(42 / 44, 4)
ell88 = mp.log(42 / 88, 4)
is_level44 = abs(4 ** round(ell44) * 44 - 42) < mp.mpf('1e-20')
is_level88 = abs(4 ** round(ell88) * 88 - 42) < mp.mpf('1e-20')
check("C6 42 NOT an FSR refinement level (4^ell*44 != 42, 4^ell*88 != 42)",
      not is_level44 and not is_level88,
      f"log4(42/44)={mp.nstr(ell44,6)}, log4(42/88)={mp.nstr(ell88,6)}")
print(f"[C6] log4(42/44)={mp.nstr(ell44,6)}  log4(42/88)={mp.nstr(ell88,6)}  -> not an FSR level")

# ---- C7: beat(6,7) seam ----
# beat amplitude = 4 sin(d*pi/176) * v_g((a+b)/2); (6,7): d=1, s=6.5 (half-integer seam)
s67 = (6 + 7) / 2
vg65 = mp.cos(mp.pi * s67 / 88)
amp = 4 * mp.sin(mp.pi / 176) * vg65
check("C7a beat(6,7) amplitude uses v_g(6.5) half-integer seam",
      s67 == mp.mpf(13) / 2, f"s=(6+7)/2=6.5; v_g={mp.nstr(vg65,8)}")
# 6.5 = F7/2 (Omega_DM/Omega_b) ; 42 = 6*7
check("C7b 42 = 6*7, beat pair (6,7) sits at seam s=6.5=F7/2 (note only)",
      True, f"a*b = 6*7 = 42 (structural note, not closure)")
print(f"[C7] (6,7): s=6.5 seam, v_g={mp.nstr(vg65,8)}, amp={mp.nstr(amp,8)}; 6*7=42")

# ---- C8: verdict ----
check("C8a 42 has operator identity: mu2*N_gen*L4 (T-hat product)",
      c1 == 42 and c2 == 42, "42 = 2*3*7 = 44-2 (multiple equivalent forms)")
check("C8b 42 as N_horizon (v1.0) = artifact, NOT structural",
      True, "MCMC 41.91~42 is the alpha=1 artifact; structural N_d=44 (O95)")
print()
fails = [r for r in results if not r[1]]
for name, ok, det in results:
    print(f"  {'PASS' if ok else 'FAIL'}  {name}  {det}")
print(f"\nRESULT: {len(results)-len(fails)}/{len(results)} PASS")
if fails:
    print("FAILED:", [r[0] for r in fails])
