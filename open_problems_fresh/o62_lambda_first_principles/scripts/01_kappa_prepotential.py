#!/usr/bin/env python3
"""
O62 一期 01: 真 κ prepotential 掃描 — 搵「穩定點候選」
========================================================
目標: V_Λ 第一性原理 — 由真 CY₃(36,98) 交集數 κ_ijk 出發,
     prepotential F(t) = (1/6)κ_ijk t_i t_j t_k,
     GVW 通量超勢 W = N·∂F, 穩定條件 ∂W/∂t = Y(t)·N = 0,
     搵出自然 Kähler 參數方案下嘅穩定點候選, 再由 F(t*) 計算真空能。

關鍵問題:
  1. 邊個自然 t 方案令 Y(t) 有 kernel? (kernel = 通量零模 N)
  2. 該 t 下 F(t) = ? ∂F/∂t = ? → 真空能 V_Λ 候選
  3. V₁₀ + 44γ₆ = 282.9706 會唔會自動出現?

自然 t 方案 (全部零參數):
  γ_n (K_Chain 諧波), φ^(±i), 1/t_i, t_i=i, Lucas, Fibonacci...
"""
import sys, os, math, json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O62 一期 01: 真 κ prepotential 掃描")
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

# ============ 1. 載入真 κ ============
print("\n[1] 真 κ (CYTools intersection)")
d = json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))
kappa = np.array(d["kappa"])
print(f"  κ shape: {kappa.shape}, 非零: {np.count_nonzero(kappa)}")
print(f"  κ range: [{kappa.min()}, {kappa.max()}]")

# ============ 2. Prepotential 工具 ============
print("\n[2] Prepotential 工具")
def F(t):
    """F = (1/6) Σ κ_ijk t_i t_j t_k"""
    return np.einsum("ijk,i,j,k", kappa, t, t, t) / 6.0

def dF(t):
    """∂F/∂t_i = (1/2) Σ κ_ijk t_j t_k"""
    return 0.5 * np.einsum("ijk,j,k", kappa, t, t)

def Y(t):
    """Yukawa Y_ij = ∂²F/∂t_i∂t_j = Σ κ_ijk t_k"""
    return np.einsum("ijk,k", kappa, t)

# ============ 3. 自然 t 方案 ============
print("\n[3] 自然 Kähler 參數方案掃描")
gamma36 = 4 * np.sin(np.pi * np.arange(1, 37) / 88) ** 2
# Lucas / Fibonacci
L = [2, 1]
for i in range(2, 40):
    L.append(L[i-1] + L[i-2])
F_ = [1, 1]
for i in range(2, 40):
    F_.append(F_[i-1] + F_[i-2])

schemes = {
    "gamma_n (γ1..γ36)": gamma36,
    "gamma_36..1 (反向)": gamma36[::-1],
    "phi^(-i)": phi ** (-np.arange(36)),
    "phi^(i-1)": phi ** (np.arange(36)),
    "phi^(35-i)": phi ** (35 - np.arange(36)),
    "phi^(-i-1)": phi ** (-(np.arange(36)+1)),
    "1/(i+1)": 1.0 / (np.arange(36) + 1),
    "1/(i+1)^2": 1.0 / (np.arange(36) + 1)**2,
    "Lucas L_(i+2)": np.array(L[2:38], dtype=float),
    "Fib F_(i+2)": np.array(F_[2:38], dtype=float),
    "t=i+1": np.arange(1, 37, dtype=float),
    "t=1 (uniform)": np.ones(36),
    "2^(-i)": 2.0 ** (-np.arange(36)),
    "sin(π(i+1)/44)": np.sin(np.pi * np.arange(1, 37) / 44),
    "gamma^2": gamma36**2,
    "sqrt(gamma)": np.sqrt(gamma36),
}

V_obs = 283.0752  # ln(1/ρ_Λ), ρ_Λ = 1.1535e-123 M_pl⁴
V10 = L[10]*phi + L[9]
g6 = 4*math.sin(6*math.pi/88)**2
V_target = V10 + 44*g6
print(f"  V_obs = {V_obs:.4f}, V₁₀+44γ₆ = {V_target:.4f}")

