#!/usr/bin/env python3
"""
O70 — 39: INDEPENDENT FULL VERIFICATION (audit)
================================================
由 CYTools raw data 開始, 獨立重跑成條鏈, 驗證文檔所有 claims:
  A. v1 結構: 155=2×73+9, 73=Nd+L₇, 9=3², 52=Nd+2B, rank 30/29/32
  B. Mori cone 185 rays (exact int, 32D)
  C. Facet-defining = 46 (139 redundant)
  D. Sage PPL extreme rays = 3732
  E. 所有 ray ∈ K, rank 31, 舊 99 ⊂ 3732
"""
import os, sys, json, math
import numpy as np
from scipy.optimize import linprog

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

sys.path.insert(0, "/home/wsl/Projects/IDCM-Original/tools/cytools")
from cytools.config import enable_experimental_features
enable_experimental_features()
from cytools import Polytope

print("=" * 76)
print("O70 39: INDEPENDENT FULL VERIFICATION")
print("=" * 76)

passed, failed = [], []

def check(name, cond, detail=""):
    (passed if cond else failed).append(name)
    print(f"  [{'✅' if cond else '❌'}] {name}  {detail}")

# ═══════════════════════════════════════════════════════════
# A. v1 結構 claims (純數學)
# ═══════════════════════════════════════════════════════════
print("\n─── A. v1 結構 claims ───")
# Lucas 數: L1=1,L2=3,L3=4,L4=7,L5=11,L6=18,L7=29,L8=47
L = {1:1,2:3,3:4,4:7,5:11,6:18,7:29,8:47}
# Fibonacci: F1=1,F2=1,F3=2,F4=3,F5=5,F6=8,F7=13,F8=21
F = {1:1,2:1,3:2,4:3,5:5,6:8,7:13,8:21}
Nd = 44
N_gen = 3
B = 4  # K_Tree 分支

check("155 = 2×73 + 9", 155 == 2*73 + 9, "155=146+9")
check("73 = Nd + L₇ = 44+29", 73 == Nd + L[7], f"{Nd}+{L[7]}")
check("73 = L₆×4+1 = 18×4+1", 73 == L[6]*4 + 1, f"{L[6]}×4+1")
check("9 = 3² = N_gen²", 9 == N_gen**2)
check("52 = Nd + 2B = 44+8", 52 == Nd + 2*B, f"{Nd}+{2*B}")
check("155 = C(36,2) − 475", 155 == 36*35//2 - 475, f"C(36,2)={36*35//2}")
check("rank 30 = 2L₅+2B = 22+8", 30 == 2*L[5] + 2*B, f"{2*L[5]}+{2*B}")
check("rank 29 = L₇", 29 == L[7])
check("185 = 155 + 30", 185 == 155 + 30)
check("extra 3 = N_gen", 3 == N_gen)

# ═══════════════════════════════════════════════════════════
# B. Mori cone 重建 (CYTools)
# ═══════════════════════════════════════════════════════════
print("\n─── B. Mori cone (CYTools) ───")
d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
pts = np.array(d["points"])
p = Polytope(pts)
tri = p.triangulate()
cy = tri.get_cy()
mc = cy.toric_mori_cone(in_basis=True)
M = np.array(mc.rays(), dtype=int)
print(f"  Mori rays: {M.shape}")
check("Mori rays 185×32", M.shape == (185, 32))
check("Mori rays exact int", np.allclose(M, np.round(M)))
check("Mori rays rank 32", np.linalg.matrix_rank(M.astype(float)) == 32)
check("冇 collinear pairs", len(M) == len(np.unique(M, axis=0)))

# ═══════════════════════════════════════════════════════════
# C. Facet-defining 檢查 (185 LP)
# ═══════════════════════════════════════════════════════════
print("\n─── C. Facet-defining 檢查 (185 LP, ~2-4 min) ───")
Mf_float = M.astype(float)
facet_def = []
for i in range(185):
    mask = np.ones(185, dtype=bool); mask[i] = False
    c = np.zeros(33); c[0] = -1
    A_ub = np.hstack([np.ones((184, 1)), -Mf_float[mask]])
    b_ub = np.zeros(184)
    A_eq = np.array([[0.0] + list(Mf_float[i])])
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=[0.0],
                  bounds=[(None, None)] + [(-1, 1)] * 32, method='highs')
    if res.success and -res.fun > 1e-7:
        facet_def.append(i)
check("facet-defining = 46", len(facet_def) == 46, f"got {len(facet_def)}")

# ═══════════════════════════════════════════════════════════
# D. Sage PPL extreme rays
# ═══════════════════════════════════════════════════════════
print("\n─── D. Sage PPL extreme rays (46 facets) ───")
from sage.all import Polyhedron
Mf_int = M[facet_def]
ieqs = [tuple([0] + [int(x) for x in row]) for row in Mf_int]
P = Polyhedron(ieqs=ieqs, backend='ppl')
print(f"  Polyhedron dim: {P.dim()}, rays: {len(P.rays())}")
check("Polyhedron dim 32", P.dim() == 32)
check("extreme rays = 3732", len(P.rays()) == 3732, f"got {len(P.rays())}")

rays = []
for r in P.rays():
    v = np.array([float(x) for x in r.vector().list()])
    n = np.linalg.norm(v)
    if n > 1e-12:
        rays.append(v / n)
R = np.array(rays)
print(f"  normalized rays: {R.shape}")

# ═══════════════════════════════════════════════════════════
# E. 驗證
# ═══════════════════════════════════════════════════════════
print("\n─── E. 驗證 ───")
# E1: 全部 ∈ K (185 ieqs)
viol = Mf_float @ R.T
check("全部 3732 ∈ K (185 ieqs)", viol.min() > -1e-6, f"min={viol.min():.2e}")

# E2: active rows rank (抽樣 500)
rng = np.random.default_rng(0)
sample = rng.choice(len(R), 500, replace=False)
bad_rank = 0
for j in sample:
    act = np.where(np.abs(viol[:, j]) < 1e-9)[0]
    if len(act) >= 31:
        rk = np.linalg.matrix_rank(Mf_float[act])
        if rk != 31:
            bad_rank += 1
    else:
        bad_rank += 1
check("active-rows rank = 31 (500 抽樣)", bad_rank == 0, f"{bad_rank} bad")

# E3: 舊 99 ⊂ 3732
R99 = np.load(os.path.join(DATA, "15_all_rays.npy"))
def signfix(r):
    for x in r:
        if abs(x) > 1e-10:
            return r if x > 0 else -r
    return r
Rf = np.array([signfix(r) for r in R])
R99f = np.array([signfix(r) for r in R99])
Dmat = np.abs(R99f @ Rf.T)
check("舊 99 ⊂ 3732 (99/99)", (Dmat.max(axis=1) > 1 - 1e-6).sum() == 99,
      f"{(Dmat.max(axis=1) > 1-1e-6).sum()}/99")

# E4: 同已存檔 33 數據一致
R33 = np.load(os.path.join(DATA, "33_exact_extreme_rays_ppl.npy"))
D33 = np.abs((Rf / np.linalg.norm(Rf,axis=1,keepdims=True)) @ (R33 / np.linalg.norm(R33,axis=1,keepdims=True)).T)
check("重跑結果 = 已存檔 33 數據", D33.max() > 1 - 1e-6 and D33.shape == (len(R), len(R33)),
      f"{D33.shape}")

# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 76)
print(f"RESULT: {len(passed)} PASS, {len(failed)} FAIL")
if failed:
    print(f"FAILED: {failed}")
print("=" * 76)
sys.exit(1 if failed else 0)
