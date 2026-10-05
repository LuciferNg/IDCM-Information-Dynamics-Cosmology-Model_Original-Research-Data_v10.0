#!/usr/bin/env python3
"""
O53: h12 高端分佈 — 98 係咪孤島?
=====================================
h11=36 家族 h12 高端 (h12 > 60) 分佈
如果 98 係孤島 → K_Chain 閉合更強
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53: h12 高端分佈")
print("=" * 70)

import pyarrow.parquet as pq
from collections import Counter

pf = pq.ParquetFile(os.path.join(BASE, '..', 'polytopes-4d', 'polytopes-4d-20-vertices.parquet'))
h11 = pf.read(columns=['h11']).column('h11').to_pylist()
h12 = pf.read(columns=['h12']).column('h12').to_pylist()

idx36 = [i for i, h in enumerate(h11) if h == 36]
h12_36 = [h12[i] for i in idx36]

# 完整分佈統計
dist = Counter(h12_36)
print(f"h11=36: {len(idx36)} 個")
print(f"h12 範圍: [{min(h12_36)}, {max(h12_36)}]")

# 高端分佈
print(f"\nh12 ≥ 60 分佈:")
for h in sorted([k for k in dist if k >= 60]):
    print(f"  h12={h}: {dist[h]} 個")

# 98 嘅鄰居
print(f"\n98 附近:")
for h in [94, 95, 96, 97, 98, 99, 100, 101, 102]:
    print(f"  h12={h}: {dist.get(h, 0)} 個")

# 統計顯著性: 98 係咪 outlier?
vals = np.array(sorted(dist.keys()))
counts = np.array([dist[h] for h in vals])
print(f"\n分佈形狀:")
print(f"  max h12 = {vals.max()}")
print(f"  top 5 h12: {list(zip(vals[-5:], counts[-5:]))}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)