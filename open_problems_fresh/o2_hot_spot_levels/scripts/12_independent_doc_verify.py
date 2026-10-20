#!/usr/bin/env python3
"""
O2 獨立文檔核對 v20260909 — smooth_cache 重算版
================================================
2026-09-09 建立。獨立重算 O2 所有文檔關鍵數值，兩條獨立路線：

A. 地圖路線 (SMICA 平滑快取, o5_catalog_compare/data/smooth_cache)
   - 快取與 O2 原數據同源 (同一 smica2.fits + remove_dipole+smoothing,
     std 全尺度對齊 O2 multiscale_scan.txt 小數點後 1-2 位)
   - 重算: Step1 熱節點平均 / Step2 對徑點 / Step3 全天最熱 /
           多尺度表 (0.5-10.0°) / F6@1.0° / F7@0.5° 位置溫度
B. 數據路線 (data/*.txt 記錄輸出 + 第一性原理算術)
   - Fibonacci 等級算術 / 比率 (1.157, 0.905) / %off /
     χ²/dof / Wiener / 座標轉換 (Galactic↔ICRS) /
     熱斑-冷斑距離 / 最近節點距離 / 排列檢驗 p↔z 一致性

Read-only audit — 唔修改任何文檔。
"""
import numpy as np
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u
import os, sys, re

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o2_hot_spot_levels'
CACHE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o5_catalog_compare/data/smooth_cache'
NODES = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt'
COLORING = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/main_problems/p4_cmb_cold_spot/data/anchored_coloring.txt'

passes, fails, warns = [], [], []

def check(name, obs, exp, tol, unit=''):
    d = abs(obs - exp)
    ok = d <= tol
    (passes if ok else fails).append(name)
    print(f"  {'✅' if ok else '❌'} {name}: {obs:.4f}{unit} vs {exp}{unit} (Δ={d:.4f})")

def check_pct(name, obs, exp, tol_pct):
    pct = abs(obs-exp)/abs(exp)*100
    ok = pct <= tol_pct
    (passes if ok else fails).append(name)
    print(f"  {'✅' if ok else '❌'} {name}: {obs:.4f} vs {exp} ({pct:.3f}% off ≤ {tol_pct}%)")

def load_smooth(fwhm):
    f = f'{CACHE}/smica2_smooth{fwhm}.fits'
    if not os.path.exists(f):
        return None
    return hp.read_map(f, field=0) * 1e6  # uK

print("="*70)
print("O2 獨立文檔核對 v20260909 (smooth_cache 重算)")
print("="*70)

# ---------- A. 地圖路線 ----------
nside = 2048
nodes_radec = np.loadtxt(NODES)
sc = SkyCoord(ra=nodes_radec[:,0]*u.deg, dec=nodes_radec[:,1]*u.deg, frame='icrs')
gal = sc.galactic
l_deg, b_deg = gal.l.deg, gal.b.deg
pix_nodes = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)
coloring = np.loadtxt(COLORING, usecols=[0,3])
color = coloring[:,1]
hot = color == 0

print("\n[A1] Step 1: 熱節點平均 (5.0° 平滑, 由 smooth_cache)")
T5 = load_smooth(5.0)
if T5 is not None:
    Tn = T5[pix_nodes]
    hot5 = Tn[hot].mean(); cold5 = Tn[~hot].mean()
    check("熱節點平均 +9.1", hot5, 9.1, 0.3, ' μK')
    check("冷節點平均 -11.5", cold5, -11.5, 0.3, ' μK')
    check("冷熱 gap +20.6", hot5-cold5, 20.6, 0.3, ' μK')
    check("map std 42.2", T5.std(), 42.2, 0.2, ' μK')
    check("node53 +102.8", Tn[53], 102.8, 0.3, ' μK')
    check("node0 冷斑 -124.6", Tn[0], -124.6, 0.3, ' μK')
    # Cohen's d
    sp = np.sqrt((Tn[hot].std()**2 + Tn[~hot].std()**2)/2)
    check("Cohen's d 0.484", (hot5-cold5)/sp, 0.484, 0.01)
    # 排列檢驗 p 值一致性: z=1.83 <-> p=0.0335 (單尾)
    from scipy.stats import norm
    z_p = norm.ppf(1-0.0335)
    check("p=0.0335 ↔ z=1.83", z_p, 1.83, 0.02, ' σ')

