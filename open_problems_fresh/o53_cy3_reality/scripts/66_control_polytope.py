#!/usr/bin/env python3
"""
O53 路徑三: 讀取對照 polytope vertices
========================================
"""
import os, json, math, sys
import numpy as np
import pyarrow.parquet as pq

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes-4d")
POLY = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53 路徑三: 讀取 vertices")
print("=" * 70)

pf = pq.ParquetFile(os.path.join(BASE, 'polytopes-4d-20-vertices.parquet'))

# 逐批讀取, 搵 h11=36 嘅 rows + 記錄 index
h11_col = pf.read(columns=['h11']).column('h11').to_pylist()
h12_col = pf.read(columns=['h12']).column('h12').to_pylist()

# 搵 (36,98) 同 h12=96/100
our_indices = [i for i, (h11v, h12v) in enumerate(zip(h11_col, h12_col)) if h11v == 36 and h12v == 98]
print(f"(36,98): {len(our_indices)} 個, indices={our_indices[:5]}")

# 搵 h12 最接近 98 嘅 (唔係 98)
nearby = []
for target in [96, 100, 94, 102, 92, 104]:
    idxs = [i for i, (h11v, h12v) in enumerate(zip(h11_col, h12_col)) if h11v == 36 and h12v == target]
    if idxs:
        nearby.append((target, idxs[0]))
        print(f"h12={target}: {len(idxs)} 個, first index={idxs[0]}")

# 讀取指定 row 嘅 vertices
def read_vertices(idx):
    """讀取第 idx 行嘅 vertices 數據"""
    # 用 row_group 定位
    rg_size = pf.metadata.num_rows // pf.metadata.num_row_groups + 1
    rg_idx = idx // rg_size
    # 讀取該 row group 嘅 vertices column
    rg = pf.read_row_group(rg_idx, columns=['vertices'])
    local_idx = idx - rg_idx * rg_size
    return rg.column('vertices')[local_idx].as_py()

# 讀取 (36,98) 嘅 vertices
if our_indices:
    idx = our_indices[0]
    verts = read_vertices(idx)
    print(f"\n(36,98) vertices:")
    print(f"  count: {len(verts)}")
    for v in verts[:6]:
        print(f"  {v}")
    # Save as PALP format
    out_path = os.path.join(POLY, "cy36_98_hf.poly")
    with open(out_path, 'w') as f:
        for v in verts:
            f.write(' '.join(str(x) for x in v) + '\n')
    print(f"  ✅ Saved: {out_path}")

# 讀取對照 polytope
if nearby:
    target, idx = nearby[0]
    verts = read_vertices(idx)
    print(f"\n對照 h12={target} vertices:")
    print(f"  count: {len(verts)}")
    for v in verts[:6]:
        print(f"  {v}")
    out_path = os.path.join(POLY, f"control_h11_36_h12_{target}.poly")
    with open(out_path, 'w') as f:
        for v in verts:
            f.write(' '.join(str(x) for x in v) + '\n')
    print(f"  ✅ Saved: {out_path}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)