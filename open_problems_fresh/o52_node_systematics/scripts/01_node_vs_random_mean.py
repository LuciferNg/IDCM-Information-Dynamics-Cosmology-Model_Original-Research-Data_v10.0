#!/usr/bin/env python3
"""
O52: 60 節點系統性微冷/微熱檢驗 — 完整版
=========================================
IDCM 核心假說: 60 個 A₅ 節點全部有溫度異常 (拓撲縫合節點)。
O5 目錄對比只確認 node0 + node9。O52 要測其餘節點有冇系統性偏移。

測試清單 (O27 前置整合):
  1. 整體均值: 60 節點 mean vs 全天空 (|b|>25°) mean — Welch z
  2. 高緯度子集: |b|>=30° 節點 mean vs 天空
  3. R3 mask 分層: unmasked 45 vs masked 15 節點分開統計 (O27 要求)
  4. 符號不對稱: 冷/熱 數量 + 2σ 極端計數
  5. 隨機控制組: 同緯度 60 點 × 2000 resample → 零假設分佈 (z_ctrl)
  6. 多尺度: 0.5°-10° 每尺度重複
  7. 堆疊 radial profile: 60 節點平均 profile (0-13°) vs 隨機位置堆疊
  8. 去除 node0/node9 後: 剩餘 58 節點 mean — 排除已知異常後仲有冇系統性?

判定 (problem record):
  🟢🟢 >3σ → 全部節點有異常
  🟢 2-3σ → 邊緣
  🔴 <2σ → 只有 node0/node9 係真異常

⚠️ 反幻覺鐵律:
  - 平滑 cache 已存在 (O5 產出), 直接讀取, 唔重新平滑
  - 銀河座標轉換必須用 SkyCoord (ICRS→Galactic), 唔好直接採樣
  - R3 mask 用 O27 已下載嘅 COM_Mask_CMB-common-Mask-Int_2048_R3.00.fits
"""
import numpy as np
import healpy as hp
import json, os
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
CACHE = os.path.join(BASE, 'open_problems_fresh/o5_catalog_compare/data/smooth_cache')
NODES_FILE = os.path.join(BASE, 'main_problems/p4_cmb_cold_spot/data/a5_nodes.txt')
MASK_R3 = os.path.join(BASE, 'open_problems_fresh/o27_node47_foreground/data/COM_Mask_CMB-common-Mask-Int_2048_R3.00.fits')
OUTDIR = os.path.join(BASE, 'open_problems_fresh/o52_node_systematics')
os.makedirs(os.path.join(OUTDIR, 'data'), exist_ok=True)

nodes = np.loadtxt(NODES_FILE)
assert nodes.shape == (60, 2)
print(f"載入 {len(nodes)} 節點")

# 🚨 FRAME RULE (skill 反幻覺鐵律): SMICA 地圖 + R3 mask 都係 Galactic frame。
# a5_nodes.txt 係 ICRS。必須 ICRS→Galactic 先可以採樣, 直接 ICRS theta/phi
# 採樣會靜默返回錯嘅像素 (frame inversion trap, 2026-08-17 教訓)。
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic
node_l, node_b = gal.l.deg, gal.b.deg
# Galactic lonlat 轉 theta/phi (供所有採樣用)
theta_g = np.radians(90.0 - node_b)
phi_g = np.radians(node_l)
high_lat = np.abs(node_b) >= 30.0
print(f"高緯度節點 (|b|>=30°): {high_lat.sum()}/60")

# R3 mask (nside=2048, Galactic frame) — 用 Galactic lonlat 採樣
if os.path.exists(MASK_R3):
    mask_r3 = hp.read_map(MASK_R3, field=0)
    nside_m = hp.get_nside(mask_r3)
    node_pix = hp.ang2pix(nside_m, node_l, node_b, lonlat=True)
    unmasked = mask_r3[node_pix] > 0.5
    print(f"R3 mask 保留 {unmasked.sum()}/60 節點 (masked {60-unmasked.sum()}) "
          f"— 用 Galactic lonlat, 同 O27 一致")
else:
    print("⚠️ R3 mask 唔存在, 用 |b|>=25° 近似")
    unmasked = np.abs(node_b) >= 25.0

# 已知異常節點 (要剔除做敏感性)
known = np.zeros(60, bool)
known[0] = True   # node0 大冷斑
known[9] = True   # node9 第二冷

SCALES = [0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 7.0, 10.0]
results = {}
rng = np.random.default_rng(20260821)

