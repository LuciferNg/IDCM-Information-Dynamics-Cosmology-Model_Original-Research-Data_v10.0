#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scripts/19_mu_e_two_step_iteration.py — 驗證 Gemini μ/e 雙步迭代假說 (優化版)
假說: m_μ/m_e = √(γ_k1) × √(γ_k2) (兩步相干乘積)
優化: 單步值集合 dict → 雙步乘積 = r1×r2, 對目標 μ/e 配對 O(88²)
"""
import mpmath as mp
mp.mp.dps = 60

N_d, B, N_gen, L5 = 44, 4, 3, 11
F_proj = 17

def gam88(n): return 4*mp.sin(n*mp.pi/88)**2
def gam176(n): return 4*mp.sin(n*mp.pi/176)**2

MU_E = mp.mpf('105.658')/mp.mpf('0.51099895')

checks, fails = [], []
def ck(name, cond, detail=""):
    checks.append(name)
    mark = "✔" if cond else "✘ FAIL"
    if not cond: fails.append(name)
    print("  [%s] %s %s" % (mark, name, detail))

print("="*72)
print("A. 單步上限確認")
print("="*72)
max88 = mp.sqrt(gam88(44)/gam88(1))
max176 = mp.sqrt(gam176(88)/gam176(1))
print("   88 域單步上限: %.2f | 176 域單步上限: %.2f | m_μ/m_e = %.6f"
      % (max88, max176, MU_E))
ck("88 域單步 28 < 206.8 (超限)", max88 < MU_E)
ck("176 域單步 56 < 206.8 (超限)", max176 < MU_E)
print()

def two_step(gam, N, label):
    """單步值集合 → 雙步配對. 返回最佳 (dev, a,b,c,d, prod)"""
    singles = {}
    for b in range(1, N+1):
        for a in range(1, N+1):
            if a == b: continue
            r = mp.sqrt(gam(a)/gam(b))
            if r < 1: continue
            key = mp.nstr(r, 50)
            singles.setdefault(key, (a, b))
    # 對每個 r1, 搵 r2 = MU_E/r1 最近
    vals = sorted(singles.keys(), key=lambda k: mp.mpf(k))
    best = None
    import bisect
    for k1 in vals:
        r1 = mp.mpf(k1)
        r2_target = MU_E / r1
        if r2_target < 1: continue
        # binary search 最近
        pos = bisect.bisect_left(vals, mp.nstr(r2_target, 50))
        for cand in (pos-1, pos, pos+1):
            if cand < 0 or cand >= len(vals): continue
            r2 = mp.mpf(vals[cand])
            prod = r1*r2
            dev = abs(prod/MU_E - 1)
            a1, b1 = singles[k1]
            a2, b2 = singles[vals[cand]]
            if best is None or dev < best[0]:
                best = (dev, a1, b1, a2, b2, prod)
    print("   %s 雙步配對 (dict 法):" % label)
    if best:
        dev, a1, b1, a2, b2, prod = best
        print("     √(γ_%d/γ_%d)×√(γ_%d/γ_%d) = %.6f  dev = %.4f%%"
              % (a1, b1, a2, b2, prod, 100*dev))
    return best

print("="*72)
print("B. 雙步乘積掃描 (dict 配對, 秒級)")
print("="*72)
best88 = two_step(gam88, 44, "88 域")
best176 = two_step(gam176, 88, "176 域")
print()

print("="*72)
print("C. 指數身份檢查 (命中解)")
print("="*72)
for lbl, best in [("88域", best88), ("176域", best176)]:
    if not best: continue
    dev, a1, b1, a2, b2, prod = best
    print("   %s 解 (a1,b1,a2,b2) = (%d,%d,%d,%d), dev=%.4f%%" % (lbl, a1, b1, a2, b2, 100*dev))
    for nm, k in [("a1",a1),("b1",b1),("a2",a2),("b2",b2)]:
        ids = []
        if k == N_gen: ids.append("N_gen")
        if k == L5: ids.append("L₅")
        if k == N_d//2 - N_gen: ids.append("f_proj")
        if k == 17: ids.append("F_proj")
        if k == 41: ids.append("f_unproj")
        if k == N_d: ids.append("N_d")
        if k == 2*N_gen*B: ids.append("2N_gen·B")
        if k == 2*B**2: ids.append("2B²")
        if k == F_proj + L5: ids.append("F_proj+L₅")
        print("     %s=%d%s" % (nm, k, (" ("+",".join(ids)+")") if ids else " (無身份)"))
print()

print("="*72)
print("D. 對照: 分步質量比鏈")
print("="*72)
TAU_MU = mp.mpf('1776.86')/mp.mpf('105.658')
print("   τ/μ = %.4f (單步可達), μ/e = %.4f (需雙步)" % (TAU_MU, MU_E))
r1 = mp.sqrt(gam176(88)/gam176(1))
r2 = MU_E / r1
print("   176 域分解: 56.0 × %.4f = %.1f" % (r2, r1*r2))
print("   → 第二因子 %.4f 對應 √(γ_a/γ_b), γ_a/γ_b = %.2f" % (r2, r2**2))
print()

print("="*72)
print("E. 誠實評估: 雙步自由度 vs null")
print("="*72)
print("   雙步配對自由度: 88 域 1892² 對, 176 域 7744² 對")
print("   → 需要 null control 先算結構 (scripts/15 教訓)")
print()

print("6. Verdict")
print("="*72)
# null: 隨機目標 200 次, 每次雙步配對 best dev
import random
random.seed(7)
print("   null control (200 隨機目標 ∈ [1, 3000], 176 域雙步配對):")
devs = []
singles = []
for b in range(1, 89):
    for a in range(1, 89):
        if a == b: continue
        r = mp.sqrt(gam176(a)/gam176(b))
        if r < 1: continue
        singles.append((r, a, b))
singles.sort(key=lambda x: x[0])
import bisect
rs = [x[0] for x in singles]
for _ in range(200):
    t = mp.mpf('1') + mp.mpf(random.random())*2999
    bd = None
    for r1, a1, b1 in singles:
        r2t = t / r1
        if r2t < 1: continue
        pos = bisect.bisect_left(rs, r2t)
        for cand in (pos-1, pos):
            if cand < 0 or cand >= len(rs): continue
            prod = r1*rs[cand]
            dv = abs(prod/t - 1)
            if bd is None or dv < bd: bd = dv
    devs.append(bd)
devs.sort()
med = devs[100]
print("   null median best dev = %.4f%%" % (100*med))
if best176:
    p_val = sum(1 for x in devs if x <= best176[0])/200.0
    print("   實測 176 域 dev = %.4f%% → null p = %.3f" % (100*best176[0], p_val))
    ck("F91 176 域雙步解通過 null control (p<0.05)", p_val < 0.05)
else:
    ck("F91 176 域雙步解通過 null control", False)
print()
total = len(checks)
print("="*72)
print("RESULT: %d/%d PASS" % (total-len(fails), total))
if fails: print("FAIL: %s" % fails)
print("="*72)
