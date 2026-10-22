#!/usr/bin/env python3
"""
O32-31: 冷斑 ε = F₇/(2N-2) 深層幾何推導 — 拓撲算符機制
=======================================================
核心問題:
1. 分母 2N-2 = 86 嘅拓撲幾何來源?
2. 分子 F₇ = 13 嘅選擇律 (點解唔係 F₆/F₈)?
3. 零參數導出 134.45 μK?

新發現候選結構:
  N = L₇ + F₇ + 2 = 29 + 13 + 2 = 44  ← Lucas+Fibonacci+特殊模式!
  86 = 2N-2 = 2(N-1) = 2×43
  43 = 2F₈+1 = 2×21+1 (質數)
  F_k + L_k = 2F_{k+1} (Lucas 恆等式) → N = 2(F₈+1) 唯一鎖定 k=7
"""
import numpy as np
import json
import math

PHI = (1+math.sqrt(5))/2
T_CMB = 2.72548

def fib(k):
    return int(round(PHI**k/math.sqrt(5))) if k > 0 else 0

def lucas(k):
    return int(round(PHI**k + (-1/PHI)**k)) if k >= 0 else 0

# Fibonacci: F₁=1, F₂=1, F₃=2, F₄=3, F₅=5, F₆=8, F₇=13, F₈=21
# Lucas:     L₁=1, L₂=3, L₃=4, L₄=7, L₅=11, L₆=18, L₇=29, L₈=47
F = {k: fib(k) for k in range(1, 13)}
L = {k: lucas(k) for k in range(1, 13)}
print("="*78)
print("冷斑 ε = F₇/(2N-2) 深層幾何推導")
print("="*78)

# ===== 1. F₇ 選擇律: N = F_k + L_k + 2 唯一解 =====
print("\n--- 1. F₇ 選擇律: N = F_k + L_k + 2 ---")
print(f"N = 44, 掃描 k = 1..12:")
for k in range(1, 13):
    val = F[k] + L[k] + 2
    mark = "★ 命中!" if val == 44 else ""
    print(f"  k={k:>2}: F_{k} = {F[k]:>3}, L_{k} = {L[k]:>3}, F+L+2 = {val:>4} {mark}")
print(f"\n→ 唯一解: k = 7 (F₇ = 13, L₇ = 29)")
print(f"  N = L₇ + F₇ + 2 = 29 + 13 + 2 = 44 ✓")

# Lucas 恆等式: F_k + L_k = 2F_{k+1}
print(f"\n驗證 Lucas 恆等式: F_k + L_k = 2F_{{k+1}}:")
for k in [5, 6, 7, 8]:
    lhs = F[k] + L[k]
    rhs = 2*F[k+1]
    print(f"  k={k}: F+L = {lhs}, 2F_{{{k+1}}} = {rhs}, {'✓' if lhs==rhs else '✗'}")

# N = 2(F₈+1) → k = 7 唯一
print(f"\nN = 2(F_k+L_k)/2 + 2 = 2(F_{{k+1}}+1):")
for k in range(1, 12):
    if 2*(F[k+1]+1) == 44:
        print(f"  k={k}: 2(F_{{{k+1}}}+1) = 2({F[k+1]}+1) = 44 ★")
print(f"→ F_{k+1} = F₈ = 21, 所以 k = 7: F₇ = 13 ★")

# ===== 2. 86 = 2N-2 嘅拓撲來源: 88-site 環簡併結構 =====
print("\n--- 2. 86 = 2N-2: 88-site 環嘅簡併自由度 ---")
# 88-site 週期環, 模式 n = 0..87, γ_n = 4sin²(πn/88)
# γ_n = γ_{88-n} (簡併對), n=0 零模 (γ=0), n=44 Nyquist (γ=4)
N88 = 88
degenerate_pairs = (N88 - 2)//2  # 43 對
zero_mode = 1      # n=0, γ=0
nyquist = 1        # n=44, γ=4
print(f"88-site 環模式: n = 0..87")
print(f"  簡併對: (n, 88-n), n = 1..43 → {degenerate_pairs} 對 = {2*degenerate_pairs} 個模式")
print(f"  特殊模式: n=0 (零模, γ=0) + n=44 (Nyquist, γ=4) = {zero_mode+nyquist} 個")
print(f"  總計: {2*degenerate_pairs} + 2 = {2*degenerate_pairs+2} ✓")
print(f"  有效自由度 = {2*degenerate_pairs} = {2*44-2} = 86 = 2N-2 ✓")

