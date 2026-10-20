#!/usr/bin/env python3
"""
20_audit_independent.py — O3 全文檔獨立核對 (T1, 2026-09-09)
================================================================
第一輪 (2026-09-09): 157/157 PASS — 覆核 01-05 + README 全部數字 + 02_results 表格
第二輪 (2026-09-11): +段 O/P (對徑對三地圖 + 方向性 + 文檔完整性) → 183/183 PASS
五步審計輪第一階段: 獨立重算 01/02/03/04/05/06 + README 所有關鍵數字,
唔 import 原 scripts (無共享 bug)。數據源:
  - data/node_temps.txt + data/bfs_distances.txt (O3 存檔)
  - cmb_cold_spot/data/a5_nodes.txt + anchored_coloring.txt (節點座標/著色)
  - o5_catalog_compare/data/smooth_cache/ (同源 4.17° 平滑版, std 對齊驗證,
    代替已被清空嘅 /tmp 原圖 — O2 教訓: 先搵同源快取, 唔好即刻下載 2GB)

任何 FAIL → 先檢查 check 自身 (O148 分流), 唔好為 PASS 改文檔。
"""
import os, re, math
import numpy as np
from scipy import stats
from collections import Counter, deque, defaultdict

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
O3 = os.path.join(BASE, "o3_node_temperatures")
CACHE = os.path.join(BASE, "o5_catalog_compare/data/smooth_cache")

passes, fails = [], []

def check(name, cond, detail=""):
    if cond:
        passes.append(name)
        print(f"  [PASS] {name} {detail}")
    else:
        fails.append(name)
        print(f"  [FAIL] {name} {detail}")

# ============ A. 檔案存在 ============
print("=== A. 檔案存在 ===")
for f in ["01_problem_record.md", "02_results.md", "03_red_flag_galactic_plane.md",
          "04_high4_node45_study.md", "05_hallucination_check_report.md",
          "README.md", "SESSION_START.md", "data/node_temps.txt",
          "data/bfs_distances.txt", "figs/01_temp_hist.png",
          "figs/02_coldhot_box.png", "figs/03_temp_vs_bfs.png"]:
    check(f"存在 {f}", os.path.exists(os.path.join(O3, f)))
# 實際列 scripts 檔案名
scripts_dir = os.path.join(O3, "scripts")
script_names = sorted(os.listdir(scripts_dir))
for i in range(1, 20):
    check(f"script {i:02d}", any(s.startswith(f"{i:02d}_") and s.endswith(".py") for s in script_names))
py_scripts = [s for s in script_names if s.endswith(".py") and not s.startswith(("20_", "21_", "22_"))]
check("scripts 19 個 .py (excl audit)", len(py_scripts) == 19, f"got {len(py_scripts)}")
check("13b DEPRECATED 存在", os.path.exists(os.path.join(scripts_dir, "13b_node45_multiscale_fast.py.DEPRECATED")))

# ============ B. 節點資料完整性 ============
print("\n=== B. 節點資料 ===")
rows = []
with open(os.path.join(O3, "data/node_temps.txt")) as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        p = line.split()
        rows.append((int(p[0]), int(p[1]), float(p[2]), float(p[3]), float(p[4]), int(p[5])))
check("node_temps 60 行", len(rows) == 60, f"got {len(rows)}")
T = np.array([r[2] for r in rows]); color = np.array([r[1] for r in rows])
l_deg = np.array([r[3] for r in rows]); b_deg = np.array([r[4] for r in rows])
hop = np.array([r[5] for r in rows])
check("idx 連續 0-59", list(range(60)) == [r[0] for r in rows])

# 著色 vs anchored_coloring
col_anch = {}
with open(os.path.join(BASE, "cmb_cold_spot/data/anchored_coloring.txt")) as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        parts = line.split()
        col_anch[int(parts[0])] = int(parts[3])
check("著色 30 冷 30 熱", sum(1 for c in col_anch.values() if c == 1) == 30)
check("著色完全一致", all(color[i] == col_anch.get(i) for i in range(60)))

