#!/usr/bin/env python3
"""
O53 路徑三: HuggingFace polytopes-4d 數據探索
================================================
讀取 polytopes-4d-36-vertices.parquet + 統計 h11=36 家族
"""
import os, json, math
import numpy as np
import pandas as pd

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes-4d")
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53 路徑三: HuggingFace 數據探索")
print("=" * 70)

# --- [1] 讀取 h11=36 parquet ---
print("\n[1] polytopes-4d-36-vertices.parquet:")
df = pd.read_parquet(os.path.join(BASE, "polytopes-4d-36-vertices.parquet"))
print(f"    rows: {len(df)}")
print(f"    columns: {list(df.columns)}")
print(f"    size: {df.memory_usage(deep=True).sum()/1024:.1f} KB")
print(f"\n    First 3 rows:")
for i in range(min(3, len(df))):
    print(f"    Row {i}:")
    row = df.iloc[i]
    for c in df.columns:
        v = row[c]
        if isinstance(v, np.ndarray):
            print(f"      {c}: shape={v.shape}, dtype={v.dtype}")
        else:
            print(f"      {c}: {v}")

# --- [2] 搵我們的 polytope (36,98) ---
print("\n[2] 搵 (36,98) 匹配:")
# Check h21 column
if 'h21' in df.columns:
    match = df[df['h21'] == 98]
    print(f"    h21=98: {len(match)} rows")
    if len(match) > 0:
        print(f"    Index: {match.index.tolist()}")
        for c in df.columns:
            v = match.iloc[0][c]
            if isinstance(v, np.ndarray):
                print(f"      {c}: shape={v.shape}")
            elif not isinstance(v, (list, dict)):
                print(f"      {c}: {v}")

# --- [3] 所有 h11=36 polytopes 統計 ---
print(f"\n[3] h11=36 家族統計:")
print(f"    總數: {len(df)}")
if 'h21' in df.columns:
    h21s = df['h21'].value_counts().sort_index()
    print(f"    h21 分佈:")
    for h21, cnt in h21s.items():
        print(f"      h21={h21}: {cnt} 個")
    print(f"    h21 範圍: {df['h21'].min()} 至 {df['h21'].max()}")

# --- [4] vertices 格式 ---
print(f"\n[4] vertices 結構:")
v0 = df.iloc[0]['vertices']
print(f"    shape: {v0.shape}")
print(f"    dtype: {v0.dtype}")
print(f"    first: {v0[:3]}")
# 4D reflexive polytope vertices
print(f"    n_vertices: {v0.shape[0]}")
print(f"    dim: {v0.shape[1]}")

# --- [5] 試搵出 (36,98) 以外嘅 polytope 做對照 ---
print(f"\n[5] 對照 polytope 選擇:")
if 'h21' in df.columns:
    # 揀 h21 最接近 98 嘅另一 polytope
    for h21 in sorted(df['h21'].unique()):
        cnt = len(df[df['h21'] == h21])
        print(f"    h21={h21}: {cnt} 個")
    # 建議: h21=97 或 99 最近

print("\n" + "=" * 70)
print("數據探索完成")
print("=" * 70)