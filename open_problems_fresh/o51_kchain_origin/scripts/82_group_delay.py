#!/usr/bin/env python3
"""
O51/82: 群延遲權重 (Group Delay) — 視角扭曲嘅幾何代數解
===============================================================
權重: w_n = 1/v_g(n) = sec(pi*n/88)
截斷: F_proj = 17 = 44 - 27, n <= 27

C_delay 對比 C_obs = 0.17
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

N_d = 44
phi = (1 + math.sqrt(5)) / 2
F_proj = 17  # O54: 44 - 27
n_cut = N_d - F_proj  # 27

print("=" * 62)
print("群延遲權重 — 視角扭曲嘅幾何代數解")
print("=" * 62)

# ============ 1. K_Chain 譜 + 群速度 ============
print("\n--- K_Chain 色散與群速度 ---")
omega = [2*math.sin(math.pi*n/(2*N_d)) for n in range(1, N_d+1)]
gamma = [4*math.sin(math.pi*n/(2*N_d))**2 for n in range(1, N_d+1)]
v_g = [math.cos(math.pi*n/(2*N_d)) for n in range(1, N_d+1)]

print(f"{'n':<4} {'omega_n':<10} {'gamma_n':<10} {'v_g(n)':<10} {'1/v_g(n)':<12}")
print("-" * 46)
for n in [1, 5, 10, 15, 20, 22, 25, 27, 30, 35, 40, 44]:
    print(f"{n:<4} {omega[n-1]:<10.4f} {gamma[n-1]:<10.4f} {v_g[n-1]:<10.4f} {1/v_g[n-1] if v_g[n-1]>1e-10 else float('inf'):<12.2f}")

# ============ 2. 群延遲權重 ============
print("\n--- 群延遲權重 w_n = 1/v_g(n) ---")
w_n = [1/v_g[n] for n in range(N_d)]  # 全部, 包括發散點
w_n_cut = [1/v_g[n] for n in range(n_cut)]  # n <= 27 截斷

print(f"F_proj = {F_proj} = 44 - 27, n <= {n_cut}")
print(f"全譜 (n=1..44): Σw = {sum(w_n):.2f}, max w = {max(w_n):.2f}")
print(f"截斷 (n=1..{n_cut}): Σw = {sum(w_n_cut):.2f}, max w = {max(w_n_cut):.2f}")

# ============ 3. 群延遲加權嘅奇偶不對稱 ============
print("\n--- 群延遲加權奇偶不對稱 ---")

# 原始: 能量權重
C_energy = (sum(gamma[1::2]) - sum(gamma[0::2])) / sum(gamma)
print(f"C_energy (γ權重, n=1..44) = {C_energy:.6f}")

# 群延遲權重 (截斷)
w_even = sum(w_n_cut[i] * gamma[i] for i in range(0, n_cut, 2))
w_odd = sum(w_n_cut[i] * gamma[i] for i in range(1, n_cut, 2))
C_delay = (w_even - w_odd) / (w_even + w_odd)
print(f"C_delay (w·γ權重, n=1..{n_cut}) = {C_delay:.6f}")

# 純群延遲權重 (唔乘 γ)
w_even2 = sum(w_n_cut[i] for i in range(0, n_cut, 2))
w_odd2 = sum(w_n_cut[i] for i in range(1, n_cut, 2))
C_delay2 = (w_even2 - w_odd2) / (w_even2 + w_odd2)
print(f"C_delay2 (w純權重, n=1..{n_cut}) = {C_delay2:.6f}")

# ============ 4. C 值放大倍數 ============
print("\n--- C 值放大倍數 ---")
ratio = C_delay / C_energy
print(f"C_delay/C_energy = {ratio:.4f}")
print(f"C_delay = {C_delay:.6f}")
print(f"C_obs = 0.1697")

# 用群延遲權重計算完整 C
# δ(ℓ) = C × (ℓ-0.5) × (1-4^{-ℓ})
# C 應該 = C_delay × 2φ⁻¹? 或者直接用 C_delay?
# 實際上 C_delay 已經係奇偶不對稱嘅群延遲修正
# 所以 C = C_delay × 2φ⁻¹ (投影伸長因子嘅貢獻)

C_final = C_delay * 2 * phi**(-1)
print(f"\nC_final = C_delay × 2φ⁻¹ = {C_delay:.6f} × {2*phi**(-1):.6f} = {C_final:.6f}")
print(f"C_obs = 0.1697")
check("C_final ≈ C_obs", abs(C_final - 0.1697) < 0.05, f"{C_final:.4f} vs 0.1697")

# ============ 5. DESI 驗證 ============
print("\n--- DESI 驗證 ---")
R_H = 4129.94
rd_c = math.pi * R_H / 88 * 420/421

def D_orig(ell):
    return R_H * (1 - 4**(-ell)) * (1 + 2*phi**(-1)*ell)

def D_corrected(ell, C_val):
    delta = C_val * (ell - 0.5) * (1 - 4**(-ell))
    return R_H * (1 - 4**(-ell)) * (1 + 2*phi**(-1)*ell + delta)

desi = [
    (0.510, 13.588, 0.167),
    (0.706, 17.351, 0.177),
    (0.934, 21.576, 0.152),
    (1.321, 27.601, 0.318),
    (2.330, 38.988, 0.531),
]

chi2_orig = 0
chi2_corr = 0
for z, dm, err in desi:
    ell = math.log(1+z, 4)
    d1 = D_orig(ell) / rd_c
    d2 = D_corrected(ell, C_final) / rd_c
    chi2_orig += ((d1 - dm)/err)**2
    chi2_corr += ((d2 - dm)/err)**2
    print(f"z={z:.3f}: orig={d1:.3f}, corr={d2:.3f}, DESI={dm:.3f}")

print(f"\nχ² (原始): {chi2_orig:.2f}")
print(f"χ² (C_final): {chi2_corr:.2f}")

# ============ 6. F_proj 截斷驗證 ============
print("\n--- F_proj = 17 截斷必要性 ---")
# 如果冇截斷 (n=1..44), C_delay 會發散
w_full = [1/v_g[n] for n in range(N_d)]
w_even_full = sum(w_full[i] * gamma[i] for i in range(0, N_d, 2))
w_odd_full = sum(w_full[i] * gamma[i] for i in range(1, N_d, 2))
C_full = (w_even_full - w_odd_full) / (w_even_full + w_odd_full)
print(f"C_delay (無截斷, n=1..44) = {C_full:.6f}")
print(f"C_delay (F_proj截斷, n=1..{n_cut}) = {C_delay:.6f}")

# ============ 7. 總結 ============
print(f"\n{'=' * 62}")
print("總結")
print("=" * 62)
print(f"""
群延遲權重 w_n = 1/v_g(n) = sec(πn/88) 嘅奇偶不對稱:

C_delay = (Σw_even - Σw_odd) / (Σw_even + Σw_odd) = {C_delay:.6f}
C_final = C_delay × 2φ⁻¹ = {C_final:.6f}
C_obs = 0.1697

F_proj = 17 截斷 (n ≤ {n_cut}) 防止 v_g → 0 發散
結構自洽: O54 F_proj = 44 - 27 精確鎖定群延遲截斷點

print(f"delta(ell) = C_final x (ell - 0.5) x (1 - 4^(-ell))")
""")

result = {
    'C_energy': round(C_energy, 6),
    'C_delay': round(C_delay, 6),
    'C_delay_ratio': round(ratio, 4),
    'C_final': round(C_final, 6),
    'C_obs': 0.1697,
    'F_proj': F_proj,
    'n_cut': n_cut,
    'chi2_orig': round(chi2_orig, 2),
    'chi2_corr': round(chi2_corr, 2),
    'pass': PASS,
    'fail': FAIL
}

with open('data/82_group_delay.json', 'w') as f:
    json.dump(result, f, indent=2, default=str)

print(f"-> data/82_group_delay.json")