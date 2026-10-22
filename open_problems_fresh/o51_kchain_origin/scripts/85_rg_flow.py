#!/usr/bin/env python3
"""
O51/85: RG Flow 非線性積分 — 投影伸長因子嘅完整 β 函數
===============================================================
從 β(g) = β₁g + β₂g² + β₃g³ + ... 嘅非線性積分推導 δ(ℓ)

一階: β₁ = C₁ = 2/90 (奇偶不對稱)
二階: β₂ = C₂/C₁ = skewness × σ/μ (譜偏度)
三階: β₃ = C₃/C₁ = kurtosis × σ²/μ² (譜峰度)

完整積分: g(ℓ) = ∫₀^ℓ β(g(ℓ')) dℓ'
δ(ℓ) = ... 從 g(ℓ) 推導
"""
import json, math

PASS = 0
FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ PASS: {name}")
    else:
        FAIL += 1
        print(f"  ❌ FAIL: {name}")
    if detail:
        print(f"    {detail}")

R_H = 4129.94
N_d = 44
phi = (1 + math.sqrt(5)) / 2
rd_c = math.pi * R_H / 88 * 420/421

print("=" * 62)
print("RG Flow 非線性積分 — 完整 β 函數")
print("=" * 62)

# ============ 1. K_Chain 譜矩 ============
gamma = [4*math.sin(math.pi*n/(2*N_d))**2 for n in range(1, N_d+1)]
sum_w = sum(gamma)
mean = sum((n+1)*gamma[n] for n in range(N_d)) / sum_w
var = sum((n+1-mean)**2*gamma[n] for n in range(N_d)) / sum_w
skew = sum((n+1-mean)**3*gamma[n] for n in range(N_d)) / sum_w / var**1.5
kurt = sum((n+1-mean)**4*gamma[n] for n in range(N_d)) / sum_w / var**2 - 3

# 群延遲加權 C_delay
n_cut = 27
v_g = [math.cos(math.pi*n/(2*N_d)) for n in range(1, N_d+1)]
w_cut = [1/v_g[n] for n in range(n_cut)]
w_even = sum(w_cut[i]*gamma[i] for i in range(0, n_cut, 2))
w_odd = sum(w_cut[i]*gamma[i] for i in range(1, n_cut, 2))
C_delay = (w_even - w_odd) / (w_even + w_odd)

# ============ 2. β 函數係數 ============
print("\n--- Beta 函數係數 ---")
beta1 = C_delay  # 群延遲不對稱
beta2 = skew * math.sqrt(var) / mean  # 譜偏度貢獻
beta3 = kurt * var / (mean**2)  # 譜峰度貢獻

print(f"β₁ = C_delay = {beta1:.6f}")
print(f"β₂ = skew·σ/μ = {skew:.4f} × {math.sqrt(var):.4f} / {mean:.4f} = {beta2:.6f}")
print(f"β₃ = kurt·σ²/μ² = {kurt:.4f} × {var:.4f} / {mean**2:.4f} = {beta3:.6f}")

# ============ 3. RG Flow 積分 ============
print("\n--- RG Flow 數值積分 ---")
# dg/dℓ = β₁g + β₂g² + β₃g³
# Runge-Kutta 4 階積分
def rg_flow(ell_max, steps=1000):
    dℓ = ell_max / steps
    g = 0.0
    ells = [0.0]
    gs = [0.0]
    for _ in range(steps):
        k1 = beta1*g + beta2*g**2 + beta3*g**3
        k2 = beta1*(g + dℓ*k1/2) + beta2*(g + dℓ*k1/2)**2 + beta3*(g + dℓ*k1/2)**3
        k3 = beta1*(g + dℓ*k2/2) + beta2*(g + dℓ*k2/2)**2 + beta3*(g + dℓ*k2/2)**3
        k4 = beta1*(g + dℓ*k3) + beta2*(g + dℓ*k3)**2 + beta3*(g + dℓ*k3)**3
        g += dℓ*(k1 + 2*k2 + 2*k3 + k4)/6
        ells.append(ells[-1] + dℓ)
        gs.append(g)
    return ells, gs

ells, gs = rg_flow(1.0)

