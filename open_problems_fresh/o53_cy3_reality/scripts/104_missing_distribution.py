#!/usr/bin/env python3
"""
O53 決定性測試: 「缺失 4 divisors 全喺 Block 0」係咪 (36,98) 專屬?
====================================================================
(36,98): divisor_basis 缺 [2,3,6,7] (0-based) — 全部喺 Block 0

對照: 其他 h12 (20,21,22,23) 嘅 divisor_basis 缺失分佈?
如果只有 (36,98) 有「缺失全喺同一 block」→ 獨特結構
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53: 缺失 divisors 分佈 — 對照測試")
print("=" * 70)

from cytools import Polytope
from cytools.config import enable_experimental_features
enable_experimental_features()

# (36,98) 家族 — 用 all_36_98.poly 前幾個
polytopes = []
with open(os.path.join(BASE, 'all_36_98.poly')) as f:
    lines = [l.strip() for l in f if l.strip()]
i = 0
while i < len(lines):
    parts = lines[i].split()
    if len(parts) == 2 and parts[0].isdigit():
        n = int(parts[0])
        verts = []
        for j in range(n):
            verts.append([int(x) for x in lines[i+1+j].split()])
        polytopes.append(np.array(verts))
        i += 1 + n
    else:
        i += 1

def missing_divs(p):
    tri = p.triangulate()
    cy = tri.get_cy()
    db = cy.divisor_basis()
    missing = sorted(set(range(36)) - set(d - 1 for d in db))
    return missing, cy

print(f"[1] (36,98) 家族 (all_36_98.poly 前 8 個):")
for k in range(min(8, len(polytopes))):
    p = Polytope(polytopes[k])
    try:
        missing, cy = missing_divs(p)
        n_b0 = sum(1 for m in missing if m < 12)
        n_b1 = sum(1 for m in missing if 12 <= m < 24)
        n_b2 = sum(1 for m in missing if m >= 24)
        print(f"  [{k}] {len(polytopes[k])}v: missing={missing}, block 分佈 ({n_b0},{n_b1},{n_b2})")
    except Exception as e:
        print(f"  [{k}] FAIL: {str(e)[:60]}")

# 對照: HF 數據其他 h12 (驗證 h11=36)
print(f"\n[2] 其他 h12 對照:")
import pyarrow.parquet as pq
pf = pq.ParquetFile(os.path.join(BASE, '..', 'polytopes-4d', 'polytopes-4d-20-vertices.parquet'))
h11 = pf.read(columns=['h11']).column('h11').to_pylist()
h12 = pf.read(columns=['h12']).column('h12').to_pylist()

indices = [i for i, h in enumerate(h11) if h == 36]
# 抽樣唔同 h12
seen = {}
for idx in indices:
    h = h12[idx]
    if h not in seen:
        seen[h] = idx
    if len(seen) >= 8:
        break

def read_vertices(idx):
    rg_size = pf.metadata.num_rows // pf.metadata.num_row_groups + 1
    rg_idx = idx // rg_size
    rg = pf.read_row_group(rg_idx, columns=['vertices'])
    local_idx = idx - rg_idx * rg_size
    return rg.column('vertices')[local_idx].as_py()

tested = 0
for h, idx in seen.items():
    if tested >= 5:
        break
    verts = np.array(read_vertices(idx), dtype=int)
    p = Polytope(verts)
    if p.h11() != 36:
        continue
    try:
        missing, cy = missing_divs(p)
        n_b0 = sum(1 for m in missing if m < 12)
        n_b1 = sum(1 for m in missing if 12 <= m < 24)
        n_b2 = sum(1 for m in missing if m >= 24)
        print(f"  h12={h}: missing={missing}, block 分佈 ({n_b0},{n_b1},{n_b2})")
        tested += 1
    except Exception as e:
        print(f"  h12={h}: FAIL {str(e)[:50]}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)