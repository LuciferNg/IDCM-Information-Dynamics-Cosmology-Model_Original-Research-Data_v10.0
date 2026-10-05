#!/usr/bin/env python3
"""
O53: HF 數據集 metadata 準確性檢查
=====================================
發現: HF (36,98) entry 實際係 h11=43/h12=37
檢查: 系統性問題定單一錯誤?
抽樣 20 個 h11=36 entries 驗證
"""
import os, json, math, sys
import numpy as np
import pyarrow.parquet as pq

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53: HF metadata 抽樣檢查")
print("=" * 70)

from cytools import Polytope

pf = pq.ParquetFile(os.path.join(BASE, '..', 'polytopes-4d', 'polytopes-4d-20-vertices.parquet'))
h11 = pf.read(columns=['h11']).column('h11').to_pylist()
h12 = pf.read(columns=['h12']).column('h12').to_pylist()

# 抽樣 h11=36 嘅 entries
indices = [i for i, h in enumerate(h11) if h == 36]
print(f"h11=36 總數: {len(indices)}")

# 抽樣 10 個 (唔同 h12)
rng = np.random.default_rng(42)
sample_idx = rng.choice(indices, size=min(10, len(indices)), replace=False)

def read_vertices(idx):
    rg_size = pf.metadata.num_rows // pf.metadata.num_row_groups + 1
    rg_idx = idx // rg_size
    rg = pf.read_row_group(rg_idx, columns=['vertices'])
    local_idx = idx - rg_idx * rg_size
    return rg.column('vertices')[local_idx].as_py()

mismatch = 0
print(f"\n抽樣 10 個 h11=36 entries:")
for idx in sample_idx:
    meta_h12 = h12[idx]
    verts = np.array(read_vertices(idx), dtype=int)
    p = Polytope(verts)
    ct_h11, ct_h12 = p.h11(), p.h12()
    match = (meta_h12 == ct_h12)
    if not match:
        mismatch += 1
    print(f"  idx {idx}: meta h12={meta_h12:3d}, CYTools h12={ct_h12:3d}, h11={ct_h11:3d} {'✅' if match else '❌'}")

print(f"\n抽樣結果: {10 - mismatch}/10 匹配, {mismatch} 個唔匹配")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)