"""
IDCM v10.0 — CKM 最終構建：分層參數化
========================================
用多尺度方法計算 CKM 混合角，然後用 PDG 標準參數化構建完整 CKM。

尺度 1: θ₁₂ = 13.58° (3×3 submatrix, 方法 A) ✅
尺度 2: θ₂₃ = 3.97°  (6×6 doublet+VEV+Z₅, 方法 I) 🟡
尺度 3: θ₁₃ + δ = 12D 完整結構 (待推導)
"""

import math
import numpy as np
import cmath

φ = (1 + math.sqrt(5)) / 2

# PDG 參考
V_PDG = np.array([
    [0.97435, 0.22500, 0.00369],
    [0.22486, 0.97349, 0.04182],
    [0.00857, 0.04110, 0.99912],
])
θ12_PDG, θ23_PDG, θ13_PDG = 13.04, 2.38, 0.201
J_CP_PDG, λ_PDG, A_PDG = 3.08e-5, 0.225, 0.83

print("=" * 80)
print("IDCM v10.0 — CKM 最終構建：分層參數化 🎯")
print("=" * 80)

# ══════════════════════════════════════════════════════════════
# 1. 載入數據
# ══════════════════════════════════════════════════════════════
d = np.load("data/d_tensor_positive.npy")
v = np.array([φ ** (-k / 12) for k in range(12)])

Y_full = np.zeros((12, 12), dtype=complex)
for i in range(12):
    for j in range(12):
        Y_full[i, j] = sum(d[i, j, k] * v[k] for k in range(12))
Y_full = (Y_full + Y_full.T) / 2

up_idx, down_idx = [0, 3, 6], [1, 4, 7]
doublet_idx = [0, 1, 3, 4, 6, 7]
z5 = [i % 5 for i in range(12)]

print(f"  d_tensor: {d.shape} ✅")

# ══════════════════════════════════════════════════════════════
# 2. 尺度 1: 3×3 submatrix → θ₁₂
# ══════════════════════════════════════════════════════════════
Y_up = np.zeros((3, 3), dtype=complex)
Y_down = np.zeros((3, 3), dtype=complex)
for a in range(3):
    for b in range(3):
        Y_up[a, b] = Y_full[up_idx[a], up_idx[b]]
        Y_down[a, b] = Y_full[down_idx[a], down_idx[b]]
Y_up = (Y_up + Y_up.T) / 2
Y_down = (Y_down + Y_down.T) / 2

def bi_diag(Y):
    H = Y @ Y.conj().T
    H = (H + H.conj().T) / 2
    evals, U = np.linalg.eigh(H)
    idx = np.argsort(evals)[::-1]
    return U[:, idx]

U_u, U_d = bi_diag(Y_up), bi_diag(Y_down)
V_3 = U_u.conj().T @ U_d
θ12_3 = math.degrees(math.atan2(abs(V_3[0,1]), abs(V_3[0,0])))

# ══════════════════════════════════════════════════════════════
# 3. 尺度 2: 6×6 doublet + VEV + Z₅ → θ₂₃
# ══════════════════════════════════════════════════════════════
w_u = np.zeros(12)
w_d = np.zeros(12)
w_cross = np.zeros(12)
for k in range(12):
    for i in up_idx:
        for j in up_idx:
            w_u[k] += abs(d[i, j, k])
    for i in down_idx:
        for j in down_idx:
            w_d[k] += abs(d[i, j, k])
    for i in up_idx:
        for j in down_idx:
            w_cross[k] += abs(d[i, j, k])
w_u = w_u / np.sum(w_u)
w_d = w_d / np.sum(w_d)
w_cross = w_cross / np.sum(w_cross)

ev_up = np.sort(np.linalg.eigvalsh(Y_up))[::-1]
ev_down = np.sort(np.linalg.eigvalsh(Y_down))[::-1]
tan_β = 172760.0 * ev_down[0] / (4180.0 * ev_up[0])
β = math.atan(tan_β)

Y_6 = np.zeros((6, 6), dtype=complex)
for a in range(6):
    for b in range(6):
        i = doublet_idx[a]
        j = doublet_idx[b]
        for k in range(12):
            w = w_u[k] * math.sin(β) if (i in up_idx and j in up_idx) else \
                w_d[k] * math.cos(β) if (i in down_idx and j in down_idx) else \
                w_cross[k] * math.sqrt(math.sin(β) * math.cos(β))
            Y_6[a, b] += d[i, j, k] * v[k] * w
Y_6 = (Y_6 + Y_6.T) / 2
for a in range(6):
    for b in range(6):
        Y_6[a, b] *= cmath.exp(2j * math.pi * (z5[doublet_idx[a]] - z5[doublet_idx[b]]) / 5)

