#!/usr/bin/env python3
"""
O70 — 22: Rebuild Q matrix + Exact Extreme Rays via Sage PPL
=============================================================
原任務 (O57 #7, 2026-08-31 留低 🟡): 36-dim Kähler cone 精確 extreme rays。

舊 session 用 float LP 攞到 99 boundary rays 但冇 exact/精確驗證。
今次: 
  1. CYTools 重建 Q 矩陣 (185×32, 1e-5 有限差分 — 同舊 scripts 一致)
  2. Sage PPL Polyhedron 精確計算 extreme rays
  3. 驗證: 99 float rays 同 exact extreme rays 一致?
"""
import sys, os, math, json, numpy as np

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
os.makedirs(DATA, exist_ok=True)
phi = (1 + math.sqrt(5)) / 2

sys.path.insert(0, "/home/wsl/Projects/IDCM-Original/tools/cytools")
from cytools.config import enable_experimental_features
enable_experimental_features()
from cytools import Polytope

print("=" * 72)
print("O70 22: Q 矩陣重建 + Sage PPL 精確 Extreme Rays")
print("=" * 72)

# 1. Load polytope & CY
d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
pts = np.array(d["points"])
print(f"points: {pts.shape}")
p = Polytope(pts)
tri = p.triangulate()
cy = tri.get_cy()
basis = cy.divisor_basis()
print(f"divisor basis: {len(basis)}")  # 32

# 2. Rebuild Q (185×32) — 同舊 scripts 15 完全一致
t_test = phi ** (-np.arange(36))
t32 = np.array([t_test[b - 1] for b in basis])
eps = 1e-5
Q = np.zeros((185, 32))
for j in range(32):
    tp = t32.copy(); tm = t32.copy()
    tp[j] += eps; tm[j] -= eps
    cvp = np.array(cy.compute_curve_volumes(tp))
    cvm = np.array(cy.compute_curve_volumes(tm))
    Q[:, j] = (cvp - cvm) / (2 * eps)
Qn = Q / (np.linalg.norm(Q, axis=1, keepdims=True) + 1e-15)
np.save(os.path.join(DATA, "22_Q_matrix_185x32.npy"), Q)
np.save(os.path.join(DATA, "22_Qn_matrix_185x32.npy"), Qn)
print(f"Q: {Q.shape}, rank: {np.linalg.matrix_rank(Q)}")
print(f"Q 值範圍: [{Q.min():.4e}, {Q.max():.4e}]")

# 3. 將 Q 轉成 rational 近似 (PPL 要 exact) — 用 high precision
# 用 float 嘅 16 位有效數字 -> Fraction
from fractions import Fraction
def to_fraction(x, max_den=10**9):
    return Fraction(x).limit_denominator(max_den)

# Qn 每一行 normalize 過, 用 Fraction 準確表示
print("\n─── 3. Sage Polyhedron (PPL backend) ───")
from sage.all import Polyhedron, QQ
# Cone: {t : Qn @ t >= 0} → 等價於 homogenous polyhedron
# Sage Polyhedron(ieqs=[(0, *row) for row in Qn]) 表示 {x: row·x >= 0}
ieqs = []
for i in range(Qn.shape[0]):
    row = Qn[i]
    # 直接用 float 會 lose precision — 改用 rational approximation
    frac_row = [to_fraction(x) for x in row]
    ieqs.append(tuple([0] + frac_row))

print(f"ieqs: {len(ieqs)} 條不等式, 32 維")
# 保留 2 個 redundant? Polyhedron 會自動處理 redundant
P = Polyhedron(ieqs=ieqs, backend='ppl')
print(f"Polyhedron dim: {P.dim()}")
print(f"is_compact: {P.is_compact()} (False = cone)")

# 4. Extreme rays (exact)
rays = P.rays()
print(f"\n─── 4. Exact Extreme Rays ───")
print(f"數目: {len(rays)}")
ray_list = []
for r in rays:
    v = np.array([float(x) for x in r.vector().list()])
    n = np.linalg.norm(v)
    if n > 0:
        ray_list.append(v / n)
R_exact = np.array(ray_list)
print(f"exact rays (normalized): {R_exact.shape}")
np.save(os.path.join(DATA, "22_exact_extreme_rays.npy"), R_exact)

# 5. 同舊 99 float rays 比較
R99 = np.load(os.path.join(DATA, "15_all_rays.npy"))
print(f"\n─── 5. 對比舊 99 float rays ───")
print(f"舊: {R99.shape}, 新 exact: {R_exact.shape}")
# 每條 exact ray 搵最近嘅舊 ray
from scipy.spatial.distance import cdist
D = cdist(R_exact, R99, metric='cosine')
# cosine distance 0 = 同向
min_d = D.min(axis=1)
match = min_d < 1e-4
print(f"exact rays 喺舊 99 rays 入面搵到 match: {match.sum()}/{len(R_exact)}")
print(f"unmatched 嘅 (若存在): {np.where(~match)[0]}")
if len(R_exact) > 0 and match.sum() == len(R_exact):
    print("\n✅ 結論: 舊 99 rays = 完整 exact extreme rays 集合")
elif len(R_exact) != 99:
    print(f"\n⚠️ exact 數目 {len(R_exact)} ≠ 99 → 舊集合唔 complete!")
    # 邊啲舊 rays 唔喺 exact 入面?
    D2 = cdist(R99, R_exact, metric='cosine')
    old_unmatched = D2.min(axis=1) > 1e-4
    print(f"舊 99 入面冇 exact match 嘅: {old_unmatched.sum()} 條 → {np.where(old_unmatched)[0]}")

print("\nDone.")
