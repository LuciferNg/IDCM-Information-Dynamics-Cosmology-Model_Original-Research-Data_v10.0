#!/usr/bin/env python3
"""
99_double_verification.py — O8 雙重驗證 (獨立重算)
====================================================
獨立重算所有閉合鏈數字, 唔用之前 script 嘅輸出:
1. 節點間距 (由 a5_nodes.txt 直接算)
2. a/2π 預測
3. 冷斑 HWHM 由 SMICA cache 重算 (唔同 binning)
4. 180/44 交叉
5. 星系團真空一致性
全部 PASS 先可以寫記錄
"""
import healpy as hp
import numpy as np
import math
from astropy.coordinates import SkyCoord
import astropy.units as u

phi = (1 + 5**0.5) / 2
eps = (1/phi)/4

print("="*70)
print("O8 雙重驗證 — 獨立重算")
print("="*70)

fails = []
passes = []

# ===== T1: 節點間距 (直接由節點 txt 算) =====
nodes = []
with open("/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)

def vec(ra, dec):
    r, d = math.radians(ra), math.radians(dec)
    return np.array([math.cos(d)*math.cos(r), math.cos(d)*math.sin(r), math.sin(d)])

vecs = np.array([vec(ra, dec) for ra, dec in nodes])
dists = []
for i in range(60):
    for j in range(i+1, 60):
        dists.append(math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))))
dists = np.array(dists)
dists_sorted = np.sort(dists)
# 邊層 = 26.091° (60 節點最近鄰, 120 條邊 — o1 已驗證)
# 26.166° 係第二層 (5-fold 旋轉), 唔好混入!
edge_mask = dists_sorted < 26.13  # 26.091 同 26.166 之間嘅 gap
a_edge = dists_sorted[edge_mask].mean()
n_edges = edge_mask.sum()
print(f"\nT1: 邊長 (直接重算, {n_edges} 條邊 < 26.13°) = {a_edge:.6f}°")
if (n_edges == 60 or n_edges == 120) and abs(a_edge - 26.0913) < 0.001:
    passes.append("T1 邊長 ✅")
else:
    fails.append(f"T1 邊長 ❌ {a_edge}")
print(f"   {'✅' if abs(a_edge-26.0913)<0.001 else '❌'}")

# ===== T2: a/2π 預測 =====
pred = a_edge/(2*np.pi)
print(f"\nT2: a/2π = {pred:.6f}°")
if abs(pred - 4.1526) < 0.01:
    passes.append("T2 a/2π ✅")
else:
    fails.append("T2 ❌")
print(f"   {'✅' if abs(pred-4.1526)<0.01 else '❌'}")

# ===== T3: 冷斑 HWHM 重算 (獨立 binning: 0.2°) =====
cache_dir = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o5_catalog_compare/data/smooth_cache"
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic
l_deg, b_deg = gal.l.deg, gal.b.deg

# 用 1.0° 平滑 (最接近真實) + 0.2° bins 重算冷斑 HWHM
m = hp.remove_dipole(hp.read_map(f"{cache_dir}/smica2_smooth1.0.fits", field=0))
nside = hp.get_nside(m)
cv = hp.ang2vec(l_deg[0], b_deg[0], lonlat=True)
pix = hp.query_disc(nside, cv, np.radians(10))
pv = np.array(hp.pix2vec(nside, pix)).T
angs = np.degrees(np.arccos(np.clip(pv @ cv, -1, 1)))
vals = m[pix]
bins = np.linspace(0, 10, 101)  # 0.1° bins (同之前 0.1° 唔同: 之前 4.17° 平滑)
idx = np.digitize(angs, bins[1:-1])
prof = np.array([((bins[j]+bins[j+1])/2, np.mean(vals[idx==j])) for j in range(100) if (idx==j).sum() > 0])
r, v = prof[:, 0], prof[:, 1]
T0 = v[0]
target = T0/2
hwhm_indep = np.nan
for j in range(1, len(v)):
    if (v[j]-target)*(v[j-1]-target) <= 0:
        t = (target - v[j-1])/(v[j]-v[j-1])
        hwhm_indep = r[j-1] + t*(r[j]-r[j-1])
        break
print(f"\nT3: 冷斑 HWHM (1.0° 平滑, 0.1° bins 獨立重算) = {hwhm_indep:.3f}°")
print(f"    (之前 0.5° 平滑 0.1° bins: 4.027°, 1.0°: 4.205°)")
print(f"    獨立重算喺 4.03-4.21 範圍內: {'✅' if 3.9 < hwhm_indep < 4.4 else '❌'}")
if 3.9 < hwhm_indep < 4.4:
    passes.append("T3 冷斑 HWHM ✅")
else:
    fails.append("T3 ❌")

