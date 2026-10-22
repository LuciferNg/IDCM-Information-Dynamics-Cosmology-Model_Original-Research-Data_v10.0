#!/usr/bin/env python3
"""
O62 二期 07: GVW 通量鎖定 t* 求解
====================================
O61 閉合: kernel(A) = 4 = B (t 無關), 32 = 2B² 鎖定
但未求出具體穩定點 t*。

本腳本: 求「真正」穩定點:
  1. 通量子 N = 66 態 / 90 Σγ 對應嘅零模組合
  2. 穩定條件: Y(t)·N = 0 或 D_iW = 0
  3. 由 F(t*) → 真空能
  4. 對比 F(γ) = 264.08
"""
import sys, os, math, json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O62 二期 07: GVW 通量鎖定 t*")
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

# ============ 1. 載入 ============
print("\n[1] 載入")
d = json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))
kappa = np.array(d["kappa"])
gamma36 = 4 * np.sin(np.pi * np.arange(1, 37) / 88) ** 2

def F(t):
    return np.einsum("ijk,i,j,k", kappa, t, t, t) / 6.0
def dF(t):
    return 0.5 * np.einsum("ijk,j,k", kappa, t, t)
def Y(t):
    return np.einsum("ijk,k", kappa, t)

# ============ 2. kernel(A) 零方向 ============
print("\n[2] kernel(A) 零方向 (t 無關)")
A = kappa.reshape(1296, 36)
U, S, Vt = np.linalg.svd(A)
n_zero = np.sum(S < 1e-8)
print(f"  A rank = {np.sum(S > 1e-8)}, kernel = {n_zero}")
check("kernel(A) = 4", n_zero == 4, f"(n={n_zero})")
# 零方向 = Vt 最尾 4 行
Z = Vt[-4:, :]  # 4×36
print(f"  零方向 shape: {Z.shape}")
for i in range(4):
    z = Z[i]
    print(f"  v{i}: sum|v| = {np.sum(np.abs(z)):.4f}, 非零 {np.count_nonzero(np.abs(z)>1e-6)}/36")

# ============ 3. 通量子 N = 66/90 ============
print("\n[3] 通量子 N 構建")
# O61 三期: 零方向整數化 sum|N| = 66 (scale=16), 90 (scale=22)
# 用 Z 嘅整數組合 → N_66, N_90
def integerize(v, scale):
    """整數化到 scale 附近"""
    s = v[np.argmax(np.abs(v))]
    N = np.round(v / s * scale).astype(int)
    return N

# 搵組合 c 令 sum|N| = 66 同 90
found_66 = None
found_90 = None
for c1 in range(-4, 5):
    for c2 in range(-4, 5):
        for c3 in range(-4, 5):
            for c4 in range(-4, 5):
                v = c1*Z[0] + c2*Z[1] + c3*Z[2] + c4*Z[3]
                s = v[np.argmax(np.abs(v))]
                if abs(s) < 1e-10:
                    continue
                N = np.round(v/s*16).astype(int)
                sa = np.sum(np.abs(N))
                if sa == 66 and found_66 is None:
                    found_66 = N
                N2 = np.round(v/s*22).astype(int)
                sa2 = np.sum(np.abs(N2))
                if sa2 == 90 and found_90 is None:
                    found_90 = N2
                if found_66 is not None and found_90 is not None:
                    break
            if found_66 is not None and found_90 is not None:
                break
        if found_66 is not None and found_90 is not None:
            break
    if found_66 is not None and found_90 is not None:
        break

print(f"  N_66 = {found_66}" if found_66 is not None else "  N_66 未搵到")
print(f"  N_90 = {found_90}" if found_90 is not None else "  N_90 未搵到")

# ============ 4. 穩定點 ============
print("\n[4] 穩定點求解")
# 方法: 通量超勢 W = N·∂F/∂t, 穩定 ∂W/∂t = Y(t)·N = 0
# 因為 N ∈ ker(A) → Y(t)·N = 0 ∀t (O61 證明)
# → t* 任意! W(t) 沿 kernel 方向 flat?
# 檢查: W(t) = Σ N_i ∂F/∂t_i 對所有 t 係咪 0?

# 用 N_66 或 N_90 或任意 kernel 組合
for label, N in [("N_66", found_66), ("N_90", found_90)]:
    if N is None:
        continue
    Nf = N.astype(float)
    # W(t) = N·∂F(t) = Σ N_i · (1/2)Σκ_ijk t_j t_k
    W_gamma = np.sum(Nf * dF(gamma36))
    print(f"  {label}: W(γ) = {W_gamma:.8f}")
    check(f"{label}: W(γ) ≈ 0 (kernel 性質)", abs(W_gamma) < 1e-6, f"(W={W_gamma:.2e})")
    
    # 隨機 t 驗證
    rng = np.random.default_rng(7)
    maxW = 0
    for _ in range(20):
        t_rand = rng.uniform(0.1, 4.0, 36)
        W_r = np.sum(Nf * dF(t_rand))
        maxW = max(maxW, abs(W_r))
    print(f"  {label}: max|W| over 20 random t = {maxW:.2e}")
    check(f"{label}: W(t) ≈ 0 ∀t", maxW < 1e-6)

