#!/usr/bin/env python3
"""
O53: all_36_98.poly 多個實例分析
===================================
all_36_98.poly 有 967 行 — 多個 polytope 實例
每個可能有唔同 block 結構 → 家族普適性測試
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53: all_36_98.poly 多實例")
print("=" * 70)

# 解析 PALP 格式: header "N 4" + N 行
polytopes = []
with open(os.path.join(BASE, 'all_36_98.poly')) as f:
    lines = [l.strip() for l in f if l.strip()]
i = 0
while i < len(lines):
    parts = lines[i].split()
    if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
        n = int(parts[0])
        dim = int(parts[1])
        verts = []
        for j in range(n):
            verts.append([int(x) for x in lines[i+1+j].split()])
        polytopes.append(np.array(verts))
        i += 1 + n
    else:
        i += 1

print(f"解析到 {len(polytopes)} 個 polytope 實例")
for k, p in enumerate(polytopes):
    print(f"  [{k}] {p.shape[0]} vertices")

# 用 CYTools 驗證每個
from cytools import Polytope
print(f"\nCYTools 驗證:")
for k, p in enumerate(polytopes[:10]):
    cp = Polytope(p)
    print(f"  [{k}] h11={cp.h11()}, h12={cp.h12()}, n_pts={len(cp.points())}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)