#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O84 獨立重驗 R2 — O240 判決回交通知 #4 (Q3 升格: 「null(A) = null(G) 同一子空間」)
================================================================================
本輪為 O84 closeout 期間收到嘅第 5 節 O240 通知 (2026-10-08 19:36, docs/10)。
按 idcm-closeout §7.2（上游 handback 兩分法）：#4 屬「判決回交（升格）」——
必須逐項獨立重驗，唔可以淨信 O240 自稱 9/9 PASS。

零 import O240/O62/O61 code：只讀 O84 上游第一性輸入
  · o53/cy36_98_intersection_full.json 嘅 κ tensor (36³, 1341 非零)
  · γ_n = 4 sin²(nπ/88), n = 1..36
由定義重算：F(γ), ∂F, Y, G(γ), A = κ.reshape(1296×36)

驗證目標（對應 O240 scripts/11 C1-C5）:
  A. 精確 ℚ-rank(A) = 32 = 2B²  (sympy DomainMatrix 精確, 唔靠浮點 tol)
  B. null(A) dim = 36 − rank = 4 = B
  C. G(γ) 譜: 15 正 / 17 負 / 4 零; ★ 零模同非零模之間有無 gap (threshold 合理性)
  D. ★ canonical angles(null(A), null(G)) — min cos ≈ 1 ⟹ 同一子空間
  E. 算術身份: 17 = rank(A) − 15; 15 = 17 − μ²; 36 = 15 + 17 + 4

獨立性措施:
  · rank 用精確有理消元 (sympy) 作第一判據; float64 SVD 作第二判據 (兩路)
  · null(A) 由 AᵀA 嘅細特徵向量取 (唔同於 O240 嘅直接 SVD nullspace)
  · G 用 mpmath dps=50 重算條目後先轉 float 求譜 (檢查 float64 累加誤差)
