#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O169 scripts/09 — 窗口選擇掃描: 數據揀邊個譜窗口?

問題: b = 1/<v_g>_{1..K} 或 <w>_{1..K} — K 由數據揀, 定係有結構理由?
      Z₂ 自對偶窗口 = 1..N_d/2 = 1..22 (n=22 係自對偶模, v_g=1/√2)
      若 K=22 係唯一/最佳 → Z₂ 半鏈窗口由數據選出 (結構支持)
"""
import mpmath as mp
mp.mp.dps = 40
phi = (1+mp.sqrt(5))/2; inv = 1/phi; pi = mp.pi
R = mp.mpf('4129.94'); rd = pi*R/88*mp.mpf(420)/421
TR = [('LRG1', mp.mpf('0.510'), mp.mpf('13.588'), mp.mpf('0.167')),
      ('LRG2', mp.mpf('0.706'), mp.mpf('17.351'), mp.mpf('0.177')),
      ('LRG3', mp.mpf('0.934'), mp.mpf('21.576'), mp.mpf('0.152')),
      ('ELG2', mp.mpf('1.321'), mp.mpf('27.601'), mp.mpf('0.318')),
      ('QSO',  mp.mpf('1.484'), mp.mpf('30.512'), mp.mpf('0.760')),
      ('Lya',  mp.mpf('2.330'), mp.mpf('38.988'), mp.mpf('0.531'))]
v = {n: mp.cos(pi*n/88) for n in range(1,45)}
w = {n: 1/v[n] for n in range(1,45)}

def chi2(a, b):
    t = mp.mpf(0); worst = mp.mpf(0)
    for n, z, dm, em in TR:
        l = mp.log(1+z,4)
        s = ((R*(1-4**(-l))*(a*l+b))/rd - dm)/em
        t += s*s
        if abs(s) > abs(worst): worst = s
    return t, abs(worst)

print("="*80)
print("O169/09 — 窗口選擇掃描 (K 由數據定? 定 Z₂ 自對偶 K=22 有結構理由?)")
print("="*80)
print(f"{'K':>3}  {'1/<v>_K':>11}{'χ²/5':>9}{'|σ|max':>8}   {'<w>_K':>11}{'χ²/5':>9}{'|σ|max':>8}")
best = {}
for K in range(1, 44):
    sv = sum(v[n] for n in range(1,K+1))/K
    sw = sum(w[n] for n in range(1,K+1))/K
    t1, w1 = chi2(mp.mpf(1), 1/sv)
    t2, w2 = chi2(mp.mpf(1), sw)
    best[K] = (t1, w1, t2, w2, 1/sv, sw)
    mark = ''
    if K in (11, 22, 27, 33): mark = '  ←'
    if w1 <= 1.0 or w2 <= 1.0:
        print(f"{K:>3}  {mp.nstr(1/sv,9):>11}{mp.nstr(t1,5):>9}{mp.nstr(w1,3):>8}   "
              f"{mp.nstr(sw,9):>11}{mp.nstr(t2,5):>9}{mp.nstr(w2,3):>8}{mark}")

k1 = min(best, key=lambda K: best[K][1])
k2 = min(best, key=lambda K: best[K][3])
print(f"\n最佳 1/<v_g> 窗口: K = {k1}  (chi2 = {mp.nstr(best[k1][0],5)}, |sigma|max = {mp.nstr(best[k1][1],3)})")
print(f"最佳 <w> 窗口    : K = {k2}  (chi2 = {mp.nstr(best[k2][2],5)}, |sigma|max = {mp.nstr(best[k2][3],3)})")
print(f"Z₂ 自對偶 K = 22: 1/<v> = {mp.nstr(best[22][4],9)}  χ² = {mp.nstr(best[22][0],5)}  |σ|max = {mp.nstr(best[22][1],3)}")
print(f"                  <w>   = {mp.nstr(best[22][5],9)}  χ² = {mp.nstr(best[22][2],5)}  |σ|max = {mp.nstr(best[22][3],3)}")

# 通過 |σ|max<=1.0 嘅窗口清單
p1 = [K for K in best if best[K][1] <= 1.0]
p2 = [K for K in best if best[K][3] <= 1.0]
print(f"\n1/<v_g> 窗口通過 |σ|max ≤ 1.0 嘅 K: {p1}")
print(f"<w> 窗口通過 |σ|max ≤ 1.0 嘅 K: {p2}")
print(f"\n結構窗口對照 (K = 11 = L₅, 22 = N_d/2 自對偶, 27 = F_proj 截斷, 33 = K_tree):")
for K in (11, 22, 27, 33):
    print(f"  K={K:>3}  1/<v> = {mp.nstr(best[K][4],9)} (χ²={mp.nstr(best[K][0],5)})"
          f"   <w> = {mp.nstr(best[K][5],9)} (χ²={mp.nstr(best[K][2],5)})")
print(f"\n對照: √5/2 = {mp.nstr(mp.sqrt(5)/2,9)}   φ = {mp.nstr(phi,9)}   μ²/4 = 1/2")
print(f"自對偶模 n=22: γ₂₂ = {mp.nstr(4*mp.sin(pi/4)**2,8)} = μ², v_g = {mp.nstr(mp.cos(pi/4),8)} = 1/√2")
