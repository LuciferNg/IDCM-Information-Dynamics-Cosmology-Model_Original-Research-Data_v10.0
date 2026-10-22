#!/usr/bin/env python3
"""
17_audit_independent.py — O30 獨立核對審計 (2026-09-11)
======================================================
O30 5-task audit round 的 T1: 獨立重算 — 唔 import 任何原 scripts、
唔讀任何原 data/*.txt|*.json 作為計算輸入 (文檔完整性 section K 除外,
嗰度先係驗證 data 檔 ↔ docs 一致性)。

方法: 從第一原理 (a5_nodes ICRS→Galactic + smooth_cache maps + o27 HFI
maps) 重算所有 headline 數值, 對比 01_problem_record.md / NN_results.md /
DISCRETENESS_COMPLETE.md / NODE53_REPORT.md / NODE33_REPORT.md 宣稱。

Sections:
  A. 60 節點 mean vs 隨機 (iso + same_lat, 1000 組, seed 20260817)
  B. 高緯 31 節點 mean
  C. 剔除 node0+node9 mean
  D. mean|T| 幅度檢驗 (iso + same_lat + drop)
  E. 冷/熱 count + 冷熱 mean|T| 比 + ΔE=0 12 節點 + O24 冷色 8/10
  F. 堆疊 radial 中心 bin (60 節點 0-0.5° 獨立重算) + data 檔 χ² 重算
  G. 離散性: 每節點跨尺度 zbar (10 尺度 nside512) → 5 節點 + max
  H. node53 三地圖 3°盤 + 環 ΔT (SMICA/NILC/Commander 4.17° cache)
  I. node53 多頻譜 dT (HFI 100/143/217/353, 3.0° FWHM) + 353 dust + 對徑 + mask
  J. node33 三地圖 + 多頻譜 dT + 353 dust + mask
  K. 文檔完整性: data 檔宣稱值 ↔ 5 份 docs 交叉引用 (只讀, 唔改)

MC 注意 (O157 教訓): 控制組統計係 seed 依賴 — 相同 seed 20260817 重跑,
若 numpy 版本差異導致小偏差, 用容差 + 註明。p 值只報觀察統計, MC p 註明
「原 script seed 依賴, audit 重跑同 seed」。
"""
import healpy as hp
import numpy as np
import os, json, re
from astropy.coordinates import SkyCoord
import astropy.units as u
from scipy import stats

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
CACHE = os.path.join(BASE, "o5_catalog_compare/data/smooth_cache")
DATA27 = os.path.join(BASE, "o27_node47_foreground/data")
NODES = os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")
COLOR = os.path.join(BASE, "cmb_cold_spot/data/anchored_coloring.txt")
O30 = os.path.join(BASE, "o30_node_systematics")

RNG = np.random.default_rng(20260817)
N_CTRL = 1000
PASS, FAIL = [], []

def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'✅' if cond else '❌'} {name} {detail}")

def z_of(mu, ctrl):
    return (mu - ctrl.mean()) / ctrl.std(ddof=1)

print("=" * 72)
print("O30-17: 獨立核對審計 (2026-09-11, 真樹路徑, 無原 script import)")
print("=" * 72)

# ---------- 載入 4.17° SMICA + 節點 (一次) ----------
m417 = hp.read_map(os.path.join(CACHE, "smica2_smooth4.17.fits"), field=0)
nside = hp.get_nside(m417)
npix = hp.nside2npix(nside)
nodes = np.loadtxt(NODES)
sc = SkyCoord(ra=nodes[:, 0] * u.deg, dec=nodes[:, 1] * u.deg, frame='icrs')
gal = sc.galactic
l_deg, b_deg = gal.l.deg, gal.b.deg
pix = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)
T = m417[pix] * 1e6
hi_mask = np.abs(b_deg) >= 30
n_hi = int(hi_mask.sum())
keep = np.array([i for i in range(60) if i not in (0, 9)])
print(f"\n4.17° SMICA: NSIDE={nside}, map std={m417.std()*1e6:.2f} μK, 高緯節點={n_hi}")

