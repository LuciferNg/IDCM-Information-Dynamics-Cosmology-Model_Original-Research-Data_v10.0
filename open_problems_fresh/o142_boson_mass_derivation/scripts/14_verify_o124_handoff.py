#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O142 - verify O124 docs/09 §7.3 handoff recommendation (2026-10-13).

O124 claims:
  (i)   a_EM^-1(0)   = 137.035999074   (CODATA measurement)
  (ii)  a_EM^-1(M_Z) = 127.930 +/- 0.008  (PDG)
  (iii) Delta(a^-1) measured = 137.035999074 - 127.930 = 9.1060 +/- 0.008
  (iv)  structural Delta = 9 = (B-1)^2 = N_gen^2
  (v)   deviation = +1.18% = 13.2 sigma  => identity 'Delta=9' REFUTED as measured prediction
  (vi)  using integer endpoint 137: 9.070 (-0.78%, 8.75 sigma) also misses
  (vii) 137.036 vs integer 137 => 0.026% magnitude offset => O142 endpoint-layer residual

Verify each arithmetic claim independently. Also test WOULD-BE structural
expressions for the 0.036 fractional part (density-style check, NOT fitting).
"""
import mpmath as mp
mp.mp.dps = 40
ok = fail = 0
def chk(name, cond, detail=""):
    global ok, fail
    if cond: ok += 1; print(f"  [PASS] {name} {detail}")
    else:    fail += 1; print(f"  [FAIL] {name} {detail}")

print("="*72)
print("A. O124 docs/09 §7.1 arithmetic")
print("="*72)
a0 = mp.mpf('137.035999074')   # CODATA alpha_EM^-1(0)
aZ = mp.mpf('127.930')           # PDG alpha_EM^-1(M_Z)
sZ = mp.mpf('0.008')
d_meas = a0 - aZ
print(f"  Delta measured = {mp.nstr(d_meas,8)} +/- {sZ}")
chk("(iii) Delta = 9.1060 (O124)", mp.almosteq(d_meas, mp.mpf('9.1060'), rel_eps=mp.mpf('1e-4')))

dev_pct = (d_meas-9)/9*100
z13 = (d_meas-9)/sZ
print(f"  dev vs 9 = {mp.nstr(dev_pct,5)}%  z = {mp.nstr(z13,4)} sigma")
chk("(v) +1.18%", abs(dev_pct - 1.18) < 0.01)
chk("(v) 13.2 sigma", abs(z13 - 13.2) < 0.3)

# integer-endpoint variant: 137 - 127.930
d_int = mp.mpf(137) - aZ
print(f"  integer endpoint: 137 - 127.930 = {mp.nstr(d_int,7)}")
chk("(vi) 9.070", mp.almosteq(d_int, mp.mpf('9.070'), rel_eps=mp.mpf('1e-3')))
dev_int = (d_int-9)/9*100
z_int = (d_int-9)/sZ
print(f"  dev = {mp.nstr(dev_int,5)}%  z = {mp.nstr(z_int,4)} sigma")
chk("(vi) -0.78%", abs(dev_int - (-0.78)) < 0.02)
chk("(vi) 8.75 sigma", abs(z_int - 8.75) < 0.3)

# 0.026% offset
frac = (a0-137)/137*100
print(f"  137.036 vs 137: offset = {mp.nstr(frac,6)}%")
chk("(vii) 0.026%", abs(frac - 0.026) < 0.002)

print("="*72)
print("B. WARNING: v7 candidate a^-1(0)=134+3+15/(phi*256) was O204-null-refuted.")
print("   The 0.036 fractional part must NOT be re-fitted. Density scan:")
print("="*72)
phi = (1+mp.sqrt(5))/2
xf = a0 - 137  # 0.035999074
print(f"  fractional part x = {mp.nstr(xf,8)}")
# density: x vs simple structural vocab ratios (abort early - just informational)
import itertools
vocab = [1,2,3,4,5,7,8,11,13,17,18,21,29,33,34,36,44,47,55,88]
hits = []
for a in vocab:
    for b in vocab:
        if b == 0: continue
        v = mp.mpf(a)/b
        if abs(v-xf)/xf < 0.01:
            hits.append((a,b,mp.nstr(v,6),mp.nstr(abs(v-xf)/xf*100,3)))
print(f"  fractional x within 1% of a/b (density probe): {len(hits)} hits")
for h in hits[:12]:
    print("   ", h)
# golden-ratio family?
for k in range(1,9):
    v = phi**(-k)
    d = abs(v-xf)/xf*100
    if d < 5: print(f"  phi^-{k} = {mp.nstr(v,8)}  dev {mp.nstr(d,3)}%")
print("  -> informational only; NO structural claim without blind-test + O204 gate.")

print("="*72)
print("C. O124 recommendation itself (logic check)")
print("="*72)
print("  O124 §7.3 routes TWO residuals to O142:")
print("   (1) exact running Delta = 9.1060(8) structural expression -> O85/O142")
print("   (2) a^-1(0)=137.036 vs integer 137  -> O142 endpoint layer, 0.026%")
print("  NOTE: O124 §4.159 says '137/128 closed by o142 (3N0+F5)': that is the INTEGER")
print("  identity chain. The 0.026% offset is the measured-vs-structure residual.")
print()
print(f"AUDIT: {ok} PASS / {fail} FAIL")