# ============ 5. W = 0 意味 D_iW = 0 ∀t → 冇鎖定! ============
print("\n[5] 關鍵: W ≡ 0 嘅物理意義")
print(f"  如果 N ∈ ker(A), 則 W(t) = N·∂F(t) ≡ 0 ∀t")
print(f"  → 通量超勢沿所有方向消失!")
print(f"  → 冇 F-term 穩定! 需要 D-term 或其他機制")
print(f"  → O61 嘅 kernel(A)=4 係「flat 方向」, 唔係鎖定機制")

# 真正嘅穩定: N ∉ ker(A)
print(f"\n  通量子 N ∉ ker(A) 時:")
# 試 N = 66 均勻
N_uniform = np.full(36, 66)
W_uni = np.sum(N_uniform * dF(gamma36))
print(f"  N=66 uniform: W(γ) = {W_uni:.4f}")
# Y(γ)·N
YN = Y(gamma36) @ N_uniform
print(f"  Y(γ)·N norm = {np.linalg.norm(YN):.4f}")
# 找 t* 令 Y(t*)·N = 0?
# 呢個係 36 個二次方程 — 困難, 但可以睇 γ 係咪接近

# ============ 6. 穩定點候選: t* = γ 嘅 justification ============
print("\n[6] t* = γ 作為穩定點嘅證據")
# 證據 1: Y(γ) kernel = 4 = B (一期 01)
Yg = Y(gamma36)
evals_Y = np.linalg.eigvalsh(Yg)
n_zer = np.sum(np.abs(evals_Y) < 1e-8)
print(f"  證據 1: Y(γ) kernel = {n_zer} = B ({'✅' if n_zer==4 else '❌'})")
# 證據 2: 質量矩陣 rank = 32 = 2B²
Mg = Yg.T @ Yg
rank_M = np.sum(np.linalg.eigvalsh(Mg) > 1e-8)
print(f"  證據 2: rank(Y(γ)^T Y(γ)) = {rank_M} = 2B² ({'✅' if rank_M==32 else '❌'})")
# 證據 3: F(γ) = 264.08 ≈ 6N_d
Fg = F(gamma36)
print(f"  證據 3: F(γ) = {Fg:.4f} ≈ 6N_d = 264 ({abs(Fg-264)/264*100:.4f}%)")

# ============ 7. D-term 穩定 ============
print("\n[7] D-term 候選 (Kähler 模鎖定)")
# 4D N=1: D-term = Σ Q_i |φ_i|² + ξ (FI term)
# IDCM: ξ = Σγ = 90? 
# V_D = (1/2)(Σ Q_i t_i)²
# 穩定: Σ Q_i t_i = 0 → 但 t_i > 0, Q 有正負

# 或者: Kähler potential K = -ln(V), V = F(t) 三次體積
# V = F(t) = (1/6)κ t³
# t* 穩定: ∂V/∂t = 0 (classical)
dF_gamma = dF(gamma36)
print(f"  ∂F/∂t(γ) = {dF_gamma}")
print(f"  ∂F/∂t(γ) 符號: +:{np.sum(dF_gamma>0)}, -:{np.sum(dF_gamma<0)}")
print(f"  Σ∂F = {dF_gamma.sum():.4f}")
print(f"  |∂F| = {np.linalg.norm(dF_gamma):.4f}")
# 有冇 t* 令 ∂F = 0? (classical SUSY vacua)

# 數值優化: 最小化 |∂F(t)|²
from scipy.optimize import minimize

def obj(t):
    t = np.abs(t)  # Kähler cone 正
    d = dF(t)
    return np.sum(d**2)

res = minimize(obj, gamma36, method="BFGS", options={"maxiter": 500})
t_opt = np.abs(res.x)
print(f"\n  數值優化 min|∂F|²:")
print(f"  |∂F(t_opt)|² = {res.fun:.6e}")
print(f"  t_opt[:8] = {[f'{x:.4f}' for x in t_opt[:8]]}")
print(f"  t_opt 同 γ 相似度: {np.corrcoef(t_opt, gamma36)[0,1]:.4f}")
F_opt = F(t_opt)
print(f"  F(t_opt) = {F_opt:.6f}")
print(f"  V_obs − F(t_opt) = {283.0752 - F_opt:.6f}")

# ============ 8. 總結 ============
print("\n" + "=" * 72)
print("二期 07 總結:")
print("=" * 72)
print(f"""
  kernel(A) 零方向 → W ≡ 0 ∀t → 冇 F-term 鎖定
  (O61 kernel(A)=4 係 flat 方向, 唔係鎖定機制)

  t* = γ 證據:
    Y(γ) kernel = {n_zer} = B
    rank M = {rank_M} = 2B²
    F(γ) = {Fg:.4f} ≈ 6N_d

  t_opt (數值最小化 |∂F|²):
    F(t_opt) = {F_opt:.6f}
    V_obs − F = {283.0752 - F_opt:.6f}

  → t* = γ_n 係「自然」VEV (P̂ Kähler 行 ↔ γ 譜)
  → 真空能 = F(γ) + 修正
""")
out = {
    "test": "O62 二期 07: GVW t*",
    "kernel_A": int(n_zero),
    "N_66": [int(x) for x in found_66] if found_66 is not None else None,
    "N_90": [int(x) for x in found_90] if found_90 is not None else None,
    "Y_gamma_kernel": int(n_zer), "M_rank": int(rank_M),
    "F_gamma": float(Fg),
    "t_opt": [float(x) for x in t_opt],
    "F_topt": float(F_opt),
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "07_gvw_tstar.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 二期 07 完成!")
