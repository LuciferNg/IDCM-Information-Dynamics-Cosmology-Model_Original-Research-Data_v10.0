"""
IDCM v10.0 — CKM 矩陣 + Jarlskog J_CP 計算
============================================
從 d_tensor_final 直接計算 Yukawa 矩陣同混合角
"""

import math
import numpy as np

# ============================================================
# 1. 載入 d_tensor
# ============================================================
d = np.load("data/d_tensor_final.npy")
assert d.shape == (12, 12, 12), f"Shape: {d.shape}"

# 12 個 Kähler moduli 嘅世代/sector 分配
# 按最終盲測嘅分配:
# Gen 3: idx 0=up(Top), 1=down(Bottom), 2=lep(Tau)
# Gen 2: idx 3=up(Charm), 4=down(Strange), 5=lep(Muon)
# Gen 1: idx 6=up(Up), 7=down(Down), 8=lep(Electron), 9=n1(ν_τ), 10=n2(ν_μ)
# idx 11 = Goldstone (零態)

# 每個 sector 嘅 index 對應
sector_indices = {
    "up": [0, 3, 6],      # Top, Charm, Up
    "down": [1, 4, 7],     # Bottom, Strange, Down
    "lep": [2, 5, 8],      # Tau, Muon, Electron
    "nu": [9, 10],         # ν_τ, ν_μ
}

# 已知質量 (MeV)
masses = {
    "up": [172760.0, 1270.0, 2.16],
    "down": [4180.0, 93.4, 4.67],
    "lep": [1776.86, 105.658, 0.51099895],
}

print("=" * 70)
print("IDCM v10.0 — CKM 矩陣計算")
print("=" * 70)

# ============================================================
# 2. 構建 Yukawa 矩陣
# ============================================================
# 用 d_tensor 同 VEV 方向 v 構建 Yukawa 矩陣:
# Y_{ab} = Σ_c d_{abc} × v_c

# VEV 方向: 由 V_cycle 同 tanβ 決定
# 假設 VEV 沿住每個世代嘅 "up" 方向
# 用之前校準嘅 V_cycle 值
V_cycles = [42.7396, 44.9431, 46.5390]  # Gen 3, 2, 1

# 構建 VEV 向量 v (12 維)
# 每個世代嘅 VEV 強度由 e^{-V_cycle} 決定
# tanβ = 7.5 影響 down-type 同 lepton
tanβ = 7.5

v = np.zeros(12)
sector_weight = {"up": 1.0, "down": 1.0/7.5, "lep": 1.0/8.6, "nu": 1.0}

# Gen 3
v[0] = math.exp(-V_cycles[0]) * sector_weight["up"]    # Top
v[1] = math.exp(-V_cycles[0]) * sector_weight["down"]  # Bottom
v[2] = math.exp(-V_cycles[0]) * sector_weight["lep"]   # Tau
# Gen 2
v[3] = math.exp(-V_cycles[1]) * sector_weight["up"]    # Charm
v[4] = math.exp(-V_cycles[1]) * sector_weight["down"]  # Strange
v[5] = math.exp(-V_cycles[1]) * sector_weight["lep"]   # Muon
# Gen 1
v[6] = math.exp(-V_cycles[2]) * sector_weight["up"]    # Up
v[7] = math.exp(-V_cycles[2]) * sector_weight["down"]  # Down
v[8] = math.exp(-V_cycles[2])  # Electron (calibration)
v[9] = math.exp(-V_cycles[2]) * 1.0  # ν_τ
v[10] = math.exp(-V_cycles[2]) * 1.0  # ν_μ
v[11] = 0.0  # Goldstone

print(f"\nVEV 向量: {v}")

# 構建 3×3 Yukawa 矩陣 for each sector
yukawas = {}
for sector, idxs in sector_indices.items():
    if len(idxs) < 3:
        continue
    Y = np.zeros((3, 3), dtype=complex)
    for a in range(3):
        for b in range(3):
            i = idxs[a]
            j = idxs[b]
            # Y_{ab} = Σ_c d_{abc} × v_c
            # 但 d 係 12×12×12, 需要正確嘅 index mapping
            # 用 full 12×12 Yukawa matrix
            val = 0.0
            for c in range(12):
                val += d[i, j, c] * v[c]
            Y[a, b] = val
    yukawas[sector] = Y
    print(f"\n{sector} Yukawa matrix:")
    for row in Y:
        print(f"  {row}")

# ============================================================
# 3. 對角化 Yukawa 矩陣
# ============================================================
print(f"\n{'='*70}")
print("Yukawa 矩陣對角化")
print(f"{'='*70}")

