#!/usr/bin/env python3
"""
O53: K_Chain Hodge 表示 — 其他 h11 有冇?
=============================================
問題: h12 = Σγ + 2B = 98 只對 h11=36?
定係有其他 h11 都用同一表示?

方法: 檢查所有 h11, 邊個有 h12=98?
如果只有 h11=36 有 h12=98 → 更強
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53: h12=98 喺所有 h11 嘅分佈")
print("=" * 70)

import pyarrow.parquet as pq

pf = pq.ParquetFile(os.path.join(BASE, '..', 'polytopes-4d', 'polytopes-4d-20-vertices.parquet'))
h11 = pf.read(columns=['h11']).column('h11').to_pylist()
h12 = pf.read(columns=['h12']).column('h12').to_pylist()

# 搵所有 h12=98
idx98 = [i for i, h in enumerate(h12) if h == 98]
print(f"h12=98: {len(idx98)} 個")

from collections import Counter
dist98 = Counter(h11[i] for i in idx98)
print(f"h12=98 嘅 h11 分佈:")
for h, c in sorted(dist98.items()):
    print(f"  h11={h}: {c} 個")

# 對比: h12=96, 100 (B 變體)
print(f"\nB 變體對照:")
for target in [96, 100]:
    idx = [i for i, h in enumerate(h12) if h == target]
    d = Counter(h11[i] for i in idx)
    print(f"h12={target}: {len(idx)} 個")
    for h, c in sorted(d.items())[:10]:
        print(f"  h11={h}: {c} 個")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)