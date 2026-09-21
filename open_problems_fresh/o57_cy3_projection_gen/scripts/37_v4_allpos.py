#!/usr/bin/env python3
"""
O57 五期 37: V4 全正點搜索 — 二次型 Kähler cone
=================================================
CYTools interior point 只保證線性正 (curve volumes),
但 V4 (4-cycle, 二次型) 有 15/36 負 → 真正 Kähler cone 更細!

策略:
  1. Interior point 附近大量隨機擾動, 篩 V4 全正
  2. 一旦搵到全正點 → 計動態範圍
  3. 用梯度方向搜尋: 增大最大 V4 / 減細最小 V4
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")

print("=" * 72)
print("O57 五期 37: V4 全正點搜索")
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

kappa = np.array(json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))["kappa"])
def vol4(t):
    return 0.5 * np.einsum('ijk,j,k->i', kappa, t, t)

d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
poly = Polytope(d["vertices"])
tri = poly.triangulate()
tv = tri.get_toric_variety()
kc = tv.kahler_cone()
ip32 = np.array(kc.find_interior_point(), dtype=float)
basis = tv.divisor_basis()
basis0 = [b - 1 for b in basis]
missing = [i for i in range(36) if i not in basis0]

def to36(t32):
    """32-dim → 36-dim (missing 用最近插值)"""
    t = np.zeros(36)
    t[basis0] = t32
    for m in missing:
        nearest = basis0[np.argmin([abs(b - m) for b in basis0])]
        t[m] = t32[basis0.index(nearest)]
    return t

# ============ 1. Interior 附近擾動 ============
print("\n[1] Interior 附近擾動 (V4 全正篩選)")
rng = np.random.default_rng(11)
found = []
for trial in range(300000):
    # 相對擾動 (log-space)
    noise = np.exp(rng.normal(0, 0.15, 32))
    t32 = ip32 * noise
    t36 = to36(t32)
    v4 = vol4(t36)
    if np.all(v4 > 0):
        pos = v4[v4 > 0]
        r = pos.max() / pos.min()
        found.append((r, t36.copy()))
        if len(found) >= 20:
            break
print(f"  搵到全正點: {len(found)}/300000")
if found:
    found.sort(key=lambda x: -x[0])
    best_r, best_t = found[0]
    print(f"  最佳 V4 range: {best_r:.2e}")
    v4b = vol4(best_t)
    print(f"  V4 sorted: {np.sort(v4b)}")
    print(f"  e^-V4 range: {np.exp(-v4b.min())/np.exp(-v4b.max()):.2e}")
    check("搵到全正 V4 點", len(found) > 0)
else:
    print("  300000 次都冇全正點!")
    check("搵到全正 V4 點", False)

# ============ 2. 大尺度變換 ============
print("\n[2] 大尺度掃描 (c·t)")
if found:
    for c in [0.01, 0.1, 0.3, 1, 3, 10]:
        t = c * best_t
        v4 = vol4(t)
        if np.all(v4 > 0):
            pos = v4[v4 > 0]
            r = pos.max()/pos.min()
            mr = np.exp(-pos.min())/np.exp(-pos.max())
            print(f"  c={c}: V4 range={r:.2e}, e^-V4 range={mr:.2e}")

# ============ 3. 世代分層 ============
print("\n[3] 世代分層 (best 點)")
if found:
    v4b = vol4(best_t)
    for g in range(3):
        sub = v4b[g*12:(g+1)*12]
        print(f"  Gen{g+1}: min={sub.min():.4f}, max={sub.max():.4f}, "
              f"pos={np.sum(sub>0)}")

# ============ 4. 總結 ============
print("\n" + "=" * 72)
print("五期 37 總結:")
print("=" * 72)
if found:
    print(f"""
  V4 全正點搜索:
  ─────────────────────────────────
  1. Interior 附近 300000 次擾動 → 搵到 {len(found)} 個全正點
  2. 最佳 V4 range: {best_r:.2e}
  3. e^-V4 range: {np.exp(-vol4(best_t).min())/np.exp(-vol4(best_t).max()):.2e}
  4. 尺度掃描: 睇上面

  {'✅ 有全正 V4 點, 動態範圍 ' + (f'{best_r:.1e}' if best_r > 1e4 else '細')}
  {'✅ 可達 10^8!' if best_r > 1e8 else '⚠️ 未達 10^8'}
""")
else:
    print(f"""
  ❌ 300000 次擾動都冇全正 V4 點
  → 二次型 Kähler cone (V4>0) 極度細, 幾乎測度零?
  → 或者 κ 本身有問題 (O53 數據同 CYTools 唔一致?)
""")

results = {
    "test": "O57 五期 37: V4 全正搜索",
    "n_found": len(found),
    "best_range": float(found[0][0]) if found else None,
    "passed": passed, "failed": failed
}
with open("data/37_v4_allpos.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:  # 探索性: fail 係誠實結論
    print("  ⚠️ 探索性 fail (誠實結論)")
else:
    pass
print("🎉 五期 37 完成!")
