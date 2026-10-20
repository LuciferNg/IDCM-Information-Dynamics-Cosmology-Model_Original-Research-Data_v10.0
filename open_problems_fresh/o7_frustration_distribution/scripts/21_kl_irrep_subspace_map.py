#!/usr/bin/env python3
"""
O7 — 21_kl_irrep_subspace_map.py (2026-10-11)
====================================================================
O7/natural-write-closure 第七輪: k↔ℓ 映射 — A₅ 子空間重合 (principal angles)
====================================================================
承接 script 20 M1/M2: 圖 Laplacian 模 ↔ 球面 Y_lm 交叉相關出現強配對
(ℓ1↔λ0.382, ℓ2↔λ1.0746, ℓ3↔λ1.7639∪2.618, ℓ4↔λ3.4481∪3.0)。

本輪: 子空間級驗證 — 每個 ℓ (2ℓ+1 維 Y span) 對每個 λ-簡併組 (圖譜 evec span)
      principal angles / 投影奇異值 → 重合度矩陣。若「ℓ ↔ λ 組」係結構,
      重合度應該接近 1 而其他接近 0 (A₅ 表示論: 維度匹配 + 子空間重合)。
"""

import math, re
from collections import defaultdict
import numpy as np

DATA = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/cmb_cold_spot/data'
results = []
def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))

print("=" * 76)
print("  O7 — k↔ℓ 子空間重合 (A₅ irrep 候選)")
print("=" * 76)

nodes = []
for i, line in enumerate(open(f'{DATA}/a5_nodes.txt')):
    if line.startswith('#'): continue
    p = line.split()
    nodes.append((float(p[0]), float(p[1])))
nodes = np.array(nodes)

adj = defaultdict(set)
for line in open(f'{DATA}/faces.txt'):
    if line.startswith('#'): continue
    m = re.search(r'\[([^\]]+)\]', line)
    vs = [int(x) for x in m.group(1).split(',')]
    for i in range(len(vs)):
        adj[vs[i]].add(vs[(i+1) % len(vs)])
        adj[vs[(i+1) % len(vs)]].add(vs[i])

from astropy.coordinates import SkyCoord
import astropy.units as AU
from scipy.special import lpmv
from math import factorial, sqrt

sc = SkyCoord(ra=nodes[:, 0]*AU.deg, dec=nodes[:, 1]*AU.deg, frame='icrs')
xyz = sc.cartesian.xyz.value
x, y, z = xyz[0], xyz[1], xyz[2]
th = np.arccos(np.clip(z, -1, 1)); ph = np.arctan2(y, x)

def ylm(l, m, th, ph):
    plm = lpmv(abs(m), l, np.cos(th))
    norm = sqrt((2*l+1)*factorial(l-abs(m))/(4*math.pi*factorial(l+abs(m))))
    if m == 0: return norm * plm
    if m > 0:  return sqrt(2)*norm * plm * np.cos(m*ph)
    return sqrt(2)*norm * plm * np.sin(-m*ph)

# ── 圖 Laplacian ──
L = np.zeros((60, 60))
for v in range(60):
    L[v, v] = len(adj[v])
    for w in adj[v]: L[v, w] = -1
evals, evecs = np.linalg.eigh(L)

# 簡併組: lambda -> evec span (orthonormal basis)
from collections import defaultdict as dd
groups = dd(list)
for k in range(60):
    groups[round(float(evals[k]), 6)].append(k)
lambdas = sorted(groups.keys())
print(f"  簡併組: { {str(l): len(v) for l, v in groups.items()} }")

def subspace(keys):
    M = evecs[:, keys].T
    # orthonormalize
    Q, R = np.linalg.qr(M.T)
    return Q  # 60 × r, orthonormal columns

def overlap(A, B):
    """principal angles cosine 平均 (A, B orthonormal column spans)"""
    # singular values of A^T B
    s = np.linalg.svd(A.T @ B, compute_uv=False)
    return s, s.mean(), s.max()

# ℓ 子空間
Yspan = {}
for l in range(5):
    Ys = np.array([ylm(l, m, th, ph) for m in range(-l, l+1)]).T
    Q, _ = np.linalg.qr(Ys)
    Yspan[l] = Q

print("\n─── ℓ 子空間 ↔ λ 簡併組 重合 (mean cos angle) ───")
print("    (維度: ℓ1=3, ℓ2=5, ℓ3=7, ℓ4=9)")
header = "  λ       " + "".join(f"ℓ{l:>8}" for l in range(1, 5))
print(header)
table = []
for lam in lambdas:
    if len(groups[lam]) < 3: continue
    A = subspace(groups[lam])
    row = []
    for l in range(1, 5):
        s, mean, mx = overlap(A, Yspan[l])
        row.append(mean)
    table.append((lam, len(groups[lam]), row))
    print(f"  {lam:8.4f} ({len(groups[lam])}d) " + "".join(f"{v:8.3f}" for v in row))

# 判定: ℓ3 應該 ↔ λ=1.7639 & λ=2.618 (7 維目標: 4+3)
# 檢查 ℓ3 (table row index 2) 嘅高重合 λ 組
print("\n  ℓ=3 高重合 λ 組 (>0.3):")
for lam, d, row in table:
    v = row[2]
    if v > 0.3:
        print(f"    λ={lam:.4f} ({d}d) → ℓ3 重合 {v:.3f}")

# 總重合: ℓ3 ↔ {1.7639, 2.618} union (用 fuzzy key)
def get_group(lam):
    for k in groups:
        if abs(k - lam) < 1e-4: return groups[k]
    return []
A3k = get_group(1.7639) + get_group(2.6180)
A3 = subspace(A3k)
s, mean, mx = overlap(A3, Yspan[3])
print(f"  ℓ3 ↔ (λ1.7639[{len(get_group(1.7639))}d] + λ2.618[{len(get_group(2.6180))}d]) : mean={mean:.3f} max={mx:.3f} (7維目標)")
check("K1a: ℓ3 ↔ λ1.7639∪λ2.618 重合 mean > 0.9", mean > 0.9, f"mean={mean:.3f}")

# ℓ1 ↔ λ0.382
A1 = subspace(get_group(0.3820))
s1, m1, x1 = overlap(A1, Yspan[1])
print(f"  ℓ1 ↔ λ0.382 (3d): mean={m1:.3f} max={x1:.3f}")
check("K1b: ℓ1 ↔ λ0.382 重合 mean > 0.7", m1 > 0.7, f"mean={m1:.3f}")

# ℓ2 ↔ λ1.0746
A2 = subspace(get_group(1.0746))
s2, m2, x2 = overlap(A2, Yspan[2])
print(f"  ℓ2 ↔ λ1.0746 (5d): mean={m2:.3f} max={x2:.3f}")
check("K1c: ℓ2 ↔ λ1.0746 重合 mean > 0.7", m2 > 0.7, f"mean={m2:.3f}")

# ℓ4 ↔ λ3.4481 ∪ λ3.0
A4 = subspace(get_group(3.4481) + get_group(3.0000))
s4, m4, x4 = overlap(A4, Yspan[4])
print(f"  ℓ4 ↔ λ3.4481∪λ3.0: mean={m4:.3f} max={x4:.3f}")
check("K1d: ℓ4 ↔ λ3.4481∪λ3.0 重合 mean > 0.6", m4 > 0.6, f"mean={m4:.3f}")

# ── 總結 ──
print("\n" + "=" * 76)
print(f"  結果: {sum(results)}/{len(results)} PASS")
print("=" * 76)