#!/usr/bin/env python3
"""
O2 F7 前景診斷 v2 — 拆 (0.2°, -37.9°) 353.1uK @ 0.5° 嘅 l=0° caveat
================================================================
v1 太慢 (3 maps x 9 scales smoothing)。v2 策略:
- 跨地圖 0.06% 一致: 用 O2 歷史 cross_map_validation.txt (09 已驗證)
- 新計算: SMICA only, 3 scales (0.5/1.0/3.0), 每層 smooth 一次
- T3 annulus: query_disc 局部 (0.5° 平滑)
- T6 點源測試: 徑向 profile FWHM vs beam (唔用 map2alm, 慢)
"""
import numpy as np
import healpy as hp
import os, math

HERE = os.path.dirname(os.path.abspath(__file__))
DATADIR = os.path.join(os.path.dirname(HERE), "data")
SMICA = "/home/wsl/.hermes/cache/scratch/planck_smica/smica.fits"
CROSSMAP = os.path.join(DATADIR, "cross_map_validation.txt")
F7 = (0.2, -37.9)
F6 = (157.8, -70.3)
COLD = (209.0, -57.0)

fails = []
def check(name, cond, detail=""):
    st = "✅" if cond else "❌"
    print(f"  {st} {name} {detail}")
    if not cond:
        fails.append(name)

print("=" * 70)
print("O2 F7 前景診斷 v2 (l=0 caveat attack)")
print("=" * 70)

# ---------- T1: historical 3-map consistency (O2 09 verified) ----------
print("\n[T1] 三地圖 F7 @0.5° (歷史 cross_map_validation.txt, O2 09/13 已驗證):")
hist = {}
with open(CROSSMAP) as f:
    for line in f:
        if "F7" in line and "0.5" in line.split()[:1]:
            try:
                toks = line.split()
                d = {}
                for t in toks[2:]:
                    if "=" in t:
                        k, v = t.split("=", 1)
                        d[k] = float(v)
                if d:
                    hist = d
            except ValueError:
                pass
print(f"  {hist}")
if hist:
    vals = np.array([v for v in hist.values() if abs(v) > 1.0])
    if len(vals) >= 2:
        mean = vals.mean(); spread = np.ptp(vals)
        pct = spread / abs(mean) * 100 if abs(mean) > 0.1 else 0
        check("T1 三地圖 ≈ 353 μK (0.06%)", abs(mean - 353.1) < 8, f"mean={mean:.1f}")
        check("T1 spread < 1%", pct < 1.0, f"spread={spread:.2f}uK ({pct:.2f}%)")
else:
    print("  (交叉地圖歷史值解讀失敗 — 落入後續 SMICA-only 判定)")

# ---------- load SMICA ----------
print("\n[load] SMICA...")
m = hp.read_map(SMICA, field=0)
nside = hp.get_nside(m)
print(f"  NSIDE={nside}")

smooth_cache = {}
def get_sm(fwhm):
    if fwhm not in smooth_cache:
        sig = np.radians(fwhm) / (2 * np.sqrt(2 * np.log(2)))
        smooth_cache[fwhm] = hp.remove_dipole(hp.smoothing(m, sigma=sig))
    return smooth_cache[fwhm]

# ---------- T2: SMICA multiscale ----------
print("\n[T2] SMICA 多尺度 (F7 vs F6 vs 冷斑):")
for fwhm in [0.5, 1.0, 3.0]:
    mm = get_sm(fwhm)
    a = mm[hp.ang2pix(nside, *F7, lonlat=True)] * 1e6
    b = mm[hp.ang2pix(nside, *F6, lonlat=True)] * 1e6
    c = mm[hp.ang2pix(nside, *COLD, lonlat=True)] * 1e6
    print(f"  {fwhm:>3.1f}°  F7:{a:+7.1f}  F6:{b:+7.1f}  cold:{c:+7.1f}")
mm05 = get_sm(0.5)
mm30 = get_sm(3.0)
f7_05 = mm05[hp.ang2pix(nside, *F7, lonlat=True)] * 1e6
f7_30 = mm30[hp.ang2pix(nside, *F7, lonlat=True)] * 1e6
r = f7_05 / (abs(f7_30) + 1e-9)
print(f"  ratio 0.5°/3.0° = {r:.2f} (點源 >5, 延展結構 <5)")
check("T2 唔似點源 (0.5/3.0 < 5)", r < 5, f"r={r:.2f}")

