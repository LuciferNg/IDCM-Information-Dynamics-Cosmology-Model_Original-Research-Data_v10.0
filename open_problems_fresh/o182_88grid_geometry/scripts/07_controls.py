#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O182 scripts/07 — 嚴格控制實驗: G88 嘅 M1 偏高係緯度定經度結構?
================================================================
三個控制:
  C1. 隨機全天空 |b|>20: M1 期望 (高斯/地圖空想)
  C2. 經度置換: 固定 G88 嘅 88 個 |b|, 隨機打亂 l (同緯度控制!)
      若 M1(G88) ≈ M1(C2) -> 偏高係緯度驅動 (混雜)
      若 M1(G88) > M1(C2) -> 有經度結構 (真正信號)
  C3. 隨機 88 點完全均勻 (全天空, 無緯度限制) 對比
"""
import numpy as np
import healpy as hp
from pathlib import Path
import json

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
OUT = ROOT / "o182_88grid_geometry/data"
A = 134.2
T11 = 11/45
NSIDE = 512
NREAL = 1000
RNG = np.random.default_rng(7)

MAPS = {
    "SMICA":     ROOT / "o175_entropy_theorem/data/planck/COM_CMB_IQU-smica_2048_R3.00_full.fits",
    "Commander": ROOT / "data_gated_unlock/COM_CMB_IQU-commander_2048_R3.00_full.fits",
    "SEVEM":     ROOT / "o42_independent_measurement_A/data/bands/sevem_final.fits",
}

# G88 銀河座標
from astropy.coordinates import SkyCoord
import astropy.units as u
def to_gal(pts):
    sc = SkyCoord(ra=pts[:, 0]*u.deg, dec=pts[:, 1]*u.deg, frame='icrs')
    g = sc.galactic
    return np.column_stack([g.l.deg, g.b.deg])

lb88 = to_gal(np.loadtxt(OUT / "g88_nodes.txt"))
lbA5 = to_gal(np.loadtxt(ROOT / "cmb_cold_spot/data/a5_nodes.txt"))
print(f"G88: n={len(lb88)}, |b|<20: {(np.abs(lb88[:,1])<20).sum()}")
print(f"A5 : n={len(lbA5)}, |b|<20: {(np.abs(lbA5[:,1])<20).sum()}")

# 降採樣平滑圖 (nside 512) + 節點採樣函數
def m1_of(T):
    T = np.asarray(T)
    return np.mean(np.abs(T - T.mean())) / A

for fwhm in [4.17, 5.0]:
    print(f"\n========== 平滑 {fwhm}° ==========")
    for name, path in MAPS.items():
        m = hp.read_map(str(path), field=0).astype(np.float64)
        m = hp.ud_grade(m, NSIDE, order_in='RING')
        ms = hp.smoothing(m, fwhm=np.radians(fwhm), verbose=False)
        ms = hp.remove_dipole(ms, verbose=False)
        # 隨機控制: |b|>20 均勻球面
        c1 = []
        c2 = []
        c3 = []
        npix = hp.nside2npix(NSIDE)
        # 預抽 C1: 每次 88 點 (|b|>20)
        # 用 rejection 直接抽 (l, b)
        lat_ok = np.sin(np.radians(20))
        def rand_highlat(n):
            """|b|>20 均勻: rejection, 66% accept, 補滿"""
            out = np.empty(n)
            filled = 0
            while filled < n:
                v = RNG.uniform(-1, 1, n)
                keep = np.abs(v) > lat_ok
                k = keep.sum()
                take = min(k, n - filled)
                out[filled:filled+take] = v[keep][:take]
                filled += take
            return out
        for _ in range(NREAL):
            # C1: |b|>20 隨機
            b1 = np.degrees(np.arcsin(rand_highlat(88))); l1 = RNG.uniform(0, 360, 88)
            T1 = hp.get_interp_val(ms, np.radians(90-b1), np.radians(l1)) * 1e6
            c1.append(m1_of(T1))
            # C2: 經度置換 (固定 G88 緯度)
            l2 = RNG.permutation(lb88[:, 0])   # 打亂經度
            T2 = hp.get_interp_val(ms, np.radians(90-lb88[:, 1]), np.radians(l2)) * 1e6
            c2.append(m1_of(T2))
            # C3: 全天空均勻 88 點
            v3 = RNG.uniform(-1, 1, 88)
            b3 = np.degrees(np.arcsin(v3)); l3 = RNG.uniform(0, 360, 88)
            T3 = hp.get_interp_val(ms, np.radians(90-b3), np.radians(l3)) * 1e6
            c3.append(m1_of(T3))
        c1, c2, c3 = np.array(c1), np.array(c2), np.array(c3)
        # G88 實測
        T88 = hp.get_interp_val(ms, np.radians(90-lb88[:,1]), np.radians(lb88[:,0])) * 1e6
        m88 = m1_of(T88)
        T_A5 = hp.get_interp_val(ms, np.radians(90-lbA5[:,1]), np.radians(lbA5[:,0])) * 1e6
        mA5 = m1_of(T_A5)
        print(f"\n  {name:10s} ({fwhm}°):")
        print(f"    G88 實測       = {m88:.5f}  (dev vs 11/45 {(m88/T11-1)*100:+.1f}%)")
        print(f"    A5 實測       = {mA5:.5f}  (dev vs 11/45 {(mA5/T11-1)*100:+.1f}%)")
        print(f"    C1 隨機|b|>20 = {c1.mean():.5f} ± {c1.std():.5f}   z(G88)={(m88-c1.mean())/c1.std():+.2f}σ")
        print(f"    C2 經度置換   = {c2.mean():.5f} ± {c2.std():.5f}   z(G88)={(m88-c2.mean())/c2.std():+.2f}σ")
        print(f"    C3 全天空隨機 = {c3.mean():.5f} ± {c3.std():.5f}   z(G88)={(m88-c3.mean())/c3.std():+.2f}σ")
        print(f"    G88 vs C2 (緯度控制後): Δ = {(m88-c2.mean())*1000:.2f}×10⁻³  "
              f"= {(m88-c2.mean())/c2.std():+.2f}σ")

print("\nRESULT: 控制實驗完成")