# ============ A. 60 節點 mean vs 隨機 ============
print("\n--- A. 60 節點 mean vs 隨機 (1000 組, seed 20260817) ---")
ctrl_iso = np.empty(N_CTRL)
ctrl_lat = np.empty(N_CTRL)
for k in range(N_CTRL):
    rpix = RNG.integers(0, npix, size=60)
    ctrl_iso[k] = m417[rpix].mean() * 1e6
    rl = RNG.uniform(0, 360, size=60)
    rpix_l = hp.ang2pix(nside, rl, b_deg, lonlat=True)
    ctrl_lat[k] = m417[rpix_l].mean() * 1e6
mu_all = T.mean()
z_iso = z_of(mu_all, ctrl_iso)
z_lat = z_of(mu_all, ctrl_lat)
check("A1 60節點 mean=-1.25", abs(mu_all + 1.25) < 0.05, f"({mu_all:+.3f})")
check("A2 z_iso=-0.21", abs(z_iso + 0.207) < 0.1, f"({z_iso:+.3f})")
check("A3 z_lat=-0.22", abs(z_lat + 0.223) < 0.1, f"({z_lat:+.3f})")
# A4: 控制組 mean ≈ 0 (mean-of-60 分佈 mean 嘅 1σ ≈ 5.79/√1000 ≈ 0.18 μK)
# 原 01 script (2026-08-21, numpy 2.4.6): mean=-0.05; audit 重跑 (numpy 版本可能
# 差異 → RNG 序列漂移): mean=-0.15 — 兩者都喺 ±0.3 內, 係同一分佈嘅合理實現。
check("A4 隨機 mean≈0.00±5.8", abs(ctrl_iso.mean()) < 0.35 and abs(ctrl_iso.std(ddof=1) - 5.79) < 0.3,
      f"(ctrl {ctrl_iso.mean():+.2f}±{ctrl_iso.std(ddof=1):.2f})")

# ============ B. 高緯 31 ============
print("\n--- B. 高緯 31 節點 mean ---")
Th = T[hi_mask]
ctrl_hi_iso = np.empty(N_CTRL)
ctrl_hi_lat = np.empty(N_CTRL)
for k in range(N_CTRL):
    rpix = RNG.integers(0, npix, size=n_hi)
    ctrl_hi_iso[k] = m417[rpix].mean() * 1e6
    rl = RNG.uniform(0, 360, size=n_hi)
    ctrl_hi_lat[k] = m417[hp.ang2pix(nside, rl, b_deg[hi_mask], lonlat=True)].mean() * 1e6
z_hi_iso = z_of(Th.mean(), ctrl_hi_iso)
z_hi_lat = z_of(Th.mean(), ctrl_hi_lat)
check("B1 高緯 mean=-4.06", abs(Th.mean() + 4.06) < 0.1, f"({Th.mean():+.3f})")
check("B2 z_hi_iso=-0.47", abs(z_hi_iso + 0.468) < 0.15, f"({z_hi_iso:+.3f})")
check("B3 z_hi_lat=-0.68", abs(z_hi_lat + 0.677) < 0.2, f"({z_hi_lat:+.3f})")

# ============ C. 剔除 node0+node9 ============
print("\n--- C. 剔除 node0+node9 (58) ---")
Tk = T[keep]
ctrl_k_iso = np.empty(N_CTRL)
for k in range(N_CTRL):
    rpix = RNG.integers(0, npix, size=58)
    ctrl_k_iso[k] = m417[rpix].mean() * 1e6
z_k = z_of(Tk.mean(), ctrl_k_iso)
check("C1 剔除後 mean=+2.87", abs(Tk.mean() - 2.87) < 0.15, f"({Tk.mean():+.3f})")
check("C2 z=+0.52", abs(z_k - 0.52) < 0.15, f"({z_k:+.3f})")

