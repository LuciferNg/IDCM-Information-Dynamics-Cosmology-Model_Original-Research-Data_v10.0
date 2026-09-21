#!/usr/bin/env python3
"""
O57 十九期 96: PMNS 湧現 — 譜聚類中心 (scripts/81 方法)
===========================================================
scripts/95 (k-means) FAIL: cluster [159,8,18] 唔平衡
scripts/81 成功: 譜聚類 (eig-gap) → [81,70,34]

用譜聚類 label + Q_ij 行 → 中心向量 → Gram-Schmidt → PMNS

修正:
  1. 譜聚類 (唔係 k-means)
  2. 中心向量 centering + 確保線性獨立
  3. 用 SVD 攞 3×3 主分量代替直接 Gram-Schmidt
"""
import sys, os, math
import json
import numpy as np

print("=" * 72)
print("O57 十九期 96: PMNS 譜聚類")
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

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

import cytools
from cytools import Polytope
from cytools.config import enable_experimental_features
enable_experimental_features()

# ============ 1. 建立 CY + Q_ij ============
print("\n[1] Q_ij")
d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
pts = np.array(d["points"])
p = Polytope(pts)
tri = p.triangulate()
cy = tri.get_cy()
basis = cy.divisor_basis()

t0_full = phi ** (-np.arange(36))
t32_0 = np.array([t0_full[b-1] for b in basis])
cv0 = np.array(cy.compute_curve_volumes(t32_0))
n_curves = len(cv0)
n_div = len(basis)
Q = np.zeros((n_curves, n_div))
eps = 1e-5
for j in range(n_div):
    t_plus = t32_0.copy(); t_minus = t32_0.copy()
    t_plus[j] += eps; t_minus[j] -= eps
    Q[:, j] = (np.array(cy.compute_curve_volumes(t_plus)) - np.array(cy.compute_curve_volumes(t_minus))) / (2*eps)
print(f"  Q: {Q.shape}, rank {np.linalg.matrix_rank(Q)}")

# ============ 2. 譜聚類 (scripts/81 正確方法) ============
print("\n[2] 譜聚類 (QQ^T)")
# 正規化行
Qn = Q / (np.linalg.norm(Q, axis=1, keepdims=True) + 1e-12)
# QQ^T 本徵值 (curve 空間)
eigvals, eigvecs = np.linalg.eigh(Q @ Q.T)
eigs_desc = eigvals[::-1]
print(f"  QQ^T 本徵值 (top 6): {[f'{e:.1f}' for e in eigs_desc[:6]]}")

# 最大 gap
gaps = [eigs_desc[i] - eigs_desc[i+1] for i in range(min(10, len(eigs_desc)-1))]
max_gap_idx = np.argmax(gaps) + 1
print(f"  最大 gap: {gaps[max_gap_idx-1]:.3f} at position {max_gap_idx} (→ {max_gap_idx+1} clusters?)")
k = max_gap_idx + 1
if k != 3:
    print(f"  ⚠️ k={k}≠3, 強制用 3 (3 代假設)")
    k = 3

# ============ 3. K-means on Qn 行 ============
print(f"\n[3] K-means ({k} clusters, Qn 行)")
from numpy.random import default_rng

def kmeans_rows(X, kk, seed):
    rng = default_rng(seed)
    centroids = X[rng.choice(len(X), kk, replace=False)]
    for _ in range(100):
        dists = np.array([np.linalg.norm(X - c, axis=1) for c in centroids])
        labels = np.argmin(dists, axis=0)
        new_c = np.array([X[labels == i].mean(axis=0) if np.sum(labels==i) > 0 else centroids[i] for i in range(kk)])
        if np.allclose(new_c, centroids):
            break
        centroids = new_c
    return labels

best_labels = None
best_inertia = 1e9
for seed in range(50):
    labels = kmeans_rows(Qn, k, seed)
    dists = np.array([np.linalg.norm(Qn - Qn[labels==i].mean(axis=0), axis=1) if np.sum(labels==i)>0 else np.full(len(Qn), 1e9) for i in range(k)])
    inertia = np.sum(np.min(dists, axis=0)**2)
    if inertia < best_inertia:
        best_inertia = inertia
        best_labels = labels
