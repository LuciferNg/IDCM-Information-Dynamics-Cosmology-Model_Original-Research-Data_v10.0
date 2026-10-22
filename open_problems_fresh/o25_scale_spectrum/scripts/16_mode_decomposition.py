#!/usr/bin/env python3
"""
16_mode_decomposition.py — O25: 冷區中心模式分解
=================================================
發現: 冷區中心嘅大尺度冷結構主導模式係 octupole (l=3)!

檢驗:
1. 全模式分解 l=1-10: 每個 l 喺冷區中心/反方向嘅貢獻
2. 對照: 冷斑方向 vs node9 vs 隨機方向嘅模式貢獻
3. 冷區中心減 l=3 之後仲冷唔冷? (殘餘分析)
4. l=3 結構 vs IDCM (K_tree 33 尺度?)
"""
import healpy as hp
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u
import os, json

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
CACHE = os.path.join(BASE, "o25_scale_spectrum", "data", "smooth_cache_large")
DATA = os.path.join(BASE, "o25_scale_spectrum", "data")

node9 = {"l": 214.92, "b": -31.16}
node0 = {"l": 209.00, "b": -57.00}
cold_center = {"l": 197.74, "b": -20.26}

m = hp.read_map(os.path.join(CACHE, "Commander_smooth15.0.fits"), field=0)
m_low = hp.ud_grade(m, 512)
nside_low = 512

print("=" * 70)
print("冷區中心模式分解 (l=1-10)")
print("=" * 70)

# ============ 1. 全模式分解 ============
print("\n[1] 每個 l 喺冷區中心/反方向嘅貢獻")
lmax = 10
alm = hp.map2alm(m_low, lmax=lmax)

def mode_contrib(l, pix, alm, lmax, nside):
    n_alm = hp.Alm.getsize(lmax)
    alm_l = np.zeros(n_alm, dtype=complex)
    for mm in range(-l, l+1):
        idx = hp.Alm.getidx(lmax, l, abs(mm))
        alm_l[idx] = alm[idx]
    mod_map = hp.alm2map(alm_l, nside, lmax=lmax)
    return mod_map[pix] * 1e6

def mode_contrib_full(l, alm, lmax, nside):
    n_alm = hp.Alm.getsize(lmax)
    alm_l = np.zeros(n_alm, dtype=complex)
    for mm in range(-l, l+1):
        idx = hp.Alm.getidx(lmax, l, abs(mm))
        alm_l[idx] = alm[idx]
    return hp.alm2map(alm_l, nside, lmax=lmax)

pix_cc = hp.ang2pix(nside_low, cold_center["l"], cold_center["b"], lonlat=True)
pix_anti = hp.ang2pix(nside_low, (cold_center["l"]+180) % 360, -cold_center["b"], lonlat=True)
pix_n9 = hp.ang2pix(nside_low, node9["l"], node9["b"], lonlat=True)
pix_n0 = hp.ang2pix(nside_low, node0["l"], node0["b"], lonlat=True)

print(f"    {'l':>3} | {'冷區中心':>10} | {'反方向':>10} | {'node9':>10} | {'冷斑':>10} | {'對稱?':>6}")
for l in range(1, 11):
    v_cc = mode_contrib(l, pix_cc, alm, lmax, nside_low)
    v_anti = mode_contrib(l, pix_anti, alm, lmax, nside_low)
    v_n9 = mode_contrib(l, pix_n9, alm, lmax, nside_low)
    v_n0 = mode_contrib(l, pix_n0, alm, lmax, nside_low)
    sym = "偶" if abs(v_cc - v_anti) < 1 else ("奇" if abs(v_cc + v_anti) < 1 else "—")
    print(f"    {l:3d} | {v_cc:+10.2f} | {v_anti:+10.2f} | {v_n9:+10.2f} | {v_n0:+10.2f} | {sym:>6}")

