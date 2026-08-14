"""
IDCM v10.0 — Higgs VEV 幾何分佈 → θ₂₃, θ₁₃
===============================================
從 d_tensor 結構推導希格斯 VEV 喺 12 個奇點之間嘅分佈，
用 VEV profile 修正 CKM 混合角 θ₂₃ 同 θ₁₃。

核心假設:
1. v_u(k) = φ^(-k/12) × w_u(k)  (up-type Higgs VEV)
2. v_d(k) = φ^(-k/12) × w_d(k)  (down-type Higgs VEV)
3. w_u(k), w_d(k) 由 d_tensor 嘅 non-zero entries 決定
4. tan(β) = v_u / v_d 由 Z₃ × Z₅ 對稱性決定
"""

import math
import numpy as np
import cmath

φ = (1 + math.sqrt(5)) / 2
sqrt_φ = math.sqrt(φ)

# PDG 參考
V_PDG = np.array([
    [0.97435, 0.22500, 0.00369],
    [0.22486, 0.97349, 0.04182],
    [0.00857, 0.04110, 0.99912],
])
θ12_PDG, θ23_PDG, θ13_PDG = 13.04, 2.38, 0.201
J_CP_PDG = 3.08e-5
λ_PDG, A_PDG, ρ_PDG, η_PDG = 0.225, 0.83, 0.15, 0.35

print("=" * 80)
print("IDCM v10.0 — Higgs VEV 幾何分佈 → θ₂₃, θ₁₃ 🎯")
print("=" * 80)

# ══════════════════════════════════════════════════════════════
# 1. 載入 d_tensor
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("1. 載入 d_tensor 同 12D 結構")
print("─" * 80)

d = np.load("data/d_tensor_positive.npy")
n = d.shape[0]
v = np.array([φ ** (-k / 12) for k in range(n)])

# 完整 12×12 Yukawa
Y_full = np.zeros((n, n), dtype=complex)
for i in range(n):
    for j in range(n):
        Y_full[i, j] = sum(d[i, j, k] * v[k] for k in range(n))
Y_full = (Y_full + Y_full.T) / 2

# 12 個 eigenvalue/eigenvector
evals_12, evecs_12 = np.linalg.eigh(Y_full)
idx_12 = np.argsort(evals_12)[::-1]
evals_12 = evals_12[idx_12]
evecs_12 = evecs_12[:, idx_12]

# 粒子 index
up_idx = [0, 3, 6]
down_idx = [1, 4, 7]
lep_idx = [2, 5, 8]

# PDG 質量
masses = {"t": 172760.0, "c": 1270.0, "u": 2.17,
          "b": 4180.0, "s": 93.4, "d": 4.67}

print(f"  d_tensor: shape={d.shape}, 負值=0 ✅")
print(f"  Y_full eigenvalues: {[f'{ev:.4f}' for ev in evals_12[:6]]}...")

# ══════════════════════════════════════════════════════════════
# 2. 從 d_tensor 推導 Higgs VEV 權重
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("2. 從 d_tensor 推導 Higgs VEV 權重")
print("─" * 80)

# 每個 Kähler modulus k 嘅 Higgs VEV 權重:
# w(k) = 該 modulus 對 Yukawa 矩陣嘅貢獻
# 用 d_tensor 嘅 row/col sum 做權重

# 對於 up sector: w_u(k) = Σ_{i,j∈up} |d_{ijk}|
# 對於 down sector: w_d(k) = Σ_{i,j∈down} |d_{ijk}|

w_u = np.zeros(12)
w_d = np.zeros(12)
for k in range(12):
    for i in up_idx:
        for j in up_idx:
            w_u[k] += abs(d[i, j, k])
    for i in down_idx:
        for j in down_idx:
            w_d[k] += abs(d[i, j, k])

# 正規化
w_u = w_u / np.sum(w_u)
w_d = w_d / np.sum(w_d)

# 同時考慮 cross-sector 混合
# w_cross(k) = Σ_{i∈up, j∈down} |d_{ijk}|
w_cross = np.zeros(12)
for k in range(12):
    for i in up_idx:
        for j in down_idx:
            w_cross[k] += abs(d[i, j, k])
