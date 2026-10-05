#!/usr/bin/env python3
"""
O53 路徑三: HF polytope vs 我哋嘅 (36,98) — 比對
====================================================
HF 嘅 cy36_98_hf.poly (20 pts) vs all_36_98.poly (6 vertices)
檢查係咪同一個 polytope
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

def read_poly(path):
    pts = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) == 2 and parts[0].isdigit():
                continue  # header
            pts.append([int(x) for x in parts])
    return np.array(pts, dtype=int)

print("=" * 70)
print("O53 路徑三: polytope 比對")
print("=" * 70)

hf = read_poly(os.path.join(BASE, 'cy36_98_hf.poly'))
ours = read_poly(os.path.join(BASE, 'all_36_98.poly'))
print(f"HF (36,98): {hf.shape}")
print(f"我哋 (36,98): {ours.shape}")

# 每個 polytope 嘅 lattice points (凸包內整數點)
def hull_points(pts):
    from scipy.spatial import ConvexHull
    # 凸包
    hull = ConvexHull(pts)
    # 生成 bounding box
    mins = pts.min(axis=0)
    maxs = pts.max(axis=0)
    # 粗略: 列出所有整數點喺凸包內
    lp = []
    # 用 half-space 表示: hull.equations
    for i in range(mins[0], maxs[0]+1):
        for j in range(mins[1], maxs[1]+1):
            for k in range(mins[2], maxs[2]+1):
                for l in range(mins[3], maxs[3]+1):
                    p = np.array([i, j, k, l])
                    if np.all(hull.equations @ np.append(p, 1) <= 1e-9):
                        lp.append(p)
    return np.array(lp)

# 太慢 - 用 scale 比較
print(f"\nHF 點範圍: {hf.min(axis=0)} 至 {hf.max(axis=0)}")
print(f"我哋 點範圍: {ours.min(axis=0)} 至 {ours.max(axis=0)}")

# 檢查 HF 20 點係咪包含我哋嘅 6 vertices
print(f"\n我哋嘅 6 vertices 係咪喺 HF 20 點入面:")
ours_set = {tuple(p) for p in ours}
hf_set = {tuple(p) for p in hf}
common = ours_set & hf_set
print(f"  共同點: {len(common)} / {len(ours_set)}")
print(f"  我哋獨有: {len(ours_set - hf_set)}")
print(f"  HF 獨有: {len(hf_set - ours_set)}")

# 檢查 HF 20 點係咪 all_36_98.poly 嘅完整點集 (48 pts)
all_pts = read_poly(os.path.join(BASE, 'all_36_98.poly'))
# all_36_98.poly 可能包含多個 polytope (967 行 = 6+6+...)
# 第一個 polytope 係 6 vertices
print(f"\nall_36_98.poly 全部行: {len(read_poly(os.path.join(BASE, 'all_36_98.poly')))}")

print("\n" + "=" * 70)
print("比對完成")
print("=" * 70)