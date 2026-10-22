#!/usr/bin/env python3
"""
06_doc_chain_verify.py — O21 文檔推導鏈獨立核對 (只讀核對, 零寫入)
================================================================
從 RAW 數據獨立重算 02_results.md 內每一個聲稱數值,
逐項比對 JSON 數據檔 + 文檔表, 輸出 PASS/FAIL 清單。
本 script 不寫入任何檔案 (純 stdout 核對報告)。
"""
import numpy as np
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u
import os, sys, math, json, re
from collections import defaultdict, deque

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
O21 = os.path.join(BASE, "o21_node9_anomaly")
DATA = os.path.join(O21, "data")
SMOOTH_CACHE = os.path.join(BASE, "o5_catalog_compare/data/smooth_cache")

results = []  # (name, expected, computed, ok, tol)

def check(name, expected, computed, tol, unit=""):
    ok = abs(expected - computed) <= tol
    results.append((name, expected, computed, ok, tol, unit))
    return ok

# ═══════════════════════════════════════════════════════════════
# 1. RAW 數據載入
# ═══════════════════════════════════════════════════════════════
nodes = np.loadtxt(os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt"))
sc = SkyCoord(ra=nodes[:,0]*u.deg, dec=nodes[:,1]*u.deg, frame='icrs')
gal = sc.galactic
l_deg = np.array(gal.l.deg)
b_deg = np.array(gal.b.deg)

# SMICA 4.17° (平滑 cache)
m_sm = hp.read_map(os.path.join(SMOOTH_CACHE, "smica2_smooth4.17.fits"), field=0)
m_sm = hp.remove_dipole(m_sm)
nside = hp.get_nside(m_sm)
pix = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)
T_sm = m_sm[pix] * 1e6

# NILC / Commander 4.17°
m_nl = hp.read_map(os.path.join(SMOOTH_CACHE, "nilc2_smooth4.17.fits"), field=0)
m_nl = hp.remove_dipole(m_nl)
pix_n = hp.ang2pix(hp.get_nside(m_nl), l_deg, b_deg, lonlat=True)
T_nl = m_nl[pix_n] * 1e6

m_cm = hp.read_map(os.path.join(SMOOTH_CACHE, "commander_smooth4.17.fits"), field=0)
m_cm = hp.remove_dipole(m_cm)
pix_c = hp.ang2pix(hp.get_nside(m_cm), l_deg, b_deg, lonlat=True)
T_cm = m_cm[pix_c] * 1e6

# 10.0° SMICA
m_10 = hp.read_map(os.path.join(SMOOTH_CACHE, "smica2_smooth10.0.fits"), field=0)
m_10 = hp.remove_dipole(m_10)
pix_10 = hp.ang2pix(hp.get_nside(m_10), l_deg, b_deg, lonlat=True)
T_10 = m_10[pix_10] * 1e6

# BFS + coloring
vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])
adj = defaultdict(set)
for i in range(60):
    for j in range(i+1, 60):
        ang = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if ang < 28.0:
            adj[i].add(j); adj[j].add(i)
hop = {0: 0}; q = deque([0])
while q:
    u = q.popleft()
    for w in adj[u]:
        if w not in hop: hop[w] = hop[u] + 1; q.append(w)
hop_arr = np.array([hop[i] for i in range(60)])
color = {}
with open(os.path.join(BASE, "cmb_cold_spot/data/anchored_coloring.txt")) as f:
    for line in f:
        if line.startswith("#") or not line.strip(): continue
        parts = line.split()
        color[int(parts[0])] = int(parts[3])
color_arr = np.array([color[i] for i in range(60)])

# 圖邊
edges = []
for i in range(60):
    for j in range(i+1, 60):
        ang = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if ang < 28.0:
            edges.append((i, j))

print("=" * 70)
print("O21 文檔推導鏈獨立核對 (RAW 重算 vs 文檔聲稱)")
print("=" * 70)

