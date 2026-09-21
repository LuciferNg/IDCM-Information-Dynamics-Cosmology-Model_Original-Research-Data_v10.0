#!/usr/bin/env python3
"""
O57 十二期 76: Sweet Spot 搜索 — 有限質量數 × 階層深度
=========================================================
scripts/75 發現 trade-off:
  φ^(35-i): 5 finite, 階層 9.8e16（太深）
  φ^(-i): 117 finite, 階層 ~1（太淺）

目標: ≥9 finite + 階層 ~1e8 (SM 1.7e8)

搜索:
  1. 混合: t = φ^(α·(35-i)) 掃描 α
  2. γ_n 譜 (95 finite)
  3. 加權組合
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 十二期 76: Sweet Spot 搜索")
print("=" * 72)

passed = 0
failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

import cytools
from cytools import Polytope
from cytools.config import enable_experimental_features
enable_experimental_features()

# ============ 1. 建立 CY ============
print("\n[1] 建立 CY")
d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
pts = np.array(d["points"])
p = Polytope(pts)
tri = p.triangulate()
cy = tri.get_cy()
basis = cy.divisor_basis()

def get_spectrum(t36):
    t32 = np.array([t36[b-1] for b in basis])
    cv = np.array(cy.compute_curve_volumes(t32))
    pos = cv[cv > 1e-10]
    if len(pos) == 0:
        return 0, 0, 0
    masses = np.exp(-pos)
    n_fin = np.sum(masses > 1e-30)
    fin = masses[masses > 1e-30]
    if len(fin) >= 2:
        ratio = fin.max()/fin.min()
    else:
        ratio = 1
    return n_fin, ratio, fin

# ============ 2. α 掃描 ============
print("\n[2] φ^(α·(35-i)) 掃描")
print(f"  {'α':>5s} {'finite':>6s} {'階層':>10s} {'評分':>8s}")
best = None
for alpha in np.linspace(-1, 2, 31):
    t36 = phi ** (alpha * (35 - np.arange(36)))
    n_fin, ratio, fin = get_spectrum(t36)
    # 評分: 要 n_fin >= 9, 階層接近 1e8 (log 距離)
    if n_fin >= 9:
        score = abs(math.log10(ratio) - 8)  # 距離 1e8
    else:
        score = 99 + (9 - n_fin)
    if best is None or score < best[0]:
        best = (score, alpha, n_fin, ratio)
    if n_fin >= 5:
        print(f"  {alpha:5.2f} {n_fin:6d} {ratio:10.2e} {score:8.2f}")

print(f"\n  最佳: α={best[1]:.2f}, finite={best[2]}, 階層={best[3]:.2e}")

# ============ 3. 詳細最佳 ============
print("\n[3] 最佳參數詳細")
if best[1] != 1:  # 唔係 φ^(35-i) 本身
    t36 = phi ** (best[1] * (35 - np.arange(36)))
    n_fin, ratio, fin = get_spectrum(t36)
    ms = np.sort(fin)[::-1]
    print(f"  α={best[1]:.2f}: {n_fin} finite, 階層 {ratio:.2e}")
    if n_fin >= 9:
        print(f"  top 9: {[f'{m:.4e}' for m in ms[:9]]}")
        print(f"  SM (sorted): {[f'{m:.1f}' for m in np.sort([2.2,1270,172760,4.7,93,4180,0.511,105.66,1776.86])[::-1]]}")
        # 校準
        sm_sorted = np.sort([2.2,1270,172760,4.7,93,4180,0.511,105.66,1776.86])[::-1]
        log_ratios = np.log(ms[:9]) - np.log(sm_sorted)
        log_err = np.std(log_ratios)
        print(f"  log-err: {log_err:.4f}")
        check("log-err < 1.5", log_err < 1.5, f"({log_err:.3f})")

# ============ 4. 總結 ============
print("\n" + "=" * 72)
print("十二期 76 總結:")
print("=" * 72)
print(f"""
  Sweet Spot 搜索:
  ─────────────────────────────────
  最佳: α={best[1]:.2f}, {best[2]} finite, 階層 {best[3]:.2e}

  trade-off 確認:
    φ^(35-i) (α=1): 5 finite, 9.8e16
    φ^(-i) (α=-1): 117 finite, ~1
    sweet spot: 揾到? {'✅' if best[2] >= 9 else '❌'}
""")

results = {
    "test": "O57 十二期 76: Sweet Spot",
    "best_alpha": float(best[1]),
    "best_finite": int(best[2]),
    "best_ratio": float(best[3]),
    "passed": passed, "failed": failed
}
with open("data/76_sweet_spot.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 十二期 76 完成!")