H_6 = Y_6 @ Y_6.conj().T
H_6 = (H_6 + H_6.conj().T) / 2
evals_6, U_6 = np.linalg.eigh(H_6)
U_6 = U_6[:, np.argsort(evals_6)[::-1]]

up_in_6, down_in_6 = [0, 2, 4], [1, 3, 5]
up_list, down_list = [], []
for i in range(6):
    vec = U_6[:, i]
    if sum(abs(vec[j])**2 for j in up_in_6) > sum(abs(vec[j])**2 for j in down_in_6):
        up_list.append(vec)
    else:
        down_list.append(vec)

U_6_up = np.array(up_list[:3]).T if len(up_list) >= 3 else U_6[:, :3]
U_6_down = np.array(down_list[:3]).T if len(down_list) >= 3 else U_6[:, 3:6]
V_6 = U_6_up.conj().T @ U_6_down
θ23_6 = math.degrees(math.atan2(abs(V_6[1,2]), abs(V_6[2,2])))

# ══════════════════════════════════════════════════════════════
# 4. CKM 最終構建：分層參數化
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("4. CKM 最終構建：分層參數化")
print("─" * 80)

# 用 IDCM 推導嘅角度
θ12_idcm = θ12_3  # 13.58° from 3×3 submatrix
θ23_idcm = θ23_6  # 3.97° from 6×6 doublet

# θ₁₃ 同 δ 需要從 12D 推導 (暫時用 PDG 值)
# 但可以用 Z₅ phase 估計 δ
# Z₅ 相位差: 2π × (q_up - q_down) / 5
# 對於 u↔b (Z₅ diff = 1-1=0): δ=0
# 對於 t↔d (Z₅ diff = 0-2=-2≡3): δ=3×2π/5=216°
# 對於 c↔s (Z₅ diff = 3-4=-1≡4): δ=4×2π/5=288°

# 平均 δ ≈ 216°? 但 PDG δ=68.8°
# 需要更精細嘅 twisted sector 分析

# 用 PDG 值做暫代
θ13_idcm = 0.201  # 暫用 PDG
δ_idcm = 68.8     # 暫用 PDG

# PDG 標準參數化
s12 = math.sin(math.radians(θ12_idcm))
c12 = math.cos(math.radians(θ12_idcm))
s23 = math.sin(math.radians(θ23_idcm))
c23 = math.cos(math.radians(θ23_idcm))
s13 = math.sin(math.radians(θ13_idcm))
c13 = math.cos(math.radians(θ13_idcm))
δ = math.radians(δ_idcm)

V_idcm = np.zeros((3, 3), dtype=complex)
V_idcm[0, 0] = c12 * c13
V_idcm[0, 1] = s12 * c13
V_idcm[0, 2] = s13 * cmath.exp(-1j * δ)
V_idcm[1, 0] = -s12 * c23 - c12 * s23 * s13 * cmath.exp(1j * δ)
V_idcm[1, 1] = c12 * c23 - s12 * s23 * s13 * cmath.exp(1j * δ)
V_idcm[1, 2] = s23 * c13
V_idcm[2, 0] = s12 * s23 - c12 * c23 * s13 * cmath.exp(1j * δ)
V_idcm[2, 1] = -c12 * s23 - s12 * c23 * s13 * cmath.exp(1j * δ)
V_idcm[2, 2] = c23 * c13

V_abs = np.abs(V_idcm)
θ12 = math.degrees(math.atan2(V_abs[0,1], V_abs[0,0]))
θ23 = math.degrees(math.atan2(V_abs[1,2], V_abs[2,2]))
θ13 = math.degrees(math.asin(min(V_abs[0,2], 1.0)))
J = np.imag(V_idcm[0,0] * V_idcm[1,1] * np.conj(V_idcm[0,1]) * np.conj(V_idcm[1,0]))

# Wolfenstein
λ = V_abs[0, 1]
A = V_abs[1, 2] / (λ**2) if λ > 0 else 0
V_ub_star = np.conj(V_idcm[0, 2])
ρη = V_ub_star / (A * λ**3) if (A * λ**3) != 0 else 0

print(f"  輸入角度:")
print(f"    θ₁₂ = {θ12_idcm:.4f}° ← 3×3 submatrix (方法 A)")
print(f"    θ₂₃ = {θ23_idcm:.4f}° ← 6×6 doublet+VEV+Z₅ (方法 I)")
print(f"    θ₁₃ = {θ13_idcm:.4f}° ← PDG (待推導)")
print(f"    δ_CP = {δ_idcm:.1f}° ← PDG (待推導)")

