#!/usr/bin/env python3
"""
DOC_AUDIT.py — O8 文檔完整性 + 數值獨立核對
=============================================
用戶要求: 獨立核對每一個文檔 (SESSION_START / 01_problem_record / 02_results / README)
所有推導鏈內容、公式、數值; 確保歷史時序完整, 唔污染舊記錄。

方法: 由原始輸入 (a5_nodes.txt + SMICA cache) 獨立重算每個文檔聲稱嘅數值。
只讀, 唔寫任何文檔 (除 final_audit 結果記錄)。
"""
import healpy as hp
import numpy as np
import math
import os
from astropy.coordinates import SkyCoord
import astropy.units as u

phi = (1 + 5**0.5) / 2
eps = (1/phi)/4

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o8_scale_radius"
NODES = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt"
CACHE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o5_catalog_compare/data/smooth_cache"

print("="*72)
print("O8 文檔完整性 + 數值獨立核對 (DOC_AUDIT)")
print("="*72)

passes, fails = [], []

def check(name, cond, detail=""):
    if cond:
        passes.append(name)
        print(f"  ✅ {name} {detail}")
    else:
        fails.append(name)
        print(f"  ❌ {name} {detail}")

# ===== 0. 文檔存在性 + 時序 =====
print("\n[0] 文檔歷史完整性 + 時序")
docs = ["SESSION_START.md", "01_problem_record.md", "02_results.md", "README.md"]
for d in docs:
    p = os.path.join(BASE, d)
    check(f"存在: {d}", os.path.exists(p))

# 時序: SESSION_START (08-16) < 其他 (08-19)
import datetime
ts = {}
for d in docs:
    p = os.path.join(BASE, d)
    ts[d] = datetime.datetime.fromtimestamp(os.path.getmtime(p))
check("SESSION_START 最早", ts["SESSION_START.md"] < ts["01_problem_record.md"] and ts["SESSION_START.md"] < ts["02_results.md"],
      f"({ts['SESSION_START.md']:%m-%d %H:%M} < {ts['02_results.md']:%m-%d %H:%M})")
check("01_problem_record 唔早過 02_results", ts["01_problem_record.md"] >= ts["02_results.md"],
      f"({ts['01_problem_record.md']:%H:%M} >= {ts['02_results.md']:%H:%M})")

# 污染檢查: SESSION_START 應該保持 08-16 內容 (冇 O8 閉合結果)
# 注意: SESSION_START 原本就有「已閉合, o1_edge_length」(指 o1 前置, 唔係 O8)
# 所以只檢查 O8 專屬閉合詞 (a/2π 值 + HWHM + 去平滑)
ss = open(os.path.join(BASE, "SESSION_START.md")).read()
check("SESSION_START 冇 O8 閉合結果污染", "4.1526" not in ss and "HWHM" not in ss and "去平滑" not in ss,
      "(保持啟動文件原始狀態; 原有 o1 前置「已閉合」唔算污染)")

# ===== 1. 節點幾何 =====
print("\n[1] 節點幾何 (01_problem_record + 02_results §1)")
nodes = []
with open(NODES) as f:
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
dists = np.sort(dists)
a_edge = dists[dists < 26.13].mean()
check("邊長 26.0913°", abs(a_edge - 26.0913) < 0.0005, f"({a_edge:.4f})")

r_pred = a_edge/(2*np.pi)
check("a/2π = 4.1526°", abs(r_pred - 4.1526) < 0.0005, f"({r_pred:.4f})")

# Voronoi cell 半徑 14.79
cell_r = math.degrees(math.sqrt((4*np.pi/60)/np.pi))
check("Voronoi 14.79°", abs(cell_r - 14.79) < 0.02, f"({cell_r:.2f})")

# 最近鄰半距離 13.05
check("最近鄰半距離 13.05°", abs(a_edge/2 - 13.05) < 0.02, f"({a_edge/2:.2f})")

# 球面三角形高 22.80
h_tri = math.degrees(math.acos(math.cos(math.radians(a_edge))/math.cos(math.radians(a_edge/2))))
check("球面三角形高 22.80°", abs(h_tri - 22.80) < 0.02, f"({h_tri:.2f})")

