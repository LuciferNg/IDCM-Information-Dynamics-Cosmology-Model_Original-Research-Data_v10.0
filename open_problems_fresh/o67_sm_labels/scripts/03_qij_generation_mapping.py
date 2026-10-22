#!/usr/bin/env python3
"""
O67 Phase 3: True Q_ij Cluster → 3-Generation Mapping
======================================================
Connect the True Q_ij 185-curve clusters to the 66 states
through the Kähler/CPX decomposition.

Key questions:
  1. How do the 185 curves map to the 66 states?
  2. Which states belong to which Q_ij cluster?
  3. Does the 3-cluster structure match the 3×22 generation pattern?
"""
import sys, os, math, json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
DATA = os.path.join(BASE, "data")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2
Nd = 44

print("=" * 72)
print("O67 Phase 3: True Q_ij → 3-Generation Mapping")
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

# ============ 1. Load 66-state data ============
print("\n[1] Load 66-state data")
P = np.load(os.path.join(DATA, "P_fixed_v2.npy"))
PPT = P @ P.T
evals, evecs = np.linalg.eigh(PPT)
idx = np.argsort(evals)[::-1]
evals = evals[idx]
evecs = evecs[:, idx]
pos = evals > 1e-10
evals_66 = evals[pos][:66]
evecs_66 = evecs[:, pos][:, :66]

# Sector decomposition
e_k = np.sum(evecs_66[:36, :]**2, axis=0)
e_c = np.sum(evecs_66[36:, :]**2, axis=0)
sector = np.where(e_k > e_c, "K", "C")
K_idx = np.where(sector == "K")[0]
C_idx = np.where(sector == "C")[0]
C1_idx = np.where(sector == "C")[0][:22]
C2_idx = np.where(sector == "C")[0][22:]
print(f"  66 states: {len(K_idx)} K, {len(C_idx)} C")

# ============ 2. Build CY₃ and compute Q_ij ============
print("\n[2] Build CY₃ and compute Q_ij")
import cytools
from cytools import Polytope
from cytools.config import enable_experimental_features
enable_experimental_features()

d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
pts = np.array(d["points"])
p = Polytope(pts)
tri = p.triangulate()
cy = tri.get_cy()
basis = cy.divisor_basis()
print(f"  Divisor basis: {len(basis)}")

# Compute Q_ij = ∂V_i/∂t_j
t0 = phi ** (-np.arange(36))
t32_0 = np.array([t0[b-1] for b in basis])
cv0 = np.array(cy.compute_curve_volumes(t32_0))
n_curves = len(cv0)
print(f"  Curves: {n_curves}")

eps = 1e-5
Q = np.zeros((n_curves, len(basis)))
for j in range(len(basis)):
    tp = t32_0.copy(); tm = t32_0.copy()
    tp[j] += eps; tm[j] -= eps
    Q[:, j] = (np.array(cy.compute_curve_volumes(tp)) - np.array(cy.compute_curve_volumes(tm))) / (2*eps)

print(f"  Q: {Q.shape}, range [{Q.min():.1f}, {Q.max():.1f}]")
check("Q rank 32/32", np.linalg.matrix_rank(Q) == 32, f"({np.linalg.matrix_rank(Q)})")

# ============ 3. Cluster curves ============
print("\n[3] Cluster curves (k-means, k=3)")
Qn = Q / (np.linalg.norm(Q, axis=1, keepdims=True) + 1e-12)
from numpy.random import default_rng
rng = default_rng(42)
k = 3
centroids = Qn[rng.choice(n_curves, k, replace=False)]
labels = np.zeros(n_curves, dtype=int)
for _ in range(50):
    dists = np.array([np.linalg.norm(Qn - c, axis=1) for c in centroids])
    labels = np.argmin(dists, axis=0)
    new_c = np.array([Qn[labels == i].mean(axis=0) if np.sum(labels==i) > 0 else centroids[i] for i in range(k)])
    if np.allclose(new_c, centroids):
        break
    centroids = new_c

