#!/usr/bin/env python3
"""
01_scale_spectrum.py — O25: 節點溫度信號隨平滑尺度嘅完整尺度譜
================================================================
用 /tmp/cache_o3/ 全部 10 尺度 × 3 地圖 (SMICA/NILC/Commander) cache,
提取 60 節點溫度 per 尺度, 計算:
  1. 冷熱差 (cold-color vs hot-color mean) per 尺度
  2. ΔE=0 比例 (12 零能量節點 mean|T| / 其他 48) per 尺度
  3. 極端節點行為 (冷斑 node0, node9, node57 對徑) per 尺度
  4. 衰減擬合 (指數/冪律) — 冷斑同冷熱差
  5. 三地圖一致性 per 尺度

框架: ICRS RA/Dec → Galactic (SkyCoord), cache 已 RING ordering (驗證過)
"""
import healpy as hp
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u
import os, json, math

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
CACHE = "/tmp/cache_o3"
OUT = os.path.join(BASE, "o25_scale_spectrum")
DATA = os.path.join(OUT, "data")
os.makedirs(DATA, exist_ok=True)

SCALES = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 4.17, 5.0, 7.0, 10.0]
MAPS = ["SMICA", "NILC", "Commander"]

# 節點座標 (ICRS)
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

# 著色 (cold=1)
color = {}
with open(os.path.join(BASE, "cmb_cold_spot/data/anchored_coloring.txt")) as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        parts = line.split()
        color[int(parts[0])] = int(parts[3])
color_arr = np.array([color[i] for i in range(60)])

# ΔE=0 零能量節點 (O3/拓撲位元記錄)
ZERO_E = [10, 12, 19, 22, 23, 25, 28, 32, 37, 40, 45, 46]
zero_mask = np.zeros(60, dtype=bool)
zero_mask[ZERO_E] = True

# 特殊節點
COLD = 0       # 冷斑
NODE9 = 9      # 第二冷結構
ANTI = 57      # 對徑

def load_map(mname, scale):
    """載入 cache 地圖 (RING, nside=2048, float32, 單位 K)"""
    if mname == "SMICA":
        fname = f"SMICA_smooth{scale}.fits" if scale != 4.17 else "SMICA_smooth4.17.fits"
    else:
        fname = f"{mname}_{scale}.fits"
    path = os.path.join(CACHE, fname)
    if not os.path.exists(path):
        return None
    m = hp.read_map(path, field=0)
    return m

results = {m: {} for m in MAPS}

for mname in MAPS:
    for scale in SCALES:
        m = load_map(mname, scale)
        if m is None:
            results[mname][scale] = {"error": f"missing {mname}_{scale}"}
            continue
        nside = hp.get_nside(m)
        pix = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)
        T = m[pix] * 1e6  # μK

        cold_mask = color_arr == 1
        hot_mask = color_arr == 0
        cold_hot_diff = T[cold_mask].mean() - T[hot_mask].mean()

        zero_T = np.abs(T[zero_mask])
        other_T = np.abs(T[~zero_mask])
        zero_ratio = zero_T.mean() / other_T.mean()

        # 銀河盤遮罩 (|b|<20)
        gal_mask = np.abs(b_deg) < 20
        hi_zero = zero_mask & ~gal_mask
        hi_other = ~zero_mask & ~gal_mask
        hi_zero_ratio = np.abs(T[hi_zero]).mean() / np.abs(T[hi_other]).mean() if hi_other.sum() > 0 else None

        results[mname][scale] = {
            "cold_hot_diff_uK": round(float(cold_hot_diff), 3),
            "cold_mean_uK": round(float(T[cold_mask].mean()), 3),
            "hot_mean_uK": round(float(T[hot_mask].mean()), 3),
            "zeroE_ratio": round(float(zero_ratio), 4),
            "zeroE_mean_abs": round(float(zero_T.mean()), 3),
            "other_mean_abs": round(float(other_T.mean()), 3),
            "hi_lat_zero_ratio": round(float(hi_zero_ratio), 4) if hi_zero_ratio else None,
            "node0": round(float(T[COLD]), 3),
            "node9": round(float(T[NODE9]), 3),
            "node57": round(float(T[ANTI]), 3),
            "node45": round(float(T[45]), 3),
            "T_min": round(float(T.min()), 3),
            "T_min_idx": int(T.argmin()),
            "T_max": round(float(T.max()), 3),
            "T_max_idx": int(T.argmax()),
            "std": round(float(T.std()), 3),
        }
        del m  # 釋放記憶體