# ============ D. mean|T| 幅度 ============
print("\n--- D. mean|T| 幅度檢驗 ---")
A = np.abs(T)
ctrl_abs = np.empty(N_CTRL)
for k in range(N_CTRL):
    rpix = RNG.integers(0, npix, size=60)
    ctrl_abs[k] = np.abs(m417[rpix]).mean() * 1e6
z_abs = z_of(A.mean(), ctrl_abs)
A_hi = A[hi_mask]
ctrl_abs_hi = np.empty(N_CTRL)
for k in range(N_CTRL):
    rpix = RNG.integers(0, npix, size=n_hi)
    ctrl_abs_hi[k] = np.abs(m417[rpix]).mean() * 1e6
z_abs_hi = z_of(A_hi.mean(), ctrl_abs_hi)
A_k = A[keep]
ctrl_abs_k = np.empty(N_CTRL)
for k in range(N_CTRL):
    rpix = RNG.integers(0, npix, size=58)
    ctrl_abs_k[k] = np.abs(m417[rpix]).mean() * 1e6
z_abs_k = z_of(A_k.mean(), ctrl_abs_k)
check("D1 mean|T|=32.75", abs(A.mean() - 32.75) < 0.05, f"({A.mean():.3f})")
check("D2 z=-0.65", abs(z_abs + 0.649) < 0.15, f"({z_abs:+.3f})")
check("D3 高緯 mean|T|=29.91", abs(A_hi.mean() - 29.91) < 0.1, f"({A_hi.mean():.3f})")
check("D4 高緯 z=-1.01", abs(z_abs_hi + 1.012) < 0.2, f"({z_abs_hi:+.3f})")
check("D5 剔除 mean|T|=29.72", abs(A_k.mean() - 29.72) < 0.1, f"({A_k.mean():.3f})")
check("D6 剔除 z=-1.45", abs(z_abs_k + 1.452) < 0.2, f"({z_abs_k:+.3f})")

# ============ E. 冷/熱 + ΔE=0 + O24 ============
print("\n--- E. 冷/熱 count + ΔE=0 + O24 冷色 ---")
n_cold = int((T < 0).sum())
A_cold, A_hot = np.abs(T[T < 0]), np.abs(T[T > 0])
ratio = A_cold.mean() / A_hot.mean()
zeroE = [10, 12, 19, 22, 23, 25, 28, 32, 37, 40, 45, 46]
dz = np.abs(T[zeroE]).mean()
check("E1 冷=29 熱=31", n_cold == 29, f"({n_cold}/{60-n_cold})")
check("E2 冷熱比 1.154", abs(ratio - 1.154) < 0.01, f"({ratio:.3f})")
check("E3 ΔE=0 mean|T|=19.05", abs(dz - 19.05) < 0.05, f"({dz:.3f})")
# O24: 最冷 10 冷色 8/10
color = {}
with open(COLOR) as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        parts = line.split()
        color[int(parts[0])] = int(parts[3])
color_arr = np.array([color[i] for i in range(60)])
order = np.argsort(T)
c_cold10 = int((color_arr[order[:10]] == 1).sum())
check("E4 最冷10 8/10 冷色", c_cold10 == 8, f"({c_cold10}/10)")

# ============ F. 堆疊 radial 中心 bin + χ² ============
print("\n--- F. 堆疊 radial 中心 bin (0-0.5°) + χ² 重算 ---")
vecs = hp.ang2vec(l_deg, b_deg, lonlat=True)
m128 = hp.ud_grade(m417, 128)
npix128 = hp.nside2npix(128)
center_vals = []
for v in vecs:
    sel = hp.query_disc(128, v, np.radians(0.5), inclusive=True)
    center_vals.append(m128[sel].mean() * 1e6)