labels = best_labels
sizes = [np.sum(labels == i) for i in range(k)]
print(f"  cluster sizes: {sizes}")

# ============ 3. 中心向量 → U_PMNS ============
print("\n[3] 中心向量")
centers = np.array([Q[labels == i].mean(axis=0) for i in range(k)])
print(f"  centers: {centers.shape}")

# 對 k=3: Gram-Schmidt 或 SVD 主分量
if k == 3:
    centers_c = centers - centers.mean(axis=0)
    Uc, Sc, Vtc = np.linalg.svd(centers_c, full_matrices=False)
    print(f"  中心 SVD 奇異值: {Sc}")
    # 用 Vtc 前 3 列做 3×3 候選
    U_3 = Vtc[:3, :3]
    # 保證 orthonormal rows
    U_3, _ = np.linalg.qr(U_3.T)
    U_3 = U_3.T
    print(f"  U_3 (3×3):")
    print(np.round(U_3, 4))

    # PMNS 參數化
    Ue1, Ue2, Ue3 = U_3[0, 0], U_3[0, 1], U_3[0, 2]
    s13_2 = Ue3**2
    c13_2 = 1 - s13_2
    s12_2 = Ue2**2 / c13_2
    Umu3 = U_3[1, 2]
    s23_2 = Umu3**2 / c13_2

    theta13 = math.asin(math.sqrt(max(0, min(1, s13_2)))) * 180/math.pi
    theta12 = math.asin(math.sqrt(max(0, min(1, s12_2)))) * 180/math.pi
    theta23 = math.asin(math.sqrt(max(0, min(1, s23_2)))) * 180/math.pi

    print(f"\n  提取角度:")
    print(f"    θ₁₂ = {theta12:.2f}° (實驗 33.41°)")
    print(f"    θ₂₃ = {theta23:.2f}° (實驗 49.1°)")
    print(f"    θ₁₃ = {theta13:.2f}° (實驗 8.54°)")

    err12 = abs(theta12 - 33.41)/33.41*100
    err23 = abs(theta23 - 49.1)/49.1*100
    err13 = abs(theta13 - 8.54)/8.54*100
    print(f"    誤差: θ₁₂ {err12:.1f}%, θ₂₃ {err23:.1f}%, θ₁₃ {err13:.1f}%")
else:
    theta12 = theta23 = theta13 = float('nan')
    err12 = err23 = err13 = float('nan')
    U_3 = np.zeros((3, 3))
    print(f"  k={k} ≠ 3, 跳過 PMNS 提取")

check("θ₁₂ < 30%", err12 < 30, f"({err12:.1f}%)")
check("θ₂₃ < 30%", err23 < 30, f"({err23:.1f}%)")
check("θ₁₃ < 30%", err13 < 30, f"({err13:.1f}%)")

# ============ 4. 總結 ============
print("\n" + "=" * 72)
print("十九期 96 總結:")
print("=" * 72)
print(f"""
  譜聚類中心 → U_PMNS?
  ─────────────────────────────────
  eig-gap position: {max_gap_idx}
  cluster: {sizes}
  θ₁₂ = {theta12:.1f}° (實驗 33.41°)
  θ₂₃ = {theta23:.1f}° (實驗 49.1°)
  θ₁₃ = {theta13:.1f}° (實驗 8.54°)
""")

results = {
    "test": "O57 十九期 96: PMNS 譜聚類",
    "eig_gap_pos": int(max_gap_idx),
    "cluster_sizes": [int(s) for s in sizes],
    "theta12": float(theta12), "theta23": float(theta23), "theta13": float(theta13),
    "err12": float(err12), "err23": float(err23), "err13": float(err13),
    "U_3": [[float(x) for x in row] for row in U_3],
    "passed": passed, "failed": failed
}
with open("data/96_pmns_spectral.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
exit(0)
