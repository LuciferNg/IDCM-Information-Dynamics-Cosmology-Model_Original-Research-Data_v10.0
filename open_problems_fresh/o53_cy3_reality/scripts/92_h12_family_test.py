#!/usr/bin/env python3
"""
O53 最終普適性測試: 唔同 h12 嘅 h11=36 polytope block 結構
=============================================================
(36,98) 全部實例 ratio > 3.0 ✅
而家測試: 其他 h12 (36,94), (36,90), (36,102)... 有冇 block 結構?
→ 判斷: 3×12 block 係 h11=36 通用 定 (36,98) 專屬?
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53: h11=36 家族 (唔同 h12) block 結構")
print("=" * 70)

from cytools import Polytope
from cytools.config import enable_experimental_features
enable_experimental_features()

# 需要其他 (36, h12) 嘅 polytope — 用 all_36_98.poly 附近?
# 冇現成檔案 — 用 HF 數據? 但 metadata 唔可靠
# 替代: 用 CYTools 隨機生成 h11=36 嘅 polytope?
# CYTools 有 random triangulation 但冇隨機 polytope

# 方案: 我哋有 alltoric.spec (30,108 pairs) — 但只係 Hodge pairs, 冇 polytope 數據

# 實際方案: 用 HF 數據嘅 vertices (雖然 metadata 唔準, 但可以用 CYTools 驗證 h11=36)
print("用 HF 數據 (CYTools 驗證 h11=36 先):")
import pyarrow.parquet as pq
pf = pq.ParquetFile(os.path.join(BASE, '..', 'polytopes-4d', 'polytopes-4d-20-vertices.parquet'))
h11 = pf.read(columns=['h11']).column('h11').to_pylist()
h12 = pf.read(columns=['h12']).column('h12').to_pylist()

# 搵 h11=36 entries
indices = [i for i, h in enumerate(h11) if h == 36]
print(f"h11=36 entries: {len(indices)}")

def read_vertices(idx):
    rg_size = pf.metadata.num_rows // pf.metadata.num_row_groups + 1
    rg_idx = idx // rg_size
    rg = pf.read_row_group(rg_idx, columns=['vertices'])
    local_idx = idx - rg_idx * rg_size
    return rg.column('vertices')[local_idx].as_py()

# 測試 10 個唔同 h12 嘅 entries
rng = np.random.default_rng(7)
# 抽樣唔同 h12
unique_h12 = {}
for idx in indices:
    h = h12[idx]
    if h not in unique_h12:
        unique_h12[h] = idx
    if len(unique_h12) >= 15:
        break

blocks = [(0,12), (12,24), (24,36)]
results = []
tested = 0
for h, idx in list(unique_h12.items())[:10]:
    verts = np.array(read_vertices(idx), dtype=int)
    p = Polytope(verts)
    # 只測 h11=36 (CYTools 確認)
    if p.h11() != 36:
        print(f"  h12={h}: CYTools h11={p.h11()} (skip)")
        continue
    try:
        tri = p.triangulate()
        cy = tri.get_cy()
        inter = cy.intersection_numbers()
        K = np.zeros((36, 36, 36))
        for key, val in inter.items():
            if isinstance(key, tuple) and len(key) == 3:
                i0, j, kk = key
                if i0 < 36 and j < 36 and kk < 36:
                    K[i0, j, kk] = val
                    K[i0, kk, j] = val
                    K[j, i0, kk] = val
                    K[j, kk, i0] = val
                    K[kk, i0, j] = val
                    K[kk, j, i0] = val
        s_same = sum(np.abs(K[a:b, a:b, a:b]).sum() for a, b in blocks)
        s_cross = np.abs(K).sum() - s_same
        ratio = s_same / max(s_cross, 1e-9)
        results.append((h, ratio))
        print(f"  h12={h}: CYTools h12={p.h12()}, ratio = {ratio:.3f}")
        tested += 1
    except Exception as e:
        print(f"  h12={h}: FAIL {str(e)[:60]}")
    if tested >= 8:
        break

print(f"\n結果 ({len(results)} 個):")
if results:
    ratios = [r[1] for r in results]
    print(f"  mean = {np.mean(ratios):.3f}, range = [{min(ratios):.3f}, {max(ratios):.3f}]")
    print(f"  > 2.0: {sum(1 for r in ratios if r > 2.0)}/{len(ratios)}")
    print(f"  > 3.0: {sum(1 for r in ratios if r > 3.0)}/{len(ratios)}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)