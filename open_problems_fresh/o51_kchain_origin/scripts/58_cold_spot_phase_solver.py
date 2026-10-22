#!/usr/bin/env python3
"""
O51/58: Cold Spot Phase Solver — 解 N 嘅精確方程
===============================================================
調律者提供嘅空間相位映射:
  φ_n(θ, φ) = n·[φ·cos(F₇/L₇) + θ·sin(B/N_d)] + 2π·n·(L₇+F₇)/N_d

冷斑條件: Ψ(209°,-57°) = arg(Σ A_n·exp(i(N·δ_n + ω_n·τ - φ_n))) = π

已知: τ = R_H/c = 13.470 Gyr, N ∈ [0, 2072]
"""
import json, math, sys

# ============ 1. 結構參數 ============
N_d = 44
B = 4
L_7 = 29
F_7 = 13

# 冷斑位置 (Galactic)
l_cold = 209.0   # 經度 φ
b_cold = -57.0   # 緯度
θ_cold = 90.0 - b_cold  # 餘緯度 = 147°

# ============ 2. K_Chain 參數 ============
R_H = 4129.94   # Mpc
c = 306.601394  # Mpc/Gyr
T_sync = 2 * math.pi * R_H / c  # Gyr
τ = R_H / c  # 13.470 Gyr, 觀察者「而家」

# 模式振幅 A_n = 2·sin(πn/88)
A_n = [2 * math.sin(math.pi * n / 88) for n in range(1, 45)]

# 43 個漂移 δ_n = frac(88·sin(πn/88))
deltas = {}
for n in range(1, 44):
    theta = 88 * math.sin(math.pi * n / 88)
    delta = theta - math.floor(theta)
    deltas[n] = delta

# ω_n·τ (以 2π 計)
omega_n_tau = {}
for n in range(1, 45):
    phase = 88 * math.sin(math.pi * n / 88) * τ / T_sync
    omega_n_tau[n] = phase

# ============ 3. 空間相位 φ_n(冷斑) ============
# φ_n = n·[φ·cos(F₇/L₇) + θ·sin(B/N_d)] + 2π·n·(L₇+F₇)/N_d
# φ, θ 用弧度
phi_cold = math.radians(l_cold)
theta_cold = math.radians(θ_cold)

cos_F7_L7 = math.cos(F_7 / L_7)
sin_B_Nd = math.sin(B / N_d)

print("=" * 62)
print("冷斑相位求解器 (N 精確鎖定)")
print("=" * 62)

print(f"\n結構參數:")
print(f"  N_d = {N_d}, B = {B}")
print(f"  L₇ = {L_7}, F₇ = {F_7}")
print(f"  L₇+F₇ = {L_7+F_7}")
print(f"  (L₇+F₇)/N_d = {(L_7+F_7)/N_d} = {L_7+F_7}/{N_d}")
print(f"  cos(F₇/L₇) = {cos_F7_L7:.6f}")
print(f"  sin(B/N_d) = {sin_B_Nd:.6f}")

# 計算 φ_n
phi_n_cold = {}
for n in range(1, 45):
    # 弧度版本
    phi_rad = n * (phi_cold * cos_F7_L7 + theta_cold * sin_B_Nd) + 2 * math.pi * n * (L_7 + F_7) / N_d
    phi_n_cold[n] = phi_rad

print(f"\n冷斑座標: l={l_cold}°, b={b_cold}°")
print(f"  φ(經度, 弧度) = {phi_cold:.6f}")
print(f"  θ(餘緯度, 弧度) = {theta_cold:.6f}")
print(f"\n前 5 個模式嘅空間相位 φ_n:")
for n in range(1, 6):
    phi_mod = phi_n_cold[n] % (2*math.pi)
    print(f"  n={n}: φ_n = {phi_n_cold[n]:.4f} rad → mod 2π = {phi_mod:.4f}")

# ============ 4. 向量和求解 N ============
print(f"\n{'=' * 62}")
print(f"向量和求解 N (τ = {τ:.4f} Gyr)")
print(f"{'=' * 62}")

