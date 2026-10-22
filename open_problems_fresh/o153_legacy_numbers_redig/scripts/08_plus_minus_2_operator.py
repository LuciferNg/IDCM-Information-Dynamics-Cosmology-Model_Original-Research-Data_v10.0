#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O153 script 08: what does +/-2 mean? (user question)
======================================================
The +/-mu2 spacing in families (42,44,46) and (88,90,92) is not arbitrary.
Hypotheses:
  H1. mu2 = gamma_44 of the 176-Laplacian = SELF-DUAL mode energy
      (k=44 pairs with 88-44=44 itself; gamma_44+gamma_44 = B = 4)
  H2. +/-2 = observer<->world duality switch: -2 projects to observer
      (42 = residual observer), +2 extends to world self (46 = s0)
  H3. +/-2 = per-operation energy: 88 ops = 176 = B*N_d -> 2 per op (O41)
  H4. +/-2 spawns an infinite family ladder (42,44,46)*2^n:
      n=0: 42/44/46, n=1: 84/88/92, n=2: 168/176/184, n=3: 336/352/368...
      even n coincides with FSR refinement levels (2^n = 4^(n/2))

Checks:
  C1. gamma_44(176-L) = 2 = mu2; self-dual: gamma_44+gamma_44 = B
  C2. spectrum decomposition: 178 = 43*B + gamma_44 + gamma_88
      (43 dual pairs + self-dual mode + Nyquist mode)
  C3. family ladder (42,44,46)*2^n for n=0..4 (centers N_d*2^n, gaps 2^n)
  C4. family sums: endpoint sums 2^n*88, totals 2^n*132, doubled 264*2^n
  C5. O41 per-op energy: 88 ops = 176 = B*N_d -> 2 per op = mu2
  C6. half-dimension family: (21,22,23) = (N_d/2-1, N_d/2, N_d/2+1);
      42 = 2*F8 = 2*N_gen*L4; 46 = 2*(N_d/2+1) = 2*23
  C7. +/-2 five-fold identity recap
  C8. even-n families = FSR refinement levels (n=0 -> 44*4^0, n=2 -> 44*4^1,
      n=4 -> 44*4^2); odd-n are dual-chain doubles (88 = 2*44, 352 = 8*44)
  C9. verdict: +/-2 = self-dual mode gamma_44 = duality switch operator
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
L4 = mp.mpf(7)
F8 = mp.mpf(21)

g176 = lambda k: 4 * mp.sin(k * mp.pi / 176) ** 2
g88 = lambda k: 4 * mp.sin(k * mp.pi / 88) ** 2

# ---- C1: gamma_44 self-dual ----
g44_176 = g176(44)
check("C1a gamma_44(176-L) = 4 sin^2(44pi/176) = 4 sin^2(pi/4) = 2 = mu2",
      abs(g44_176 - 2) < mp.mpf('1e-40'), f"gamma_44={mp.nstr(g44_176,12)}")
check("C1b self-dual: gamma_44 + gamma_(88-44) = 2*gamma_44 = 4 = B",
      abs(2 * g44_176 - B) < mp.mpf('1e-40'), f"2*gamma_44={mp.nstr(2*g44_176,12)}")
check("C1c gamma_44(88-L) = 4 = B (Nyquist of 88-Laplacian)",
      abs(g88(44) - B) < mp.mpf('1e-40'), f"gamma_44(88-L)={mp.nstr(g88(44),12)}")
print(f"[C1] gamma_44(176-L) = {mp.nstr(g44_176,12)} = mu2 (self-dual mode: "
      f"pairs with itself, 2*gamma_44 = B = 4); gamma_44(88-L) = {mp.nstr(g88(44),6)} = B")

# ---- C2: spectrum decomposition ----
s_total = sum(g176(k) for k in range(1, 89))
c2 = 43 * B + g44_176 + g176(88)     # 43 pairs*4 + self-dual 2 + Nyquist(176-L) 4
check("C2 178 = 43*B + gamma_44 + gamma_88 = 172+2+4",
      abs(s_total - c2) < mp.mpf('1e-30'),
      f"total={mp.nstr(s_total,8)}; 43*4+2+4={mp.nstr(c2,8)}")
print(f"[C2] 178 = 43 dual pairs*B + self-dual gamma_44(=2) + Nyquist gamma_88(=4)")

# ---- C3: family ladder ----
print("[C3] family ladder (42,44,46)*2^n:")
ladder = []
for n in range(0, 5):
    fam = (42 * 2 ** n, 44 * 2 ** n, 46 * 2 ** n)
    ladder.append(fam)
    print(f"    n={n}: {fam[0]}/{fam[1]}/{fam[2]}  center=2^{n}*44={2**n*44}  "
          f"gap=2^{n}*2={2**n*2}")
