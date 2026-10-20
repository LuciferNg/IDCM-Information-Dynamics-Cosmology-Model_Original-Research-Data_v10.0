#!/usr/bin/env python3
"""
19_full_hallucination_check.py — O3 全套記錄文檔數字驗證 (最終版)
==================================================================
獨立重算 01/02/03/04 所有記錄文檔嘅關鍵數字, 唔依賴之前 script 輸出:
1. 重新讀 SMICA/NILC/Commander 4.17° cache + remove_dipole 重平滑
2. 重新建圖 (BFS hop, k, 著色, 對徑對)
3. 重新抽 60 節點溫度
4. 驗證所有統計數字
任何 fail → exit 1
"""
import healpy as hp
import numpy as np
import math
import os
from collections import defaultdict, deque, Counter
from astropy.coordinates import SkyCoord
import astropy.units as u
from scipy import stats

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o3_node_temperatures"
DATA = os.path.join(BASE, "data")
CACHE = "/tmp/cache_o3"

fails = []
passes = []

def check(name, cond, detail=""):
    if cond:
        passes.append(name)
        print(f"  ✅ {name} {detail}")
    else:
        fails.append(name)
        print(f"  ❌ {name} {detail}")

print("=" * 66)
print("O3 全套記錄文檔幻覺檢查")
print("=" * 66)

# ============ 1. 檔案存在檢查 ============
print("\n=== 1. 檔案存在 ===")
files_expected = [
    "01_problem_record.md", "02_results.md", "03_red_flag_galactic_plane.md",
    "04_high4_node45_study.md", "README.md", "SESSION_START.md",
    "data/node_temps.txt", "data/bfs_distances.txt",
    "figs/01_temp_hist.png", "figs/02_coldhot_box.png", "figs/03_temp_vs_bfs.png",
]
for f in files_expected:
    check(f"檔案 {f}", os.path.exists(os.path.join(BASE, f)))

scripts_expected = [
    "01_node_temps.py", "02_stats_tests.py", "03_extreme_test.py",
    "04_ladder_corr.py", "05_verify.py", "06_node57_puzzle.py",
    "07_plots.py", "08_zero_energy_nodes.py", "09_hallucination_check.py",
    "10_red_flag_check.py", "11_cross_map_zeroE.py",
    "12_midlayer_rotation_test.py", "13_node45_multiscale.py",
    "14_high4_positions.py", "15_high4_multiscale.py",
    "16_high4_vs_node45.py", "17_antipodal_pairs.py",
    "18_node45_region.py", "19_full_hallucination_check.py",
]
for f in scripts_expected:
    check(f"script {f}", os.path.exists(os.path.join(BASE, "scripts", f)))

