#!/usr/bin/env python3
"""
08_audit_independent.py — O6 獨立核對審計 (2026-09-11 審計輪)
================================================================
T1: 完全獨立重算 — 唔 import 任何 O6 scripts / 唔讀 O6 data/*.txt (只讀原始來源)。

資料來源 (全部只讀):
- 節點: cmb_cold_spot/data/a5_nodes.txt (60 節點 ICRS, 同 O6 原用)
- 平滑地圖: o5_catalog_compare/data/smooth_cache/smica2_smooth{scale}.fits
  ★ 同源代理 (O2/O3 smooth-cache 先例): 已驗證節點值與 O6 聲稱值一致到
  ≤0.01 μK (-134.189 vs -134.19; +8.207 vs +8.21; 0.5° 與 10° 亦吻合)
  → 證明 o5 cache == 原 /tmp/cache_o3 同源。
- 再生證: data/audit_cache/SMICA_4.17_regen.fits (由 o26 2GB 原圖重建, J 節)

方法: 由原始定義重算每一個 headline 數字, 對比文檔聲稱值 (容差制, 唔用 ==)。
"""

import math
import os
import sys
import numpy as np
import healpy as hp
from collections import defaultdict, deque
from scipy import stats
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
NODE_FILE = os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")
CACHE = os.path.join(BASE, "o5_catalog_compare/data/smooth_cache")
REGEN = os.path.join(BASE, "o6_antipode_check/data/audit_cache/SMICA_4.17_regen.fits")

passes, fails = [], []


def check(name, got, expected, tol, unit=""):
    if isinstance(got, (list, tuple, np.ndarray)) and isinstance(expected, (list, tuple, np.ndarray)):
        got = np.asarray(got, dtype=float)
        expected = np.asarray(expected, dtype=float)
        ok = (len(got) == len(expected)) and np.all(np.abs(got - expected) <= tol)
    else:
        ok = abs(float(got) - float(expected)) <= tol
    if ok:
        passes.append(name)
        print(f"  [PASS] {name}: got={got} {unit}")
    else:
        fails.append(name)
        print(f"  [FAIL] {name}: got={got} {unit} vs expected={expected} {unit} (tol={tol})")


def check_bool(name, cond, detail=""):
    if bool(cond):
        passes.append(name)
        print(f"  [PASS] {name} {detail}")
    else:
        fails.append(name)
        print(f"  [FAIL] {name} {detail}")


print("=" * 70)
print("O6 獨立核對審計 (2026-09-11) — 唔 import O6 scripts / 唔讀 O6 data/*.txt")
print("=" * 70)

# ============ 載入節點 ============
nodes = []
with open(NODE_FILE) as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)

sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic
l_deg = gal.l.deg
b_deg = gal.b.deg

vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])

# ============ 圖 + BFS ============
adj = defaultdict(set)
edges_list = []
for i in range(60):
    for j in range(i+1, 60):
        ang = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if ang < 28.0:
            adj[i].add(j)
            adj[j].add(i)
            edges_list.append((i, j))

hop = {0: 0}
color = {0: 1}
q = deque([0])
while q:
    u = q.popleft()
    for w in adj[u]:
        if w not in hop:
            hop[w] = hop[u] + 1
            color[w] = 1 - color[u]
            q.append(w)

cold_arr = np.array([color[i] for i in range(60)])

# ============ 載入多尺度地圖 (o5 same-source cache) ============
scales = [0.5, 1.0, 2.0, 3.0, 4.17, 5.0, 7.0, 10.0]
T_all = {}
ns_all = {}
for s in scales:
    m = hp.read_map(os.path.join(CACHE, f"smica2_smooth{s}.fits"), field=0)
    ns = hp.get_nside(m)
    pix = hp.ang2pix(ns, l_deg, b_deg, lonlat=True)
    T_all[s] = m[pix] * 1e6
    ns_all[s] = ns

m417 = hp.read_map(os.path.join(CACHE, "smica2_smooth4.17.fits"), field=0)
nside = hp.get_nside(m417)
pix417 = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)
T = m417[pix417] * 1e6

