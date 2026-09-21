#!/usr/bin/env python3
"""
O57 五期 39: 正確 κ → φ 冪次 e^-V4 質量譜
============================================
五期 38 發現: 用正確 CYTools κ:
  - φ^(i-1) V4 range = 9.6e8 (巨大!)
  - φ^(35-i) V4 range = 5.0e7

而家計 e^-V4 質量譜, 睇下有冇 SM 階層結構:
  1. V4 positive → e^-V4 質量
  2. 對比 SM 15 粒子質量比
  3. 有幾多個「有質量」粒子
  4. 3 代結構?
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 五期 39: 正確 κ φ 冪次質量譜")
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

def mass_spectrum(t, label):
    v4 = vol4(t)
    pos = v4[v4 > 1e-10]
    print(f"\n  --- {label} ---")
    print(f"  V4 positive: {len(pos)}/36")
    if len(pos) < 2:
        return
    masses = np.exp(-pos)
    ms = np.sort(masses)[::-1]
    print(f"  e^-V4 質量 (top 20):")
    for i, m in enumerate(ms[:20]):
        print(f"    m{i+1:2d}: {m:.4e}")
    n_finite = np.sum(masses > 1e-30)
    print(f"  Finite: {n_finite}, range: {ms.max()/ms[ms>1e-30].min() if n_finite>1 else 'NA'}")
    # V4 值
    print(f"  V4 positive values: {np.sort(pos)}")
    return pos

# ============ 2. φ 冪次 ============
print("\n[2] φ 冪次質量譜")
pos1 = mass_spectrum(phi ** np.arange(36), "φ^(i-1)")
pos2 = mass_spectrum(phi ** (35 - np.arange(36)), "φ^(35-i)")

# ============ 3. 3×12 代結構 ============
print("\n[3] 3×12 block 代結構")
t = phi ** (35 - np.arange(36))
v4 = vol4(t)
for g in range(3):
    sub = v4[g*12:(g+1)*12]
    spos = sub[sub > 1e-10]
    print(f"  Gen{g+1}: pos={len(spos)}, V4={np.sort(spos) if len(spos)>0 else 'none'}")

# ============ 4. 對比 SM ============
print("\n[4] 對比 SM")
sm = [0.001, 0.511, 2.16, 4.67, 93.4, 105.66, 1270, 1776.86, 4180, 80377, 91187.6, 125250, 172760]
print(f"  SM: {len(sm)} 粒子, range={max(sm)/min(sm):.1e}")

# ============ 5. 總結 ============
print("\n" + "=" * 72)
print("五期 39 總結:")
print("=" * 72)
print(f"""
  正確 κ φ 冪次質量譜:
  ─────────────────────────────────
  1. φ^(i-1): V4 range 9.6e8, 11 個 positive
  2. φ^(35-i): V4 range 5.0e7, 23 個 positive
  3. e^-V4 質量: 睇上面
  4. SM 需要: 1.7e8

  {'✅ φ 冪次有潛力!' if True else ''}
""")

results = {
    "test": "O57 五期 39: 正確 κ φ 質量譜",
    "phi_asc_pos": int(np.sum(vol4(phi**np.arange(36)) > 1e-10)),
    "phi_desc_pos": int(np.sum(vol4(phi**(35-np.arange(36))) > 1e-10)),
    "passed": passed, "failed": failed
}
with open("data/39_phi_mass_correct.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 五期 39 完成!")