# ===== 2. 比例搜索候選 =====
print("\n[2] 比例搜索 (02_results §2)")
cands = {
    "a/2π": a_edge/(2*np.pi),
    "180/44": 180/44,
    "a×ε": a_edge*eps,
    "a×φ⁻³": a_edge*phi**-3,
}
FWHM = 4.17
expected = {"a/2π": 0.42, "180/44": 1.90, "a×ε": 3.33, "a×φ⁻³": 47.7}
for name, val in cands.items():
    dev = abs(val - FWHM)/FWHM*100
    check(f"候選 {name} 偏差 {dev:.2f}%", abs(dev - expected[name]) < 0.15, f"(doc {expected[name]}%)")

ratio = a_edge/FWHM
check("26.09/4.17 = 6.2569", abs(ratio - 6.2569) < 0.001, f"({ratio:.4f})")
dev_2pi = (ratio - 2*np.pi)/(2*np.pi)*100
check("vs 2π 偏差 -0.42%", abs(dev_2pi + 0.42) < 0.05, f"({dev_2pi:.2f}%)")

# ===== 3. 冷斑 profile 表 (02_results §3) =====
print("\n[3] 冷斑 profile 表 (10 尺度)")
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic
l0, b0 = gal.l.deg[0], gal.b.deg[0]
cv0 = hp.ang2vec(l0, b0, lonlat=True)

doc_table = {
    0.5: (-202.1, 4.027), 1.0: (-172.9, 4.205), 1.5: (-160.7, 4.327),
    2.0: (-154.1, 4.400), 3.0: (-144.8, 4.511), 4.0: (-135.9, 4.633),
    4.17: (-134.2, 4.659), 5.0: (-124.6, 4.834), 7.0: (-99.7, 5.364),
    10.0: (-68.8, 5.904),
}
prof_ok = True
for s in doc_table:
    fn = os.path.join(CACHE, f"smica2_smooth{s}.fits")
    if not os.path.exists(fn):
        print(f"  ❌ cache 缺失: {s}°")
        prof_ok = False
        continue
    ms = hp.remove_dipole(hp.read_map(fn, field=0))
    ns = hp.get_nside(ms)
    pix = hp.query_disc(ns, cv0, np.radians(15))
    pv = np.array(hp.pix2vec(ns, pix)).T
    angs = np.degrees(np.arccos(np.clip(pv @ cv0, -1, 1)))
    vals = ms[pix]
    bins = np.linspace(0, 15, 150)  # 0.1° bins (同 script 05)
    idx = np.digitize(angs, bins[1:-1])
    prof = np.array([((bins[j]+bins[j+1])/2, np.mean(vals[idx==j])) for j in range(149) if (idx==j).sum() > 0])
    r, v = prof[:, 0], prof[:, 1]
    T0 = v[0]*1e6
    tgt = v[0]/2
    hr = np.nan
    for j in range(1, len(v)):
        if (v[j]-tgt)*(v[j-1]-tgt) <= 0:
            tt = (tgt - v[j-1])/(v[j]-v[j-1])
            hr = r[j-1] + tt*(r[j]-r[j-1])
            break
    dt = abs(T0 - doc_table[s][0])
    dh = abs(hr - doc_table[s][1])
    if dt > 0.6 or dh > 0.003:
        prof_ok = False
        print(f"  ❌ {s}°: doc({doc_table[s]}) vs 重算({T0:.1f},{hr:.3f})")
check("冷斑 profile 表 10 尺度", prof_ok)

# ===== 4. 去平滑外推 =====
print("\n[4] 去平滑外推 (02_results §3)")
scales_fit = [0.5, 1.0, 1.5, 2.0, 3.0]
hwhms = []
for s in scales_fit:
    ms = hp.remove_dipole(hp.read_map(os.path.join(CACHE, f"smica2_smooth{s}.fits"), field=0))
    ns = hp.get_nside(ms)
    pix = hp.query_disc(ns, cv0, np.radians(15))
    pv = np.array(hp.pix2vec(ns, pix)).T
    angs = np.degrees(np.arccos(np.clip(pv @ cv0, -1, 1)))
    vals = ms[pix]
    bins = np.linspace(0, 15, 150)
    idx = np.digitize(angs, bins[1:-1])
    prof = np.array([((bins[j]+bins[j+1])/2, np.mean(vals[idx==j])) for j in range(149) if (idx==j).sum() > 0])
    r, v = prof[:, 0], prof[:, 1]
    tgt = v[0]/2
    hr = np.nan
    for j in range(1, len(v)):
        if (v[j]-tgt)*(v[j-1]-tgt) <= 0:
            tt = (tgt - v[j-1])/(v[j]-v[j-1])
            hr = r[j-1] + tt*(r[j]-r[j-1])
            break
    hwhms.append(hr)