center_mean = np.mean(center_vals)
# 隨機 1000 組中心 bin (每組 60 隨機中心, query_disc 0.5°)
ctrl_c = np.empty(N_CTRL)
for k in range(N_CTRL):
    rpix = RNG.integers(0, npix128, size=60)
    vals = []
    for rp in rpix:
        rv = hp.pix2vec(128, int(rp))
        sel = hp.query_disc(128, rv, np.radians(0.5), inclusive=True)
        vals.append(m128[sel].mean() * 1e6)
    ctrl_c[k] = np.mean(vals)
z_c = z_of(center_mean, ctrl_c)
check("F1 中心bin mean=-1.13", abs(center_mean + 1.13) < 0.15, f"({center_mean:+.3f})")
check("F2 中心bin z=-0.16", abs(z_c + 0.162) < 0.2, f"({z_c:+.3f})")
# χ² 由 data 檔 z 列重算 (讀檔只為核對, 唔係計算輸入)
d2 = np.loadtxt(os.path.join(O30, "data/02_stack_radial.txt"))
z_col = d2[:, 8]
chi2 = np.nansum(z_col ** 2)
p_chi2 = 1 - stats.chi2.cdf(chi2, 20)
check("F3 data χ²=0.37/20dof p=1.0", abs(chi2 - 0.369) < 0.05, f"(χ²={chi2:.3f}, p={p_chi2:.4f})")

# ============ G. 離散性: 跨尺度 zbar ============
print("\n--- G. 離散性: 跨尺度 zbar (10 尺度, nside512) ---")
SCALES = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 4.17, 5.0, 7.0, 10.0]
MAPS = {0.5: "smica2_smooth0.5.fits", 1.0: "smica2_smooth1.0.fits",
        1.5: "smica2_smooth1.5.fits", 2.0: "smica2_smooth2.0.fits",
        3.0: "smica2_smooth3.0.fits", 4.0: "smica2_smooth4.0.fits",
        4.17: "smica2_smooth4.17.fits", 5.0: "smica2_smooth5.0.fits",
        7.0: "smica2_smooth7.0.fits", 10.0: "smica2_smooth10.0.fits"}
NSD = 512
npix_d = hp.nside2npix(NSD)
Z = np.zeros((len(SCALES), 60))
for si, s in enumerate(SCALES):
    ms = hp.read_map(os.path.join(CACHE, MAPS[s]), field=0)
    ms = hp.ud_grade(ms, NSD)
    pxs = hp.ang2pix(NSD, l_deg, b_deg, lonlat=True)
    Z[si] = (ms[pxs] * 1e6 - ms.mean() * 1e6) / (ms.std() * 1e6)
zbar = Z.mean(axis=0)
zbar_abs = np.abs(zbar)
n_stable = int((zbar_abs > 2).sum())
stable_idx = sorted(np.where(zbar_abs > 2)[0].tolist())
max_zbar = zbar_abs.max()
argmax = int(np.argmax(zbar_abs))
check("G1 穩定異常=5", n_stable == 5, f"({n_stable}: {stable_idx})")
check("G2 idx=[0,9,33,47,53]", stable_idx == [0, 9, 33, 47, 53], f"({stable_idx})")
check("G3 max=node47 2.78", argmax == 47 and abs(max_zbar - 2.779) < 0.1, f"(node{argmax} {max_zbar:.3f})")
check("G4 node53 zbar=+2.14", abs(zbar[53] - 2.1358) < 0.15, f"({zbar[53]:+.3f})")
check("G5 node33 zbar=-2.10", abs(zbar[33] + 2.0956) < 0.15, f"({zbar[33]:+.3f})")
check("G6 node0 zbar=-2.70", abs(zbar[0] + 2.7021) < 0.15, f"({zbar[0]:+.3f})")
check("G7 node9 zbar=-2.24", abs(zbar[9] + 2.2376) < 0.15, f"({zbar[9]:+.3f})")

