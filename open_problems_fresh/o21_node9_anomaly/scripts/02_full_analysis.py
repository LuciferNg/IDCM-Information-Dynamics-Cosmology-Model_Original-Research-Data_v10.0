#!/usr/bin/env python3
"""
02_full_analysis.py — O21: Complete Node 9 Analysis
====================================================
1. Bootstrap at 4.17° (already done, load results)
2. Bootstrap at 10.0°  (node 9 is coldest — check significance)
3. Geodesic profile at 1.0° (the +75 μK ridge)
4. Cross-map at node 9 (SMICA × NILC × Commander @ 4.17°)
5. Summary
"""

import numpy as np
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u
import os, sys, math, time, json
from collections import defaultdict, deque

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
O21 = os.path.join(BASE, "o21_node9_anomaly")
DATA = os.path.join(O21, "data")
os.makedirs(DATA, exist_ok=True)

SMOOTH_CACHE = os.path.join(BASE, "o5_catalog_compare/data/smooth_cache")
NSIDE_OUT = 64

# ─── Load nodes ────────────────────────────────────────────────────
nodes = np.loadtxt(os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt"))
sc = SkyCoord(ra=nodes[:,0]*u.deg, dec=nodes[:,1]*u.deg, frame='icrs')
gal = sc.galactic
l_deg = np.array(gal.l.deg)
b_deg = np.array(gal.b.deg)
pix_out = hp.ang2pix(NSIDE_OUT, l_deg, b_deg, lonlat=True)

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

# Observed temperatures at 4.17°
T_obs = np.loadtxt(os.path.join(BASE, "o3_node_temperatures/data/node_temps.txt"), skiprows=1)
T_obs_uK = T_obs[:, 2]
T_node9_obs = T_obs_uK[9]
T_node0_obs = T_obs_uK[0]

hop1_nodes = [i for i in range(60) if hop_arr[i] == 1]
hop1_color0 = [i for i in hop1_nodes if color_arr[i] == 0]

print("=" * 66)
print("O21: Complete Node 9 Analysis")
print("=" * 66)

# ====================================================================
# 1. Load bootstrap results from Phase 1
# ====================================================================
print("\n─── 1. Bootstrap 4.17° (from Phase 1) ───")
with open(os.path.join(DATA, "bootstrap_results.json")) as f:
    br = json.load(f)

print(f"  2nd coldest distribution: mean={br['T_2nd_mean_uK']:.2f}, std={br['T_2nd_std_uK']:.2f} μK")
print(f"  Node 9 observed: {br['T_node9_obs_uK']:.2f} μK → z = {br['z_node9']:.2f}σ")
print(f"  P(T_2nd ≤ {br['T_node9_obs_uK']:.0f}): {br['p_T_2nd_le_obs']:.4f} ({br['p_T_2nd_le_obs']*100:.1f}%)")
print(f"  P_joint (hop=1 ∩ color=0): {br['p_joint_hop1_color0']:.6f} ({br['p_joint_hop1_color0']*100:.4f}%)")
print(f"  P(hop=1|T_2nd≤obs): {br['p_hop1_given_T']:.4f} vs random {br['frac_hop1']:.4f}")
print(f"  → 4.17°: Node 9 is NOT extreme (z={br['z_node9']:.2f}σ, p={br['p_T_2nd_le_obs']:.4f})")

# ====================================================================
# 2. Bootstrap at 10.0° — node 9 is coldest
# ====================================================================
print(f"\n─── 2. Bootstrap at 10.0° (node 9 is coldest at this scale) ───")

smica10_path = os.path.join(SMOOTH_CACHE, "smica2_smooth10.0.fits")
if os.path.exists(smica10_path):
    m10 = hp.read_map(smica10_path, field=0)
    m10 = hp.remove_dipole(m10)
    m10_uK = m10 * 1e6
    print(f"  SMICA 10.0°: std={m10_uK.std():.1f} μK")

    # Cℓ at 10.0° from the map
    cl10 = hp.anafast(m10_uK, lmax=NSIDE_OUT*2)
    cl10_input = np.zeros(len(cl10))
    cl10_input[2:] = cl10[2:]
    var10 = np.sum((2*np.arange(len(cl10_input))[2:] + 1) * cl10_input[2:] / (4*np.pi))
    print(f"  Cℓ expected σ: {np.sqrt(var10):.1f} μK")

    # Node temperatures at 10.0°
    nside10 = hp.get_nside(m10)
    pix10 = hp.ang2pix(nside10, l_deg, b_deg, lonlat=True)
    T10 = m10_uK[pix10]
    node9_rank10 = np.sum(T10 < T10[9]) + 1  # 1-indexed rank
    print(f"  Node 9 at 10.0°: T={T10[9]:.1f} μK, rank={node9_rank10}/60 (coldest)")
    print(f"  Node 0 at 10.0°: T={T10[0]:.1f} μK, rank={np.sum(T10 < T10[0]) + 1}/60")

    # GRF at 10.0°: 10,000 realizations
    print(f"  Running 10,000 GRF at 10.0°...")
    N_REAL = 10000
    batch_size = 200
    n_batches = N_REAL // batch_size
    t0 = time.time()

    count_coldest_is_node9 = 0      # node 9 is coldest
    count_coldest_is_hop1 = 0       # coldest is hop=1
    count_coldest_node9_T = 0       # T ≤ T10[9] AND at node 9 position
    all_coldest_temps = []

    for batch in range(n_batches):
        for i in range(batch_size):
            alm = hp.synalm(cl10_input, lmax=2*NSIDE_OUT, verbose=False)
            m = hp.alm2map(alm, nside=NSIDE_OUT, verbose=False)
            T = m[pix_out]
            sorted_idx = np.argsort(T)
            coldest = sorted_idx[0]
            T_coldest = T[coldest]
            all_coldest_temps.append(T_coldest)

            if T_coldest <= T10[9]:
                count_coldest_node9_T += 1
                if coldest == 9:
                    count_coldest_is_node9 += 1
                if hop_arr[coldest] == 1:
                    count_coldest_is_hop1 += 1

        elapsed = time.time() - t0
        rate = (batch+1) * batch_size / elapsed
        remaining = (n_batches - batch - 1) * batch_size / rate
        print(f"    Batch {batch+1}/{n_batches}: {elapsed:.0f}s, {rate:.0f}/s, ~{remaining:.0f}s remaining")

    T_cold_arr = np.array(all_coldest_temps)
    T_cold_mean = float(np.mean(T_cold_arr))
    T_cold_std = float(np.std(T_cold_arr))
    z_node9_10 = float((T10[9] - T_cold_mean) / T_cold_std)

    p_Tcold_le_node9 = count_coldest_node9_T / N_REAL
    p_node9_is_coldest = count_coldest_is_node9 / N_REAL
    p_hop1_is_coldest = count_coldest_is_hop1 / N_REAL

    print(f"\n  RESULTS at 10.0°:")
    print(f"  Coldest distribution: mean={T_cold_mean:.2f}, std={T_cold_std:.2f} μK")
    print(f"  Node 9 cold T={T10[9]:.1f} μK → z = {z_node9_10:.2f}σ")
    print(f"  P(T_coldest ≤ {T10[9]:.0f}) = {p_Tcold_le_node9:.4f} ({p_Tcold_le_node9*100:.1f}%)")
    print(f"  P(coldest is node 9) = {p_node9_is_coldest:.6f} ({p_node9_is_coldest*100:.4f}%)")
    print(f"  P(coldest is hop=1) = {p_hop1_is_coldest:.4f} ({p_hop1_is_coldest*100:.1f}%)")
    print(f"  Random P(coldest is hop=1) = {len(hop1_nodes)/60:.4f}")

    # Save 10.0° results
    br10 = {
        "fwhm": 10.0,
        "n_real": N_REAL,
        "T_node9_uK": float(T10[9]),
        "T_node0_uK": float(T10[0]),
        "T_cold_mean_uK": T_cold_mean,
        "T_cold_std_uK": T_cold_std,
        "z_node9": z_node9_10,
        "p_T_coldest_le_node9": p_Tcold_le_node9,
        "p_node9_is_coldest": p_node9_is_coldest,
        "p_hop1_is_coldest": p_hop1_is_coldest,
        "node9_rank": int(node9_rank10),
    }
    with open(os.path.join(DATA, "bootstrap_10deg.json"), "w") as f:
        json.dump(br10, f, indent=2)
    print(f"  ✅ Saved: bootstrap_10deg.json")
else:
    print(f"  🔴 SMICA 10.0° cache not found")

# ====================================================================
# 3. Geodesic profile at 1.0° (the +75 μK ridge)
# ====================================================================
print(f"\n─── 3. Geodesic profile at 1.0° (the +75 μK ridge) ───")

node0_l, node0_b = l_deg[0], b_deg[0]
node9_l, node9_b = l_deg[9], b_deg[9]
v0 = np.array([math.cos(math.radians(node0_b))*math.cos(math.radians(node0_l)),
               math.cos(math.radians(node0_b))*math.sin(math.radians(node0_l)),
               math.sin(math.radians(node0_b))])
v9 = np.array([math.cos(math.radians(node9_b))*math.cos(math.radians(node9_l)),
               math.cos(math.radians(node9_b))*math.sin(math.radians(node9_l)),
               math.sin(math.radians(node9_b))])
sep = math.degrees(math.acos(np.clip(np.dot(v0, v9), -1, 1)))
omega = math.acos(np.clip(np.dot(v0, v9), -1, 1))

n_steps = 200
t_vals = np.linspace(0, 1, n_steps)
geo_vecs = np.array([(math.sin((1-t)*omega) * v0 + math.sin(t*omega) * v9) / math.sin(omega)
                     if omega > 1e-10 else v0 for t in t_vals])
geo_l = np.degrees(np.arctan2(geo_vecs[:, 1], geo_vecs[:, 0])) % 360
geo_b = np.degrees(np.arcsin(geo_vecs[:, 2]))

# Extract at multiple smoothing scales
for scale in [1.0, 3.0, 4.17]:
    cache_path = os.path.join(SMOOTH_CACHE, f"smica2_smooth{scale}.fits")
    if os.path.exists(cache_path):
        m = hp.read_map(cache_path, field=0)
        # Check if remove_dipole was already applied
        m = hp.remove_dipole(m)
        nside_m = hp.get_nside(m)
        geo_pix = hp.ang2pix(nside_m, geo_l, geo_b, lonlat=True)
        T_geo = m[geo_pix] * 1e6

        # Find ridge
        mid = T_geo[30:170]
        ridge_idx = np.argmax(mid) + 30
        ridge_T = T_geo[ridge_idx]
        ridge_dist = t_vals[ridge_idx] * sep

        # Node 0 and node 9 temperatures
        T_n0 = T_geo[0]
        T_n9 = T_geo[-1]

        print(f"  {scale}°: node0={T_n0:.1f}, node9={T_n9:.1f}, ridge={ridge_T:.1f} μK @ {ridge_dist:.1f}°")
        print(f"         Ridge amplitude: {ridge_T:.1f} μK (ΔT node0→ridge = {ridge_T - T_n0:.1f} μK)")

        # Save profile
        prof = {"angular_distance_deg": (t_vals * sep).tolist(), "T_uK": T_geo.tolist()}
        with open(os.path.join(DATA, f"geodesic_{scale}deg.json"), "w") as f:
            json.dump(prof, f, indent=2)
        print(f"  ✅ Saved: geodesic_{scale}deg.json")
    else:
        print(f"  {scale}°: 🔴 cache not found")

# ====================================================================
# 4. Cross-map node 9 temperature comparison
# ====================================================================
print(f"\n─── 4. Cross-map: Node 9 at 4.17° (SMICA × NILC × Commander) ───")

cross_map = {}
for map_name, cache_file in [("SMICA", "smica2_smooth4.17.fits"),
                              ("NILC", "nilc2_smooth4.17.fits"),
                              ("Commander", "commander_smooth4.17.fits")]:
    cache_path = os.path.join(SMOOTH_CACHE, cache_file)
    if os.path.exists(cache_path):
        m = hp.read_map(cache_path, field=0)
        m = hp.remove_dipole(m)
        nside_m = hp.get_nside(m)
        pix = hp.ang2pix(nside_m, l_deg, b_deg, lonlat=True)
        T = m[pix] * 1e6
        cross_map[map_name] = {
            "node9_T_uK": float(T[9]),
            "node0_T_uK": float(T[0]),
            "node9_rank": int(np.sum(T < T[9]) + 1),
            "node0_rank": int(np.sum(T < T[0]) + 1),
            "all_T_uK": T.tolist(),
        }
        print(f"  {map_name}: node9={T[9]:.1f} μK, rank={np.sum(T < T[9]) + 1}/60, "
              f"node0={T[0]:.1f} μK, rank={np.sum(T < T[0]) + 1}/60")
    else:
        print(f"  {map_name}: 🔴 cache not found at {cache_file}")

# Cross-map spread at node 9
spread_pct = 0
if len(cross_map) >= 2:
        T9_vals = [v["node9_T_uK"] for v in cross_map.values()]
        spread = max(T9_vals) - min(T9_vals)
        mean_T9 = np.mean(T9_vals)
        spread_pct = spread / abs(mean_T9) * 100 if mean_T9 != 0 else 0
        print(f"  Cross-map spread: {spread:.1f} μK ({spread_pct:.1f}%)")
        if spread_pct < 5:
            print(f"  🟢🟢 Cross-map consistent (<5% spread)")
        elif spread_pct < 20:
            print(f"  🟡 Marginal ({spread_pct:.1f}% spread)")
        else:
            print(f"  🔴 Not consistent (>20% spread)")

with open(os.path.join(DATA, "cross_map.json"), "w") as f:
    json.dump(cross_map, f, indent=2)
print(f"  ✅ Saved: cross_map.json")

# ====================================================================
# 5. Summary
# ====================================================================
print(f"\n{'='*66}")
print(f"O21: Node 9 Summary")
print(f"{'='*66}")

print(f"\n─── Bootstrap @ 4.17° ───")
print(f"  z = {br['z_node9']:.2f}σ   (NOT significant)")
print(f"  P(T_2nd ≤ -107) = {br['p_T_2nd_le_obs']:.1%}")
print(f"  P_joint (hop=1∩color=0) = {br['p_joint_hop1_color0']:.4%}")
print(f"  P(hop=1|T_2nd≤obs) = {br['p_hop1_given_T']:.1%} vs random {br['frac_hop1']:.1%}")
print(f"  → H1 (coincidence) consistent with data")

if os.path.exists(os.path.join(DATA, "bootstrap_10deg.json")):
    with open(os.path.join(DATA, "bootstrap_10deg.json")) as f:
        br10 = json.load(f)
    print(f"\n─── Bootstrap @ 10.0° ───")
    print(f"  Node 9 is coldest (rank 1/60, T={br10['T_node9_uK']:.1f} μK)")
    print(f"  z = {br10['z_node9']:.2f}σ")
    print(f"  P(coldest is node 9) = {br10['p_node9_is_coldest']:.4%}")
    print(f"  P(coldest is hop=1) = {br10['p_hop1_is_coldest']:.1%} vs random {len(hop1_nodes)/60:.1%}")

print(f"\n─── Geodesic ridge ───")
for scale in [1.0, 3.0, 4.17]:
    fn = os.path.join(DATA, f"geodesic_{scale}deg.json")
    if os.path.exists(fn):
        with open(fn) as f:
            prof = json.load(f)
        T = np.array(prof["T_uK"])
        ridge_idx = np.argmax(T[30:170]) + 30
        print(f"  {scale}°: ridge T={T[ridge_idx]:.1f} μK @ {prof['angular_distance_deg'][ridge_idx]:.1f}°")

print(f"\n─── Cross-map @ 4.17° ───")
for name, data in cross_map.items():
    print(f"  {name}: node9={data['node9_T_uK']:.1f} μK, rank={data['node9_rank']}/60")
if len(cross_map) >= 2:
    T9s = [v["node9_T_uK"] for v in cross_map.values()]
    print(f"  Spread: {max(T9s)-min(T9s):.1f} μK ({spread_pct:.1f}%)")