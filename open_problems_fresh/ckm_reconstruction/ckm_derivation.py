"""
IDCM v10.0 — CKM 重構推導 (GST 為基礎)
===========================================
從頭重構 CKM 矩陣推導，以 GST (Gatto-Sartori-Tonin) 關係為基礎。

GST 關係:
θ₁₂ = arcsin(√(m_d/m_s)) ≈ 12.92° (PDG 13.04°, 誤差 0.91%)

策略:
1. 用清洗後 d_tensor_positive.npy 構建完整 Yukawa 矩陣
2. 通過 VEV 分離 up/down sector
3. 從 Yukawa 本徵向量計算 CKM
4. 用 GST 關係做校準
"""

import math
import numpy as np
import os

φ = (1 + math.sqrt(5)) / 2
M_Pl = 1.220890e22  # MeV

# ══════════════════════════════════════════════════════════════
# 現有結果回顧
# ══════════════════════════════════════════════════════════════
print("=" * 80)
print("IDCM v10.0 — CKM 重構推導 (GST 為基礎)")
print("=" * 80)

print(f"""
現有結果回顧:
────────────
盲測成功: 6/8 < 1% ✅
Up 修正: √φ = 1.272020 ✅
波函數重整化: 四重代數驗證通過 ✅

CKM 現狀 (全部錯誤 ❌):
  方法 1: 直接對角化 → θ₁₂=15.23°, θ₂₃=76.00°, θ₁₃=1.93°
  方法 2: P₃×₁₂ 投影 → θ₁₂=0.10°, θ₂₃=12.52°, θ₁₃=1.14°
  方法 3: 自洽投影 → θ₁₂=0.00°, θ₂₃=31.49°, θ₁₃=0.00°
  PDG 參考:         θ₁₂=13.04°, θ₂₃=2.38°, θ₁₃=0.201°

GST 關係 (正確 🟢):
  θ₁₂ = arcsin(√(m_d/m_s)) = arcsin(√(4.67/93.4)) = 12.92°
  PDG 13.04°, 誤差 0.91%
""")

# ══════════════════════════════════════════════════════════════
# 1. 載入 d_tensor
# ══════════════════════════════════════════════════════════════
print("─" * 80)
print("1. 載入 d_tensor")
print("─" * 80)

d_clean = np.load("data/d_tensor_positive.npy")
d_raw = np.load("data/d_tensor_final.npy")
n = d_clean.shape[0]
v = np.array([φ ** (-k / 12) for k in range(n)])

print(f"  d_tensor_positive: shape={d_clean.shape}, 負值={np.sum(d_clean<0)}/{d_clean.size}")
print(f"  d_tensor_final:    shape={d_raw.shape}, 負值={np.sum(d_raw<0)}/{d_raw.size}")

# Yukawa 矩陣
Y_full = np.zeros((n, n))
for i in range(n):
    for j in range(n):
        Y_full[i, j] = sum(d_clean[i, j, k] * v[k] for k in range(n))
Y_full = (Y_full + Y_full.T) / 2

# ══════════════════════════════════════════════════════════════
# 2. 質量公式回顧
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("2. 質量公式: m = λ × M_Pl × exp(-V_cycle) × f_sector")
print("─" * 80)

# 物理質量
masses = {
    "Top": 172760.0, "Bottom": 4180.0, "Tau": 1776.86,
    "Charm": 1270.0, "Strange": 93.4, "Muon": 105.6583745,
    "Up": 2.17, "Down": 4.67, "Electron": 0.51099895,
}

# 12 個 eigenvalue (WDVV 解)
eigvals = [51.56061144, 10.00020784, 4.57828158, 3.43285526,
           1.86617103, 0.23471919, 0.02274885, 0.01172015,
           0.00681361, 0.00185077, 0.00136084, -1.264797e-11]

# 粒子到 eigenvalue 嘅映射
particle_ev_idx = {
    "Top": 0, "Bottom": 1, "Tau": 2, "Charm": 3,
    "Strange": 4, "Muon": 5, "Up": 6, "Down": 7, "Electron": 8
}

V_cycle = {"Gen3": 42.7396, "Gen2": 44.9431, "Gen1": 46.5390}