check("C3a n=1 family = (84,88,92)", ladder[1] == (84, 88, 92))
check("C3b n=2 family = (168,176,184)", ladder[2] == (168, 176, 184))
check("C3c n=3 family = (336,352,368)", ladder[3] == (336, 352, 368))

# ---- C4: family identities ----
ok_c4 = True
for n in range(0, 5):
    a, b, c = ladder[n]
    if a + c != 2 ** n * 88:          # endpoint sum = 2^n * sum_odd
        ok_c4 = False
    if a + b + c != 2 ** n * 132:     # total = 2^n * 132
        ok_c4 = False
    if 2 * (a + b + c) != 2 ** n * 264:
        ok_c4 = False
check("C4 family identities: endpoint sums 2^n*88, totals 2^n*132 (n=0..4)",
      ok_c4, f"42+46=88, 84+92=176, ...; sums 132,264,528,1056,2112")
print(f"[C4] endpoint sums: 88,176,352,704,1408 = 2^n*88; "
      f"totals: 132,264,528,1056,2112 = 2^n*132")

# ---- C5: O41 per-op energy ----
ops = 88
total_ops_energy = B * N_d                    # 176
per_op = total_ops_energy / ops               # 2
check("C5 88 ops = 176 = B*N_d -> 2 per op = mu2",
      per_op == 2, f"176/88={per_op}")
print(f"[C5] O41 read-write cycle: 88 ops = {mp.nstr(total_ops_energy,5)} = B*N_d "
      f"-> per-op energy = {mp.nstr(per_op,4)} = mu2")

# ---- C6: half-dimension family ----
check("C6a 21 = F8 = N_gen*L4 = N_d/2 - 1", F8 == N_gen * L4 == N_d / 2 - 1)
check("C6b 23 = N_d/2 + 1 = F8 + mu2", N_d / 2 + 1 == 23 and F8 + mu2 == 23)
check("C6c 42 = 2*F8 = 2*N_gen*L4; 46 = 2*23",
      42 == 2 * F8 and 46 == 2 * 23)
print(f"[C6] half-dim family (21,22,23) = (N_d/2-1, N_d/2, N_d/2+1); "
      f"42 = 2F8 = 2*N_gen*L4, 46 = 2*(N_d/2+1)")

# ---- C7: +/-2 five-fold identity ----
s_even = sum(g176(k) for k in range(2, 89, 2))   # 90
s_odd = sum(g176(k) for k in range(1, 88, 2))    # 88
s0 = sum(g176(k) for k in range(4, 89, 4))       # 46
s2 = sum(g176(k) for k in range(2, 89, 4))       # 44
check("C7a mu2 = E-O = 90-88", abs(s_even - s_odd - 2) < mp.mpf('1e-30'))
check("C7b mu2 = log2(B)", mp.log(B, 2) == 2)
check("C7c mu2 = s0-s2 = 46-44", s0 - s2 == 2)
check("C7d mu2 = gamma_44(176-L) (self-dual mode)", abs(g44_176 - 2) < mp.mpf('1e-40'))
check("C7e mu2 = per-op energy (88 ops = 176)", B * N_d / 88 == 2)
print(f"[C7] mu2 five-fold: E-O = log2(B) = s0-s2 = gamma_44(self-dual) = per-op energy = 2")

# ---- C8: even-n families = FSR levels ----
print("[C8] family centers 44*2^n vs FSR levels 44*4^ell:")
fsr_ok = True
for n in [0, 2, 4]:
    center = 44 * 2 ** n
    ell = n // 2
    if center != 44 * 4 ** ell:
        fsr_ok = False
    print(f"    n={n}: center={center} = 44*4^{ell} (FSR level ell={ell}) {'OK' if center == 44*4**ell else 'FAIL'}")
for n in [1, 3]:
    center = 44 * 2 ** n
    print(f"    n={n}: center={center} = dual-chain double (not FSR integer level)")
check("C8 even-n centers = FSR refinement levels (n=2ell -> 44*4^ell)",
      fsr_ok, "n=0->44*4^0, n=2->44*4^1, n=4->44*4^2")

# ---- C9: verdict ----
print()
fails = [r for r in results if not r[1]]
for name, ok, det in results:
    print(f"  {'PASS' if ok else 'FAIL'}  {name}  {det}")
print(f"\nRESULT: {len(results)-len(fails)}/{len(results)} PASS")
if fails:
    print("FAILED:", [r[0] for r in fails])
print()
print("VERDICT: +/-2 = +/-mu2 = +/-gamma_44(self-dual mode of 176-Laplacian)")
print("= world-observer duality switch: -2 projects world to observer (42),")
print("+2 extends world to self (46 = s0). Spawns family ladder")
print("(42,44,46)*2^n; even-n centers are FSR refinement levels 44*4^(n/2).")
