#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O153 script 07: 92 — the third rung after 88, 90 (user hypothesis)
====================================================================
User: "42 44 46 都有身份 理論上應該 88 90 後還有 92"
i.e. the N_d +/- mu2 family (42,44,46) doubled gives (84,88,92);
84 = B*F8 (O152), 88 = sum_gamma_odd (C_obs). Is 92 = 2*(N_d+mu2) structural?

Checks:
  C1. small family (42,44,46) = N_d-mu2, N_d, N_d+mu2; endpoint sum 42+46=88
  C2. big family (88,90,92); 92 = sum_gamma_even + mu2 = 2*s0 = C_obs + B
  C3. 88+92 = 180 = 2*sum_gamma_even (endpoints symmetric about 90)
  C4. T-hat forms: 92 = L9 + B^2 = 76+16; 92 = L10 - L7 - mu2 = 123-29-2
  C5. 84+88+92 = 264 = N_d*2N_gen (C_ladder rung)
  C6. honesty: 92 NOT a mod-4 subspace sum; NOT an FSR level
  C7. 88+90+92 = 270 = N_gen * sum_gamma_even
  C8. verdict: family-consistent identity
"""
import mpmath as mp
mp.mp.dps = 50

results = []
def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))

N_d = mp.mpf(44)
mu2 = mp.mpf(2)
B = mp.mpf(4)
N_gen = mp.mpf(3)

# 88-site dual chain = 176-Laplacian
g = lambda k: 4 * mp.sin(k * mp.pi / 176) ** 2
s_even = sum(g(k) for k in range(2, 89, 2))    # 90
s_odd = sum(g(k) for k in range(1, 88, 2))     # 88
s_total = sum(g(k) for k in range(1, 89))      # 178
s0 = sum(g(k) for k in range(4, 89, 4))        # 46
s2 = sum(g(k) for k in range(2, 89, 4))        # 44
s1 = sum(g(k) for k in range(1, 89, 4))        # 44 - sec(pi/88)
s3 = sum(g(k) for k in range(3, 89, 4))        # 44 + sec(pi/88)
print(f"[spectra] even={mp.nstr(s_even,6)} odd={mp.nstr(s_odd,6)} total={mp.nstr(s_total,6)} "
      f"s0={mp.nstr(s0,6)} s1={mp.nstr(s1,10)} s2={mp.nstr(s2,6)} s3={mp.nstr(s3,10)}")

# ---- C1: small family ----
a42, a44, a46 = N_d - mu2, N_d, N_d + mu2
check("C1a (42,44,46) = N_d-mu2, N_d, N_d+mu2", a42 == 42 and a44 == 44 and a46 == 46)
check("C1b 42+46 = 88 = sum_gamma_odd (endpoint sum)",
      abs(a42 + a46 - s_odd) < mp.mpf('1e-30'), f"42+46={a42+a46}")
check("C1c 42+44+46 = 132 = N_d*(B-1) = B*K_Tree",
      a42 + a44 + a46 == 132, f"sum={a42+a44+a46}")
print(f"[C1] small family (42,44,46): endpoint sum = 88, total = 132")

# ---- C2: big family ----
c92a = s_even + mu2
c92b = 2 * s0
c92c = s_odd + B
check("C2a 92 = sum_gamma_even + mu2 = 90+2", abs(c92a - 92) < mp.mpf('1e-30'))
check("C2b 92 = 2*s0 = 2*(N_d+mu2) = 2*46", abs(c92b - 92) < mp.mpf('1e-30'),
      f"2*46={c92b}")
check("C2c 92 = C_obs + B = 88+4", c92c == 92, f"88+4={c92c}")
print(f"[C2] 92 = sum_gamma_even+mu2 = 2*s0 = C_obs+B (all EXACT)")

# ---- C3: symmetry about 90 ----
check("C3 88+92 = 180 = 2*sum_gamma_even = B*(N_d+1)",
      s_odd + c92a == 180, f"88+92={s_odd+c92a}; 2*90=180")
check("C3b (88+92)/2 = 90 = sum_gamma_even (center)",
      (s_odd + c92a) / 2 == 90)
print(f"[C3] 88 and 92 symmetric about 90: 88+92 = 180 = 2*sum_gamma_even")

# ---- C4: T-hat forms ----
L9, L10, L7 = mp.mpf(76), mp.mpf(123), mp.mpf(29)
c4a = L9 + B ** 2                                # 76 + 16
c4b = L10 - L7 - mu2                             # 123 - 29 - 2
check("C4a 92 = L9 + B^2 = 76+16 (T-hat trace + SO(10) spinor)",
      c4a == 92, f"76+16={c4a}")
check("C4b 92 = L10 - L7 - mu2 = 123-29-2",
      c4b == 92, f"123-29-2={c4b}")
print(f"[C4] T-hat: L9+B^2 = 76+16 = {mp.nstr(c4a,4)}; L10-L7-mu2 = 123-29-2 = {mp.nstr(c4b,4)}")

# ---- C5: doubled family sum ----
c5 = 2 * a42 + 2 * a44 + 2 * a46                 # 84+88+92
check("C5 84+88+92 = 264 = N_d*2N_gen (C_ladder rung)",
      c5 == 264, f"84+88+92={c5}; 44*6=264")
check("C5b 84 = 2*42 = B*F8 (O152 identity)",
      2 * a42 == B * 21 == 84)
print(f"[C5] doubled family 84+88+92 = {mp.nstr(c5,5)} = 264 = N_d*2N_gen")

# ---- C6: honesty ----
mod_sums = {"s0": s0, "s1": s1, "s2": s2, "s3": s3, "even": s_even, "odd": s_odd}
none_92 = all(abs(v - 92) > mp.mpf('1e-20') for v in mod_sums.values())
check("C6a 92 NOT a mod-4 subspace sum (honest)",
      none_92, f"{ {k: mp.nstr(v,6) for k,v in mod_sums.items()} }")
ell = mp.log(92 / 44, 4)
is_level = abs(4 ** round(ell) * 44 - 92) < mp.mpf('1e-20')
check("C6b 92 NOT an FSR refinement level", not is_level, f"log4(92/44)={mp.nstr(ell,6)}")
print(f"[C6] honesty: 92 not a mod-4 subspace sum; log4(92/44)={mp.nstr(ell,6)} not FSR level")

# ---- C7: big family total ----
c7 = s_odd + s_even + c92a                        # 88+90+92
check("C7 88+90+92 = 270 = N_gen*sum_gamma_even = 3*90",
      c7 == 270, f"88+90+92={c7}; 3*90=270")
print(f"[C7] big family total 88+90+92 = {mp.nstr(c7,5)} = 270 = N_gen*sum_gamma_even")

# ---- C8: verdict ----
print()
fails = [r for r in results if not r[1]]
for name, ok, det in results:
    print(f"  {'PASS' if ok else 'FAIL'}  {name}  {det}")
print(f"\nRESULT: {len(results)-len(fails)}/{len(results)} PASS")
if fails:
    print("FAILED:", [r[0] for r in fails])
print()
print("VERDICT: 92 = sum_gamma_even + mu2 = 2*s0 = 2*(N_d+mu2) = C_obs + B")
print("Family: (88,90,92) = (sum_odd, sum_even, sum_even+mu2), endpoint sum 180,")
print("total 270 = N_gen*sum_even; doubled small family 84+88+92 = 264 = C_ladder.")
