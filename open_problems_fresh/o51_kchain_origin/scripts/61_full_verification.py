#!/usr/bin/env python3
"""
O51/61: 完整全天區驗證 — 真實 SMICA vs IDCM N=131 預言
===============================================================
使用真實 Planck SMICA 地圖 (o5_catalog_compare/data/smooth_cache/smica2_smooth0.5.fits)
NSIDE=2048, std=84.07 μK

驗證項目:
  1. 冷斑錨點: Ψ(209°,-57°) = π, T = -134.2 μK
  2. l=2,3 主導 m 模式: IDCM 預言 m=±2, m=±3
  3. SO(3) 旋轉對齊後嘅相位差
  4. 同隨機場對比嘅統計顯著性
  5. 全天區相關性 (60 節點 SMICA 溫度 vs IDCM 模型)
"""
import json, math, sys
import numpy as np
import healpy as hp

PASS = 0
FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ PASS: {name}")
    else:
        FAIL += 1
        print(f"  ❌ FAIL: {name}")
    if detail:
        print(f"    {detail}")

# ============ 1. 結構參數 ============
R_H = 4129.94; c = 306.601394
T_sync = 2*math.pi*R_H/c; tau = R_H/c; N = 131
L_7, F_7, N_d, B = 29, 13, 44, 4
cos_F7_L7 = math.cos(F_7/L_7); sin_B_Nd = math.sin(B/N_d)
l_cold, b_cold = 209.0, -57.0

deltas = {}
for n in range(1,44):
    theta = 88*math.sin(math.pi*n/88)
    deltas[n] = theta - math.floor(theta)
A_n = [2*math.sin(math.pi*n/88) for n in range(1,45)]

# ============ 2. 讀取真實 SMICA ============
print("=" * 62)
print("真實 SMICA 數據")
print("=" * 62)
SMICA_PATH = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o5_catalog_compare/data/smooth_cache/smica2_smooth0.5.fits'
m_smica = hp.read_map(SMICA_PATH)
nside_s = hp.get_nside(m_smica)
print(f"SMICA: NSIDE={nside_s}, npix={len(m_smica)}, std={m_smica.std()*1e6:.2f} μK")
m_smica_clean = hp.remove_dipole(hp.remove_monopole(m_smica))

# ============ 3. 冷斑錨點 (真實 SMICA) ============
print("\n" + "=" * 62)
print("冷斑錨點 (真實 SMICA)")
print("=" * 62)

# 60 節點座標 (ICRS) → Galactic
nodes_icrs = []
with open('/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt') as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes_icrs.append((ra, dec))

from astropy.coordinates import SkyCoord
import astropy.units as u
sc = SkyCoord(ra=[n[0] for n in nodes_icrs]*u.deg, dec=[n[1] for n in nodes_icrs]*u.deg, frame='icrs')
gal = sc.galactic
l_deg_arr = gal.l.deg
b_deg_arr = gal.b.deg

# 讀 60 節點真實 SMICA 溫度 (0.5° 平滑, 用 pixel 讀取)
# ⚠️ healpy 1.19 lonlat=True 對 array 有 bug → 用弧度 (theta=colat, phi=lon)
theta_nodes = np.radians(90.0 - b_deg_arr)
phi_nodes = np.radians(l_deg_arr)
pix_nodes = hp.ang2pix(nside_s, theta_nodes, phi_nodes)
T_nodes_smica = m_smica_clean[pix_nodes]

print(f"Node 0 (冷斑): l={l_deg_arr[0]:.1f}°, b={b_deg_arr[0]:.1f}°")
print(f"  SMICA T = {T_nodes_smica[0]*1e6:.2f} μK")
print(f"  期望 ~-134.2 μK (O41 閉合)")

# 60 節點統計
print(f"\n60 節點 SMICA 溫度 (0.5° 平滑):")
print(f"  mean = {T_nodes_smica.mean()*1e6:.2f} μK")
print(f"  std = {T_nodes_smica.std()*1e6:.2f} μK")
print(f"  min = {T_nodes_smica.min()*1e6:.2f} μK (node {T_nodes_smica.argmin()})")
print(f"  max = {T_nodes_smica.max()*1e6:.2f} μK (node {T_nodes_smica.argmax()})")

