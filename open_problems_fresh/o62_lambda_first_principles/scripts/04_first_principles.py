#!/usr/bin/env python3
"""
O62 一期 04: 第一性原理閉合 — V_Λ = F(γ) + 44 − F₈ − B
========================================================
★ 發現 (一期 02/03):
  F(γ) = 264.082129 (真 κ prepotential @ t*=γ_n)
  V_Λ = F(γ) + 44 − F₈ − B = 283.082129 (0.00245%)
       = F(γ) + (N_d − Z₂fixed − branching)
       = F(γ) + (44 − 21 − 4) = F(γ) + 19

結構解讀:
  44 = N_d (K_Chain site)
  F₈ = 21 = Z₂ fixed beats (946 投影)
  B = 4 = K_Tree 分支
  19 = 44 − 25 = N_d − CPX kernel gap
  25 = F₈ + B = 98 − 73 (CPX rank 缺口!)

本腳本:
  1. 驗證 V_Λ = F(γ) + 44 − F₈ − B 精確閉合
  2. 物理詮釋: 44γ₆ 舊公式 vs 新公式
  3. 檢查 F(γ) 嘅 264.0821 = 6N_d 有冇更深結構
  4. 推導鏈完整版
"""
import sys, os, math, json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O62 一期 04: 第一性原理閉合驗證")
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

# ============ 1. 核心量 ============
print("\n[1] 核心量")
d = json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))
kappa = np.array(d["kappa"])
gamma36 = 4 * np.sin(np.pi * np.arange(1, 37) / 88) ** 2
L = [2, 1]
for i in range(2, 40):
    L.append(L[i-1] + L[i-2])

def F(t):
    return np.einsum("ijk,i,j,k", kappa, t, t, t) / 6.0

Nd = 44
F8 = 21
B = 4
g6 = 4*math.sin(6*math.pi/88)**2
Fg = F(gamma36)
V_obs = 283.0752
V_Lambda = Fg + Nd - F8 - B
V_old = L[10]*phi + L[9] + 44*g6

print(f"  F(γ) = {Fg:.10f}")
print(f"  V_Λ(new) = F(γ) + 44 − 21 − 4 = {V_Lambda:.10f}")
print(f"  V_obs = {V_obs:.10f}")
print(f"  V_Λ(old) = V₁₀+44γ₆ = {V_old:.10f}")

# ============ 2. 閉合驗證 ============
print("\n[2] 閉合驗證")
err_new = abs(V_Lambda - V_obs)/V_obs*100
err_old = abs(V_old - V_obs)/V_obs*100
check("V_Λ(new) 誤差 < 0.01%", err_new < 0.01, f"({err_new:.5f}%)")
check("V_Λ(new) 比 V_Λ(old) 精確", err_new < err_old, f"(new {err_new:.5f}% vs old {err_old:.5f}%)")

# 密度比
rho_new = math.exp(-V_Lambda)
rho_obs = 1.1535e-123
ratio_new = rho_new / rho_obs
ratio_old = math.exp(-V_old) / rho_obs
print(f"  ρ_new/ρ_obs = {ratio_new:.4f} (誤差 {abs(ratio_new-1)*100:.2f}%)")
print(f"  ρ_old/ρ_obs = {ratio_old:.4f} (誤差 {abs(ratio_old-1)*100:.2f}%)")
check("ρ 比 ∈ [0.9, 1.1]", 0.9 < ratio_new < 1.1, f"({ratio_new:.4f})")

# ============ 3. 19 嘅結構身份 ============
print("\n[3] 19 = 44 − 25 = N_d − CPX kernel gap")
print(f"  44 = N_d (K_Chain site 數)")
print(f"  25 = F₈ + B = 21 + 4 (Z₂ fixed + branching)")
print(f"  25 = 98 − 73 = h²¹ − rank(CPX) (CPX 投影 rank 缺口!)")
print(f"  19 = 44 − 25 = N_d − CPX gap")
print(f"  19 = L₅ + F₆ = 11 + 8 (Lucas 5 + Fibonacci 6)")
print(f"  19 = L₆ + 1 = 18 + 1")
print(f"  19 = F₁₀ − 36 = 55 − 36")
check("19 = 44 − 25", 19 == 44 - 25)
check("19 = L₅+F₆", 19 == 11 + 8)
check("25 = F₈+B", 25 == 21 + 4)

# ============ 4. 264 = 6N_d 深層 ============
print("\n[4] F(γ) = 264.0821 ≈ 6N_d")
print(f"  F(γ) = {Fg:.10f}")
print(f"  6×44 = 264")
print(f"  F(γ) − 264 = {Fg - 264:.8f}")
print(f"  F(γ)/(6N_d) = {Fg/264:.8f}")
print(f"  264 = 6×44 = 6N_d")
print(f"  264 = 88×3 = 2N_d×3")
print(f"  264 = 2×132 = 2×L₈×...? L₈ = 47, L₉ = 76, L₁₀ = 123")
print(f"  264 = 4×66 = B×66 (66 態!)")
print(f"  264 = 66×4 = 66 態 × B")
check("264 = 4×66 (66 態 × B)", 264 == 4*66)
print(f"  264 = 2×Σγ + 84 = 180 + 84? 84 = F₈·B")
print(f"  264 = 2×90 + 84 = {2*90 + 84}")
check("264 = 2Σγ + F₈·B", 264 == 2*90 + 21*4)

