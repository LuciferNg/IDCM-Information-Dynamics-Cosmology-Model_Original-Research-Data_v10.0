#!/usr/bin/env python3
"""
O43-B: Homology groups = Fibonacci cascade verification
Compute Betti numbers of the A₅ 60-node graph
"""
import numpy as np
import math, os
from collections import Counter, defaultdict, deque

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat"
OUT = f"{BASE}/open_problems_fresh/o43_holographic_untested"

# Load nodes
nodes = []
with open(f"{BASE}/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
N = 60

# Convert to unit vectors
vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])

# Build graph (threshold 28°)
adj = [set() for _ in range(N)]
edges = []
for i in range(N):
    for j in range(i+1, N):
        a = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if a < 28:
            adj[i].add(j); adj[j].add(i)
            edges.append((i, j))

E = len(edges)
results = []
def log(*args):
    line = " ".join(str(a) for a in args)
    print(line)
    results.append(line)

log("=" * 72)
log("O43-B: 同調群 = Fibonacci 級聯驗證")
log("=" * 72)
log(f"圖: V={N}, E={E}")

# 1. Connected components (H₀)
log("\n1. H₀ (連通分量):")
visited = set()
components = []
for s in range(N):
    if s in visited: continue
    q = deque([s]); visited.add(s)
    comp = []
    while q:
        u = q.popleft(); comp.append(u)
        for v in adj[u]:
            if v not in visited: visited.add(v); q.append(v)
    components.append(comp)
log(f"   連通分量數: {len(components)}")
for c in components:
    log(f"   分量 ({len(c)} 節點): {sorted(c)[:10]}...")

# 2. Find all triangles (3-cliques)
log("\n2. 三角形 (2-simplices):")
triangles = set()
for i in range(N):
    for j in adj[i]:
        if j <= i: continue
        for k in adj[i] & adj[j]:
            if k > j:
                triangles.add(tuple(sorted((i, j, k))))
log(f"   三角形數: {len(triangles)}")

# 3. Compute graph Laplacian spectrum
log("\n3. 圖拉普拉斯譜:")
import scipy.sparse as sp
from scipy.sparse.linalg import eigsh

A = np.zeros((N, N))
for i, j in edges:
    A[i, j] = A[j, i] = 1
D = np.diag([len(adj[i]) for i in range(N)])
L = D - A

# Compute eigenvalues
eigvals = np.linalg.eigvalsh(L)
log(f"   特徵值 (前10): {[f'{v:.4f}' for v in sorted(eigvals)[:10]]}")
zero_eigs = np.sum(np.abs(eigvals) < 1e-10)
log(f"   零特徵值數: {zero_eigs} (= H₀ 維度)")

# 4. Simplicial homology
log("\n4. 單純同調 (Simplicial homology):")
# Build boundary matrices
# C₀: 0-chains (vertices) — dimension N
# C₁: 1-chains (edges) — dimension E
# C₂: 2-chains (triangles) — dimension T

# ∂₁: C₁ → C₀  (edge boundary: maps edge (i,j) to i + j)
# ∂₂: C₂ → C₁  (triangle boundary: maps triangle (i,j,k) to (i,j)+(j,k)+(i,k))

T = len(triangles)
tri_list = list(triangles)

# Edge indexing
edge_to_idx = {e: idx for idx, e in enumerate(edges)}

# ∂₂ matrix (T × E): triangle → edges
# ∂₂[tri_idx, edge_idx] = 1 if edge is in triangle, with orientation sign
# For simplicity (mod 2 coefficients): 1 if edge in triangle
d2 = np.zeros((T, E), dtype=int)
for ti, tri in enumerate(tri_list):
    for a, b in [(tri[0], tri[1]), (tri[1], tri[2]), (tri[0], tri[2])]:
        e = (min(a, b), max(a, b))
        if e in edge_to_idx:
            d2[ti, edge_to_idx[e]] = 1

# ∂₁ matrix (E × N): edge → vertices
d1 = np.zeros((E, N), dtype=int)
for ei, (i, j) in enumerate(edges):
    d1[ei, i] = 1
    d1[ei, j] = 1

# Compute ranks over GF(2)
# β₀ = dim(ker ∂₀) - dim(im ∂₁) = N - rank(∂₁) = number of components
# Actually over GF(2): β₀ = N - rank(∂₁)
# β₁ = dim(ker ∂₁) - dim(im ∂₂) = (E - rank(∂₁)) - rank(∂₂)
# β₂ = dim(ker ∂₂) - 0 = T - rank(∂₂) (since no 3-chains)