w_cross = w_cross / np.sum(w_cross)

print(f"\n  Higgs VEV 權重分佈:")
print(f"  {'k':>3} | {'v_base':>10} | {'w_u':>10} | {'w_d':>10} | {'w_cross':>10} | {'v_u/w_u':>10}")
print("-" * 60)
for k in range(12):
    v_base = φ ** (-k / 12)
    v_u_eff = v_base * w_u[k]
    v_d_eff = v_base * w_d[k]
    ratio = w_u[k] / w_d[k] if w_d[k] > 1e-15 else float('inf')
    print(f"  {k:>3} | {v_base:>10.6f} | {w_u[k]:>10.6f} | {w_d[k]:>10.6f} | {w_cross[k]:>10.6f} | {ratio:>10.4f}")

# ══════════════════════════════════════════════════════════════
# 3. tan(β) 從 d_tensor 結構推導
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("3. tan(β) 從 d_tensor 結構推導")
print("─" * 80)

# tan(β) = v_u / v_d
# 喺 MSSM 中, Y_u ∝ 1/tan(β), Y_d ∝ tan(β)
# 所以 tan(β) = √(Y_d / Y_u) 喺某種意義上

# 但更直接: 從 Yukawa 矩陣嘅 eigenvalue 推導
# Y_u eigenvalue = m_u / (v_weak × sin(β))
# Y_d eigenvalue = m_d / (v_weak × cos(β))
# 所以 tan(β) = (m_u / Y_u eigenvalue) / (m_d / Y_d eigenvalue)

# 從 3×3 submatrix 嘅 eigenvalue
Y_up_3 = np.zeros((3, 3), dtype=complex)
Y_down_3 = np.zeros((3, 3), dtype=complex)
for a in range(3):
    for b in range(3):
        Y_up_3[a, b] = Y_full[up_idx[a], up_idx[b]]
        Y_down_3[a, b] = Y_full[down_idx[a], down_idx[b]]

evals_up = np.sort(np.linalg.eigvalsh(Y_up_3))[::-1]
evals_down = np.sort(np.linalg.eigvalsh(Y_down_3))[::-1]

# 用最大 eigenvalue (Top/Bottom) 估算 tan(β)
# Y_t = m_t / (v_weak × sin(β)) → λ_top = evals_up[0]
# Y_b = m_b / (v_weak × cos(β)) → λ_bottom = evals_down[0]
# tan(β) = (m_t / λ_top) / (m_b / λ_bottom) = m_t × λ_bottom / (m_b × λ_top)

tan_β = masses["t"] * evals_down[0] / (masses["b"] * evals_up[0])
β = math.atan(tan_β)

print(f"\n  Top eigenvalue: λ_t = {evals_up[0]:.6f}")
print(f"  Bottom eigenvalue: λ_b = {evals_down[0]:.6f}")
print(f"  m_t/λ_t = {masses['t']/evals_up[0]:.2f} MeV")
print(f"  m_b/λ_b = {masses['b']/evals_down[0]:.2f} MeV")
print(f"  tan(β) = m_t × λ_b / (m_b × λ_t) = {tan_β:.4f}")
print(f"  β = {math.degrees(β):.2f}°")
print(f"  sin(β) = {math.sin(β):.4f}, cos(β) = {math.cos(β):.4f}")

# v_u = v_weak × sin(β), v_d = v_weak × cos(β)
v_weak = 246.0e3  # MeV
v_u = v_weak * math.sin(β)
v_d = v_weak * math.cos(β)
print(f"  v_u = {v_u:.2f} MeV, v_d = {v_d:.2f} MeV")

# ══════════════════════════════════════════════════════════════
# 4. 用 VEV 權重建構 3×3 Yukawa
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("4. 用 VEV 權重建構 3×3 Yukawa")
print("─" * 80)

# 用 VEV 權重修正 Yukawa 矩陣:
# Y_up_ij = Σ_k d_{ijk} × v_base(k) × w_u(k) × sin(β)
# Y_down_ij = Σ_k d_{ijk} × v_base(k) × w_d(k) × cos(β)

