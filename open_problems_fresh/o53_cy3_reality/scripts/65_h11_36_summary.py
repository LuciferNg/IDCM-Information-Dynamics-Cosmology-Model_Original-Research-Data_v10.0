#!/usr/bin/env python3
"""
O53 路徑三: h11=36 家族 summary + 對照 polytope 選擇
======================================================
只統計, 唔印全部 h12 值
"""
import os, json, math
import numpy as np
import pandas as pd

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes-4d")
print("=" * 70)
print("O53 路徑三: h11=36 家族 summary")
print("=" * 70)

files = sorted([f for f in os.listdir(BASE) if f.endswith('.parquet')])
print(f"\n掃描 {len(files)} 個 files...")

total = 0
h12_counts = {}
our_pt = None  # (36,98)

for fname in files:
    path = os.path.join(BASE, fname)
    df = pd.read_parquet(path, columns=['h11', 'h12', 'vertex_count', 'point_count'])
    mask = df['h11'] == 36
    n = mask.sum()
    if n == 0:
        continue
    total += n
    rows = df[mask]
    # count h12
    for h12 in rows['h12'].unique():
        h12_counts[h12] = h12_counts.get(h12, 0) + len(rows[rows['h12'] == h12])
    # find (36,98)
    match = rows[rows['h12'] == 98]
    if len(match) > 0:
        our_pt = {'file': fname, 'vertices': match.iloc[0]['vertex_count'], 'points': match.iloc[0]['point_count']}
    # print summary per file
    print(f"  {fname}: {n} 個 h11=36  (h12 range {rows['h12'].min()}-{rows['h12'].max()})")

print(f"\n總共 {total} 個 h11=36 polytopes")
print(f"h12 分佈 (top 20):")
for h12, cnt in sorted(h12_counts.items(), key=lambda x: -x[1])[:20]:
    print(f"  h12={h12}: {cnt} 個")

if our_pt:
    print(f"\n📌 (36,98): 喺 {our_pt['file']} ({our_pt['vertices']} vertices, {our_pt['points']} points)")

# 揀對照: 同一 vertex count, 最接近 h12?
print(f"\n對照 polytope 建議:")
print(f"  同一 file 內 h12=98 以外嘅 polytope → 同 vertex count")
print(f"  最接近 h12 → h12=96 或 102")

# 檢查 06-vertices 內有冇 h12=96 或 102
df6 = pd.read_parquet(os.path.join(BASE, 'polytopes-4d-06-vertices.parquet'), columns=['h11', 'h12', 'vertex_count', 'point_count'])
mask6 = df6['h11'] == 36
for h12 in [96, 102, 100, 94, 104]:
    cnt = len(df6[mask6 & (df6['h12'] == h12)])
    if cnt > 0:
        print(f"  polytopes-4d-06-vertices.parquet: h12={h12} → {cnt} 個候選")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)