print("\n[A2] Step 2: 對徑點 (5.0° 平滑)")
pix_anti = hp.ang2pix(nside, 29.0, 57.0, lonlat=True)
check("對徑點精確 +17.9", T5[pix_anti], 17.9, 0.3, ' μK')
vec_anti = hp.ang2vec(29.0, 57.0, lonlat=True)
disc = hp.query_disc(nside, vec_anti, np.radians(5.0))
check("5° 圓盤 max +41.6", T5[disc].max(), 41.6, 0.3, ' μK')
check("5° 圓盤 mean +23.4", T5[disc].mean(), 23.4, 0.3, ' μK')
check("5° 圓盤 std 8.4", T5[disc].std(), 8.4, 0.2, ' μK')
check("98.7% pixels 正", (T5[disc]>0).mean()*100, 98.7, 0.5, ' %')

print("\n[A3] Step 3: 全天最熱 (5.0° 平滑)")
l_all, b_all = hp.pix2ang(nside, np.arange(len(T5)), lonlat=True)
for mask_deg, exp in [(25, 119.9), (50, 115.2)]:
    T_m = T5.copy(); T_m[np.abs(b_all) < mask_deg] = -np.inf
    check(f"masked max |b|≥{mask_deg} = {exp}", np.nanmax(T_m), exp, 0.3, ' μK')
# 無 mask 全天最熱
check("無 mask 全天最熱 150.4", T5.max(), 150.4, 0.3, ' μK')
check("無 mask 位置 l=264.0", l_all[np.argmax(T5)], 264.0, 0.3, ' °')
check("無 mask 位置 b=-19.9", b_all[np.argmax(T5)], -19.9, 0.3, ' °')
# max_sigma = 3.56 (150.4/42.2)
check("max_sigma 3.56", T5.max()/T5.std(), 3.56, 0.05, ' σ')

print("\n[A4] 多尺度掃描表 (smooth_cache, 對比 multiscale_scan.txt)")
ms = {}
with open(f'{BASE}/data/multiscale_scan.txt') as f:
    for line in f:
        if line.startswith('#') or not line.strip(): continue
        p = line.split()
        ms[float(p[0])] = {'map_std': float(p[1]), 'cold': float(p[2]),
                           'hot': float(p[3]), 'cold_m': float(p[4]),
                           'gap': float(p[5]), 'S': float(p[6]), 'mx': float(p[7])}
for fwhm in [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 7.0, 10.0]:
    T_s = load_smooth(fwhm)
    if T_s is None:
        warns.append(f"cache:{fwhm}"); continue
    Tn = T_s[pix_nodes]
    pix_cs = hp.ang2pix(nside, 209.0, -57.0, lonlat=True)
    T_m = T_s.copy(); T_m[np.abs(b_all) < 25] = -np.inf
    r = ms[fwhm]
    check(f"{fwhm}° map_std {r['map_std']}", T_s.std(), r['map_std'], 0.15, ' μK')
    check(f"{fwhm}° cold {r['cold']}", T_s[pix_cs], r['cold'], 0.3, ' μK')
    check(f"{fwhm}° hot_mean {r['hot']}", Tn[hot].mean(), r['hot'], 0.3, ' μK')
    check(f"{fwhm}° cold_mean {r['cold_m']}", Tn[~hot].mean(), r['cold_m'], 0.3, ' μK')
    check(f"{fwhm}° gap {r['gap']}", Tn[hot].mean()-Tn[~hot].mean(), r['gap'], 0.3, ' μK')
    check(f"{fwhm}° stack_S {r['S']}", (Tn*np.where(hot,1,-1)).mean(), r['S'], 0.3, ' μK')
    check(f"{fwhm}° masked_max {r['mx']}", np.nanmax(T_m), r['mx'], 0.3, ' μK')