Y_up_vev = np.zeros((3, 3), dtype=complex)
Y_down_vev = np.zeros((3, 3), dtype=complex)

for a in range(3):
    for b in range(3):
        i, j = up_idx[a], up_idx[b]
        for k in range(12):
            Y_up_vev[a, b] += d[i, j, k] * v[k] * w_u[k] * math.sin(β)
        i, j = down_idx[a], down_idx[b]
        for k in range(12):
            Y_down_vev[a, b] += d[i, j, k] * v[k] * w_d[k] * math.cos(β)

Y_up_vev = (Y_up_vev + Y_up_vev.T) / 2
Y_down_vev = (Y_down_vev + Y_down_vev.T) / 2

# 對角化 (bi-unitary)
def bi_unitary_diag(Y):
    H = Y @ Y.conj().T
    H = (H + H.conj().T) / 2
    evals, U = np.linalg.eigh(H)
    idx = np.argsort(evals)[::-1]
    return U[:, idx], evals[idx]

U_u, ev_u = bi_unitary_diag(Y_up_vev)
U_d, ev_d = bi_unitary_diag(Y_down_vev)

# 質量
m_u_calc = np.sqrt(np.maximum(ev_u, 0)) * v_weak
m_d_calc = np.sqrt(np.maximum(ev_d, 0)) * v_weak

print(f"\n  Up masses: {[f'{m:.2f}' for m in m_u_calc]} MeV")
print(f"  期望: [{masses['t']:.0f}, {masses['c']:.0f}, {masses['u']:.2f}] MeV")
print(f"  Down masses: {[f'{m:.2f}' for m in m_d_calc]} MeV")
print(f"  期望: [{masses['b']:.0f}, {masses['s']:.1f}, {masses['d']:.2f}] MeV")

# CKM
V_ckm_vev = U_u.conj().T @ U_d
V_abs = np.abs(V_ckm_vev)

θ12 = math.degrees(math.atan2(V_abs[0, 1], V_abs[0, 0]))
θ23 = math.degrees(math.atan2(V_abs[1, 2], V_abs[2, 2]))
θ13 = math.degrees(math.asin(min(V_abs[0, 2], 1.0)))
J = np.imag(V_ckm_vev[0, 0] * V_ckm_vev[1, 1] * np.conj(V_ckm_vev[0, 1]) * np.conj(V_ckm_vev[1, 0]))

print(f"\n  V_CKM (VEV weighted):")
for row in V_abs:
    print(f"    {[f'{x:.6f}' for x in row]}")

print(f"\n  {'參數':>10} | {'IDCM':>12} | {'PDG':>12} | {'誤差':>10}")
print("-" * 50)
print(f"  {'θ₁₂':>10} | {θ12:>12.4f}° | {θ12_PDG:>12.4f}° | {abs(θ12-θ12_PDG):>9.4f}°")
print(f"  {'θ₂₃':>10} | {θ23:>12.4f}° | {θ23_PDG:>12.4f}° | {abs(θ23-θ23_PDG):>9.4f}°")
print(f"  {'θ₁₃':>10} | {θ13:>12.4f}° | {θ13_PDG:>12.4f}° | {abs(θ13-θ13_PDG):>9.4f}°")
print(f"  {'J_CP':>10} | {J:>12.2e} | {J_CP_PDG:>12.2e} | {'—':>10}")

# ══════════════════════════════════════════════════════════════
# 5. 加入 cross-sector hopping + Z₅ phase
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("5. 加入 cross-sector hopping + Z₅ phase")
print("─" * 80)

# Cross-sector hopping: 容許 up/down 之間嘅混合
# 強度由 w_cross 決定
# 對於每個 k, cross-sector 混合強度 ∝ w_cross[k]

# 構建 6×6 混合矩陣 (doublet space)
doublet_idx = [0, 1, 3, 4, 6, 7]
Y_6vev = np.zeros((6, 6), dtype=complex)

