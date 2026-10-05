"""
IDCM v10.0 — P₃×₁₂ 代數投影模型
==================================
12D Kähler 空間 → 3D Flavor 空間投影
CKM 混合角 = 子空間嘅相對幾何夾角
"""

import math
import numpy as np

φ = (1 + math.sqrt(5)) / 2

# ============================================================
# 1. 載入 d_tensor
# ============================================================
d = np.load("data/d_tensor_final.npy")
assert d.shape == (12, 12, 12)

# 12 個 Kähler moduli 嘅世代/sector 分配
# Gen 3: idx 0=up(Top), 1=down(Bottom), 2=lep(Tau)
# Gen 2: idx 3=up(Charm), 4=down(Strange), 5=lep(Muon)
# Gen 1: idx 6=up(Up), 7=down(Down), 8=lep(Electron), 9=n1(ν_τ), 10=n2(ν_μ)
# idx 11 = Goldstone

sector_indices = {
    "up": [0, 3, 6],
    "down": [1, 4, 7],
    "lep": [2, 5, 8],
    "nu": [9, 10],
}

# 已知質量 (MeV) - 用於校準 VEV 方向
masses = {
    "up": [172760.0, 1270.0, 2.16],
    "down": [4180.0, 93.4, 4.67],
    "lep": [1776.86, 105.658, 0.51099895],
}

# V_cycle 值
V_cycles = {"Gen3": 42.7396, "Gen2": 44.9431, "Gen1": 46.5390}

print("=" * 70)
print("IDCM v10.0 — P₃×₁₂ 代數投影模型")
print("=" * 70)

# ============================================================
# 2. 構建 VEV 方向
# ============================================================
# VEV 向量 v (12D):
# 每個世代嘅 VEV 由 e^{-V_cycle} 決定
# 每種 sector 有唔同嘅 scaling (tanβ-like)

# 從盲測校準得到嘅 sector scaling factors
sector_scale = {
    "up": 1.0,
    "down": 1.0/7.5,  # 約 0.133
    "lep": 1.0/8.6,   # 約 0.116
    "nu": 1.0,
}

# 構建 12D VEV 向量
v = np.zeros(12)
for gen_name, gen_idx in [("Gen3", 0), ("Gen2", 1), ("Gen1", 2)]:
    V = V_cycles[gen_name]
    sup = math.exp(-V)
    for sec_name, scale in sector_scale.items():
        sec_idx_map = {"up": 0, "down": 1, "lep": 2, "nu": 3}
        if sec_name in sector_indices:
            sec_list = sector_indices[sec_name]
            for i, idx in enumerate(sec_list):
                if gen_idx < len(sec_list) or True:
                    if gen_idx * 3 + i < 12:
                        pass

# 直接用 WDVV solver 嘅 VEV 方向: v_k = φ^(-k/12)
v = np.array([φ ** (-k / 12) for k in range(12)])

# ============================================================
# 3. 構建 12×12 Yukawa 矩陣
# ============================================================
print(f"\n{'='*70}")
print("12×12 Yukawa 矩陣")
print(f"{'='*70}")

Y_12 = np.zeros((12, 12))
for i in range(12):
    for j in range(12):
        Y_12[i, j] = sum(d[i, j, k] * v[k] for k in range(12))

print(f"Y_12 shape: {Y_12.shape}")
print(f"Y_12 對角元: {np.diag(Y_12)}")

# 對稱化
Y_12_sym = (Y_12 + Y_12.T) / 2

# 對角化
evals_12, evecs_12 = np.linalg.eigh(Y_12_sym)
idx = np.argsort(evals_12)[::-1]
evals_12 = evals_12[idx]
evecs_12 = evecs_12[:, idx]

print(f"\n12 個本徵值:")
for i in range(12):
    print(f"  λ_{i+1:2d} = {evals_12[i]:.6e}")