# 驗證質量公式
print(f"\n{'粒子':>10} | {'λ':>10} | {'V_cycle':>8} | {'bare(MeV)':>12} | {'PDG(MeV)':>12} | {'誤差%':>8}")
print("-" * 65)

for name, mass in masses.items():
    idx = particle_ev_idx[name]
    lam = eigvals[idx]
    gen = "Gen3" if name in ["Top", "Bottom", "Tau"] else ("Gen2" if name in ["Charm", "Strange", "Muon"] else "Gen1")
    V = V_cycle[gen]
    bare = lam * M_Pl * math.exp(-V)
    err = abs(bare / mass - 1) * 100
    print(f"{name:>10} | {lam:>10.6f} | {V:>8.4f} | {bare:>12.4f} | {mass:>12.4f} | {err:>7.2f}%")

# ══════════════════════════════════════════════════════════════
# 3. GST 關係驗證
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("3. GST 關係: θ₁₂ = arcsin(√(m_d/m_s))")
print("─" * 80)

m_d = masses["Down"]
m_s = masses["Strange"]
m_u = masses["Up"]
m_c = masses["Charm"]

theta_12_gst = math.asin(math.sqrt(m_d / m_s))
theta_12_pdg = math.radians(13.04)

# 其他 GST 關係
# θ₁₃ ≈ arcsin(√(m_u/m_t) × sin(θ₁₂))? 唔係 standard
# 實際 GST 只有 θ₁₂

# 第二個關係: θ₂₃ ≈ arcsin(√(m_s/m_b))? 唔啱
# θ₂₃ 同 m_s/m_b 嘅關係係: θ₂₃ ≈ λ² (Wolfenstein)
# 即係 θ₂₃ ≈ (|V_us|)² ≈ 0.04 rad ≈ 2.3° — 接近 PDG 2.38°

# Wolfenstein 參數
lam_W = 0.225  # |V_us| ≈ 0.225
A = 0.83       # |V_cb| / λ²
rho = 0.15
eta = 0.35

print(f"\n  GST 關係:")
print(f"    θ₁₂(GST) = arcsin(√({m_d:.2f}/{m_s:.2f})) = arcsin({math.sqrt(m_d/m_s):.6f})")
print(f"             = {math.degrees(theta_12_gst):.4f}°")
print(f"    θ₁₂(PDG) = {math.degrees(theta_12_pdg):.4f}°")
print(f"    誤差     = {abs(math.degrees(theta_12_gst) - math.degrees(theta_12_pdg)):.4f}°")
print(f"    (PDG 誤差 = {abs(math.degrees(theta_12_gst)/math.degrees(theta_12_pdg)-1)*100:.2f}%)")

print(f"\n  Wolfenstein 參數:")
print(f"    λ = |V_us| = {lam_W}")
print(f"    A = |V_cb| / λ² = {A}")
print(f"    ρ = {rho}, η = {eta}")
print(f"    θ₂₃(Wolf) ≈ A·λ² = {A*lam_W**2:.4f} rad = {math.degrees(A*lam_W**2):.2f}°")
print(f"    θ₂₃(PDG)  = 2.38°")

# ══════════════════════════════════════════════════════════════
# 4. 從 Yukawa 矩陣提取 CKM
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("4. 從 Yukawa 矩陣提取 CKM")
print("─" * 80)

# 問題: 12×12 Yukawa 矩陣如何分離 up/down sector?
# 目前嘅方法: 用固定 index 分離
# Y_up = Y_full[0,3,6; 0,3,6] (Top, Charm, Up)
# Y_down = Y_full[1,4,7; 1,4,7] (Bottom, Strange, Down)

# 但呢個分離方式可能唔啱——Yukawa 矩陣可能喺世代之間有混合

# 方法 A: 直接取 3×3 子矩陣
up_idx = [0, 3, 6]    # Top, Charm, Up
down_idx = [1, 4, 7]   # Bottom, Strange, Down

Y_up = np.zeros((3, 3))
Y_down = np.zeros((3, 3))
for a in range(3):
    for b in range(3):
        Y_up[a, b] = Y_full[up_idx[a], up_idx[b]]
        Y_down[a, b] = Y_full[down_idx[a], down_idx[b]]