print("\n### A. 圖論/幾何 (03_derivation §1-2, 06_verify, 07) ###")
check("A1 節點數 60", len(nodes), 60, 0)
check("A2 邊數 120", len(edges_list), 120, 0)
check_bool("A3 degree 均勻 4", all(len(adj[i]) == 4 for i in range(60)),
           f"(degrees={sorted({len(adj[i]) for i in range(60)})})")
check("A4 節點 57 hop=8", hop[57], 8, 0)
check("A5 節點 57 冷色(1)", color[57], 1, 0)
check_bool("A6 著色=1-(hop%2) 全 60", all(color[i] == 1 - (hop[i] % 2) for i in range(60)))
ang57 = math.degrees(math.acos(np.clip(np.dot(vecs[0], vecs[57]), -1, 1)))
check("A7 對徑角 174.66°", round(ang57, 2), 174.66, 0.05, "°")
check("A8 冷斑 b=-57.0°", round(b_deg[0], 2), -57.00, 0.5, "°")
check("A9 對徑 b=+52.71°", round(b_deg[57], 2), 52.71, 0.5, "°")

pairs = []
for i in range(60):
    for j in range(i+1, 60):
        a = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if a > 170.0:
            pairs.append((i, j, a))
check("A10 對徑對 = 30", len(pairs), 30, 0)
same_col = sum(1 for i, j, a in pairs if color[i] == color[j])
check("A11 對徑對全同色 30/30", same_col, 30, 0)
hop8 = sum(1 for i, j, a in pairs if hop[i] + hop[j] == 8)
check("A12 對徑對 hop 和=8 30/30", hop8, 30, 0)
pair_angs = np.array([a for _, _, a in pairs])
check("A13 對徑對角距全 ≈174.66", (round(pair_angs.min(), 2), round(pair_angs.max(), 2)),
      (174.66, 174.66), 0.06, "°")

nbrs = sorted(adj[57])
nbr_angs = sorted(math.degrees(math.acos(np.clip(np.dot(vecs[57], vecs[w]), -1, 1))) for w in nbrs)
print(f"    A14 鄰居邊長: {[f'{a:.2f}' for a in nbr_angs]}°")
check_bool("A14 鄰居邊長 26.09-26.17°",
           min(nbr_angs) >= 26.09 - 0.02 and max(nbr_angs) <= 26.17 + 0.02,
           f"(min={min(nbr_angs):.3f}, max={max(nbr_angs):.3f})")
check("A15 鄰居 = [5,31,35,54]", nbrs, [5, 31, 35, 54], 0)
check_bool("A16 鄰居 hop 全 7", all(hop[n] == 7 for n in nbrs))
check_bool("A17 鄰居全熱色 (color=0)", all(color[n] == 0 for n in nbrs))

print("\n### B. 節點溫度 8 尺度 (03_derivation §1/§4, 07 §6) ###")
check("B1 節點0 T@4.17 = -134.19", round(T[0], 2), -134.19, 0.05, "μK")
check("B2 節點57 T@4.17 = +8.21", round(T[57], 2), 8.21, 0.05, "μK")
claimed_T57 = [-5.76, -36.37, -15.37, 4.78, 8.21, 6.19, 2.60, 5.46]
got_T57 = [round(float(T_all[s][57]), 2) for s in scales]
check("B3 節點57 T 8尺度", got_T57, claimed_T57, 0.06, "μK")
claimed_T0 = [-203.13, -174.44, -154.71, -145.02, -134.19, -124.59, -99.67, -68.83]
got_T0 = [round(float(T_all[s][0]), 2) for s in scales]
check("B4 節點0 T 8尺度", got_T0, claimed_T0, 0.06, "μK")
check_bool("B5 符號翻轉 0.5-2° 負, 3-10° 正",
           all(T_all[s][57] < 0 for s in [0.5, 1.0, 2.0]) and all(T_all[s][57] > 0 for s in [3.0, 4.17, 5.0, 7.0, 10.0]),
           f"([{','.join(f'{T_all[s][57]:+.2f}' for s in scales)}])")
sample417 = m417[::7] * 1e6
pct57 = (sample417 < T[57]).mean() * 100
pct0 = (sample417 < T[0]).mean() * 100
check("B6 節點57 百分位 56.6%", round(pct57, 1), 56.6, 1.0, "%")
check("B7 節點0 百分位 0.3%", round(pct0, 1), 0.3, 0.5, "%")

