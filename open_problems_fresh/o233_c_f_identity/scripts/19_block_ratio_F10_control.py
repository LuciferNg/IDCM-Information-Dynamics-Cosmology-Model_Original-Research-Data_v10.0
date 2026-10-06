#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O233 scripts/19 — 塊參數盲測補充：G3/G1 ≈ F₁₀ 對照（第二十輪附屬）
====================================================================
scripts/18 Q3 意外發現：G3/G1 = 54.8358 ≈ F₁₀ = 55（dev 0.30%）。
但 docs/02 教訓：池密度可以殺「漂亮命中」——單點 dev 0.30% 喺結構池入面
未必稀有。本 script 補做兩個對照（pre-registered）：

  C1: 對照池（結構冪/斐波那契/F₁₀ 家族同級）—— 隨機 塊間比 對「最接近
      結構值」嘅 min-dev 分布（direction: R1·R2 = G3/G1, log-uniform）
  C2: G3/G1 撞凍結池 1e-3 窗（scripts/18 已 28 hits）—— 但命中數要對照
      MC：5 目標中「max hits」嘅分布（look-elsewhere over 5 targets）
  C3: 精確值：G3/G1 = 54.8358 —— 有冇其他 docs 已身份常數喺 54–56 之間
      更近？（F₁₀=55, L₈=47, 2·L₇=58, B³−10=54, 123/… 唔好亂加——
      只列 corpus 已有身份常數, 禁後驗加池）
判定: C1 p < 0.05 ∧ C2 look-elsewhere < 0.05 先可以考慮升格 F₁₀ 線索。
"""
import json, math, random
import mpmath as mp
mp.mp.dps = 40

G1, G2, G3 = 3.685, 61.35, 202.07
R12 = G3 / G1

# corpus 已有身份常數（docs/02 池同源, 零新常數）
L = [2, 1]
for k in range(2, 15): L.append(L[-1] + L[-2])
F = [0, 1]
for k in range(2, 21): F.append(F[k-1] + F[k-2])
STRUCT = sorted(set(L) | set(F[2:]) | {4, 16, 64, 256, 3, 44, 33, 134, 36, 98, 2,
                        18, 5, 88, 176, 946, 123, 137, 90, 46, 45, 60, 42, 37,
                        41, 47, 48, 50, 51, 26, 22, 17, 8, 40})

print("=== C1: G3/G1 = %.4f vs 最近結構常數 ===" % R12)
best = min(STRUCT, key=lambda s: abs(R12 - s)/s)
dev_best = abs(R12 - best) / best
print(f"  最近: {best} (dev {dev_best*100:.3f}%); F₁₀=55 dev {abs(R12-55)/55*100:.3f}%")
print(f"  dev_best = {dev_best:.4f}")

# C1 null: 隨機 [1, 250] log-uniform 值, 對「最近結構常數」嘅 min-dev 分布
random.seed(20261008)
N = 200000
le = 0
for _ in range(N):
    r = 10**random.uniform(0, 2.4)   # [1, 250]
    b = min(abs(r - s)/s for s in STRUCT)
    if b <= dev_best: le += 1
print(f"  C1: P(隨機值對結構常數 min-dev ≤ {dev_best*100:.3f}%) = {le/N:.6f}")

# C2: 凍結池重建成 bottles（用 5 目標 look-elsewhere）
Lc = [2, 1]
for k in range(2, 15): Lc.append(Lc[-1] + Lc[-2])
Fc = [0, 1]
for k in range(2, 21): Fc.append(Fc[k-1] + Fc[k-2])
S = set(Lc) | set(Fc[2:]) | {4, 16, 64, 256, 3, 44, 33, 134, 36, 98, 2, 18, 5,
                             88, 176, 946, 123, 137, 90, 46, 45, 60, 42, 37, 41,
                             47, 48, 50, 51, 26, 22, 17, 8, 40}
S = sorted(S)
POOL = set()
def addp(v):
    if mp.mpf('0.1') <= v <= mp.mpf('1e4'):
        POOL.add(mp.nstr(v, 12))
for s in S: addp(mp.mpf(s))
for c in S:
    for s in S: addp(mp.mpf(s)/mp.mpf(c))
for c in S:
    for s1 in S:
        for s2 in S:
            addp((mp.mpf(s1)+mp.mpf(s2))/mp.mpf(c))
            if s1 > s2: addp((mp.mpf(s1)-mp.mpf(s2))/mp.mpf(c))
for i in range(1, 45):
    for j in range(i+1, 45):
        addp(mp.sin(mp.pi*i/88)**2 / mp.sin(mp.pi*j/88)**2)
        addp(mp.sin(mp.pi*j/88)**2 / mp.sin(mp.pi*i/88)**2)
for x3 in (1, 5, 9):
    for x3p in (0, 1, 3, 4, 6, 7): addp(mp.mpf(1 + x3*x3p))
POOL = sorted((mp.mpf(k) for k in POOL))

import bisect
def hits(t, dT):
    t = mp.mpf(t)
    lo, hi = t/mp.mpf(1+dT), t*mp.mpf(1+dT)
    return bisect.bisect_right(POOL, hi) - bisect.bisect_left(POOL, lo)

obs_h3 = hits(R12, 1e-3)
obs_h4 = hits(R12, 1e-4)
T5 = [G1, G2, G3, G2/G1, G3/G2]
obs_max3 = max(hits(t, 1e-3) for t in T5)
obs_max4 = max(hits(t, 1e-4) for t in T5)
print(f"\n=== C2: 凍結池命中 + look-elsewhere over 5 targets ===")
print(f"  G3/G1: hits(1e-3)={obs_h3} hits(1e-4)={obs_h4}")
print(f"  5 target max hits: 1e-3={obs_max3} 1e-4={obs_max4}")

random.seed(20261009)
N2 = 20000
ge3 = ge4 = 0
for _ in range(N2):
    ts = [10**random.uniform(-1, 3.0) for _ in range(5)]
    m3 = max(hits(t, 1e-3) for t in ts)
    m4 = max(hits(t, 1e-4) for t in ts)
    if m3 >= obs_max3: ge3 += 1
    if m4 >= obs_max4: ge4 += 1
print(f"  C2: P(max hits ≥ {obs_max3} @1e-3) = {ge3/N2:.6f}"
      f"  P(max hits ≥ {obs_max4} @1e-4) = {ge4/N2:.6f}")

out = {"R12": R12, "best_struct": best, "dev_best": dev_best,
       "C1_p": le/N, "obs_h3": obs_h3, "obs_h4": obs_h4,
       "C2_p_3": ge3/N2, "C2_p_4": ge4/N2,
       "F10_dev": abs(R12-55)/55,
       "note": "scripts/18 Q3 意外發現 G3/G1≈F₁₀ 之對照盲測; C1 結構常數min-dev分布 C2 look-elsewhere"}
with open("data/19_block_ratio_F10_control.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print("\n✅ data/19_block_ratio_F10_control.json 寫入")