# 12 個本徵值應該同之前嘅 eigenvalues_final 一致
evals_ref = np.load("data/eigenvalues_final.npy")
ref_pos = sorted([e for e in evals_ref if e > 1e-10], reverse=True)
print(f"\n參考 (eigenvalues_final):")
for i in range(min(11, len(ref_pos))):
    print(f"  λ_{i+1:2d} = {ref_pos[i]:.6f}")

# 比較 (忽略 scaling)
for i in range(11):
    ratio = evals_12[i] / ref_pos[i]
    if abs(ratio) > 1e-10:
        print(f"  ratio {i+1}: {ratio:.4e}")

# 提取 3 個主成分 (dominant eigenvectors)
print(f"\n{'='*70}")
print("P₃×₁₂ 投影矩陣")
print(f"{'='*70}")

# 取前 3 個 eigenvector 做 P₃×₁₂
P_3x12 = evecs_12[:, :3].T  # 3×12

print(f"P (3×12) shape: {P_3x12.shape}")
print(f"P·P^T = I₃:")
print(P_3x12 @ P_3x12.T)

# 檢查 P·P^T = I₃
iso = np.allclose(P_3x12 @ P_3x12.T, np.eye(3), atol=1e-10)
print(f"等距條件滿足: {iso}")

# ============================================================
# 4. Up/Down Sector 投影
# ============================================================
print(f"\n{'='*70}")
print("Up/Down Sector 投影")
print(f"{'='*70}")

# 從 12×12 Yukawa 矩陣提取 up/down sector 嘅 3×3 子矩陣
# 用 P₃×₁₂ 投影: Y_3x3 = P · Y_12 · P^T

Y_up_3 = P_3x12 @ Y_12_sym @ P_3x12.T  # 3×3
Y_down_3 = P_3x12 @ Y_12_sym @ P_3x12.T  # 3×3 (same, but with different VEV)

# 但 up 同 down 嘅 VEV 方向唔同
# 需要分別構建 up 同 down 嘅 VEV 向量

# Up-sector VEV (用 φ^(-k/12) 乘 up-type 嘅 generation scaling)
# 每個世代嘅 up-type 有相同嘅 VEV 方向，但強度由 V_cycle 決定
v_up = np.array([φ ** (-k / 12) for k in range(12)])
# 加入 generation scaling
v_up[0] *= math.exp(-V_cycles["Gen3"])  # Top
v_up[3] *= math.exp(-V_cycles["Gen2"])  # Charm
v_up[6] *= math.exp(-V_cycles["Gen1"])  # Up

# Down-sector VEV (唔同 tanβ)
v_down = np.array([φ ** (-k / 12) for k in range(12)])
# 加入 generation scaling + tanβ
v_down[1] *= math.exp(-V_cycles["Gen3"]) / 7.5  # Bottom
v_down[4] *= math.exp(-V_cycles["Gen2"]) / 7.5  # Strange
v_down[7] *= math.exp(-V_cycles["Gen1"]) * 5.3  # Down

# 構建 up/down Yukawa 矩陣
Y_up_12 = np.zeros((12, 12))
Y_down_12 = np.zeros((12, 12))
for i in range(12):
    for j in range(12):
        Y_up_12[i, j] = sum(d[i, j, k] * v_up[k] for k in range(12))
        Y_down_12[i, j] = sum(d[i, j, k] * v_down[k] for k in range(12))

Y_up_sym = (Y_up_12 + Y_up_12.T) / 2
Y_down_sym = (Y_down_12 + Y_down_12.T) / 2

# 對角化 up-sector
evals_up, evecs_up = np.linalg.eigh(Y_up_sym)
idx_up = np.argsort(evals_up)[::-1]
evals_up = evals_up[idx_up]
evecs_up = evecs_up[:, idx_up]

# 對角化 down-sector
evals_down, evecs_down = np.linalg.eigh(Y_down_sym)
idx_down = np.argsort(evals_down)[::-1]
evals_down = evals_down[idx_down]
evecs_down = evecs_down[:, idx_down]