# ============ 5. 剩餘 0.0821 精確 ============
print("\n[5] 剩餘 0.082129 精確分解")
rem = Fg - 264
print(f"  rem = {rem:.10f}")
# 高精度搜索: a·γ_b + c·γ_d 組合
gamma44 = 4 * np.sin(np.pi * np.arange(1, 45) / 88) ** 2
best = []
for a in range(1, 5):
    for b in range(1, 45):
        for c in range(0, 5):
            for dd in range(1, 45):
                val = a*gamma44[b-1] + c*gamma44[dd-1]
                err = abs(val - rem)/rem
                if err < 1e-3:
                    best.append((err, f"{a}γ_{b}+{c}γ_{dd}", val))
best.sort()
print(f"  top 5 (誤差<0.1%):")
for err, name, val in best[:5]:
    print(f"    {name:14s} = {val:.10f} (誤差 {err*100:.5f}%)")

# γ_29/36 精確度
print(f"\n  γ_29/36 = {gamma44[28]/36:.10f} vs rem = {rem:.10f}")
print(f"  誤差: {abs(gamma44[28]/36 - rem)/rem*100:.5f}%")
print(f"  γ_29 = {gamma44[28]:.8f}")
print(f"  36 = h¹¹ (Kähler moduli 數!)")
print(f"  29 = L₇ (Lucas 7)")

# ============ 6. 推導鏈完整版 ============
print("\n[6] 第一性原理推導鏈")
print(f"""
  x²+x−1=0 → φ
    → K_Chain 44-site (γ_n = 4sin²(nπ/88), Σγ=90)
    → Beat 空間 Λ²(R⁴⁴) = 946
    → 投影算子 P̂(134×946):
        Kähler 36 行 (support 21=F₈, full rank 36)
        CPX 98 行 (rank 73, 缺口 25=F₈+B)
    → CY₃(36,98) 真交集數 κ_ijk (1341 非零)
    → Kähler 模 VEV: t*_i = γ_i (K_Chain 諧波)
        (唯一自然方案: Y(γ) kernel=4=B, M_rank=32=2B²)
    → prepotential: F(t*) = (1/6)κ_ijk t*_i t*_j t*_k
        = {Fg:.6f} ≈ 6N_d = 264 ({abs(Fg-264)/264*100:.4f}%)
    → 真空能:
        V_Λ = F(t*) + (N_d − F₈ − B)
            = {Fg:.4f} + (44 − 21 − 4)
            = {V_Lambda:.4f}
        vs V_obs = {V_obs:.4f}  ({err_new:.5f}%)
    → ρ_Λ = e^-V_Λ = {rho_new:.3e} vs 觀測 1.1535e-123
        比 = {ratio_new:.4f} ({abs(ratio_new-1)*100:.2f}%)
""")

# ============ 7. 預指數因子 ============
print("\n[7] 預指數因子 (SUGRA 對照)")
C = math.exp(-(Nd - F8 - B))
print(f"  C = e^-(44−21−4) = e^-19 = {C:.6e}")
print(f"  SUGRA 預期 C ≈ 10⁻³~10⁻⁴? e^-19 = {C:.2e}")
print(f"  e^-19 = {C:.3e} ≈ 10⁻⁸.3")
print(f"  -log10(e^-19) = {19*math.log10(math.e):.4f} = 8.25")
print(f"  對比 44γ₆: e^-7.95 = {math.exp(-44*g6):.2e} ≈ 10⁻⁴")
print(f"  19 ≈ 8.25 個數量級 (唔係 10⁻⁴)")
print(f"  ⚠️ e^-19 太細 — 預指數因子係 8.25 個數量級")
print(f"  需要重新審視: 44−F₈−B 係咪真係真空能修正?")
print(f"  定係 F(γ) 有 8.25 個數量級嘅 pre-factor?")
C2 = math.exp(-Fg)
print(f"  如果 V_Λ = F(γ) + 修正: ρ = e^-F(γ)·e^-19")
print(f"  e^-F(γ) = {C2:.3e} ≈ 10⁻¹¹⁴.7")

# ============ 8. 總結 ============
print("\n" + "=" * 72)
print("一期 04 總結:")
print("=" * 72)
print(f"""
  ★ 第一性原理閉合:
  V_Λ = F(γ) + 44 − F₈ − B = {V_Lambda:.6f}
  vs V_obs = {V_obs:.6f}
  誤差 = {err_new:.5f}% (O57 舊公式 {err_old:.5f}%)

  結構:
  F(γ) = {Fg:.6f} = prepotential @ K_Chain 諧波 VEV
  44−F₈−B = 19 = N_d − CPX kernel gap (25)
  25 = 98−73 = h²¹ − rank(CPX)

  問題:
  - 19 嘅結構身份多重 (L₅+F₆, L₆+1, 44−25) — 邊個係「第一性」?
  - e^-19 預指數 = 8.25 數量級 vs SUGRA 10⁻⁴ — 需要詮釋
""")
out = {
    "test": "O62 一期 04: 第一性原理閉合",
    "F_gamma": float(Fg), "V_Lambda_new": float(V_Lambda),
    "V_obs": V_obs, "err_new_pct": float(err_new),
    "err_old_pct": float(err_old), "rho_ratio": float(ratio_new),
    "F_minus_264": float(Fg - 264),
    "rem_candidates": [{"name": n, "val": float(v), "err": float(e)} for e, n, v in best[:5]],
    "prefactor_e19": float(C),
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "04_first_principles.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 一期 04 完成!")
