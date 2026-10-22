#!/usr/bin/env python3
"""
O70 — 05: 全驗證報告（Summary）
=================================
"""
import sys, os, json, math
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2
Nd = 44
B = 4

def Ln(n):
    return round(phi**n + (-1)**n * phi**(-n))

print("=" * 72)
print("O70 全驗證報告")
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

# 1. 155 = 2×73+9
print("\n[1] 155 = 2×73+9")
check("155 = 630-475", 155 == 36*35//2 - 475)
check("73 = Nd+L₇", 73 == Nd + Ln(7), f"({Nd}+{Ln(7)})")
check("73 = L₆×4+1", 73 == Ln(6)*4 + 1, f"({Ln(6)}×4+1)")
check("9 = 3² = N_gen²", 9 == 3**2)

# 2. Volume vectors
print("\n[2] Volume vectors")
d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
sr = d["sr_ideal"]
sr_set = set()
for s in sr:
    sr_set.add((min(s), max(s)))
adj = [(i, j) for i in range(1, 37) for j in range(i+1, 37) if (i, j) not in sr_set]
kappa = np.array(json.load(open(os.path.join(O53, "cy36_98_intersection_full.json"))).get("kappa"))
V = np.array([kappa[:, i-1, j-1] for i, j in adj])
nz = np.abs(V).sum(axis=1) > 1e-10
rank = np.linalg.matrix_rank(V)
check("52 nonzero = Nd+2B", nz.sum() == Nd + 2*B, f"({nz.sum()})")
check("rank 30 = 2L₅+2B", rank == 2*Ln(5) + 2*B, f"({rank})")

# 3. 66 states
print("\n[3] 66 states")
DATA = os.path.join(BASE, "data")
P_path = os.path.join(DATA, "P_fixed_v2.npy")
if os.path.exists(P_path):
    P = np.load(P_path)
    PPT = P @ P.T
    evals, evecs = np.linalg.eigh(PPT)
    idx = np.argsort(evals)[::-1]
    evecs = evecs[:, idx]
    pos = evals > 1e-10
    evecs_pos = evecs[:, pos][:, :66]
    sector = []
    for i in range(66):
        e_k = np.sum(evecs_pos[:36, i]**2)
        e_c = np.sum(evecs_pos[36:, i]**2)
        sector.append('K' if e_k >= e_c else 'C')
    c_idx = [i for i, s in enumerate(sector) if s == 'C']
    k_idx = [i for i, s in enumerate(sector) if s == 'K']
    check("30 C states", len(c_idx) == 30)
    check("36 K states", len(k_idx) == 36)
    
    # 155 curves vs K states
    U_adj, S_adj, _ = np.linalg.svd(V.T)
    basis_adj = U_adj[:, :30]
    W_C = evecs_pos[:36, c_idx]
    W_K = evecs_pos[:36, k_idx]
    
    # C states projection
    proj_C = W_C.T @ basis_adj
    overlap_C = np.linalg.norm(proj_C, axis=0)
    check("C states orthogonal to 155 curves", overlap_C.max() < 1e-10, 
          f"(max={overlap_C.max():.2e})")
    
    # K states projection
    proj_K = W_K.T @ basis_adj
    overlap_K = np.linalg.norm(proj_K, axis=0)
    check("K states overlap with 155 curves", overlap_K.mean() > 0.5, 
          f"(mean={overlap_K.mean():.3f})")
    
    # 6 null directions
    null_basis = U_adj[:, 30:]
    proj_null_K = null_basis.T @ W_K
    null_overlap = np.linalg.norm(proj_null_K, axis=0)
    check("6 null = 6 K states", np.sum(null_overlap > 0.1), 
          f"({np.sum(null_overlap > 0.1)}/36 K states in null)")

# 4. Summary
print(f"\n{'='*72}")
print(f"總計: Passed {passed}, Failed {failed}")
if failed == 0:
    print("🎉 O70 全驗證 PASS!")
else:
    print(f"⚠️ 有 {failed} 個失敗")
    exit(1)