results = []
for name, t in schemes.items():
    t = t.astype(float)
    Fval = F(t)
    dFv = dF(t)
    Ymat = Y(t)
    # Yukawa kernel (零本徵值數)
    evals = np.linalg.eigvalsh(Ymat)
    n_zero = np.sum(np.abs(evals) < 1e-8)
    # 質量矩陣 Y^T Y
    Mt = Ymat.T @ Ymat
    ev_M = np.sort(np.linalg.eigvalsh(Mt))[::-1]
    rank_M = np.sum(ev_M > 1e-8)
    # 真空能候選: e^-F, e^-∂F·1, ln(1/F)
    results.append({
        "scheme": name, "F": float(Fval),
        "dF_norm": float(np.linalg.norm(dFv)),
        "dF_sum": float(dFv.sum()),
        "Y_kernel": int(n_zero), "M_rank": int(rank_M),
        "M_top5": [float(x) for x in ev_M[:5]],
        "ln_F": float(math.log(abs(Fval))) if Fval != 0 else None,
    })
    print(f"  {name:22s} F={Fval:12.4f} |∂F|={np.linalg.norm(dFv):10.4f} "
          f"Σ∂F={dFv.sum():10.4f} Yker={n_zero} Mrank={rank_M}")

# ============ 4. 重點: 邊啲 t 令 Y(t) 有 kernel? ============
print("\n[4] Yukawa kernel 分析 (kernel = 通量零模 N)")
print("  O61: kernel(A) = 4 係 t 無關 (Σκ_ijk v_k = 0)")
print("  但 kernel(Y(t)) 依賴 t:")
for r in results:
    if r["Y_kernel"] > 0:
        print(f"    {r['scheme']}: kernel(Y) = {r['Y_kernel']}, F = {r['F']:.4f}")

# ============ 5. F(t) 有冇接近 V 目標? ============
print("\n[5] F(t) vs V_Λ 目標")
print(f"  V₁₀ = {V10:.4f}, V₁₀+44γ₆ = {V_target:.4f}, V_obs = {V_obs:.4f}")
print(f"  搜索: F(t) ≈ 275/283? (1-6 個數量級內)")
for r in sorted(results, key=lambda r: abs(math.log10(abs(r["F"])) - math.log10(V_target))):
    ratio = abs(r["F"]) / V_target
    print(f"    {r['scheme']:22s} F={r['F']:14.6f}  F/V_target={ratio:10.2e}  ln|F|={math.log(abs(r['F'])) if r['F'] else 0:10.4f}")

# ============ 6. 關鍵測試: t* = φ^(-i) 或 γ 有冇 kernel = 通量解? ============
print("\n[6] 穩定點求解: Y(t)·N = 0")
# 對每個有 kernel 嘅 t, 攞零模 N, 驗證 66/90 通量子對齊
for r in results:
    if r["Y_kernel"] == 0:
        continue
    name = r["scheme"]
    t = schemes[name].astype(float)
    Ymat = Y(t)
    evals, evecs = np.linalg.eigh(Ymat)
    zero_idx = np.where(np.abs(evals) < 1e-8)[0]
    for zi in zero_idx:
        N0 = evecs[:, zi]
        # 整數化: scale 到最大分量
        s = N0[np.argmax(np.abs(N0))]
        N_int = np.round(N0 / s).astype(int)
        sum_abs = np.sum(np.abs(N_int))
        print(f"  {name}: 零模 sum|N| = {sum_abs} (66? {sum_abs==66}, 90? {sum_abs==90}, 44? {sum_abs==44})")

# ============ 7. 總結 ============
print("\n" + "=" * 72)
print("一期 01 總結:")
print("=" * 72)
print(f"""
  κ prepotential 掃描完成:
  - {len(schemes)} 個自然 t 方案
  - 每個 F(t), ∂F, Y(t) kernel, 質量矩陣 rank 已記錄

  關鍵發現:
  - kernel(Y(t)) 依賴 t (同 O61 誠實修正一致)
  - F(t) 數量級: 邊啲 t 方案嘅 F 接近 V_Λ ≈ 283?
  - 零模 N 嘅整數化 sum|N| 對齊 66/90?

  → 下一步 (一期 02): P̂ 奇異值譜真空能 + 二期 GVW 鎖定
""")

out = {
    "test": "O62 一期 01: κ prepotential 掃描",
    "schemes": results,
    "V_obs": V_obs, "V10": float(V10), "V_target": float(V_target),
    "kappa_nnz": int(np.count_nonzero(kappa)),
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "01_kappa_prepotential.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 一期 01 完成!")
