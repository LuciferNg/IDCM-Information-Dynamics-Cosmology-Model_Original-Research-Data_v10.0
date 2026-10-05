#!/usr/bin/env python3
"""
O53 決定性測試: 對照 polytope (36,94) 嘅 block 結構
=====================================================
如果 (36,94) 都有 3×12 block-triangular + ratio ~3:
  → h11=36 家族通用性質
如果冇:
  → (36,98) 獨有 → K_Chain 唯一性

問題: HF 提取嘅 control polytope (20 pts) 經 PALP 計出 H:37,43
唔係 (36,94) — 需要攞正確嘅 (36,94) polytope
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53: 對照 polytope 搵真身")
print("=" * 70)

# 用 pyarrow 讀取 20-vertices.parquet 搵 h11=36, h12=94 嘅正確 polytope
import pyarrow.parquet as pq
pf = pq.ParquetFile(os.path.join(BASE, '..', 'polytopes-4d', 'polytopes-4d-20-vertices.parquet'))
print(f"Rows: {pf.metadata.num_rows}")

# 讀取 h11, h12
h11 = pf.read(columns=['h11']).column('h11').to_pylist()
h12 = pf.read(columns=['h12']).column('h12').to_pylist()

# 搵 h11=36, h12=94 嘅 rows
targets = [i for i, (a, b) in enumerate(zip(h11, h12)) if a == 36 and b == 94]
print(f"(36,94): {len(targets)} 個, indices = {targets[:10]}")

# 讀取第一個嘅 vertices
if targets:
    idx = targets[0]
    rg_size = pf.metadata.num_rows // pf.metadata.num_row_groups + 1
    rg_idx = idx // rg_size
    rg = pf.read_row_group(rg_idx, columns=['vertices'])
    local_idx = idx - rg_idx * rg_size
    verts = rg.column('vertices')[local_idx].as_py()
    print(f"  vertices: {len(verts)} 個")
    print(f"  first 5: {verts[:5]}")
    # 儲存
    out = os.path.join(BASE, 'control_36_94.poly')
    with open(out, 'w') as f:
        for v in verts:
            f.write(' '.join(str(x) for x in v) + '\n')
    print(f"  ✅ Saved: {out}")
    
    # 用 CYTools 驗證 Hodge
    from cytools import Polytope
    p = Polytope(np.array(verts, dtype=int))
    print(f"  CYTools: h11={p.h11()}, h12={p.h12()}, reflex={p.is_reflexive()}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)