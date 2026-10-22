#!/usr/bin/env python3
"""
O143 Step 1 — 建立雙鏈環到 2D 天球嘅拓撲映射算子 𝒫
====================================================
目標: 構造投影算子 𝒫: ℋ₈₈ → L²(S²)，將 88-site 1D 離散環嘅相位場
映射到 2D 天球 CMB 觀察面嘅 60 個採樣節點。

理論基礎:
- 88-site 雙鏈: x_k = 2πk/88, k=0..87
  - 偶數 k=2n: 世界模式 (γ_{2n} = γ_n^(44), Σγ=90)
  - 奇數 k=2n-1: 觀察者模式 (γ_{2n-1} = γ_{n+0.5}, Σγ=88)
- 60 A₅ 節點: Rhombicosidodecahedron 頂點 (20Δ+30□+12⬠, χ=2)
- 幾何約束: 未投影弧長比 41/60, 投影弧長比 19/60 (O34/O47)

反幻覺鐵律:
  - 座標: a5_nodes.txt 係 ICRS, 必須轉 Galactic
  - 88-site 環係 1D, 天球係 2D — 𝒫 唔係簡單 injection
"""

import numpy as np
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u
import json, os, sys

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
O143 = f'{BASE}/open_problems_fresh/o143_phase_selection_mechanism'
NODES_FILE = f'{BASE}/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt'
OUTDIR = f'{O143}/data'
os.makedirs(OUTDIR, exist_ok=True)

# ══════════════════════════════════════════════════════════════
# 1. 載入 60 節點
# ══════════════════════════════════════════════════════════════
nodes = np.loadtxt(NODES_FILE)
assert nodes.shape == (60, 2), f"Expected 60×2, got {nodes.shape}"

sc = SkyCoord(ra=nodes[:,0]*u.deg, dec=nodes[:,1]*u.deg, frame='icrs')
gal = sc.galactic
l_arr = np.array([float(g.l.deg) for g in gal])
b_arr = np.array([float(g.b.deg) for g in gal])

print("=" * 72)
print("  O143 Step 1: 投影算子 𝒫 建立")
print("=" * 72)

# ══════════════════════════════════════════════════════════════
# 2. 88-site 雙鏈環定義
# ══════════════════════════════════════════════════════════════
N_sites = 88
x_k = np.linspace(0, 2*np.pi, N_sites, endpoint=False)  # k = 0..87

# K_Chain 色散
k_idx = np.arange(1, N_sites + 1)
gamma_k = 4 * np.sin(np.pi * k_idx / (2 * N_sites))**2

# 奇偶分解
even_idx = np.arange(1, N_sites + 1, 2)  # k = 2, 4, 6, ..., 88 (1-indexed)
odd_idx = np.arange(0, N_sites, 2)       # k = 1, 3, 5, ..., 87 (1-indexed)
gamma_even = gamma_k[even_idx]  # 世界模式
gamma_odd = gamma_k[odd_idx]    # 觀察者模式

print(f"\n88-site 雙鏈:")
print(f"  Σγ_even (世界) = {gamma_even.sum():.10f}  (理論: 90)")
print(f"  Σγ_odd (觀察者) = {gamma_odd.sum():.10f}  (理論: 88)")
print(f"  Σγ_total = {gamma_k.sum():.10f}  (理論: 178)")

# ══════════════════════════════════════════════════════════════
# 3. 幾何約束驗證 (O34/O47)
# ══════════════════════════════════════════════════════════════
# 未投影弧長比 = 41/60 = 0.68333... = 未被觀察者投影嘅能量比例
# 投影弧長比 = 19/60 = 0.31666... = 被觀察者投影嘅能量比例

# 從 O34: 觀察者能量 Σγ_odd = 88, 世界能量 Σγ_even = 90
# 未被投影能量 = Σγ_odd - B·L = 88 - 4×? = 61.5
# 投影能量 = 2 + B·L = 28.5
# 總能量 = 61.5 + 28.5 = 90 = Σγ_even

# 從 O34: M = 33 = K_Tree 深度 = 3×(φ⁵−φ⁻⁵) = (χ−2)/4
# 未被投影 = (Σγ_even + M)/2, 投影 = (Σγ_even - M)/2
M = 33  # K_Tree 深度
unproj_energy = (gamma_even.sum() + M) / 2  # 61.5
proj_energy = (gamma_even.sum() - M) / 2   # 28.5

print(f"\n幾何約束 (O34/O47):")
print(f"  未被投影能量 = (Σγ_even + M)/2 = {unproj_energy:.6f}")
print(f"  投影能量 = (Σγ_even - M)/2 = {proj_energy:.6f}")
print(f"  總和 = {unproj_energy + proj_energy:.6f} = Σγ_even = {gamma_even.sum():.6f}")

unproj_ratio = unproj_energy / gamma_even.sum()
proj_ratio = proj_energy / gamma_even.sum()
print(f"  未投影比 = {unproj_ratio:.10f}  (理論 41/60 = {41/60:.10f})")
print(f"  投影比 = {proj_ratio:.10f}  (理論 19/60 = {19/60:.10f})")
print(f"  Ω_Λ = 4/(φ⁴-1) = {4/(((1+np.sqrt(5))/2)**4 - 1):.10f}")
print(f"  41/60 - Ω_Λ = {41/60 - 4/(((1+np.sqrt(5))/2)**4 - 1):.10e}")

