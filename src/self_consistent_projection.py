"""
IDCM v10.0 — 自洽投影矩陣 P₃×₁₂
====================================
用 K_Chain 本徵值比例做幾何權重構建投影矩陣
"""

import math
import numpy as np

# ============================================================
# 1. 載入 d_tensor 同 eigenvalues
# ============================================================
d = np.load("data/d_tensor_final.npy")
evals = np.load("data/eigenvalues_final.npy")
sorted_pos = sorted([e for e in evals if e > 1e-10], reverse=True)

M_Pl = 1.220890e22
φ = (1 + math.sqrt(5)) / 2

print("=" * 70)
print("IDCM v10.0 — 自洽投影矩陣 P₃×₁₂")
print("=" * 70)

# ============================================================
# 2. 構建 12×12 Yukawa 矩陣 (用 φ^(-k/12) VEV)
# ============================================================
v = np.array([φ ** (-k / 12) for k in range(12)])
Y_12 = np.zeros((12, 12))
for i in range(12):
    for j in range(12):
        Y_12[i, j] = sum(d[i, j, k] * v[k] for k in range(12))
Y_sym = (Y_12 + Y_12.T) / 2

# 對角化
evals_12, evecs_12 = np.linalg.eigh(Y_sym)
idx = np.argsort(evals_12)[::-1]
evals_12 = evals_12[idx]
evecs_12 = evecs_12[:, idx]

# 驗證: 12 個本徵值應該同 eigenvalues_final 一致
print(f"\n12 本徵值驗證:")
for i in range(12):
    ratio = evals_12[i] / sorted_pos[i] if i < 11 else 0
    print(f"  λ_{i+1:2d} = {evals_12[i]:.6f} (ref: {sorted_pos[i] if i < 11 else 0:.6f}, ratio: {ratio:.2f})")

# ============================================================
# 3. 用 eigenvalue 比例做幾何權重
# ============================================================
# 每個 12D eigenvector 嘅 "generation weight" 由 eigenvalue 大小決定
# 大 eigenvalue = 主導第 3 代，細 eigenvalue = 第 1 代

# 正規化 eigenvalue 做權重
weights = np.array([e if e > 0 else 0 for e in evals_12])
weights = weights / weights.sum()

print(f"\nEigenvalue 權重分佈:")
for i in range(12):
    print(f"  w_{i+1:2d} = {weights[i]:.6f}")

# ============================================================
# 4. 構建 P₃×₁₂ (用權重加權嘅 eigenvector projection)
# ============================================================
# P 嘅第 g 行 = eigenvector 嘅加權和，權重由第 g 代決定
# 第 3 代: 用最大 eigenvalue 嘅 eigenvectors
# 第 2 代: 用中等 eigenvalue 嘅 eigenvectors
# 第 1 代: 用最小 eigenvalue 嘅 eigenvectors

# 方法: 用 eigenvalue 做生成標度
# 第 g 代嘅投影方向 = Σ_i w_i(g) × evecs_12[:, i]
# 其中 w_i(g) ∝ exp(-|g - scale_i|²)

# 將 12 個 eigenvalue 映射到 3 代
# 最大 4 個 eigenvalue → Gen 3 (index 0,1,2,3)
# 中間 4 個 → Gen 2 (index 4,5,6,7)
# 最小 4 個 → Gen 1 (index 8,9,10,11)

P = np.zeros((3, 12))
for gen in range(3):
    start = gen * 4
    end = start + 4
    for i in range(start, min(end, 12)):
        # 權重: 正比於 eigenvalue 嘅平方根 (場論正規化)
        w = math.sqrt(weights[i]) if weights[i] > 0 else 0
        P[gen, :] += w * evecs_12[:, i]
    # 正規化
    norm = np.linalg.norm(P[gen, :])
    if norm > 0:
        P[gen, :] /= norm

print(f"\nP₃×₁₂ 投影矩陣:")
print(P)
print(f"\nP·P^T = I₃:")
print(P @ P.T)
iso = np.allclose(P @ P.T, np.eye(3), atol=1e-10)
print(f"等距條件: {iso}")

# ============================================================
# 5. Up/Down Sector 投影
# ============================================================
# Up sector: 用 eigenvalue 權重聚焦喺 up-type 方向
# Down sector: 用 eigenvalue 權重聚焦喺 down-type 方向

# 構建 sector-specific 嘅 VEV 方向
# Up-type: 權重集中在奇數 index (0, 2, 4, ...) — 對應 up-type eigenvalues
# Down-type: 權重集中在偶數 index (1, 3, 5, ...) — 對應 down-type eigenvalues