# ============ H. node53 三地圖 3°盤 + 環 ΔT ============
print("\n--- H. node53 三地圖 (4.17° cache) ---")
L53, B53 = 319.50, -34.20
vals3, ring3 = {}, {}
for name, fn in [("SMICA", "smica2_smooth4.17.fits"), ("NILC", "nilc2_smooth4.17.fits"),
                 ("Commander", "commander_smooth4.17.fits")]:
    mm = hp.read_map(os.path.join(CACHE, fn), field=0)
    ns = hp.get_nside(mm)
    vec = hp.ang2vec(L53, B53, lonlat=True)
    p3 = hp.query_disc(ns, vec, np.radians(3.0))
    pc = hp.query_disc(ns, vec, np.radians(2.0))
    pr = hp.query_disc(ns, vec, np.radians(8.0))
    pi = hp.query_disc(ns, vec, np.radians(4.0))
    pr = np.setdiff1d(pr, pi)
    vals3[name] = np.mean(mm[p3]) * 1e6
    ring3[name] = (np.mean(mm[pc]) - np.mean(mm[pr])) * 1e6
spread3 = (max(vals3.values()) - min(vals3.values())) / abs(np.mean(list(vals3.values()))) * 100
spread_r = (max(ring3.values()) - min(ring3.values())) / abs(np.mean(list(ring3.values()))) * 100
check("H1 SMICA 3°盤 +96.83", abs(vals3["SMICA"] - 96.83) < 1.0, f"({vals3['SMICA']:+.2f})")
check("H2 NILC 3°盤 +96.21", abs(vals3["NILC"] - 96.21) < 1.0, f"({vals3['NILC']:+.2f})")
check("H3 Commander 3°盤 +95.14", abs(vals3["Commander"] - 95.14) < 1.0, f"({vals3['Commander']:+.2f})")
check("H4 spread=1.8%", abs(spread3 - 1.76) < 0.5, f"({spread3:.2f}%)")
check("H5 環ΔT SMICA +82.0", abs(ring3["SMICA"] - 81.97) < 2.0, f"({ring3['SMICA']:+.2f})")
check("H6 環ΔT NILC +82.1", abs(ring3["NILC"] - 82.14) < 2.0, f"({ring3['NILC']:+.2f})")
check("H7 環ΔT Commander +82.4", abs(ring3["Commander"] - 82.40) < 2.0, f"({ring3['Commander']:+.2f})")
check("H8 環 spread=0.5%", abs(spread_r - 0.52) < 0.3, f"({spread_r:.2f}%)")

# ============ I. node53 多頻譜 (HFI 3.0° smooth) + dust + 對徑 + mask ============
print("\n--- I. node53 多頻譜 dT (HFI 3.0° FWHM) + 353 dust + 對徑 + mask ---")
FWHM = 3.0
SIGMA = np.radians(FWHM) / (2 * np.sqrt(2 * np.log(2)))
FREQ_MAPS = {100: "HFI_SkyMap_100_2048_R3.01_full.fits",
             143: "HFI_SkyMap_143_2048_R3.01_full.fits",
             217: "HFI_SkyMap_217_2048_R3.01_full.fits",
             353: "HFI_SkyMap_353_2048_R3.01_full.fits"}
maps = {}
for freq, fn in FREQ_MAPS.items():
    m = hp.read_map(os.path.join(DATA27, fn), field=0, nest=True)
    m = hp.reorder(m, n2r=True)
    bad = (~np.isfinite(m)) | (np.abs(m) > 1e-3)
    m = np.where(bad, np.nan, m)
    mk = np.isfinite(m)
    sm = hp.smoothing(np.where(mk, m, 0.0), sigma=SIGMA, verbose=False)
    sm_ok = hp.smoothing(mk.astype(float), sigma=SIGMA, verbose=False)
    maps[freq] = np.where(sm_ok > 0.1, sm / sm_ok, np.nan)

