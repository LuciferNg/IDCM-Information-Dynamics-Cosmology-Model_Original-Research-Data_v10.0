#!/usr/bin/env python3
"""
O57 十二期 74: Kähler 參數搜索 — 最大化有限質量數
====================================================
scripts/73 發現: φ^(35-i) 只有 5 個有限質量 (其餘 112 個 V 超大)

問題: 有冇 Kähler 參數 t 令更多 curve volumes 細?
  → 9 個有限質量先夠 SM 9 費米子

搜索策略:
  1. φ^(i-1) (反向)
  2. 線性: t_i = i
  3. 混合: t_i = φ^(35-i) × 尺度
  4. 隨機 (對數均勻)
  5. 分析: 點解 φ^(35-i) 得 5 個?
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 十二期 74: Kähler 參數搜索")
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
n_curve = len(cy.curve_basis())
print(f"  basis: {len(basis)}, curves: {n_curve}")

def count_finite(t36, thresh=1e-30):
    t32 = np.array([t36[b-1] for b in basis])
    cv = np.array(cy.compute_curve_volumes(t32))
    pos = cv[cv > 1e-10]
    if len(pos) == 0:
        return 0, []
    masses = np.exp(-pos)
    n_fin = np.sum(masses > thresh)
    return n_fin, pos

# ============ 2. 多種參數 ============
print("\n[2] 參數掃描")
candidates = {
    "φ^(35-i)": phi ** (35 - np.arange(36)),
    "φ^(i-1)": phi ** np.arange(36),
    "線性 1..36": np.arange(1, 37),
    "線性 36..1": np.arange(36, 0, -1),
    "φ^(-i)": phi ** (-np.arange(36)),
    "φ^(-(35-i))": phi ** (-(35 - np.arange(36))),
    "常數 1": np.ones(36),
    "γ_n": 4*np.sin(np.pi*np.arange(1, 37)/88)**2,
    "γ_n×10": 10*4*np.sin(np.pi*np.arange(1, 37)/88)**2,
    "φ^5·(35-i)": phi**5 * (35 - np.arange(36)),
    "2^i": 2.0 ** np.arange(36),
    "2^(-i)": 2.0 ** (-np.arange(36)),
}

results = []
for name, t36 in candidates.items():
    try:
        n_fin, pos = count_finite(t36)
        ratio = pos.max()/pos.min() if len(pos) > 1 else 0
        results.append((n_fin, name, ratio, len(pos)))
        print(f"  {name:15s}: finite={n_fin}, pos={len(pos)}, range={ratio:.1e}")
    except Exception as e:
        print(f"  {name:15s}: ⚠️ {e}")

# ============ 3. 最佳 ============
print("\n[3] 最佳候選")
results.sort(reverse=True)
for n_fin, name, ratio, npos in results[:5]:
    print(f"  {name}: {n_fin} finite (range {ratio:.1e})")

best = results[0]
check("有候選 ≥9 finite", best[0] >= 9, f"({best[1]}: {best[0]})")

# ============ 4. 分析 φ^(35-i) ============
print("\n[4] 點解 φ^(35-i) 得 5 個?")
# φ^(35-i): t_0 = φ^35 (超大), t_35 = 1 (細)
# curve volume = Σ κ_ijk t_j t_k ~ t_max² ~ φ^70 ~ 1e15
# e^-V ~ e^-1e15 = 0
# 只有 t 好細嘅 curve 先有細 volume
# φ^(35-i) 由 t_35=1 開始, 所以只有 5 條 curve 用細 t
print(f"  φ^(35-i): t_0 = φ^35 = {phi**35:.2e}, t_35 = 1")
print(f"  → 大部分 curve volume ~ φ^70 ~ 1e15 → e^-V = 0")
print(f"  → 只有用細 t (尾部) 嘅 curve 有細 volume")

# 如果要 9 個: 需要 t 分佈令至少 9 條 curve 細
print(f"\n  策略: 均勻細 t?")
t_uniform = np.ones(36) * 5
n_fin, pos = count_finite(t_uniform)
print(f"  t=5 均勻: finite={n_fin}, pos={len(pos)}")

t_uniform2 = np.ones(36) * 2
n_fin2, pos2 = count_finite(t_uniform2)
print(f"  t=2 均勻: finite={n_fin2}, pos={len(pos2)}")

# ============ 5. 總結 ============
print("\n" + "=" * 72)
print("十二期 74 總結:")
print("=" * 72)
print(f"""
  Kähler 參數搜索:
  ─────────────────────────────────
  1. φ^(35-i): 5 finite
  2. 最佳候選: {best[1]} ({best[0]} finite)
  3. φ^(35-i) 分析: t_0=φ^35 太大 → 大部分 curve e^-V=0

  {'✅ 揾到 ≥9 finite 候選!' if best[0] >= 9 else '❌ 未有 ≥9, 需更多搜索'}
""")

results_out = {
    "test": "O57 十二期 74: Kähler 搜索",
    "best": best[1] if best else None,
    "best_finite": best[0] if best else 0,
    "scan": [{"name": str(n), "finite": int(f), "pos": int(p)} for f, n, r, p in results],
    "passed": passed, "failed": failed
}
with open("data/74_kahler_search.json", "w") as f:
    json.dump(results_out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 十二期 74 完成!")