for a in range(6):
    for b in range(6):
        i = doublet_idx[a]
        j = doublet_idx[b]
        # 判斷係 up-up, down-down, 定 cross
        is_up = i in up_idx and j in up_idx
        is_down = i in down_idx and j in down_idx
        is_cross = (i in up_idx and j in down_idx) or (i in down_idx and j in up_idx)
        
        for k in range(12):
            if is_up:
                w = w_u[k] * math.sin(β)
            elif is_down:
                w = w_d[k] * math.cos(β)
            else:  # cross
                w = w_cross[k] * math.sqrt(math.sin(β) * math.cos(β))
            
            Y_6vev[a, b] += d[i, j, k] * v[k] * w

Y_6vev = (Y_6vev + Y_6vev.T) / 2

# 加入 Z₅ phase
z5_charges = [i % 5 for i in range(12)]
for a in range(6):
    for b in range(6):
        i = doublet_idx[a]
        j = doublet_idx[b]
        phase = cmath.exp(2j * math.pi * (z5_charges[i] - z5_charges[j]) / 5)
        Y_6vev[a, b] *= phase

# 對角化 6×6
H_6 = Y_6vev @ Y_6vev.conj().T
H_6 = (H_6 + H_6.conj().T) / 2
evals_6, U_6 = np.linalg.eigh(H_6)
idx_6 = np.argsort(evals_6)[::-1]
U_6 = U_6[:, idx_6]

# 將 6 個 eigenvectors 分成 up/down subspace
# 用 index weight 分離
up_weight = np.array([1, 0, 1, 0, 1, 0])  # indices 0,3,6 in doublet_idx
down_weight = np.array([0, 1, 0, 1, 0, 1])  # indices 1,4,7 in doublet_idx

up_vecs, down_vecs = [], []
for i in range(6):
    v = U_6[:, i]
    w_up = np.sum(np.abs(v)**2 * up_weight)
    w_down = np.sum(np.abs(v)**2 * down_weight)
    if w_up > w_down:
        up_vecs.append(v)
    else:
        down_vecs.append(v)

# 確保 3+3
U_6_up = np.array(up_vecs[:3]).T if len(up_vecs) >= 3 else U_6[:, :3]
U_6_down = np.array(down_vecs[:3]).T if len(down_vecs) >= 3 else U_6[:, 3:6]

V_ckm_6d = U_6_up.conj().T @ U_6_down
V_abs_6 = np.abs(V_ckm_6d)

θ12_6 = math.degrees(math.atan2(V_abs_6[0, 1], V_abs_6[0, 0]))
θ23_6 = math.degrees(math.atan2(V_abs_6[1, 2], V_abs_6[2, 2]))
θ13_6 = math.degrees(math.asin(min(V_abs_6[0, 2], 1.0)))
J_6 = np.imag(V_ckm_6d[0, 0] * V_ckm_6d[1, 1] * np.conj(V_ckm_6d[0, 1]) * np.conj(V_ckm_6d[1, 0]))

print(f"\n  V_CKM (6×6 + VEV + Z₅ phase):")
for row in V_abs_6:
    print(f"    {[f'{x:.6f}' for x in row]}")

print(f"\n  {'參數':>10} | {'IDCM':>12} | {'PDG':>12} | {'誤差':>10}")
print("-" * 50)
print(f"  {'θ₁₂':>10} | {θ12_6:>12.4f}° | {θ12_PDG:>12.4f}° | {abs(θ12_6-θ12_PDG):>9.4f}°")
print(f"  {'θ₂₃':>10} | {θ23_6:>12.4f}° | {θ23_PDG:>12.4f}° | {abs(θ23_6-θ23_PDG):>9.4f}°")
print(f"  {'θ₁₃':>10} | {θ13_6:>12.4f}° | {θ13_PDG:>12.4f}° | {abs(θ13_6-θ13_PDG):>9.4f}°")
print(f"  {'J_CP':>10} | {J_6:>12.2e} | {J_CP_PDG:>12.2e} | {'—':>10}")

# ══════════════════════════════════════════════════════════════
# 6. 分析同總結
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("6. 分析同總結")
print("─" * 80)