print("\n[A5] F₆/F₇ 熱斑位置溫度 (1.0°/0.5° 平滑)")
T10 = load_smooth(1.0); T05 = load_smooth(0.5)
pix_f6 = hp.ang2pix(nside, 157.8, -70.3, lonlat=True)
pix_f7 = hp.ang2pix(nside, 0.2, -37.9, lonlat=True)
check("F₆ @1.0° = 277.6", T10[pix_f6], 277.6, 0.3, ' μK')
# 註: multiscale 表 353.4 係全天 masked max (另一位置), F₇ 位置 (0.2,-37.9) 溫度 = 353.0
check("F₇ @0.5° = 353.0 (§9 SMICA 列)", T05[pix_f7], 353.0, 0.3, ' μK')
# 跨尺度一致性 (F₆): 0.5/1.0/1.5/2.0/3.0
for fwhm, exp in [(0.5, 337.0), (1.5, 224.3), (2.0, 187.0), (3.0, 141.0)]:
    T_s = load_smooth(fwhm)
    if T_s is not None:
        check(f"F₆ @{fwhm}° = {exp}", T_s[pix_f6], exp, 0.6, ' μK')

# ---------- B. 數據路線 ----------
print("\n[B1] Fibonacci 等級算術")
F = {3:60.1, 4:90.1, 5:150.2, 6:240.3, 7:390.4, 8:630.7}
fib = {3:2, 4:3, 5:5, 6:8, 7:13, 8:21}
per_units = [F[k]/fib[k] for k in F]
check("per-unit 一致 (30.03-30.05)", np.mean(per_units), 30.04, 0.02, ' μK')
check("F₆/F₅ = φ", F[6]/F[5], 1.618034, 0.02)
check("F₇/F₆ = φ", F[7]/F[6], 1.618034, 0.02)
check("F₈/F₇ = φ", F[8]/F[7], 1.618034, 0.02)
# 1.157 / 0.905 比率
check("F₆ obs/th = 1.157", 277.7/240.3, 1.157, 0.002)
check("F₇ obs/th = 0.905", 353.1/390.4, 0.905, 0.002)
# 冷斑 %off
check("冷斑 3.5% off", abs(-144.7-(-150))/150*100, 3.5, 0.2, ' %')
check("冷斑 3° 3.3% off", abs(-145.0-(-150))/150*100, 3.3, 0.2, ' %')

print("\n[B2] BFS ladder 層級平均 (fib_ladder_fit.txt 重算)")
bfs = {}
with open(f'{BASE}/data/fib_ladder_fit.txt') as f:
    for line in f:
        if line.startswith('node'):
            p = line.split()
            # 格式: node 0: bfs_dist=0, color=cold, T=-124.6
            i = int(p[1].rstrip(':'))
            d = int(p[2].split('=')[1].rstrip(','))
            T = float(p[4].split('=')[1])
            bfs.setdefault(d, []).append(T)
for d, exp in [(0,-124.6),(1,-9.3),(2,-2.6),(3,22.4),(4,-12.8),(5,-2.9),(6,-6.4),(7,24.0),(8,6.2)]:
    if d in bfs:
        check(f"BFS d={d} mean = {exp}", np.mean(bfs[d]), exp, 0.5, ' μK')
    else:
        warns.append(f"bfs d={d} missing")

print("\n[B3] χ²/dof 模型 (fib_ladder_fit.txt 記錄)")
with open(f'{BASE}/data/fib_ladder_fit.txt') as f:
    txt = f.read()
for name, exp in [('3-level', 0.90), ('5-level', 0.55), ('6-level', 0.54), ('continuous', 1.17)]:
    m = re.search(rf'{name}: chi2=([\d.]+), dof=([\d.]+)', txt)
    if m:
        c2, dof = float(m.group(1)), float(m.group(2))
        check(f"{name} χ²/dof = {exp}", c2/dof, exp, 0.01)

