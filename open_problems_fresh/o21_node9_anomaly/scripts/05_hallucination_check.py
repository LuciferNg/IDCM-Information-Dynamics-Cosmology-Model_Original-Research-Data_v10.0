#!/usr/bin/env python3
"""
05_hallucination_check.py — O21 所有數值獨立驗證
=============================================
從 RAW 數據重新計算每個關鍵數值，核對記錄文檔
"""

import numpy as np
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u
import os, sys, math, json
from collections import defaultdict, deque

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
O21 = os.path.join(BASE, "o21_node9_anomaly")
DATA = os.path.join(O21, "data")
SMOOTH_CACHE = os.path.join(BASE, "o5_catalog_compare/data/smooth_cache")

# ─── Load raw data ─────────────────────────────────────────────────
nodes = np.loadtxt(os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt"))
sc = SkyCoord(ra=nodes[:,0]*u.deg, dec=nodes[:,1]*u.deg, frame='icrs')
gal = sc.galactic
l_deg = np.array(gal.l.deg)
b_deg = np.array(gal.b.deg)

# Node temperatures from SMICA 4.17° (read from cached smooth map)
m_smica = hp.read_map(os.path.join(SMOOTH_CACHE, "smica2_smooth4.17.fits"), field=0)
m_smica = hp.remove_dipole(m_smica)
nside = hp.get_nside(m_smica)
pix = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)
T_uK = m_smica[pix] * 1e6

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

edges = []
for i in range(60):
    for j in range(i+1, 60):
        ang = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if ang < 28.0:
            edges.append((i, j))

# ─── Load NILC/Commander for cross-map ────────────────────────────
m_nilc = hp.read_map(os.path.join(SMOOTH_CACHE, "nilc2_smooth4.17.fits"), field=0)
m_nilc = hp.remove_dipole(m_nilc)
m_cmd = hp.read_map(os.path.join(SMOOTH_CACHE, "commander_smooth4.17.fits"), field=0)
m_cmd = hp.remove_dipole(m_cmd)
pix_n = hp.ang2pix(hp.get_nside(m_nilc), l_deg, b_deg, lonlat=True)
pix_c = hp.ang2pix(hp.get_nside(m_cmd), l_deg, b_deg, lonlat=True)
T_nilc = m_nilc[pix_n] * 1e6
T_cmd = m_cmd[pix_c] * 1e6

# ─── Load 10.0° map ───────────────────────────────────────────────
m10 = hp.read_map(os.path.join(SMOOTH_CACHE, "smica2_smooth10.0.fits"), field=0)
m10 = hp.remove_dipole(m10)
pix10 = hp.ang2pix(hp.get_nside(m10), l_deg, b_deg, lonlat=True)
T10 = m10[pix10] * 1e6

# ===================================================================
# VERIFICATION 1: Node 9 basic identity
# ===================================================================
print("=" * 66)
print("VERIFICATION 1: Node 9 basic identity")
print("=" * 66)
pass_fail = []

# V1.1: Node 9 coordinates
node9_l, node9_b = l_deg[9], b_deg[9]
print(f"  Node 9 l={node9_l:.2f}° (expected 214.92°), b={node9_b:.2f}° (expected -31.16°)")
assert abs(node9_l - 214.92) < 0.1, f"l mismatch: {node9_l}"
assert abs(node9_b - (-31.16)) < 0.1, f"b mismatch: {node9_b}"
pass_fail.append(("V1.1 Node 9 coords", True))

# V1.2: Node 9 hop=1
assert hop_arr[9] == 1, f"Node 9 hop={hop_arr[9]} != 1"
print(f"  Node 9 hop={hop_arr[9]} (expected 1)")
pass_fail.append(("V1.2 Node 9 hop=1", True))

# V1.3: Node 9 color=0
assert color_arr[9] == 0, f"Node 9 color={color_arr[9]} != 0"
print(f"  Node 9 color={color_arr[9]} (expected 0 = hot)")
pass_fail.append(("V1.3 Node 9 color=0", True))

# V1.4: Node 9 has 4 neighbours, all cold-coloured
n9_neighbors = [i for i in adj[9]]
print(f"  Node 9 neighbours: {n9_neighbors}")
assert len(n9_neighbors) == 4, f"Node 9 has {len(n9_neighbors)} neighbours, expected 4"
n9_neighbor_colors = [color_arr[i] for i in n9_neighbors]
assert all(c == 1 for c in n9_neighbor_colors), f"Not all neighbours cold: {n9_neighbor_colors}"
print(f"  All neighbours cold-coloured: {n9_neighbor_colors}")
pass_fail.append(("V1.4 Node 9 neighbours", True))

