#!/usr/bin/env python3
"""
O57 五期 40: 歸一化 φ 冪次 → e^-V4 質量譜（修正版）
=====================================================
五期 39: φ^(35-i) V4 range 5e7 但 V4 值太大 (1.9e8~9e15) → e^-V4 ≈ 0

物理: Kähler moduli t 有自由尺度 (Kähler cone 係錐!)
      t → c·t 保持 cone 性質, V4 → c²·V4

策略:
  1. 歸一化: 揀 c 令 V4_max ≈ 20 (最大質量 e^-20 ≈ 2e-9)
  2. 然後 V4_min = V4_max/range → e^-V4 質量譜
  3. 睇下有幾多個粒子有合理質量
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 五期 40: 歸一化 φ 質量譜")
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
print("\n[1] 重建正確 κ")
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
print(f"  κ nnz={np.count_nonzero(K)}")

def vol4(t):
    return 0.5 * np.einsum('ijk,j,k->i', K, t, t)

# ============ 2. 歸一化質量譜 ============
print("\n[2] 歸一化 φ 冪次質量譜")
def norm_spectrum(t, label):
    v4 = vol4(t)
    pos_mask = v4 > 1e-10
    pos = v4[pos_mask]
    print(f"\n  --- {label} ---")
    print(f"  V4 positive: {len(pos)}/36, range={pos.max()/pos.min():.2e}")
    # 歸一化: 令最小 V4 = 1 (最重粒子 e^-1 ≈ 0.37)
    c = 1.0 / math.sqrt(pos.min())
    v4n = vol4(c * t)
    posn = v4n[pos_mask]
    masses = np.exp(-posn)
    ms = np.sort(masses)[::-1]
    print(f"  歸一化 c = {c:.4f}")
    print(f"  歸一化 V4: min={posn.min():.4f}, max={posn.max():.4f}")
    print(f"  e^-V4 質量 (top 25):")
    for i, m in enumerate(ms[:25]):
        print(f"    m{i+1:2d}: {m:.4e}")
    n_finite = np.sum(ms > 1e-30)
    print(f"  Finite: {n_finite}")
    # 質量比
    if n_finite >= 2:
        print(f"  質量比 max/min = {ms[ms>1e-30].max()/ms[ms>1e-30].min():.2e}")
    return ms

ms1 = norm_spectrum(phi ** np.arange(36), "φ^(i-1)")
ms2 = norm_spectrum(phi ** (35 - np.arange(36)), "φ^(35-i)")

# ============ 3. 世代結構 ============
print("\n[3] 世代結構 (φ^(35-i) 歸一化)")
t = phi ** (35 - np.arange(36))
v4 = vol4(t)
pos_mask = v4 > 1e-10
c = 1.0 / math.sqrt(v4[pos_mask].min())
v4n = vol4(c * t)
for g in range(3):
    sub = v4n[g*12:(g+1)*12]
    spos = sub[sub > 0]
    print(f"  Gen{g+1}: {len(spos)} 個 positive, V4={np.sort(spos) if len(spos)>0 else 'none'}")

# ============ 4. SM 對比 ============
print("\n[4] SM 對比")
sm = [0.001, 0.511, 2.16, 4.67, 93.4, 105.66, 1270, 1776.86, 4180, 80377, 91187.6, 125250, 172760]
sm_sorted = np.sort(sm)
print(f"  SM 質量比: {sm_sorted[-1]/sm_sorted[0]:.1e}")
if len(ms2[ms2 > 1e-30]) >= 2:
    mf = ms2[ms2 > 1e-30]
    print(f"  模型質量比: {mf.max()/mf.min():.2e}")

# ============ 5. 總結 ============
print("\n" + "=" * 72)
print("五期 40 總結:")
print("=" * 72)
print(f"""
  歸一化 φ 質量譜:
  ─────────────────────────────────
  1. φ^(i-1): {np.sum(ms1 > 1e-30)} 個有限質量
  2. φ^(35-i): {np.sum(ms2 > 1e-30)} 個有限質量
  3. 世代結構: 睇上面
  4. SM 需要 13 粒子, 質量比 1.7e8

  {'✅ φ 冪次 (正確 κ) 有 SM 質量潛力!' if np.sum(ms2 > 1e-30) >= 5 else '❌ 有限質量太少'}
""")

results = {
    "test": "O57 五期 40: 歸一化 φ 質量譜",
    "phi_asc_finite": int(np.sum(ms1 > 1e-30)),
    "phi_desc_finite": int(np.sum(ms2 > 1e-30)),
    "passed": passed, "failed": failed
}
with open("data/40_norm_phi_mass.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 五期 40 完成!")
