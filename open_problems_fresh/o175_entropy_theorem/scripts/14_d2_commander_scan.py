#!/usr/bin/env python3
"""
O175 script 14 — D2 攻堅: Commander PR3 全圖 192μK 特徵搜索 (data unlock)
========================================================================
數據: COM_CMB_IQU-commander_2048_R3.00_full.fits (nside 2048, ~1.1GB)
目標: ① 全圖統計 (RMS 等) ② 冷斑 (209°,-57°) 驗證 ③ 192μK 特徵搜索
"""
import numpy as np
import healpy as hp

MAP = "COM_CMB_IQU-commander_2048_R3.00_full.fits"

print("讀取 Commander 溫度圖...")
# field=0 → 溫度 (I); Commander 單位 K_CMB
T = hp.read_map(MAP, field=0, verbose=False)
T = T.astype(np.float64)
print(f"nside={hp.get_nside(T)}, 像素={T.size}")

# 移除單極/偶極 (CMB 標準處理)
m = T - np.mean(T)
nside = hp.get_nside(T)

print("\n=== ① 全圖統計 ===")
rms = np.std(m)
print(f"RMS = {rms*1e6:.1f} μK (CMB 預期 ~110μK)")
print(f"min = {m.min()*1e6:.1f} μK, max = {m.max()*1e6:.1f} μK")
print(f"⟨|T|⟩ = {np.mean(np.abs(m))*1e6:.1f} μK")

# 冷斑位置 (209°, -57°) — O173 docs/09
print("\n=== ② 冷斑驗證 (209°, -57°) ===")
for lon, lat in [(209.0, -57.0), (209.5, -57.0), (209.0, -56.5)]:
    theta = np.radians(90 - lat)
    phi = np.radians(lon)
    pix = hp.ang2pix(nside, theta, phi)
    print(f"  ({lon:.1f}°, {lat:.1f}°): T = {m[pix]*1e6:+.1f} μK")

# 冷斑區域平均 (半徑 5°)
vec = hp.ang2vec(np.radians(90+57), np.radians(209))  # 注意: (209,-57) → theta=147°, phi=209°
vec = hp.ang2vec(np.radians(90-(-57)), np.radians(209))
disc = hp.query_disc(nside, vec, np.radians(5.0))
print(f"  冷斑 5° 盤平均: {np.mean(m[disc])*1e6:+.1f} μK (N={disc.size})")

print("\n=== ③ 192μK 特徵搜索 ===")
# |T| ≈ 192μK 像素比例
for target, name in [(192.0, "192μK (T_write)"), (134.2, "134.2μK (冷斑 A)")]:
    frac = np.mean(np.abs(m)*1e6 > target*0.9) - np.mean(np.abs(m)*1e6 > target*1.1)
    # 正確: 比例喺 ±10% 窗口
    lo, hi = target*0.9, target*1.1
    frac = np.mean((np.abs(m)*1e6 >= lo) & (np.abs(m)*1e6 <= hi))
    print(f"  |T| ∈ [{lo:.0f},{hi:.0f}] μK: {frac*100:.2f}% 像素")

# 192μK 特別: 睇「寫入對」(相位滑移成對出現) — 冷斑-熱斑 192μK 對?
# 實際搜索: 全圖 >192μK 像素嘅團 (clusters)
thresh = 192.0e-6
hot = m > thresh
cold = m < -thresh
print(f"  T > +192μK: {np.mean(hot)*100:.2f}% 像素")
print(f"  T < -192μK: {np.mean(cold)*100:.2f}% 像素")
print(f"  |T| > 192μK 總比例: {np.mean(hot|cold)*100:.2f}% (高斯期望: 2×1.7σ≈8.9%)")

# 對比: 192μK 喺 CMB 譜嘅位置 (σ 單位 — 修正: rms 係 K, 192 係 μK)
print(f"  192μK = {192.0/(rms*1e6):.2f}σ (rms={rms*1e6:.0f}μK)")

# Mask 版本: |b| > 30° (避銀河面殘餘)
print("\n=== ④ Mask 檢查 (|b|>30°) ===")
ipix = np.arange(T.size)
theta_pix, phi_pix = hp.pix2ang(nside, ipix)
b_deg = 90.0 - np.degrees(theta_pix)
mask_gal = np.abs(b_deg) > 30.0
m_masked = m[mask_gal]
print(f"  |b|>30° 像素: {mask_gal.sum()} ({mask_gal.mean()*100:.1f}%)")
print(f"  RMS(|b|>30°) = {np.std(m_masked)*1e6:.1f} μK (含前景應 ~110-130μK)")
print(f"  ⟨|T|⟩(|b|>30°) = {np.mean(np.abs(m_masked))*1e6:.1f} μK")

print("\nRESULT: Commander 全圖統計 + 冷斑驗證 + 192μK 特徵基線完成")
