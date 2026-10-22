#!/usr/bin/env python3
"""O45 — GL 疇網絡: 60 節點 = 60 個 GL 凝聚疇 (2026-09-12, v2 用 T_pix)
假設: 每節點 i 係 GL 疇中心, T_pix,i (4.17° smooth) 反映疇大小 R_i
      T_i = −A·tanh²(R_i/ξ)·smooth 效應 — 大疇飽和 → |T|→A; 細疇欠飽和
反推 R_i, 檢查分佈結構 + 同網絡幾何關聯
"""
import json
import os
import numpy as np
import healpy as hp

A = 134.2
XI = 0.663   # GL 相干長度 (fit)
PROJECT = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
CACHE = os.path.join(PROJECT, 'open_problems_fresh/o5_catalog_compare/data/smooth_cache')
data = json.load(open('data/02_smhw_full_data.json'))

# 60 節點銀河座標
gal = np.array([data['nodes'][f'node{i}']['gal'] for i in range(60)])
l, b = gal.T

# 4.17° smooth map → 抽 60 節點 pixel 溫度
m = hp.read_map(os.path.join(CACHE, 'smica2_smooth4.17.fits'))
pix = hp.ang2pix(hp.get_nside(m), l, b, lonlat=True)
T_pix = m[pix] * 1e6  # μK

print("=== 60 節點 T_pix (4.17° smooth) ===")
print(f"  mean = {T_pix.mean():+.2f} μK, std = {T_pix.std():.2f}")
print(f"  min = {T_pix.min():+.2f} (node {T_pix.argmin()}), max = {T_pix.max():+.2f} (node {T_pix.argmax()})")

# 冷節點: GL 疇反推 R_i
cold = T_pix < 0
print(f"\n冷節點數: {cold.sum()}/60")
print(f"\n{'node':>4} {'T_pix(μK)':>10} {'|T|/A':>7} {'R_i(°)':>8} {'距冷斑':>8} {'hop':>5}")
R_cold_map = {}
for i in np.where(cold)[0]:
    ratio = abs(T_pix[i])/A
    R_i = np.inf if ratio >= 1 else XI*np.arctanh(np.sqrt(ratio))
    R_cold_map[int(i)] = float(R_i)
    # 距冷斑
    l0, b0 = gal[0]
    cosd = np.sin(np.radians(b[i]))*np.sin(np.radians(b0)) + \
           np.cos(np.radians(b[i]))*np.cos(np.radians(b0))*np.cos(np.radians(l[i]-l0))
    ad = np.degrees(np.arccos(np.clip(cosd, -1, 1)))
    print(f"{i:>4} {T_pix[i]:>10.2f} {ratio:>7.3f} {R_i:>8.2f} {ad:>8.2f} {ad/26.17:>5.1f}")

R_cold_arr = np.array([v for v in R_cold_map.values() if np.isfinite(v)])
print(f"\n冷節點 R_i (有限): n={len(R_cold_arr)}, mean={R_cold_arr.mean():.2f}°, std={R_cold_arr.std():.2f}°")
print(f"  min={R_cold_arr.min():.2f}, max={R_cold_arr.max():.2f}")

# 冷斑 node0 R (飽和假設 check)
print(f"\n冷斑 node0: T_pix={T_pix[0]:.2f}, |T|/A={abs(T_pix[0])/A:.3f}")
if abs(T_pix[0])/A > 0.98:
    print("  → 飽和 (R_0 ≫ ξ), 同 GL 疇 R*=6.02° 一致 ✓")
else:
    print(f"  → 欠飽和 R_0={XI*np.arctanh(np.sqrt(abs(T_pix[0])/A)):.2f}°")

# node 9 (第二冷) 檢查
print(f"\nnode 9: T_pix={T_pix[9]:.2f}, R_9={R_cold_map.get(9, np.nan):.2f}°")
print(f"node 9 距冷斑 = 26.17° = 1.0 hop (A₅ 網絡最近鄰)")

json.dump({'A': A, 'xi': XI, 'T_pix': T_pix.tolist(), 'cold_R': R_cold_map},
          open('data/16_gl_network.json', 'w'), indent=2)
print("\n儲存: data/16_gl_network.json")

