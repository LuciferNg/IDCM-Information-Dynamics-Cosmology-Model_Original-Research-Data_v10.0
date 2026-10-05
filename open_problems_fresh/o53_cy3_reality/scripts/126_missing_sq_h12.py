#!/usr/bin/env python3
"""
O53 決定性測試: 缺失 divisors 平方和 = h12 係咪 (36,98) 專屬?
==================================================================
(36,98): missing [2,3,6,7], Σm² = 4+9+36+49 = 98 = h12!
其他 polytope 有冇?
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53: 缺失平方和 = h12 對照")
print("=" * 70)

from cytools import Polytope
from cytools.config import enable_experimental_features
enable_experimental_features()

# (36,98) 家族 (all_36_98.poly)
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

print(f"[1] (36,98) 家族:")
for k in range(min(8, len(polytopes))):
    p = Polytope(polytopes[k])
    try:
        tri = p.triangulate()
        cy = tri.get_cy()
        db = np.array(cy.divisor_basis()) - 1
        missing = sorted(set(range(36)) - set(db))
        sm2 = sum(m*m for m in missing)
        h12 = cy.h12()
        match = "✓✓✓" if sm2 == h12 else ""
        print(f"  [{k}] {len(polytopes[k])}v: missing={missing}, Σm²={sm2}, h12={h12} {match}")
    except Exception as e:
        print(f"  [{k}] FAIL: {str(e)[:50]}")

# 對照: 其他 h12
print(f"\n[2] 對照 (其他 h11=36, 唔同 h12):")
import pyarrow.parquet as pq
pf = pq.ParquetFile(os.path.join(BASE, '..', 'polytopes-4d', 'polytopes-4d-20-vertices.parquet'))
h11 = pf.read(columns=['h11']).column('h11').to_pylist()
h12 = pf.read(columns=['h12']).column('h12').to_pylist()
indices = [i for i, h in enumerate(h11) if h == 36]

# 抽樣幾個唔同 h12
seen = {}
for idx in indices:
    h = h12[idx]
    if h not in seen and h not in (36, 98):
        seen[h] = idx
    if len(seen) >= 6:
        break

tested = 0
for h, idx in seen.items():
    if tested >= 4:
        break
    rg_size = pf.metadata.num_rows // pf.metadata.num_row_groups + 1
    rg_idx = idx // rg_size
    try:
        rg = pf.read_row_group(rg_idx, columns=['vertices'])
        local_idx = idx - rg_idx * rg_size
        verts = np.array(rg.column('vertices')[local_idx].as_py(), dtype=int)
        p = Polytope(verts)
        if p.h11() != 36:
            continue
        tri = p.triangulate()
        cy = tri.get_cy()
        db = np.array(cy.divisor_basis()) - 1
        missing = sorted(set(range(36)) - set(db))
        sm2 = sum(m*m for m in missing)
        h12c = cy.h12()
        match = "✓✓✓" if sm2 == h12c else ""
        print(f"  h12={h}: missing={missing}, Σm²={sm2}, actual h12={h12c} {match}")
        tested += 1
    except Exception as e:
        print(f"  h12={h}: FAIL {str(e)[:50]}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)