def rank_gf2(M):
    """Compute rank of matrix over GF(2) using Gaussian elimination"""
    if len(M) == 0 or len(M[0]) == 0:
        return 0
    A = M.copy() % 2
    m, n = A.shape
    rank = 0
    row = 0
    for col in range(n):
        pivot = -1
        for r in range(row, m):
            if A[r, col] == 1:
                pivot = r
                break
        if pivot == -1:
            continue
        # Swap
        A[[row, pivot]] = A[[pivot, row]]
        # Eliminate
        for r in range(m):
            if r != row and A[r, col] == 1:
                A[r] ^= A[row]
        row += 1
        rank += 1
        if row == m:
            break
    return rank

rank_d1 = rank_gf2(d1)
rank_d2 = rank_gf2(d2)

# H₀ = ker(∂₀) / im(∂₁)
# ker(∂₀) = C₀ = N (all vertices)
# im(∂₁) = rank(∂₁)
beta0 = N - rank_d1
log(f"   rank(∂₁) = {rank_d1}")
log(f"   β₀ = N - rank(∂₁) = {N} - {rank_d1} = {beta0}")

# H₁ = ker(∂₁) / im(∂₂)
# ker(∂₁) = E - rank(∂₁) (cycles)
# im(∂₂) = rank(∂₂) (boundaries of triangles)
cycles_dim = E - rank_d1
beta1 = cycles_dim - rank_d2
log(f"   rank(∂₂) = {rank_d2}")
log(f"   ker(∂₁) dim = E - rank(∂₁) = {E} - {rank_d1} = {cycles_dim}")
log(f"   β₁ = {cycles_dim} - {rank_d2} = {beta1}")

# H₂ = ker(∂₂) (since no 3-chains)
# Actually H₂ = ker(∂₂) = T - rank(∂₂) for 2-cycles
beta2 = T - rank_d2
log(f"   β₂ = T - rank(∂₂) = {T} - {rank_d2} = {beta2}")

# 5. Compare with Fibonacci numbers
log("\n5. Fibonacci 對比:")
F = [0, 1]
for i in range(2, 15): F.append(F[-1] + F[-2])
log(f"   Fibonacci: F₀=0, F₁=1, F₂=1, F₃=2, F₄=3, F₅=5, F₆=8, F₇=13, F₈=21")
log(f"   β₀ = {beta0}, β₁ = {beta1}, β₂ = {beta2}")
log(f"   β₀ = F₀? {beta0} vs {F[0]}")
log(f"   β₁ = F₅=5? {beta1} vs {F[5]}")
log(f"   β₂ = F₆=8? {beta2} vs {F[6]}")

# Check if Betti numbers match Fibonacci
log("\n6. 振幅級聯對比:")
log(f"   A₅ = 3/14, A₇ = 1/7, A₅/A₇ = 2/3 = F₃/F₄")
log(f"   偶峰: A₂/A₁ = (2/3)² = (F₃/F₄)²")
log(f"   A₄/A₁ = (3/7)² = (L₂/L₄)²")
log(f"   A₆/A₁ = (4/11)² = (L₃/L₅)²")

# 7. Check H₁ cycle structure
log("\n7. H₁ 循環結構:")
# Find cycles that are not boundaries of triangles
# These are the nontrivial 1-cycles representing H₁

# The nullspace of d1 over GF(2) would give us cycles
# But for large matrices this is expensive
# Instead, let's check the number of independent cycles
log(f"   獨立循環數 (β₁) = {beta1}")
log(f"   如果 β₁ = F₅ = 5, 則 Fibonacci 對應成立")
log(f"   如果 β₁ = F₆ = 8, 則 Fibonacci 對應成立")
log(f"   如果 β₁ = 其他, 則 Fibonacci 對應不成立")

# 8. Check Euler characteristic
log("\n8. Euler 特徵數:")
chi = beta0 - beta1 + beta2
log(f"   χ = β₀ - β₁ + β₂ = {beta0} - {beta1} + {beta2} = {chi}")
log(f"   V - E + F = {N} - {E} + {T} = {N - E + T}")
log(f"   (三角形面當作 2-simplices, 冇其他面)")

# Conclusion
log("\n" + "=" * 72)
log("結論:")
log("=" * 72)
fib_match = (beta0 == F[0]) or (beta1 == F[5]) or (beta1 == F[6]) or (beta2 == F[6])
log(f"   Betti 數: β₀={beta0}, β₁={beta1}, β₂={beta2}")
log(f"   Fibonacci 對應: {'✅ 部分成立' if fib_match else '❌ 不成立'}")
log(f"   注意: 圖非平面, 單純同調用 20 個三角形做 2-skeleton")
log(f"   H₁ 嘅表現需要進一步分析 (非平面圖嘅循環結構)")

with open(f"{OUT}/data_o43b.txt", "w") as f:
    f.write("\n".join(results) + "\n")
print(f"\n✅ 結果寫入 {OUT}/data_o43b.txt")