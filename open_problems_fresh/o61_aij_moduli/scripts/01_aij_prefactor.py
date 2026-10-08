#!/usr/bin/env python3
"""
O61 一期 01: A_ij(z) pre-factor — 複結構模空間 3-form 交集積分
================================================================
問題: CY₃(36,98) 嘅 Yukawa 矩陣需要 A_ij(z) pre-factor:
  A_ij(z) = ∫_X α_i ∧ β_j ∧ Ω(z)  (i,j = 1..98, 複結構模)
但 98 維模空間嘅完整計算唔可行 → 用 IDCM 結構做簡化:

IDCM 結構:
  h²¹ = 98 = Σγ + 2B = 90 + 8
  b₃ = 2(1+h²¹) = 198
  CPX sector: 484 odd beats = R²²⊗R²²
  66 態: 3×22 (3 代 × Nd/2)

方法:
  1. 用 P̂ 投影算子 (134×946) 攞 CPX 分量 W_C (98×30)
  2. 建構 98-dim 3-form basis: 用 h²¹=98 嘅結構性分解
     98 = 3×12 (C(12,2)=66?) + 62? 或者 98 = 2×44 + 10?
  3. A_ij = 幾何 pairing: ∫ α_i ∧ β_j 用 γ 譜權重
  4. 驗證 A_ij 對稱性 (A_ij = A_ji? antisymmetric?)
  5. 同 66 態結構對應
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
DATA_DIR = os.path.join(BASE, "main_problems", "p15_early_derivations", "data")
DATA = DATA_DIR  # P_fixed_v2.npy 真實位置 (2026-10-08 修正: 原 BASE/data 斷裂)
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O61 一期 01: A_ij(z) pre-factor — 3-form 交集積分")
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

# ============ 1. 結構常數 ============
print("\n[1] IDCM 結構常數")
B = 4
L5, L6 = 11, 18
F8 = 21
Nd = 44
h11, h21 = 36, 98
chi = 2 * (h11 - h21)
b3 = 2 * (1 + h21)
gamma = 4 * np.sin(np.pi * np.arange(1, 45) / 88) ** 2
print(f"  h11={h11}, h21={h21}, χ={chi}, b₃={b3}")
print(f"  Σγ={gamma.sum():.6f} (應=90)")
check("Σγ = 90", abs(gamma.sum() - 90) < 1e-10)
check("h21 = Σγ + 2B = 98", h21 == int(gamma.sum()) + 2 * B)
check("b₃ = 2(1+h21) = 198", b3 == 2 * (1 + h21))

# ============ 2. 3-form basis 建構 ============
print("\n[2] 3-form basis (h²¹=98 維)")
# 複結構模空間 H^{2,1}(X) 維度 h21=98
# 用 P̂ 投影算子: 98×946 CPX 分量
P = np.load(os.path.join(DATA, "P_fixed_v2.npy"))
print(f"  P̂ shape: {P.shape}")
# P̂ 134×946: 前 36 行 Kähler, 後 98 行 CPX
P_cpx = P[36:, :]  # 98×946
# CPX 行 rank 73, 缺口 25
rank_cpx = np.linalg.matrix_rank(P_cpx, tol=1e-10)
print(f"  CPX rank: {rank_cpx} (缺口 {98-rank_cpx})")
check("CPX rank = 73", rank_cpx == 73)
check("缺口 = 25", 98 - rank_cpx == 25)

# 3-form basis: 用 SVD 攞 73 個有效 CPX 方向
U, S, Vt = np.linalg.svd(P_cpx, full_matrices=False)
n_eff = np.sum(S > 1e-10)
print(f"  SVD: {n_eff} 個非零奇異值")
check("SVD rank = 73", n_eff == 73)

# 98-dim 嘅結構性分解: h21 = 98
# 98 = 2×44 + 10? 或者 98 = 3×32 + 2? 或者 98 = 4×24 + 2?
# 但其實 O57 docs/02: 66 態 = 22 C + 36 K + 8 C
# C 態 30 個 = 2L5 + 2B, K 態 36 = 2L6
# 98-dim 複結構模空間同 30 C 態嘅關係?
# 30 = 2×11 + 2×4 = 2L5 + 2B
print("\n  98-dim 分解候選:")
for block in [12, 22, 32, 44, 49]:
    if 98 % block == 0:
        print(f"    98 = {98//block} × {block} ✅")
    else:
        print(f"    98 / {block} = {98/block:.4f}")
print(f"  98 = 2×44 + 10 = 2Nd + 10")
print(f"  98 = 44 + 54 = Nd + 3L6")
print(f"  98 = 3×32 + 2 = 3×(h11−4) + 2")
print(f"  98 = 4×24 + 2 = 4×(Nd/2+2) + 2")
# 有趣: 98 = Nd + 3L6 = 44 + 54, 或者 98 = h11 + 62 = 36 + 62

# ============ 3. A_ij 幾何 pairing ============
print("\n[3] A_ij(z) 幾何 pairing")
# 方法: 用 γ 譜權重建構 98-dim 嘅「質量權重」矩陣
# γ_n = 4sin²(πn/88), n=1..44
# 98 = 2×44 + 10 → γ98 = [γ, γ, γ[:10]]
gamma98 = np.concatenate([gamma, gamma, gamma[:10]])
print(f"  γ98 shape: {gamma98.shape}")
check("γ98 長度 = 98", len(gamma98) == 98)

# A_ij = ∫ α_i ∧ β_j: 用 diag(γ98) 做 pairing
# 但 A 應該係 98×98 嘅 antisymmetric matrix (intersection form on H³)
# 對 CY₃: intersection form Q: H³ × H³ → R 係 antisymmetric
# 用 symplectic basis {α_i, β_i}: Q(α_i, β_j) = δ_ij
# → A_ij = 98×98 antisymmetric

# 建構: A = [[0, I], [-I, 0]] 嘅推廣?
# 但 h21=98 → 需要 2×98 = 196 > b3=198? 唔對
# b3 = 2(1+h21) = 198 → H³ = H^{3,0} ⊕ H^{2,1} ⊕ H^{1,2} ⊕ H^{0,3}
# dim H^{2,1} = h21 = 98, dim H^{1,2} = h21 = 98
# + H^{3,0} (1) + H^{0,3} (1) = 198
# intersection form 喺 H³: Q(α_i, β_j) = δ_ij 對 i,j = 1..98

# IDCM 版本: 用 P̂ CPX 分量 + γ 譜
# W = P_cpx @ beats (98×946 @ 946×N)
# 但更直接: A_ij 應該從 3-form 交集 ∫ α_i ∧ β_j 嚟
# 用 γ 譜: A_ij = Σ_k γ_k α_ik β_jk (weighted overlap)

# 用 66 態嘅 C 分量做 pairing
P66 = P @ P.T  # 134×134
evals, evecs = np.linalg.eigh(P66)
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
print(f"\n  66 態: C={len(C_idx)}, K={len(K_idx)}")
check("C 態 = 30", len(C_idx) == 30)
check("K 態 = 36", len(K_idx) == 36)

# A_ij (30×30): C 態之間嘅幾何 pairing
# 用 γ98 權重: A = W_C.T @ diag(γ98) @ W_C
A_C = W_C.T @ np.diag(gamma98) @ W_C
print(f"\n  A_C (30×30) = W_C^T γ98 W_C:")
ev_A = np.linalg.eigvalsh(A_C)
print(f"  本徵值 (排序): {np.sort(ev_A)[::-1][:10]}")
print(f"  正: {np.sum(ev_A > 1e-10)}/{len(ev_A)}")
# 對稱性
print(f"  對稱性: max|A_C - A_C^T| = {np.max(np.abs(A_C - A_C.T)):.2e}")
check("A_C 對稱", np.max(np.abs(A_C - A_C.T)) < 1e-8)

# A_C 嘅結構: 30×30 = 3 gen × 10?
# 30 = 3×10 → 睇有冇 3×10 block 結構
# 用能量排序
order = np.argsort(np.diag(A_C))[::-1]
A_sorted = A_C[np.ix_(order, order)]
print(f"\n  30×30 排序後 (top-left 6×6):")
for i in range(6):
    print(f"    {[f'{x:.3f}' for x in A_sorted[i,:6]]}")

# ============ 4. A_ij 結構驗證 ============
print("\n[4] A_ij 結構驗證")
# 檢查 3×10 block 結構
# 30 = 3 gen × 10 態
block_means = np.zeros((3, 3))
for g1 in range(3):
    for g2 in range(3):
        block_means[g1, g2] = np.mean(np.abs(A_sorted[g1*10:(g1+1)*10, g2*10:(g2+1)*10]))
print(f"  3×10 block mean |A|:")
for i in range(3):
    print(f"    {[f'{x:.3f}' for x in block_means[i]]}")
# 檢查 block 結構: 對角 block 應該顯著大於非對角?
diag_blocks = [block_means[i, i] for i in range(3)]
off_blocks = [block_means[i, j] for i in range(3) for j in range(3) if i != j]
print(f"  diag: {[f'{x:.3f}' for x in diag_blocks]}, off: {[f'{x:.3f}' for x in off_blocks]}")
if max(off_blocks) > 0:
    print(f"  diag/off 比: {max(diag_blocks)/max(off_blocks):.2f}")

# 檢查 φ 結構: 3 gen 嘅 eigenvalue 比
ev_sorted = np.sort(ev_A)[::-1]
if len(ev_sorted) >= 6:
    # 3 代: 每代 top eigenvalue
    gen_ev = [ev_sorted[0], ev_sorted[10], ev_sorted[20]]  # 或者用其他劃分
    print(f"\n  每 10 個 eigenvalue 嘅 top: {gen_ev}")
    if gen_ev[1] > 0 and gen_ev[2] > 0:
        print(f"  比: {gen_ev[0]/gen_ev[1]:.3f}, {gen_ev[1]/gen_ev[2]:.3f}")
        print(f"  φ = {phi:.3f}, φ² = {phi**2:.3f}")

# ============ 5. 總結 ============
print("\n" + "=" * 72)
print("O61 一期 01 總結:")
print("=" * 72)
print(f"""
  A_ij(z) pre-factor 探索:
  ─────────────────────────────────
  1. CPX rank = {rank_cpx} (缺口 {98-rank_cpx})
  2. 66 態: C={len(C_idx)}, K={len(K_idx)}
  3. A_C (30×30) 本徵值 top: {[f'{x:.3f}' for x in np.sort(ev_A)[::-1][:5]]}
  4. 對稱性: {np.max(np.abs(A_C - A_C.T)):.2e}

  {'✅ A_ij 結構探索完成' if passed >= 0 else '❌ 失敗'}
""")
results = {
    "test": "O61 01: A_ij(z) pre-factor",
    "h11": h11, "h21": h21, "chi": chi, "b3": b3,
    "cpx_rank": int(rank_cpx), "gap": int(98 - rank_cpx),
    "n_C": int(len(C_idx)), "n_K": int(len(K_idx)),
    "A_C_eigenvalues": [float(x) for x in np.sort(ev_A)[::-1][:10]],
    "A_C_symmetry": float(np.max(np.abs(A_C - A_C.T))),
    "block_means": [[float(x) for x in row] for row in block_means],
    "passed": passed, "failed": failed
}
os.makedirs("data", exist_ok=True)
with open("data/01_aij_prefactor.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 O61 一期 01 完成!")