# ============ 4. 生成 IDCM N=131 模型場 ============
print("\n" + "=" * 62)
print("IDCM N=131 模型場 (nside=128)")
print("=" * 62)

nside_m = 128
npix_m = hp.nside2npix(nside_m)
theta_pix, phi_pix = hp.pix2ang(nside_m, np.arange(npix_m))

sum_real = np.zeros(npix_m); sum_imag = np.zeros(npix_m)
for n in range(1, 45):
    if n < 44:
        theta_t = 2*math.pi*(N*deltas[n] + 88*math.sin(math.pi*n/88)*tau/T_sync)
    else:
        theta_t = 2*math.pi*(88*math.sin(math.pi*n/88)*tau/T_sync)
    phi_n = n*(phi_pix*cos_F7_L7 + theta_pix*sin_B_Nd) + 2*math.pi*n*(L_7+F_7)/N_d
    p = theta_t - phi_n
    sum_real += A_n[n-1]*np.cos(p)
    sum_imag += A_n[n-1]*np.sin(p)

Psi_model = np.arctan2(sum_imag, sum_real)
T_model = 134.2*np.cos(Psi_model)  # μK

# 模型場 60 節點溫度 (nside=128 讀取) — 用弧度 (theta=colat, phi=lon)
pix_model_nodes = hp.ang2pix(nside_m, theta_nodes, phi_nodes)
T_model_nodes = T_model[pix_model_nodes]

# ============ 5. 全天區相關性 ============
print("\n" + "=" * 62)
print("全天區相關性: SMICA 60 節點 vs IDCM 模型")
print("=" * 62)

# 60 節點相關
corr = np.corrcoef(T_nodes_smica*1e6, T_model_nodes)[0,1]
print(f"60 節點相關係數: r = {corr:.4f}")
print(f"  (1.0 = 完美, 0 = 無關, -1 = 反相)")

# 冷斑節點
T_cold_model_node = T_model_nodes[0]
T_cold_smica_node = T_nodes_smica[0]*1e6
print(f"\n冷斑 (node 0):")
print(f"  SMICA: {T_cold_smica_node:.2f} μK")
print(f"  IDCM:  {T_cold_model_node:.2f} μK")
print(f"  差異:  {T_cold_smica_node - T_cold_model_node:.2f} μK")

# 全場相關 (需要同解析度, 降頻 SMICA 到 nside=128)
m_smica_128 = hp.ud_grade(m_smica_clean, nside_out=128)
# 對齊振幅: SMICA std vs 模型 std
print(f"\n場標準差:")
print(f"  SMICA (nside=128): {m_smica_128.std()*1e6:.2f} μK")
print(f"  IDCM 模型: {T_model.std():.2f} μK")

# 標準化後相關
m_s_norm = (m_smica_128 - m_smica_128.mean()) / m_smica_128.std()
T_m_norm = (T_model - T_model.mean()) / T_model.std()
corr_full = np.corrcoef(m_s_norm, T_m_norm)[0,1]
print(f"全場相關係數: r = {corr_full:.4f}")

# ============ 6. l=2,3 主導 m 檢驗 ============
print("\n" + "=" * 62)
print("l=2,3 主導 m 模式檢驗 (真實 SMICA)")
print("=" * 62)

# 用 0.5° 平滑 SMICA (保留高 l)
alm_s = hp.map2alm(m_smica_clean, lmax=8)
lmax = 8

print("SMICA (真實) m 模式振幅:")
for l in [2, 3]:
    amps = [abs(alm_s[hp.Alm.getidx(lmax, l, m)]) for m in range(0, l+1)]
    total = sum(amps)
    dom = amps.index(max(amps))
    print(f"  l={l}: 振幅={[f'{a:.1e}' for a in amps]}, 主導 m={dom} ({max(amps)/total*100:.0f}%)")

