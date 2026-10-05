#!/usr/bin/env python3
"""
O53 決定性測試: h12 = Σγ + 2B 係咪 (36,98) 專屬?
=====================================================
所有 h11=36 polytope 嘅 h12, 邊個滿足 h12 = 90 + 8 = 98?
如果只有 (36,98) → K_Chain Hodge 閉合專屬!

擴展: 其他 (h11, h12) 組合有冇 K_Chain 表示?
h11 = Nd - 2B = 36 (固定)
h12 = Σγ + 2B = 98 (固定)
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53: h12 對照 — 其他 h11=36 嘅 h12 值")
print("=" * 70)

import pyarrow.parquet as pq

# 用 20-vertices parquet (h11=36 家族)
pf = pq.ParquetFile(os.path.join(BASE, '..', 'polytopes-4d', 'polytopes-4d-20-vertices.parquet'))
print(f"parquet rows: {pf.metadata.num_rows}")

# 讀 h11, h12 columns (可能好大 — 只讀 metadata?)
# 用 metadata 或者 scan
try:
    h11 = pf.read(columns=['h11']).column('h11').to_pylist()
    h12 = pf.read(columns=['h12']).column('h12').to_pylist()
    print(f"h11/h12 讀取完成: {len(h11)} rows")
    
    # 篩選 h11=36
    idx36 = [i for i, h in enumerate(h11) if h == 36]
    print(f"h11=36: {len(idx36)} 個")
    
    # h12 分佈
    h12_36 = [h12[i] for i in idx36]
    from collections import Counter
    dist = Counter(h12_36)
    print(f"\nh12 分佈 (h11=36):")
    for h, c in sorted(dist.items())[:20]:
        marker = " ← 98!" if h == 98 else ""
        print(f"  h12={h}: {c} 個{marker}")
    
    # 有冇其他 h12 = 98?
    n98 = sum(1 for h in h12_36 if h == 98)
    print(f"\nh12=98: {n98} 個")
    
    # 其他 h12 有冇 K_Chain 表示?
    # h12 = 90 + 2B = 98 係唯一 (B=4 固定)
    # 但其他 h12 可以用唔同 B?
    print(f"\n[對照] 其他 h12 用 K_Chain 表示 (h12 = Σγ + 2B, B 可變):")
    print(f"  B=4: h12 = 98")
    print(f"  B=3: h12 = 96")
    print(f"  B=5: h12 = 100")
    print(f"  有冇 h12 ∈ {{96, 98, 100}}?")
    for h in [96, 98, 100]:
        c = dist.get(h, 0)
        print(f"    h12={h}: {c} 個 {'✓' if c > 0 else ''}")
    
except Exception as e:
    print(f"FAIL: {str(e)[:200]}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)