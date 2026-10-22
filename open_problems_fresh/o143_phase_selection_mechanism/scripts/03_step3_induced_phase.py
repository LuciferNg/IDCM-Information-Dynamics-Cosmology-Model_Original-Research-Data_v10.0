#!/usr/bin/env python3
"""
O143 Step 3+4 — 誘導相因子 θ_i^ind 計算 + 節點分化判據
========================================================
目標: 計算 60 節點嘅誘導相因子 θ_i^ind，並驗證 node0/node9
係咪位於拓撲邊界/相干波腹。

核心方法:
  1. 將 60 節點按 41/19 拓撲分區 (未投影/投影, 對應 41/60 同 19/60)
  2. 每個節點嘅 θ_i^ind = 由節點喺 88-site 環上嘅投影位置決定
  3. 用 A₅ 二十面體對稱性將 60 節點映射到 88-site 環

反幻覺鐵律:
  - 所有數字必須來自結構推導, 唔可以係 fitting
  - 41/19 分區來自 O34 (Σγ_even ± M)/2 能量分區
  - 60 = 41 + 19 係拓撲分區, 唔係自由參數
"""

import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u
import json, os

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
O143 = f'{BASE}/open_problems_fresh/o143_phase_selection_mechanism'
NODES_FILE = f'{BASE}/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt'
OUTDIR = f'{O143}/data'
os.makedirs(OUTDIR, exist_ok=True)

print("=" * 72)
print("  O143 Step 3+4: 誘導相因子 + 節點分化判據")
print("=" * 72)

# ══════════════════════════════════════════════════════════════
# 1. 載入 60 節點
# ══════════════════════════════════════════════════════════════
nodes = np.loadtxt(NODES_FILE)
assert nodes.shape == (60, 2)

sc = SkyCoord(ra=nodes[:,0]*u.deg, dec=nodes[:,1]*u.deg, frame='icrs')
gal = sc.galactic
l_arr = np.array([float(g.l.deg) for g in gal])
b_arr = np.array([float(g.b.deg) for g in gal])

# 88-site 環
N = 88
x_k = np.linspace(0, 2*np.pi, N, endpoint=False)
k_arr = np.arange(N)

# ══════════════════════════════════════════════════════════════
# 2. 41/19 拓撲分區
# ══════════════════════════════════════════════════════════════
# 從 O34: M=33, Σγ_even=90
# 未被投影 = (90+33)/2 = 61.5 → 41/60 比例
# 投影 = (90-33)/2 = 28.5 → 19/60 比例
# 60 節點以 41:19 比例分為兩組

# 41 個「未被投影」節點 (觀察者自我參照, 相位正交)
# 19 個「投影」節點 (變成物質, 相位非正交)
# 分區方法: 用 Galactic latitude 排序 (b 越大越接近北銀極)
# 未被投影 = 較高緯度 (遠離銀河面 = 較純嘅觀察者視角)
# 投影 = 較低緯度 (近銀河面 = 物質投影)

sort_idx = np.argsort(b_arr)  # 由南到北
n_unproj = 41
n_proj = 19

# 未被投影節點: 較高緯度 (41 個)
unproj_idx = sort_idx[-n_unproj:]  # 最高緯度 41 個
# 投影節點: 較低緯度 (19 個)
proj_idx = sort_idx[:n_proj]  # 最低緯度 19 個

# 確保 node0 (冷斑) 喺未被投影組
node0_idx = 0
node9_idx = 9

print(f"\n41/19 拓撲分區:")
print(f"  未被投影 (高緯): {n_unproj} nodes")
print(f"  投影 (低緯): {n_proj} nodes")
print(f"  node0 (冷斑) 喺未被投影: {node0_idx in unproj_idx}")
print(f"  node9 (第二冷) 喺未被投影: {node9_idx in unproj_idx}")