print("\n### C. 5° 區域統計 (03_derivation §3 step1, 07 §3) ###")


def region_vals(idx, radius_deg, s=4.17):
    if s == 4.17:
        mm, ns = m417, nside
    else:
        mm = hp.read_map(os.path.join(CACHE, f"smica2_smooth{s}.fits"), field=0)
        ns = hp.get_nside(mm)
    disc = hp.query_disc(ns, hp.ang2vec(l_deg[idx], b_deg[idx], lonlat=True), np.radians(radius_deg))
    return mm[disc] * 1e6


vals57 = region_vals(57, 5.0)
check("C1 節點57 5° mean +0.20", round(float(vals57.mean()), 2), 0.20, 0.1, "μK")
check("C2 節點57 5° std 22.07", round(float(vals57.std()), 2), 22.07, 0.5, "μK")
check("C3 節點57 5° min -42.50", round(float(vals57.min()), 2), -42.50, 0.5, "μK")
check("C4 節點57 5° max +34.94", round(float(vals57.max()), 2), 34.94, 0.5, "μK")

vals0 = region_vals(0, 5.0)
check("C5 節點0 5° mean -93.71", round(float(vals0.mean()), 2), -93.71, 1.0, "μK")
check("C6 節點0 5° std 25.2", round(float(vals0.std()), 1), 25.2, 1.0, "μK")
check("C7 節點0 5° min -138.02", round(float(vals0.min()), 2), -138.02, 0.5, "μK")
check("C8 節點0 5° max -25.84", round(float(vals0.max()), 2), -25.84, 0.5, "μK")

pix_c57 = hp.ang2pix(nside, l_deg[57], b_deg[57], lonlat=True)
pix_c0 = hp.ang2pix(nside, l_deg[0], b_deg[0], lonlat=True)
check("C9a 中心像素 57 = +8.21", round(float(m417[pix_c57] * 1e6), 2), 8.21, 0.05, "μK")
check("C9b 中心像素 0 = -134.19", round(float(m417[pix_c0] * 1e6), 2), -134.19, 0.05, "μK")

rng = np.random.default_rng(42)
rand_means, rand_stds = [], []
for _ in range(200):
    v = rng.normal(size=3)
    v = v / np.linalg.norm(v)
    d = hp.query_disc(nside, v, np.radians(5.0))
    rv = m417[d] * 1e6
    rand_means.append(rv.mean())
    rand_stds.append(rv.std())
rand_means = np.array(rand_means)
rand_stds = np.array(rand_stds)
z_m = (vals57.mean() - rand_means.mean()) / rand_means.std()
z_s = (vals57.std() - rand_stds.mean()) / rand_stds.std()
check("C10 隨機盤 mean +0.71±36.67",
      (round(float(rand_means.mean()), 2), round(float(rand_means.std()), 2)),
      (0.71, 36.67), 0.5, "μK")
check("C10b 節點57 z_mean = -0.01σ", round(float(z_m), 2), -0.01, 0.1, "σ")
check("C11 隨機盤 std 21.48±7.21",
      (round(float(rand_stds.mean()), 2), round(float(rand_stds.std()), 2)),
      (21.48, 7.21), 0.5, "μK")
check("C11b 節點57 z_std = +0.08σ", round(float(z_s), 2), 0.08, 0.1, "σ")

print("\n### D. 鄰居溫度 (03_derivation §3 step2) ###")
Tn = T[nbrs]
check("D1 鄰居溫度 [-25.48,+1.91,+46.72,+71.67]",
      [round(float(x), 2) for x in Tn], [-25.48, 1.91, 46.72, 71.67], 0.06, "μK")
check("D2 鄰居 mean +23.71", round(float(Tn.mean()), 2), 23.71, 0.5, "μK")
check("D3 鄰居 min/max -25.48/+71.67",
      (round(float(Tn.min()), 2), round(float(Tn.max()), 2)), (-25.48, 71.67), 0.5, "μK")
check("D4 節點57-鄰居mean 差 -15.50", round(float(T[57] - Tn.mean()), 2), -15.50, 0.1, "μK")

