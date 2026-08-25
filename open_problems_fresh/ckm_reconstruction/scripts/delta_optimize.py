"""
IDCM v10.0 — CKM δ_CP 精確微調
================================
目標: 搵最佳 δ 值同時匹配 V_td, V_ts, J_CP
"""

import math
import numpy as np
import cmath

φ = (1 + math.sqrt(5)) / 2
N_d = 44
ω = np.array([2 * abs(math.sin(math.pi * n / 88)) for n in range(1, N_d + 1)])

def beat(i, j):
    return abs(ω[i-1] - ω[j-1])

# Beat 公式角度 (固定)
θ12 = math.atan(beat(5,6)/beat(19,25))
θ23 = math.atan(beat(33,35)/beat(3,22))
θ13 = math.asin(min(beat(42,43)/beat(10,31), 1.0))

s12, s23, s13 = math.sin(θ12), math.sin(θ23), math.sin(θ13)
c12, c23, c13 = math.cos(θ12), math.cos(θ23), math.cos(θ13)

# PDG 參考
V_td_pdg = 0.00857
V_ts_pdg = 0.04110
J_CP_pdg = 3.08e-5

print("=" * 80)
print("CKM δ_CP 精確微調 🎯")
print("=" * 80)
print(f"\n  固定角度 (beat 公式):")
print(f"    θ₁₂ = {math.degrees(θ12):.4f}°")
print(f"    θ₂₃ = {math.degrees(θ23):.4f}°")
print(f"    θ₁₃ = {math.degrees(θ13):.4f}°")

# 掃描 δ 從 0° 到 180°
print(f"\n  δ 掃描 (0°-180°):")
print(f"  {'δ (°)':>8} | {'V_td':>10} | {'V_ts':>10} | {'J_CP':>12} | {'V_td err':>10} | {'V_ts err':>10} | {'J_CP err':>10} | {'total':>10}")
print("-" * 85)

best = None
best_err = float('inf')

for δ_deg in [d/10 for d in range(0, 1801)]:
    δ = math.radians(δ_deg)
    
    # CKM 矩陣
    V = np.zeros((3, 3), dtype=complex)
    V[0,0] = c12*c13; V[0,1] = s12*c13; V[0,2] = s13*cmath.exp(-1j*δ)
    V[1,0] = -s12*c23 - c12*s23*s13*cmath.exp(1j*δ)
    V[1,1] = c12*c23 - s12*s23*s13*cmath.exp(1j*δ)
    V[1,2] = s23*c13
    V[2,0] = s12*s23 - c12*c23*s13*cmath.exp(1j*δ)
    V[2,1] = -c12*s23 - s12*c23*s13*cmath.exp(1j*δ)
    V[2,2] = c23*c13
    
    V_abs = np.abs(V)
    J = np.imag(V[0,0]*V[1,1]*np.conj(V[0,1])*np.conj(V[1,0]))
    
    V_td_val = V_abs[2, 0]
    V_ts_val = V_abs[2, 1]
    
    err_td = abs(V_td_val - V_td_pdg) / V_td_pdg
    err_ts = abs(V_ts_val - V_ts_pdg) / V_ts_pdg
    err_j = abs(J - J_CP_pdg) / J_CP_pdg
    total = err_td + err_ts + err_j
    
    if total < best_err:
        best_err = total
        best = (δ_deg, V_td_val, V_ts_val, J, err_td, err_ts, err_j, total)

# 顯示最佳附近
for δ_deg in [d for d in range(0, 181)]:
    δ = math.radians(δ_deg)
    
    V = np.zeros((3, 3), dtype=complex)
    V[0,0] = c12*c13; V[0,1] = s12*c13; V[0,2] = s13*cmath.exp(-1j*δ)
    V[1,0] = -s12*c23 - c12*s23*s13*cmath.exp(1j*δ)
    V[1,1] = c12*c23 - s12*s23*s13*cmath.exp(1j*δ)
    V[1,2] = s23*c13
    V[2,0] = s12*s23 - c12*c23*s13*cmath.exp(1j*δ)
    V[2,1] = -c12*s23 - s12*c23*s13*cmath.exp(1j*δ)
    V[2,2] = c23*c13
    
    V_abs = np.abs(V)
    J = np.imag(V[0,0]*V[1,1]*np.conj(V[0,1])*np.conj(V[1,0]))
    
    V_td_val = V_abs[2, 0]
    V_ts_val = V_abs[2, 1]
    
    err_td = abs(V_td_val - V_td_pdg) / V_td_pdg * 100
    err_ts = abs(V_ts_val - V_ts_pdg) / V_ts_pdg * 100
    err_j = abs(J - J_CP_pdg) / J_CP_pdg * 100
    
    if max(err_td, err_ts, err_j) < 10 or δ_deg in [0, 30, 60, 72, 90, 108, 120, 144, 180]:
        print(f"  {δ_deg:>8.1f} | {V_td_val:>10.5f} | {V_ts_val:>10.5f} | {J:>12.2e} | {err_td:>9.2f}% | {err_ts:>9.2f}% | {err_j:>9.2f}% | {err_td+err_ts+err_j:>9.2f}%")

# 最佳 δ
print(f"\n  🎯 最佳 δ:")
δ_best = best[0]
δ = math.radians(δ_best)

V = np.zeros((3, 3), dtype=complex)
V[0,0] = c12*c13; V[0,1] = s12*c13; V[0,2] = s13*cmath.exp(-1j*δ)
V[1,0] = -s12*c23 - c12*s23*s13*cmath.exp(1j*δ)
V[1,1] = c12*c23 - s12*s23*s13*cmath.exp(1j*δ)
V[1,2] = s23*c13
V[2,0] = s12*s23 - c12*c23*s13*cmath.exp(1j*δ)
V[2,1] = -c12*s23 - s12*c23*s13*cmath.exp(1j*δ)
V[2,2] = c23*c13

V_abs = np.abs(V)

print(f"    δ = {δ_best:.2f}°")
print(f"    V_td = {V_abs[2,0]:.5f} (PDG 0.00857, err {best[4]*100:.2f}%)")
print(f"    V_ts = {V_abs[2,1]:.5f} (PDG 0.04110, err {best[5]*100:.2f}%)")
print(f"    J_CP = {best[3]:.2e} (PDG 3.08e-5, err {best[6]*100:.2f}%)")

# 完整 CKM 矩陣
print(f"\n  完整 CKM 矩陣 (δ={δ_best:.2f}°):")
V_PDG = np.array([[0.97435, 0.22500, 0.00369],
                   [0.22486, 0.97349, 0.04182],
                   [0.00857, 0.04110, 0.99912]])

print(f"  {'元素':>8} | {'IDCM':>10} | {'PDG':>10} | {'偏差':>10}")
print("-" * 45)
for label, i, j in [("V_ud",0,0), ("V_us",0,1), ("V_ub",0,2),
                     ("V_cd",1,0), ("V_cs",1,1), ("V_cb",1,2),
                     ("V_td",2,0), ("V_ts",2,1), ("V_tb",2,2)]:
    err = abs(V_abs[i,j] - V_PDG[i,j]) / V_PDG[i,j] * 100
    print(f"  {label:>8} | {V_abs[i,j]:>10.5f} | {V_PDG[i,j]:>10.5f} | {err:>9.2f}%")

# 儲存最佳矩陣
np.save("open_problems_fresh/ckm_reconstruction/V_ckm_optimal.npy", V)
print(f"\n  已儲存最佳 CKM 矩陣 ✅")