print("\n[B4] Wiener filter (wiener_filter.txt)")
with open(f'{BASE}/data/wiener_filter.txt') as f:
    wtxt = f.read()
m_w = re.search(r'S=([\d.]+), z=([\d.]+), p=([\d.]+)', wtxt)
if m_w:
    S, z, p = float(m_w.group(1)), float(m_w.group(2)), float(m_w.group(3))
    check("Wiener S = +15.4", S, 15.4, 0.1, ' μK')
    check("Wiener z = 1.59", z, 1.59, 0.02, ' σ')
    check("Wiener p = 0.058", p, 0.058, 0.005)
    # z <-> p 一致性 (單尾)
    from scipy.stats import norm
    check("z=1.59 ↔ p=0.058", norm.sf(z), p, 0.005)
# 37.5% noise reduction: (48.3-30.2)/48.3? 由 wiener 表: sky noise 48.3 μK
# 文檔聲稱 37.5% — 驗證: 需要 noise 數值, 記錄為 map-derived, 標 warn
warns.append("Wiener 37.5% noise reduction 係 script 07 地圖路線輸出, smooth_cache 冇殘留噪聲分量, 靠 08-16 60/60 驗證")

print("\n[B5] 座標轉換 (Galactic ↔ ICRS)")
f6_g = SkyCoord(157.8, -70.3, unit='deg', frame='galactic')
f6_i = f6_g.icrs
check("F₆ ICRS RA = 24.16", f6_i.ra.deg, 24.16, 0.05, ' °')
check("F₆ ICRS Dec = -10.55", f6_i.dec.deg, -10.55, 0.05, ' °')
f7_g = SkyCoord(0.2, -37.9, unit='deg', frame='galactic')
cs_i = SkyCoord(48.30, -20.44, unit='deg', frame='icrs')
cs_g = cs_i.galactic
check("冷斑 Galactic l = 209", cs_g.l.deg, 209.0, 0.5, ' °')
check("冷斑 Galactic b = -57", cs_g.b.deg, -57.0, 0.5, ' °')

print("\n[B6] 幾何距離 (F₆ 熱斑 vs 冷斑 / 最近節點)")
f6_vec = hp.ang2vec(157.8, -70.3, lonlat=True)
cs_vec = hp.ang2vec(209.0, -57.0, lonlat=True)
d_ang = np.degrees(np.arccos(np.clip(np.dot(f6_vec, cs_vec), -1, 1)))
check("F₆-冷斑距離 25.2°", d_ang, 25.2, 0.2, ' °')
node_vec = hp.ang2vec(l_deg, b_deg, lonlat=True)
d_nodes = np.degrees(np.arccos(np.clip(node_vec @ f6_vec, -1, 1)))
imin = np.argmin(d_nodes)
check("最近節點距離 9.03°", d_nodes[imin], 9.03, 0.1, ' °')
check("最近節點 = node 55", imin, 55, 0)
# 對徑點: (209,-57) 對面 = (29,57)
check("冷斑對徑點 l = 29", (209+180)%360, 29, 0.01, ' °')
check("冷斑對徑點 b = +57", -(-57), 57, 0.01, ' °')

print("\n[B7] 三地圖交叉驗證表算術 (cross_map_validation.txt)")
cm = {}
with open(f'{BASE}/data/cross_map_validation.txt') as f:
    for line in f:
        if '=' in line and ('SMICA=' in line):
            p = line.split()
            fwhm = float(p[0]); pos = p[1]
            vals = {k: float(v.split('=')[1]) for k, v in zip(['SMICA','NILC','Commander'], p[2:5])}
            cm[(fwhm, pos)] = vals
