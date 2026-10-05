#!/usr/bin/env python3
"""
O137 Phase 3: 真 Yukawa Y = κ·J* 特徵值 vs γ_n 匹配
======================================================
測試: 真幾何 (無 WDVV 懲罰污染) 嘅同調特徵值譜,
      對 L 類內選擇嘅閉合。

Y = κ_ijk·J*^k (36×36), J* = Jstar_36D (O53 正則 Kähler 類)
"""
import json, numpy as np, math
from collections import defaultdict

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh'
raw = json.load(open(f'{BASE}/o53_cy3_reality/data/polytopes/cy36_98_intersection_full.json'))
K = np.array(raw['kappa'])
J = np.array(json.load(open(f'{BASE}/o53_cy3_reality/data/polytopes/Jstar_36D.json'))['Jstar_36D'])

phi = (1 + math.sqrt(5)) / 2
th = math.pi / 88
N = 44
gamma = np.array([4*math.sin(i*th)**2 for i in range(1, N+1)])
omega = np.array([2*math.sin(i*th) for i in range(1, N+1)])

def v2(n):
    k = 0
    while n % 2 == 0:
        n //= 2
        k += 1
    return k

cand = {1: 'e⁻', 7: 'μ⁻', 20: 'τ⁻', 14: 's', 33: 'b', 34: 'c'}

print("=" * 72)
print("O137 Phase 3: 真 Yukawa 特徵值 vs γ_n 匹配")
print("=" * 72)

# Y = κ·J* (36×36), 對稱化
Y = np.einsum('ijk,k->ij', K, J)
Y = (Y + Y.T) / 2
evals = np.linalg.eigvalsh(Y)
ev_nz = np.sort(evals)[::-1]
n_nz = np.sum(np.abs(evals) > 1e-10)
print(f"\n[1] Y (36×36) 特徵值: {n_nz} 非零")
print(f"    譜: {np.array2string(ev_nz, precision=6)}")

# [2] 匹配: γ_n vs |λ| (tol 10%)
print(f"\n[2] γ_n vs |Y 特徵值| 匹配 (tol 10%):")
matches = defaultdict(list)
for n in range(1, N+1):
    best = None
    for lam in ev_nz:
        if abs(lam) < 1e-12:
            continue
        rel = abs(gamma[n-1] - abs(lam)) / abs(lam)
        if rel < 0.10:
            if best is None or rel < best[1]:
                best = (lam, rel)
    if best:
        matches[n] = best

for n, (lam, rel) in sorted(matches.items()):
    tag = cand.get(n, '')
    print(f"    n={n:2d}{'★' if tag else ' '}: γ={gamma[n-1]:.5f} vs λ={lam:+.5f} (rel {rel*100:.1f}%) {tag}")

# [3] L 類內選擇檢查
print(f"\n[3] L 類內選擇 (v₂ 規則):")
for k in [0, 1, 2]:
    L = 44 // (2**k)
    cls_modes = [n for n in range(1, 45) if v2(n) == k]
    cls_cand = [n for n in cls_modes if n in cand]
    cls_match = [n for n in cls_modes if n in matches]
    print(f"    L={L:2d} (v₂={k}): 類={cls_modes}")
    print(f"        候選={cls_cand}, 匹配={cls_match}")

# [4] ω 匹配
print(f"\n[4] ω_n vs |λ| 匹配 (tol 10%):")
matches_w = {}
for n in range(1, N+1):
    best = None
    for lam in ev_nz:
        if abs(lam) < 1e-12:
            continue
        rel = abs(omega[n-1] - abs(lam)) / abs(lam)
        if rel < 0.10:
            if best is None or rel < best[1]:
                best = (lam, rel)
    if best:
        matches_w[n] = best
for n, (lam, rel) in sorted(matches_w.items()):
    tag = cand.get(n, '')
    print(f"    n={n:2d}{'★' if tag else ' '}: ω={omega[n-1]:.5f} vs λ={lam:+.5f} (rel {rel*100:.1f}%) {tag}")
