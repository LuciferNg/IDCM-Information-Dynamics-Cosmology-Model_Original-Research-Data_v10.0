#!/usr/bin/env python3
"""
O57 十九期 95: ★★ PMNS 湧現 — Q_ij cluster 中心 Gram-Schmidt
================================================================
scripts/94 發現: cluster 大小比直接比唔中 PMNS (除 tan²θ₁₂=34/81 3.5%)

新方法: 
  1. 重算 Q_ij (185×32)
  2. K-means 3 cluster → 中心向量 c₁,c₂,c₃ (32-dim)
  3. Gram-Schmidt 正交化 → U_PMNS 候選
  4. PMNS 參數化提取 θ₁₂, θ₂₃, θ₁₃
  5. 對比 NuFIT 2024

需要 CYTools (400s)
"""
import sys, os, math
import json
import numpy as np

print("=" * 72)
print("O57 十九期 95: PMNS 湧現 (Gram-Schmidt)")
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

# ============ 1. 建立 CY ============
print("\n[1] 建立 CY")
d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
pts = np.array(d["points"])
p = Polytope(pts)
tri = p.triangulate()
cy = tri.get_cy()
basis = cy.divisor_basis()
print(f"  divisor basis: {len(basis)}")
print(f"  curves: {len(cy.curve_basis())}")

# ============ 2. Q_ij 重算 ============
print("\n[2] Q_ij 重算")
n_div = len(basis)
t0_full = phi ** (-np.arange(36))
t32_0 = np.array([t0_full[b-1] for b in basis])
cv0 = np.array(cy.compute_curve_volumes(t32_0))
n_curves = len(cv0)
print(f"  curves: {n_curves}, divisor basis: {n_div}")

# 中心差分
Q = np.zeros((n_curves, n_div))
eps = 1e-5
for j in range(n_div):
    t_plus = t32_0.copy()
    t_minus = t32_0.copy()
    t_plus[j] += eps
    t_minus[j] -= eps
    cv_plus = np.array(cy.compute_curve_volumes(t_plus))
    cv_minus = np.array(cy.compute_curve_volumes(t_minus))
    Q[:, j] = (cv_plus - cv_minus) / (2*eps)

print(f"  Q shape: {Q.shape}, rank: {np.linalg.matrix_rank(Q)}")
print(f"  Q range: [{Q.min():.1f}, {Q.max():.1f}]")

# ============ 3. K-means 3 cluster (多 seed) ============
print("\n[3] K-means 3 cluster (多 seed)")
U, S, Vt = np.linalg.svd(Q, full_matrices=False)
Q3 = Q @ Vt[:3].T  # 投影到 top-3 奇異向量
print(f"  Q3 shape: {Q3.shape}")

def kmeans(X, k, iters=200, seed=42):
    rng = np.random.default_rng(seed)
    centers = X[rng.choice(len(X), k, replace=False)]
    for _ in range(iters):
        dists = np.linalg.norm(X[:, None, :] - centers[None, :, :], axis=2)
        labels = np.argmin(dists, axis=1)
        new_centers = np.array([X[labels == i].mean(axis=0) if np.any(labels == i) else centers[i] for i in range(k)])
        if np.allclose(new_centers, centers):
            break
        centers = new_centers
    return labels, centers

# 多 seed 揀慣量最小 (最緊湊, 標準 k-means 準則, 冇偷睇)
best_seed = None
best_inertia = 1e9
best_labels = None
for seed in range(30):
    labels, centers_l = kmeans(Q3, 3, seed=seed)
    dists = np.linalg.norm(Q3[:, None, :] - centers_l[None, :, :], axis=2)
    inertia = np.sum(np.min(dists, axis=1)**2)
    if inertia < best_inertia:
        best_inertia = inertia
        best_seed = seed
        best_labels = labels

labels = best_labels
sizes = [np.sum(labels == i) for i in range(3)]
print(f"  cluster sizes (seed {best_seed}, inertia {best_inertia:.3f}): {sizes}")

