#!/usr/bin/env python3
"""
O137 Phase 2b: CY₃ 2-cycle 長度 (γ-weighted volume) — 充分性測試 v2
=====================================================================
映射確認: sr 36 點 = pt 1-36 → divisor index i ↔ pt i+1 ↔ mode n = i+1

長度定義 (4 種候選):
  L1 = support size #{k: κ_ijk ≠ 0}
  L3 = Σ_k κ_ijk                    (代數相交和)
  L4 = Σ_k γ_k·κ_ijk                (γ-weighted volume, O17 標準)
  L5 = Σ_k ω_k·κ_ijk                (ω-weighted)

費米子量子化: n·L ≡ 44 (mod 88) 用嘅 L 係「cycle 長度以 chain site 為單位」。
"""
import json, numpy as np
from collections import Counter

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh'
raw = json.load(open(f'{BASE}/o53_cy3_reality/data/polytopes/cy36_98_intersection_full.json'))
K = np.array(raw['kappa'])  # 36×36×36
d = json.load(open(f'{BASE}/o53_cy3_reality/data/polytopes/cy36_98_sage_export.json'))
adj = np.load(f'{BASE}/o137_cy3_topological_resonance/data/adjacency.npy')
n = adj.shape[0]

# K_Chain
th = np.pi / 88.0
N = 44
gamma = np.array([4*np.sin(i*th)**2 for i in range(1, N+1)])   # γ_i, i=1..44
omega = np.array([2*np.sin(i*th) for i in range(1, N+1)])

print("=" * 72)
print("O137 Phase 2b: 2-cycle 長度 (γ-weighted) — 充分性測試")
print("=" * 72)

# sr 36 點 = pt 1..36 = κ index 0..35
sr_pts = list(range(1, 37))
pairs = [(i, j) for i in range(1, 37) for j in range(i+1, 37) if adj[i, j] > 0]
print(f"\n[1] sr-internal adjacency pairs: {len(pairs)}")

L3s, L4s, L5s = [], [], []
for (i, j) in pairs:
    ii, jj = i-1, j-1
    col = K[ii, jj, :]                       # κ_{ij·} over 36 divisors
    L3s.append(float(col.sum()))
    L4s.append(float((gamma[:36] * col).sum()))
    L5s.append(float((omega[:36] * col).sum()))

L3a, L4a, L5a = np.array(L3s), np.array(L4s), np.array(L5s)
print(f"\n[2] 長度分佈:")
print(f"    L3 (代數和 Σκ): mean {L3a.mean():.3f}, std {L3a.std():.3f}, range [{L3a.min():.1f}, {L3a.max():.1f}]")
print(f"    L4 (γ-weighted): mean {L4a.mean():.3f}, std {L4a.std():.3f}, range [{L4a.min():.2f}, {L4a.max():.2f}]")
print(f"    L5 (ω-weighted): mean {L5a.mean():.3f}, std {L5a.std():.3f}, range [{L5a.min():.2f}, {L5a.max():.2f}]")

# 候選 L 值附近嘅 cycles (tol 5%)
print(f"\n[3] 結構長度 L ∈ {{4, 8, 11, 22, 44}} 附近 (tol 5%) 嘅 cycles:")
for Lname, La in [("L3", L3a), ("L4", L4a), ("L5", L5a)]:
    print(f"    {Lname}:")
    for L in [4, 8, 11, 22, 44]:
        hits = [(pairs[k], La[k]) for k in range(len(La)) if abs(La[k] - L) / L < 0.05]
        if hits:
            for (p, v) in hits[:6]:
                print(f"      L={L:2d}: cycle {p} → {v:.4f} ({abs(v-L)/L*100:.2f}%)")
        else:
            print(f"      L={L:2d}: 冇命中")

# [4] 候選模式嘅 cycles + 長度
print(f"\n[4] 候選模式 (pt = mode) 嘅非零 cycles:")
cand = {1: 'e⁻', 7: 'μ⁻', 20: 'τ⁻', 14: 's', 33: 'b', 34: 'c'}
for n, name in cand.items():
    my = [(i, j, k) for k, (i, j) in enumerate(pairs) if i == n or j == n]
    nz = [(i, j, L3s[k], L4s[k], L5s[k]) for (i, j, k) in my if abs(L3s[k]) > 1e-9 or abs(L4s[k]) > 1e-9]
    print(f"    n={n:2d} ({name}): {len(my)} cycles, {len(nz)} 非零")
    for (i, j, l3, l4, l5) in nz[:8]:
        print(f"      ({i:2d},{j:2d}): L3={l3:8.2f}  L4={l4:8.3f}  L5={l5:8.3f}")

# [5] 保存 (fix int64)
def clean(x):
    return [float(v) for v in x]
json.dump({'pairs': [[int(a), int(b)] for (a, b) in pairs],
           'L3': clean(L3s), 'L4': clean(L4s), 'L5': clean(L5s)},
          open(f'{BASE}/o137_cy3_topological_resonance/data/cycle_lengths_v2.json', 'w'), indent=1)
print("\n已保存 data/cycle_lengths_v2.json")