print(f"Up-sector 本徵值: {evals_up[:3]}")
print(f"Down-sector 本徵值: {evals_down[:3]}")

# 構建 P_u 同 P_d (前 3 個 eigenvector)
P_u = evecs_up[:, :3].T  # 3×12
P_d = evecs_down[:, :3].T  # 3×12

# ============================================================
# 5. CKM 矩陣
# ============================================================
print(f"\n{'='*70}")
print("CKM 矩陣 (從 P₃×₁₂ 投影)")
print(f"{'='*70}")

# V_CKM = P_u · P_d^T
V_CKM = P_u @ P_d.T

print(f"V_CKM:")
for row in np.abs(V_CKM):
    print(f"  {row}")

# 解析 CKM 角度
V_abs = np.abs(V_CKM)

# Standard parameterization:
# V = [c12c13  s12c13  s13e^{-iδ}]
#     [-s12c23 - c12s23s13e^{iδ}  c12c23 - s12s23s13e^{iδ}  s23c13]
#     [s12s23 - c12c23s13e^{iδ}  -c12s23 - s12c23s13e^{iδ}  c23c13]

# 實數近似 (δ=0):
s12 = V_abs[0, 1] / math.sqrt(1 - V_abs[0, 2]**2)
s23 = V_abs[1, 2] / math.sqrt(1 - V_abs[0, 2]**2)
s13 = V_abs[0, 2]

theta_12 = math.asin(min(s12, 1.0))
theta_23 = math.asin(min(s23, 1.0))
theta_13 = math.asin(min(s13, 1.0))

print(f"\nCKM 混合角:")
print(f"  θ₁₂ (Cabibbo) = {math.degrees(theta_12):.4f}°")
print(f"  θ₂₃ = {math.degrees(theta_23):.4f}°")
print(f"  θ₁₃ = {math.degrees(theta_13):.4f}°")

# PDG 參考
print(f"\nPDG 2024 參考:")
print(f"  θ₁₂ = 13.04°")
print(f"  θ₂₃ = 2.38°")
print(f"  θ₁₃ = 0.201°")

# 誤差
err_12 = abs(math.degrees(theta_12) / 13.04 - 1) * 100
err_23 = abs(math.degrees(theta_23) / 2.38 - 1) * 100
err_13 = abs(math.degrees(theta_13) / 0.201 - 1) * 100
print(f"\n誤差:")
print(f"  θ₁₂: {err_12:.2f}%")
print(f"  θ₂₃: {err_23:.2f}%")
print(f"  θ₁₃: {err_13:.2f}%")

# ============================================================
# 6. 儲存
# ============================================================
np.save("data/P_3x12.npy", P_3x12)
np.save("data/P_up.npy", P_u)
np.save("data/P_down.npy", P_d)
np.save("data/ckm_from_projection.npy", V_CKM)

with open("data/ckm_projection_results.txt", "w") as f:
    f.write("IDCM v10.0 — P₃×₁₂ 投影 CKM 結果\n")
    f.write("=" * 60 + "\n\n")
    f.write("V_CKM:\n")
    for row in np.abs(V_CKM):
        f.write(f"  {row}\n")
    f.write(f"\n混合角:\n")
    f.write(f"  θ₁₂ = {math.degrees(theta_12):.4f}°\n")
    f.write(f"  θ₂₃ = {math.degrees(theta_23):.4f}°\n")
    f.write(f"  θ₁₃ = {math.degrees(theta_13):.4f}°\n")
    f.write(f"\nPDG 參考:\n")
    f.write(f"  θ₁₂ = 13.04°\n")
    f.write(f"  θ₂₃ = 2.38°\n")
    f.write(f"  θ₁₃ = 0.201°\n")

print(f"\n已儲存 data/ckm_projection_results.txt ✅")