#!/usr/bin/env python3
"""
02_decay_and_structure.py — O25: 衰減模型比較 + ΔE0 V形定位 + 顯著性
=====================================================================
1. 冷熱差衰減: 單指數 vs 雙指數 vs 冪律 (BIC 比較)
2. 高緯 ΔE0 比例 V 形: 最小值定位 + 二次擬合
3. 每尺度冷熱差 Welch 顯著性 (SMICA 全 60 節點)
4. 結構尺度解讀: 3°-5° 窗口
"""
import healpy as hp
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u
from scipy.optimize import curve_fit
from scipy import stats
import os, json

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
CACHE = "/tmp/cache_o3"
OUT = os.path.join(BASE, "o25_scale_spectrum")
DATA = os.path.join(OUT, "data")

SCALES = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 4.17, 5.0, 7.0, 10.0]
ZERO_E = [10, 12, 19, 22, 23, 25, 28, 32, 37, 40, 45, 46]

# 節點 + 著色 + 銀道
nodes = []
with open(os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")) as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic
b_deg = np.array(gal.b.deg)

color = {}
with open(os.path.join(BASE, "cmb_cold_spot/data/anchored_coloring.txt")) as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        parts = line.split()
        color[int(parts[0])] = int(parts[3])
color_arr = np.array([color[i] for i in range(60)])
zero_mask = np.zeros(60, dtype=bool)
zero_mask[ZERO_E] = True
gal_mask = np.abs(b_deg) < 20

# ============ 重新抽樣 (為咗 Welch 檢驗要完整 T 向量) ============
T_by_scale = {}
for s in SCALES:
    path = os.path.join(CACHE, f"SMICA_smooth{s}.fits" if s != 4.17 else "SMICA_smooth4.17.fits")
    m = hp.read_map(path, field=0)
    nside = hp.get_nside(m)
    pix = hp.ang2pix(nside, gal.l.deg, gal.b.deg, lonlat=True)
    T_by_scale[s] = m[pix] * 1e6
    del m

print("=" * 80)
print("1. 冷熱差衰減模型比較 (BIC)")
print("=" * 80)
scales_arr = np.array(SCALES)
diffs = np.array([T_by_scale[s][color_arr==1].mean() - T_by_scale[s][color_arr==0].mean() for s in SCALES])
diff_abs = np.abs(diffs)
n = len(SCALES)

def bic(n, rss, k):
    return n*np.log(rss/n) + k*np.log(n)

models = {}

# 單指數: y = a*exp(-x/tau) + c
def exp3(x, a, tau, c):
    return a*np.exp(-x/tau) + c
popt, _ = curve_fit(exp3, scales_arr, diff_abs, p0=(35, 3, 13), maxfev=20000)
pred = exp3(scales_arr, *popt)
rss = np.sum((diff_abs-pred)**2)
models['exp3'] = (popt, rss, bic(n, rss, 3))
print(f"  單指數 exp3: a={popt[0]:.2f} tau={popt[1]:.3f}° c={popt[2]:.2f} R²={1-rss/np.sum((diff_abs-diff_abs.mean())**2):.4f} BIC={models['exp3'][2]:.1f}")

# 雙指數: y = a1*exp(-x/t1) + a2*exp(-x/t2) + c
def exp5(x, a1, t1, a2, t2, c):
    return a1*np.exp(-x/t1) + a2*np.exp(-x/t2) + c
try:
    popt, _ = curve_fit(exp5, scales_arr, diff_abs, p0=(25, 1.5, 15, 8, 10), maxfev=40000)
    pred = exp5(scales_arr, *popt)
    rss = np.sum((diff_abs-pred)**2)
    models['exp5'] = (popt, rss, bic(n, rss, 5))
    print(f"  雙指數 exp5: a1={popt[0]:.2f} t1={popt[1]:.3f}° a2={popt[2]:.2f} t2={popt[3]:.3f}° c={popt[4]:.2f} R²={1-rss/np.sum((diff_abs-diff_abs.mean())**2):.4f} BIC={models['exp5'][2]:.1f}")
except Exception as e:
    print(f"  雙指數 exp5: FAIL {e}")

# 冪律: y = a*x^b + c
def pow3(x, a, b, c):
    return a*x**b + c
popt, _ = curve_fit(pow3, scales_arr, diff_abs, p0=(40, -0.4, 0), maxfev=20000)
pred = pow3(scales_arr, *popt)
rss = np.sum((diff_abs-pred)**2)
models['pow3'] = (popt, rss, bic(n, rss, 3))
print(f"  冪律 pow3: a={popt[0]:.2f} b={popt[1]:.3f} c={popt[2]:.2f} R²={1-rss/np.sum((diff_abs-diff_abs.mean())**2):.4f} BIC={models['pow3'][2]:.1f}")

# 對數線性 (純冪律無常數): log y = log a + b log x
A = np.vstack([np.ones_like(np.log(scales_arr)), np.log(scales_arr)]).T
(lna, b), *_ = np.linalg.lstsq(A, np.log(diff_abs), rcond=None)
pred = np.exp(lna) * scales_arr**b
rss = np.sum((diff_abs-pred)**2)
models['pure_pow'] = (np.array([np.exp(lna), b]), rss, bic(n, rss, 2))
print(f"  純冪律: a={np.exp(lna):.2f} b={b:.3f} R²={1-rss/np.sum((diff_abs-diff_abs.mean())**2):.4f} BIC={models['pure_pow'][2]:.1f}")

# 常數 (null)
pred = np.full(n, diff_abs.mean())
rss = np.sum((diff_abs-pred)**2)
models['const'] = (None, rss, bic(n, rss, 1))
print(f"  常數 null: mean={diff_abs.mean():.2f} BIC={models['const'][2]:.1f}")

best = min(models, key=lambda k: models[k][2])
print(f"\n  🏆 最佳模型: {best} (BIC={models[best][2]:.1f})")
for k, v in sorted(models.items(), key=lambda kv: kv[1][2]):
    print(f"    {k}: BIC={v[2]:.1f}  ΔBIC vs best = {v[2]-models[best][2]:+.1f}")

# ============ 2. 高緯 ΔE0 比例 V 形 ============
print("\n" + "=" * 80)
print("2. 高緯 ΔE0 比例 V 形 (SMICA)")
print("=" * 80)
hi_ratios = []
for s in SCALES:
    T = T_by_scale[s]
    hi_zero = zero_mask & ~gal_mask
    hi_other = ~zero_mask & ~gal_mask
    r = np.abs(T[hi_zero]).mean() / np.abs(T[hi_other]).mean()
    hi_ratios.append(r)
    print(f"  {s:>5.2f}° : {r:.4f}")
hi_ratios = np.array(hi_ratios)

# 二次擬合 r(θ) = aθ² + bθ + c
def quad(x, a, b, c):
    return a*x**2 + b*x + c
popt, _ = curve_fit(quad, scales_arr, hi_ratios, p0=(0.02, -0.2, 1.0), maxfev=20000)
# 最小值: θ* = -b/(2a)
theta_star = -popt[1]/(2*popt[0])
r_min = quad(theta_star, *popt)
print(f"\n  二次擬合: r(θ) = {popt[0]:.4f}θ² + {popt[1]:.4f}θ + {popt[2]:.3f}")
print(f"  V 形最小值: θ* = {theta_star:.2f}°, r_min = {r_min:.3f}")
print(f"  觀測最小值: θ = {SCALES[int(np.argmin(hi_ratios))]}°, r = {hi_ratios.min():.3f}")

# 結構尺度解讀
print(f"\n  結構尺度對照:")
print(f"    4.17° = 冷斑 FWHM (R8)")
print(f"    5.00° = ΔE0 壓制峰值尺度")
print(f"    φ·4.17 = {4.17*1.618034:.2f}° ≈ 7°")
print(f"    4.17/φ = {4.17/1.618034:.2f}° ≈ 2.6°")

# ============ 3. 每尺度冷熱差 Welch 顯著性 ============
print("\n" + "=" * 80)
print("3. 冷熱差 Welch t-test per 尺度 (SMICA, 全 60 節點)")
print("=" * 80)
print(f"{'scale':>6} | {'diff':>8} | {'t':>6} | {'p':>7} | {'sig'}")
for s in SCALES:
    T = T_by_scale[s]
    cold = T[color_arr==1]
    hot = T[color_arr==0]
    t, p = stats.ttest_ind(cold, hot, equal_var=False)
    sig = "🟢" if p < 0.05 else ("🟡" if p < 0.1 else "🔴")
    print(f"{s:>6.2f} | {cold.mean()-hot.mean():>+8.2f} | {t:>6.2f} | {p:>7.4f} | {sig}")

# ============ 4. 三地圖一致性 ============
print("\n" + "=" * 80)
print("4. 三地圖冷熱差一致性 (spread %)")
print("=" * 80)
with open(os.path.join(DATA, "scale_spectrum.json")) as f:
    R = json.load(f)
for s in SCALES:
    vals = [R[m][str(s)]["cold_hot_diff_uK"] for m in ["SMICA", "NILC", "Commander"]]
    spread = (max(vals)-min(vals))/abs(np.mean(vals))*100
    status = "🟢🟢" if spread < 1 else ("🟢" if spread < 5 else ("🟡" if spread < 20 else "🔴"))
    print(f"  {s:>5.2f}° : SMICA={vals[0]:+.2f} NILC={vals[1]:+.2f} Commander={vals[2]:+.2f} | spread={spread:.2f}% {status}")

# 儲存模型結果
out = {
    "decay_models": {k: {"params": [float(x) for x in v[0]] if v[0] is not None else None, "rss": float(v[1]), "bic": float(v[2])} for k, v in models.items()},
    "best_model": best,
    "hi_zero_quad_fit": {"a": float(popt[0]), "b": float(popt[1]), "c": float(popt[2]), "theta_star": float(theta_star), "r_min": float(r_min)},
    "hi_zero_ratios": {str(s): float(r) for s, r in zip(SCALES, hi_ratios)},
}
with open(os.path.join(DATA, "decay_analysis.json"), "w") as f:
    json.dump(out, f, indent=2)
print("\n✅ saved data/decay_analysis.json")
