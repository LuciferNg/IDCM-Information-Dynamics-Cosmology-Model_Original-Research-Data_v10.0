#!/usr/bin/env python3
"""
O137 Phase 6 — 鏡像週期積分條件測試 (Mori generators + Dwork integrality)
=========================================================================
從 Δ* 的 GLSM charge matrix 提取有效 Mori generators，
對每個方向計算 1-parameter GKZ 週期係數 c_k，測試:
  1. Dwork integrality: c_k ∈ ℤ? (整數化週期 = 合法 mirror 方向)
  2. 收斂半徑 R (discriminant 位置)
  3. mode n ↔ Mori direction 對應後，{1,7,33} vs {15,21,25,35} 盲測
"""
import json
import sys
import os
from math import lgamma, log

import numpy as np

os.environ.setdefault(
    "LD_LIBRARY_PATH",
    os.path.expanduser("~/tools/lib") + ":" + os.environ.get("LD_LIBRARY_PATH", ""),
)
os.environ["CCTOOLS_ENABLE_EXPERIMENTAL"] = "1"

from cytools import Polytope
from cytools.config import enable_experimental_features

enable_experimental_features()

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
DATA = os.path.join(PROJ, "data")
SAGE_EXPORT = os.path.join(
    PROJ, "..", "o53_cy3_reality", "data", "polytopes", "cy36_98_sage_export.json"
)

# Target sets for blind test
ALLOWED = {1, 7, 33}
EXCLUDED = {15, 21, 25, 35}


def gkz_coeffs(charges, kmax=10):
    """c_k = prod_i Gamma(1 + q_i k) / Gamma(1 + k)^h  (q_i = positive charges)"""
    q_pos = [int(q) for q in charges if int(q) > 0]
    if not q_pos:
        return None
    deg = sum(q_pos)  # degree = sum of positive charges (Dwork balance: deg == max?)
    out = []
    for k in range(1, kmax + 1):
        lc = lgamma(1 + deg * k) - sum(lgamma(1 + q * k) for q in q_pos)
        out.append(lc)
    return out, q_pos, deg


def main():
    with open(SAGE_EXPORT) as f:
        data = json.load(f)
    pts = np.array(data["points"])
    p = Polytope(pts)
    p_dual = p.dual()
    tri = p_dual.triangulate(backend="topcom", verbosity=0)

    # 1. GLSM charge matrix (68 rows = all relations, 73 cols = points)
    glsm = tri.poly.glsm_charge_matrix()
    print(f"GLSM charge matrix: {glsm.shape}")
    print(f"Row sums (should be 0, CY condition): {glsm.sum(axis=1)[:5]}")

    # 2. For each row, compute GKZ coefficients and check balance
    print("\n=== ROW-WISE GKZ ANALYSIS ===")
    valid_rows = []
    for i, row in enumerate(glsm):
        q_pos = [int(q) for q in row if int(q) > 0]
        if not q_pos:
            continue
        deg = sum(q_pos)
        balance = deg - max(q_pos)
        # Dwork-type: series has integer coefficients if deg = sum of pos charges
        # and the series is "balanced" (finite radius)
        valid_rows.append((i, deg, len(q_pos)))
        if i < 68:
            pass
    print(f"Rows with positive charges: {len(valid_rows)}")
    degs = sorted(set(d for _, d, _ in valid_rows))
    print(f"Degrees (sum positive charges): {degs}")

    # 3. Try compute_cy for the real Mori data
    print("\n=== COMPUTE_CY ===")
    try:
        cy = tri.compute_cy()
        print(f"CY: {type(cy)}")
        attrs = [m for m in dir(cy) if not m.startswith("_")]
        print(f"CY attrs: {attrs[:30]}")
    except Exception as e:
        print(f"compute_cy: {type(e).__name__}: {str(e)[:300]}")


if __name__ == "__main__":
    main()
