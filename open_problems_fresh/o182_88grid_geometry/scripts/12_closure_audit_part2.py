#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O182 scripts/12 — 閉合審計 part 2: 控制實驗獨立重跑
====================================================
新 RNG seed (20260913) + N=500, 重跑 C1(隨機|b|>20)/C2(經度置換)/C3(全天空)
對照 docs/04 §2 表 + z 值 + A5 z=0.14σ。
"""
import numpy as np, healpy as hp, json, time
from pathlib import Path
from astropy.coordinates import SkyCoord
import astropy.units as u

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
OUT = ROOT / "o182_88grid_geometry/data"
A = 134.2
t0 = time.time()

def to_gal(ra, dec):
    sc = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame='icrs')
    g = sc.galactic
    return g.l.deg, g.b.deg   # .value 已係度, 唔好 np.degrees 再轉 (double-conversion bug)

# 載入 88 格: g88_nodes.txt = RA/Dec ICRS -> 銀河 (l,b) (地圖係銀河座標!)
pts88 = np.loadtxt(OUT / "g88_nodes.txt")
l88, b88 = to_gal(pts88[:, 0], pts88[:, 1])
g88_vec = np.column_stack([np.cos(np.radians(b88))*np.cos(np.radians(l88)),
                           np.cos(np.radians(b88))*np.sin(np.radians(l88)),
                           np.sin(np.radians(b88))])

ok = 0; tot = 0
def chk(name, cond, detail=""):
    global ok, tot
    tot += 1
    if cond: ok += 1
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")

def sample_m1(map_, pts_vec, fwhm):
    npix = hp.nside2npix(2048)
    sm = hp.smoothing(map_.copy(), fwhm=np.radians(fwhm))
    vx = hp.vec2pix(2048, pts_vec[:, 0], pts_vec[:, 1], pts_vec[:, 2])
    T = sm[vx]
    return T

MAPS = {}
MAPS["SMICA"] = hp.read_map(str(ROOT / "o175_entropy_theorem/data/planck/COM_CMB_IQU-smica_2048_R3.00_full.fits"), field=0).astype(np.float64)
MAPS["Commander"] = hp.read_map(str(ROOT / "data_gated_unlock/COM_CMB_IQU-commander_2048_R3.00_full.fits"), field=0).astype(np.float64)
MAPS["SEVEM"] = hp.read_map(str(ROOT / "o42_independent_measurement_A/data/bands/sevem_final.fits"), field=0).astype(np.float64)

def control_matrix(map_, pts_vec, fwhm, nreal, seed):
    rng = np.random.default_rng(seed)
    npix = hp.nside2npix(2048)
    sm = hp.remove_dipole(hp.smoothing(map_.copy(), fwhm=np.radians(fwhm)), verbose=False) * 1e6
    T0 = sm[hp.vec2pix(2048, pts_vec[:, 0], pts_vec[:, 1], pts_vec[:, 2])]
    # C1: 隨機 88 點 |b|>20 (逐點 rejection, 冇無限循環)
    n = len(pts_vec)
    def m1(T): return np.mean(np.abs(T - T.mean())) / A
    def draw_random(npts, seed):
        r = np.random.default_rng(seed)
        th = np.arccos(r.uniform(-1, 1, npts)); ph = r.uniform(0, 2*np.pi, npts)
        # ICRS -> 銀河 vector (地圖係銀河座標)
        l_, b_ = to_gal(np.degrees(ph), np.degrees(np.pi/2 - th))
        vec = np.column_stack([np.cos(np.radians(b_))*np.cos(np.radians(l_)),
                               np.cos(np.radians(b_))*np.sin(np.radians(l_)),
                               np.sin(np.radians(b_))])
        bad = np.abs(b_) <= 20
        while bad.any():
            th2 = np.arccos(r.uniform(-1, 1, bad.sum())); ph2 = r.uniform(0, 2*np.pi, bad.sum())
            l2, b2 = to_gal(np.degrees(ph2), np.degrees(np.pi/2 - th2))
            vec[bad] = np.column_stack([np.cos(np.radians(b2))*np.cos(np.radians(l2)),
                                        np.cos(np.radians(b2))*np.sin(np.radians(l2)),
                                        np.sin(np.radians(b2))])
            bad[bad] = np.abs(b2) <= 20
        return vec
    c1 = []
    for i in range(nreal):
        v = draw_random(n, seed + i)
        T = sm[hp.vec2pix(2048, v[:, 0], v[:, 1], v[:, 2])]
        c1.append(m1(T))
    # C2: 經度置換 (同緯度, 88 格嘅 b 保留, l 隨機平移)
    c2 = []
    for i in range(nreal):
        dl = rng.uniform(0, 360)
        l2 = (l88 + dl) % 360
        vec = np.column_stack([np.cos(np.radians(b88))*np.cos(np.radians(l2)),
                               np.cos(np.radians(b88))*np.sin(np.radians(l2)),
                               np.sin(np.radians(b88))])
        T = sm[hp.vec2pix(2048, vec[:, 0], vec[:, 1], vec[:, 2])]
        c2.append(m1(T))
    # C3: 全天空隨機
    c3 = []
    for i in range(nreal):
        th = np.arccos(rng.uniform(-1, 1, n)); ph = rng.uniform(0, 2*np.pi, n)
        l3, b3 = to_gal(np.degrees(ph), np.degrees(np.pi/2 - th))
        vec = np.column_stack([np.cos(np.radians(b3))*np.cos(np.radians(l3)),
                               np.cos(np.radians(b3))*np.sin(np.radians(l3)),
                               np.sin(np.radians(b3))])
        T = sm[hp.vec2pix(2048, vec[:, 0], vec[:, 1], vec[:, 2])]
        c3.append(m1(T))
    return T0, np.array(c1), np.array(c2), np.array(c3)

# docs/04 表 (4.17°): C1 0.2416/0.2402/0.2382 ±0.019; C2 0.2542/0.2562/0.2636 ±0.020/0.021/0.022
#                   C3 0.2587/0.2619/0.2672 ±0.022/0.022/0.025; G88 z vs C2 +2.17/+1.77/+1.08
doc_c1 = {"SMICA": (0.2416, 0.019), "Commander": (0.2402, 0.019), "SEVEM": (0.2382, 0.019)}
doc_c2 = {"SMICA": (0.2542, 0.020), "Commander": (0.2562, 0.021), "SEVEM": (0.2636, 0.022)}
doc_c3 = {"SMICA": (0.2587, 0.022), "Commander": (0.2619, 0.022), "SEVEM": (0.2672, 0.025)}
doc_z  = {"SMICA": 2.17, "Commander": 1.77, "SEVEM": 1.08}

for name in MAPS:
    T88, c1, c2, c3 = control_matrix(MAPS[name], g88_vec, 4.17, 500, 20260913)
    m1_88 = np.mean(np.abs(T88 - T88.mean())) / A
    print(f"--- {name} @4.17° (N=500, seed 20260913) ---")
    for label, c, doc in [("C1", c1, doc_c1[name]), ("C2", c2, doc_c2[name]), ("C3", c3, doc_c3[name])]:
        mn, sd = c.mean(), c.std()
        chk(f"C-{label} mean {doc[0]:.4f}", abs(mn - doc[0]) < 0.004, f"(重跑 {mn:.4f}±{sd:.3f})")
        chk(f"C-{label} std {doc[1]:.3f}", abs(sd - doc[1]) < 0.004, f"({sd:.3f})")
    z = (m1_88 - c2.mean()) / c2.std()
    chk(f"C-z vs C2 {doc_z[name]:.2f}σ", abs(z - doc_z[name]) < 0.35, f"(重跑 z={z:+.2f}σ, G88={m1_88:.5f})")
    # A5 z=0.14σ (SMICA)
    if name == "SMICA":
        a5 = json.loads((OUT/"temps2_SMICA_4.17deg.json").read_text())["A5_60"]
        m1_a5 = np.mean(np.abs(np.array(a5) - np.mean(a5))) / A
        z_a5 = (m1_a5 - c1.mean()) / c1.std()
        chk("A5 z vs C1 = +0.14σ", abs(z_a5 - 0.14) < 0.15, f"(z={z_a5:+.2f}σ)")

print(f"\nRESULT_AUDIT_PART2: {ok}/{tot} PASS ({time.time()-t0:.0f}s)")
exit(0 if ok == tot else 1)