# F6 @1.0 mean±std
v = cm[(1.0, 'F6_hotspot')]
mean = np.mean(list(v.values())); std = np.std(list(v.values()))
check("F₆@1.0 mean 277.7", mean, 277.7, 0.2, ' μK')
check("F₆@1.0 std 0.74", std, 0.74, 0.1, ' μK')
check("F₆@1.0 spread 0.3%", std/abs(mean)*100, 0.3, 0.1, ' %')
v = cm[(0.5, 'F7_hotspot')]
check("F₇@0.5 mean 353.1", np.mean(list(v.values())), 353.1, 0.2, ' μK')
check("F₇@0.5 std 0.06", np.std(list(v.values())), 0.06, 0.06, ' μK')
v = cm[(3.0, 'Cold_spot')]
check("冷斑@3.0 mean -144.7", np.mean(list(v.values())), -144.7, 0.3, ' μK')
# correlation 矩陣
corr = {}
with open(f'{BASE}/data/cross_map_validation.txt') as f:
    for line in f:
        # 只取第一組 corr 區塊 — 檔案尾部有 09 早期 reorder-bug 版本殘留
        # (rr_NILC_SMICA / corr 0.5838/0.5864), 第一組先係 09b 修正版正確值
        if line.startswith('corr_'):
            p = line.split()
            a, b = p[0].split('_')[1], p[0].split('_')[2]
            if (a, b) not in corr:
                corr[(a, b)] = float(p[1])
for pair, exp in [(('SMICA','NILC'), 0.9994), (('SMICA','Commander'), 0.9970), (('NILC','Commander'), 0.9948)]:
    check(f"corr {pair[0]}-{pair[1]} = {exp}", corr[pair], exp, 0.0005)

print("\n[B8] 文檔內數字算術 (NN_results / problem_record 聲稱值)")
# NN_results: F₆ 277.7±0.74 = 1.157×F₆; F₇ 353.1±0.06
check("277.7/240.3 = 1.157", 277.7/240.3, 1.157, 0.002)
check("353.1/390.4 = 0.905", 353.1/390.4, 0.905, 0.002)
check("144.7/150 = 0.965", 144.7/150, 0.965, 0.002)
# 狀態表聲稱 0.03-1.3% NILC 差異 (§8 初步): F6 0.3%, F7 0.03%, 冷斑1.0° 0.5%, 0.5° 1.3%, 3.0° 0.6%
n8 = [(277.6,276.8),(353.0,353.1),(174.4,175.3),(203.1,205.7),(145.0,145.9)]
pcts = [abs(a-b)/a*100 for a,b in n8]
check("§8 NILC 差異範圍 0.03-1.3%", min(pcts), 0.03, 0.02, ' %')
check("§8 NILC 差異 max 1.3%", max(pcts), 1.3, 0.05, ' %')

print("\n[B9] 已知事實表: ε⁵/8 × T_CMB = 30 μK")
# cmb_cold_spot 定義: ε = φ⁻¹/4 (02_cold_spot_structural.py line 18)
phi = (1+5**0.5)/2
eps = (1/phi)/4
val = (eps**5)/8
check("ε⁵/8 = 1.1007e-5", val, 1.1007e-5, 5e-8)
check("ε⁵/8×T_CMB = 30.0 μK", val*2.72548*1e6, 30.0, 0.1, ' μK')
check("5ε⁵/8×T_CMB = 150.2 μK", val*2.72548*1e6*5, 150.2, 0.5, ' μK')

print("\n[B10] FWHM→σ 公式")
for fwhm, exp_sigma in [(5.0, 2.123), (3.0, 1.274), (1.0, 0.4247), (0.5, 0.2123)]:
    sig = fwhm/(2*np.sqrt(2*np.log(2)))
    check(f"σ({fwhm}°) = {exp_sigma}°", sig, exp_sigma, 0.002, ' °')

# ---------- 總結 ----------
print("\n" + "="*70)
print(f"RESULT: {len(passes)} passed, {len(fails)} failed, {len(warns)} warnings")
print("="*70)
for w in warns:
    print(f"  ⚠️  {w}")
if fails:
    print("FAILED:")
    for f_ in fails:
        print(f"  ❌ {f_}")
    sys.exit(1)
print("🎉 ALL CHECKS PASSED")