# 比較: 一階 linear vs 非線性 RG
print(f"{'ℓ':<6} {'g_linear':<12} {'g_RG':<12} {'dev%':<10}")
print("-" * 40)
for i in range(0, len(ells), 200):
    g_lin = beta1 * ells[i]
    dev = (gs[i] - g_lin) / g_lin * 100 if g_lin > 0 else 0
    print(f"{ells[i]:<6.3f} {g_lin:<12.6f} {gs[i]:<12.6f} {dev:>+8.2f}%")

# ============ 4. δ(ℓ) 從 RG Flow 推導 ============
print("\n--- delta(ℓ) 從 RG Flow 推導 ---")
# δ(ℓ) 嘅核心係 g(ℓ) - β₁ℓ (非線性殘差)
# 但係完整 δ(ℓ) 要考慮投影伸長因子嘅貢獻
# 近似: δ(ℓ) = g(ℓ) × (ℓ-0.5) × (1-4^{-ℓ})

def D_orig(ell):
    return R_H * (1 - 4**(-ell)) * (1 + 2*phi**(-1)*ell)

def D_RG(ell):
    # 從 RG flow 積分插值
    i = int(ell / 1.0 * 1000)
    if i >= len(gs): i = len(gs) - 1
    g_ell = gs[i]
    # 修正: δ(ℓ) = -g(ℓ) × 2φ⁻¹ × √5 × (ℓ-0.5) × (1-4^{-ℓ})
    delta = -g_ell * 2*phi**(-1) * 5**0.5 * (ell - 0.5) * (1 - 4**(-ell))
    return R_H * (1 - 4**(-ell)) * (1 + 2*phi**(-1)*ell + delta)

# DESI 驗證
desi = [(0.510, 13.588, 0.167), (0.706, 17.351, 0.177), (0.934, 21.576, 0.152), (1.321, 27.601, 0.318), (2.330, 38.988, 0.531)]
chi2_orig = 0; chi2_rg = 0
print(f"{'z':<6} {'orig':<10} {'RG':<10} {'DESI':<10} {'orig dev':<10} {'RG dev':<10}")
print("-" * 56)
for z, dm, err in desi:
    ell = math.log(1+z, 4)
    d1 = D_orig(ell)/rd_c; d2 = D_RG(ell)/rd_c
    dev1 = (d1-dm)/dm*100; dev2 = (d2-dm)/dm*100
    chi2_orig += ((d1-dm)/err)**2; chi2_rg += ((d2-dm)/err)**2
    print(f"{z:<6.3f} {d1:<10.3f} {d2:<10.3f} {dm:<10.3f} {dev1:>+7.2f}% {dev2:>+7.2f}%")

print(f"chi2 原始: {chi2_orig:.2f}")
print(f"chi2 RG: {chi2_rg:.2f}")
print(f"改善: {(1-chi2_rg/chi2_orig)*100:.1f}%")

# ============ 5. 同群延遲修正比較 ============
print("\n--- 群延遲 vs RG Flow 比較 ---")
def D_group(ell):
    C_val = -C_delay * 2*phi**(-1) * 5**0.5
    delta = C_val * (ell - 0.5) * (1 - 4**(-ell))
    return R_H * (1 - 4**(-ell)) * (1 + 2*phi**(-1)*ell + delta)

chi2_group = 0
for z, dm, err in desi:
    ell = math.log(1+z, 4)
    d = D_group(ell)/rd_c
    chi2_group += ((d-dm)/err)**2
print(f"chi2 群延遲: {chi2_group:.2f}")
print(f"chi2 RG: {chi2_rg:.2f}")

# ============ 6. 總結 ============
print(f"\n{'=' * 62}")
print(f"總結: {PASS}/{PASS+FAIL}")
print(f"{'=' * 62}")

result = {
    'beta1': round(beta1, 6),
    'beta2': round(beta2, 6),
    'beta3': round(beta3, 6),
    'chi2_orig': round(chi2_orig, 2),
    'chi2_rg': round(chi2_rg, 2),
    'chi2_group': round(chi2_group, 2),
    'pass': PASS,
    'fail': FAIL
}

with open('data/85_rg_flow.json', 'w') as f:
    json.dump(result, f, indent=2, default=str)
print(f"-> data/85_rg_flow.json")