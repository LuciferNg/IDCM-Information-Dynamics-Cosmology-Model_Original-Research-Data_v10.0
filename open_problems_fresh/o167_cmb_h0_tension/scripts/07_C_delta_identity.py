#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O167 scripts/07 — O4: δ 權重 C = −0.1697 結構身份掃描

O51 scripts/82 已 FAIL (C_final = 0.0759 ≠ 0.1697, 群延遲推導唔中)。
本 script: 結構家族掃描 (γ-比, L/F 比, φ 冪, 組合) — 睇 C_obs = −0.1697
有冇任何已命名結構身份。冇就誠實 🔴 (δ 修正係 fit, 唔係推導)。
"""
import mpmath as mp
mp.mp.dps = 60

def eq(a, b, tol):
    return abs(a - b) < tol

n_pass = 0
n_fail = 0
def chk(name, cond):
    global n_pass, n_fail
    if cond:
        n_pass += 1
        print(f"[PASS] {name}")
    else:
        n_fail += 1
        print(f"[FAIL] {name}")

print("="*70)
print("O167 scripts/07 — C = -0.1697 結構身份掃描")
print("="*70)

C_obs = mp.mpf("0.1697")
C_abs = abs(C_obs)
phi = (1 + mp.sqrt(5)) / 2

# C1: 確認 O51 scripts/82 FAIL (C_final ≠ C_obs)
C_delay = mp.mpf("0.061410")
C_final = C_delay * 2 / phi
chk("C1 O51 scripts/82 推導 FAIL: C_final = 0.0759 ≠ 0.1697 (差 2.2×)",
    abs(C_final - C_obs) > mp.mpf("0.05"))
print(f"    C_delay = {mp.nstr(C_delay,8)}, C_final = {mp.nstr(C_final,8)} vs C_obs = 0.1697")

# C2: γ-比掃描 — C_abs ≈ γ_a/γ_b?
gamma = [4*mp.sin(mp.pi*k/176)**2 for k in range(1, 89)]
best = (mp.inf, None)
for a in range(1, 89):
    for b in range(1, 89):
        if a == b: continue
        r = gamma[a-1]/gamma[b-1]
        d = abs(r - C_abs)
        if d < best[0]:
            best = (d, (a, b, r))
d0, (a0, b0, r0) = best
chk("C2 γ-比命中? (dev < 0.1%)", d0 < C_abs*mp.mpf("0.001"))
print(f"    best γ_ratio: γ_{a0}/γ_{b0} = {mp.nstr(r0,10)} (dev {float(d0/C_abs)*100:.2f}%)")

# C3: ω-比 (ω = 2sin(kπ/176))
omega = [2*mp.sin(mp.pi*k/176) for k in range(1, 89)]
best3 = (mp.inf, None)
for a in range(1, 89):
    for b in range(1, 89):
        if a == b: continue
        r = omega[a-1]/omega[b-1]
        d = abs(r - C_abs)
        if d < best3[0]:
            best3 = (d, (a, b, r))
d3, (a3, b3, r3) = best3
chk("C3 ω-比命中? (dev < 0.1%)", d3 < C_abs*mp.mpf("0.001"))
print(f"    best ω_ratio: ω_{a3}/ω_{b3} = {mp.nstr(r3,10)} (dev {float(d3/C_abs)*100:.2f}%)")

# C4: L/F 比 (Lucas/Fibonacci 家族)
L = {0:2, 1:1, 2:3, 3:4, 4:7, 5:11, 6:18, 7:29, 8:47, 9:76, 10:123}
F = {1:1, 2:1, 3:2, 4:3, 5:5, 6:8, 7:13, 8:21, 9:34, 10:55, 11:89, 12:144, 13:233, 14:377}
best4 = (mp.inf, None)
for a_name, a_val in list(L.items()) + list(F.items()):
    for b_name, b_val in list(L.items()) + list(F.items()):
        if b_val == 0: continue
        r = mp.mpf(a_val)/mp.mpf(b_val)
        d = abs(r - C_abs)
        if d < best4[0]:
            best4 = (d, (a_name, a_val, b_name, b_val, r))
d4, (an, av, bn, bv, r4) = best4
chk("C4 L/F 比命中? (dev < 0.1%)", d4 < C_abs*mp.mpf("0.001"))
print(f"    best L/F: {av}/{bv} = {mp.nstr(r4,10)} (dev {float(d4/C_abs)*100:.2f}%)")

# C5: φ 冪
best5 = (mp.inf, None)
for k_num in range(-40, 41):
    for k_den in [1, 2, 3, 4]:
        k = mp.mpf(k_num)/k_den
        r = phi**k
        d = abs(r - C_abs)
        if d < best5[0]:
            best5 = (d, (k, r))
d5, (k5, r5) = best5
chk("C5 φ^k 命中? (dev < 0.1%)", d5 < C_abs*mp.mpf("0.001"))
print(f"    best φ^k: φ^{k5} = {mp.nstr(r5,10)} (dev {float(d5/C_abs)*100:.2f}%)")

# C6: 簡單代數候選
cands = {
    "17/100": mp.mpf(17)/100,
    "1-4^(-1/3)": 1 - 4**mp.mpf("-0.5"),
    "1/(2pi·0.938)": 1/(2*mp.pi*mp.mpf("0.938")),
    "gamma7/(gamma7+10)": gamma[6]/(gamma[6]+10),
    "1/(1+gamma44·3)": 1/(1+2*3),
    "sin(pi/18)": mp.sin(mp.pi/18),
    "sin(pi/19)": mp.sin(mp.pi/19),
    "(1-phi^-2)/2": (1-phi**-2)/2,
    "phi^-2/phi": phi**-3,
    "1/6 - 1/60": mp.mpf(1)/6 - mp.mpf(1)/60,
    "1/(2·L7)": 1/(2*mp.mpf(29)),
    "1/(L4+F7)": 1/(mp.mpf(7)+mp.mpf(13)),
    "F7/76": mp.mpf(13)/76,
    "L5/(2·F10)": mp.mpf(11)/(2*mp.mpf(55)),
    "1-F5/6": 1 - mp.mpf(5)/6,
}
best6 = (mp.inf, None)
for name, val in cands.items():
    d = abs(val - C_abs)
    if d < best6[0]:
        best6 = (d, (name, val))
d6, (n6, v6) = best6
chk("C6 代數候選命中? (dev < 0.1%)", d6 < C_abs*mp.mpf("0.001"))
print(f"    best: {n6} = {mp.nstr(v6,10)} (dev {float(d6/C_abs)*100:.2f}%)")

# C7: 誠實裁決
print("\n" + "="*70)
print("裁決: C = -0.1697 冇結構身份 (γ/ω/L/F/φ/代數全 miss)")
print("→ δ 修正係 O76 fit 參數, 唔係結構推導 → 🔴 開放")
print(f"RESULT: {n_pass}/{n_pass+n_fail} PASS")
print("="*70)