# 對稱化
Y_up = (Y_up + Y_up.T) / 2
Y_down = (Y_down + Y_down.T) / 2

print(f"\n  Up Yukawa (3x3 submatrix):")
for row in Y_up:
    print(f"    {[f'{x:.6f}' for x in row]}")

print(f"\n  Down Yukawa (3x3 submatrix):")
for row in Y_down:
    print(f"    {[f'{x:.6f}' for x in row]}")

# 對角化
evals_up, evecs_up = np.linalg.eigh(Y_up)
evals_down, evecs_down = np.linalg.eigh(Y_down)

# 排序 (由大到小)
idx_up = np.argsort(evals_up)[::-1]
evals_up = evals_up[idx_up]
evecs_up = evecs_up[:, idx_up]

idx_down = np.argsort(evals_down)[::-1]
evals_down = evals_down[idx_down]
evecs_down = evecs_down[:, idx_down]

print(f"\n  Up eigenvalues: {[f'{x:.6f}' for x in evals_up]}")
print(f"  期望: Top={eigvals[0]:.6f}, Charm={eigvals[3]:.6f}, Up={eigvals[6]:.6f}")
print(f"  Down eigenvalues: {[f'{x:.6f}' for x in evals_down]}")
print(f"  期望: Bottom={eigvals[1]:.6f}, Strange={eigvals[4]:.6f}, Down={eigvals[7]:.6f}")

# CKM: V_CKM = U_u^† · U_d
V_ckm = evecs_up.conj().T @ evecs_down

print(f"\n  V_CKM (direct 3x3 submatrix):")
for row in np.abs(V_ckm):
    print(f"    {[f'{x:.6f}' for x in row]}")

# 混合角
V_abs = np.abs(V_ckm)
theta_12 = math.degrees(math.atan2(V_abs[0, 1], V_abs[0, 0]))
theta_13 = math.degrees(math.asin(V_abs[0, 2]))
theta_23 = math.degrees(math.atan2(V_abs[1, 2], V_abs[2, 2]))

print(f"\n  混合角:")
print(f"    θ₁₂ = {theta_12:.4f}° (PDG: 13.04°)")
print(f"    θ₂₃ = {theta_23:.4f}° (PDG: 2.38°)")
print(f"    θ₁₃ = {theta_13:.4f}° (PDG: 0.201°)")

# Jarlskog 不變量
J = np.imag(V_ckm[0, 0] * V_ckm[1, 1] * np.conj(V_ckm[0, 1]) * np.conj(V_ckm[1, 0]))
print(f"\n  J_CP = {J:.6e} (PDG: 3.08e-05)")

# ══════════════════════════════════════════════════════════════
# 5. 方法 B: 用 VEV 加權分離 sector
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("5. 方法 B: VEV 加權分離")
print("─" * 80)

# 每個粒子嘅 VEV 權重: exp(-V_cycle) × sector_factor
# 用呢個權重重新構建 3×3 Yukawa

# 對於 up sector: VEV 權重 = exp(-V_cycle)
# 對於 down sector: VEV 權重 = exp(-V_cycle) × (down/up ratio)

# 但問題係: 12D 空間入面, up/down 分離唔係咁簡單
# 12 個 Kähler moduli 對應 12 個粒子, 唔係 3 個 generation

# 正確嘅方法: 用完整 12×12 Yukawa 矩陣, 然後投影到 up/down 子空間
# 但 up/down 子空間喺 12D 入面點定義?

# 一個可能: 用 12 個 eigenvalue 嘅本徵向量做基底
# 然後將 up/down 粒子投影到呢個基底

print(f"\n  完整 12×12 Yukawa 矩陣本徵值:")
evals_full, evecs_full = np.linalg.eigh(Y_full)
idx_full = np.argsort(evals_full)[::-1]
evals_full = evals_full[idx_full]
evecs_full = evecs_full[:, idx_full]

for i in range(12):
    marker = ""
    if i == 0: marker = " ← Top"
    elif i == 6: marker = " ← Up"
    elif i == 8: marker = " ← Electron"
    print(f"    λ_{i+1:2d} = {evals_full[i]:.6f}{marker}")

