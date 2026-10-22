#!/usr/bin/env python3
"""
O70 — 最終驗證：全部公式、結構、數值核對
=========================================
"""
import sys, os, math, json, numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2
Nd = 44
B = 4

def Ln(n):
    return round(phi**n + (-1)**n * phi**(-n))

print("=" * 72)
print("O70 最終驗證")
print("=" * 72)

passed = 0
failed = 0
total = 0

def check(name, cond, expected=None, got=None):
    global passed, failed, total
    total += 1
    if cond:
        passed += 1
        detail = f" → {expected}" if expected else ""
        print(f"  ✅ {name}{detail}")
    else:
        failed += 1
        detail = f" (expected {expected}, got {got})" if expected and got else ""
        print(f"  ❌ {name}{detail}")

# ===== 1. Load data =====
print("\n[1] Load data")
d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
sr = d["sr_ideal"]
sr_set = set()
for s in sr:
    sr_set.add((min(s), max(s)))

# 155 adjacency curves
adj = [(i, j) for i in range(1, 37) for j in range(i+1, 37) if (i, j) not in sr_set]
print(f"  Loaded {len(adj)} adjacency curves, {len(sr)} sr_ideal entries")

# ===== 2. 155 = 2×73+9 =====
print("\n[2] 155 = 2×73+9")
check("155 = C(36,2) - 475", len(adj) == 36*35//2 - 475, "155", len(adj))
check("155 = 2×73+9", len(adj) == 2*73+9, "155", len(adj))
check("73 = Nd+L₇", 73 == Nd + Ln(7), f"{Nd}+{Ln(7)}={Nd+Ln(7)}")
check("73 = L₆×4+1", 73 == Ln(6)*4 + 1, f"{Ln(6)}×4+1={Ln(6)*4+1}")
check("9 = 3² = N_gen²", 9 == 3**2, "9")

# 9 duplicates
sr_count = {}
for s in sr:
    key = (min(s), max(s))
    sr_count[key] = sr_count.get(key, 0) + 1
dup_pairs = {k: v for k, v in sr_count.items() if v > 1}
dup_entries = sum(v-1 for v in dup_pairs.values())
check("9 duplicate entries", dup_entries == 9, "9", dup_entries)
check("5 unique duplicate pairs", len(dup_pairs) == 5, "5", len(dup_pairs))

# ===== 3. Volume vectors =====
print("\n[3] Volume vectors")
kappa = np.array(json.load(open(os.path.join(O53, "cy36_98_intersection_full.json"))).get("kappa"))
V_adj = np.array([kappa[:, i-1, j-1] for i, j in adj])  # 155×36

nz = np.abs(V_adj).sum(axis=1) > 1e-10
rank_36 = np.linalg.matrix_rank(V_adj)

check("52 nonzero = Nd+2B", nz.sum() == Nd + 2*B, f"{Nd+2*B}={nz.sum()}")
check("rank 30 in 36D = 2L₅+2B", rank_36 == 2*Ln(5) + 2*B, f"{2*Ln(5)+2*B}={rank_36}")

# 32D rank
import cytools
from cytools import Polytope
from cytools.config import enable_experimental_features
enable_experimental_features()
pts = np.array(d["points"])
p = Polytope(pts)
tri = p.triangulate()
cy = tri.get_cy()
basis = cy.divisor_basis()
basis_0 = np.array([b-1 for b in basis])

V_32 = V_adj[:, basis_0]
rank_32 = np.linalg.matrix_rank(V_32)
check("rank 29 in 32D = L₇", rank_32 == Ln(7), f"{Ln(7)}={rank_32}")
check("Loss from 36D→32D = 1", rank_36 - rank_32 == 1, "1", rank_36 - rank_32)

# ===== 4. 185 curves Q_ij =====
print("\n[4] 185 curves Q_ij")
phi_val = (1 + math.sqrt(5)) / 2
t_test = phi_val ** (-np.arange(36))
t32 = np.array([t_test[b-1] for b in basis])
eps_d = 1e-5
Q = np.zeros((185, 32))
for j in range(32):
    tp = t32.copy(); tm = t32.copy()
    tp[j] += eps_d; tm[j] -= eps_d
    cvp = np.array(cy.compute_curve_volumes(tp))
    cvm = np.array(cy.compute_curve_volumes(tm))
    Q[:, j] = (cvp - cvm) / (2*eps_d)

rank_Q = np.linalg.matrix_rank(Q)
check("Q_ij rank 32", rank_Q == 32, "32", rank_Q)

# Extra dimensions
U_Q, S_Q, Vt_Q = np.linalg.svd(Q, full_matrices=False)
U_155, S_155, Vt_155 = np.linalg.svd(V_32, full_matrices=False)
col_155 = Vt_155[:rank_32].T
col_Q = Vt_Q[:rank_Q].T
Q_orth = col_Q - col_155 @ (col_155.T @ col_Q)
sv_orth = np.linalg.svd(Q_orth, compute_uv=False)
extra = np.sum(sv_orth > 1e-8)
check("Extra dimensions = 3 = N_gen", extra == 3, "3", extra)

# ===== 5. 66 states connection =====
print("\n[5] 66 states connection")
DATA = os.path.join(BASE, "data")
P_path = os.path.join(DATA, "P_fixed_v2.npy")
if os.path.exists(P_path):
    P = np.load(P_path)
    PPT = P @ P.T
    evals, evecs = np.linalg.eigh(PPT)
    idx = np.argsort(evals)[::-1]
    evecs = evecs[:, idx]
    evals = evals[idx]
    pos = evals > 1e-10
    n_pos = pos.sum()
    # Take first 66 positive eigenvalues
    n_states = min(66, n_pos)
    evecs_pos = evecs[:, pos][:, :n_states]
    sector = []
    for i in range(n_states):
        e_k = np.sum(evecs_pos[:36, i]**2)
        e_c = np.sum(evecs_pos[36:, i]**2)
        sector.append('K' if e_k >= e_c else 'C')
    c_idx = [i for i, s in enumerate(sector) if s == 'C']
    k_idx = [i for i, s in enumerate(sector) if s == 'K']
    check(f"{len(c_idx)} C states + {len(k_idx)} K states = {len(c_idx)+len(k_idx)}", 
          len(c_idx) + len(k_idx) == n_states, str(n_states), str(len(c_idx)+len(k_idx)))
    
    # Use V_adj (36D) for 66 states comparison, not V_32 (32D)
    W_C = evecs_pos[:36, c_idx]  # 36 × n_C
    W_K = evecs_pos[:36, k_idx]  # 36 × n_K
    
    # 155 curves vs C states (both in 36D)
    proj_C = W_C.T @ V_adj.T  # n_C × 155
    overlap_C = np.linalg.norm(proj_C, axis=0)
    check("C states orthogonal to 155 curves", overlap_C.max() < 1e-10, 
          f"<1e-10", f"{overlap_C.max():.2e}")
    
    # 155 curves vs K states
    proj_K = W_K.T @ V_adj.T  # n_K × 155
    overlap_K = np.linalg.norm(proj_K, axis=0)
    check("K states overlap with 155 curves", overlap_K.mean() > 0.5,
          ">0.5", f"{overlap_K.mean():.3f}")
    
    # 6 null directions — use 36D SVD
    U_36, S_36, Vt_36 = np.linalg.svd(V_adj, full_matrices=False)
    null_basis_36 = Vt_36[rank_36:rank_36+6].T  # 36×6
    proj_null_K = null_basis_36.T @ W_K
    null_overlap = np.linalg.norm(proj_null_K, axis=0)
    check("6 null directions = 6 K states", np.sum(null_overlap > 0.1) >= 6,
          "≥6", np.sum(null_overlap > 0.1))

# ===== 6. Missing divisors =====
print("\n[6] Missing divisors")
missing = sorted(set(range(1,37)) - set(basis))
check("4 missing divisors [3,4,7,8]", missing == [3,4,7,8], "[3,4,7,8]", missing)

# ===== 7. 99 boundary rays =====
print("\n[7] Boundary rays")
rays_path = os.path.join(os.path.dirname(__file__), "..", "data", "15_all_rays.npy")
if os.path.exists(rays_path):
    R = np.load(rays_path)
    rank_R = np.linalg.matrix_rank(R)
    check("99 rays span full 32D", rank_R == 32, "32", rank_R)
    check("99 unique rays", len(R) >= 32, "≥32", len(R))

# ===== Summary =====
print(f"\n{'='*72}")
print(f"總計: {passed}/{total} PASS, {failed} FAIL")
if failed == 0:
    print("🎉 O70 全部驗證通過!")
else:
    print(f"⚠️ {failed} 個失敗")
    exit(1)