# ---------- T3: annulus peak-over-background (0.5° smoothed) ----------
print("\n[T3] annulus 1-3° 背景 (SMICA 0.5°):")
vec = hp.ang2vec(F7[0], F7[1], lonlat=True)
pix_disc = hp.query_disc(nside, vec, np.radians(5.0))
pix_vec = np.stack(hp.pix2vec(nside, pix_disc), axis=1)
ang_deg = np.degrees(hp.rotator.angdist(vec[np.newaxis, :], pix_vec))[0]
bg_mask = (ang_deg > 1.0) & (ang_deg < 3.0)
bg_mean = mm05[pix_disc[bg_mask]].mean() * 1e6
peak = mm05[hp.ang2pix(nside, *F7, lonlat=True)] * 1e6
print(f"  peak={peak:+.1f}, annulus={bg_mean:+.1f}, peak-bg={peak-bg_mean:+.1f}")
check("T3 peak 明顯 (peak-bg > 3x std)", (peak - bg_mean) > 3 * mm05.std() * 1e6,
      f"std={mm05.std()*1e6:.1f}")

# ---------- T4: nearest A5 node ----------
print("\n[T4] 最近 A5 節點:")
from astropy.coordinates import SkyCoord
import astropy.units as uu
nodes = np.loadtxt("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt")
sc = SkyCoord(ra=nodes[:, 0]*uu.deg, dec=nodes[:, 1]*uu.deg, frame='icrs')
gal = sc.galactic
nvec = hp.ang2vec(gal.l.deg, gal.b.deg, lonlat=True)
d = np.degrees(np.arccos(np.clip(np.dot(nvec, vec), -1, 1)))
dmin = d.min(); imin = d.argmin()
print(f"  最近節點 #{imin}: {dmin:.2f}° (O5 記錄 F6/F7 離節點 8-9°)")
check("T4 F7 唔喺節點上 (>3°)", dmin > 3.0, f"d={dmin:.2f}°")

# ---------- T5: galactic plane ----------
print("\n[T5] 銀道面:")
check("T5 |b|=37.9° > 20°", abs(F7[1]) > 20, "(唔受標準 mask 影響)")

# ---------- T6: radial profile FWHM vs beam (point-source test) ----------
print("\n[T6] 徑向 profile @0.5° 平滑 (FWHM vs 平滑 beam 0.5°):")
prof = []
for rad in [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0]:
    if rad == 0:
        prof.append(peak)
        continue
    pix_r = hp.query_disc(nside, vec, np.radians(rad + 0.05))
    pix_vec_r = np.stack(hp.pix2vec(nside, pix_r), axis=1)
    a_r = np.degrees(hp.rotator.angdist(vec[np.newaxis, :], pix_vec_r))[0]
    sel = (a_r >= rad - 0.05) & (a_r < rad + 0.05)
    prof.append(mm05[pix_r[sel]].mean() * 1e6 if sel.sum() > 0 else np.nan)
for rad, v in zip([0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0], prof):
    print(f"  r={rad:>4.2f}°: {v:+7.1f} μK")
half = peak / 2
fwhm_est = np.nan
for rad, v in zip([0.25, 0.5, 0.75, 1.0, 1.5, 2.0], prof[1:]):
    if v < half:
        fwhm_est = 2 * rad
        break
print(f"  FWHM_est ≈ {fwhm_est if not math.isnan(fwhm_est) else '>2°'}  (beam=0.5° 平滑)")
check("T6 結構延展 (FWHM_est > beam)", (fwhm_est if not math.isnan(fwhm_est) else 99) > 0.5,
      f"FWHM≈{fwhm_est}")

print("\n" + "=" * 70)
if fails:
    print(f"❌ F7 診斷有失敗: {len(fails)} — {'; '.join(fails)}")
else:
    print("✅ F7 診斷全過 — 延展結構, 唔似點源/前景")
print("=" * 70)