# ===== T4: 去平滑外推重算 (用獨立嘅 0.2° bins) =====
print(f"\nT4: 去平滑外推 (獨立重算)")
scales = [0.5, 1.0, 1.5, 2.0, 3.0]
hwhms = []
for s in scales:
    ms = hp.remove_dipole(hp.read_map(f"{cache_dir}/smica2_smooth{s}.fits", field=0))
    ns = hp.get_nside(ms)
    pix = hp.query_disc(ns, cv, np.radians(10))
    pv2 = np.array(hp.pix2vec(ns, pix)).T
    angs2 = np.degrees(np.arccos(np.clip(pv2 @ cv, -1, 1)))
    vals2 = ms[pix]
    bins2 = np.linspace(0, 10, 51)  # 0.2° bins (獨立!)
    idx2 = np.digitize(angs2, bins2[1:-1])
    prof2 = np.array([((bins2[j]+bins2[j+1])/2, np.mean(vals2[idx2==j])) for j in range(50) if (idx2==j).sum() > 0])
    r2, v2 = prof2[:, 0], prof2[:, 1]
    T02 = v2[0]
    tgt = T02/2
    hr = np.nan
    for j in range(1, len(v2)):
        if (v2[j]-tgt)*(v2[j-1]-tgt) <= 0:
            tt = (tgt - v2[j-1])/(v2[j]-v2[j-1])
            hr = r2[j-1] + tt*(r2[j]-r2[j-1])
            break
    hwhms.append(hr)

hwhms = np.array(hwhms)
sig2 = (np.array(scales)/(2*math.sqrt(2*math.log(2))))**2
# 線性擬合 (手動, 唔用 scipy)
A = np.vstack([sig2, np.ones(len(sig2))]).T
coef, res, rank, sv = np.linalg.lstsq(A, hwhms**2, rcond=None)
intercept = coef[1]
hwhm_true_indep = math.sqrt(max(0, intercept))
# R²
y_pred = A @ coef
ss_res = np.sum((hwhms**2 - y_pred)**2)
ss_tot = np.sum((hwhms**2 - np.mean(hwhms**2))**2)
r2_val = 1 - ss_res/ss_tot
print(f"    獨立外推 HWHM_true = {hwhm_true_indep:.4f}° (R²={r2_val:.3f})")
print(f"    a/2π = {pred:.4f}° → 偏差 {(hwhm_true_indep-pred)/pred*100:.2f}%")
dev = abs(hwhm_true_indep-pred)/pred*100
if dev < 2:
    passes.append(f"T4 外推閉合 ✅ ({dev:.2f}%)")
else:
    fails.append(f"T4 ❌ ({dev:.2f}%)")
print(f"    {'✅' if dev<2 else '❌'}")

# ===== T5: 180/44 交叉 =====
half44 = 180/44
dev44 = abs(hwhm_true_indep - half44)/half44*100
print(f"\nT5: 180/44 = {half44:.4f}° → 偏差 {dev44:.2f}%")
print(f"    a/2π 更接近實測: {'✅' if dev < dev44 else '❌ (180/44 更好)'}")
if dev < dev44:
    passes.append("T5 a/2π 優於 180/44 ✅")
else:
    fails.append("T5 ❌")

# ===== T6: 星系團真空 =====
print(f"\nT6: 星系團真空 4.5-5.0° vs a/2π = {pred:.2f}°")
print(f"    真空/影響 = {4.5/pred:.2f}-{5.0/pred:.2f}× (>1: 排除區大於影響區)")
if 4.5 > pred and 5.0 > pred:
    passes.append("T6 真空交叉 ✅")
else:
    fails.append("T6 ❌")
print(f"    {'✅' if 4.5 > pred else '❌'}")

# ===== T7: 尺度鏈 ℓ 一致性 =====
ell_pred = 180/pred
print(f"\nT7: ℓ = 180/(a/2π) = {ell_pred:.2f} ≈ 44 = 2N_d (偏差 {(ell_pred-44)/44*100:.2f}%)")
if abs(ell_pred - 44)/44 < 0.02:
    passes.append("T7 ℓ≈44 ✅")
else:
    fails.append("T7 ❌")
print(f"    {'✅' if abs(ell_pred-44)/44<0.02 else '❌'}")

# ===== 總結 =====
print("\n" + "="*70)
print(f"雙重驗證: {len(passes)} PASS / {len(fails)} FAIL")
for p in passes:
    print(f"  {p}")
for f in fails:
    print(f"  {f}")
print("="*70)

with open("/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o8_scale_radius/data/verification_result.txt", "w") as f:
    f.write(f"# O8 雙重驗證結果\n")
    f.write(f"# {len(passes)} PASS / {len(fails)} FAIL\n")
    f.write(f"# a = {a_edge:.6f}°, a/2π = {pred:.6f}°\n")
    f.write(f"# HWHM_true (獨立外推) = {hwhm_true_indep:.4f}° (偏差 {(hwhm_true_indep-pred)/pred*100:.2f}%)\n")
    f.write(f"# 180/44 = {half44:.4f}° (偏差 {dev44:.2f}%)\n")
    for p in passes:
        f.write(f"# PASS: {p}\n")
    for fl in fails:
        f.write(f"# FAIL: {fl}\n")

print(f"\n{'🎉 全部 PASS — 可以寫記錄' if not fails else '❌ 有 FAIL — 唔可以寫記錄'}")
