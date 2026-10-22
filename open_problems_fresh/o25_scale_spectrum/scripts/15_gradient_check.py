#!/usr/bin/env python3
"""
15_gradient_check.py — O25: 熱環真身檢驗 — compensated void vs 大尺度梯度
=========================================================================
發現: 熱環峰喺 41-45°+ 而且單調上升 — 唔似環,似梯度。

檢驗:
1. 延伸徑向掃描到 90°: 溫度會唔會回落? (compensated void: 會) (梯度: 唔會)
2. 全天空對照: 冷區方向 vs 反方向 (dipole 檢驗)
3. 大尺度模式分解: 冷區中心係咪喺某個低階模式 (dipole/quadrupole) 節點?
4. IDCM τ 分析: 冷區中心衰減 τ (用多尺度)
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
cold_center = {"l": 197.74, "b": -20.26}

m = hp.read_map(os.path.join(CACHE, "Commander_smooth15.0.fits"), field=0)
m_low = hp.ud_grade(m, 512)
nside_low = 512

print("=" * 70)
print("熱環真身檢驗: compensated void vs 大尺度梯度")
print("=" * 70)

# ============ 1. 延伸徑向掃描到 90° ============
print("\n[1] 延伸徑向掃描 (0-90°, 每 5°, 冷區中心)")
def ring_profile(l_deg, b_deg, r0, r1):
    vec = hp.ang2vec(l_deg, b_deg, lonlat=True)
    d_out = hp.query_disc(nside_low, vec, np.radians(r1))
    if r0 == 0:
        return d_out, m_low[d_out].mean()*1e6
    d_in = hp.query_disc(nside_low, vec, np.radians(r0))
    ring = np.setdiff1d(d_out, d_in)
    return ring, m_low[ring].mean()*1e6

vec_cc = hp.ang2vec(cold_center["l"], cold_center["b"], lonlat=True)
temps = []
for r0 in range(0, 90, 5):
    ring, t = ring_profile(cold_center["l"], cold_center["b"], r0, r0+5)
    temps.append((r0+2.5, t))
    bar = "█" * max(0, int((t + 20) / 2))
    print(f"    {r0+2.5:>5.1f}°: {t:>+7.2f} μK {bar}")

# 係咪回落?
t_max_idx = np.argmax([t for _, t in temps])
t_end = temps[-1][1]
print(f"\n    最高溫: {temps[t_max_idx][1]:+.2f} μK @ {temps[t_max_idx][0]:.1f}°")
print(f"    90° 環: {t_end:+.2f} μK")
print(f"    {'回落 (compensated void)' if t_end < temps[t_max_idx][1] - 3 else '持續上升 (梯度)'}")

# ============ 2. 全天空 dipole 檢驗 ============
print("\n[2] 全天空大尺度模式 (Commander 15° 平滑)")
# 計算 dipole/quadrupole
alm = hp.map2alm(m_low, lmax=3)
T0 = alm[0] / np.sqrt(4*np.pi) * np.sqrt(4*np.pi)  # 直接
# dipole 振幅
a10, a11 = alm[1], alm[2]
dip_amp = np.sqrt(abs(a10)**2 + abs(a11)**2 + abs(alm[3])**2)  # 唔啱, 要計埋 a1-1
print(f"    l=1: a10={a10:.2f}, a11={a11:.2f}")
# 完整 dipole
dipole_map = hp.alm2map(np.array([0, a10, a11, 0, 0, 0, 0, 0, 0, 0], dtype=complex), nside_low, lmax=3)
# 喺冷區中心方向嘅 dipole 值
pix_cc = hp.ang2pix(nside_low, cold_center["l"], cold_center["b"], lonlat=True)
pix_anti = hp.ang2pix(nside_low, (cold_center["l"]+180) % 360, -cold_center["b"], lonlat=True)
print(f"    dipole @ 冷區中心: {dipole_map[pix_cc]*1e6:+.2f} μK")
print(f"    dipole @ 反方向:   {dipole_map[pix_anti]*1e6:+.2f} μK")

# 冷區中心減去 dipole/quadrupole 之後仲冷唔冷?
mono = m_low.mean()
resid = m_low - dipole_map - mono
print(f"    冷區中心 20° 盤 (減 dipole+mono): {resid[hp.query_disc(nside_low, vec_cc, np.radians(20.0))].mean()*1e6:+.2f} μK")

# ============ 3. 大尺度模式貢獻 ============
print("\n[3] 低階模式喺冷區中心嘅貢獻")
for l in [1, 2, 3]:
    alm_l = np.zeros(10, dtype=complex)
    for m in range(-l, l+1):
        idx = hp.Alm.getidx(3, l, abs(m))
        alm_l[idx] = alm[idx]
    mod_map = hp.alm2map(alm_l, nside_low, lmax=3)
    val_cc = mod_map[pix_cc] * 1e6
    val_anti = mod_map[pix_anti] * 1e6
    print(f"    l={l}: 冷區中心={val_cc:+.2f}, 反方向={val_anti:+.2f} μK")

# ============ 4. IDCM τ 分析 (冷區中心多尺度) ============
print("\n[4] 冷區中心衰減 τ (用全部 15° 平滑 cache 尺度)")
# 我哋有 12/15/20° 大尺度 + 原有 10 尺度
scales_avail = [12.0, 15.0, 20.0]
T_cc = []
for s in scales_avail:
    for mname in ["NILC", "Commander"]:
        fname = os.path.join(CACHE, f"{mname}_smooth{s}.fits")
        if os.path.exists(fname):
            mm = hp.read_map(fname, field=0)
            mm_low = hp.ud_grade(mm, 512)
            d = hp.query_disc(512, vec_cc, np.radians(20.0))
            T_cc.append((s, mname, mm_low[d].mean()*1e6))
for s, mname, t in T_cc:
    print(f"    {mname} {s}°: 20°盤={t:+.2f} μK")

# 冷區中心 vs node9: 邊個更冷?
d9 = hp.query_disc(nside_low, hp.ang2vec(node9["l"], node9["b"], lonlat=True), np.radians(20.0))
dcc = hp.query_disc(nside_low, vec_cc, np.radians(20.0))
print(f"\n    node9 20°盤: {m_low[d9].mean()*1e6:+.2f} μK")
print(f"    冷區中心 20°盤: {m_low[dcc].mean()*1e6:+.2f} μK")
print(f"    → 冷區中心比 node9 冷 {abs(m_low[dcc].mean()-m_low[d9].mean())*1e6:.1f} μK")

out = {
    "radial_90": [[float(r), float(t)] for r, t in temps],
    "dipole": {"cc": float(dipole_map[pix_cc]*1e6), "anti": float(dipole_map[pix_anti]*1e6)},
    "resid_cc_20deg": float(resid[hp.query_disc(nside_low, vec_cc, np.radians(20.0))].mean()*1e6),
    "cc_vs_node9_20deg": {"node9": float(m_low[d9].mean()*1e6), "coldcenter": float(m_low[dcc].mean()*1e6)},
}
with open(os.path.join(DATA, "gradient_check.json"), "w") as f:
    json.dump(out, f, indent=2)
print("\n✅ saved data/gradient_check.json")