# ===================================================================
# VERIFICATION 2: SMICA 4.17° temperatures
# ===================================================================
print(f"\n{'='*66}")
print("VERIFICATION 2: SMICA 4.17° temperatures")
print("=" * 66)

# V2.1: Node 9 temperature
T9 = T_uK[9]
print(f"  Node 9: {T9:.2f} μK (expected -106.99 μK)")
assert abs(T9 - (-106.99)) < 0.1, f"Node 9 T mismatch: {T9}"
pass_fail.append(("V2.1 Node 9 T", True))

# V2.2: Node 0 temperature
T0 = T_uK[0]
print(f"  Node 0: {T0:.2f} μK (expected -134.19 μK)")
assert abs(T0 - (-134.19)) < 0.1, f"Node 0 T mismatch: {T0}"
pass_fail.append(("V2.2 Node 0 T", True))

# V2.3: Node 9 rank
sorted_T = np.sort(T_uK)
rank9 = np.sum(T_uK < T9) + 1
print(f"  Node 9 rank: {rank9}/60 (expected 3/60)")
assert rank9 == 3, f"Node 9 rank {rank9} != 3"
pass_fail.append(("V2.3 Node 9 rank 3/60", True))

# V2.4: 60-node std
std60 = T_uK.std()
print(f"  60-node std: {std60:.1f} μK (expected ~45.8 μK)")
assert abs(std60 - 45.8) < 1.0, f"Std mismatch: {std60}"
pass_fail.append(("V2.4 60-node std", True))

# V2.5: Hop=1 temperatures
hop1_nodes = [i for i in range(60) if hop_arr[i] == 1]
T_hop1 = T_uK[hop1_nodes]
print(f"  Hop=1 nodes: {hop1_nodes}")
print(f"  Hop=1 temps: {[f'{T:.2f}' for T in T_hop1]}")
print(f"  Node 9: {T_hop1[0]:.2f} (expected -106.99)")
print(f"  Node 20: {T_hop1[1]:.2f} (expected +35.41)")
print(f"  Node 41: {T_hop1[2]:.2f} (expected -6.28)")
print(f"  Node 50: {T_hop1[3]:.2f} (expected +36.19)")
assert abs(T_hop1[0] - (-106.99)) < 0.1
assert abs(T_hop1[1] - 35.41) < 1.0
assert abs(T_hop1[2] - (-6.28)) < 1.0
assert abs(T_hop1[3] - 36.19) < 1.0
pass_fail.append(("V2.5 Hop=1 temps", True))

# ===================================================================
# VERIFICATION 3: Cross-map
# ===================================================================
print(f"\n{'='*66}")
print("VERIFICATION 3: Cross-map")
print("=" * 66)

T9_sm = T_uK[9]
T9_nl = T_nilc[9]
T9_cm = T_cmd[9]
T0_sm = T_uK[0]
T0_nl = T_nilc[0]
T0_cm = T_cmd[0]

print(f"  SMICA:    node9={T9_sm:+.2f} μK, node0={T0_sm:+.2f} μK")
print(f"  NILC:     node9={T9_nl:+.2f} μK, node0={T0_nl:+.2f} μK")
print(f"  Commander: node9={T9_cm:+.2f} μK, node0={T0_cm:+.2f} μK")

# Cross-map spread
T9_all = np.array([T9_sm, T9_nl, T9_cm])
spread9 = T9_all.max() - T9_all.min()
mean9 = T9_all.mean()
pct9 = spread9 / abs(mean9) * 100
print(f"  Node 9 spread: {spread9:.2f} μK ({pct9:.2f}%)")
assert spread9 < 5.0, f"Cross-map spread {spread9} > 5 μK"
assert pct9 < 5.0, f"Cross-map spread {pct9}% > 5%"
pass_fail.append(("V3.1 Cross-map spread < 5%", True))

# Rank consistency
rank9_sm = np.sum(T_uK < T9_sm) + 1
rank9_nl = np.sum(T_nilc < T9_nl) + 1
rank9_cm = np.sum(T_cmd < T9_cm) + 1
print(f"  Node 9 ranks: SMICA={rank9_sm}/60, NILC={rank9_nl}/60, Commander={rank9_cm}/60")
assert rank9_sm == rank9_nl == rank9_cm == 3, f"Rank mismatch: {rank9_sm}, {rank9_nl}, {rank9_cm}"
pass_fail.append(("V3.2 All rank 3/60", True))

