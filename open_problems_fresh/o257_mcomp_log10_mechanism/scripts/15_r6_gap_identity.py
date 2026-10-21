#!/usr/bin/env python3
"""
O257 scripts/15 — R6: 主項缺口 identity 攻堅 (2026-10-21)
========================================================
R5 留低死位: M_cal/M_main 缺口 ~3%, 1/gap ≈ 32 = N_d−hop_max (dev 0.12%)

R6 問題:
  1. 缺口基準釐清 — 用邊個做主項?
     (a) log 主項:   M_pl·10^{-1/γ₆}         (operator: 1/γ₆)
     (b) 無log主項: M_pl/(88³/2)             (純算子 EXACT)
     (c) O66 值:    M_pl·10^{-(1/γ₆−1/76)}   (R4 已判 1/76 後驗)
  2. 缺口候選: 1+1/x 家族 x ∈ 結構池 — 邊個最優?
  3. Density 閘: 隨機目標下近命中密度 (look-elsewhere)
  4. MC null: 隨機 gap 目標, 結構池優先生命中率
  5. 32 = N_d−hop_max 嘅機制問題: 係咪又一個 hop 補數後驗?

判準: |dev| < 0.01% 且 MC null p < 5% 且機制唔事後 = 升格
      否則: 維持「缺口冇 operator 身份」= O257 完整 negative
"""
import mpmath as mp
mp.mp.dps = 50

M_pl = mp.mpf("1.220910e19")
M_cal = mp.mpf("3.6909e13")
g6 = 4*mp.sin(6*mp.pi/88)**2
inv_g6 = 1/g6

print("="*72)
print("O257 scripts/15 — R6: 主項缺口 identity 攻堅")
print("="*72)

# ── 1. 三種主項基準 ──
N3h = mp.mpf(88)**3/2
M_nolog = M_pl / N3h          # M_pl/(88³/2)
M_log = M_pl * mp.power(10, -inv_g6)   # M_pl·10^{-1/γ₆}
M_o66 = M_pl * mp.power(10, -(inv_g6 - mp.mpf(1)/76))

print("\n[1] 主項基準對照 (vs M_cal=3.6909e13)")
for name, M in [("無log主項 M_pl/(88³/2)", M_nolog),
                ("log主項 M_pl·10^-1/γ6", M_log),
                ("O66 值 (1/76 修正)", M_o66)]:
    print(f"  {name}: {mp.nstr(M, 10)}  dev {mp.nstr((M-M_cal)/M_cal*100, 8)}%")

# 各基準嘅 gap ratio
print("\n  ratio M_cal/主項:")
for name, M in [("無log", M_nolog), ("log", M_log)]:
    r = M_cal/M
    print(f"    {name}: ratio = {mp.nstr(r, 15)}  ratio−1 = {mp.nstr(r-1, 12)}  1/(ratio−1) = {mp.nstr(1/(r-1), 10)}")

# ── 2. 1+1/x 候選掃描 ──
print("\n[2] gap 候選: gap = 1/x, x 結構池")
pool = [32, 32-1, 33, 34, 31, 44-11, 44-13, 88-55, 88-56, 88-57, 44-10,
        12+19, 12+20, 12+21, 29+3, 29+4, 47, 60-27, 60-28, 60-29, 176/5, 176/6,
        90-58, 90-59, 90-57, 88/2.75, 88/2.72, 44*3/4, 44*2/3, 88*21/58]
results = []
for x in pool:
    for base_name, M in [("M_nolog", M_nolog), ("M_log", M_log)]:
        Mx = M * (1 + mp.mpf(1)/x)
        dev = (Mx - M_cal)/M_cal*100
        results.append((abs(dev), x, base_name, dev))
results.sort()
print("  最優 10 組合 (aim: dev<0.01%):")
for d, x, bn, dev in results[:10]:
    flag = " ★" if d < 0.01 else ""
    print(f"    x={x} [{bn}]: dev {mp.nstr(dev, 6)}%{flag}")

