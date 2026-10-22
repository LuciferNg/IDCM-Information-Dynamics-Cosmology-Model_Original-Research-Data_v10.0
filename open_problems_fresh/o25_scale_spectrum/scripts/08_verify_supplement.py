#!/usr/bin/env python3
"""
08_verify_supplement.py — O25 一次過: 補充報告驗證
===================================================
讀返 scale_spectrum_large.json + tau_refine.json,
獨立重算延伸數據聲稱, 對比 03_supplement_large_scale.md 數字。
"""
import healpy as hp
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u
from scipy import stats
import os, json, sys

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
CACHE = os.path.join(BASE, "o25_scale_spectrum", "data", "smooth_cache_large")
DATA = os.path.join(BASE, "o25_scale_spectrum", "data")

nodes = []
with open(os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")) as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic
l_deg = np.array(gal.l.deg)
b_deg = np.array(gal.b.deg)

color = {}
with open(os.path.join(BASE, "cmb_cold_spot/data/anchored_coloring.txt")) as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        parts = line.split()
        color[int(parts[0])] = int(parts[3])
color_arr = np.array([color[i] for i in range(60)])
ZERO_E = [10, 12, 19, 22, 23, 25, 28, 32, 37, 40, 45, 46]
zero_mask = np.zeros(60, dtype=bool)
zero_mask[ZERO_E] = True

with open(os.path.join(DATA, "scale_spectrum_large.json")) as f:
    RL = json.load(f)

passes, fails = 0, 0
fail_msgs = []

def check(name, claimed, recomputed, tol):
    global passes, fails
    if abs(claimed - recomputed) <= tol:
        passes += 1
    else:
        fails += 1
        fail_msgs.append(f"{name}: claimed={claimed} recomputed={recomputed:.6f} tol={tol}")

# ============ 1. 延伸尺度冷熱差 + node9/node0 ============
print("驗證 1: 延伸尺度 (NILC/Commander × 7 尺度)")
for mname in ["NILC", "Commander"]:
    for s in [0.3, 0.75, 6.0, 8.0, 12.0, 15.0, 20.0]:
        m = hp.read_map(os.path.join(CACHE, f"{mname}_smooth{s}.fits"), field=0)
        nside = hp.get_nside(m)
        pix = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)
        T = m[pix] * 1e6
        r = RL[mname][str(s)]
        d = T[color_arr==1].mean() - T[color_arr==0].mean()
        check(f"{mname}@{s}° diff", r["cold_hot_diff"], d, 0.1)
        check(f"{mname}@{s}° node0", r["node0"], T[0], 0.1)
        check(f"{mname}@{s}° node9", r["node9"], T[9], 0.1)
        # ΔE0
        zr = np.abs(T[zero_mask]).mean() / np.abs(T[~zero_mask]).mean()
        check(f"{mname}@{s}° zeroE", r["zeroE_ratio"], zr, 0.005)
        del m

# ============ 2. τ 擬合重跑 ============
print("驗證 2: τ 擬合 (SMICA 10 尺度)")
SCALES10 = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 4.17, 5.0, 7.0, 10.0]
with open(os.path.join(DATA, "scale_spectrum.json")) as f:
    R10 = json.load(f)
x10 = np.array(SCALES10)
d10 = np.array([abs(R10['SMICA'][str(s)]['cold_hot_diff_uK']) for s in SCALES10])

def exp5(x, a1, t1, a2, t2, c):
    return a1*np.exp(-x/t1) + a2*np.exp(-x/t2) + c
from scipy.optimize import curve_fit
popt, _ = curve_fit(exp5, x10, d10, p0=(25, 1.5, 15, 8, 10), maxfev=40000)
tr = json.load(open(os.path.join(DATA, "tau_refine.json")))
claimed_free = tr["smica_10"]["free"]["params"]
for i, (cp, rp) in enumerate(zip(claimed_free, popt)):
    check(f"free param[{i}]", cp, rp, abs(rp)*0.05 + 0.01)

# 固定 2/3
def exp5f(x, a1, a2, t2, c):
    return a1*np.exp(-x/(2/3)) + a2*np.exp(-x/t2) + c
poptf, _ = curve_fit(exp5f, x10, d10, p0=(25, 15, 8, 10), maxfev=40000)
claimed_fixed = tr["smica_10"]["fixed_t1_2_3"]["params"]
for i, (cp, rp) in enumerate(zip(claimed_fixed, poptf)):
    check(f"fixed param[{i}]", cp, rp, abs(rp)*0.05 + 0.01)

# t1 vs 2/3
check("t1=2/3", tr["smica_10"]["free"]["params"][1], 2/3, 0.1)

# ============ 3. node9 區域檢驗 ============
print("驗證 3: node9 區域 (Commander)")
rng = np.random.default_rng(7)
for s in [10.0, 15.0, 20.0]:
    m = hp.read_map(os.path.join(CACHE, f"Commander_smooth{s}.fits"), field=0)
    nside = hp.get_nside(m)
    pix9 = hp.ang2pix(nside, l_deg[9], b_deg[9], lonlat=True)
    vec9 = hp.pix2vec(nside, pix9)
    radius = np.radians(s)
    d9 = hp.query_disc(nside, vec9, radius)
    m9 = m[d9].mean() * 1e6
    rands = []
    for _ in range(100):
        rv = rng.standard_normal(3)
        rv /= np.linalg.norm(rv)
        rd = hp.query_disc(nside, rv, radius)
        rands.append(m[rd].mean() * 1e6)
    rands = np.array(rands)
    z9 = (m9 - rands.mean()) / rands.std()
    # 對比補充報告: 10°=-2.56, 15°=-2.32, 20°=-1.89
    claimed_z = {10.0: -2.56, 15.0: -2.32, 20.0: -1.89}[s]
    check(f"node9 region z@{s}°", claimed_z, z9, 0.15)
    del m

print(f"\n{'='*60}")
print(f"驗證結果: {passes} PASS, {fails} FAIL")
if fails:
    for msg in fail_msgs:
        print(f"  ❌ {msg}")
    sys.exit(1)
else:
    print("🎉 全部驗證通過 — 無幻覺")