# ============ 2. 殘餘分析 ============
print("\n[2] 逐級減模式: 冷區中心 20° 盤剩餘")
vec_cc = hp.ang2vec(cold_center["l"], cold_center["b"], lonlat=True)
d20 = hp.query_disc(nside_low, vec_cc, np.radians(20.0))
n_alm = hp.Alm.getsize(lmax)
mono = m_low.mean()
resid = m_low - mono
print(f"    原始 20° 盤: {m_low[d20].mean()*1e6:+.2f} μK")
print(f"    減 mono:     {resid[d20].mean()*1e6:+.2f} μK")
for lmax_cut in [1, 2, 3, 4, 5, 6, 8]:
    alm_cut = np.zeros(n_alm, dtype=complex)
    for l in range(1, lmax_cut+1):
        for mm in range(-l, l+1):
            idx = hp.Alm.getidx(lmax, l, abs(mm))
            alm_cut[idx] = alm[idx]
    low_modes = hp.alm2map(alm_cut, nside_low, lmax=lmax)
    resid = m_low - mono - low_modes
    print(f"    減 l≤{lmax_cut}: {resid[d20].mean()*1e6:+.2f} μK")

# ============ 3. 隨機方向對照 ============
print("\n[3] 隨機方向 l=3 貢獻對照")
rng = np.random.default_rng(7)
l3_vals = []
for _ in range(500):
    rv = rng.standard_normal(3)
    rv /= np.linalg.norm(rv)
    pix = hp.vec2pix(nside_low, *rv)
    l3_vals.append(mode_contrib(3, pix, alm, lmax, nside_low))
l3_vals = np.array(l3_vals)
print(f"    隨機 500 方向 l=3 貢獻: {l3_vals.mean():+.2f} ± {l3_vals.std():.2f} μK")
print(f"    冷區中心 l=3 ({mode_contrib(3, pix_cc, alm, lmax, nside_low):+.2f}) z = {(mode_contrib(3, pix_cc, alm, lmax, nside_low)-l3_vals.mean())/l3_vals.std():+.2f}σ")

# ============ 4. 冷區中心減 l=3 後仲冷唔冷 ============
print("\n[4] 冷區中心 20° 盤: 全模式 vs 減 l=3")
alm_all = np.zeros(n_alm, dtype=complex)
for l in range(1, lmax+1):
    for mm in range(-l, l+1):
        idx = hp.Alm.getidx(lmax, l, abs(mm))
        alm_all[idx] = alm[idx]
full_modes = hp.alm2map(alm_all, nside_low, lmax=lmax)
resid_no3 = m_low - mono - full_modes + mode_contrib_full(3, alm, lmax, nside_low)
print(f"    減全部模式再+返 l=3 (即係只有 l=3): {resid_no3[d20].mean()*1e6:+.2f} μK")

# 只有 l=3
only3 = mode_contrib_full(3, alm, lmax, nside_low)
print(f"    只有 l=3 模式喺 20° 盤: {only3[d20].mean()*1e6:+.2f} μK")
print(f"    減 l=3 之後殘餘: {(m_low-mono-only3)[d20].mean()*1e6:+.2f} μK")
print(f"    → l=3 佔冷區中心嘅 {(abs(only3[d20].mean()/max(m_low[d20].mean()-mono, 1e-9)))*100:.0f}%")

# 儲存
out = {
    "cold_center": cold_center,
    "mode_contrib": {str(l): {"cc": float(mode_contrib(l, pix_cc, alm, lmax, nside_low)),
                               "anti": float(mode_contrib(l, pix_anti, alm, lmax, nside_low)),
                               "node9": float(mode_contrib(l, pix_n9, alm, lmax, nside_low)),
                               "node0": float(mode_contrib(l, pix_n0, alm, lmax, nside_low))} for l in range(1, 11)},
    "only_l3_20deg": float(only3[d20].mean()*1e6),
    "resid_no_l3_20deg": float((m_low-mono-only3)[d20].mean()*1e6),
    "random_l3": {"mean": float(l3_vals.mean()), "std": float(l3_vals.std()), "z_cc": float((mode_contrib(3, pix_cc, alm, lmax, nside_low)-l3_vals.mean())/l3_vals.std())},
}
with open(os.path.join(DATA, "mode_decomposition.json"), "w") as f:
    json.dump(out, f, indent=2)
print("\n✅ saved data/mode_decomposition.json")