eigenvectors = {}
for sector in ["up", "down"]:
    Y = yukawas[sector]
    # 對稱化
    Y_sym = (Y + Y.T) / 2
    evals, evecs = np.linalg.eigh(Y_sym)
    
    # 排序 (由大到小)
    idx = np.argsort(evals)[::-1]
    evals = evals[idx]
    evecs = evecs[:, idx]
    
    print(f"\n{sector} sector:")
    print(f"  Eigenvalues: {evals}")
    print(f"  Expected: {masses[sector]}")
    
    eigenvectors[sector] = evecs

# ============================================================
# 4. CKM 矩陣
# ============================================================
print(f"\n{'='*70}")
print("CKM 夸克混合矩陣")
print(f"{'='*70}")

# V_CKM = U_u^† × U_d
U_u = eigenvectors["up"]
U_d = eigenvectors["down"]

V_CKM = U_u.conj().T @ U_d

print(f"\nV_CKM 矩陣:")
np.set_printoptions(precision=6, suppress=True)
print(f"  |V_ud| |V_us| |V_ub|")
print(f"  |V_cd| |V_cs| |V_cb|")
print(f"  |V_td| |V_ts| |V_tb|")
print(f"\n  V_CKM = ")
for row in np.abs(V_CKM):
    print(f"    {row}")

# PDG 參考
V_CKM_PDG = np.array([
    [0.97435, 0.2250, 0.00369],
    [0.22486, 0.97349, 0.04182],
    [0.00857, 0.04110, 0.999118],
])

print(f"\n  PDG 2024:")
for row in V_CKM_PDG:
    print(f"    {row}")

# ============================================================
# 5. Jarlskog 不變量
# ============================================================
print(f"\n{'='*70}")
print("Jarlskog J_CP 不變量")
print(f"{'='*70}")

# J_CP = Im(V_us V_cb V_ub^* V_cs^*)
# Using the standard parameterization
# J = Im(V_11 V_22 V_12^* V_21^*) (for 2×2 sub-block)
# More generally: J = Im(V_ij V_kl V_il^* V_kj^*)

# 用標準公式
J = np.imag(V_CKM[0, 0] * V_CKM[1, 1] * np.conj(V_CKM[0, 1]) * np.conj(V_CKM[1, 0]))
print(f"  J_CP (computed) = {J:.6e}")

# PDG 值
J_PDG = 3.08e-5
print(f"  J_CP (PDG 2024) = {J_PDG:.6e}")

if abs(J) > 0:
    ratio = abs(J) / J_PDG
    print(f"  比例: {ratio:.2f}x")

# ============================================================
# 6. 混合角
# ============================================================
print(f"\n{'='*70}")
print("CKM 混合角")
print(f"{'='*70}")

V_abs = np.abs(V_CKM)

# PDG 混合角
theta_12 = math.asin(V_abs[0, 1])  # Cabibbo
theta_23 = math.asin(V_abs[1, 2])  # 
theta_13 = math.asin(V_abs[0, 2])

print(f"  θ₁₂ (Cabibbo) = {theta_12:.4f} rad = {math.degrees(theta_12):.2f}°")
print(f"  θ₂₃ = {theta_23:.4f} rad = {math.degrees(theta_23):.2f}°")
print(f"  θ₁₃ = {theta_13:.4f} rad = {math.degrees(theta_13):.2f}°")

# PDG 比較
theta_12_PDG = math.asin(0.2250)
theta_23_PDG = math.asin(0.04182)
theta_13_PDG = math.asin(0.00369)
print(f"  PDG θ₁₂ = {math.degrees(theta_12_PDG):.2f}°")
print(f"  PDG θ₂₃ = {math.degrees(theta_23_PDG):.2f}°")
print(f"  PDG θ₁₃ = {math.degrees(theta_13_PDG):.2f}°")

# ============================================================
# 7. 儲存
# ============================================================
np.save("data/ckm_matrix.npy", V_CKM)
np.save("data/yukawa_up.npy", yukawas["up"])
np.save("data/yukawa_down.npy", yukawas["down"])

with open("data/ckm_results.txt", "w") as f:
    f.write("IDCM v10.0 — CKM 矩陣計算結果\n")
    f.write("=" * 60 + "\n\n")
    f.write("V_CKM 矩陣:\n")
    for i, row in enumerate(np.abs(V_CKM)):
        f.write(f"  {row}\n")
    f.write(f"\nJ_CP = {J:.6e}\n")
    f.write(f"J_CP (PDG) = {J_PDG:.6e}\n")
    f.write(f"\n混合角:\n")
    f.write(f"  θ₁₂ = {math.degrees(theta_12):.2f}°\n")
    f.write(f"  θ₂₃ = {math.degrees(theta_23):.2f}°\n")
    f.write(f"  θ₁₃ = {math.degrees(theta_13):.2f}°\n")

print(f"\n已儲存 data/ckm_results.txt ✅")
print(f"已儲存 data/ckm_matrix.npy ✅")