hwhms = np.array(hwhms)
sig2 = (np.array(scales_fit)/(2*math.sqrt(2*math.log(2))))**2
A = np.vstack([sig2, np.ones(5)]).T
coef, *_ = np.linalg.lstsq(A, hwhms**2, rcond=None)
intercept = coef[1]
hwhm_true_01 = math.sqrt(intercept)
dev01 = (hwhm_true_01 - r_pred)/r_pred*100
print(f"  0.1°bins: HWHM_true={hwhm_true_01:.4f}° (doc 4.138, 偏差 {dev01:+.2f}% vs doc +0.34%)")
check("去平滑 0.1°bins → 4.138", abs(hwhm_true_01 - 4.138) < 0.02, f"({hwhm_true_01:.4f})")

# 0.2° bins
hwhms2 = []
for s in scales_fit:
    ms = hp.remove_dipole(hp.read_map(os.path.join(CACHE, f"smica2_smooth{s}.fits"), field=0))
    ns = hp.get_nside(ms)
    pix = hp.query_disc(ns, cv0, np.radians(10))
    pv = np.array(hp.pix2vec(ns, pix)).T
    angs = np.degrees(np.arccos(np.clip(pv @ cv0, -1, 1)))
    vals = ms[pix]
    bins = np.linspace(0, 10, 51)
    idx = np.digitize(angs, bins[1:-1])
    prof = np.array([((bins[j]+bins[j+1])/2, np.mean(vals[idx==j])) for j in range(50) if (idx==j).sum() > 0])
    r, v = prof[:, 0], prof[:, 1]
    tgt = v[0]/2
    hr = np.nan
    for j in range(1, len(v)):
        if (v[j]-tgt)*(v[j-1]-tgt) <= 0:
            tt = (tgt - v[j-1])/(v[j]-v[j-1])
            hr = r[j-1] + tt*(r[j]-r[j-1])
            break
    hwhms2.append(hr)
hwhms2 = np.array(hwhms2)
A2 = np.vstack([sig2, np.ones(5)]).T
coef2, *_ = np.linalg.lstsq(A2, hwhms2**2, rcond=None)
hwhm_true_02 = math.sqrt(coef2[1])
dev02 = (hwhm_true_02 - r_pred)/r_pred*100
print(f"  0.2°bins: HWHM_true={hwhm_true_02:.4f}° (doc 4.1522, 偏差 {dev02:+.2f}% vs doc -0.01%)")
check("去平滑 0.2°bins → 4.1522", abs(hwhm_true_02 - 4.1522) < 0.02, f"({hwhm_true_02:.4f})")

# ===== 5. Gaussian 擬合 (02_results §3b) =====
print("\n[5] Gaussian 擬合 (3b)")
from scipy.optimize import curve_fit
ms = hp.remove_dipole(hp.read_map(os.path.join(CACHE, "smica2_smooth4.17.fits"), field=0))
ns = hp.get_nside(ms)
pix = hp.query_disc(ns, cv0, np.radians(12))
pv = np.array(hp.pix2vec(ns, pix)).T
angs = np.degrees(np.arccos(np.clip(pv @ cv0, -1, 1)))
vals = ms[pix]
bins = np.linspace(0, 12, 121)
idx = np.digitize(angs, bins[1:-1])
prof = np.array([((bins[j]+bins[j+1])/2, np.mean(vals[idx==j])) for j in range(120) if (idx==j).sum() > 0])
r, v = prof[:, 0], prof[:, 1]

def gauss(rr, A, sigma, B):
    return A*np.exp(-rr**2/(2*sigma**2)) + B

popt, _ = curve_fit(gauss, r, v, p0=[v[0]-v[-1], 3.0, v[-1]], maxfev=5000)
A_g, sig_g, B_g = popt
resid = v - gauss(r, *popt)
r2g = 1 - np.sum(resid**2)/np.sum((v-np.mean(v))**2)
check("Gaussian A=-148.7", abs(A_g*1e6 + 148.7) < 3, f"({A_g*1e6:.1f})")
check("Gaussian σ=4.452", abs(sig_g - 4.452) < 0.05, f"({sig_g:.3f})")
check("Gaussian B=+15.5", abs(B_g*1e6 - 15.5) < 2, f"({B_g*1e6:.1f})")
check("Gaussian R²=0.9958", abs(r2g - 0.9958) < 0.002, f"({r2g:.4f})")