# ============ 2. 載入節點 + 溫度 ============
print("\n=== 2. 節點資料 ===")
nodes = []
with open(f"{BASE}/../cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
check("60 節點", len(nodes) == 60)

# 讀 node_temps.txt
rows = []
with open(os.path.join(DATA, "node_temps.txt")) as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        p = line.split()
        rows.append((int(p[0]), int(p[1]), float(p[2]), float(p[3]), float(p[4]), int(p[5])))
T_saved = np.array([r[2] for r in rows])
color_saved = np.array([r[1] for r in rows])
b_saved = np.array([r[4] for r in rows])
hop_saved = np.array([r[5] for r in rows])

# ============ 3. 獨立重讀 4.17° 三地圖 ============
print("\n=== 3. 三地圖 4.17° 獨立重算 ===")
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic
nside = 2048
pix_all = hp.ang2pix(nside, gal.l.deg, gal.b.deg, lonlat=True)

sigma = np.radians(4.17) / (2 * np.sqrt(2 * np.log(2)))

# 獨立重平滑 (唔用 cache, 真正重算) — 用原始地圖
maps_raw = {}
maps_raw['SMICA'] = hp.read_map('/tmp/smica2.fits')
mn = hp.read_map('/tmp/nilc.fits', field=0, nest=True)
maps_raw['NILC'] = hp.reorder(mn, n2r=True)
mc = hp.read_map('/tmp/commander.fits', field=0, nest=True)
maps_raw['Commander'] = hp.reorder(mc, n2r=True)

T3 = {}
for name, m in maps_raw.items():
    ms = hp.remove_dipole(hp.smoothing(m, sigma=sigma))
    T3[name] = ms[pix_all] * 1e6

# 同存檔對比 (SMICA)
diff_smica = np.abs(T3['SMICA'] - T_saved)
check("SMICA 重算 vs 存檔 max|Δ|<0.05", diff_smica.max() < 0.05, f"max={diff_smica.max():.4f}")

# ============ 4. Node 45 數字 ============
print("\n=== 4. Node 45 ===")
i45 = 45
check("node45 SMICA +1.57", abs(T3['SMICA'][45] - 1.57) < 0.1, f"got {T3['SMICA'][45]:.2f}")
check("node45 NILC +2.76", abs(T3['NILC'][45] - 2.76) < 0.1, f"got {T3['NILC'][45]:.2f}")
check("node45 Commander +1.19", abs(T3['Commander'][45] - 1.19) < 0.1, f"got {T3['Commander'][45]:.2f}")
spread45 = max(abs(T3['SMICA'][45]-T3['NILC'][45]), abs(T3['SMICA'][45]-T3['Commander'][45]), abs(T3['NILC'][45]-T3['Commander'][45]))
check("node45 spread 1.57", abs(spread45 - 1.57) < 0.1, f"got {spread45:.2f}")

# 全 60 spread
spreads = np.array([max(abs(T3['SMICA'][i]-T3['NILC'][i]), abs(T3['SMICA'][i]-T3['Commander'][i]), abs(T3['NILC'][i]-T3['Commander'][i])) for i in range(60)])
check("全60 spread mean 3.27", abs(spreads.mean() - 3.27) < 0.1, f"got {spreads.mean():.2f}")
check("全60 spread max 15.42", abs(spreads.max() - 15.42) < 0.1, f"got {spreads.max():.2f}")
pct45 = (spreads < spreads[45]).mean() * 100
check("node45 25 百分位", abs(pct45 - 25) < 5, f"got {pct45:.0f}%")

# ΔE=0 節點 spread
ZERO_E = {10, 12, 19, 22, 23, 25, 28, 32, 37, 40, 45, 46}
check("node23 spread 15.42", abs(spreads[23] - 15.42) < 0.1, f"got {spreads[23]:.2f}")
check("node46 spread 15.24", abs(spreads[46] - 15.24) < 0.1, f"got {spreads[46]:.2f}")

# ============ 5. 高緯度 4 節點 ============
print("\n=== 5. 高緯度 4 節點 ===")
HIGH4 = [10, 22, 25, 32]
others_high = [i for i in range(60) if abs(gal.b.deg[i]) >= 20 and i not in HIGH4]
check("高緯度其他 34", len(others_high) == 34, f"got {len(others_high)}")

Tz = np.abs(T3['SMICA'][HIGH4]).mean()
To = np.abs(T3['SMICA'][others_high]).mean()
check("SMICA ΔE0 mean|T| 12.45", abs(Tz - 12.45) < 0.1, f"got {Tz:.2f}")
check("SMICA 其他 mean|T| 33.21", abs(To - 33.21) < 0.1, f"got {To:.2f}")
check("SMICA 比例 0.375", abs(Tz/To - 0.375) < 0.005, f"got {Tz/To:.3f}")

# 三地圖比例
ratios = {}
for name in ['SMICA', 'NILC', 'Commander']:
    r = np.abs(T3[name][HIGH4]).mean() / np.abs(T3[name][others_high]).mean()
    ratios[name] = r
check("NILC 比例 0.416", abs(ratios['NILC'] - 0.416) < 0.005, f"got {ratios['NILC']:.3f}")
check("Commander 比例 0.372", abs(ratios['Commander'] - 0.372) < 0.005, f"got {ratios['Commander']:.3f}")

# 個別節點三地圖
for i, exp in [(10, -11.68), (22, -23.63), (25, 10.35), (32, -4.13)]:
    check(f"node{i} SMICA {exp}", abs(T3['SMICA'][i] - exp) < 0.1, f"got {T3['SMICA'][i]:.2f}")

# Welch p
tt = stats.ttest_ind(np.abs(T3['SMICA'][HIGH4]), np.abs(T3['SMICA'][others_high]), equal_var=False)
check("Welch p=0.0074", abs(tt.pvalue - 0.0074) < 0.002, f"got {tt.pvalue:.4f}")

# ============ 6. 12 節點統計 ============
print("\n=== 6. 12 節點 ===")
Tz12 = np.abs(T3['SMICA'][list(ZERO_E)]).mean()
To12 = np.abs(T3['SMICA'][[i for i in range(60) if i not in ZERO_E]]).mean()
check("12節點 mean|T| 19.05", abs(Tz12 - 19.05) < 0.1, f"got {Tz12:.2f}")
check("12節點其他 36.18", abs(To12 - 36.18) < 0.1, f"got {To12:.2f}")
check("12節點比例 0.526", abs(Tz12/To12 - 0.526) < 0.005, f"got {Tz12/To12:.3f}")

# ============ 7. 圖論結構 (重建) ============
print("\n=== 7. 圖論結構 ===")
vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])
adj = defaultdict(set)
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < 28.0:
            adj[i].add(j); adj[j].add(i)