def core_ring(l, b):
    vec = hp.ang2vec(l, b, lonlat=True)
    out = {}
    for freq, m in maps.items():
        ns = hp.get_nside(m)
        pc = hp.query_disc(ns, vec, np.radians(2.0))
        pr = hp.query_disc(ns, vec, np.radians(8.0))
        pi = hp.query_disc(ns, vec, np.radians(4.0))
        pr = np.setdiff1d(pr, pi)
        out[freq] = (np.nanmean(m[pc]) - np.nanmean(m[pr])) * 1e6
    return out

dT53 = core_ring(L53, B53)
check("I1 100GHz dT=+82.7", abs(dT53[100] - 82.75) < 3.0, f"({dT53[100]:+.1f})")
check("I2 143GHz dT=+80.9", abs(dT53[143] - 80.90) < 3.0, f"({dT53[143]:+.1f})")
check("I3 217GHz dT=+51.0", abs(dT53[217] - 50.97) < 4.0, f"({dT53[217]:+.1f})")
check("I4 353GHz dT=+103.5", abs(dT53[353] - 103.52) < 8.0, f"({dT53[353]:+.1f})")
# 平譜 spread (100/143/217)
v = [dT53[100], dT53[143], dT53[217]]
spread_dT = (max(v) - min(v)) / max(abs(x) for x in v)
check("I5 平譜 spread=0.38", abs(spread_dT - 0.384) < 0.15, f"({spread_dT:.3f})")
# I6: 353 dust — 原記錄 (12_node53_antipode_mask.py) 定義: bad = ~finite | |T|>1e-3
# (即 |T|>1000 μK 嘅強 dust pixel 被視 bad → nan), 然後 3° 盤 nanmean = 914 μK,
# 高緯 median (|b|>30°) = 698 μK → 1.31x。audit 必須重現同一定義先可核對原記錄。
# 注意: 若用 raw finite (唔篩 1e-3), 3° 盤 = 1298 μK — 定義唔同, 唔可比。
m353_raw = hp.read_map(os.path.join(DATA27, "HFI_SkyMap_353_2048_R3.01_full.fits"),
                       field=0, nest=True)
m353_raw = hp.reorder(m353_raw, n2r=True)
bad353 = (~np.isfinite(m353_raw)) | (np.abs(m353_raw) > 1e-3)
m353_raw = np.where(bad353, np.nan, m353_raw)
ns353 = hp.get_nside(m353_raw)
vec53 = hp.ang2vec(L53, B53, lonlat=True)
vec0 = hp.ang2vec(209.0, -57.0, lonlat=True)
dust53 = np.nanmean(m353_raw[hp.query_disc(ns353, vec53, np.radians(3.0))]) * 1e6
dust0 = np.nanmean(m353_raw[hp.query_disc(ns353, vec0, np.radians(2.0))]) * 1e6
check("I6 353 dust node53=914 (1.31x 高緯)", abs(dust53 - 914) < 60, f"({dust53:+.0f})")
check("I7 353 dust node0=542", abs(dust0 - 542) < 60, f"({dust0:+.0f})")
# 對徑
vec_a = hp.ang2vec((L53 + 180) % 360, +34.2, lonlat=True)
T_a = np.mean(m417[hp.query_disc(nside, vec_a, np.radians(3.0))]) * 1e6
check("I8 對徑 -46.05", abs(T_a + 46.05) < 1.5, f"({T_a:+.2f})")
# R3 mask
mk = hp.read_map(os.path.join(DATA27, "COM_Mask_CMB-common-Mask-Int_2048_R3.00.fits"), field=0)
ns_mk = hp.get_nside(mk)
p53 = mk[hp.ang2pix(ns_mk, L53, B53, lonlat=True)]
p47 = mk[hp.ang2pix(ns_mk, 313.47, -8.58, lonlat=True)]
check("I9 node53 R3 unmasked", p53 > 0.5, f"(pixel={p53:.3f})")
check("I10 node47 R3 masked (對比)", p47 < 0.5, f"(pixel={p47:.3f})")

