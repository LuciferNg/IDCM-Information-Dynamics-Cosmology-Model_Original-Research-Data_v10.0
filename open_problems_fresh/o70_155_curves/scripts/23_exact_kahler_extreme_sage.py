#!/usr/bin/env python3
"""
O70 — 23: Exact Extreme Rays via Mori Cone Duality (Sage PPL)
=============================================================
原任務 (O57 #7, 🟡): 36-dim Kähler cone 精確 extreme rays。

方法:
  1. CYTools toric_mori_cone(in_basis=True) → 185 exact integer rays (32D)
     = Kähler cone 嘅定義不等式 normals
  2. Sage Polyhedron(rays=...) PPL backend → Mori cone (exact)
  3. Kähler cone = Mori cone 嘅 dual cone
     → Kähler extreme rays = 解 dual (Sage .dual() / polar)
  4. 同舊 99 float boundary rays 交叉驗證
"""
import sys, os, math, json, numpy as np

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

sys.path.insert(0, "/home/wsl/Projects/IDCM-Original/tools/cytools")
from cytools.config import enable_experimental_features
enable_experimental_features()
from cytools import Polytope

print("=" * 72)
print("O70 23: Exact Kähler Cone Extreme Rays — Mori Duality")
print("=" * 72)

# 1. Load CY
d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
pts = np.array(d["points"])
p = Polytope(pts)
tri = p.triangulate()
cy = tri.get_cy()

# 2. Mori cone exact rays (32D)
mc = cy.toric_mori_cone(in_basis=True)
rays = np.array(mc.rays(), dtype=int)
print(f"Mori cone rays (exact int): {rays.shape}, rank {np.linalg.matrix_rank(rays)}")

# 3. Sage Polyhedron from rays (PPL backend — exact)
from sage.all import Polyhedron, QQ, vector
# Polyhedron(rays=[...]) 喺 QQ 空間
ray_qq = [tuple(int(x) for x in r) for r in rays]
M = Polyhedron(rays=ray_qq, backend='ppl')
print(f"Mori cone polyhedron dim: {M.dim()}")

# 4. Dual cone (Kähler cone)
# Sage: P.dual() 對 polyhedral cone 計 polar/dual
try:
    K = M.dual()
    print(f"Kähler cone (dual): dim {K.dim()}")
    krays = K.rays()
    print(f"Kähler extreme rays 數目: {len(krays)}")
    # Save exact
    kray_list = []
    for r in krays:
        v = np.array([float(x) for x in r.vector().list()])
        kray_list.append(v)
    Rk = np.array(kray_list)
    # Normalize rows
    Rn = Rk / np.linalg.norm(Rk, axis=1, keepdims=True)
    np.save(os.path.join(DATA, "23_kahler_exact_extreme_rays.npy"), Rn)
    print(f"Saved exact Kähler extreme rays: {Rn.shape}")
except Exception as e:
    print(f"dual() failed: {e}")
    # fallback: 直接用 ieqs
    print("Fallback: Polyhedron(ieqs=rays)...")
    ieq_qq = [tuple([0] + [int(x) for x in r]) for r in rays]
    K = Polyhedron(ieqs=ieq_qq, backend='ppl')
    print(f"K dim: {K.dim()}")
    krays = K.rays()
    print(f"K extreme rays 數目: {len(krays)}")
    Rk = np.array([[float(x) for x in r.vector().list()] for r in krays])
    Rn = Rk / np.linalg.norm(Rk, axis=1, keepdims=True)
    np.save(os.path.join(DATA, "23_kahler_exact_extreme_rays.npy"), Rn)
    print(f"Saved: {Rn.shape}")

# 5. 對比舊 99 float rays
R99 = np.load(os.path.join(DATA, "15_all_rays.npy"))
Rn = np.load(os.path.join(DATA, "23_kahler_exact_extreme_rays.npy"))
print(f"\n─── 對比 ───")
print(f"舊 boundary rays: {R99.shape}")
print(f"新 exact extreme: {Rn.shape}")
from scipy.spatial.distance import cdist
# 新 rays 喺舊入面搵 match (cosine)
D = cdist(Rn, R99, metric='cosine')
match = D.min(axis=1) < 1e-4
print(f"新 exact rays 喺舊 99 入面: {match.sum()}/{len(Rn)}")
# 舊 rays 喺新入面搵 match
D2 = cdist(R99, Rn, metric='cosine')
match2 = D2.min(axis=1) < 1e-4
print(f"舊 99 rays 喺新 exact 入面: {match2.sum()}/{len(R99)}")
if len(Rn) == 99 and match.all():
    print("\n✅✅ 完美閉合: 99 float boundary rays = 99 exact extreme rays!")
elif match2.sum() == len(R99) and len(Rn) > 99:
    print(f"\n⚠️ 新 exact 有 {len(Rn)} 條 > 舊 99 — 舊集合唔 complete!")
elif match2.sum() < len(R99):
    print(f"\n❌ 舊 99 有 {len(R99)-match2.sum()} 條唔係 extreme!")
print("\nDone.")
