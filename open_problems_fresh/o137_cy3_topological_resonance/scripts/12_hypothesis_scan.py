#!/usr/bin/env python3
"""
O137 Phase 4c: 對應假設掃描 — κ index ↔ mode 嘅 P_f 選擇律
=============================================================
問題: κ index i ↔ pt i (0-based) 確認, 但 κ ↔ mode 有兩個候選:
  H1: κ index i ↔ mode i+1   (divisor 0 = pt 0 = origin ↔ mode 1)
  H2: κ index i+1 ↔ mode i   (divisor 1 = pt 1 ↔ mode 1; divisor 0 唔用)

對每個假設 × 波函數版本, 計算 P_f(n) 並測試:
  - 候選 6 個係咪「突出」(|P_f| 排名 top 或 bottom)
  - 純玻色子 5 個係咪「被禁」(|P_f| ≈ 0)
"""
import json, numpy as np, math
from collections import defaultdict

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh'
raw = json.load(open(f'{BASE}/o53_cy3_reality/data/polytopes/cy36_98_intersection_full.json'))
K = np.array(raw['kappa'])

th = math.pi / 88
N = 44
gamma = np.array([4*math.sin(i*th)**2 for i in range(1, N+1)])
omega = np.array([2*math.sin(i*th) for i in range(1, N+1)])

cand = {1: 'e⁻', 7: 'μ⁻', 20: 'τ⁻', 14: 's', 33: 'b', 34: 'c'}
def v2(n):
    k = 0
    while n % 2 == 0:
        n //= 2
        k += 1
    return k
bosons = [n for n in range(1, 45) if v2(n) >= 3]

print("=" * 76)
print("O137 Phase 4c: 對應假設 × 波函數掃描")
print("=" * 76)

# 波函數版本 (返回 36-dim vector, i = κ index 0..35)
def wf_cos(n, shift):
    idx = np.arange(0, 36) + shift   # κ index 0..35 (+shift 做 mode 對應)
    return np.cos(2*np.pi*n*idx/88)

def wf_sin(n, shift):
    idx = np.arange(0, 36) + shift
    return np.sin(np.pi*n*idx/88)

def wf_chain(n, shift):
    # K_Chain 本徵函數 sin(πnk/88), k = site
    idx = np.arange(0, 36) + shift
    return np.sin(np.pi*n*idx/88)

results = {}
for hname, shift in [('H1 κ i↔mode i+1', 1), ('H2 κ i+1↔mode i', 0)]:
    for wname, wf in [('cos2πn/88', wf_cos), ('sinπn/88', wf_sin)]:
        key = f'{hname} × {wname}'
        Pf = {}
        for n in range(1, N+1):
            c = wf(n, shift)
            Pf[n] = np.einsum('ijk,i,j,k->', K, c, c, c)
        results[key] = Pf

# --- 分析: 每個組合嘅候選排名 + 玻色子抑制 ---
print(f"\n[1] 候選 |P_f| 排名 (of 44, 細=突出) + 純玻色子 |P_f|:")
for key, Pf in results.items():
    allv = np.array([Pf[n] for n in range(1, 45)])
    order = np.argsort(np.abs(allv))[::-1]
    ranks = {n+1: r for n, r in enumerate(order)}
    c_ranks = sorted((ranks[n], n, cand[n]) for n in cand)
    b_vals = np.abs([Pf[n] for n in bosons])
    print(f"\n  {key}:")
    print(f"    候選排名: {[(cand[n], r) for r, n, _ in sorted((r, n, c) for c, r, n in [(cand[n], ranks[n], n) for n in cand])]}")
    print(f"    候選 |P_f|: {[round(abs(Pf[n]),1) for n in sorted(cand)]}")
    print(f"    純玻色子 |P_f|: {[round(v,1) for v in b_vals]} (mean {b_vals.mean():.1f})")
    # 玻色子係咪全部細過候選?
    c_min = min(abs(Pf[n]) for n in cand)
    b_max = max(abs(Pf[n]) for n in bosons)
    print(f"    候選最小 |P_f| = {c_min:.1f}, 玻色子最大 |P_f| = {b_max:.1f}, 分離: {c_min > b_max}")

# --- [2] 直接對比: 6 候選 + 5 玻色子 + 33 其他 ---
print(f"\n[2] 最佳組合嘅完整譜 (H2 × sinπn/88):")
Pf = results['H2 κ i+1↔mode i × sinπn/88']
for n in range(1, N+1):
    tag = cand.get(n, '')
    star = '★' if tag else ('B' if v2(n) >= 3 else ' ')
    print(f"    n={n:2d}{star}: P_f = {Pf[n]:+12.4f} {tag}")

json.dump({k: {str(n): v for n, v in Pf.items()} for k, Pf in results.items()},
          open(f'{BASE}/o137_cy3_topological_resonance/data/pf_hypothesis_scan.json', 'w'), indent=1)
print("\n已保存 data/pf_hypothesis_scan.json")