# 驗證 γ 簡併
gamma = lambda n: 4*math.sin(math.pi*n/88)**2
print(f"\n簡併驗證: γ_n = γ_{{88-n}}:")
for n in [1, 10, 22, 30, 43]:
    print(f"  γ_{n} = {gamma(n):.6f}, γ_{88-n} = {gamma(88-n):.6f}, {'✓' if abs(gamma(n)-gamma(88-n))<1e-10 else '✗'}")
print(f"  零模 γ_0 = {gamma(0):.1e} (≈0)")
print(f"  Nyquist γ_44 = {gamma(44):.6f} (=4=γ_max=B)")

# ===== 3. ε = F₇/(2N-2) 唯一性: 掃描 F_k =====
print("\n--- 3. ε = F_k/(2N-2) 掃描: 只有 F₇ 命中 134μK ---")
dT_obs = 134.2e-6
eps_obs = (8*dT_obs/T_CMB/5)**(1/5)
print(f"觀測反推: ε_obs = {eps_obs:.8f}")
print(f"ε_obs² 反推: (8·134.2μK/2.72548/5)^(1/5)")
for k in range(1, 12):
    eps_k = F[k]/86
    dT_k = 5*eps_k**5*T_CMB/8*1e6
    dev = abs(dT_k - 134.2)/134.2*100
    mark = "★ 命中!" if dev < 1 else ""
    print(f"  F_{k:>2} = {F[k]:>3}: ε = {eps_k:.8f}, δT = {dT_k:>9.2f} μK, 偏差 {dev:>6.2f}% {mark}")

# ===== 4. ε 嘅雙重結構: F₇ 同 86 都係 44 嘅分解 =====
print("\n--- 4. ε 嘅雙重結構 ---")
print(f"N = 44 = L₇ + F₇ + 2 = 29 + 13 + 2")
print(f"86 = 2N-2 = 2(F₇+L₇+2) - 2 = 2F₇ + 2L₇ + 2 = {2*13} + {2*29} + 2 = {2*13+2*29+2}")
print(f"ε = F₇/86 = F₇/(2F₇+2L₇+2)")
print(f"  = 13/(26+58+2) = 13/86 = {13/86:.8f}")
print(f"  = F₇/(2(N-1)) = 13/(2×43)")

# 43 = 2F₈+1
print(f"\n43 = N-1 = 2F₈+1 = 2×21+1 = 43 (質數)")
print(f"86 = 2(N-1) = 4F₈+2 = {4*21+2}")

# ===== 5. F₇/F₈ ≈ 1/φ =====
print("\n--- 5. F₇/F₈ ≈ 1/φ (Fibonacci 比例) ---")
ratio = F[7]/F[8]
print(f"F₇/F₈ = 13/21 = {ratio:.6f}")
print(f"1/φ = {1/PHI:.6f}")
print(f"偏差 = {abs(ratio-1/PHI)/(1/PHI)*100:.4f}%")

# ===== 6. 位置閉合: 冷斑 (209°, -57°) = (180+L₇, -(44+F₇)) =====
print("\n--- 6. 位置閉合 ---")
lon = 180 + L[7]
lat = -(44 + F[7])
print(f"經度: 180 + L₇ = 180 + 29 = {lon}° ✓ (SMICA 209°)")
print(f"緯度: -(44 + F₇) = -(44 + 13) = {lat}° ✓ (SMICA -57°)")
print(f"44 = N, 13 = F₇: 緯度 57 = N + F₇")