# ===== 6. 星系團真空 (02_results §4) =====
print("\n[6] 星系團真空交叉")
r41 = 4.5/r_pred
r42 = 5.0/r_pred
check("PSZ1 4.5° → 1.084×", abs(r41 - 1.084) < 0.002, f"({r41:.3f})")
check("MCXC 5.0° → 1.204×", abs(r42 - 1.204) < 0.002, f"({r42:.3f})")

# ===== 7. ℓ 一致性 (02_results) =====
print("\n[7] ℓ 一致性")
ell = 180/r_pred
check("ℓ = 43.35", abs(ell - 43.35) < 0.05, f"({ell:.2f})")
check("ℓ ≈ 44 (-1.5%)", abs((ell-44)/44 + 0.015) < 0.005, f"({(ell/44-1)*100:.2f}%)")

# ===== 8. 26.09×44 vs 360π =====
print("\n[8] 26.09×44 vs 360π")
lhs = a_edge*44
rhs = 360*np.pi
check("26.09×44 = 1148", abs(lhs - 1148) < 2, f"({lhs:.0f})")
check("360π = 1131", abs(rhs - 1131) < 2, f"({rhs:.0f})")
check("差 1.5%", abs((lhs/rhs-1)*100 - 1.5) < 0.2, f"({(lhs/rhs-1)*100:.1f}%)")

# ===== 9. README + 01_problem_record 一致性 =====
print("\n[9] 跨文檔一致性 (README / 01_problem_record / 02_results)")
readme = open(os.path.join(BASE, "README.md")).read()
rec = open(os.path.join(BASE, "01_problem_record.md")).read()
res = open(os.path.join(BASE, "02_results.md")).read()

# 三個文檔都要有核心結論
for key in ["4.1526", "26.0913"]:
    check(f"README 含 {key}", key in readme)
    check(f"01_problem_record 含 {key}", key in rec)
    check(f"02_results 含 {key}", key in res)

# 冇矛盾: README 4.17, 01_rec 4.17, 02_res 4.17
check("README R8 4.17", "4.17" in readme)
check("01_rec R8 4.17", "4.17" in rec)

# 01_problem_record 嘅候選排除同 02_results 一致
check("01_rec 排除 180/44", "180/44" in rec and "4.09" in rec)
check("01_rec 排除 a×ε", "26.09×ε" in rec and "4.03" in rec)

# ===== 10. 驗證狀態 =====
print("\n[10] 驗證狀態 (01_problem_record + 02_results)")
check("01_rec 有 7/7", "7/7" in rec)
check("01_rec 有 23/23", "23/23" in rec)
check("01_rec 有 46/46", "46/46" in rec)
check("01_rec 有推導時序索引", "推導時序索引" in rec)
check("02_results 有 7/7", "7/7" in res)
check("02_results 有 23/23", "23/23" in res)

# ===== 11. final_result.md (RESULT_TEMPLATE 格式) =====
print("\n[11] final_result.md 核對")
fr_path = os.path.join(BASE, "final_result.md")
check("final_result.md 存在", os.path.exists(fr_path))
if os.path.exists(fr_path):
    fr = open(fr_path).read()
    check("狀態 🟢 已閉合", "🟢 已閉合" in fr)
    check("核心結論 4.1526", "4.1526" in fr)
    check("關鍵公式 λ/2π", "λ/2π" in fr)
    check("依賴鏈", "O8" in fr and "→" in fr)
    check("極簡 (≤25 行)", fr.count("\n") <= 25, f"({fr.count(chr(10))} 行)")
    # 同 02_results 核心數字一致
    for key in ["26.0913", "4.17", "4.152", "43.3", "44"]:
        check(f"final_result 含 {key}", key in fr)

# ===== 總結 =====
print("\n" + "="*72)
print(f"DOC_AUDIT: {len(passes)} PASS / {len(fails)} FAIL")
for f_ in fails:
    print(f"  ❌ {f_}")
print("="*72)

with open(os.path.join(BASE, "data/doc_audit.txt"), "w") as f:
    f.write(f"# O8 文檔完整性 + 數值獨立核對 (DOC_AUDIT)\n")
    f.write(f"# {len(passes)} PASS / {len(fails)} FAIL\n")
    for p in passes:
        f.write(f"# PASS: {p}\n")
    for fl in fails:
        f.write(f"# FAIL: {fl}\n")

print(f"\n{'🎉 全部 PASS' if not fails else '❌ 有 FAIL'}")