print("\n### E. 符號分佈 (03_derivation §3 step3) ###")
n_cold_neg = int(np.sum((T < 0) & (cold_arr == 1)))
n_cold_pos = int(np.sum((T > 0) & (cold_arr == 1)))
n_hot_pos = int(np.sum((T > 0) & (cold_arr == 0)))
n_hot_neg = int(np.sum((T < 0) & (cold_arr == 0)))
check("E1a 冷色負溫 18", n_cold_neg, 18, 0)
check("E1b 冷色正溫 12", n_cold_pos, 12, 0)
check("E1c 熱色正溫 19", n_hot_pos, 19, 0)
check("E1d 熱色負溫 11", n_hot_neg, 11, 0)

table = [[n_cold_neg, n_cold_pos], [n_hot_neg, n_hot_pos]]
odds, p_fisher = stats.fisher_exact(table)
check("E2a Fisher p=0.1205", round(float(p_fisher), 4), 0.1205, 0.005)
check("E2b odds ratio=2.591", round(float(odds), 3), 2.591, 0.05)

match417 = ((cold_arr == 1) & (T < 0)) | ((cold_arr == 0) & (T > 0))
check("E3 匹配率 4.17 = 61.7%", round(float(match417.mean() * 100), 1), 61.7, 1.0, "%")
check("E3b 61.7% == 37/60", int(match417.sum()), 37, 0)

claimed_rates = [60.0, 63.3, 63.3, 61.7, 61.7, 60.0, 58.3, 60.0]
got_rates = []
for s in scales:
    Ts = T_all[s]
    mch = ((cold_arr == 1) & (Ts < 0)) | ((cold_arr == 0) & (Ts > 0))
    got_rates.append(round(float(mch.mean() * 100), 1))
check("E4 跨尺度匹配率", got_rates, claimed_rates, 1.0, "%")
print(f"    E4 實際範圍: {min(got_rates)}-{max(got_rates)}% (文檔: 58-63%)")

corrs = {}
for s in scales:
    corrs[s] = np.corrcoef(cold_arr, T_all[s])[0, 1]
check("E5a r@2.0° = -0.275", round(float(corrs[2.0]), 3), -0.275, 0.01)
check("E5b r@10.0° = -0.181", round(float(corrs[10.0]), 3), -0.181, 0.01)
check("E5c r@4.17° = -0.244", round(float(corrs[4.17]), 3), -0.244, 0.01)
check_bool("E5d 全尺度 r ∈ [-0.28, -0.17]",
           min(corrs.values()) >= -0.28 and max(corrs.values()) <= -0.17,
           f"({ {s: round(corrs[s], 3) for s in scales} })")

cp_idx = sorted([i for i in range(60) if cold_arr[i] == 1 and T[i] > 0])
check("E6 冷色正溫群", cp_idx, [2, 6, 14, 16, 17, 28, 29, 43, 48, 55, 57, 58], 0)
cp_mean = float(np.mean([T[i] for i in cp_idx]))
check("E7 群 mean +25.90", round(cp_mean, 2), 25.90, 0.5, "μK")
cp_sorted = sorted(cp_idx, key=lambda i: T[i])
check("E8 節點57 排名 4/12", cp_sorted.index(57) + 1, 4, 0)

print("\n### F. 對徑對 (03_derivation §3 step5) ###")
sums = np.array([T[i] + T[j] for i, j, a in pairs])
diffs = np.array([abs(T[i] - T[j]) for i, j, a in pairs])
check("F1 對數 30", len(pairs), 30, 0)
check("F2 T_i+T_j mean -2.50", round(float(sums.mean()), 2), -2.50, 0.5, "μK")
check("F3 T_i+T_j std 55.7", round(float(sums.std()), 1), 55.7, 1.0, "μK")
check("F4 |ΔT| mean 56.0", round(float(diffs.mean()), 1), 56.0, 1.0, "μK")
check("F5 |ΔT| median 38.6", round(float(np.median(diffs)), 1), 38.6, 1.0, "μK")
check("F6 |ΔT| max 178.7", round(float(diffs.max()), 1), 178.7, 1.0, "μK")
same_sign = int(np.sum((T[[i for i, j, a in pairs]] > 0) == (T[[j for i, j, a in pairs]] > 0)))
check("F7 同號 11/30", same_sign, 11, 0)