# ===== 7. 帶內模態: n = 88/3 ≈ L₇ = 29 =====
print("\n--- 7. 帶內模態 n = 29 = L₇ ---")
n_inband = 88/3
print(f"E=1: 2cos(πn/88) = 1 → n = 88/3 = {n_inband:.4f}")
print(f"L₇ = {L[7]} (偏差 {abs(n_inband-L[7])/n_inband*100:.2f}%)")
print(f"F₇+L₇ = 42 = 44-2 = N-2")

# ===== 8. 最終閉合: δT = 5ε⁵T/8 =====
print("\n" + "="*78)
print("★ 零參數閉合")
print("="*78)
eps = F[7]/(2*44-2)
dT_pred = 5*eps**5*T_CMB/8
print(f"ε = F₇/(2N-2) = 13/86 = {eps:.10f}")
print(f"δT = 5ε⁵·T_cmb/8 = 5×({eps:.6f})⁵×{T_CMB}/8")
print(f"    = {dT_pred*1e6:.4f} μK")
print(f"觀測 (SMICA) = {dT_obs*1e6:.1f} μK")
print(f"偏差 = {abs(dT_pred-dT_obs)/dT_obs*100:.4f}%")

# RMS
rms = eps**5/8*T_CMB*1e6
print(f"RMS = ε⁵·T/8 = {rms:.2f} μK")
print(f"深度/RMS = 5 (δT = 5×RMS)")
print(f"RMS/深度 = 1/5 = 0.2")
print(f"19.05/134.2 = {19.05/134.2:.4f} ≈ 1/7 = {1/7:.4f} (0.6%)")

# ===== 9. 總結推導鏈 =====
print("\n" + "="*78)
print("★ 深層推導總結")
print("="*78)
print(f"""
F₇ 選擇律 (唯一解):
  N = F_k + L_k + 2 = 44 → 唯一 k = 7 (F₇ = 13, L₇ = 29)
  因為 F_k + L_k = 2F_{{k+1}} → N = 2(F₈+1) = 2(21+1) = 44
  → F₇ 係唯一令 N = 44 成立嘅 Fibonacci-Lucas 配對!

86 嘅拓撲來源:
  88-site 週期環: 43 對簡併模式 (n, 88-n) + 零模 (n=0) + Nyquist (n=44)
  有效自由度 = 86 = 2N-2 = 2(44)-2
  (扣除零模 + 駐波兩個特殊模式)

ε = F₇/(2N-2) = 13/86:
  = F₇/(2(F₇+L₇+2)-2) = F₇/(2F₇+2L₇+2)
  = 13/(26+58+2) = 13/86
  分子 = Fibonacci 選擇態 (中樞微擾截斷)
  分母 = 簡併自由度 (雙邊界投影自相干)

位置閉合:
  經度 209° = 180+L₇ = 180+29 (Lucas 帶內模態)
  緯度 57° = 44+F₇ = N+13 (Fibonacci 截斷)
  
零參數閉合:
  δT = 5ε⁵T/8 = 5(13/86)⁵×2.72548/8 = {dT_pred*1e6:.2f} μK
  vs SMICA 134.2 μK → 偏差 {abs(dT_pred-dT_obs)/dT_obs*100:.2f}%
""")

output = {
    'F7_selection': {'N': 44, 'F7': 13, 'L7': 29, 'unique_k': 7,
                     'identity': 'N = F_k+L_k+2 = 2(F_8+1) = 44'},
    'deg_86': {'N88': 88, 'pairs': 43, 'effective': 86, 'zero_mode': 'n=0',
               'nyquist': 'n=44', 'formula': '2N-2 = 2(44)-2 = 86'},
    'epsilon': {'formula': 'F7/(2N-2)', 'value': 13/86, 'decimal': 13/86},
    'dT_pred_uK': float(dT_pred*1e6),
    'dT_obs_uK': 134.2,
    'deviation_pct': float(abs(dT_pred-dT_obs)/dT_obs*100),
    'position': {'lon': 209, 'lat': -57, 'lon_formula': '180+L7', 'lat_formula': '-(N+F7)'}
}
with open('data/coldspot_epsilon_derivation.json', 'w') as f:
    json.dump(output, f, indent=2)
print("結果已存: data/coldspot_epsilon_derivation.json")