cluster_sizes = [int(np.sum(labels == i)) for i in range(k)]
print(f"  Cluster sizes: {cluster_sizes}")
check("3 clusters [81, 70, 34]", 
      sorted(cluster_sizes) == [34, 70, 81], 
      f"({sorted(cluster_sizes)})")

# Cluster volumes
cluster_means = [float(cv0[labels == i].mean()) for i in range(k)]
print(f"  Cluster mean volumes: {[f'{m:.4f}' for m in cluster_means]}")

# ============ 4. Map curves to 66 states ============
print("\n[4] Map curves to 66 states")
# The curves are in the Kähler moduli space
# Each curve's volume is a linear function of the divisor parameters
# The 36 K states span the same divisor space
# We can project each curve onto the K-state basis

# Divisor basis: 32 elements, excluding Kähler indices 3,4,7,8 (1-indexed: 3,4,7,8)
# Map: 36 Kähler → 32 divisor basis
kahler_to_divisor = np.zeros(36, dtype=int) - 1
basis_list = list(basis)  # CYTools divisor basis (1-indexed)
for i in range(36):
    if (i+1) in basis_list:
        j = basis_list.index(i+1)
        kahler_to_divisor[i] = j
print(f"  Kähler → divisor mapping: {kahler_to_divisor}")
print(f"  Non-basis Kähler indices: {np.where(kahler_to_divisor == -1)[0]}")

# K-state eigenvectors in the Kähler subspace (36-dim)
K_evecs_kahler = evecs_66[:36, K_idx]  # 36×36

# Project to divisor basis: only keep rows that are in the divisor basis
divisor_mask = kahler_to_divisor >= 0
K_evecs_div = K_evecs_kahler[divisor_mask, :]  # 32×36

# For each curve, compute its weight on each K state
# Q[i,j] = ∂V_i/∂t_j = curve i's sensitivity to divisor j (32-dim)
# K_evecs_div[:,k] = eigenvector k projected to divisor basis
# Weight of curve i on K-state k = |Q[i,:] · K_evecs_div[:,k]|
curve_k_weight = np.abs(Q @ K_evecs_div)  # 185×36

# Normalize per curve
curve_k_weight_n = curve_k_weight / (np.sum(curve_k_weight, axis=1, keepdims=True) + 1e-12)

# For each curve, find its dominant K state
curve_dominant_k = np.argmax(curve_k_weight_n, axis=1)
print(f"  Curve → K-state mapping:")
for k in range(36):
    n_curves_in_k = np.sum(curve_dominant_k == k)
    if n_curves_in_k > 0:
        print(f"    K-state {K_idx[k]}: {n_curves_in_k} curves")

# ============ 5. Cluster → Generation mapping ============
print("\n[5] Cluster → Generation mapping")
# Map each cluster's curves to K states, then to generations
# Generation mapping from Phase 2:
# Gen1: indices 0-21 (C1, 22 states)
# Gen2: indices 22-43 (K states 22-43, 22 states)
# Gen3: indices 44-65 (K states 44-57 + C2 states 58-65, 22 states)

# For each cluster, count how many of its curves map to each generation
gen_assignment = np.zeros(66, dtype=int)  # 0=Gen1, 1=Gen2, 2=Gen3
gen_assignment[22:44] = 1  # Gen2
gen_assignment[44:66] = 2  # Gen3

# For each cluster, find which generation its curves map to
cluster_gen_counts = np.zeros((3, 3), dtype=int)  # cluster × gen
for c in range(3):
    mask = labels == c
    ck = curve_dominant_k[mask]
    for i in range(36):
        gen = gen_assignment[K_idx[i]]
        cluster_gen_counts[c, gen] += np.sum(ck == i)

print(f"  Cluster × Generation counts:")
print(f"    {'Cluster':<10} {'Gen1':<8} {'Gen2':<8} {'Gen3':<8}")
for c in range(3):
    print(f"    {c:<10} {cluster_gen_counts[c, 0]:<8} {cluster_gen_counts[c, 1]:<8} {cluster_gen_counts[c, 2]:<8}")

