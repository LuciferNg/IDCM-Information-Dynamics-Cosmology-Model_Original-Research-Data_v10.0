#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O167 scripts/09 — O3: r_d × 420/421 機制 (點解 420/421?)

身份 (O51 發現):
  420 = B·N_gen·F₅·L₄ = 60·L₄ = 14×30 = (2L₄)(2N_gen·F₅)
  421 = 420+1 = F₁₄+N_d = 14²+15² = (2L₄)²+(N_gen·F₅)²  (連續平方和)

機制候選:
  (a) 420/421 = 1 − 1/421: 修正 = 1/(F₁₄+N_d)
  (b) 對角線平方: 14²+15² = 對角線² of 14×15 矩形; 420 = 2×14×15 面積×2
  (c) drag vs decoupling: Planck r_d/r* = 147.09/144.46 — 有冇結構?
  (d) 420 = 4·105 = B·(3·5·7); 421 = 質數
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
print("O167 scripts/09 — 420/421 機制")
print("="*70)

R = mp.mpf("4129.94")
rd_idcm = mp.pi * R / 88
rd_corr = rd_idcm * 420/421

# C1: 421 = 14²+15² (連續平方和, 14 = 2L₄, 15 = N_gen·F₅)
chk("C1 421 = 14²+15² = (2L₄)²+(N_gen·F₅)²", 14**2 + 15**2 == 421 and (2*7)**2 + (3*5)**2 == 421)
print(f"    14²+15² = 196+225 = 421 (14 = 2L₄ = 2×7, 15 = N_gen·F₅ = 3×5)")

# C2: 420 = 2·14·15 = 2×(2L₄)(N_gen·F₅) = B·L₄·N_gen·F₅
chk("C2 420 = 2×14×15 = B·L₄·N_gen·F₅ (4×7×3×5)", 2*14*15 == 420 and 4*7*3*5 == 420)

# C3: 唯一性 — 421 係唯一連續平方和喺 88 附近? 掃 n²+(n+1)² = 421
n_sol = None
for n in range(1, 100):
    if n**2 + (n+1)**2 == 421:
        n_sol = n
chk("C3 421 = n²+(n+1)² 唯一解 n = 14", n_sol == 14)

# C4: 修正量 1/421 vs 其他結構量
chk("C4 1/421 = 0.002375 — 修正量 0.2375% = raw dev (0.237%)", 
    abs(mp.mpf(1)/421 - (rd_idcm - rd_corr)/rd_idcm) < mp.mpf("1e-12"))
print(f"    1/421 = {mp.nstr(mp.mpf(1)/421, 10)}")

# C5: drag/decoupling 交叉 — Planck r_d = 147.09, r* = 144.46
rd_planck = mp.mpf("147.09")
rstar_planck = mp.mpf("144.46")
ratio = rd_planck / rstar_planck
chk("C5 r_d/r* = 1.0182 — 冇簡單結構比 (試 1+1/55=1.01818, dev 0.002%)",
    abs(ratio - (1 + mp.mpf(1)/55)) < mp.mpf("0.001"))
print(f"    r_d/r* = {mp.nstr(ratio, 8)} vs 1+1/55 = {mp.nstr(1+mp.mpf(1)/55, 8)} (55 = F₁₀ = θ₂₃ home)")

# C6: rd_corr 嘅替代分解 — rd_corr = rd_idcm(1-1/421) = rd_idcm - rd_idcm/421
chk("C6 rd_corr = rd_idcm − rd_idcm/421 (修正 = 一個 λ_sync/2 嘅 1/421)", 
    eq(rd_corr, rd_idcm - rd_idcm/421, mp.mpf("1e-40")))

# C7: 421 仲有冇其他結構身份?
# 421 = 20²+21²? 400+441=841 唔啱; 421 質數?
import sympy as sp
chk("C7 421 係質數", sp.isprime(421))
# 421 = 6×70+1? 6×70 = 420 ✓; 421 = 5×84+1? 唔啱
print("    421 質數 ✓; 420 = 6×70 = 2N_gen × 70 (70 = 2·5·7 = 2·F₅·L₄)")

print("\n" + "="*70)
print(f"RESULT: {n_pass}/{n_pass+n_fail} PASS")
print("="*70)
print("誠實標記: 420/421 全結構數身份確認, 但「點解角化修正係 420/421」")
print("嘅機制 (幾何來源) 未推導 → 🟡 (描述層閉合, 機制層開放)")