# ============ J. node33 ============
print("\n--- J. node33 三地圖 + 多頻譜 + 353 dust + mask ---")
L33, B33 = 191.4, -16.1
vals33 = {}
for name, fn in [("SMICA", "smica2_smooth4.17.fits"), ("NILC", "nilc2_smooth4.17.fits"),
                 ("Commander", "commander_smooth4.17.fits")]:
    mm = hp.read_map(os.path.join(CACHE, fn), field=0)
    ns = hp.get_nside(mm)
    vec = hp.ang2vec(L33, B33, lonlat=True)
    p3 = hp.query_disc(ns, vec, np.radians(3.0))
    vals33[name] = np.mean(mm[p3]) * 1e6
spread33 = (max(vals33.values()) - min(vals33.values())) / abs(np.mean(list(vals33.values()))) * 100
check("J1 SMICA -74.12", abs(vals33["SMICA"] + 74.12) < 1.5, f"({vals33['SMICA']:+.2f})")
check("J2 NILC -74.60", abs(vals33["NILC"] + 74.60) < 1.5, f"({vals33['NILC']:+.2f})")
check("J3 Commander -71.78", abs(vals33["Commander"] + 71.78) < 1.5, f"({vals33['Commander']:+.2f})")
check("J4 spread=3.8%", abs(spread33 - 3.83) < 0.5, f"({spread33:.2f}%)")
dT33 = core_ring(L33, B33)
check("J5 100GHz dT=-9.0", abs(dT33[100] + 8.97) < 3.0, f"({dT33[100]:+.1f})")
check("J6 143GHz dT=+1.3", abs(dT33[143] - 1.31) < 3.0, f"({dT33[143]:+.1f})")
check("J7 217GHz dT=+47.4", abs(dT33[217] - 47.39) < 5.0, f"({dT33[217]:+.1f})")
# J8/J9: node33 353 dust — 原記錄 (16_node33_verify.py) 定義: 只 finite (唔理
# |T|>1e-3 閾值!) 因為 node33 353 值 +4.8e-3 K 超過 1e-3 會被誤判 bad → nan。
# 注意: 呢個同 I6 (node53) 嘅 1e-3 閾值定義唔同 — 因為原 script 各自用唔同定義,
# audit 必須重現各自原 script 定義先可核對。
m353_f = hp.read_map(os.path.join(DATA27, "HFI_SkyMap_353_2048_R3.01_full.fits"),
                     field=0, nest=True)
m353_f = hp.reorder(m353_f, n2r=True)
m353_f = np.where(np.isfinite(m353_f), m353_f, np.nan)
ns353f = hp.get_nside(m353_f)
dust33 = np.nanmean(m353_f[hp.query_disc(ns353f, hp.ang2vec(L33, B33, lonlat=True), np.radians(2.0))]) * 1e6
dust0_f = np.nanmean(m353_f[hp.query_disc(ns353f, hp.ang2vec(209.0, -57.0, lonlat=True), np.radians(2.0))]) * 1e6
check("J8 353 dust node33 +4844", abs(dust33 - 4844) < 300, f"({dust33:+.0f})")
check("J9 dust 8.9x node0", abs(dust33 / dust0_f - 8.9) < 1.2, f"({dust33/dust0_f:.1f}x)")
p33m = mk[hp.ang2pix(ns_mk, L33, B33, lonlat=True)]
check("J10 node33 R3 unmasked", p33m > 0.5, f"(pixel={p33m:.3f})")
# node33 raw 143 GHz 轉正 (多頻譜判前景關鍵)
m143 = maps[143]
ns143 = hp.get_nside(m143)
T143_33 = m143[hp.ang2pix(ns143, L33, B33, lonlat=True)] * 1e6
T143_53 = m143[hp.ang2pix(ns143, L53, B53, lonlat=True)] * 1e6
check("J11 node33 143GHz +104 (轉正)", abs(T143_33 - 104.4) < 8.0, f"({T143_33:+.1f})")
check("J12 node53 143GHz +171", abs(T143_53 - 171.4) < 8.0, f"({T143_53:+.1f})")
# node33 raw SMICA 3° (4.17 cache) 為負 (符號分歧: SMICA 冷 vs 143 熱)
sm33 = hp.read_map(os.path.join(CACHE, "smica2_smooth4.17.fits"), field=0)
ns_s = hp.get_nside(sm33)
SMICA_33 = sm33[hp.ang2pix(ns_s, L33, B33, lonlat=True)] * 1e6
check("J13 node33 SMICA 冷 (<0) vs 143 熱 (>0) 符號分歧",
      SMICA_33 < 0 and T143_33 > 0, f"(SMICA {SMICA_33:+.1f}, 143 {T143_33:+.1f})")

