#!/usr/bin/env python3
"""
O57 十四期 81: 真 Q_ij 世代結構 — 行空間/列空間分析
======================================================
scripts/80: 真 Q_ij = 185×32, rank 32/32, 冇零模式
scripts/68: γ-weighted Q 顯示 3 代階梯 (0.57→1.92→3.16)

問題: 真 Q_ij 有冇世代結構?
方法:
  1. Q 列空間 (curve 空間) 聚類
  2. Q 行空間 (divisor 空間) 本徵結構
  3. 每條 curve 嘅 volume 向量 → 相似度聚類
  4. 3 個 cluster? (3 代?)
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 十四期 81: 真 Q_ij 世代結構")
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

# ============ 1. 建立 + Q ============
print("\n[1] 建立 + Q_ij")
d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
pts = np.array(d["points"])
p = Polytope(pts)
tri = p.triangulate()
cy = tri.get_cy()
basis = cy.divisor_basis()

t0 = phi ** (-np.arange(36))
t32_0 = np.array([t0[b-1] for b in basis])
cv0 = np.array(cy.compute_curve_volumes(t32_0))
n_curves = len(cv0)

eps = 1e-5
Q = np.zeros((n_curves, len(basis)))
for j in range(len(basis)):
    tp = t32_0.copy(); tm = t32_0.copy()
    tp[j] += eps; tm[j] -= eps
    Q[:, j] = (np.array(cy.compute_curve_volumes(tp)) - np.array(cy.compute_curve_volumes(tm))) / (2*eps)

print(f"  Q: {Q.shape}, range [{Q.min():.1f}, {Q.max():.1f}]")

# ============ 2. curve 相似度聚類 ============
print("\n[2] curve 相似度 (Q 列空間)")
# 正規化每行
Qn = Q / (np.linalg.norm(Q, axis=1, keepdims=True) + 1e-12)
# 相關矩陣
C = Qn @ Qn.T  # 185×185
print(f"  相關矩陣: {C.shape}")
print(f"  對角: {np.diag(C)[:5]}")
off = C - np.eye(n_curves)
print(f"  off-diag mean: {off.mean():.4f}, std: {off.std():.4f}")
print(f"  off-diag range: [{off.min():.4f}, {off.max():.4f}]")

# 高相關 pairs
hi = np.argwhere(np.abs(off) > 0.9)
print(f"  |corr|>0.9: {len(hi)} pairs")

# ============ 3. 本徵聚類 (譜聚類) ============
print("\n[3] 譜聚類 (Laplacian)")
# 用 Q Q^T 嘅本徵值 (curve 空間)
eigvals, eigvecs = np.linalg.eigh(Q @ Q.T)
# 大本徵值 = 主要結構
print(f"  QQ^T 本徵值 (top 10): {eigvals[::-1][:10]}")
print(f"  eig gap 分析:")
eigs_desc = eigvals[::-1]
for i in range(1, 6):
    gap = eigs_desc[i-1] - eigs_desc[i]
    print(f"    gap {i}: {gap:.3f} ({eigs_desc[i-1]:.1f} → {eigs_desc[i]:.1f})")

# 最大 gap = 聚類數?
gaps = [eigs_desc[i] - eigs_desc[i+1] for i in range(min(10, len(eigs_desc)-1))]
max_gap_idx = np.argmax(gaps) + 1
print(f"  最大 gap: {gaps[max_gap_idx-1]:.3f} at position {max_gap_idx} (→ {max_gap_idx+1} clusters?)")

# ============ 4. K-means 3 clusters ============
print("\n[4] K-means (3 clusters, 3 代?)")
from numpy.random import default_rng
rng = default_rng(42)
# 用 Q 列 (32-dim) 做 k-means
k = 3
centroids = Qn[rng.choice(n_curves, k, replace=False)]
for _ in range(50):
    dists = np.array([np.linalg.norm(Qn - c, axis=1) for c in centroids])
    labels = np.argmin(dists, axis=0)
    new_c = np.array([Qn[labels == i].mean(axis=0) if np.sum(labels==i) > 0 else centroids[i] for i in range(k)])
    if np.allclose(new_c, centroids):
        break
    centroids = new_c

print(f"  cluster sizes: {[np.sum(labels==i) for i in range(k)]}")
# cluster 內平均 volume (用 cv0)
for i in range(k):
    idx = np.where(labels == i)[0]
    vols = cv0[idx]
    print(f"  cluster {i} ({len(idx)}): mean vol = {vols.mean():.4f}, std = {vols.std():.4f}")

# ============ 5. 世代階梯? ============
print("\n[5] 世代階梯檢查")
# cluster mean volume 有冇階梯?
cluster_means = [cv0[labels==i].mean() for i in range(k)]
cluster_means.sort(reverse=True)
print(f"  cluster mean volumes: {[f'{m:.4f}' for m in cluster_means]}")
if len(cluster_means) >= 2 and cluster_means[0] > 0:
    ratios = [cluster_means[i]/cluster_means[i+1] for i in range(len(cluster_means)-1)]
    print(f"  比率: {[f'{r:.2f}' for r in ratios]}")
    print(f"  φ² = {phi**2:.3f}, φ = {phi:.3f}")
    check("有 φ 階梯", any(abs(r - phi**2)/phi**2 < 0.3 or abs(r-phi)/phi < 0.3 for r in ratios),
          f"({[f'{r:.2f}' for r in ratios]})")

# ============ 6. 總結 ============
print("\n" + "=" * 72)
print("十四期 81 總結:")
print("=" * 72)
print(f"""
  真 Q_ij 世代結構:
  ─────────────────────────────────
  1. Q: {Q.shape}, rank 32/32
  2. 譜聚類: 最大 gap at {max_gap_idx+1} clusters?
  3. K-means: {[np.sum(labels==i) for i in range(k)]}
  4. cluster volumes: {[f'{m:.3f}' for m in cluster_means]}

  {'✅ 真 Q 有世代結構!' if any(abs(r-phi**2)/phi**2 < 0.3 or abs(r-phi)/phi < 0.3 for r in ratios) else '❌ 冇明顯 φ 階梯'}
""")

results = {
    "test": "O57 十四期 81: 真 Q 世代",
    "Q_shape": list(Q.shape),
    "eig_top10": [float(e) for e in eigs_desc[:10]],
    "max_gap": int(max_gap_idx),
    "cluster_sizes": [int(np.sum(labels==i)) for i in range(k)],
    "cluster_means": [float(m) for m in cluster_means],
    "passed": passed, "failed": failed
}
with open("data/81_q_generations.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 十四期 81 完成!")