check("120 邊", sum(len(adj[i]) for i in range(60))//2 == 120)

# BFS
hop = {0: 0}; q = deque([0])
while q:
    u = q.popleft()
    for w in adj[u]:
        if w not in hop:
            hop[w] = hop[u] + 1; q.append(w)
hop_arr = np.array([hop[i] for i in range(60)])
check("BFS 分佈 1+4+8+11+12+11+8+4+1",
      all(np.bincount(hop_arr, minlength=9)[:9] == [1,4,8,11,12,11,8,4,1]),
      f"got {list(np.bincount(hop_arr, minlength=9)[:9])}")

# 著色
color = {0: 1}; q = deque([0])
while q:
    u = q.popleft()
    for w in adj[u]:
        if w not in color:
            color[w] = 1 - color[u]; q.append(w)
check("著色 = BFS parity", np.all(color_saved == (1 - (hop_arr % 2))))

# k (frustration 邊數)
k_count = {}
for i in range(60):
    k_count[i] = sum(1 for j in adj[i] if color[i] == color[j])
k2 = [i for i in range(60) if k_count[i] == 2]
check("k=2 節點 = 12 個", len(k2) == 12)
check("k=2 = ZERO_E", set(k2) == ZERO_E)
check("k=2 全部喺 d3-d5", all(hop[i] in (3,4,5) for i in k2), f"hop={sorted(hop[i] for i in k2)}")

# 中間層銀河盤
gal_mask = np.abs(gal.b.deg) < 20
mid = (hop_arr >= 3) & (hop_arr <= 5)
mid_gal = (mid & gal_mask).sum()
check("中間層銀河盤 18/34", mid_gal == 18 and mid.sum() == 34, f"got {mid_gal}/{mid.sum()}")

# ΔE=0 銀河盤條件機率
ze_mask = np.array([i in ZERO_E for i in range(60)])
ze_gal = (ze_mask & gal_mask).sum()
check("ΔE=0 銀河盤 8/12", ze_gal == 8, f"got {ze_gal}")
exp_cond = 12 * mid_gal / mid.sum()
check("條件期望 6.35", abs(exp_cond - 6.35) < 0.1, f"got {exp_cond:.2f}")
p_cond = stats.binomtest(8, 12, mid_gal/mid.sum()).pvalue
check("條件 p=0.40", abs(p_cond - 0.40) < 0.05, f"got {p_cond:.3f}")

# ============ 8. 對徑對 ============
print("\n=== 8. 對徑對 ===")
pairs = []
for i in range(60):
    for j in range(i+1, 60):
        ang = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if ang > 170:
            pairs.append((i, j, ang))
check("30 對 >170°", len(pairs) == 30, f"got {len(pairs)}")
all_same = all(color[i] == color[j] for i, j, _ in pairs)
check("全部同色", all_same)
all_hop8 = all(hop[i] + hop[j] == 8 for i, j, _ in pairs)
check("全部 hop 和=8", all_hop8)
all_17466 = all(abs(ang - 174.66) < 0.01 for _, _, ang in pairs)
check("全部 174.66°", all_17466)

# 高緯度 4 對徑對
ang_10_25 = math.degrees(math.acos(np.clip(np.dot(vecs[10], vecs[25]), -1, 1)))
ang_22_32 = math.degrees(math.acos(np.clip(np.dot(vecs[22], vecs[32]), -1, 1)))
check("10↔25 = 174.66", abs(ang_10_25 - 174.66) < 0.01, f"got {ang_10_25:.2f}")
check("22↔32 = 174.66", abs(ang_22_32 - 174.66) < 0.01, f"got {ang_22_32:.2f}")

# hop 組合分佈
hop_pairs = Counter()
for i, j, _ in pairs:
    hop_pairs[(min(hop[i],hop[j]), max(hop[i],hop[j]))] += 1
check("d0↔d8=1, d1↔d7=4, d2↔d6=8, d3↔d5=11, d4↔d4=6",
      hop_pairs[(0,8)]==1 and hop_pairs[(1,7)]==4 and hop_pairs[(2,6)]==8
      and hop_pairs[(3,5)]==11 and hop_pairs[(4,4)]==6,
      f"got {dict(hop_pairs)}")

# ============ 9. 位置 ============
print("\n=== 9. 位置 ===")
check("node10 b=+60.4", abs(gal.b.deg[10] - 60.4) < 0.1, f"got {gal.b.deg[10]:.1f}")
check("node22 b=-30.0", abs(gal.b.deg[22] - (-30.0)) < 0.1, f"got {gal.b.deg[22]:.1f}")
check("node25 b=-62.7", abs(gal.b.deg[25] - (-62.7)) < 0.1, f"got {gal.b.deg[25]:.1f}")
check("node32 b=+34.2", abs(gal.b.deg[32] - 34.2) < 0.1, f"got {gal.b.deg[32]:.1f}")
check("node45 b=-8.4", abs(gal.b.deg[45] - (-8.4)) < 0.1, f"got {gal.b.deg[45]:.1f}")

# ============ 10. 舊記錄數字 ============
print("\n=== 10. 舊記錄 (02_results) ===")
check("mean=-1.25", abs(T3['SMICA'].mean() - (-1.25)) < 0.05, f"got {T3['SMICA'].mean():.2f}")
check("std=46.19", abs(T3['SMICA'].std(ddof=1) - 46.19) < 0.05, f"got {T3['SMICA'].std(ddof=1):.2f}")
check("min=-134.19 @0", abs(T3['SMICA'].min() - (-134.19)) < 0.05 and np.argmin(T3['SMICA']) == 0)
check("max=112.00 @53", abs(T3['SMICA'].max() - 112.00) < 0.05 and np.argmax(T3['SMICA']) == 53)
Tc = T3['SMICA'][color_saved == 1]
Th = T3['SMICA'][color_saved == 0]
check("冷色 mean -12.41", abs(Tc.mean() - (-12.41)) < 0.05, f"got {Tc.mean():.2f}")
check("熱色 mean +9.91", abs(Th.mean() - 9.91) < 0.05, f"got {Th.mean():.2f}")
check("冷熱差 -22.31", abs((Tc.mean() - Th.mean()) - (-22.31)) < 0.05, f"got {Tc.mean()-Th.mean():.2f}")
check("node0 -134.19", abs(T3['SMICA'][0] - (-134.19)) < 0.05, f"got {T3['SMICA'][0]:.2f}")
check("node47 -123.40", abs(T3['SMICA'][47] - (-123.40)) < 0.05, f"got {T3['SMICA'][47]:.2f}")
check("node57 +8.21", abs(T3['SMICA'][57] - 8.21) < 0.05, f"got {T3['SMICA'][57]:.2f}")

# 匹配率
match = ((color_saved == 1) & (T3['SMICA'] < 0)) | ((color_saved == 0) & (T3['SMICA'] > 0))
check("匹配率 61.7%", abs(match.mean() - 0.617) < 0.01, f"got {match.mean():.3f}")

# ============ 結果 ============
print(f"\n{'='*66}")
print(f"結果: {len(passes)} 通過, {len(fails)} 失敗")
if fails:
    print("❌ 有失敗:")
    for f in fails:
        print(f"  - {f}")
    exit(1)
print("✅ 全部通過 — 記錄文檔數字零幻覺")
