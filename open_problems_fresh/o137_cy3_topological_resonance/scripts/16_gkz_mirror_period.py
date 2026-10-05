#!/usr/bin/env python3
"""
O137 Phase 5c — 鏡像三角剖分 + GKZ 週期計算
=============================================
用 TOPCOM (backend="topcom") 對鏡像 polytope Δ* (85 點, 4D reflexive)
做 regular star triangulation，提取 GKZ φ 向量，建立鏡像週期級數。

前置條件: TOPCOM + gfan 已安裝於 ~/tools/bin, libs 於 ~/tools/lib
  (LD_LIBRARY_PATH 須包含 ~/tools/lib)

輸出:
  data/dual_triangulation_data.json — triangulation 結構 + GKZ φ
  data/gkz_period_data.json        — charges + 週期係數 + 結構連結
"""
import json
import sys
import os
from collections import Counter
from math import lgamma

import numpy as np

class NumpyEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, (np.ndarray,)):
            return o.tolist()
        return super().default(o)

sys.path.insert(0, os.path.expanduser("~/tools/lib"))
os.environ.setdefault(
    "LD_LIBRARY_PATH",
    os.path.expanduser("~/tools/lib") + ":" + os.environ.get("LD_LIBRARY_PATH", ""),
)

from cytools import Polytope

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
DATA = os.path.join(PROJ, "data")
os.makedirs(DATA, exist_ok=True)

SAGE_EXPORT = os.path.join(
    PROJ, "..", "o53_cy3_reality", "data", "polytopes", "cy36_98_sage_export.json"
)


def main():
    with open(SAGE_EXPORT) as f:
        data = json.load(f)
    pts = np.array(data["points"])

    p = Polytope(pts)
    p_dual = p.dual()
    print(f"Δ  : {len(p.points())} pts (CY3 h11=36, h21=98)")
    print(f"Δ* : {len(p_dual.points())} pts (CY3 h11=98, h21=36)")

    # --- 1. TOPCOM triangulation (previously timed out on default backend) ---
    tri = p_dual.triangulate(backend="topcom", verbosity=0)
    phi = [int(x) for x in tri.gkz_phi()]
    simps = [[int(x) for x in s] for s in tri.simplices()]

    print(f"Triangulation: fine={tri.is_fine()}, regular={tri.is_regular()}, "
          f"star={tri.is_star()}, {len(simps)} simplices, {len(phi)} points")

    # --- 2. GKZ φ vector ---
    print(f"\nGKZ φ ({len(phi)} entries, sum={sum(phi)}):")
    for v, c in sorted(Counter(phi).items()):
        print(f"  φ={v:4d}: {c}")

    # --- 3. Charges q_i = φ_origin - φ_i (standard GKZ hypergeometric form) ---
    q = [phi[0] - phi[i] for i in range(1, len(phi))]
    print(f"\ncharges q_i = φ_origin − φ_i ({len(q)} values, sum={sum(q)}):")
    for v, c in sorted(Counter(q).items()):
        print(f"  q={v:4d}: {c}")

    # --- 4. Structural links to K_Chain ---
    SUM_GAMMA = 90.0  # 44-site K_Chain Σγ
    links = {
        "φ_origin = 4·Σγ (=360)": phi[0] == 4 * SUM_GAMMA,
        "Σφ = 20·Σγ (=1800)": sum(phi) == 20 * SUM_GAMMA,
        "φ[1] = 2·88 (=176)": phi[1] == 176,
    }
    print("\nK_Chain 結構連結:")
    for k, v in links.items():
        print(f"  {'✅' if v else '❌'} {k}")

    # --- 5. GKZ period coefficients ---
    # ω₀(z) = Σ_k c_k z^k,  c_k = Γ(1+360k)/∏Γ(1+q_i k)
    print("\nGKZ 週期係數 log c_k:")
    for k in range(1, 6):
        lc = lgamma(1 + phi[0] * k) - sum(lgamma(1 + qi * k) for qi in q)
        print(f"  log c_{k} = {lc:.3f}")

    S = sum(q)
    print(f"\n漸近: coef of k·log(k) = {phi[0] - S} "
          f"({'>0 有限半徑' if phi[0] - S > 0 else '<0 全函數'})")

    # --- 6. Save ---
    out_tri = {
        "dim": tri.dim(),
        "n_simplices": len(simps),
        "n_points": len(phi),
        "gkz_phi": phi,
        "phi_counter": {str(k): v for k, v in Counter(phi).items()},
        "phi_sum": sum(phi),
        "simplices": simps,
        "is_fine": tri.is_fine(),
        "is_regular": tri.is_regular(),
        "is_star": tri.is_star(),
        "h11": int(p_dual.h11()),
        "h21": int(p_dual.h21()),
    }
    out_gkz = {
        "gkz_phi": phi,
        "phi_origin": phi[0],
        "phi_sum": sum(phi),
        "charges_q": q,
        "sum_charges": S,
        "n_points_used": len(phi),
        "n_simplices": len(simps),
        "structural_links": links,
        "h11_mirror": int(p_dual.h11()),
        "h21_mirror": int(p_dual.h21()),
    }
    with open(os.path.join(DATA, "dual_triangulation_data.json"), "w") as f:
        json.dump(out_tri, f, indent=2, cls=NumpyEncoder)
    with open(os.path.join(DATA, "gkz_period_data.json"), "w") as f:
        json.dump(out_gkz, f, indent=2, cls=NumpyEncoder)
    print("\nSaved: data/dual_triangulation_data.json + data/gkz_period_data.json")


if __name__ == "__main__":
    main()