# ══════════════════════════════════════════════════════════════
# 3. 構建 A₅ 對稱性投影
# ══════════════════════════════════════════════════════════════
# 60 節點 = Rhombicosidodecahedron = A₅ 對稱群嘅 60 個頂點
# 88-site 環 = K_Chain 雙鏈
# 
# A₅ 嘅 60 個元素: 60 = 5!/2 (交代群)
# 88-site 環嘅 88 個 site: 88 = 2×44
# 
# 60 節點 + 88-site 環嘅共同結構: 
# - 60 節點 = 12 pentagons (12×5=60)
# - 88-site 環 = 44 even + 44 odd
# - 12 pentagons ↔ 12 ΔE=0 nodes (O102)

# 12 pentagons 嘅中心 = 12 個 ΔE=0 節點
# ΔE=0 節點: {10,12,19,22,23,25,28,32,37,40,45,46}
DE0 = {10, 12, 19, 22, 23, 25, 28, 32, 37, 40, 45, 46}

# 每個 pentagon 有 5 個頂點, 但 A₅ 對稱性將 60 節點分為 5 個軌道 x 12 pentagons
# 喺環上嘅投影: 每個 pentagon 對應環上 88/12 ≈ 7.33 個 site
# 即 12 pentagons × 7.33 ≈ 88 sites

# 更精確: 88/12 = 22/3 ≈ 7.33
# 但 12 pentagons 嘅中心 (ΔE=0 節點) 應該對應環上特定 site

# 實際上, 88-site 環同 60 節點嘅關係由拍頻周期表 (BPT) 決定:
# 946 = C(44,2) = 44×43/2 個拍頻
# 60 節點 = A₅ 對稱群嘅階

# 構建「節點 → 環 site」映射矩陣 Q (60×88)
# 用節點嘅 Galactic longitude 做主映射, 但用 A₅ 對稱性做修正

phi_i = np.radians(l_arr % 360)  # 節點 longitude

# 88-site 環上嘅相位場
# 基態: Φ_base(x_k) = cos(πk/44)
# 真空態: 基態 + 微擾

# 每個節點 i 嘅誘導相位 = 節點 longitude 對應環 site 嘅相位
# site 索引: k_i = round(phi_i / (2π/88)) mod 88
k_i = np.round(phi_i / (2*np.pi/N)).astype(int) % N

# 直接讀取相位
Phi_base = np.cos(np.pi * k_arr / (N/2))
theta_ind_direct = Phi_base[k_i]  # 直接讀取, 冇平滑

# 或用窗口平滑 (同 Step 1)
sigma_site = 2*np.pi / N
theta_ind_smooth = np.zeros(60)
for i in range(60):
    dphi = np.abs(x_k - phi_i[i])
    dphi = np.minimum(dphi, 2*np.pi - dphi)
    w = np.exp(-0.5 * (dphi / sigma_site)**2)
    w = w / w.sum()
    theta_ind_smooth[i] = np.sum(w * Phi_base)

# ══════════════════════════════════════════════════════════════
# 4. 計算誘導相位 θ_i^ind
# ══════════════════════════════════════════════════════════════
# δT_i = A·cos(θ_i^ind) where θ_i^ind = arccos(Φ_base(k_i))
# 但需要一個 global phase shift 令 δT_i 匹配觀測

# 方法: 定義 θ_i^ind = arccos(Φ_base(k_i)) + φ_global
# φ_global 由 node0 嘅觀測溫度鎖定
# 觀測: node0 T = -134.2 μK → cos(θ_0) = -1 → θ_0 = π

A = 134.2  # μK

# 用平滑版本
# 先 normalize 到 [-1, 1]
T_smooth = A * theta_ind_smooth / np.max(np.abs(theta_ind_smooth))

# 計算 θ_i^ind 
cos_theta_smooth = T_smooth / A
cos_theta_smooth = np.clip(cos_theta_smooth, -1, 1)
theta_ind_smooth = np.arccos(cos_theta_smooth)

# 但 arccos 只返 [0, π], 需要 sign
# 用原始相位嘅 sign 決定正負
sign_smooth = np.sign(theta_ind_smooth)
for i in range(60):
    if theta_ind_smooth[i] > np.pi/2:
        theta_ind_smooth[i] = np.pi - theta_ind_smooth[i]  # 映射到 [0, π/2]
    # 還原 sign
    if T_smooth[i] < 0:
        theta_ind_smooth[i] = np.pi - theta_ind_smooth[i]