# 60-node correlation
r_sm_nl = np.corrcoef(T_uK, T_nilc)[0, 1]
r_sm_cm = np.corrcoef(T_uK, T_cmd)[0, 1]
r_nl_cm = np.corrcoef(T_nilc, T_cmd)[0, 1]
print(f"  Corr: SMICA×NILC={r_sm_nl:.4f}, SMICA×Commander={r_sm_cm:.4f}, NILC×Commander={r_nl_cm:.4f}")
assert r_sm_nl > 0.99, f"SMICA×NILC corr {r_sm_nl} < 0.99"
assert r_sm_cm > 0.99, f"SMICA×Commander corr {r_sm_cm} < 0.99"
pass_fail.append(("V3.3 Cross-map corr > 0.99", True))

# ===================================================================
# VERIFICATION 4: Frustration edge test
# ===================================================================
print(f"\n{'='*66}")
print("VERIFICATION 4: Frustration edge |ΔT|")
print("=" * 66)

frust_edges = []
normal_edges = []
for i, j in edges:
    dT = abs(T_uK[i] - T_uK[j])
    if color_arr[i] == color_arr[j]:
        frust_edges.append(dT)
    else:
        normal_edges.append(dT)
frust_arr = np.array(frust_edges)
normal_arr = np.array(normal_edges)

frust_mean = frust_arr.mean()
normal_mean = normal_arr.mean()
gap = normal_mean - frust_mean
print(f"  Frustration edges: {len(frust_arr)} mean={frust_mean:.2f} μK (expected ~34.48)")
print(f"  Normal edges: {len(normal_arr)} mean={normal_mean:.2f} μK (expected ~53.12)")
print(f"  Gap: {gap:.2f} μK (expected ~18.64)")
assert abs(frust_mean - 34.48) < 1.0, f"Frust mean {frust_mean}"
assert abs(normal_mean - 53.12) < 1.0, f"Normal mean {normal_mean}"
assert abs(gap - 18.64) < 1.0, f"Gap {gap}"
pass_fail.append(("V4.1 Frust vs Normal gap", True))

# ===================================================================
# VERIFICATION 5: 10.0° bootstrap
# ===================================================================
print(f"\n{'='*66}")
print("VERIFICATION 5: 10.0° temperatures")
print("=" * 66)

T9_10 = T10[9]
T0_10 = T10[0]
rank9_10 = np.sum(T10 < T9_10) + 1
print(f"  Node 9 @ 10°: {T9_10:.2f} μK (expected -90.34 μK)")
print(f"  Node 0 @ 10°: {T0_10:.2f} μK (expected -68.83 μK)")
print(f"  Node 9 rank @ 10°: {rank9_10}/60 (expected 1/60)")
assert abs(T9_10 - (-90.34)) < 0.5, f"Node 9 10° T mismatch: {T9_10}"
assert abs(T0_10 - (-68.83)) < 0.5, f"Node 0 10° T mismatch: {T0_10}"
assert rank9_10 == 1, f"Node 9 10° rank {rank9_10} != 1"
pass_fail.append(("V5.1 10.0° temperatures", True))

# ===================================================================
# VERIFICATION 6: Geodesic ridge at 1.0°
# ===================================================================
print(f"\n{'='*66}")
print("VERIFICATION 6: Geodesic ridge at 1.0°")
print("=" * 66)

# Read 1.0° geodesic profile
with open(os.path.join(DATA, "geodesic_1.0deg.json")) as f:
    geo10 = json.load(f)
T_geo = np.array(geo10["T_uK"])
mid = T_geo[30:170]
ridge_idx = np.argmax(mid) + 30
ridge_T = T_geo[ridge_idx]
ridge_dist = geo10["angular_distance_deg"][ridge_idx]
print(f"  Ridge: T={ridge_T:.1f} μK @ {ridge_dist:.1f}° (expected ~+78.3 μK @ 13.3°)")
assert ridge_T > 70, f"Ridge T {ridge_T} < 70 μK"
assert abs(ridge_dist - 13.3) < 1.0, f"Ridge distance {ridge_dist}"
pass_fail.append(("V6.1 +75 μK ridge", True))

# ===================================================================
# SUMMARY
# ===================================================================
print(f"\n{'='*66}")
print("VERIFICATION SUMMARY")
print(f"{'='*66}")
all_pass = True
for name, ok in pass_fail:
    status = "✅" if ok else "❌"
    print(f"  {status} {name}")
    if not ok:
        all_pass = False

print(f"\n{'='*66}")
if all_pass:
    print(f"ALL {len(pass_fail)}/{len(pass_fail)} VERIFICATIONS PASSED ✅")
else:
    print(f"⚠️  {sum(1 for _, ok in pass_fail if not ok)} FAILURES")
print(f"{'='*66}")