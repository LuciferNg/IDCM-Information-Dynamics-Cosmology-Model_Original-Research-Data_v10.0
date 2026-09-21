#!/usr/bin/env python3
"""
O57 五期 38: 正確 CYTools κ → V4 動態範圍（修正版）
=====================================================
🔴 重大發現: O53 cy36_98_intersection_full.json 嘅 κ 有問題!
  - CYTools 直接算: K[0,0,0] = 4.0, 1122 非零
  - O53 存檔: K[0,0,0] = -360.0, 1341 非零
  - 兩者差 364! O53 數據可能由 ambient 4-fold 投影, 唔係 CY 3-fold

而家用正確 CYTools κ (361 entries → 36³ dense) 重做:
  1. 重建正確 κ
  2. V4 = ½κ_ijk t_j t_k (4-cycle volume)
  3. 搵 Kähler cone 內點 (V4 全正)
  4. e^-V4 動態範圍
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 五期 38: 正確 CYTools κ")
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

# ============ 1. 重建正確 κ ============
print("\n[1] 重建正確 κ (CYTools)")
d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
pts = np.array(d["points"])
p = Polytope(pts)
tri = p.triangulate()
cy = tri.get_cy()
inter = cy.intersection_numbers()

K = np.zeros((36, 36, 36))
for key, val in inter.items():
    if isinstance(key, tuple) and len(key) == 3:
        i, j, k = key
        if 1 <= i <= 36 and 1 <= j <= 36 and 1 <= k <= 36:
            K[i-1, j-1, k-1] = val
            K[i-1, k-1, j-1] = val
            K[j-1, i-1, k-1] = val
            K[j-1, k-1, i-1] = val
            K[k-1, i-1, j-1] = val
            K[k-1, j-1, i-1] = val

print(f"  κ: {K.shape}, nnz={np.count_nonzero(K)}")
print(f"  K[0,0,0] = {K[0,0,0]}")
check("κ[0,0,0] = 4 (合理)", abs(K[0,0,0] - 4) < 0.01, f"({K[0,0,0]})")

# 對比 O53
K53 = np.array(json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))["kappa"])
print(f"  O53 κ[0,0,0] = {K53[0,0,0]} ← 可疑!")
print(f"  🔴 O53 κ 同 CYTools 不一致: {not np.allclose(K, K53)}")

# ============ 2. V4 二次型 ============
print("\n[2] V4 = ½κ_ijk t_j t_k")
def vol4(t):
    return 0.5 * np.einsum('ijk,j,k->i', K, t, t)

# 用 J* 試
jd = json.load(open(os.path.join(O53, "Jstar_36D.json")))
Jstar = np.array(jd.get("Jstar_36D", jd))
v4_J = vol4(Jstar)
print(f"  J* V4: n_pos={np.sum(v4_J>0)}, n_neg={np.sum(v4_J<0)}/36")
print(f"  J* V4 positive: {np.sort(v4_J[v4_J>0])}")
check("J* V4 全正 (正確 κ)", np.all(v4_J > 0), f"({np.sum(v4_J>0)}/36)")

# ============ 3. φ 冪次 ============
print("\n[3] φ 冪次 V4")
for name, t in [("φ^(i-1)", phi**np.arange(36)), ("φ^(35-i)", phi**(35-np.arange(36)))]:
    v4 = vol4(t)
    print(f"  {name}: n_pos={np.sum(v4>0)}, range={v4[v4>0].max()/v4[v4>0].min() if np.sum(v4>0)>1 else 'NA'}")

# ============ 4. 隨機 cone 搜索 ============
print("\n[4] 隨機 Kähler 參數 (V4 全正)")
rng = np.random.default_rng(5)
found = []
for trial in range(100000):
    t = np.exp(rng.normal(0, 2, 36))
    v4 = vol4(t)
    if np.all(v4 > 0):
        r = v4.max() / v4.min()
        found.append((r, t.copy()))
        if len(found) >= 10:
            break
print(f"  全正 V4: {len(found)}/100000")
if found:
    found.sort(key=lambda x: -x[0])
    r_best, t_best = found[0]
    print(f"  最佳 range: {r_best:.2e}")
    v4b = vol4(t_best)
    print(f"  e^-V4 range: {np.exp(-v4b.min())/np.exp(-v4b.max()):.2e}")
    print(f"  V4 sorted: {np.sort(v4b)}")

# ============ 5. 總結 ============
print("\n" + "=" * 72)
print("五期 38 總結:")
print("=" * 72)
print(f"""
  正確 CYTools κ 分析:
  ─────────────────────────────────
  1. 🔴 O53 κ 數據有問題 (K[0,0,0] = -360 vs CYTools 4)
  2. J* V4 (正確 κ): {np.sum(v4_J>0)}/36 正
  3. φ 冪次: 睇上面
  4. 隨機全正: {len(found)}/100000

  結論: {'✅ J* 用正確 κ 係全正 V4!' if np.all(v4_J > 0) else '❌ 仍然有負'}
""")

results = {
    "test": "O57 五期 38: 正確 κ",
    "K00": float(K[0,0,0]),
    "K53_00": float(K53[0,0,0]),
    "inconsistent": bool(not np.allclose(K, K53)),
    "Jstar_allpos": bool(np.all(v4_J > 0)),
    "n_found": len(found),
    "passed": passed, "failed": failed
}
with open("data/38_correct_kappa.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:  # 探索性: fail 係誠實結論
    print("  ⚠️ 探索性 fail (誠實結論)")
else:
    pass
print("🎉 五期 38 完成!")