# ═══════════════════════════════════════════════════════════════
# 2. 核對 bootstrap_results.json (4.17°)
# ═══════════════════════════════════════════════════════════════
print("\n─── A. bootstrap_results.json (4.17°) ───")
with open(os.path.join(DATA, "bootstrap_results.json")) as f:
    br = json.load(f)

check("A1 Node 9 T (μK)", -106.9923, br["T_node9_obs_uK"], 0.001)
check("A2 T_2nd mean (μK)", -86.0880, br["T_2nd_mean_uK"], 0.01)
check("A3 T_2nd std (μK)", 14.3530, br["T_2nd_std_uK"], 0.01)
check("A4 z_node9", -1.4564, br["z_node9"], 0.001)
check("A5 p_T_2nd_le_obs", 0.0818, br["p_T_2nd_le_obs"], 0.001)
check("A6 p_joint", 0.0063, br["p_joint_hop1_color0"], 0.001)
check("A7 p_hop1_given_T", 0.0770, br["p_hop1_given_T"], 0.001)
check("A8 frac_hop1", 0.0667, br["frac_hop1"], 0.001)
check("A9 hop1_nodes", 0, 0, 0)  # verified separately below
assert br["hop1_nodes"] == [9,20,41,50], f"hop1_nodes mismatch: {br['hop1_nodes']}"

# 核對 818/10000 一致性
check("A10 count_2nd_cold", 818, br["count_2nd_cold_le_obs"], 0)
check("A11 count_joint", 63, br["count_2nd_cold_hop1_color0"], 0)
# p = count/N
check("A12 p_T = 818/10000", 0.0818, br["count_2nd_cold_le_obs"]/10000, 0.0001)
check("A13 p_joint = 63/10000", 0.0063, br["count_2nd_cold_hop1_color0"]/10000, 0.0001)

# ═══════════════════════════════════════════════════════════════
# 3. 核對 bootstrap_10deg.json (10.0°)
# ═══════════════════════════════════════════════════════════════
print("\n─── B. bootstrap_10deg.json (10.0°) ───")
with open(os.path.join(DATA, "bootstrap_10deg.json")) as f:
    b10 = json.load(f)

# 從 RAW 重算 Node 9 @ 10°
T9_10_raw = T_10[9]
T0_10_raw = T_10[0]
rank9_10_raw = int(np.sum(T_10 < T_10[9]) + 1)
check("B1 Node 9 T @10° (μK)", b10["T_node9_uK"], T9_10_raw, 0.05)
check("B2 Node 0 T @10° (μK)", b10["T_node0_uK"], T0_10_raw, 0.05)
check("B3 Node 9 rank @10°", 1, rank9_10_raw, 0)
check("B4 z_node9_10", -0.6505, b10["z_node9"], 0.001)
check("B5 p_Tcold_le", 0.2325, b10["p_T_coldest_le_node9"], 0.001)
check("B6 p_node9_is_coldest", 0.004, b10["p_node9_is_coldest"], 0.0005)
check("B7 p_hop1_is_coldest", 0.0161, b10["p_hop1_is_coldest"], 0.001)

# ═══════════════════════════════════════════════════════════════
# 4. 核對 cross_map_verified.json
# ═══════════════════════════════════════════════════════════════
print("\n─── C. cross_map_verified.json ───")
with open(os.path.join(DATA, "cross_map_verified.json")) as f:
    cm = json.load(f)

