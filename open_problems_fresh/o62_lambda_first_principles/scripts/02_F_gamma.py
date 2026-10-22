#!/usr/bin/env python3
"""
O62 一期 02: F(γ) 精確閉合 — K_Chain 諧波 prepotential = 真空能
================================================================
發現 (一期 01): t = γ_n (K_Chain 諧波) 係唯一自然方案:
  F(γ) = 264.0821 (自動接近 V_Λ ≈ 283)
  Y(γ) kernel = 4 = B, M_rank = 32 = 2B²

初步: V_obs − F(γ) = 18.993 ≈ 44γ₆ + L₅ = 18.952 (0.24%?)

本腳本: 精確驗證 F(γ) 嘅結構:
  1. F(γ) 精確值 + 同 V₁₀/V_obs 嘅關係
  2. Δ = V_obs − F(γ) 嘅結構分解 (44γ₆? L₅? φ?)
  3. Y(γ) kernel 零模 N 嘅整數化 → 66/90 通量子
  4. 推導鏈: t*=γ → F(t*) → V_Λ 自動出現?
"""
import sys, os, math, json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O62 一期 02: F(γ) 精確閉合分析")
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

# ============ 1. 載入 + 基本量 ============
print("\n[1] 基本量")
d = json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))
kappa = np.array(d["kappa"])
gamma36 = 4 * np.sin(np.pi * np.arange(1, 37) / 88) ** 2
L = [2, 1]
for i in range(2, 40):
    L.append(L[i-1] + L[i-2])

def F(t):
    return np.einsum("ijk,i,j,k", kappa, t, t, t) / 6.0
def dF(t):
    return 0.5 * np.einsum("ijk,j,k", kappa, t, t)
def Y(t):
    return np.einsum("ijk,k", kappa, t)

V10 = L[10]*phi + L[9]
g6 = 4*math.sin(6*math.pi/88)**2
V_obs = 283.0752
Fg = F(gamma36)
print(f"  F(γ) = {Fg:.10f}")
print(f"  V₁₀ = {V10:.10f}")
print(f"  V_obs = {V_obs:.10f}")
print(f"  V₁₀+44γ₆ = {V10+44*g6:.10f}")

# ============ 2. Δ 分解 ============
print("\n[2] Δ = V_obs − F(γ) 結構分解")
dV1 = V_obs - Fg
dV2 = V10 - Fg
print(f"  Δ_obs = V_obs − F(γ) = {dV1:.8f}")
print(f"  Δ_10  = V₁₀ − F(γ)  = {dV2:.8f}")

# 候選分解
cands = {
    "44γ₆": 44*g6,
    "L₅": 11.0,
    "44γ₆+L₅": 44*g6 + 11,
    "44γ₆+L₅+γ₁L₅": 44*g6 + 11 + 4*math.sin(math.pi/88)**2*11,
    "2×L₆+γ₆²": 36 + g6**2,
    "L₅+γ₆×44+2": 11 + 44*g6 + 2,
    "18.99≈19": 19.0,
    "φ⁶": phi**6,
    "L₆+2": 18+2,
}
print(f"\n  Δ_obs = {dV1:.6f} 候選:")
for name, val in cands.items():
    err = abs(val - dV1)/dV1*100
    print(f"    {name:18s} = {val:.8f}  (誤差 {err:.3f}%)")

# ============ 3. F(γ) 自身結構 ============
print("\n[3] F(γ) 自身結構")
print(f"  F(γ) = {Fg:.8f}")
print(f"  V₁₀ − F(γ) = {V10 - Fg:.8f}")
print(f"  V₁₀/F(γ) = {V10/Fg:.8f}")
print(f"  F(γ) ≈ 264? 264 = 6×44 = 6N_d")
print(f"  6×44 = {6*44}, F(γ)/(6×44) = {Fg/(6*44):.6f}")
print(f"  264.0821/44 = {Fg/44:.6f}")
print(f"  264.0821/88 = {Fg/88:.6f}")
print(f"  264.0821/90 = {Fg/90:.6f}")
print(f"  264.0821/134 = {Fg/134:.6f}")
print(f"  264.0821 - 264 = {Fg - 264:.6f}")

# 264 = 6×44 = 6N_d?  F(γ)/6 = ?
print(f"  F(γ)/6 = {Fg/6:.6f} (平均 κ 立方)")
print(f"  F(γ)/36 = {Fg/36:.6f}")

# ============ 4. Y(γ) kernel = 4 深入 ============
print("\n[4] Y(γ) kernel 零模 → 通量子")
Yg = Y(gamma36)
evals, evecs = np.linalg.eigh(Yg)
n_zero = np.sum(np.abs(evals) < 1e-8)
print(f"  Y(γ) 零本徵值: {n_zero}")
check("Y(γ) kernel = 4 = B", n_zero == 4, f"(n={n_zero})")

zero_idx = np.where(np.abs(evals) < 1e-8)[0]
for zi in zero_idx:
    N0 = evecs[:, zi]
    s = N0[np.argmax(np.abs(N0))]
    N_int = np.round(N0 / s).astype(int)
    sum_abs = np.sum(np.abs(N_int))
    print(f"  零模 {zi}: sum|N| = {sum_abs}, 非零 {np.count_nonzero(N_int)}/36")
    print(f"    N = {N_int}")