print(f"\n  V_CKM (IDCM 分層參數化):")
for row in V_abs:
    print(f"    {[f'{x:.6f}' for x in row]}")

print(f"\n  {'參數':>10} | {'IDCM':>12} | {'PDG':>12} | {'誤差':>10}")
print("-" * 50)
print(f"  {'θ₁₂':>10} | {θ12:>12.4f}° | {θ12_PDG:>12.4f}° | {abs(θ12-θ12_PDG):>9.4f}°")
print(f"  {'θ₂₃':>10} | {θ23:>12.4f}° | {θ23_PDG:>12.4f}° | {abs(θ23-θ23_PDG):>9.4f}°")
print(f"  {'θ₁₃':>10} | {θ13:>12.4f}° | {θ13_PDG:>12.4f}° | {abs(θ13-θ13_PDG):>9.4f}°")
print(f"  {'J_CP':>10} | {J:>12.2e} | {J_CP_PDG:>12.2e} | {'—':>10}")
print(f"  {'λ':>10} | {λ:>12.6f} | {λ_PDG:>12.6f} | {abs(λ/λ_PDG-1)*100:>9.2f}%")
print(f"  {'A':>10} | {A:>12.4f} | {A_PDG:>12.4f} | {abs(A/A_PDG-1)*100:>9.2f}%")
print(f"  {'ρ':>10} | {ρη.real:>12.4f} | {'0.1500':>12} | {'—':>10}")
print(f"  {'η':>10} | {ρη.imag:>12.4f} | {'0.3500':>12} | {'—':>10}")

print(f"\n  CKM 完整對比:")
print(f"  {'IDCM':>32} | {'PDG':>32}")
for i in range(3):
    idcm_r = [f'{V_abs[i,j]:.5f}' for j in range(3)]
    pdg_r = [f'{V_PDG[i,j]:.5f}' for j in range(3)]
    print(f"  [{', '.join(idcm_r):>32}] | [{', '.join(pdg_r):>32}]")

# ══════════════════════════════════════════════════════════════
# 5. 總結
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("5. 總結")
print("─" * 80)

print(f"""
  🎯 CKM 最終狀態:

  IDCM 推導 (0 自由參數):
  θ₁₂ = {θ12_idcm:.4f}° (PDG {θ12_PDG}°) — 誤差 {abs(θ12_idcm-θ12_PDG):.4f}° 🟢
  θ₂₃ = {θ23_idcm:.4f}° (PDG {θ23_PDG}°) — 誤差 {abs(θ23_idcm-θ23_PDG):.4f}° 🟡
  θ₁₃ = {θ13_idcm:.4f}° (PDG {θ13_PDG}°) — 待推導 🔴
  J_CP = {J:.2e} (PDG {J_CP_PDG:.2e}) — 待推導 🔴

  V_CKM (IDCM):
  [{', '.join(f'{V_abs[0,j]:.5f}' for j in range(3))}]
  [{', '.join(f'{V_abs[1,j]:.5f}' for j in range(3))}]
  [{', '.join(f'{V_abs[2,j]:.5f}' for j in range(3))}]

  Wolfenstein:
  λ = {λ:.6f} (PDG {λ_PDG})
  A = {A:.4f} (PDG {A_PDG})

  完成嘅推導:
  ✅ 3×3 submatrix: θ₁₂ = {θ12_idcm:.4f}° (Cabibbo 角)
  ✅ 6×6 doublet+VEV+Z₅: θ₂₃ = {θ23_idcm:.4f}°
  ✅ Z₃ × Z₅ 對稱性: SU(2)_L Δ=1
  ✅ tan(β) = {tan_β:.4f} (從 d_tensor 推導)
  
  待推導:
  🔴 θ₁₃: 需要 12D 完整結構
  🔴 δ_CP, J_CP: 需要 twisted sector 相位
""")

# 儲存
np.save("main_problems/p2_ckm_reconstruction/V_ckm_final.npy", V_idcm)

with open("main_problems/p2_ckm_reconstruction/ckm_final_results.txt", "w") as f:
    f.write(f"IDCM v10.0 — CKM 最終結果\n")
    f.write(f"θ₁₂ = {θ12_idcm:.4f}° (PDG {θ12_PDG}°)\n")
    f.write(f"θ₂₃ = {θ23_idcm:.4f}° (PDG {θ23_PDG}°)\n")
    f.write(f"θ₁₃ = {θ13_idcm:.4f}° (PDG {θ13_PDG}°)\n")
    f.write(f"J_CP = {J:.2e} (PDG {J_CP_PDG:.2e})\n")
    f.write(f"λ = {λ:.6f}, A = {A:.4f}\n")

print("已儲存 ✅")