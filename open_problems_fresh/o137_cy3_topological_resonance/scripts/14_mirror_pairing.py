#!/usr/bin/env python3
"""
O137 Phase 5a: 鏡像 dual pairing 矩陣 — 模式選擇測試
======================================================
Reflexive polytope (Δ, Δ*): 每個 p ∈ Δ, q ∈ Δ* 有 ⟨p,q⟩ ≥ -1。

Hypothesis (鏡像拓撲鎖定):
  mode n (= pt n ∈ Δ) 係物理嘅 ⟺ 佢喺 Δ* 中有「tight partner」
  q 使得 ⟨pt_n, q⟩ = -1 (boundary lock) 或特定 pairing 結構。

核心結構事實:
  l(Δ) = 48 (h11=36), l(Δ*) = 85
  Batyrev: Σl*(facets_Δ) = 48-5-36 = 7
           Σl*(facets_Δ*) = 85-5-36 = 44 = Nd ★
  → 鏡像 facets 嘅 interior points 數 = 44 = K_Chain sites!
"""
import json, numpy as np, math
from cytools import Polytope
from cytools.config import enable_experimental_features

enable_experimental_features()
BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh'
d = json.load(open(f'{BASE}/o53_cy3_reality/data/polytopes/cy36_98_sage_export.json'))
pts = np.array(d['points'])   # Δ: 48×4
p = Polytope(pts.tolist())
p_dual = p.dual()
pts_dual = np.array(p_dual.points())   # Δ*: 85×4

cand = {1: 'e⁻', 7: 'μ⁻', 20: 'τ⁻', 14: 's', 33: 'b', 34: 'c'}
def v2(n):
    k = 0
    while n % 2 == 0:
        n //= 2
        k += 1
    return k

print("=" * 76)
print("O137 Phase 5a: 鏡像 dual pairing")
print("=" * 76)
print(f"Δ: {pts.shape[0]} pts (h11=36), Δ*: {pts_dual.shape[0]} pts")
print(f"Batyrev: Σl*(facets_Δ*) = {pts_dual.shape[0]} - 5 - 36 = {pts_dual.shape[0]-5-36} = Nd ★")

# [1] dual pairing 矩陣
P = pts @ pts_dual.T   # 48×85
print(f"\n[1] pairing 矩陣 {P.shape}:")
print(f"    min = {P.min()}, max = {P.max()}")
print(f"    ⟨p,q⟩ = -1 嘅 pairs: {(P == -1).sum()}")
print(f"    ⟨p,q⟩ = 0 嘅 pairs: {(P == 0).sum()}")
print(f"    ⟨p,q⟩ ≥ 1 嘅 pairs: {(P >= 1).sum()}")

# [2] 每個 mode 嘅 tight partner 數 (#{q ∈ Δ*: ⟨pt_n, q⟩ = -1})
# 注意: mode n ↔ pt n (1-based) = pts[n] (0-based idx)
# pts[0] = origin (apex, 唔係 prime divisor)
print(f"\n[2] 每個 mode n 嘅 tight partner 數 (#{'{'}q ∈ Δ*: ⟨pt_n, q⟩ = -1{'}'}):")
tight = {}
for n in range(1, 45):
    if n <= pts.shape[0] - 1:  # mode 1..36: pts[1]..pts[36]; mode 37..44: maybe pts[37]..pts[43]?
        idx = min(n, pts.shape[0] - 1)  # safety
        t = int((P[idx] == -1).sum()) if idx < P.shape[0] else 0
        tight[n] = t
    else:
        tight[n] = None

for n in range(1, 45):
    tag = cand.get(n, '')
    star = '★' if tag else ('B' if v2(n) >= 3 else ' ')
    t = tight[n]
    print(f"    n={n:2d}{star}: tight partners = {t} {tag}")

# [3] 統計: 候選 vs 非候選 tight partners
print(f"\n[3] 統計:")
c_n = [tight[n] for n in sorted(cand) if tight[n] is not None]
nc_n = [tight[n] for n in range(1, 45) if n not in cand and tight[n] is not None]
b_n = [tight[n] for n in range(1, 45) if v2(n) >= 3]
print(f"    候選 tight: {c_n}")
print(f"    非候選 tight: mean={np.mean(nc_n):.2f}, std={np.std(nc_n):.2f}, min={min(nc_n)}, max={max(nc_n)}")
print(f"    純玻色子 tight: {b_n}")

# [4] 其他 pairing 條件
print(f"\n[4] 其他條件掃描:")
for cond_name, cond in [('⟨p,q⟩ = -1', lambda v: v == -1),
                         ('⟨p,q⟩ = 0', lambda v: v == 0),
                         ('⟨p,q⟩ ≤ -1', lambda v: v <= -1),
                         ('⟨p,q⟩ ≥ 2', lambda v: v >= 2)]:
    counts = {}
    for n in range(1, 45):
        if n <= pts.shape[0] - 1:
            idx = min(n, pts.shape[0] - 1)
            counts[n] = int(cond(P[idx]).sum())
        else:
            counts[n] = 0
    cc = [counts[n] for n in sorted(cand)]
    nc_ = [counts[n] for n in range(1, 45) if n not in cand]
    bb = [counts[n] for n in range(1, 45) if v2(n) >= 3]
    print(f"    {cond_name}: 候選 {cc} | 非候選 mean {np.mean(nc_):.1f} | 玻色子 {bb}")
    # 候選 vs 非候選分離
    sep = (min(cc) > max(nc_)) or (max(cc) < min(nc_))
    print(f"      分離: {sep}")

json.dump({'pairing_min': float(P.min()), 'pairing_max': float(P.max()),
           'tight': {str(n): tight[n] for n in tight},
           'n_dual': pts_dual.shape[0]},
          open(f'{BASE}/o137_cy3_topological_resonance/data/mirror_pairing.json', 'w'), indent=1)
print("\n已保存 data/mirror_pairing.json")