# 本徵向量 overlap
print(f"\n  本徵向量 overlap with particle basis:")
for i in range(3):
    name = ["Top", "Charm", "Up"][i]
    idx_p = [0, 3, 6][i]
    print(f"    {name} (index {idx_p}):")
    # 睇下呢個粒子嘅 state 喺本徵向量空間嘅分佈
    for j in range(5):
        overlap = abs(evecs_full[idx_p, j])
        if overlap > 0.1:
            print(f"      與 λ_{j+1} overlap = {overlap:.4f}")

# ══════════════════════════════════════════════════════════════
# 6. 小結: 邊個方向要改?
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("6. 分析: 現有方法嘅問題")
print("─" * 80)

print(f"""
  問題診斷:
  ─────────
  1. 直接 3×3 submatrix 方法:
     - 假設 up/down Yukawa 完全獨立 (no cross-sector mixing)
     - 但 12×12 Yukawa 矩陣有 cross-sector 項 (d_{{ijk}} 無 sector 分離)
     - 結果: eigenvalue 唔 match 物理質量

  2. VEV 加權方法:
     - 引入 exp(-V_cycle) 權重, 但權重嘅分配方式影響結果
     - 需要知道每個粒子嘅 V_cycle 精確值

  3. 根本問題:
     - d_{{ijk}} 張量嘅 12 個 index 對應 Kähler moduli, 唔係粒子
     - 粒子係經過 Z₃ orbifold 投影同 WDVV 求解後嘅 eigenvalue
     - 所以 12 個 eigenvalue ≠ 12 個粒子
     - 粒子係 eigenvalue 嘅某種線性組合

  解決方向:
  ─────────
  1. 用 GST 關係做校準:
     θ₁₂(GST) = 12.92° (PDG 13.04°, 誤差 0.91%) 🟢
     
  2. 從 Wolfenstein 參數出發構建 CKM:
     λ = |V_us| = 0.225
     A = |V_cb| / λ² ≈ 0.83
     ρ, η from J_CP

  3. 用 12D 本徵向量嘅 overlap 做 sector 分離:
     - 每個物理粒子係 12 個 eigenvalue 嘅線性組合
     - 線性組合係數由 d_{{ijk}} 嘅結構決定
     - 呢個組合就係 CKM 嘅起源
""")

# ══════════════════════════════════════════════════════════════
# 7. 儲存
# ══════════════════════════════════════════════════════════════
print("─" * 80)
print("7. 儲存結果")
print("─" * 80)

# 儲存關鍵數據
np.save("open_problems_fresh/ckm_reconstruction/V_ckm_3x3.npy", V_ckm)
np.save("open_problems_fresh/ckm_reconstruction/Y_up_3x3.npy", Y_up)
np.save("open_problems_fresh/ckm_reconstruction/Y_down_3x3.npy", Y_down)

lines = []
lines.append("IDCM v10.0 — CKM 重構推導初始結果")
lines.append("=" * 60)
lines.append("")
lines.append(f"GST θ₁₂ = {math.degrees(theta_12_gst):.4f}° (PDG 13.04°)")
lines.append(f"誤差 = {abs(math.degrees(theta_12_gst)/math.degrees(theta_12_pdg)-1)*100:.2f}%")
lines.append("")
lines.append(f"Direct 3x3 submatrix:")
lines.append(f"  θ₁₂ = {theta_12:.4f}°")
lines.append(f"  θ₂₃ = {theta_23:.4f}°")
lines.append(f"  θ₁₃ = {theta_13:.4f}°")
lines.append(f"  J_CP = {J:.6e}")
lines.append("")
lines.append(f"問題: direct 3x3 submatrix 唔 match PDG")
lines.append(f"原因: 12 個 eigenvalue ≠ 12 個粒子")
lines.append(f"解決: 需要正確嘅 sector 分離方法")

with open("open_problems_fresh/ckm_reconstruction/initial_results.txt", "w") as f:
    f.write("\n".join(lines))

print("已儲存 open_problems_fresh/ckm_reconstruction/ ✅")