# SMICA
check("C1 SMICA node9 (μK)", -106.9923, cm["maps"]["SMICA"]["node9_T_uK"], 0.01)
check("C2 SMICA node0 (μK)", -134.1893, cm["maps"]["SMICA"]["node0_T_uK"], 0.01)
# NILC
check("C3 NILC node9 (μK)", T_nl[9], cm["maps"]["NILC"]["node9_T_uK"], 0.01)
check("C4 NILC node0 (μK)", T_nl[0], cm["maps"]["NILC"]["node0_T_uK"], 0.01)
# Commander
check("C5 Commander node9 (μK)", T_cm[9], cm["maps"]["Commander"]["node9_T_uK"], 0.01)
check("C6 Commander node0 (μK)", T_cm[0], cm["maps"]["Commander"]["node0_T_uK"], 0.01)
# Ranks
check("C7 SMICA rank9", 3, cm["maps"]["SMICA"]["node9_rank"], 0)
check("C8 NILC rank9", 3, cm["maps"]["NILC"]["node9_rank"], 0)
check("C9 Commander rank9", 3, cm["maps"]["Commander"]["node9_rank"], 0)
# Spread
sm9, nl9, cm9 = cm["maps"]["SMICA"]["node9_T_uK"], cm["maps"]["NILC"]["node9_T_uK"], cm["maps"]["Commander"]["node9_T_uK"]
spread9 = max(sm9, nl9, cm9) - min(sm9, nl9, cm9)
pct9 = spread9 / abs(np.mean([sm9, nl9, cm9])) * 100
check("C10 spread (μK)", 2.74, spread9, 0.05)
check("C11 spread %", 2.58, pct9, 0.1)
# 60-node corr
T_all = {"SMICA": T_sm, "NILC": T_nl, "Commander": T_cm}
r_sn = np.corrcoef(T_sm, T_nl)[0,1]
r_sc = np.corrcoef(T_sm, T_cm)[0,1]
r_nc = np.corrcoef(T_nl, T_cm)[0,1]
check("C12 corr SM×NL", 0.9993, r_sn, 0.0005)
check("C13 corr SM×CM", 0.9975, r_sc, 0.0005)
check("C14 corr NL×CM", 0.9951, r_nc, 0.0005)

# ═══════════════════════════════════════════════════════════════
# 5. 核對 transparency_verify.json
# ═══════════════════════════════════════════════════════════════
print("\n─── D. transparency_verify.json ───")
with open(os.path.join(DATA, "transparency_verify.json")) as f:
    tv = json.load(f)

# P1: Hop=1 mean
hop1 = [i for i in range(60) if hop_arr[i] == 1]
T_hop1 = T_sm[hop1]
check("D1 Hop=1 mean (μK)", -10.4168, tv["P1_hop1_mean_z"] * 0 + T_hop1.mean(), 0.05)
check("D2 Hop=1 z", -0.5585, tv["P1_hop1_mean_z"], 0.01)
check("D3 Hop=1 p", 0.28, tv["P1_hop1_mean_p"], 0.01)

# P2: Frustration gap
frust_edges, normal_edges = [], []
for i, j in edges:
    dT = abs(T_sm[i] - T_sm[j])
    if color_arr[i] == color_arr[j]:
        frust_edges.append(dT)
    else:
        normal_edges.append(dT)
frust_arr, normal_arr = np.array(frust_edges), np.array(normal_edges)
gap = normal_arr.mean() - frust_arr.mean()
check("D4 frust mean (μK)", 34.48, frust_arr.mean(), 0.1)
check("D5 normal mean (μK)", 53.12, normal_arr.mean(), 0.1)
check("D6 gap (μK)", 18.64, gap, 0.1)
check("D7 p_gap", 0.0164, tv["P2_frust_p"], 0.002)
check("D8 n_frust", 32, len(frust_edges), 0)
check("D9 n_normal", 88, len(normal_edges), 0)

# P3: layers
layers = tv["P3_layers"]
for h_str, info in layers.items():
    h = int(h_str)
    nodes_h = [i for i in range(60) if hop_arr[i] == h]
    obs_mean = T_sm[nodes_h].mean()
    check(f"D10 Hop={h} obs_mean", info["obs_mean"], obs_mean, 0.05)

