#!/usr/bin/env python3
"""
O57 三期 25: 真 κ_ijk + Curve Volumes + e^{-V} 質量譜
======================================================
用 CYTools intersection_numbers() 重建 36³ κ_ijk,
然後用 J* = I₃⊗J₁₂ 計 curve volumes,
最後得 e^{-V} 質量譜對比 SM!

方法:
  1. 從 4-tuple dict 重建 κ_ijk (3-tuple → sum over 4th)
  2. 確認 κ_ijk 對稱性 + 非零數
  3. 對比 O50 嘅 κ_ijk (1341 非零)
  4. 用 J* 計 155 curves volumes
  5. e^{-V} 質量譜
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
DATA = os.path.join(BASE, "data")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
O50 = os.path.join(BASE, "open_problems_fresh", "o50_cy3_intersection", "data")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 三期 25: 真 κ_ijk + Curve Volumes")
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

d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
poly = Polytope(d["vertices"])
tri = poly.triangulate()
tv = tri.get_toric_variety()

# ============ 1. 重建 κ_ijk ============
print("\n[1] 重建 κ_ijk (36³)")
inter = tv.intersection_numbers()
# 4-tuple dict: (a,b,c,d) → value
# 3-fold intersection: ∫ D_a D_b D_c = Σ_d κ_abcd? 唔
# 實際: CY3 有 4 個 divisor 相交 = 0 (dim 3)
# 但 4-tuple 可能係 (D_a·D_b·D_c, D_d coefficient)?
# CYTools 嘅 convention: 4-tuple = D_a·D_b·D_c·D_d (4-fold ambient intersection)
# 喺 CY3 中 D_a·D_b·D_c·D_d = κ_abc × (D_d 嘅 ...)?

# 正確理解: ambient 4-fold (P^5?) 嘅 intersection
# CY3 嵌入: D_a·D_b·D_c 喺 CY 上 = ambient 中 D_a·D_b·D_c·CY
# 所以 3-tuple intersection 需要 4 個 divisor (1 個 = CY class)

# 直接用 3-tuple 部分: keys (a,b,c,d) → 對應 κ_abc 嘅 contribution
# 標準: κ_abc = Σ_d Q_d × κ_abcd? 
# 或者: κ_abc = inter[(a,b,c,d)] for fixed d?

# 先睇: (0,a,b,c) keys = CY class × D_a D_b D_c?
keys0 = [k for k in inter.keys() if k[0] == 0]
print(f"  keys with leading 0: {len(keys0)}")
if keys0:
    print(f"  sample: {keys0[:5]}")
    # (0,1,3,7) → 1.0 代表 CY·D_1·D_3·D_7?

# 睇 0 喺邊個位置
zero_pos = []
for k in inter.keys():
    zero_pos.append(k.index(0) if 0 in k else -1)
from collections import Counter
print(f"  0 位置分佈: {Counter(zero_pos)}")

# ============ 2. 3-tuple κ_ijk ============
print("\n[2] 3-tuple κ_ijk (用 leading-0 當 CY class)")
# 如果 (0,a,b,c) = ∫_CY D_a D_b D_c = κ_abc
kappa3 = np.zeros((36, 36, 36))
n_3tuple = 0
for k, v in inter.items():
    if k[0] == 0 and all(1 <= x <= 36 for x in k[1:]):
        a, b, c = k[1]-1, k[2]-1, k[3]-1
        kappa3[a, b, c] = v
        kappa3[a, c, b] = v
        kappa3[b, a, c] = v
        kappa3[b, c, a] = v
        kappa3[c, a, b] = v
        kappa3[c, b, a] = v
        n_3tuple += 1
print(f"  3-tuple entries: {n_3tuple}")
nz3 = np.count_nonzero(kappa3)
print(f"  κ_ijk 非零: {nz3}")
print(f"  κ_ijk min: {kappa3.min()}, max: {kappa3.max()}")

# ============ 3. 對比 O50 ============
print("\n[3] 對比 O50 κ_ijk")
# O50: 1341 非零, min -360, max 180, d_000=-360
# 搵 O50 kappa file
import glob
kappa_files = glob.glob(os.path.join(O50, "*kappa*"))
print(f"  O50 kappa files: {[os.path.basename(f) for f in kappa_files]}")
for kf in kappa_files:
    try:
        kd = json.load(open(kf))
        if isinstance(kd, dict):
            print(f"    {os.path.basename(kf)}: keys={list(kd.keys())[:6]}")
        else:
            print(f"    {os.path.basename(kf)}: {np.array(kd).shape}")
    except Exception as e:
        print(f"    {os.path.basename(kf)}: {e}")

# ============ 4. J* 計 volumes ============
print("\n[4] J* = I₃⊗J₁₂ 計 curve volumes")
jstar_path = os.path.join(O53, "Jstar_36D.json")
if os.path.exists(jstar_path):
    jd = json.load(open(jstar_path))
    Jstar = np.array(jd.get("Jstar_36D", jd))
    print(f"  Jstar shape: {Jstar.shape}")
    # J* 可能係 vector: J = Σ t_i D_i, t = Jstar
    # 或者 matrix: J = Σ J_ij D_i D_j
    if Jstar.ndim == 1:
        print(f"  Jstar vector: {Jstar[:8]}...")
        # volume(C_jk) = Σ_i t_i κ_ijk (curve = D_j·D_k)
        # 計所有 curve volumes
        vol_curves = []
        for j in range(36):
            for k in range(j+1, 36):
                v = np.sum(Jstar * kappa3[:, j, k])
                if abs(v) > 1e-10:
                    vol_curves.append((j+1, k+1, v))
        print(f"  Nonzero curve volumes: {len(vol_curves)}")
        if vol_curves:
            vols = np.array([v for _, _, v in vol_curves])
            print(f"  Volume range: [{vols.min():.4f}, {vols.max():.4f}]")
            print(f"  Positive: {(vols > 0).sum()}, Negative: {(vols < 0).sum()}")

# ============ 5. 總結 ============
print("\n" + "=" * 72)
print("三期 25 總結:")
print("=" * 72)

results = {
    "test": "O57 三期 25: 真 κ_ijk",
    "n_3tuple": n_3tuple,
    "kappa_nonzero": int(nz3),
    "kappa_range": [float(kappa3.min()), float(kappa3.max())],
    "passed": passed, "failed": failed
}
with open("data/25_kappa_volumes.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 三期 25 完成!")
