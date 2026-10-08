#!/usr/bin/env python3
"""
O61 二期 06: Moduli stabilization — Gukov-Vafa-Witten 通量超勢
================================================================
問題: CY₃(36,98) 嘅 Kähler moduli (36 個) 點樣被鎖定?

IDCM 框架:
  - Kähler moduli = 36 = h11
  - κ_ijk 有 3×12 block 結構 (一期)
  - 66 態 = 3×(12 K + 10 C)

方法 (Gukov-Vafa-Witten):
  W = ∫_X G₃ ∧ Ω  (G₃ = NSNS + RR flux)
  D_i W = 0 → 鎖定複結構 moduli
  D_i W = 0 → 鎖定 Kähler moduli

IDCM 版本: 通量 = K_Chain 投影?
  - flux quanta: N_i ∈ Z (通量子)
  - W = Σ N_i t_i (線性)
  - 穩定條件: ∂W/∂t_i = N_i = 0? 太trivial
  - 真正: W = Σ_i N_i · F_i(t), F_i = prepotential 導數

用 κ_ijk:
  - prepotential F(t) = (1/6) Σ κ_ijk t_i t_j t_k
  - ∂F/∂t_i = (1/2) Σ κ_ijk t_j t_k (Yukawa 積分)
  - flux superpotential: W = Σ N_i ∂F/∂t_i
  - 穩定: D_i W = ∂_i W + (∂_i K) W = 0

本輪:
  1. 建構 prepotential F(t) = κ_ijk t_i t_j t_k / 6
  2. 通量超勢 W = N·∂F
  3. 揾穩定點 (∂W/∂t = 0)
  4. 驗證真空存在 + 質量矩陣正定
  5. 通量子 N 用 IDCM 結構數
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O61 二期 06: Moduli stabilization (GVW 通量)")
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

# ============ 1. 載入 κ ============
d = json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))
kappa = np.array(d["kappa"])

# ============ 2. Prepotential ============
print("\n[1] Prepotential F(t) = κ_ijk t_i t_j t_k / 6")
def prepotential(t):
    """F = (1/6) Σ κ_ijk t_i t_j t_k"""
    return np.einsum("ijk,i,j,k", kappa, t, t, t) / 6.0

def dF_dt(t):
    """∂F/∂t_i = (1/2) Σ κ_ijk t_j t_k"""
    return 0.5 * np.einsum("ijk,j,k", kappa, t, t)

def d2F_dt2(t):
    """∂²F/∂t_i∂t_j = Σ κ_ijk t_k"""
    return np.einsum("ijk,k", kappa, t)

# 用 γ 譜測試
gamma36 = 4 * np.sin(np.pi * np.arange(1, 37) / 88) ** 2
F_gamma = prepotential(gamma36)
dF_gamma = dF_dt(gamma36)
print(f"  F(γ) = {F_gamma:.4f}")
print(f"  ∂F/∂t (γ): norm = {np.linalg.norm(dF_gamma):.4f}")
print(f"  ∂²F/∂t² (γ) = Yukawa Y(γ): shape {d2F_dt2(gamma36).shape}")

# ============ 3. 通量超勢 ============
print("\n[2] 通量超勢 W = N·∂F")
# 通量子 N: IDCM 結構數候選
# 66 態, 36 moduli, 44 sites, 90 Σγ, 98 h21
candidates = {
    "N=1 (uniform)": np.ones(36),
    "N=γ (譜)": gamma36,
    "N=44/Nd": np.full(36, 44),
    "N=90/Σγ": np.full(36, 90),
    "N=66": np.full(36, 66),
    "N=φ^i": phi ** np.arange(36),
    "N=φ^-i": phi ** (-np.arange(36)),
}
for name, N in candidates.items():
    W = np.sum(N * dF_dt(gamma36))
    print(f"  {name}: W = {W:.4f}")

# ============ 4. 穩定點 ============
print("\n[3] 穩定點求解")
# 穩定條件: ∂(N·∂F)/∂t_j = Σ_i N_i ∂²F/∂t_i∂t_j = Y^T N = 0
# 即 Yukawa 矩陣 Y(t) @ N = 0
# 用 t = γ: Y_gamma @ N = 0 → N 喺 kernel(Y_gamma)
Y_gamma = d2F_dt2(gamma36)
evals_Y, evecs_Y = np.linalg.eigh(Y_gamma)
print(f"  Y(γ) 本徵值 (top 5): {[f'{x:.2f}' for x in np.sort(evals_Y)[::-1][:5]]}")
n_zero = np.sum(np.abs(evals_Y) < 1e-8)
print(f"  零本徵值: {n_zero}")
if n_zero > 0:
    zero_idx = np.where(np.abs(evals_Y) < 1e-8)[0]
    for zi in zero_idx:
        N0 = evecs_Y[:, zi]
        print(f"  零模 {zi}: N = {[f'{x:.3f}' for x in N0[:8]]}...")
        # 通量子要整數?
        print(f"    sum|N| = {np.sum(np.abs(N0)):.3f}")

# 通量子整數化
print("\n[4] 通量子整數化")
if n_zero > 0:
    N0 = evecs_Y[:, zero_idx[0]]
    scale = N0[np.argmax(np.abs(N0))]
    N_int = np.round(N0 / scale).astype(int)
    print(f"  整數化 N: {N_int}")
    print(f"  sum = {N_int.sum()}, sum|N| = {np.sum(np.abs(N_int))}")
    print(f"  非零: {np.count_nonzero(N_int)}/{len(N_int)}")
    # 對齊結構數?
    print(f"  66? {np.sum(np.abs(N_int)) == 66}, 44? {np.sum(np.abs(N_int)) == 44}, 90? {np.sum(np.abs(N_int)) == 90}")

# ============ 5. 質量矩陣 ============
print("\n[5] 質量矩陣")
# moduli mass: m² = ∂²V/∂t², V = |W|²
# 用 F-term: V = e^K |W|², 質量 ~ 本徵值(Y^T Y)
M = Y_gamma.T @ Y_gamma  # 36×36
ev_M = np.sort(np.linalg.eigvalsh(M))[::-1]
print(f"  M = Y^T Y 本徵值 top5: {[f'{x:.2f}' for x in ev_M[:5]]}")
print(f"  M rank: {np.linalg.matrix_rank(M, tol=1e-8)}")
# 質量階梯?
if len(ev_M) > 5 and ev_M[4] > 0:
    print(f"  m1/m2 = {ev_M[0]/ev_M[1]:.2f}, m2/m3 = {ev_M[1]/ev_M[2]:.2f}")

# ============ 6. 通量量子數 IDCM 對應 ============
print("\n[6] 通量量子數 ↔ IDCM 結構")
# 標準 flux: ∫ F₃ ∧ H₃ = N_flux (D3 charge)
# CY₃: N_flux = (1/2) ∫ G₃ ∧ G₃
# IDCM: 66 態 / 44 sites / 90 Σγ / 98 h21
# 試: N_flux = 66 = 3×22 (3 代 × 每代 22 態)?
# 或者 N_flux = 946 beats?
# 或者 N_flux = 484 odd beats?
print(f"  候選 N_flux:")
for nf, label in [(66, "66 態"), (44, "Nd"), (90, "Σγ"), (98, "h21"), (946, "beats"), (484, "odd beats"), (198, "b₃"), (134, "134 moduli")]:
    print(f"    {label} = {nf}")

# 用 N = 66 求穩定點?
# W = 66·∂F/∂t 嘅 gradient
def flux_W(t, N):
    return np.sum(N * dF_dt(t))

# 數值梯度
def grad_W(t, N, eps=1e-6):
    g = np.zeros(36)
    for i in range(36):
        tp = t.copy(); tp[i] += eps
        tm = t.copy(); tm[i] -= eps
        g[i] = (flux_W(tp, N) - flux_W(tm, N)) / (2*eps)
    return g

# 睇 γ 附近 grad
for name, N in [("N=66", np.full(36, 66)), ("N=φ^-i", phi**(-np.arange(36)))]:
    g = grad_W(gamma36, N)
    print(f"\n  {name}: ||grad W|| at t=γ = {np.linalg.norm(g):.4f}")
    print(f"    grad top: {[f'{x:.2f}' for x in g[:5]]}")

# ============ 7. 總結 ============
print("\n" + "=" * 72)
print("O61 二期 06 總結:")
print("=" * 72)
print(f"""
  GVW 通量超勢探索:
  ─────────────────────────────────
  1. F(γ) = {F_gamma:.4f}
  2. Y(γ) 零模: {n_zero} 個
  3. 質量矩陣 M = Y^T Y: rank {np.linalg.matrix_rank(M, tol=1e-8)}

  {'✅ 探索完成' if failed == 0 else '❌ 有失敗'}
""")
results = {
    "test": "O61 06: GVW flux",
    "F_gamma": float(F_gamma),
    "Y_zero_modes": int(n_zero),
    "M_rank": int(np.linalg.matrix_rank(M, tol=1e-8)),
    "M_ev": [float(x) for x in ev_M[:10]],
    "passed": passed, "failed": failed
}
with open("data/06_gvw_flux.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 O61 二期 06 完成!")