# ── 3. Density 閘: 1+1/x 對隨機目標 ──
print("\n[3] Density: 1+1/x (x∈結構池) 命中 |dev|<0.01% 概率")
import random
random.seed(25715)
pool_unique = sorted(set(pool))
# 隨機目標 M_rnd = M_nolog × (1+u), u∈[0.01, 0.06] (3%±3%)
N = 20000
hits_loose = 0
hits_strict = 0
for _ in range(N):
    u = mp.mpf(random.uniform(0.01, 0.06))
    M_rnd = M_nolog * (1+u)
    best = min(abs((M_nolog*(1+mp.mpf(1)/x) - M_rnd)/M_rnd*100) for x in pool_unique)
    if best < 0.1: hits_loose += 1
    if best < 0.01: hits_strict += 1
print(f"  池 {len(pool_unique)} 個 x: |dev|<0.1% 命中率 {hits_loose/N*100:.2f}%  (|dev|<0.01%: {hits_strict/N*100:.2f}%)")
print(f"  → 若命中率 >> 5%, 缺口身份後驗嫌疑大")

# ── 4. MC null: 隨機目標下「最優 x 落入結構池且 dev<0.01%」──
print("\n[4] MC null: 隨機目標下結構池 x* 優先生命中")
# 結構池 x 對應 ratio (1+1/x) vs 任意 x∈[20,60] (連續帶)
band_ratio_hits = 0
pool_hits = 0
for _ in range(20000):
    u = mp.mpf(random.uniform(0.01, 0.06))
    r_target = 1 + u
    # 結構池最優
    best_pool = min(pool_unique, key=lambda x: abs((1+mp.mpf(1)/x) - r_target))
    best_band = 0
    best_d = mp.inf
    for xx in range(20, 61):
        d = abs((1+mp.mpf(1)/xx) - r_target)
        if d < best_d:
            best_d = d; best_band = xx
    if abs((1+mp.mpf(1)/best_pool) - r_target) < mp.mpf("0.0002"): pool_hits += 1
    if best_d < mp.mpf("0.0002"): band_ratio_hits += 1
print(f"  池 [20..60] 全帶 |Δr|<2e-4 命中率: {band_ratio_hits/20000*100:.1f}%")
print(f"  結構池 |Δr|<2e-4 命中率: {pool_hits/20000*100:.1f}%")
print(f"  → 全帶命中率高 = 1/32 唔特別")

# ── 5. 精確 1/32 候選 ──
print("\n[5] 32 = N_d−hop_max 精確檢查")
r_log = M_cal/M_log
d32 = abs((mp.mpf(1)+mp.mpf(1)/32 - r_log)/(r_log)*100)
print(f"  M_cal/M_log = {mp.nstr(r_log, 16)}")
print(f"  1+1/32 = 9/8? no; 33/32 = {mp.nstr(mp.mpf(33)/32, 16)}")
print(f"  dev(33/32 vs ratio) = {mp.nstr(d32, 8)}%")
d32nl = abs((mp.mpf(1)+mp.mpf(1)/32 - M_cal/M_nolog)/(M_cal/M_nolog)*100)
print(f"  dev(33/32 vs 無log ratio) = {mp.nstr(d32nl, 8)}%")
# 32 嘅 operator 鏈
print("  32 身份鏈:")
for v, name in [(32, "N_d−hop_max = 44−12"), (33, "N_d−hop_max+1 = 33"),
                (11, "L₅"), (12, "hop_max"), (44, "N_d"), (88, "N"), (176, "2N")]:
    print(f"    {v} = {name}")

# 33/32 分解: (N_d−hop_max+1)/(N_d−hop_max)
a = mp.mpf("33"); b = mp.mpf("32")
print(f"\n  33/32 = {mp.nstr(a/b, 30)}")
print(f"  = (N_d−hop_max+1)/(N_d−hop_max)")
print(f"  = (44−12+1)/(44−12) = 33/32")
print(f"  = (2N−2hop_max+1)/(2N−2hop_max)? {(176-24+1)}/{(176-24)} = {mp.nstr((176-24+1)/(176-24), 12)} ✗")
print(f"  = (N−2hop_max+1)/(N−2hop_max)? {(88-24+1)}/{(88-24)} = {mp.nstr((88-24+1)/(88-24), 12)} ✗")
print(f"  = (N_d−hop_max+γ₄₄−...?) 33=3·11=3L₅; 32=2⁵")

print("\n" + "="*40)
print("R6 判定待定: 見上面 dev/命中率")