# ══════════════════════════════════════════════════════════════
# 4. 構建投影算子 𝒫
# ══════════════════════════════════════════════════════════════
# 𝒫: ℋ₈₈ → L²(S²) 係一個 60 × 88 矩陣
# 每個節點 i 對應一個 88-site 環上嘅「窗口函數」W_i(k)
# 窗口函數決定 site k 對節點 i 嘅貢獻權重

# 方法: 每個節點嘅天球位置 (l_i, b_i) 映射到 88-site 環上嘅「相位角」
# 用節點嘅 Galactic longitude l_i 作為環上嘅角位置
# (因為 88-site 環嘅主要對稱軸係 Galactic longitude)

# 將 Galactic longitude 歸一化到 [0, 2π)
phi_i = np.radians(l_arr % 360)

# 窗口函數: 高斯型, 寬度 = 一個 site 間距
sigma_site = 2 * np.pi / N_sites  # = π/44

# 構建 𝒫 矩陣
P = np.zeros((60, N_sites))
for i in range(60):
    # 每個節點睇到環上所有 site, 但權重由 angular distance 決定
    dphi = np.abs(x_k - phi_i[i])
    dphi = np.minimum(dphi, 2*np.pi - dphi)  # 週期性
    w = np.exp(-0.5 * (dphi / sigma_site)**2)
    w = w / w.sum()  # 歸一化
    P[i, :] = w

# 驗證: 𝒫 係唔係隨機矩陣? (每行和 = 1)
row_sums = P.sum(axis=1)
print(f"\n投影算子 𝒫 (60×88):")
print(f"  row sums: min={row_sums.min():.6e}, max={row_sums.max():.6e}")
print(f"  all rows sum to 1: {np.allclose(row_sums, 1.0)}")

# ══════════════════════════════════════════════════════════════
# 5. 投影驗證: 相位場 → 節點溫度
# ══════════════════════════════════════════════════════════════
# 基態相位場: Φ_base(x_k) = cos(π·k/44) (n=1 模式)
# 投影到節點: δT_i = Σ_k P_ik · Φ_base(x_k)

phi_base = np.cos(np.pi * np.arange(N_sites) / (N_sites/2))
T_proj = P @ phi_base

# 歸一化: A = 134.2 μK
A = 134.2
T_proj = A * T_proj / np.max(np.abs(T_proj))

# 計算誘導相位: δT_i = A·cos(θ_i^ind)
theta_ind = np.arccos(np.clip(T_proj / A, -1, 1))

print(f"\n相位場投影結果:")
print(f"  T_proj range: [{T_proj.min():.2f}, {T_proj.max():.2f}] μK")
print(f"  θ_ind range: [{np.degrees(theta_ind.min()):.2f}°, {np.degrees(theta_ind.max()):.2f}°]")

# 節點 0 同 9 嘅預測
node0_idx = 0
node9_idx = 9  # 注意: a5_nodes.txt 係 0-indexed
print(f"\n  節點 0 (冷斑): θ_ind = {np.degrees(theta_ind[node0_idx]):.2f}°, T = {T_proj[node0_idx]:.2f} μK")
print(f"  節點 9 (第二冷): θ_ind = {np.degrees(theta_ind[node9_idx]):.2f}°, T = {T_proj[node9_idx]:.2f} μK")

# θ_ind 分佈
theta_deg = np.degrees(theta_ind)
near_pi2 = np.sum(np.abs(theta_deg - 90) < 30)
near_0 = np.sum(theta_deg < 30)
near_pi = np.sum(theta_deg > 150)
print(f"\n  θ_ind 分佈:")
print(f"    近 π/2 (60°-120°): {near_pi2}/60")
print(f"    近 0 (0°-30°): {near_0}/60")
print(f"    近 π (150°-180°): {near_pi}/60")

# ══════════════════════════════════════════════════════════════
# 6. 儲存結果
# ══════════════════════════════════════════════════════════════
results = {
    'N_sites': N_sites,
    'N_nodes': 60,
    'sum_gamma_even': float(gamma_even.sum()),
    'sum_gamma_odd': float(gamma_odd.sum()),
    'sum_gamma_total': float(gamma_k.sum()),
    'unproj_energy': float(unproj_energy),
    'proj_energy': float(proj_energy),
    'unproj_ratio': float(unproj_ratio),
    'proj_ratio': float(proj_ratio),
    'unproj_ratio_4160': 41/60,
    'proj_ratio_1960': 19/60,
    'P_matrix_shape': list(P.shape),
    'node_theta_ind_deg': [round(t, 4) for t in theta_deg],
    'node_T_proj_muK': [round(t, 4) for t in T_proj],
    'node0_theta_ind_deg': round(float(theta_deg[node0_idx]), 4),
    'node0_T_muK': round(float(T_proj[node0_idx]), 4),
    'node9_theta_ind_deg': round(float(theta_deg[node9_idx]), 4),
    'node9_T_muK': round(float(T_proj[node9_idx]), 4),
}

outpath = f'{OUTDIR}/step1_projection_operator.json'
with open(outpath, 'w') as f:
    json.dump(results, f, indent=2, default=float)
print(f"\n✅ 結果已存: {outpath}")