def vector_sum(N, tau_frac):
    """計算 Σ A_n·exp(i(θ_n - φ_n))"""
    sum_real = 0.0
    sum_imag = 0.0
    for n in range(1, 45):
        # 模式相位 θ_n = N·δ_n + ω_n·τ
        if n < 44:
            theta_n = 2 * math.pi * (N * deltas[n] + omega_n_tau[n])
        else:
            # n=44: δ_44 = 0 (整數), ω_44·τ = 88·τ/T_sync
            theta_n = 2 * math.pi * (N * 0 + omega_n_tau[n])
        
        # 總相位 = θ_n - φ_n
        total_phase = theta_n - phi_n_cold[n]
        sum_real += A_n[n-1] * math.cos(total_phase)
        sum_imag += A_n[n-1] * math.sin(total_phase)
    
    return sum_real, sum_imag

# 掃描 N=0..2072, τ=0.159155 (R_H/c)
tau_frac = τ / T_sync
print(f"τ/T_sync = {tau_frac:.6f}")

best_N = 0
best_Ψ_error = 1e10
best_Ψ = 0
best_mag = 0

print(f"\n掃描 N=0..2000...")
for N in range(0, 2001):
    re, im = vector_sum(N, tau_frac)
    Ψ = math.atan2(im, re)  # -π..π
    mag = math.sqrt(re**2 + im**2)
    
    # Ψ 應 = π (mod 2π)
    # 誤差: dist_from_pi = min(|Ψ - π|, |Ψ + π|)
    err = min(abs(Ψ - math.pi), abs(Ψ + math.pi))
    
    if err < best_Ψ_error:
        best_Ψ_error = err
        best_N = N
        best_Ψ = Ψ
        best_mag = mag
        best_re = re
        best_im = im

print(f"\n最佳解:")
print(f"  N = {best_N}")
print(f"  Ψ = {best_Ψ:.6f} rad (目標 π = {math.pi:.6f} rad)")
print(f"  誤差 = {best_Ψ_error:.6f} rad")
print(f"  向量幅度 = {best_mag:.6f}")
print(f"  向量和 = ({best_re:.6f}, {best_im:.6f})")

# 冷斑溫度
A = 134.2  # μK
T_cold = A * math.cos(best_Ψ)
print(f"  冷斑溫度 T = A·cos(Ψ) = {T_cold:.2f} μK (觀測 = -134.19 μK)")
print(f"  差異 = {abs(T_cold - (-134.19)):.2f} μK")

# 真實年齡
t_true = best_N * T_sync + τ
print(f"\n  真實年齡 t_true = {best_N} × {T_sync:.4f} + {τ:.4f} = {t_true:.4f} Gyr")

# ============ 5. 局部精細掃描 (around best N) ============
print(f"\n局部精細 (N={best_N-2}..{best_N+2}):")
for N in range(max(0, best_N-2), best_N+3):
    re, im = vector_sum(N, tau_frac)
    Ψ = math.atan2(im, re)
    err = min(abs(Ψ - math.pi), abs(Ψ + math.pi))
    T = A * math.cos(Ψ)
    print(f"  N={N:4d}: Ψ={Ψ:.4f} rad, err={err:.6f} rad, T={T:.2f} μK")

# ============ 6. N=0 特殊情況 (ΛCDM 年齡最接近) ============
print(f"\nN=0 特殊情況:")
re0, im0 = vector_sum(0, tau_frac)
Ψ0 = math.atan2(im0, re0)
err0 = min(abs(Ψ0 - math.pi), abs(Ψ0 + math.pi))
T0 = A * math.cos(Ψ0)
print(f"  Ψ={Ψ0:.4f} rad, err={err0:.6f} rad, T={T0:.2f} μK")
print(f"  t_true = 0 + {τ:.4f} = {τ:.4f} Gyr")

# ============ 7. 結果輸出 ============
result = {
    'N': best_N,
    'Psi_rad': round(best_Ψ, 6),
    'Psi_error_rad': round(best_Ψ_error, 6),
    'vector_magnitude': round(best_mag, 6),
    'T_cold_uK': round(T_cold, 2),
    'T_obs_uK': -134.19,
    'T_diff_uK': round(abs(T_cold - (-134.19)), 2),
    'tau_gyr': round(τ, 4),
    'T_sync_gyr': round(T_sync, 4),
    't_true_gyr': round(t_true, 4),
    'N_0_Psi': round(Ψ0, 6),
    'N_0_err': round(err0, 6),
    'N_0_T': round(T0, 2)
}

with open('data/58_phase_solution.json', 'w') as f:
    json.dump(result, f, indent=2)

print(f"\n✅ 結果已存: data/58_phase_solution.json")