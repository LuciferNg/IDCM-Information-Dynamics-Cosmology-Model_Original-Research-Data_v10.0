#!/usr/bin/env python3
"""
O53: HF vertices 之謎 — dual polytope 測試
=============================================
HF 20 vertices → CYTools h11=43, h12=37 (唔係 36,94)
試: 1. dual polytope
    2. 全 point set (包含 interior)
    3. 唔同 normal form
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53: HF vertices 之謎")
print("=" * 70)

from cytools import Polytope

# 讀取 control_36_94.poly (HF 20 vertices)
verts = []
with open(os.path.join(BASE, 'control_36_94.poly')) as f:
    for line in f:
        line = line.strip()
        if line:
            verts.append([int(x) for x in line.split()])
verts = np.array(verts)
p = Polytope(verts)
print(f"原始: h11={p.h11()}, h12={p.h12()}, reflex={p.is_reflexive()}")
print(f"  n_vertices={len(p.vertices())}, n_points={len(p.points())}")

# 1. dual
pd = p.dual()
print(f"\n[1] dual: h11={pd.h11()}, h12={pd.h12()}")
print(f"  n_vertices={len(pd.vertices())}, n_points={len(pd.points())}")

# 2. 用全部 points (包含 interior)
pts_all = p.points()
print(f"\n[2] 全部 points ({len(pts_all)}):")
p2 = Polytope(pts_all)
print(f"  h11={p2.h11()}, h12={p2.h12()}")

# 3. dual 嘅 points
pd_pts = pd.points()
print(f"\n[3] dual points ({len(pd_pts)}):")
p3 = Polytope(pd_pts)
print(f"  h11={p3.h11()}, h12={p3.h12()}")

# 4. 試下 vertices 有冇 interior points 漏咗
# HF 話 point_count 可能係 132 — 但我哋只有 20 個 vertices
# 需要生成全部 132 points? Polytope.points() 會做
print(f"\n[4] 原始 polytope 全部 points:")
print(f"  n_points = {len(p.points())}")

# 關鍵: (36,98) 嘅 Sage export 有 48 points (包含 origin)
# HF 版本可能係將 vertices 存成唔同嘢
# 等我用 pyarrow 讀返 (36,98) 嘅完整數據
import pyarrow.parquet as pq
pf = pq.ParquetFile(os.path.join(BASE, '..', 'polytopes-4d', 'polytopes-4d-20-vertices.parquet'))
# 讀取 metadata columns
cols = pf.schema.names
print(f"\n[5] HF columns: {cols}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)