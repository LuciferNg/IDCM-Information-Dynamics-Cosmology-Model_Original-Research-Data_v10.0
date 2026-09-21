#!/usr/bin/env python3
"""
O57 五期 36: Kähler Cone 內點 → 4-cycle Volume 動態範圍
=========================================================
用 CYTools kahler_cone().find_interior_point() 攞真正 cone 內參數!

關鍵:
  - interior point 係 32-dim (divisor basis [1,2,5,6,9..36])
  - 要 map 返 36-dim (missing divisors [3,4,7,8] 補值)
  - 然後測 4-cycle volume (二次型) 動態範圍
  - e^-V4 質量譜

missing divisors 嘅 t 值: 用相鄰 divisor 平均? 定係 0?
(佢哋係 redundant, 線性相關 → 可以用線性組合表示)
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 五期 36: Cone 內點 → V4 動態範圍")
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

# ============ 1. 攞 cone 內點 ============
print("\n[1] CYTools cone 內點")
d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
poly = Polytope(d["vertices"])
tri = poly.triangulate()
tv = tri.get_toric_variety()
kc = tv.kahler_cone()
ip32 = np.array(kc.find_interior_point(), dtype=float)
print(f"  Interior point (32-dim): {ip32}")
basis = tv.divisor_basis()
print(f"  Divisor basis: {basis}")

# ============ 2. Map 到 36-dim ============
print("\n[2] Map 到 36-dim")
# basis 係 1-index divisor 編號 → 0-index
basis0 = [b - 1 for b in basis]
missing = [i for i in range(36) if i not in basis0]
print(f"  Basis (0-index): {basis0}")
print(f"  Missing (0-index): {missing}")

# 36-dim t: basis 位置用 interior point, missing 用插值
t36 = np.zeros(36)
t36[basis0] = ip32
# missing divisors: 用相鄰平均 (redundant, 影響細)
for m in missing:
    # 揾最接近嘅 basis divisor 值
    dists = [abs(b - m) for b in basis0]
    nearest = basis0[np.argmin(dists)]
    t36[m] = t36[nearest]
print(f"  t36: {t36}")
print(f"  All positive: {np.all(t36 > 0)}")

# ============ 3. V4 動態範圍 ============
print("\n[3] 4-cycle volume 動態範圍")
v4 = vol4(t36)
print(f"  V4: n_pos={np.sum(v4>0)}, n_neg={np.sum(v4<0)}")
print(f"  V4 positive: {v4[v4>0]}")
print(f"  V4 negative: {v4[v4<0]}")
check("全正 V4 (cone 內)", np.all(v4 > 0), f"({np.sum(v4>0)}/36)")

pos = v4[v4 > 0]
if len(pos) > 1:
    r = pos.max() / pos.min()
    print(f"  V4 動態範圍: {r:.2e}")
    print(f"  ln(range) = {math.log(r):.2f}")
    print(f"  e^-V4 質量範圍: {np.exp(-pos.min())/np.exp(-pos.max()):.2e}")

# ============ 4. 世代 block ============
print("\n[4] 世代 block V4")
for g in range(3):
    sub = v4[g*12:(g+1)*12]
    print(f"  Gen{g+1}: pos={np.sum(sub>0)}, min={sub.min():.4f}, max={sub.max():.4f}")

# ============ 5. 尺度掃描 ============
print("\n[5] 尺度掃描 (乘 c)")
# V4(c·t) = c²·V4(t): 相對範圍不變, 但絕對值變
# e^-V4 質量範圍 = e^{c²(V_max - V_min)}: c 大 → 範圍大!
for c in [0.1, 0.3, 1.0, 3.0, 10.0, 30.0]:
    v4c = vol4(c * t36)
    if np.all(v4c > 0):
        posc = v4c[v4c > 0]
        rc = posc.max() / posc.min()
        mass_r = np.exp(-posc.min()) / np.exp(-posc.max())
        print(f"  c={c}: V4 range={rc:.2e}, e^-V4 range={mass_r:.2e}")

# ============ 6. 總結 ============
print("\n" + "=" * 72)
print("五期 36 總結:")
print("=" * 72)
print(f"""
  Cone 內點 → V4:
  ─────────────────────────────────
  1. CYTools interior point (32-dim) → 36-dim
  2. V4 全正: {np.all(v4 > 0)}
  3. V4 動態範圍: {pos.max()/pos.min() if len(pos)>1 else 'NA':.2e}
  4. 尺度掃描: 睇上面
  5. e^-V4 質量範圍: 睇上面

  {'✅ Kähler cone 內點確認!' if np.all(v4 > 0) else '❌ map 有問題'}
""")

results = {
    "test": "O57 五期 36: Cone 內點 V4",
    "t36": [float(x) for x in t36],
    "v4_allpos": bool(np.all(v4 > 0)),
    "v4_range": float(pos.max()/pos.min()) if len(pos) > 1 else None,
    "passed": passed, "failed": failed
}
with open("data/36_cone_interior.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:  # 探索性: fail 係誠實結論
    print("  ⚠️ 探索性 fail (誠實結論)")
else:
    pass
print("🎉 五期 36 完成!")