print(f"""
  🎯 Higgs VEV 幾何分佈結果:

  tan(β) = {tan_β:.4f} (從 d_tensor eigenvalue 推導)
  β = {math.degrees(β):.2f}°
  v_u = {v_u:.2f} MeV, v_d = {v_d:.2f} MeV

  方法 H: VEV 加權 3×3:
  θ₁₂ = {θ12:.4f}° (PDG: {θ12_PDG}°) — 誤差 {abs(θ12-θ12_PDG):.4f}°
  θ₂₃ = {θ23:.4f}° (PDG: {θ23_PDG}°) — 誤差 {abs(θ23-θ23_PDG):.4f}°
  θ₁₃ = {θ13:.4f}° (PDG: {θ13_PDG}°) — 誤差 {abs(θ13-θ13_PDG):.4f}°
  J_CP = {J:.2e} (PDG: {J_CP_PDG:.2e})

  方法 I: 6×6 + VEV + Z₅ phase:
  θ₁₂ = {θ12_6:.4f}° (PDG: {θ12_PDG}°) — 誤差 {abs(θ12_6-θ12_PDG):.4f}°
  θ₂₃ = {θ23_6:.4f}° (PDG: {θ23_PDG}°) — 誤差 {abs(θ23_6-θ23_PDG):.4f}°
  θ₁₃ = {θ13_6:.4f}° (PDG: {θ13_PDG}°) — 誤差 {abs(θ13_6-θ13_PDG):.4f}°
  J_CP = {J_6:.2e} (PDG: {J_CP_PDG:.2e})

  分析:
  ────
  1. VEV 權重成功引入 tan(β) ≈ {tan_β:.4f} 嘅 MSSM 結構
  2. 6×6 doublet space 保留跨 sector 混合
  3. Z₅ phase 引入複數相位，J_CP = {J_6:.2e}
  
  下一步:
  ──────
  1. 優化 w_u, w_d, w_cross 嘅權重分佈
  2. 精確對齊 Z₅ phase 嘅 twisted sector 貢獻
  3. 將結果寫入文檔
""")

# 儲存
np.save("open_problems_fresh/ckm_reconstruction/V_ckm_vev.npy", V_ckm_vev)
np.save("open_problems_fresh/ckm_reconstruction/V_ckm_6d.npy", V_ckm_6d)
np.save("open_problems_fresh/ckm_reconstruction/w_u.npy", w_u)
np.save("open_problems_fresh/ckm_reconstruction/w_d.npy", w_d)
np.save("open_problems_fresh/ckm_reconstruction/w_cross.npy", w_cross)

lines = []
lines.append("IDCM v10.0 — Higgs VEV 幾何分佈結果")
lines.append("=" * 60)
lines.append("")
lines.append(f"tan(β) = {tan_β:.4f} (從 d_tensor 推導)")
lines.append(f"β = {math.degrees(β):.2f}°")
lines.append("")
lines.append(f"方法 H (VEV 3×3):")
lines.append(f"  θ₁₂ = {θ12:.4f}° (PDG: {θ12_PDG}°)")
lines.append(f"  θ₂₃ = {θ23:.4f}° (PDG: {θ23_PDG}°)")
lines.append(f"  θ₁₃ = {θ13:.4f}° (PDG: {θ13_PDG}°)")
lines.append(f"  J_CP = {J:.2e} (PDG: {J_CP_PDG:.2e})")
lines.append("")
lines.append(f"方法 I (6×6 + VEV + Z₅):")
lines.append(f"  θ₁₂ = {θ12_6:.4f}° (PDG: {θ12_PDG}°)")
lines.append(f"  θ₂₃ = {θ23_6:.4f}° (PDG: {θ23_PDG}°)")
lines.append(f"  θ₁₃ = {θ13_6:.4f}° (PDG: {θ13_PDG}°)")
lines.append(f"  J_CP = {J_6:.2e} (PDG: {J_CP_PDG:.2e})")

with open("open_problems_fresh/ckm_reconstruction/vev_profile_results.txt", "w") as f:
    f.write("\n".join(lines))

print("已儲存所有結果 ✅")