rng2 = np.random.default_rng(42)
rand_diff_means, rand_sum_stds = [], []
for _ in range(2000):
    perm = rng2.permutation(60)
    ri, rj = perm[:30], perm[30:]
    rand_diff_means.append(np.abs(T[ri] - T[rj]).mean())
    rand_sum_stds.append((T[ri] + T[rj]).std())
rand_diff_means = np.array(rand_diff_means)
rand_sum_stds = np.array(rand_sum_stds)
z_diff = (diffs.mean() - rand_diff_means.mean()) / rand_diff_means.std()
z_sum = (sums.std() - rand_sum_stds.mean()) / rand_sum_stds.std()
check("F8 隨機 |ΔT| mean 50.0±4.6",
      (round(float(rand_diff_means.mean()), 1), round(float(rand_diff_means.std()), 1)),
      (50.0, 4.6), 0.5, "μK")
check("F8b 對徑對 |ΔT| z = +1.31σ", round(float(z_diff), 2), 1.31, 0.15, "σ")
check("F9 隨機 和 std 64.0±6.1",
      (round(float(rand_sum_stds.mean()), 1), round(float(rand_sum_stds.std()), 1)),
      (64.0, 6.1), 1.0, "μK")
check("F9b 對徑對 和std z = -1.37σ", round(float(z_sum), 2), -1.37, 0.15, "σ")

binom_z = (same_sign - 15) / math.sqrt(30 * 0.25)
print(f"\n    [註] 同號 11/30 二項 z = {binom_z:.3f}σ; 文檔 02/03 將 -1.37σ 同時掛喺\n"
      f"    「11/30 同號」同「和std 隨機對照」— 二項 z 其實係 -1.46σ (-1.37σ 屬和std 對照)")
check_bool("F10 -1.37σ 標籤 = 和std 對照 z (F9b); 同號二項 z = -1.46",
           abs(z_sum + 1.37) < 0.15 and abs(binom_z + 1.46) < 0.05,
           f"(binom_z={binom_z:.3f})")

print("\n### G. |T| 排名 / hop / ΔE=0 (03_derivation §3 step5, §6) ###")
absT = np.abs(T)
rank57 = int(np.sum(absT <= absT[57]))
check("G1 |T| 排名 14/60", rank57, 14, 0)

hop_dist = {h: sum(1 for i in range(60) if hop[i] == h) for h in range(9)}
check("G2 hop 分佈 [1,4,8,11,12,11,8,4,1]",
      [hop_dist[h] for h in range(9)], [1, 4, 8, 11, 12, 11, 8, 4, 1], 0)

r_abs, p_abs = stats.spearmanr([hop[i] for i in range(60)], absT)
check("G3a Spearman r=-0.224", round(float(r_abs), 3), -0.224, 0.01)
check("G3b Spearman p=0.0853", round(float(p_abs), 4), 0.0853, 0.01)

mabs_h0 = float(np.abs(T[[i for i in range(60) if hop[i] == 0]]).mean())
mabs_h8 = float(np.abs(T[[i for i in range(60) if hop[i] == 8]]).mean())
check("G4 hop0 mean|T| = 134.2", round(mabs_h0, 1), 134.2, 1.0, "μK")
check("G4b hop8 mean|T| = 8.2", round(mabs_h8, 1), 8.2, 1.0, "μK")

frust = set()
for a, b in edges_list:
    if color[a] == color[b]:
        frust.add(frozenset((a, b)))
k = {i: sum(1 for w in adj[i] if frozenset((i, w)) in frust) for i in range(60)}
zeroE = sorted([i for i in range(60) if k[i] == 2])
check("G5 ΔE=0 群 12 節點", zeroE, [10, 12, 19, 22, 23, 25, 28, 32, 37, 40, 45, 46], 0)
check("G6 ΔE=0 mean|T| 19.05", round(float(np.abs(T[zeroE]).mean()), 2), 19.05, 0.5, "μK")
other48 = [i for i in range(60) if i not in zeroE]
check("G7 其他48 mean|T| 36.18", round(float(np.abs(T[other48]).mean()), 2), 36.18, 0.5, "μK")
check("G8 節點57 k=0", k[57], 0, 0)
check_bool("G8b 57 唔喺 ΔE=0 群", 57 not in zeroE)