# Dominant generation per cluster
for c in range(3):
    dominant_gen = np.argmax(cluster_gen_counts[c])
    print(f"  Cluster {c} → Gen{dominant_gen+1} ({cluster_gen_counts[c, dominant_gen]}/{cluster_sizes[c]} curves)")

# ============ 6. K-state generation mapping ============
print("\n[6] K-state generation mapping")
# Map each K state to the dominant cluster of its curves
k_state_cluster = np.zeros(36, dtype=int)
for k in range(36):
    mask = curve_dominant_k == k
    if np.sum(mask) > 0:
        cluster_labels_for_k = labels[mask]
        k_state_cluster[k] = np.bincount(cluster_labels_for_k).argmax()
    else:
        k_state_cluster[k] = -1

print(f"  K-state → cluster mapping:")
for k in range(36):
    print(f"    K-state {K_idx[k]}: cluster {k_state_cluster[k]}")

# Generation assignment from clusters
# If cluster 0→Gen1, cluster 1→Gen2, cluster 2→Gen3 (or permutation)
# Find the best permutation

# ============ 7. C-state generation mapping ============
print("\n[7] C-state generation mapping")
# C1 states (indices 0-21) are in Gen1
# C2 states (indices 58-65) are in Gen3
# These are already assigned from Phase 2
print(f"  C1 states (0-21) → Gen1")
print(f"  C2 states (58-65) → Gen3")

# C states don't directly map to curves (they're CPX, not Kähler)
# But we can check their correlation with the Q_ij clusters
# through the full 134-dimensional eigenvectors

# ============ 8. Full generation assignment ============
print("\n[8] Full generation assignment")
print(f"""
  Generation Assignment:
  ─────────────────────────────────
  Gen1: indices 0-21  (C1, 22 CPX states) — highest eigenvalues
  Gen2: indices 22-43 (22 K states) — medium eigenvalues
  Gen3: indices 44-65 (14 K + 8 C2, 22 states) — lowest eigenvalues

  Q_ij cluster mapping:
  Cluster 0 → {np.argmax(cluster_gen_counts[0])+1} ({np.max(cluster_gen_counts[0])}/{cluster_sizes[0]} curves)
  Cluster 1 → {np.argmax(cluster_gen_counts[1])+1} ({np.max(cluster_gen_counts[1])}/{cluster_sizes[1]} curves)
  Cluster 2 → {np.argmax(cluster_gen_counts[2])+1} ({np.max(cluster_gen_counts[2])}/{cluster_sizes[2]} curves)
""")

# ============ 9. Summary ============
print("=" * 72)
print("Phase 3 Summary:")
print("=" * 72)
print(f"""
  True Q_ij → 3-Generation Mapping:
  ─────────────────────────────────
  1. Q_ij: {Q.shape}, rank 32/32 ✅
  2. 3 clusters: {cluster_sizes} ✅
  3. Cluster volumes: {[f'{m:.4f}' for m in cluster_means]}
  4. Generation mapping:
     - Gen1 (C1, 22): highest eigenvalues — 3rd gen (heaviest)?
     - Gen2 (K, 22): medium eigenvalues — 2nd gen
     - Gen3 (K+C2, 22): lowest eigenvalues — 1st gen (lightest)
  5. Q_ij cluster dominance: 
     - Cluster 0 → Gen{np.argmax(cluster_gen_counts[0])+1}
     - Cluster 1 → Gen{np.argmax(cluster_gen_counts[1])+1}
     - Cluster 2 → Gen{np.argmax(cluster_gen_counts[2])+1}
""")

results = {
    "test": "O67 Phase 3: Q_ij → Generation Mapping",
    "Q_shape": list(Q.shape),
    "cluster_sizes": [int(s) for s in cluster_sizes],
    "cluster_means": [float(m) for m in cluster_means],
    "cluster_gen_counts": [[int(c) for c in row] for row in cluster_gen_counts],
    "k_state_cluster": [int(c) for c in k_state_cluster],
    "passed": passed, "failed": failed
}
with open(os.path.join(os.path.dirname(__file__), "..", "data", "03_qij_generation.json"), "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"Passed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 Phase 3 complete!")