#!/usr/bin/env python3
"""
O57 七期 50: 真空翻轉 — C 態質量 3×10 聚類測試
================================================
Gemini 苗頭 1: 負質量 = 塔基昂真空 → 翻轉 M²=|λ|
Gemini 苗頭 2: 負 volume = cone 取向 → V_phys=|V|

測試:
  1. C 態 30 個質量 (γ98 weighted) — |λ| mapping
  2. 有冇 3×10 聚類 (3 代 × 10 態)?
  3. Support 28-98 有冇 3 組?
  4. 聚類顯著性 (permutation test)
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
DATA = os.path.join(BASE, "data")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 七期 50: 真空翻轉 C 態 3×10")
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

# ============ 1. 66 態 ============
print("\n[1] 66 態")
P = np.load(os.path.join(DATA, "P_fixed_v2.npy"))
evals, evecs = np.linalg.eigh(P @ P.T)
idx = np.argsort(evals)[::-1]
evals = evals[idx]
evecs = evecs[:, idx]
pos = evals > 1e-10
evecs_pos = evecs[:, pos][:, :66]
e_k = np.sum(evecs_pos[:36, :]**2, axis=0)
e_c = np.sum(evecs_pos[36:, :]**2, axis=0)
sector = np.where(e_k > e_c, "K", "C")
C_idx = np.where(sector == "C")[0]
K_idx = np.where(sector == "K")[0]
W_C = evecs_pos[36:, C_idx]  # 98×30
print(f"  C: {len(C_idx)}, K: {len(K_idx)}")

# ============ 2. 質量譜 (多種 weighting) ============
print("\n[2] 質量譜 (多種 weighting)")
gamma = 4 * np.sin(np.pi * np.arange(1, 45) / 88) ** 2
gamma98 = np.concatenate([gamma, gamma, gamma[:10]])

# 方法 A: γ98 weighted (之前)
A_Cw = W_C.T @ np.diag(gamma98) @ W_C
ev_A = np.linalg.eigvalsh(A_Cw)
mA = np.abs(ev_A)  # 真空翻轉
mA_sorted = np.sort(mA)[::-1]
print(f"  A (γ98): {mA_sorted}")

# 方法 B: identity (A_C = I → 全部 1, 冇結構)
# 方法 C: support-weighted
support = np.sum(np.abs(W_C) > 1e-3, axis=0)
mC_sup = support / 98
mC_sup_sorted = np.sort(mC_sup)[::-1]
print(f"  C (support): {mC_sup_sorted}")
print(f"  support: {np.sort(support)[::-1]}")

# ============ 3. 3×10 聚類測試 ============
print("\n[3] 3×10 聚類測試")
# 方法: k-means (k=3) 喺質量值上
def kmeans_1d(x, k=3, iters=100, seed=42):
    rng = np.random.default_rng(seed)
    x = np.array(x, dtype=float)
    centers = rng.choice(x, k, replace=False)
    for _ in range(iters):
        dists = np.abs(x[:, None] - centers[None, :])
        labels = np.argmin(dists, axis=1)
        new_centers = np.array([x[labels == j].mean() if np.sum(labels == j) > 0 else centers[j]
                                for j in range(k)])
        if np.allclose(new_centers, centers):
            break
        centers = new_centers
    return labels, centers

for name, masses in [("γ98 |λ|", mA), ("support", mC_sup)]:
    labels, centers = kmeans_1d(masses, k=3)
    counts = np.bincount(labels, minlength=3)
    print(f"\n  --- {name} ---")
    print(f"  clusters: {counts} (目標 10/10/10)")
    print(f"  centers: {centers}")
    # cluster 質量範圍
    for j in range(3):
        cls = masses[labels == j]
        if len(cls) > 0:
            print(f"    cluster {j}: n={len(cls)}, range=[{cls.min():.4f}, {cls.max():.4f}]")

# ============ 4. 聚類顯著性 ============
print("\n[4] 聚類顯著性 (permutation)")
# 用 silhouette score 或者 within-cluster variance
def within_var(x, labels, k=3):
    return sum(np.sum((x[labels == j] - x[labels == j].mean())**2) for j in range(k))

rng = np.random.default_rng(123)
for name, masses in [("γ98 |λ|", mA), ("support", mC_sup)]:
    labels, _ = kmeans_1d(masses, k=3)
    w_obs = within_var(masses, labels)
    # permutation
    n_perm = 500
    w_null = []
    for _ in range(n_perm):
        perm_labels = rng.integers(0, 3, len(masses))
        # 修正: 保證每 cluster 至少 1 個
        while len(np.unique(perm_labels)) < 3:
            perm_labels = rng.integers(0, 3, len(masses))
        w_null.append(within_var(masses, perm_labels))
    w_null = np.array(w_null)
    p_val = np.mean(w_null <= w_obs)
    print(f"\n  --- {name} ---")
    print(f"  within-var observed: {w_obs:.4f}")
    print(f"  within-var null mean: {w_null.mean():.4f} ± {w_null.std():.4f}")
    print(f"  p = {p_val:.3f}")
    check(f"{name} 聚類顯著 (p<0.05)", p_val < 0.05, f"(p={p_val:.3f})")

# ============ 5. 總結 ============
print("\n" + "=" * 72)
print("七期 50 總結:")
print("=" * 72)
print(f"""
  真空翻轉 C 態 3×10:
  ─────────────────────────────────
  1. γ98 |λ|: {mA_sorted[:5]}...
  2. support: {np.sort(support)[::-1][:5]}...
  3. k-means 3 cluster: 睇上面
  4. permutation: 睇上面

  {'✅ 有 3×10 聚類!' if False else '❌ 睇上面結果'}
""")

results = {
    "test": "O57 七期 50: 真空翻轉",
    "mA": [float(x) for x in mA_sorted],
    "support": [int(x) for x in np.sort(support)[::-1]],
    "passed": passed, "failed": failed
}
with open("data/50_vacuum_flip.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 七期 50 完成!")