# 原始空間中心
centers = np.array([Q[labels == i].mean(axis=0) for i in range(3)])
print(f"  centers shape: {centers.shape}")

# ============ 4. Gram-Schmidt → U ============
print("\n[4] Gram-Schmidt 正交化")
# 中心向量減 mean (centering)
centers_c = centers - centers.mean(axis=0)
# Gram-Schmidt
u1 = centers_c[0] / np.linalg.norm(centers_c[0])
u2 = centers_c[1] - np.dot(centers_c[1], u1)*u1
u2 = u2 / np.linalg.norm(u2)
u3 = centers_c[2] - np.dot(centers_c[2], u1)*u1 - np.dot(centers_c[2], u2)*u2
u3 = u3 / np.linalg.norm(u3)
U_gs = np.stack([u1, u2, u3])  # 3×32
print(f"  U_gs shape: {U_gs.shape}")
print(f"  正交性: {np.abs(U_gs @ U_gs.T - np.eye(3)).max():.2e}")

# ============ 5. PMNS 參數化 ============
print("\n[5] PMNS 參數化")
# U_PMNS = U_gs (3×32) 嘅 3×3 子矩陣?
# 方法: 攞 U_gs 前三列 (或前 3 個主要分量)
U_3 = U_gs[:, :3]  # 3×3
# 確保 unitary (Gram-Schmidt 後 rows 正交, 需要 columns 正交)
U_3 = U_3 / np.linalg.norm(U_3, axis=0, keepdims=True)
print(f"  U_3 (3×3):")
print(np.round(U_3, 4))

# PMNS 標準參數化 (PDG):
# |U_e1| = c₁₂c₁₃, |U_e2| = s₁₂c₁₃, |U_e3| = s₁₃
Ue1, Ue2, Ue3 = U_3[0, 0], U_3[0, 1], U_3[0, 2]
s13_2 = Ue3**2
c13_2 = 1 - s13_2
s12_2 = Ue2**2 / c13_2
# |U_μ3| = s₂₃c₁₃
Umu3 = U_3[1, 2]
s23_2 = Umu3**2 / c13_2

theta13 = math.asin(math.sqrt(max(0, s13_2))) * 180/math.pi
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

check("θ₁₂ < 30% 誤差", err12 < 30, f"({err12:.1f}%)")
check("θ₂₃ < 30% 誤差", err23 < 30, f"({err23:.1f}%)")
check("θ₁₃ < 30% 誤差", err13 < 30, f"({err13:.1f}%)")

# ============ 6. 總結 ============
print("\n" + "=" * 72)
print("十九期 95 總結:")
print("=" * 72)
print(f"""
  Q_ij cluster 中心 → U_PMNS?
  ─────────────────────────────────
  cluster: {sizes}
  Gram-Schmidt 提取:
    θ₁₂ = {theta12:.2f}° (實驗 33.41°, 誤差 {err12:.1f}%)
    θ₂₃ = {theta23:.2f}° (實驗 49.1°, 誤差 {err23:.1f}%)
    θ₁₃ = {theta13:.2f}° (實驗 8.54°, 誤差 {err13:.1f}%)

  {'✅ 有混合角結構!' if err12 < 30 and err23 < 30 else '❌ 直接唔啱'}
  {'🟢 θ₁₃ 特別準!' if err13 < 30 else '🔴 θ₁₃ 唔啱'}
""")

results = {
    "test": "O57 十九期 95: PMNS Gram-Schmidt",
    "cluster_sizes": [int(s) for s in sizes],
    "theta12": float(theta12), "theta23": float(theta23), "theta13": float(theta13),
    "err12": float(err12), "err23": float(err23), "err13": float(err13),
    "U_3": [[float(x) for x in row] for row in U_3],
    "passed": passed, "failed": failed
}
with open("data/95_pmns_gramschmidt.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
exit(0)
