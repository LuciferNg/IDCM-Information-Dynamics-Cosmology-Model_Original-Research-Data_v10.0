#!/usr/bin/env python3
"""
O53 決定性測試: (36,98) 家族 block 結構普適性
================================================
all_36_98.poly 100 個 (36,98) 實例
檢查每個嘅 3×12 block ratio + Schur block-triangular

如果全部都有 ratio ~3:
  → 3×12 block 係 (36,98) 家族通用性質
如果只有部分:
  → 特定 polytope 先有 → K_Chain 唯一性
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53: (36,98) 家族 block 普適性")
print("=" * 70)

from cytools import Polytope
from cytools.config import enable_experimental_features
enable_experimental_features()

# 解析 polytopes
polytopes = []
with open(os.path.join(BASE, 'all_36_98.poly')) as f:
    lines = [l.strip() for l in f if l.strip()]
i = 0
while i < len(lines):
    parts = lines[i].split()
    if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
        n = int(parts[0])
        verts = []
        for j in range(n):
            verts.append([int(x) for x in lines[i+1+j].split()])
        polytopes.append(np.array(verts))
        i += 1 + n
    else:
        i += 1

print(f"總共 {len(polytopes)} 個實例")

# 對前 10 個計算 block ratio
blocks = [(0,12), (12,24), (24,36)]
results = []

for k in range(min(15, len(polytopes))):
    p = Polytope(polytopes[k])
    try:
        tri = p.triangulate()
        cy = tri.get_cy()
        inter = cy.intersection_numbers()
        K = np.zeros((36, 36, 36))
        for key, val in inter.items():
            if isinstance(key, tuple) and len(key) == 3:
                i0, j, kk = key
                if i0 < 36 and j < 36 and kk < 36:
                    K[i0, j, kk] = val
                    K[i0, kk, j] = val
                    K[j, i0, kk] = val
                    K[j, kk, i0] = val
                    K[kk, i0, j] = val
                    K[kk, j, i0] = val
        # ratio
        s_same = sum(np.abs(K[a:b, a:b, a:b]).sum() for a, b in blocks)
        s_cross = np.abs(K).sum() - s_same
        ratio = s_same / max(s_cross, 1e-9)
        nnz = np.count_nonzero(K)
        results.append((k, len(polytopes[k]), ratio, nnz, p.h12()))
        print(f"  [{k}] {len(polytopes[k])}v: ratio = {ratio:.3f}, nnz = {nnz}")
    except Exception as e:
        print(f"  [{k}] FAIL: {str(e)[:80]}")

print(f"\n結果統計:")
ratios = [r[2] for r in results]
if ratios:
    print(f"  ratio mean = {np.mean(ratios):.3f}, std = {np.std(ratios):.3f}")
    print(f"  ratio range = [{min(ratios):.3f}, {max(ratios):.3f}]")
    print(f"  > 2.0: {sum(1 for r in ratios if r > 2.0)}/{len(ratios)}")
    print(f"  > 3.0: {sum(1 for r in ratios if r > 3.0)}/{len(ratios)}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)