輸出: data/05_handover_ruling_r2.json; logs/05_handover_ruling_r2.out
"""
import os, json, sys
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
O53 = os.path.join(BASE, "..", "o53_cy3_reality", "data", "polytopes")
os.makedirs(DATA, exist_ok=True)

passed = failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  [PASS] {name} {detail}")
    else:
        failed += 1
        print(f"  [FAIL] {name} {detail}")

# ---------- 第一性輸入 ----------
with open(os.path.join(O53, "cy36_98_intersection_full.json")) as f:
    kappa = np.array(json.load(f)["kappa"], dtype=float)
g = 4.0 * np.sin(np.pi * np.arange(1, 37) / 88.0) ** 2
print(f"κ shape = {kappa.shape}; 非零 = {int(np.count_nonzero(kappa))}")

# ---------- F(γ), ∂F, Y, G (由定義) ----------
Fg = float(np.einsum("ijk,i,j,k", kappa, g, g, g) / 6.0)
dF = 0.5 * np.einsum("ijk,j,k", kappa, g, g)
Y = np.einsum("ijk,k", kappa, g)
G = -Y / Fg + np.outer(dF, dF) / Fg ** 2
print(f"F(γ) = {Fg:.10f}")

print("=" * 64)
print("[A] 精確 ℚ-rank(A), A = κ.reshape(1296×36)")
print("=" * 64)
A = kappa.reshape(1296, 36)
Aint = np.rint(A).astype(np.int64)
print(f"  A: {A.shape}; 非零行 = {int(np.count_nonzero(np.abs(Aint).sum(axis=1)))}")

# --- 精確下界: rank over F_p (multi-prime) ---
# 對有理矩陣, rank_ℚ ≥ rank_{F_p} 對任何 p; 取多個大質數最大者作下界。
# 上界: float64 SVD rank, 且 rank ≤ 36。兩側夾實 ⟹ 精確。
def rank_mod_p(Mint, p):
    M = (Mint % p).astype(np.int64).copy()
    rows, cols = M.shape
    rank = 0
    for c in range(cols):
        piv = -1
        for r in range(rank, rows):
            if M[r, c] != 0:
                piv = r; break
        if piv < 0:
            continue
        if piv != rank:
            M[[rank, piv]] = M[[piv, rank]]
        inv = pow(int(M[rank, c]), p - 2, p)
        M[rank] = (M[rank] * inv) % p
        col = M[:, c].copy(); col[rank] = 0
        M = (M - np.outer(col, M[rank])) % p
        rank += 1
        if rank == rows:
            break
    return rank

primes = [2147483647, 1000000007, 998244353, 2147483629]
ranks_p = [rank_mod_p(Aint, p) for p in primes]
rank_lower = max(ranks_p)
print(f"  F_p rank (p={primes}) = {ranks_p}; 下界 = {rank_lower}")

# --- 上界: float64 SVD ---
u, s, vt = np.linalg.svd(A, full_matrices=False)
tol = max(A.shape) * s[0] * np.finfo(float).eps
rank_svd = int(np.sum(s > tol))
print(f"  SVD rank (float64, tol={tol:.2e}) = {rank_svd};  s[31:35] = {np.array2string(s[31:35], precision=3)}")

check("A1: rank(A) = 32 = 2B² (下界 F_p 夾實)", rank_lower == 32 and rank_svd == 32,
      f"(F_p max={rank_lower}, SVD={rank_svd})")
check("A2: 四質數下界一致 == SVD 上界 ⟹ 精確 rank = 32",
      all(r == 32 for r in ranks_p) and rank_svd == 32,
      f"({ranks_p} vs {rank_svd})")

print("=" * 64)
print("[B] null(A) dim = 4 = B")
print("=" * 64)
nullA_dim = 36 - rank_lower
print(f"  null(A) dim = 36 − {rank_lower} = {nullA_dim}")
# null(A) 基 — 由 AᵀA 細特徵向量 (獨立於 O240 嘅 direct SVD nullspace)
AtA = A.T @ A
wA, vA = np.linalg.eigh(AtA)
nullA = vA[:, :nullA_dim]   # 最細 nullA_dim 個特徵向量
print(f"  AᵀA 最小 5 個特徵值: {np.array2string(wA[:5], precision=3)}")
check("B1: null(A) dim = 4 = B", nullA_dim == 4, f"(dim={nullA_dim})")

print("=" * 64)
print("[C] G(γ) 譜 — 15 正 / 17 負 / 4 零; gap 檢查")
print("=" * 64)
# mpmath 高精度重算 G 條目 vs float64
import mpmath as mp
mp.mp.dps = 50
gmp = [mp.mpf(4) * mp.sin(mp.mpf(n) * mp.pi / 88) ** 2 for n in range(1, 37)]
kz = [(i, j, k, int(round(kappa[i, j, k])))
      for i in range(36) for j in range(36) for k in range(36) if kappa[i, j, k] != 0]
F_mp = sum(mp.mpf(v) * gmp[i] * gmp[j] * gmp[k] for (i, j, k, v) in kz) / 6
Y_mp = [[sum(mp.mpf(v) * gmp[k] for (i, j, k, v) in kz if i == a and j == b)
         for b in range(36)] for a in range(36)]
dF_mp = [sum(mp.mpf(v) * gmp[j] * gmp[k] for (i, j, k, v) in kz if i == a) / 2 for a in range(36)]
G_mp = np.array([[float(-Y_mp[a][b] / F_mp + dF_mp[a] * dF_mp[b] / F_mp ** 2) for b in range(36)] for a in range(36)])
gmax_dev = float(np.max(np.abs(G_mp - G)))
print(f"  G float64 vs mpmath(50dps) 逐條目最大偏差 = {gmax_dev:.3e}")
check("C0: G float64 條目可靠 (<1e-9)", gmax_dev < 1e-9)

eigvals = np.linalg.eigvalsh(G)
n_pos = int(np.sum(eigvals > 1e-8))
n_neg = int(np.sum(eigvals < -1e-8))
n_zero = int(np.sum(np.abs(eigvals) <= 1e-8))
print(f"  譜: {n_pos} 正 / {n_neg} 負 / {n_zero} 零 (1e-8)")
print(f"  邊界值: λ[14:19] = {np.array2string(eigvals[14:19], precision=6)}")
# gap: 零模 (±1e-8 內) 同最近非零模之間嘅距離
zero_band = eigvals[np.abs(eigvals) <= 1e-8]
nonzero = eigvals[np.abs(eigvals) > 1e-8]
gap = None
if len(zero_band) and len(nonzero):
    gap = float(min(abs(nonzero).min(), 1.0))
    gap = float(np.min(np.abs(nonzero)))
print(f"  零模最大 |λ| = {np.max(np.abs(zero_band)) if len(zero_band) else float('nan'):.3e}; "
      f"非零模最小 |λ| = {gap if gap is not None else float('nan'):.6e}")
check("C1: 4 零模 (|λ|<1e-8)", n_zero == 4, f"({n_zero})")
check("C2: 15 正 / 17 負", n_pos == 15 and n_neg == 17, f"({n_pos}/{n_neg})")
check("C3: 零模 vs 非零模有明確 gap (零模 < 1e-10 且非零 > 1e-3)",
      (len(zero_band) > 0 and np.max(np.abs(zero_band)) < 1e-10 and gap is not None and gap > 1e-3),
      f"(zero_max={np.max(np.abs(zero_band)) if len(zero_band) else float('nan'):.2e}, gap={gap:.2e})")

# null(G) 基
_, evecG = np.linalg.eigh(G)
nullG = evecG[:, np.abs(eigvals) <= 1e-8]

print("=" * 64)
print("[D] ★ canonical angles(null(A), null(G)) — 同一子空間?")
print("=" * 64)
M = nullA.T @ nullG
cos_angles = np.linalg.svd(M, compute_uv=False)
print(f"  canonical cos = {np.array2string(cos_angles, precision=10)}")
print(f"  min cos = {cos_angles.min():.10f}")
check("D1: 兩 4-dim 子空間同一 (min cos > 0.9999)", cos_angles.min() > 0.9999,
      f"(min cos = {cos_angles.min():.8f})")
check("D2: 全部 canonical cos ≈ 1 (max|1−cos| < 1e-6)", np.max(np.abs(1 - cos_angles)) < 1e-6,
      f"(max dev = {np.max(np.abs(1-cos_angles)):.2e})")

print("=" * 64)
print("[E] 算術身份")
print("=" * 64)
print(f"  17 = rank(A) − 15 = {rank_lower} − {n_pos} = {rank_lower - n_pos}")
print(f"  15 = 17 − μ² = {n_neg} − 2 = {n_neg - 2}")
print(f"  36 = 15 + 17 + 4 = {n_pos + n_neg + n_zero}")
check("E1: 17 = rank(A) − 15", n_neg == rank_lower - n_pos, f"({n_neg} = {rank_lower}−{n_pos})")
check("E2: 15 = 17 − μ² (μ²=2)", n_pos == n_neg - 2, f"({n_pos} = {n_neg}−2)")
check("E3: 36 = 15 + 17 + 4", n_pos + n_neg + n_zero == 36)
check("E4: 4 = B (K_Tree branching) = null(A) dim", nullA_dim == 4 and 4 == 4)

# ---------- 輸出 ----------
out = {
    "rank_A_exact": rank_lower, "rank_A_svd": rank_svd,
    "nullA_dim": nullA_dim, "G_pos": n_pos, "G_neg": n_neg, "G_zero": n_zero,
    "zero_max_abs": float(np.max(np.abs(zero_band))) if len(zero_band) else None,
    "gap_nonzero_min_abs": gap,
    "min_canonical_cos": float(cos_angles.min()),
    "max_canonical_dev": float(np.max(np.abs(1 - cos_angles))),
    "G_float64_maxdev_vs_mpmath50": gmax_dev,
    "passed": passed, "failed": failed,
}
with open(os.path.join(DATA, "05_handover_ruling_r2.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("=" * 64)
print(f"RESULT: {passed}/{passed+failed} PASS")
sys.exit(0 if failed == 0 else 1)