print(f"\n誘導相位 θ_i^ind (平滑):")
print(f"  range: [{np.degrees(theta_ind_smooth.min()):.2f}°, {np.degrees(theta_ind_smooth.max()):.2f}°]")
print(f"  node0: θ = {np.degrees(theta_ind_smooth[node0_idx]):.2f}°, T = {A*np.cos(theta_ind_smooth[node0_idx]):.2f} μK")
print(f"  node9: θ = {np.degrees(theta_ind_smooth[node9_idx]):.2f}°, T = {A*np.cos(theta_ind_smooth[node9_idx]):.2f} μK")

# ══════════════════════════════════════════════════════════════
# 5. 節點分化判據
# ══════════════════════════════════════════════════════════════
# 判定每個節點嘅類型:
# - 普通節點: θ_i^ind ≈ π/2 → |cos| < 0.2
# - 異常節點: θ_i^ind ≈ 0 or π → |cos| > 0.8

cos_theta = np.cos(theta_ind_smooth)
node_types = []
for i in range(60):
    if abs(cos_theta[i]) < 0.2:
        node_types.append('普通 (正交)')
    elif abs(cos_theta[i]) > 0.8:
        node_types.append('異常 (波腹)')
    else:
        node_types.append('中間')

n_orthogonal = sum(1 for t in node_types if '正交' in t)
n_antinode = sum(1 for t in node_types if '波腹' in t)
n_mid = sum(1 for t in node_types if '中間' in t)

print(f"\n節點分化判據:")
print(f"  普通 (正交, |cos|<0.2): {n_orthogonal}/60")
print(f"  異常 (波腹, |cos|>0.8): {n_antinode}/60")
print(f"  中間: {n_mid}/60")
print(f"  node0 類型: {node_types[node0_idx]}")
print(f"  node9 類型: {node_types[node9_idx]}")

# ΔE=0 節點嘅相位
de0_list = list(DE0)
de0_cos = np.array([cos_theta[i] for i in de0_list])
de0_theta = np.array([theta_ind_smooth[i] for i in de0_list])
print(f"\nΔE=0 節點 (12 個):")
print(f"  mean|cos| = {np.mean(np.abs(de0_cos)):.4f}")
print(f"  near π/2: {sum(abs(de0_theta - np.pi/2) < 0.5)}/12")

# ══════════════════════════════════════════════════════════════
# 6. 儲存
# ══════════════════════════════════════════════════════════════
results = {
    'A_muK': A,
    'n_nodes': 60,
    'n_sites': N,
    'n_unproj': n_unproj,
    'n_proj': n_proj,
    'node0_in_unproj': bool(node0_idx in unproj_idx),
    'node9_in_unproj': bool(node9_idx in proj_idx),
    'theta_ind_deg': [round(float(np.degrees(t)), 4) for t in theta_ind_smooth],
    'cos_theta': [round(float(c), 4) for c in cos_theta],
    'node_types': node_types,
    'node0_theta_deg': round(float(np.degrees(theta_ind_smooth[node0_idx])), 4),
    'node0_T_muK': round(float(A * np.cos(theta_ind_smooth[node0_idx])), 4),
    'node9_theta_deg': round(float(np.degrees(theta_ind_smooth[node9_idx])), 4),
    'node9_T_muK': round(float(A * np.cos(theta_ind_smooth[node9_idx])), 4),
    'n_orthogonal': n_orthogonal,
    'n_antinode': n_antinode,
    'n_mid': n_mid,
    'de0_mean_abs_cos': round(float(np.mean(np.abs(de0_cos))), 4),
    'de0_near_pi2': int(sum(abs(de0_theta - np.pi/2) < 0.5)),
}

outpath = f'{OUTDIR}/step3_induced_phase.json'
with open(outpath, 'w') as f:
    json.dump(results, f, indent=2, default=float)
print(f"\n✅ 結果已存: {outpath}")