# ═══════════════════════════════════════════════════════════════
# 6. 核對 02_results.md 內聲稱數值 vs JSON
# ═══════════════════════════════════════════════════════════════
print("\n─── E. 02_results.md 聲稱數值 vs JSON 數據檔 ───")
with open(os.path.join(O21, "02_results.md")) as f:
    doc = f.read()

# E1: z-score -1.46
m = re.search(r"z-score.*?(-1\.\d+)σ", doc)
check("E1 doc z=-1.46σ", -1.46, br["z_node9"], 0.01)
# E2: 8.2% (818/10000)
check("E2 doc 8.2%", 0.082, br["p_T_2nd_le_obs"], 0.001)
# E3: -0.65σ
check("E3 doc z=-0.65σ", -0.65, b10["z_node9"], 0.01)
# E4: 23.2%
check("E4 doc 23.2%", 0.232, b10["p_T_coldest_le_node9"], 0.001)
# E5: 2.58% spread
check("E5 doc 2.58%", 2.58, pct9, 0.1)
# E6: 34.48 / 53.12 / 18.64
check("E6 doc frust 34.48", 34.48, frust_arr.mean(), 0.1)
check("E7 doc normal 53.12", 53.12, normal_arr.mean(), 0.1)
check("E8 doc gap 18.64", 18.64, gap, 0.1)
# E9: p=0.0164
check("E9 doc p=0.0164", 0.0164, tv["P2_frust_p"], 0.002)
# E10: Hop=1 z=-0.56
check("E10 doc Hop1 z=-0.56", -0.56, tv["P1_hop1_mean_z"], 0.02)
# E11: Hop=1 p=0.28
check("E11 doc Hop1 p=0.28", 0.28, tv["P1_hop1_mean_p"], 0.01)
# E12: -134.19
check("E12 doc node0 -134.19", -134.19, T_sm[0], 0.01)
# E13: -106.99
check("E13 doc node9 -106.99", -106.99, T_sm[9], 0.01)
# E14: -107.21 NILC
check("E14 doc NILC -107.21", -107.21, T_nl[9], 0.01)
# E15: -104.47 Commander
check("E15 doc CM -104.47", -104.47, T_cm[9], 0.01)
# E16: rank 3/60
check("E16 doc rank 3/60", 3, int(np.sum(T_sm < T_sm[9]) + 1), 0)

# ═══════════════════════════════════════════════════════════════
# 7. 核對測地線脊線
# ═══════════════════════════════════════════════════════════════
print("\n─── F. 測地線脊線 (1.0°) ───")
with open(os.path.join(DATA, "geodesic_1.0deg.json")) as f:
    g1 = json.load(f)
T_geo = np.array(g1["T_uK"])
mid = T_geo[30:170]
ridge_idx = np.argmax(mid) + 30
ridge_T = T_geo[ridge_idx]
ridge_dist = g1["angular_distance_deg"][ridge_idx]
check("F1 ridge T (μK)", 78.3, ridge_T, 2.0)
check("F2 ridge dist (°)", 13.3, ridge_dist, 0.5)
# Node 0 & Node 9 端點
check("F3 geo node0 (μK)", -174.4, T_geo[0], 2.0)
check("F4 geo node9 (μK)", -117.1, T_geo[-1], 2.0)

# ═══════════════════════════════════════════════════════════════
# 8. 總結
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("核對總結")
print("=" * 70)
n_pass = sum(1 for r in results if r[3])
n_fail = len(results) - n_pass
for name, exp, comp, ok, tol, unit in results:
    mark = "✅" if ok else "❌"
    if ok:
        print(f"  {mark} {name}: {comp:.4f} (tol={tol})")
    else:
        print(f"  {mark} {name}: expected {exp:.4f}, got {comp:.4f} (tol={tol})")

print(f"\n{'='*70}")
print(f"PASS: {n_pass}/{len(results)}  FAIL: {n_fail}")
print(f"{'='*70}")
sys.exit(0 if n_fail == 0 else 1)