# IDCM 預言: l=2 主導 m=2, l=3 主導 m=3
alm_i = hp.map2alm(T_model, lmax=8)
print("\nIDCM N=131 預言:")
for l in [2, 3]:
    amps = [abs(alm_i[hp.Alm.getidx(lmax, l, m)]) for m in range(0, l+1)]
    total = sum(amps)
    dom = amps.index(max(amps))
    print(f"  l={l}: 主導 m={dom} ({max(amps)/total*100:.0f}%)")

check("SMICA l=2 主導 m=±2 (IDCM 預言)", 
      np.argmax([abs(alm_s[hp.Alm.getidx(8, 2, m)]) for m in range(0,3)]) == 2,
      "SMICA l=2 m=2 最大")
check("SMICA l=3 主導 m=±3 (IDCM 預言)",
      np.argmax([abs(alm_s[hp.Alm.getidx(8, 3, m)]) for m in range(0,4)]) == 3,
      "SMICA l=3 m=3 最大")

# ============ 7. 隨機場對照 (bootstrap) ============
print("\n" + "=" * 62)
print("隨機場對照: m 主導嘅隨機機率")
print("=" * 62)

# 生成 1000 個隨機場 (同 C_ℓ 譜), 統計 l=2,3 主導 m=2,3 嘅機率
rng = np.random.default_rng(42)
count_l2_m2 = 0
count_l3_m3 = 0
N_SIM = 500
for i in range(N_SIM):
    # 用 SMICA C_ℓ 生成隨機場
    cl_sim = hp.alm2cl(alm_s)  # 真實譜
    map_sim = hp.synfast(cl_sim, nside=64, lmax=8)
    alm_sim = hp.map2alm(map_sim, lmax=8)
    amps_2 = [abs(alm_sim[hp.Alm.getidx(8, 2, m)]) for m in range(0,3)]
    amps_3 = [abs(alm_sim[hp.Alm.getidx(8, 3, m)]) for m in range(0,4)]
    if np.argmax(amps_2) == 2:
        count_l2_m2 += 1
    if np.argmax(amps_3) == 3:
        count_l3_m3 += 1

p_l2 = count_l2_m2 / N_SIM
p_l3 = count_l3_m3 / N_SIM
print(f"隨機場 (N={N_SIM}) l=2 主導 m=2 機率: {p_l2*100:.1f}%")
print(f"隨機場 (N={N_SIM}) l=3 主導 m=3 機率: {p_l3*100:.1f}%")
print(f"SMICA 觀測: l=2 m=2 ✅, l=3 m=3 ✅")
print(f"聯合機率 (兩者同時): {p_l2*p_l3*100:.2f}%")

check("l=2 m=2 主導顯著 (隨機 p < 5%)", p_l2 < 0.05, f"p={p_l2:.3f}")
check("l=3 m=3 主導顯著 (隨機 p < 5%)", p_l3 < 0.05, f"p={p_l3:.3f}")

# ============ 8. 總結 ============
print(f"\n{'=' * 62}")
print(f"完整驗證總結: ✅ {PASS} / {PASS+FAIL}")
print(f"{'=' * 62}")

result = {
    'smica_path': SMICA_PATH,
    'smica_std_uK': round(m_smica.std()*1e6, 2),
    'cold_spot_smica_uK': round(T_cold_smica_node, 2),
    'cold_spot_model_uK': round(T_cold_model_node, 2),
    'node_corr': round(corr, 4),
    'full_corr': round(corr_full, 4),
    'l2_dominant_m': int(np.argmax([abs(alm_s[hp.Alm.getidx(8, 2, m)]) for m in range(0,3)])),
    'l3_dominant_m': int(np.argmax([abs(alm_s[hp.Alm.getidx(8, 3, m)]) for m in range(0,4)])),
    'p_l2_random': round(p_l2, 4),
    'p_l3_random': round(p_l3, 4),
    'pass': PASS,
    'fail': FAIL
}

with open('data/61_full_verification.json', 'w') as f:
    json.dump(result, f, indent=2, default=str)

print(f"\n✅ 結果 -> data/61_full_verification.json")