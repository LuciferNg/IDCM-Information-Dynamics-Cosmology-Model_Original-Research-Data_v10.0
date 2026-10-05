#!/usr/bin/env python3
"""
O53 路徑三: 掃描全部 parquet 搵 h11=36 polytopes
====================================================
"""
import os, json, math
import numpy as np
import pandas as pd

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes-4d")
print("=" * 70)
print("O53 路徑三: 掃描 h11=36 家族")
print("=" * 70)

# 掃描全部 parquet 搵 h11=36
files = sorted([f for f in os.listdir(BASE) if f.endswith('.parquet')])
print(f"\n掃描 {len(files)} 個 parquet files...")

h11_36 = []
for fname in files:
    path = os.path.join(BASE, fname)
    df = pd.read_parquet(path, columns=['h11', 'h12', 'vertex_count', 'point_count'])
    mask = df['h11'] == 36
    n = mask.sum()
    if n > 0:
        rows = df[mask]
        for _, row in rows.iterrows():
            h11_36.append({
                'file': fname,
                'h11': row['h11'],
                'h12': row['h12'],
                'vertices': row['vertex_count'],
                'points': row['point_count'],
                'chi': 2 * (row['h11'] - row['h12'])
            })
        print(f"  {fname}: {n} 個 h11=36 (h12={rows['h12'].tolist()})")

print(f"\n總共 {len(h11_36)} 個 h11=36 polytopes:")
for p in h11_36:
    print(f"  {p['file']}: h11={p['h11']}, h12={p['h12']}, χ={p['chi']}, "
          f"n_vertices={p['vertices']}, n_points={p['points']}")

# 標記我哋嘅 (36,98)
print(f"\n(36,98) — χ=-124: ", end="")
for p in h11_36:
    if p['h12'] == 98:
        print(f"✅ 找到! 喺 {p['file']} ({p['vertices']} vertices, {p['points']} points)")

print("\n" + "=" * 70)
print("掃描完成")
print("=" * 70)