# kernel 零模嘅組合: 66/90?
print("\n  零模線性組合 → 66/90?")
# 4 個零模
Ns = evecs[:, zero_idx]  # 36×4
# 隨機整數組合 c ∈ {-3..3}⁴ 搜索 sum|N| = 66/90
found = []
for c1 in range(-3, 4):
    for c2 in range(-3, 4):
        for c3 in range(-3, 4):
            for c4 in range(-3, 4):
                N = c1*Ns[:,0] + c2*Ns[:,1] + c3*Ns[:,2] + c4*Ns[:,3]
                # 整數化
                s = N[np.argmax(np.abs(N))]
                if abs(s) < 1e-8:
                    continue
                N_int = np.round(N/s).astype(int)
                sa = np.sum(np.abs(N_int))
                if sa in (44, 66, 90) and np.all(np.abs(N_int) < 100):
                    found.append((c1, c2, c3, c4, sa, N_int))
                    if len(found) > 5:
                        break
            if len(found) > 5:
                break
        if len(found) > 5:
            break
    if len(found) > 5:
        break

if found:
    for c1, c2, c3, c4, sa, N_int in found[:5]:
        print(f"  ✅ (c1,c2,c3,c4)=({c1},{c2},{c3},{c4}) → sum|N| = {sa}")
        print(f"     N = {N_int}")
else:
    print("  ❌ 冇簡單整數組合命中 44/66/90")

# ============ 5. F(γ) 修正方案 ============
print("\n[5] F(γ) + 修正 vs V_Λ 完整比較")
print(f"  V_obs = {V_obs:.8f}")
cands2 = {
    "F(γ)": Fg,
    "F(γ)+44γ₆": Fg + 44*g6,
    "F(γ)+L₅": Fg + 11,
    "F(γ)+44γ₆+L₅": Fg + 44*g6 + 11,
    "F(γ)+2L₆": Fg + 36,
    "F(γ)+90": Fg + 90,
    "F(γ)+88": Fg + 88,
    "F(γ)+84": Fg + 84,
    "F(γ)+44": Fg + 44,
    "V₁₀+44γ₆ (舊)": V10 + 44*g6,
}
print(f"  {'公式':24s} {'值':>12s} {'誤差%':>9s}")
for name, val in cands2.items():
    err = abs(val - V_obs)/V_obs*100
    print(f"  {name:24s} {val:12.6f} {err:8.4f}%")

# ============ 6. 檢查: F(γ) 同 44γ₆ 有冇代數關係 ============
print("\n[6] F(γ) 同 γ₆/44 關係")
print(f"  F(γ) mod 44 = {Fg % 44:.6f}")
print(f"  F(γ) - 6×44 = {Fg - 264:.6f}")
print(f"  264 - F(γ) = {264 - Fg:.6f}")
print(f"  44×6 = 264, F(γ) = 264.0821 → 差 0.0821")
print(f"  0.0821 ≈ γ₁×16.1? γ₁ = {4*math.sin(math.pi/88)**2:.6f}")
print(f"  0.0821 ≈ γ₆²×2.5? γ₆² = {g6**2:.6f}")
print(f"  0.0821 ≈ 1/12.18?")
print(f"  0.0821 = ?")

# 關鍵: F(γ) 係咪 = 264 + 某 γ 組合?
rem = Fg - 264
print(f"\n  剩餘 0.0821 分解:")
for n in range(1, 45):
    gn = 4*math.sin(n*math.pi/88)**2
    err = abs(gn - rem)/rem*100
    if err < 5:
        print(f"    γ_{n} = {gn:.6f} (誤差 {err:.2f}%)")
    err2 = abs(gn/2 - rem)/rem*100
    if err2 < 5:
        print(f"    γ_{n}/2 = {gn/2:.6f} (誤差 {err2:.2f}%)")

# ============ 7. 總結 ============
print("\n" + "=" * 72)
print("一期 02 總結:")
print("=" * 72)
print(f"""
  F(γ) = {Fg:.6f} 係唯一自然 K_Chain 方案嘅 prepotential
  Y(γ) kernel = {n_zero} = B (4), M_rank = 32 = 2B²

  Δ_obs = {dV1:.6f} 候選: {min(cands.items(), key=lambda x: abs(x[1]-dV1)/dV1)[0]}
  F(γ)+44γ₆+L₅ = {Fg+44*g6+11:.4f} vs V_obs = {V_obs:.4f}

  推導鏈狀態:
  t* = γ_n (K_Chain 諧波, 投影算子自然結構)
  → F(t*) = {Fg:.4f} (自動接近 V_Λ)
  → 修正項? → V_Λ
""")
out = {
    "test": "O62 一期 02: F(γ) 精確閉合",
    "F_gamma": float(Fg), "V10": float(V10), "V_obs": V_obs,
    "delta_obs": float(dV1), "delta_10": float(dV2),
    "candidates": {k: float(v) for k, v in cands.items()},
    "F_plus_cands": {k: float(v) for k, v in cands2.items()},
    "Y_kernel": int(n_zero), "M_rank": int(np.sum(np.linalg.eigvalsh(Yg.T@Yg) > 1e-8)),
    "zero_mode_combos": [[int(c) for c in f[:4]] for f in found[:5]] if found else [],
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "02_F_gamma.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 一期 02 完成!")