# ============ C. 同源快取重抽 vs node_temps.txt ============
print("\n=== C. 同源平滑 cache 重抽 (4.17°) ===")
try:
    import healpy as hp
    from astropy.coordinates import SkyCoord
    import astropy.units as u
    nodes = []
    with open(os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")) as f:
        for line in f:
            ra, dec = map(float, line.split())
            nodes.append((ra, dec))
    nodes = np.array(nodes)
    sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
    gal = sc.galactic
    nside = 2048
    pix = hp.ang2pix(nside, gal.l.deg, gal.b.deg, lonlat=True)

    # 同源驗證: cache std 對齊
    for name, fn, exp_std in [("SMICA", "smica2_smooth4.17.fits", 44.3),
                              ("NILC", "nilc2_smooth4.17.fits", 44.24),
                              ("Commander", "commander_smooth4.17.fits", 45.03)]:
        m = hp.read_map(os.path.join(CACHE, fn), field=0)
        s = m.std() * 1e6
        check(f"cache {name} std~{exp_std}", abs(s - exp_std) < 0.3, f"got {s:.2f}")

    m = hp.read_map(os.path.join(CACHE, "smica2_smooth4.17.fits"), field=0)
    T_audit = m[pix] * 1e6
    d = np.abs(T_audit - T)
    check("SMICA 重抽 vs 存檔 max|d|<0.0001", d.max() < 0.0001, f"max={d.max():.6f}")
    check("node0 -134.1893", abs(T_audit[0] + 134.1893) < 0.001, f"got {T_audit[0]:.4f}")
    check("node47 -123.3967", abs(T_audit[47] + 123.3967) < 0.001, f"got {T_audit[47]:.4f}")
    check("node53 +111.9971", abs(T_audit[53] - 111.9971) < 0.001, f"got {T_audit[53]:.4f}")
    check("node57 +8.2073", abs(T_audit[57] - 8.2073) < 0.001, f"got {T_audit[57]:.4f}")

    # 高緯度 4 節點三地圖 (04 報告 §2.6)
    HIGH4 = [10, 22, 25, 32]
    others_high = [i for i in range(60) if abs(b_deg[i]) >= 20 and i not in HIGH4]
    check("高緯其他 34", len(others_high) == 34, f"got {len(others_high)}")
    ratios = {}
    for name, fn, exp in [("SMICA", "smica2_smooth4.17.fits", 0.375),
                          ("NILC", "nilc2_smooth4.17.fits", 0.416),
                          ("Commander", "commander_smooth4.17.fits", 0.372)]:
        mm = hp.read_map(os.path.join(CACHE, fn), field=0)
        Tv = mm[pix] * 1e6
        r = np.abs(Tv[HIGH4]).mean() / np.abs(Tv[others_high]).mean()
        ratios[name] = r
        check(f"{name} 比例 {exp}", abs(r - exp) < 0.005, f"got {r:.3f}")

    # Node 45 三地圖 (04 §1.1)
    for name, fn, exp in [("SMICA", "smica2_smooth4.17.fits", 1.57),
                          ("NILC", "nilc2_smooth4.17.fits", 2.76),
                          ("Commander", "commander_smooth4.17.fits", 1.19)]:
        mm = hp.read_map(os.path.join(CACHE, fn), field=0)
        v = mm[pix][45] * 1e6
        check(f"node45 {name} {exp}", abs(v - exp) < 0.1, f"got {v:.2f}")

    # spread
    vals = {}
    for name, fn in [("SMICA", "smica2_smooth4.17.fits"),
                     ("NILC", "nilc2_smooth4.17.fits"),
                     ("Commander", "commander_smooth4.17.fits")]:
        mm = hp.read_map(os.path.join(CACHE, fn), field=0)
        vals[name] = mm[pix] * 1e6
    spread45 = max(abs(vals['SMICA'][45]-vals['NILC'][45]),
                   abs(vals['SMICA'][45]-vals['Commander'][45]),
                   abs(vals['NILC'][45]-vals['Commander'][45]))
    check("node45 spread 1.57", abs(spread45 - 1.57) < 0.1, f"got {spread45:.2f}")
    spreads = np.array([max(abs(vals['SMICA'][i]-vals['NILC'][i]),
                            abs(vals['SMICA'][i]-vals['Commander'][i]),
                            abs(vals['NILC'][i]-vals['Commander'][i])) for i in range(60)])
    check("全60 spread mean 3.27", abs(spreads.mean() - 3.27) < 0.1, f"got {spreads.mean():.2f}")
    check("全60 spread max 15.42", abs(spreads.max() - 15.42) < 0.1, f"got {spreads.max():.2f}")
    pct45 = (spreads < spreads[45]).mean() * 100
    check("node45 25 百分位", abs(pct45 - 25) < 5, f"got {pct45:.0f}%")

    # 多尺度 (04 §2.5 SMICA 高緯 4 節點比例)
    ms_table = {1.0: 0.886, 2.0: 0.722, 3.0: 0.509, 4.0: 0.379, 4.17: 0.375,
                5.0: 0.352, 7.0: 0.443, 10.0: 0.613}
    for scale, exp in ms_table.items():
        fn = f"smica2_smooth{scale:.1f}.fits" if scale != 4.17 else "smica2_smooth4.17.fits"
        fp = os.path.join(CACHE, fn)
        if not os.path.exists(fp):
            check(f"多尺度 {scale}° 檔案存在", False, f"missing {fn}")
            continue
        mm = hp.read_map(fp, field=0)
        Tv = mm[pix] * 1e6
        r = np.abs(Tv[HIGH4]).mean() / np.abs(Tv[others_high]).mean()
        check(f"SMICA {scale}° 比例 {exp}", abs(r - exp) < 0.02, f"got {r:.3f}")

    # Node 45 多尺度 (04 §1.2 SMICA)
    n45_ms = {0.5: 0.30, 1.0: 44.78, 1.5: 60.99, 2.0: 55.43, 3.0: 27.90,
              4.0: 4.67, 4.17: 1.57, 5.0: -10.33, 7.0: -23.99, 10.0: -28.04}
    for scale, exp in n45_ms.items():
        fn = f"smica2_smooth{scale:.1f}.fits" if scale != 4.17 else "smica2_smooth4.17.fits"
        fp = os.path.join(CACHE, fn)
        if not os.path.exists(fp):
            check(f"node45 多尺度 {scale}° 檔案", False, f"missing {fn}")
            continue
        mm = hp.read_map(fp, field=0)
        v = mm[pix][45] * 1e6
        check(f"node45 SMICA {scale}° {exp}", abs(v - exp) < 1.0, f"got {v:.2f}")
except ImportError as e:
    check("healpy/astropy 可用", False, str(e))

# ============ D. 分佈統計 (02_results §1) ============
print("\n=== D. 分佈統計 ===")
check("mean -1.25", abs(T.mean() - (-1.25)) < 0.05, f"got {T.mean():.2f}")
check("std 46.19", abs(T.std(ddof=1) - 46.19) < 0.05, f"got {T.std(ddof=1):.2f}")
check("min -134.19 @0", abs(T.min() + 134.19) < 0.05 and np.argmin(T) == 0, f"got {T.min():.2f}@{np.argmin(T)}")
check("max +112.00 @53", abs(T.max() - 112.00) < 0.05 and np.argmax(T) == 53, f"got {T.max():.2f}@{np.argmax(T)}")
check("median +1.44", abs(np.median(T) - 1.44) < 0.05, f"got {np.median(T):.2f}")

# K-S vs 高斯 (節點自身 mean/std)
cdf_self = stats.norm(loc=T.mean(), scale=T.std(ddof=1)).cdf
ks = stats.kstest(T, cdf_self)
check("K-S 自身 D=0.1035", abs(ks.statistic - 0.1035) < 0.002, f"got {ks.statistic:.4f}")
check("K-S 自身 p=0.509", abs(ks.pvalue - 0.509) < 0.03, f"got {ks.pvalue:.3f}")
# K-S vs 全圖 std (44.3)
cdf_map = stats.norm(loc=0.0, scale=44.3).cdf
ks2 = stats.kstest(T, cdf_map)
check("K-S 全圖 D=0.0857", abs(ks2.statistic - 0.0857) < 0.002, f"got {ks2.statistic:.4f}")
check("K-S 全圖 p=0.738", abs(ks2.pvalue - 0.738) < 0.03, f"got {ks2.pvalue:.3f}")
# A-D
ad = stats.anderson(T, dist='norm')
check("A-D 0.875", abs(ad.statistic - 0.875) < 0.02, f"got {ad.statistic:.4f}")
check("skew -0.468", abs(stats.skew(T) + 0.468) < 0.01, f"got {stats.skew(T):.3f}")
check("kurt +1.216", abs(stats.kurtosis(T) - 1.216) < 0.01, f"got {stats.kurtosis(T):.3f}")

# ============ E. 冷熱分離 (02_results §2) ============
print("\n=== E. 冷熱分離 ===")
Tc = T[color == 1]; Th = T[color == 0]
check("冷色 mean -12.41", abs(Tc.mean() + 12.41) < 0.05, f"got {Tc.mean():.2f}")
check("熱色 mean +9.91", abs(Th.mean() - 9.91) < 0.05, f"got {Th.mean():.2f}")
d = Tc.mean() - Th.mean()
check("冷熱差 -22.31", abs(d + 22.31) < 0.05, f"got {d:.2f}")
tt = stats.ttest_ind(Tc, Th, equal_var=False)
check("Welch p=0.061", abs(tt.pvalue - 0.061) < 0.01, f"got {tt.pvalue:.3f}")
mw = stats.mannwhitneyu(Tc, Th, alternative='two-sided')
check("Mann-Whitney p=0.066", abs(mw.pvalue - 0.066) < 0.01, f"got {mw.pvalue:.3f}")

# Bootstrap 95% CI (seed 42, 100k)
rng = np.random.default_rng(42)
n_boot = 100_000
allT = np.concatenate([Tc, Th])
diffs = np.empty(n_boot)
for k in range(n_boot):
    idx = rng.choice(60, 60, replace=True)
    diffs[k] = allT[idx][:30].mean() - allT[idx][30:].mean()
ci = np.percentile(diffs, [2.5, 97.5])
check("Bootstrap CI [-23.2,+23.3]", abs(ci[0] + 23.2) < 1.0 and abs(ci[1] - 23.3) < 1.0, f"got [{ci[0]:.1f},{ci[1]:.1f}]")

# 排列檢驗 (seed 42, 20k)
diffs0 = np.empty(20000)
for k in range(20000):
    idx = rng.permutation(60)
    diffs0[k] = allT[idx[:30]].mean() - allT[idx[30:]].mean()
p_perm = (np.abs(diffs0) >= np.abs(d)).mean()
check("排列 p=0.061", abs(p_perm - 0.061) < 0.01, f"got {p_perm:.3f}")

# 剔除銀河盤後
keep = np.abs(b_deg) >= 20
Tc2, Th2 = T[(color == 1) & keep], T[(color == 0) & keep]
d2 = Tc2.mean() - Th2.mean()
tt2 = stats.ttest_ind(Tc2, Th2, equal_var=False)
check("剔除銀河差 -17.3", abs(d2 + 17.3) < 0.5, f"got {d2:.2f}")
check("剔除銀河 p=0.239", abs(tt2.pvalue - 0.239) < 0.03, f"got {tt2.pvalue:.3f}")

# ============ F. 極端值 vs 隨機 (02_results §3, seed 123 2000組) ============
print("\n=== F. 極端值 vs 隨機 (2000 組) ===")
# 用同源 cache 做 map_vals (|b|>20 像素)
try:
    m_smooth = hp.read_map(os.path.join(CACHE, "smica2_smooth4.17.fits"), field=0)
    theta, phi = hp.pix2ang(nside, np.arange(len(m_smooth)), lonlat=True)
    gal_mask = np.abs(phi) < 20
    pix_ok = np.where(~gal_mask)[0]
    map_vals = m_smooth[pix_ok] * 1e6
    rng3 = np.random.default_rng(123)
    N = 2000
    rand_min = np.empty(N); rand_max = np.empty(N); rand_std = np.empty(N)
    rand_coldhot = np.empty(N)
    for k in range(N):
        idx = rng3.choice(len(pix_ok), 60, replace=False)
        samp = map_vals[idx]
        rand_min[k] = samp.min(); rand_max[k] = samp.max(); rand_std[k] = samp.std(ddof=1)
        perm = rng3.permutation(60)
        rand_coldhot[k] = samp[perm[:30]].mean() - samp[perm[30:]].mean()
    obs_min = T.min()
    p_colder = (rand_min > obs_min).mean()
    z_min = (obs_min - rand_min.mean()) / rand_min.std()
    check("最冷 98.2% 更冷", abs(p_colder - 0.982) < 0.02, f"got {p_colder*100:.1f}%")
    check("最冷 z=-1.98", abs(z_min + 1.98) < 0.1, f"got {z_min:.2f}")
    obs_max = T.max()
    p_hotter = (rand_max < obs_max).mean()
    z_max = (obs_max - rand_max.mean()) / rand_max.std()
    check("最熱 90.2% 更熱", abs(p_hotter - 0.902) < 0.02, f"got {p_hotter*100:.1f}%")
    check("最熱 z=+1.27", abs(z_max - 1.27) < 0.1, f"got {z_max:.2f}")
    obs_std = T.std(ddof=1)
    p_std = (rand_std < obs_std).mean()
    z_std = (obs_std - rand_std.mean()) / rand_std.std()
    check("std 91.8% 更大", abs(p_std - 0.918) < 0.02, f"got {p_std*100:.1f}%")
    check("std z=1.42", abs(z_std - 1.42) < 0.1, f"got {z_std:.2f}")
    obs_d = d
    p_d = (np.abs(rand_coldhot) >= np.abs(obs_d)).mean()
    check("冷熱差 3.4%", abs(p_d - 0.034) < 0.01, f"got {p_d*100:.1f}%")
    joint = (rand_min > obs_min) & (rand_max < obs_max)
    check("雙極端 88.8%", abs(joint.mean() - 0.888) < 0.02, f"got {joint.mean()*100:.1f}%")
except Exception as e:
    check("極端值隨機對照可運行", False, str(e))

# ============ G. BFS ladder (02_results §4) ============
print("\n=== G. BFS ladder ===")
rho, p_sp = stats.spearmanr(T, hop)
check("Spearman T vs hop rho=-0.05", abs(rho + 0.05) < 0.02, f"got {rho:.3f}")
check("Spearman p=0.71", abs(p_sp - 0.71) < 0.05, f"got {p_sp:.2f}")
rho2, p2 = stats.spearmanr(np.abs(T), hop)
check("|T| vs hop rho=-0.224", abs(rho2 + 0.224) < 0.02, f"got {rho2:.3f}")
check("|T| vs hop p=0.085", abs(p2 - 0.085) < 0.02, f"got {p2:.3f}")
# BFS 層平均
layer_means = [T[hop == d].mean() for d in range(9)]
exp_layers = [-134.2, -10.4, -3.8, 24.1, -14.2, -1.9, -5.7, 23.7, 8.2]
ok_layers = all(abs(lm - el) < 0.3 for lm, el in zip(layer_means, exp_layers))
check("層平均 d0..d8", ok_layers, f"got {[round(x,1) for x in layer_means]}")

# ============ H. 匹配率 + 節點57 (02_results §5) ============
print("\n=== H. 匹配率 ===")
match = ((color == 1) & (T < 0)) | ((color == 0) & (T > 0))
check("匹配率 61.7%", abs(match.mean() - 0.617) < 0.01, f"got {match.mean():.3f}")
cold_pos = ((color == 1) & (T > 0)).sum()
hot_neg = ((color == 0) & (T < 0)).sum()
check("12 冷正 + 11 熱負", cold_pos == 12 and hot_neg == 11, f"got {cold_pos}+{hot_neg}")
check("node57 +8.21", abs(T[57] - 8.21) < 0.05, f"got {T[57]:.2f}")
p_binom = stats.binomtest(match.sum(), 60, 0.5).pvalue
check("Binomial p=0.09", abs(p_binom - 0.09) < 0.02, f"got {p_binom:.3f}")

# ============ I. ΔE=0 12 節點 (02_results §6, 08 script) ============
print("\n=== I. ΔE=0 12 節點 ===")
ZERO_E = {10, 12, 19, 22, 23, 25, 28, 32, 37, 40, 45, 46}
zero_mask = np.array([i in ZERO_E for i in range(60)])
Tz = T[zero_mask]; To = T[~zero_mask]
check("12 節點 mean|T| 19.05", abs(np.abs(Tz).mean() - 19.05) < 0.1, f"got {np.abs(Tz).mean():.2f}")
check("其他 48 mean|T| 36.18", abs(np.abs(To).mean() - 36.18) < 0.1, f"got {np.abs(To).mean():.2f}")
ratio12 = np.abs(Tz).mean() / np.abs(To).mean()
check("比例 0.526", abs(ratio12 - 0.526) < 0.005, f"got {ratio12:.3f}")
# Permutation (seed 99, 20k)
rng = np.random.default_rng(99)
allT_abs = np.abs(T)
obs = allT_abs[zero_mask].mean()
cnt = 0
for k in range(20000):
    idx = rng.choice(60, 12, replace=False)
    if allT_abs[idx].mean() <= obs:
        cnt += 1
p_perm12 = (cnt + 1) / (20000 + 1)
check("Permutation p=0.038", abs(p_perm12 - 0.038) < 0.01, f"got {p_perm12:.4f}")
t0, p0 = stats.ttest_1samp(Tz, 0)
check("t-test vs 0 p=0.395", abs(p0 - 0.395) < 0.03, f"got {p0:.3f}")
# bootstrap z (seed 99, 10k)
n_boot = 10000
boot_means = np.empty(n_boot)
for k in range(n_boot):
    idx = rng.choice(60, 12, replace=False)
    boot_means[k] = allT_abs[idx].mean()
z12 = (obs - boot_means.mean()) / boot_means.std()
check("Bootstrap z=-1.64", abs(z12 + 1.64) < 0.1, f"got {z12:.2f}")
check("node45 +1.57", abs(T[45] - 1.57) < 0.05, f"got {T[45]:.2f}")
check("|T|<15 7/12", (np.abs(Tz) < 15).sum() == 7, f"got {(np.abs(Tz) < 15).sum()}")

# ============ J. 紅燈 1 破解 (03 報告) ============
print("\n=== J. 紅燈 1: 中間層效應 ===")
gal_mask_arr = np.abs(b_deg) < 20
mid = (hop >= 3) & (hop <= 5)
mid_gal = (mid & gal_mask_arr).sum()
mid_sum = mid.sum()
check("k=2 全部 d3-d5", all(hop[i] in (3, 4, 5) for i in ZERO_E), f"hop={sorted(hop[i] for i in ZERO_E)}")
check("中間層銀河盤 18/34", mid_gal == 18 and mid_sum == 34, f"got {mid_gal}/{mid_sum}")
ze_gal = (zero_mask & gal_mask_arr).sum()
check("ΔE=0 銀河盤 8/12", ze_gal == 8, f"got {ze_gal}")
exp_cond = 12 * mid_gal / mid_sum
check("條件期望 6.35", abs(exp_cond - 6.35) < 0.1, f"got {exp_cond:.2f}")
p_cond = stats.binomtest(8, 12, mid_gal / mid_sum).pvalue
check("條件 p=0.40", abs(p_cond - 0.40) < 0.05, f"got {p_cond:.3f}")

# 2×2 表 (03 紅燈 3)
gl = gal_mask_arr
ze = zero_mask
sub_gl = ze & gl
oth_gl = ~ze & gl
sub_hi = ze & ~gl
oth_hi = ~ze & ~gl
check("銀河盤 8 vs 14", sub_gl.sum() == 8 and oth_gl.sum() == 14, f"got {sub_gl.sum()}/{oth_gl.sum()}")
check("高緯 4 vs 34", sub_hi.sum() == 4 and oth_hi.sum() == 34, f"got {sub_hi.sum()}/{oth_hi.sum()}")
m_gl = np.abs(T[sub_gl]).mean(); o_gl = np.abs(T[oth_gl]).mean()
check("銀河盤 22.34 vs 43.38", abs(m_gl - 22.34) < 0.1 and abs(o_gl - 43.38) < 0.1,
      f"got {m_gl:.2f}/{o_gl:.2f}")
tt_gl = stats.ttest_ind(np.abs(T[sub_gl]), np.abs(T[oth_gl]), equal_var=False)
check("銀河盤 Welch p=0.105", abs(tt_gl.pvalue - 0.105) < 0.02, f"got {tt_gl.pvalue:.3f}")
m_hi = np.abs(T[sub_hi]).mean(); o_hi = np.abs(T[oth_hi]).mean()
check("高緯 12.45 vs 33.21", abs(m_hi - 12.45) < 0.05 and abs(o_hi - 33.21) < 0.05,
      f"got {m_hi:.2f}/{o_hi:.2f}")
tt_hi = stats.ttest_ind(np.abs(T[sub_hi]), np.abs(T[oth_hi]), equal_var=False)
check("高緯 Welch p=0.0074", abs(tt_hi.pvalue - 0.0074) < 0.002, f"got {tt_hi.pvalue:.4f}")

# 紅燈 4: 銀河盤整體
check("銀河盤全部 22 mean|T| 35.73", abs(np.abs(T[gl]).mean() - 35.73) < 0.1, f"got {np.abs(T[gl]).mean():.2f}")
check("高緯全部 38 mean|T| 31.02", abs(np.abs(T[~gl]).mean() - 31.02) < 0.1, f"got {np.abs(T[~gl]).mean():.2f}")

# ============ K. 高緯度 4 節點 (04 報告) ============
print("\n=== K. 高緯度 4 節點 ===")
check("node10 -11.68", abs(T[10] + 11.68) < 0.05, f"got {T[10]:.2f}")
check("node22 -23.63", abs(T[22] + 23.63) < 0.05, f"got {T[22]:.2f}")
check("node25 +10.35", abs(T[25] - 10.35) < 0.05, f"got {T[25]:.2f}")
check("node32 -4.13", abs(T[32] + 4.13) < 0.05, f"got {T[32]:.2f}")
check("4 節點 mean|T| 12.45", abs(np.abs(T[HIGH4]).mean() - 12.45) < 0.05, f"got {np.abs(T[HIGH4]).mean():.2f}")
check("其他 34 mean|T| 33.21", abs(np.abs(T[others_high]).mean() - 33.21) < 0.05, f"got {np.abs(T[others_high]).mean():.2f}")
check("比例 0.375", abs(np.abs(T[HIGH4]).mean() / np.abs(T[others_high]).mean() - 0.375) < 0.005,
      f"got {np.abs(T[HIGH4]).mean()/np.abs(T[others_high]).mean():.3f}")
# 對徑對
vecs = np.array([[math.cos(math.radians(n[1]))*math.cos(math.radians(n[0])),
                  math.cos(math.radians(n[1]))*math.sin(math.radians(n[0])),
                  math.sin(math.radians(n[1]))] for n in nodes])
def ang(i, j):
    return math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
a10_25 = ang(10, 25); a22_32 = ang(22, 32)
check("10<->25 174.66", abs(a10_25 - 174.66) < 0.01, f"got {a10_25:.2f}")
check("22<->32 174.66", abs(a22_32 - 174.66) < 0.01, f"got {a22_32:.2f}")
check("10<->32 31.68", abs(ang(10, 32) - 31.68) < 0.05, f"got {ang(10,32):.2f}")
check("22<->25 42.11", abs(ang(22, 25) - 42.11) < 0.05, f"got {ang(22,25):.2f}")

# ============ L. 對徑對全體 (05 報告) ============
print("\n=== L. 對徑對 ===")
pairs = []
for i in range(60):
    for j in range(i+1, 60):
        a = ang(i, j)
        if a > 170:
            pairs.append((i, j, a))
check("30 對 >170°", len(pairs) == 30, f"got {len(pairs)}")
check("全部同色", all(color[i] == color[j] for i, j, _ in pairs))
check("全部 hop 和=8", all(hop[i] + hop[j] == 8 for i, j, _ in pairs))
check("全部 174.66°", all(abs(a - 174.66) < 0.01 for _, _, a in pairs))
hop_pairs = Counter((min(hop[i], hop[j]), max(hop[i], hop[j])) for i, j, _ in pairs)
check("分佈 d0d8=1 d1d7=4 d2d6=8 d3d5=11 d4d4=6",
      hop_pairs[(0,8)] == 1 and hop_pairs[(1,7)] == 4 and hop_pairs[(2,6)] == 8
      and hop_pairs[(3,5)] == 11 and hop_pairs[(4,4)] == 6, f"got {dict(hop_pairs)}")

# ============ M. 02_results.md 完整 60 節點表 (T2 目標) ============
print("\n=== M. 02_results.md 完整表格逐 node 核對 ===")
lines = open(os.path.join(O3, "02_results.md")).read().split('\n')
in_tab = False
doc_rows = {}
for ln in lines:
    if ln.startswith('| idx'):
        in_tab = True
        continue
    if in_tab:
        if re.match(r'\| (\d+) \|', ln):
            parts = [p.strip() for p in ln.split('|')[1:-1] if p.strip()]
            for off in range(0, len(parts) - 3, 4):
                i = parts[off]
                if i.isdigit():
                    tval = float(parts[off+2].replace('**', ''))
                    doc_rows[int(i)] = (parts[off+1], tval, int(parts[off+3]))
        elif '完整數據' in ln:
            in_tab = False
check("02_results 表 60 行", len(doc_rows) == 60, f"got {len(doc_rows)}")
t_bad = []
hop_bad = []
for i in range(60):
    dc = doc_rows.get(i)
    if dc is None:
        continue
    if abs(dc[1] - T[i]) > 0.01:
        t_bad.append((i, dc[1], T[i]))
    if dc[2] != hop[i]:
        hop_bad.append((i, dc[2], hop[i]))
print(f"  表 T 錯 {len(t_bad)} 個: {[(i, doc_rows[i][1], round(T[i],2)) for i,_,_ in t_bad]}")
print(f"  表 hop 錯 {len(hop_bad)} 個: {[(i, doc_rows[i][2], int(hop[i])) for i,_,_ in hop_bad]}")
check("02_results 表格 T 全對", len(t_bad) == 0, f"{len(t_bad)} 個錯 (需修正)")
check("02_results 表格 hop 全對", len(hop_bad) == 0, f"{len(hop_bad)} 個錯 (需修正)")

# ============ N. 01_problem_record 狀態表 ============
print("\n=== N. 01_problem_record 狀態表 ===")
check("record mean=-1.25", "mean=-1.25" in open(os.path.join(O3, "01_problem_record.md")).read())
check("record std=46.19", "46.19" in open(os.path.join(O3, "01_problem_record.md")).read())
check("record node47 -123.40", "-123.40" in open(os.path.join(O3, "01_problem_record.md")).read())
check("record node53 +112.00", "+112.00" in open(os.path.join(O3, "01_problem_record.md")).read())
check("record node57 +8.21", "+8.21" in open(os.path.join(O3, "01_problem_record.md")).read())

# ============ O. 對徑對三地圖溫度差 (22 script 驗證) ============
print("\n=== O. 對徑對三地圖溫度差 (22_antipodal_temp_check) ===")
T3 = {}
import healpy as hp3
from astropy.coordinates import SkyCoord as SC3
import astropy.units as u3
_nodes3 = np.array([tuple(map(float, ln.split())) for ln in open(os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")) if ln.strip()])
_sc3 = SC3(ra=_nodes3[:, 0]*u3.deg, dec=_nodes3[:, 1]*u3.deg, frame='icrs')
_pix3 = hp3.ang2pix(2048, _sc3.galactic.l.deg, _sc3.galactic.b.deg, lonlat=True)
for nm, f in [("SMICA", "smica2_smooth4.17.fits"), ("NILC", "nilc2_smooth4.17.fits"), ("Commander", "commander_smooth4.17.fits")]:
    m3 = hp3.read_map(os.path.join(CACHE, f), field=0)
    T3[nm] = m3[_pix3] * 1e6  # 全精度 astropy 座標 (NSIDE 2048), 獨立於 C 段
check("三地圖 SMICA 同源", np.abs(T3["SMICA"] - T).max() < 0.001, f"max|d|={np.abs(T3['SMICA']-T).max():.6f}")
pairs30 = []
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) > 170:
            pairs30.append((i, j))
check("對徑對 30 對", len(pairs30) == 30, f"got {len(pairs30)}")
exp10 = {"SMICA": 22.03, "NILC": 21.69, "Commander": 21.97}
exp22 = {"SMICA": 19.50, "NILC": 16.96, "Commander": 18.84}
for nm in ["SMICA", "NILC", "Commander"]:
    d10 = abs(T3[nm][10] - T3[nm][25]); d22 = abs(T3[nm][22] - T3[nm][32])
    check(f"(10,25)|dT| {nm}", abs(d10 - exp10[nm]) < 0.15, f"got {d10:.2f}")
    check(f"(22,32)|dT| {nm}", abs(d22 - exp22[nm]) < 0.15, f"got {d22:.2f}")
for nm in ["SMICA", "NILC", "Commander"]:
    dts = sorted([abs(T3[nm][i] - T3[nm][j]) for i, j in pairs30])
    r10 = dts.index(abs(T3[nm][10] - T3[nm][25])) + 1
    r22 = dts.index(abs(T3[nm][22] - T3[nm][32])) + 1
    check(f"排名 {nm}", r10 == 10 and r22 == 9, f"got {r10}/{r22}")
    mdt = np.mean([abs(T3[nm][i] - T3[nm][j]) for i, j in pairs30])
    exp_m = {"SMICA": 55.99, "NILC": 55.61, "Commander": 56.11}[nm]
    check(f"30 對 mean|dT| {nm}", abs(mdt - exp_m) < 0.1, f"got {mdt:.2f}")

# ============ P. 方向性 + 文檔完整性 (22 script / 04 待辦 / 06 報告) ============
print("\n=== P. 方向性 + 文檔完整性 ===")
v0v = vecs[0]
angs_all = []
for i, j in pairs30:
    axv = vecs[i] + vecs[j]; axv /= np.linalg.norm(axv)
    av = math.degrees(math.acos(np.clip(np.dot(axv, v0v), -1, 1)))
    angs_all.append(min(av, 180 - av))
angs_all = np.array(angs_all)
check("軸-冷斑角 mean 57.0", abs(angs_all.mean() - 57.0) < 0.5, f"got {angs_all.mean():.1f}")
def ax_ang(i, j):
    axv = vecs[i] + vecs[j]; axv /= np.linalg.norm(axv)
    av = math.degrees(math.acos(np.clip(np.dot(axv, v0v), -1, 1)))
    return min(av, 180 - av)
check("高緯 (10,25) 54.3°", abs(ax_ang(10, 25) - 54.3) < 0.3, f"got {ax_ang(10,25):.1f}")
check("高緯 (22,32) 41.7°", abs(ax_ang(22, 32) - 41.7) < 0.3, f"got {ax_ang(22,32):.1f}")
doc04 = open(os.path.join(O3, "04_high4_node45_study.md")).read()
check("04 待辦 1 打勾", "- [x] 高緯度 4 節點嘅對徑對" in doc04)
check("04 待辦 2 打勾", "- [x] 呢 2 對同色對徑對" in doc04)
check("04 含 22 script 引用", "22_antipodal_temp_check.py" in doc04)
check("06 報告存在", os.path.exists(os.path.join(O3, "06_antipodal_temp_check.md")))
doc01 = open(os.path.join(O3, "01_problem_record.md")).read()
check("01 索引 #19", "| 19 |" in doc01)
check("01 索引 #20", "| 20 |" in doc01)
check("01 索引 #21", "| 21 |" in doc01)
check("README scripts 22", "scripts/ (22 個)" in open(os.path.join(O3, "README.md")).read())
check("final_result 存在", os.path.exists(os.path.join(O3, "final_result.md")))

# ============ 結果 ============
print(f"\n{'='*66}")
print(f"獨立核對結果: {len(passes)} 通過, {len(fails)} 失敗")
if fails:
    print("FAIL 清單:")
    for f in fails:
        print(f"  - {f}")
print(f"RESULT: {len(passes)}/{len(passes)+len(fails)} PASS")