print("\n### H. 大尺度背景 (03_derivation §3 step5, §4) ###")
m10 = hp.read_map(os.path.join(CACHE, "smica2_smooth10.0.fits"), field=0)
ns10 = hp.get_nside(m10)
disc10 = hp.query_disc(ns10, hp.ang2vec(l_deg[57], b_deg[57], lonlat=True), np.radians(10.0))
rmean10 = float(m10[disc10].mean() * 1e6)
check("H1 10°區域mean(57) +12.99", round(rmean10, 2), 12.99, 1.0, "μK")
T10_57 = float(T_all[10.0][57])
T10_0 = float(T_all[10.0][0])
check("H2a 節點57@10° +5.46", round(T10_57, 2), 5.46, 0.5, "μK")
check("H2b 節點0@10° -68.83", round(T10_0, 2), -68.83, 0.5, "μK")
check("H3 12.99-8.21=4.78 (相對冷點)", round(rmean10 - float(T[57]), 2), 4.78, 0.1, "μK")
check("H4 180-174.66=5.34° (A5 冇反演)", round(180 - ang57, 2), 5.34, 0.05, "°")
check("H5 對徑 4.17→10°: +8.2→+5.5", round(T10_57, 1), 5.5, 0.2, "μK")
check("H6 冷斑 4.17→10°: -134→-68.8", round(T10_0, 1), -68.8, 0.2, "μK")

print("\n### I. 跨文檔聲稱 (01_problem_record / 02_results / README) ###")
check("I1 0.5-2° 全負 (-5.8 到 -36.4)",
      (round(min(got_T57[:3]), 1), round(max(got_T57[:3]), 1)), (-36.4, -5.8), 0.1, "μK")
check_bool("I2 跨尺度匹配率範圍 58-63%",
           min(got_rates) >= 58.0 and max(got_rates) <= 63.5,
           f"(範圍 {min(got_rates)}-{max(got_rates)}%)")
check("I3 61.7% == 37/60", round(37 / 60 * 100, 1), 61.7, 0.1, "%")
check_bool("I4 對徑對隨機期望 ~15 = 30×0.5", abs(30 * 0.5 - 15.0) < 1e-12)

print("\n### J. 再生證 (o26 2GB 原圖 → 4.17° pipeline) ###")
if os.path.exists(REGEN):
    mr = hp.read_map(REGEN, field=0)
    nsr = hp.get_nside(mr)
    pir = hp.ang2pix(nsr, l_deg, b_deg, lonlat=True)
    Tr = mr[pir] * 1e6
    print(f"    再生 map: std={mr.std()*1e6:.2f} μK (o5 cache 4.17 std={m417.std()*1e6:.2f} μK)")
    check("J1 再生 std ≈ o5 cache std", round(float(mr.std() * 1e6), 2),
          round(float(m417.std() * 1e6), 2), 0.5, "μK")
    check("J2 再生 節點0 = -134.19", round(float(Tr[0]), 2), -134.19, 0.1, "μK")
    check("J3 再生 節點57 = +8.21", round(float(Tr[57]), 2), 8.21, 0.1, "μK")
    dr = hp.query_disc(nsr, hp.ang2vec(l_deg[57], b_deg[57], lonlat=True), np.radians(5.0))
    vr = mr[dr] * 1e6
    check("J4 再生 5°mean = 0.20", round(float(vr.mean()), 2), 0.20, 0.1, "μK")
    check("J5 再生 5°std = 22.07", round(float(vr.std()), 2), 22.07, 0.5, "μK")
else:
    print("    再生 map 未就緒, J 節跳過 (背景重建中)")

print("\n" + "=" * 70)
print(f"審計結果: {len(passes)} PASS / {len(fails)} FAIL (共 {len(passes) + len(fails)} 項)")
if fails:
    print("❌ 有 FAIL — 見上文")
    sys.exit(1)
print("✅ 獨立核對全部通過 — 推導鏈無幻覺")