# ============ 儲存 ============
with open(os.path.join(DATA, "scale_spectrum.json"), "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

# ============ 打印摘要 ============
print("=" * 100)
print("O25 溫度尺度譜 — SMICA (10 尺度)")
print("=" * 100)
print(f"{'scale':>6} | {'冷-熱差':>8} | {'ΔE0比':>6} | {'node0':>8} | {'node9':>8} | {'node57':>7} | {'min':>8}(#{'':<2}) | {'max':>8}")
for s in SCALES:
    r = results["SMICA"][s]
    print(f"{s:>6.2f} | {r['cold_hot_diff_uK']:>+8.2f} | {r['zeroE_ratio']:>6.3f} | {r['node0']:>+8.2f} | {r['node9']:>+8.2f} | {r['node57']:>+7.2f} | {r['T_min']:>+8.2f}({r['T_min_idx']:>2d}) | {r['T_max']:>+8.2f}")

print("\n" + "=" * 100)
print("三地圖交叉 — 冷熱差 + ΔE0 比例 (NILC/Commander)")
print("=" * 100)
for s in SCALES:
    row = " | ".join(f"{m}: {results[m][s]['cold_hot_diff_uK']:+.1f}Δ {results[m][s]['zeroE_ratio']:.3f}r" for m in MAPS)
    print(f"{s:>6.2f} | {row}")

# ============ 衰減擬合 ============
print("\n" + "=" * 100)
print("衰減擬合 (SMICA)")
print("=" * 100)
scales_arr = np.array(SCALES)

# 冷斑 node0 衰減
node0_vals = np.array([results["SMICA"][s]["node0"] for s in SCALES])
# 冷熱差衰減
diff_vals = np.array([results["SMICA"][s]["cold_hot_diff_uK"] for s in SCALES])

def fit_exp(x, y):
    """擬合 y = a*exp(-x/tau) + c, 返回 (a, tau, c, R2)"""
    # 初始猜測: c = 最後值, 對 ln(y-c) 做線性擬合
    try:
        c0 = y[-1]
        if np.all(y - c0 > 0):
            yy = np.log(np.clip(y - c0, 1e-9, None))
            A = np.vstack([np.ones_like(x), x]).T
            (lna, neg_inv_tau), *_ = np.linalg.lstsq(A, yy, rcond=None)
            a, tau = np.exp(lna), -1.0/neg_inv_tau
            pred = a*np.exp(-x/tau) + c0
            ss_res = np.sum((y - pred)**2)
            ss_tot = np.sum((y - y.mean())**2)
            r2 = 1 - ss_res/ss_tot
            return a, tau, c0, r2
    except Exception as e:
        pass
    return None

def fit_pow(x, y):
    """擬合 |y| = a*x^b + c"""
    try:
        c0 = y[-1]
        if np.all(np.abs(y - c0) > 0):
            yy = np.log(np.abs(y - c0))
            xx = np.log(x)
            A = np.vstack([np.ones_like(xx), xx]).T
            (lna, b), *_ = np.linalg.lstsq(A, yy, rcond=None)
            a = np.exp(lna)
            pred = a*x**b + c0
            ss_res = np.sum((y - pred)**2)
            ss_tot = np.sum((y - y.mean())**2)
            r2 = 1 - ss_res/ss_tot
            return a, b, c0, r2
    except Exception:
        pass
    return None

print(f"冷斑 node0: {node0_vals}")
fe = fit_exp(scales_arr, node0_vals)
fp = fit_pow(scales_arr, node0_vals)
if fe:
    print(f"  指數: T(θ) = {fe[0]:.1f}·exp(-θ/{fe[1]:.2f}°) + {fe[2]:.1f}  (R²={fe[3]:.4f})")
if fp:
    print(f"  冪律: |T| = {fp[0]:.1f}·θ^{fp[1]:.3f} + {fp[2]:.1f}  (R²={fp[3]:.4f})")

print(f"\n冷熱差: {diff_vals}")
fe2 = fit_exp(scales_arr, diff_vals)
if fe2:
    print(f"  指數: ΔT(θ) = {fe2[0]:.1f}·exp(-θ/{fe2[1]:.2f}°) + {fe2[2]:.1f}  (R²={fe2[3]:.4f})")
# 冷熱差有負號 — 用絕對值
diff_abs = np.abs(diff_vals)
fe3 = fit_exp(scales_arr, diff_abs)
fp2 = fit_pow(scales_arr, diff_abs)
if fe3:
    print(f"  指數(|ΔT|): |ΔT|(θ) = {fe3[0]:.1f}·exp(-θ/{fe3[1]:.2f}°) + {fe3[2]:.1f}  (R²={fe3[3]:.4f})")
if fp2:
    print(f"  冪律(|ΔT|): |ΔT| = {fp2[0]:.1f}·θ^{fp2[1]:.3f} + {fp2[2]:.1f}  (R²={fp2[3]:.4f})")

# 峰值搜尋: 冷熱差絕對值最大尺度
peak_s = SCALES[int(np.argmax(np.abs(diff_vals)))]
print(f"\n峰值尺度: |冷熱差| 最大喺 {peak_s}° (值 {diff_vals[np.argmax(np.abs(diff_vals))]:+.2f} μK)")
peak_s0 = SCALES[int(np.argmax(np.abs(node0_vals)))]
print(f"峰值尺度: |node0| 最大喺 {peak_s0}° (值 {node0_vals[np.argmax(np.abs(node0_vals))]:+.2f} μK)")

# ΔE0 比例尺度譜
zero_ratios = np.array([results["SMICA"][s]["zeroE_ratio"] for s in SCALES])
print(f"\nΔE0 比例尺度譜 (SMICA): {zero_ratios}")
print(f"  最小值喺 {SCALES[int(np.argmin(zero_ratios))]}° (比例 {zero_ratios.min():.3f})")
print(f"  範圍: [{zero_ratios.min():.3f}, {zero_ratios.max():.3f}]")

print("\nDONE ✅")