# ============ K. 文檔完整性 (data 檔 ↔ docs 交叉, 只讀) ============
print("\n--- K. 文檔完整性: 宣稱數值 ↔ 5 份 docs (只讀核對) ---")
docs = {}
for fn in ["NN_results.md", "DISCRETENESS_COMPLETE.md", "NODE53_REPORT.md",
           "NODE33_REPORT.md", "01_problem_record.md", "SESSION_START.md"]:
    with open(os.path.join(O30, fn), encoding="utf-8") as f:
        docs[fn] = f.read().replace("−", "-")
all_docs = " ".join(docs.values())
key_claims = [
    ("-1.25", "60節點 mean"), ("-0.21", "z all iso"), ("32.75", "mean|T|"),
    ("1.154", "冷熱比"), ("29:31", "冷熱 count"), ("19.05", "ΔE=0"),
    ("5 個跨尺度", "離散 5"), ("node53", "node53 出現"), ("+112", "node53 T"),
    ("96.8", "SMICA 3°盤"), ("1.8%", "spread"), ("0.5%", "環 spread"),
    ("-46.05", "對徑"), ("unmasked", "mask"), ("4844", "353 dust"),
    ("5.09", "217/143 node33"), ("8.9", "dust 8.9x"),
    ("3.8%", "node33 spread"), ("-74.12", "node33 SMICA"),
]
for val, label in key_claims:
    check(f"K1 '{val}' ({label})", val in all_docs)
# data 檔被引用
data_refs = ["01_mean_vs_random.txt", "02_stack_radial.txt", "03_multiscale.txt",
             "04_sign_asymmetry.txt", "06_amplitude_test.txt", "08_discreteness.txt",
             "09_node53_multifreq.json", "10_node53_ring_background.json",
             "11_node53_crossmap.json", "12_node53_antipode_mask.json",
             "15_node33_multifreq.json"]
for df in data_refs:
    check(f"K2 data/{df} 被引用", df in all_docs)
# 交叉引用
check("K3 NN→DISCRETENESS", "DISCRETENESS_COMPLETE" in docs["NN_results.md"])
check("K4 NN→NODE53", "NODE53_REPORT" in docs["NN_results.md"])
check("K5 01→NODE53", "NODE53_REPORT" in docs["01_problem_record.md"])
check("K6 01→NN", "NN_results" in docs["01_problem_record.md"])
check("K7 01→NODE33", "NODE33_REPORT" in docs["01_problem_record.md"])
check("K8 NN→NODE33", "NODE33_REPORT" in docs["NN_results.md"])

# ============ 總結 ============
print("\n" + "=" * 72)
print(f"結果: {len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL:
    print("❌ FAILED:")
    for f_ in FAIL:
        print(f"   - {f_}")
    exit(1)
print("✅ 全部通過 — O30 所有推導/計算/結果獨立重算一致")
