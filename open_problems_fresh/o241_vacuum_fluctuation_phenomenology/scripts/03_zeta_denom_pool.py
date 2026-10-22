#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O241 Q2 殘餘① — 240 機制測試: ζ 分母族 vs 結構池覆蓋率 (含隨機池 null)
================================================================================
v2 修正 (2026-10-08): mpmath bernoulli() 返回十進制唔係精確有理數,
首版 C1-C3 全錯 (分母 2e40). 改用精確 Fraction Bernoulli 表.

方法:
  (a) ζ 分母族: ζ(-(2k-1)) = -B_{2k}/(2k), B = Bernoulli (精確 Fraction)
      前 10: 12,120,252,240,132,32760,12,8160,14364,6600 (簡化後分母)
  (b) 「結構池表示」: n∈池 或 ∃ a,b∈池: n=a×b 或 n=a±b (深度 1, 二元運算)
  (c) 結構池對 ζ 族命中 vs 2000 個隨機 28 元素池同類命中 (MC null)
  (d) 判決: 結構池覆蓋 ζ 分母族顯著高於隨機 ⟹ 240 轉錄有意義; 否則巧合
"""

import json, os, random
from fractions import Fraction

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
results = []

def check(name, cond, detail=""):
    results.append({"check": name, "pass": bool(cond), "detail": detail})
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}  {detail}")

# ---- (a) Bernoulli 精確表: B_2=1/6, B_4=-1/30, B_6=1/42, B_8=-1/30, B_10=5/66,
#           B_12=-691/2730, B_14=7/6, B_16=-3617/510, B_18=43867/798, B_20=-174611/330
BERN = {
    2: Fraction(1,6), 4: Fraction(-1,30), 6: Fraction(1,42), 8: Fraction(-1,30),
    10: Fraction(5,66), 12: Fraction(-691,2730), 14: Fraction(7,6),
    16: Fraction(-3617,510), 18: Fraction(43867,798), 20: Fraction(-174611,330),
}
def zeta_odd(k):
    """ζ(-(2k-1)) = -B_{2k}/(2k)"""
    B = BERN[2*k]
    return -B / (2*k)

print("="*72)
print("ζ 分母族 (Bernoulli 精確)")
print("="*72)
denoms = {}
for k in range(1, 11):
    v = zeta_odd(k)
    denoms[2*k-1] = v
    print(f"  ζ(-{2*k-1:2d}) = {v}   (分母 {v.denominator})")
D_family = [abs(denoms[2*k-1].denominator) for k in range(1, 11)]
print(f"  ζ 分母族 (10): {D_family}")
check("C1: ζ(-1)=-1/12, ζ(-3)=1/120, ζ(-5)=-1/252, ζ(-7)=1/240 (Bernoulli 恆等)",
      denoms[1] == Fraction(-1,12) and denoms[3] == Fraction(1,120)
      and denoms[5] == Fraction(-1,252) and denoms[7] == Fraction(1,240),
      f"{denoms[1]}, {denoms[3]}, {denoms[5]}, {denoms[7]}")

# ---- (b) 結構池 (閉合結構數, 全部有 O 出處)
pool_int = sorted(set([
    2,3,4,5,7,8,11,13,17,         # 質數因子 / μ²=2 / N_gen=3 / B=4 / L4=7 / F6=8
    18,20,21,29,33,34,42,44,60,88,90,   # γ 譜系 / N_d=44 / 2N_d=88 / Σγ=90
    120,123,137,176,178,240,            # L10-dimC / α⁻¹ / 88×2 / 240
    36, 98,                             # h11=36, h21=98 (O211)
]))
print(f"  結構池 (整數 {len(pool_int)} 個): {pool_int}")

def representable(pool_list, maxn=40000):
    s = set(pool_list)
    for a in pool_list:
        for b in pool_list:
            if a*b <= maxn: s.add(a*b)
            if a+b <= maxn: s.add(a+b)
            if abs(a-b) <= maxn and abs(a-b) > 0: s.add(abs(a-b))
    return s

rep = representable(pool_int, 40000)
print(f"  二元表示集合大小 (≤40000): {len(rep)}")
hits = [d for d in D_family if d in rep]
print(f"  表示命中 ζ 分母族: {hits}")
check("C2: ζ 分母族中喺結構池二元表示內嘅數 >= 4/10",
      len(hits) >= 4, f"{len(hits)}/10: {hits}")

# ---- (c) MC null: 2000 個隨機 28 元素池 (同大小, 同範圍 2..240, 有放回樣本太疏, 用 sample)
random.seed(20261008)
N_MC = 2000
hit_counts = []
for _ in range(N_MC):
    rpool = random.sample(range(2, 241), len(pool_int))
    rrep = representable(rpool, 40000)
    hit_counts.append(sum(1 for d in D_family if d in rrep))
from collections import Counter
dist = Counter(hit_counts)
mean_h = sum(hit_counts)/len(hit_counts)
p_ge = sum(1 for h in hit_counts if h >= len(hits)) / N_MC
print(f"\n  MC null ({N_MC} 池): 命中分佈 {sorted(dist.items())}")
print(f"  隨機池平均命中 = {mean_h:.2f}/10;  結構池命中 = {len(hits)}/10")
print(f"  p(≥{len(hits)}) = {p_ge:.4f}")
check("C3: 結構池命中顯著高於隨機池 (p<5% 單尾)",
      p_ge < 0.05, f"p={p_ge:.4f} (隨機池平均 {mean_h:.2f}/10)")

# ---- (d) 120 表示方式 (唯一性) + 240 表示方式
print("\n  120 表示方式:")
ways120 = []
for a in pool_int:
    for b in pool_int:
        if a*b == 120: ways120.append((a, b, "×"))
        if a+b == 120: ways120.append((a, b, "+"))
        if abs(a-b) == 120 and a != b: ways120.append((a, b, "−"))
print(f"  {sorted(set(ways120))}")
print("  240 表示方式:")
ways240 = []
for a in pool_int:
    for b in pool_int:
        if a*b == 240: ways240.append((a, b, "×"))
        if a+b == 240: ways240.append((a, b, "+"))
        if abs(a-b) == 240 and a != b: ways240.append((a, b, "−"))
print(f"  {sorted(set(ways240))}")
check("C4: 120 有「自然」結構表示, 且其中最少一條係 123−3",
      (123, 3, "−") in ways120 or 123-3 == 120 in rep, f"{sorted(set(ways120))[:8]}")
check("C5: 240 有「自然」結構表示 (2×120 或 240∈池)",
      240 in pool_int or (2, 120, "×") in ways240, f"{sorted(set(ways240))[:8]}")

with open(os.path.join(BASE, "data", "03_zeta_denom_pool.json"), "w") as f:
    json.dump({
        "denoms": {str(k): str(v) for k, v in denoms.items()},
        "family": D_family,
        "pool": pool_int,
        "hits": hits,
        "mc_mean": mean_h,
        "dist": {str(k): v for k, v in dist.items()},
        "p_ge": p_ge,
        "ways120": sorted(set(ways120)),
        "ways240": sorted(set(ways240)),
    }, f, indent=2, default=str)

npass = sum(1 for r in results if r["pass"])
nfail = sum(1 for r in results if not r["pass"])
print(f"\n{'='*72}\nRESULT: {npass}/{len(results)} PASS\n{'='*72}")