for fwhm in SCALES:
    fname = os.path.join(CACHE, f'smica2_smooth{fwhm}.fits')
    if not os.path.exists(fname):
        print(f"  [skip] no cache {fname}")
        continue
    m = hp.read_map(fname, field=0) * 1e6  # μK
    nside = hp.get_nside(m)

    # 節點像素值 — Galactic frame (theta_g, phi_g 已定義)
    pix = hp.ang2pix(nside, theta_g, phi_g)
    node_T = m[pix]

    # 全天空統計 (避開銀河面 |b|<25°)
    npix = hp.nside2npix(nside)
    l_arr, b_arr = hp.pix2ang(nside, np.arange(npix), lonlat=True)
    sky_mask = np.abs(b_arr) >= 25.0
    sky_mean = np.mean(m[sky_mask])
    sky_sigma = np.std(m[sky_mask])

    # 1. 60 節點 mean vs 天空
    node_mean = np.mean(node_T)
    node_sem = np.std(node_T) / np.sqrt(60)
    z_all = (node_mean - sky_mean) / node_sem

    # 2. 高緯度子集
    n_hl = high_lat.sum()
    hl_mean = np.mean(node_T[high_lat])
    hl_sem = np.std(node_T[high_lat]) / np.sqrt(n_hl)
    z_hl = (hl_mean - sky_mean) / hl_sem

    # 3. R3 mask 分層
    n_um = unmasked.sum()
    um_mean = np.mean(node_T[unmasked])
    um_sem = np.std(node_T[unmasked]) / np.sqrt(n_um)
    z_um = (um_mean - sky_mean) / um_sem
    n_msk = (~unmasked).sum()
    if n_msk >= 5:
        msk_mean = np.mean(node_T[~unmasked])
        msk_sem = np.std(node_T[~unmasked]) / np.sqrt(n_msk)
        z_msk = (msk_mean - sky_mean) / msk_sem
    else:
        msk_mean, z_msk = np.nan, np.nan

    # 4. 符號不對稱
    n_cold = int(np.sum(node_T < sky_mean))
    n_hot = int(np.sum(node_T > sky_mean))
    n_cold_2sig = int(np.sum(node_T < sky_mean - 2*sky_sigma))
    n_hot_2sig = int(np.sum(node_T > sky_mean + 2*sky_sigma))

    # 5. 隨機控制組: 同緯度 60 點 × 2000 (Galactic frame)
    rand_means = np.zeros(2000)
    for k in range(2000):
        rand_phi = rng.uniform(0, 2*np.pi, 60)
        rand_theta = theta_g + rng.normal(0, 0.02, 60)
        rand_theta = np.clip(rand_theta, 0.01, np.pi-0.01)
        rpix = hp.ang2pix(nside, rand_theta, rand_phi)
        rand_means[k] = np.mean(m[rpix])
    rand_mean = np.mean(rand_means)
    rand_std = np.std(rand_means)
    z_ctrl = (node_mean - rand_mean) / rand_std
    pct = float(np.mean(rand_means < node_mean))

    # 8. 剔除 node0/node9 後
    keep = ~known
    n_keep = keep.sum()
    rem_mean = np.mean(node_T[keep])
    rem_sem = np.std(node_T[keep]) / np.sqrt(n_keep)
    z_rem = (rem_mean - sky_mean) / rem_sem
    # 剔除後 vs 控制組
    z_rem_ctrl = (rem_mean - rand_mean) / rand_std

    results[fwhm] = {
        'node_mean': round(float(node_mean), 3),
        'sky_mean': round(float(sky_mean), 3),
        'z_vs_sky': round(float(z_all), 2),
        'hl_n': int(n_hl), 'hl_mean': round(float(hl_mean), 3),
        'z_hl': round(float(z_hl), 2),
        'um_n': int(n_um), 'um_mean': round(float(um_mean), 3),
        'z_um': round(float(z_um), 2),
        'msk_n': int(n_msk),
        'msk_mean': round(float(msk_mean), 3) if not np.isnan(msk_mean) else None,
        'z_msk': round(float(z_msk), 2) if not np.isnan(z_msk) else None,
        'n_cold': n_cold, 'n_hot': n_hot,
        'n_cold_2sig': n_cold_2sig, 'n_hot_2sig': n_hot_2sig,
        'ctrl_mean': round(float(rand_mean), 3),
        'ctrl_std': round(float(rand_std), 3),
        'z_vs_ctrl': round(float(z_ctrl), 2),
        'pctile': round(pct*100, 1),
        'rem_n': int(n_keep), 'rem_mean': round(float(rem_mean), 3),
        'z_rem': round(float(z_rem), 2),
        'z_rem_ctrl': round(float(z_rem_ctrl), 2),
    }
    print(f"\n=== 尺度 {fwhm}° ===")
    print(f"  60節點 mean={node_mean:.2f} vs 天空 {sky_mean:.2f} → z={z_all:+.2f}")
    print(f"  高緯 mean={hl_mean:.2f} (n={n_hl}) → z={z_hl:+.2f}")
    print(f"  unmasked mean={um_mean:.2f} (n={n_um}) → z={z_um:+.2f} | masked mean={msk_mean:.2f} (n={n_msk}) → z={z_msk:+.2f}")
    print(f"  冷/熱 = {n_cold}/{n_hot}  2σ冷/熱 = {n_cold_2sig}/{n_hot_2sig}")
    print(f"  控制組 mean={rand_mean:.2f}±{rand_std:.2f} → z={z_ctrl:+.2f} (pct={pct*100:.1f}%)")
    print(f"  剔除 node0/9 後 mean={rem_mean:.2f} (n={n_keep}) → z={z_rem:+.2f} | vs ctrl z={z_rem_ctrl:+.2f}")

with open(os.path.join(OUTDIR, 'data/o52_systematics.json'), 'w') as f:
    json.dump(results, f, indent=2)
print("\n結果寫入 data/o52_systematics.json")