# 用 12 個 eigenvalue 嘅奇偶分佈做 sector 投影
v_up = np.array([φ ** (-k / 12) for k in range(12)])
v_down = np.array([φ ** (-k / 12) for k in range(12)])

# 加入 V_cycle 同 tanβ 嘅 scaling
V_cycles = [42.7396, 44.9431, 46.5390]
# Up-type 世代 scaling
v_up[0] *= math.exp(-V_cycles[0])  # Top
v_up[3] *= math.exp(-V_cycles[1])  # Charm
v_up[6] *= math.exp(-V_cycles[2])  # Up
# Down-type 世代 scaling + tanβ
v_down[1] *= math.exp(-V_cycles[0]) / 7.5  # Bottom
v_down[4] *= math.exp(-V_cycles[1]) / 7.5  # Strange
v_down[7] *= math.exp(-V_cycles[2]) * 5.3  # Down

# 構建 up/down Yukawa 矩陣
Y_up_12 = np.zeros((12, 12))
Y_down_12 = np.zeros((12, 12))
for i in range(12):
    for j in range(12):
        Y_up_12[i, j] = sum(d[i, j, k] * v_up[k] for k in range(12))
        Y_down_12[i, j] = sum(d[i, j, k] * v_down[k] for k in range(12))

Y_up_sym = (Y_up_12 + Y_up_12.T) / 2
Y_down_sym = (Y_down_12 + Y_down_12.T) / 2

# 對角化
evals_up, evecs_up = np.linalg.eigh(Y_up_sym)
evals_down, evecs_down = np.linalg.eigh(Y_down_sym)

idx_up = np.argsort(evals_up)[::-1]
idx_down = np.argsort(evals_down)[::-1]
evecs_up = evecs_up[:, idx_up]
evecs_down = evecs_down[:, idx_down]

# 用 eigenvalue 權重構建 P_u 同 P_d
P_u = np.zeros((3, 12))
P_d = np.zeros((3, 12))

for gen in range(3):
    start = gen * 4
    end = start + 4
    for sector, evecs_mat in [("up", evecs_up), ("down", evecs_down)]:
        P_mat = P_u if sector == "up" else P_d
        for i in range(start, min(end, 12)):
            w = math.sqrt(max(evals_up[i], 0) / max(evals_up[0], 1)) if sector == "up" else \
                math.sqrt(max(evals_down[i], 0) / max(evals_down[0], 1))
            if w > 1e-10:
                P_mat[gen, :] += w * evecs_mat[:, i]
        norm = np.linalg.norm(P_mat[gen, :])
        if norm > 0:
            P_mat[gen, :] /= norm

# ============================================================
# 6. CKM 矩陣
# ============================================================
print(f"\n{'='*70}")
print("CKM 矩陣 (自洽投影)")
print(f"{'='*70}")

V_CKM = P_u @ P_d.T
V_abs = np.abs(V_CKM)

print(f"V_CKM:")
for row in V_abs:
    print(f"  {row}")

# 混合角
s12 = V_abs[0, 1] / math.sqrt(1 - V_abs[0, 2]**2) if V_abs[0, 2] < 1 else 0
s23 = V_abs[1, 2] / math.sqrt(1 - V_abs[0, 2]**2) if V_abs[0, 2] < 1 else 0
s13 = V_abs[0, 2]

theta_12 = math.asin(min(s12, 1.0))
theta_23 = math.asin(min(s23, 1.0))
theta_13 = math.asin(min(s13, 1.0))

print(f"\nCKM 混合角:")
print(f"  θ₁₂ (Cabibbo) = {math.degrees(theta_12):.4f}°")
print(f"  θ₂₃ = {math.degrees(theta_23):.4f}°")
print(f"  θ₁₃ = {math.degrees(theta_13):.4f}°")

print(f"\nPDG 參考:")
print(f"  θ₁₂ = 13.04°")
print(f"  θ₂₃ = 2.38°")
print(f"  θ₁₃ = 0.201°")

# 儲存
np.save("data/P_self_consistent.npy", P)
np.save("data/P_u_sc.npy", P_u)
np.save("data/P_d_sc.npy", P_d)
np.save("data/ckm_self_consistent.npy", V_CKM)

with open("data/ckm_self_consistent.txt", "w") as f:
    f.write("IDCM v10.0 — 自洽投影 CKM\n\n")
    f.write("V_CKM:\n")
    for row in V_abs:
        f.write(f"  {row}\n")
    f.write(f"\nθ₁₂ = {math.degrees(theta_12):.4f}°\n")
    f.write(f"θ₂₃ = {math.degrees(theta_23):.4f}°\n")
    f.write(f"θ₁₃ = {math.degrees(theta_13):.4f}°\n")

print(f"\n已儲存 ✅")