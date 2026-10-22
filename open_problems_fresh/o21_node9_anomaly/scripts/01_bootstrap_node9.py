#!/usr/bin/env python3
"""
O21: Node 9 Bootstrap + Geodesic Profile + Cross-map
=====================================================
Phase 1: 10,000 GRF (Planck 2018 Cℓ via CAMB) → joint probability
Phase 2: Geodesic profile node 0 → node 9 (SMICA/NILC/Commander)
Phase 3: Cross-map comparison at node 9 position

Condition: P(T_2nd ≤ -106.99 μK AND hop=1 AND color=0)
"""

import numpy as np
import healpy as hp
import camb
from astropy.coordinates import SkyCoord
import astropy.units as u
import os, sys, math, time, json
from collections import defaultdict, deque

# ─── Config ────────────────────────────────────────────────────────
N_REAL = 10000
FWHM_DEG = 4.17
FWHM_RAD = np.radians(FWHM_DEG)
NSIDE_OUT = 64          # pixel ~0.92°, fine for 4.17° smoothing
BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
O21 = os.path.join(BASE, "o21_node9_anomaly")
SCRIPTS = os.path.join(O21, "scripts")
DATA = os.path.join(O21, "data")
os.makedirs(DATA, exist_ok=True)
os.makedirs(SCRIPTS, exist_ok=True)

# ─── 1. Load A₅ nodes ──────────────────────────────────────────────
nodes_file = os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")
nodes = np.loadtxt(nodes_file)  # (60, 2) RA, Dec

sc = SkyCoord(ra=nodes[:,0]*u.deg, dec=nodes[:,1]*u.deg, frame='icrs')
gal = sc.galactic
l_deg = np.array(gal.l.deg)
b_deg = np.array(gal.b.deg)

# Pixel indices at output nside
pix_out = hp.ang2pix(NSIDE_OUT, l_deg, b_deg, lonlat=True)

# ─── 2. Read SMICA power spectrum ──────────────────────────────────
print("=" * 66)
print("O21: Node 9 Bootstrap — GRF × 10,000")
print("=" * 66)

# Read SMICA 4.17° smoothed map and compute its power spectrum
# This ensures GRF matches SMICA's actual statistical properties
smica_path = os.path.join(BASE, "o5_catalog_compare/data/smooth_cache/smica2_smooth4.17.fits")
if not os.path.exists(smica_path):
    print(f"🔴 SMICA 4.17° cache not found at {smica_path}")
    sys.exit(1)

m_smica = hp.read_map(smica_path, field=0)
m_smica = hp.remove_dipole(m_smica)
# Convert to μK for Cℓ computation
m_smica_uK = m_smica * 1e6
nside_smica = hp.get_nside(m_smica)
print(f"SMICA 4.17°: nside={nside_smica}, std={m_smica_uK.std():.1f} μK")

# Compute Cℓ from SMICA map in μK (this is the beam-convolved power spectrum)
cl_data = hp.anafast(m_smica_uK, lmax=NSIDE_OUT*2)
# anafast returns Cℓ starting from ℓ=0
cl_input = np.zeros(len(cl_data))
cl_input[2:] = cl_data[2:]  # skip ℓ=0,1 (monopole, dipole)

# No additional beam convolution needed — Cℓ already includes 4.17° smoothing
cl_beam = cl_input.copy()

# Expected variance from Cℓ
ells = np.arange(len(cl_beam))
var_expected = np.sum((2*ells[2:] + 1) * cl_beam[2:] / (4*np.pi))
print(f"Cℓ from SMICA: ℓ_max={len(cl_data)-1}, expected σ={np.sqrt(var_expected):.1f} μK")

# ─── 3. Build BFS graph + coloring ─────────────────────────────────
vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])
adj = defaultdict(set)
for i in range(60):
    for j in range(i+1, 60):
        ang = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if ang < 28.0:
            adj[i].add(j)
            adj[j].add(i)

hop = {0: 0}
q = deque([0])
while q:
    u = q.popleft()
    for w in adj[u]:
        if w not in hop:
            hop[w] = hop[u] + 1
            q.append(w)
hop_arr = np.array([hop[i] for i in range(60)])

# Color from anchored_coloring.txt
color = {}
with open(os.path.join(BASE, "cmb_cold_spot/data/anchored_coloring.txt")) as f:
    for line in f:
        if line.startswith("#") or not line.strip(): continue
        parts = line.split()
        color[int(parts[0])] = int(parts[3])  # cold=1
color_arr = np.array([color[i] for i in range(60)])

# Observed temperatures
T_obs = np.loadtxt(os.path.join(BASE, "o3_node_temperatures/data/node_temps.txt"), skiprows=1)
T_obs_uK = T_obs[:, 2]

T_node9_obs = T_obs_uK[9]   # -106.99 μK
T_node0_obs = T_obs_uK[0]   # -134.19 μK

# Hop=1 neighbors of node 0 (nodes directly adjacent to cold spot)
hop1_nodes = [i for i in range(60) if hop_arr[i] == 1]
hop1_color0 = [i for i in hop1_nodes if color_arr[i] == 0]

print(f"\nA₅ network: 60 nodes, diameter={hop_arr.max()}")
print(f"Hop=1 neighbors of node 0: {hop1_nodes}")
print(f"  Node 9:  T={T_node9_obs:.2f} μK, color={color_arr[9]} (hot)")
print(f"  Node 20: T={T_obs_uK[20]:.2f} μK, color={color_arr[20]}")
print(f"  Node 41: T={T_obs_uK[41]:.2f} μK, color={color_arr[41]}")
print(f"  Node 50: T={T_obs_uK[50]:.2f} μK, color={color_arr[50]}")
print(f"Hop=1 ∩ color=0 nodes: {hop1_color0}")

# ─── 4. Bootstrap — 10,000 GRF ────────────────────────────────────
print(f"\n─── Phase 1: {N_REAL} GRF realizations ───")

t0 = time.time()
batch_size = 200
n_batches = N_REAL // batch_size

count_2nd_cold_le_obs = 0
count_2nd_cold_hop1 = 0
count_2nd_cold_hop1_color0 = 0
all_2nd_cold_temps = []
all_2nd_cold_indices = []
all_coldest_indices = []

for batch in range(n_batches):
    for i in range(batch_size):
        # Generate a_lm from beam-convolved Cℓ
        alm = hp.synalm(cl_beam, lmax=2*NSIDE_OUT, verbose=False)
        m = hp.alm2map(alm, nside=NSIDE_OUT, verbose=False)
        T = m[pix_out]  # μK (Cℓ was in μK²)

        # Order statistics
        sorted_idx = np.argsort(T)
        coldest = int(sorted_idx[0])
        second_coldest = int(sorted_idx[1])
        T_2nd = T[second_coldest]

        all_2nd_cold_temps.append(T_2nd)
        all_2nd_cold_indices.append(second_coldest)
        all_coldest_indices.append(coldest)

        # Condition: 2nd coldest ≤ -106.99 μK
        if T_2nd <= T_node9_obs:
            count_2nd_cold_le_obs += 1
            if hop_arr[second_coldest] == 1:
                count_2nd_cold_hop1 += 1
                if color_arr[second_coldest] == 0:
                    count_2nd_cold_hop1_color0 += 1

    elapsed = time.time() - t0
    rate = (batch + 1) * batch_size / elapsed
    remaining = (n_batches - batch - 1) * batch_size / rate
    print(f"  Batch {batch+1}/{n_batches}: {elapsed:.0f}s elapsed, {rate:.1f} real/s, ~{remaining:.0f}s remaining")

# ─── 5. Results ────────────────────────────────────────────────────
T_2nd_arr = np.array(all_2nd_cold_temps)
T_2nd_mean = float(np.mean(T_2nd_arr))
T_2nd_std = float(np.std(T_2nd_arr))
z_node9 = float((T_node9_obs - T_2nd_mean) / T_2nd_std)

p_T_le_obs = count_2nd_cold_le_obs / N_REAL
p_joint = count_2nd_cold_hop1_color0 / N_REAL
p_joint_percentile = (1 - np.searchsorted(np.sort(T_2nd_arr), T_node9_obs) / N_REAL)

# Conditional probability
p_hop1_given_T = count_2nd_cold_hop1 / count_2nd_cold_le_obs if count_2nd_cold_le_obs > 0 else 0
p_hop1_color0_given_T = count_2nd_cold_hop1_color0 / count_2nd_cold_le_obs if count_2nd_cold_le_obs > 0 else 0

# Expected fraction of hop=1 nodes among 60
frac_hop1 = len(hop1_nodes) / 60  # 4/60 = 0.0667
frac_hop1_color0 = len(hop1_color0) / 60  # 2/60 = 0.0333

print(f"\n{'='*66}")
print(f"RESULTS")
print(f"{'='*66}")
print(f"2nd coldest distribution: mean={T_2nd_mean:.2f} μK, std={T_2nd_std:.2f} μK")
print(f"Node 9 observed: {T_node9_obs:.2f} μK → z = {z_node9:.2f}σ")
print(f"Percentile: {p_joint_percentile:.4f} ({p_joint_percentile*100:.1f}%)")
print()
print(f"P(T_2nd ≤ {T_node9_obs:.1f} μK) = {p_T_le_obs:.6f}  ({count_2nd_cold_le_obs}/{N_REAL})")
print(f"P(T_2nd ≤ {T_node9_obs:.1f} AND hop=1) = {count_2nd_cold_hop1/N_REAL:.6f}  ({count_2nd_cold_hop1}/{N_REAL})")
print(f"P(hop=1 | T_2nd ≤ {T_node9_obs:.1f}) = {p_hop1_given_T:.4f}  (random: {frac_hop1:.4f})")
print()
print(f"★ P_joint = P(T_2nd ≤ {T_node9_obs:.1f} AND hop=1 AND color=0) = {p_joint:.6f}  ({count_2nd_cold_hop1_color0}/{N_REAL})")
print(f"  (random expectation: {frac_hop1_color0:.4f})")
print(f"  Enrichment vs random: {p_joint/frac_hop1_color0:.2f}×" if frac_hop1_color0 > 0 else "  N/A")

# ─── 6. Save GRF results ──────────────────────────────────────────
results_json = {
    "n_real": N_REAL,
    "fwhm_deg": FWHM_DEG,
    "nside": NSIDE_OUT,
    "T_node9_obs_uK": float(T_node9_obs),
    "T_2nd_mean_uK": T_2nd_mean,
    "T_2nd_std_uK": T_2nd_std,
    "z_node9": z_node9,
    "p_T_2nd_le_obs": p_T_le_obs,
    "p_joint_hop1_color0": p_joint,
    "p_hop1_given_T": p_hop1_given_T,
    "count_2nd_cold_le_obs": count_2nd_cold_le_obs,
    "count_2nd_cold_hop1_color0": count_2nd_cold_hop1_color0,
    "frac_hop1": frac_hop1,
    "frac_hop1_color0": frac_hop1_color0,
    "hop1_nodes": hop1_nodes,
    "hop1_color0_nodes": hop1_color0,
    "coldest_index_mode": int(max(set(all_coldest_indices), key=all_coldest_indices.count)),
    "T_2nd_percentile": float(p_joint_percentile),
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
}

with open(os.path.join(DATA, "bootstrap_results.json"), "w") as f:
    json.dump(results_json, f, indent=2)
print(f"\n✅ Saved: bootstrap_results.json")

# ─── 7. Geodesic profile node 0 → node 9 (Phase 2) ────────────────
print(f"\n─── Phase 2: Geodesic profile node 0 → node 9 ───")

# Node 0 and 9 positions (Galactic)
node0_l, node0_b = l_deg[0], b_deg[0]
node9_l, node9_b = l_deg[9], b_deg[9]

# Vector positions
v0 = np.array([math.cos(math.radians(node0_b))*math.cos(math.radians(node0_l)),
               math.cos(math.radians(node0_b))*math.sin(math.radians(node0_l)),
               math.sin(math.radians(node0_b))])
v9 = np.array([math.cos(math.radians(node9_b))*math.cos(math.radians(node9_l)),
               math.cos(math.radians(node9_b))*math.sin(math.radians(node9_l)),
               math.sin(math.radians(node9_b))])

# Great circle angular distance
sep = math.degrees(math.acos(np.clip(np.dot(v0, v9), -1, 1)))
print(f"Angular separation: {sep:.4f}° (expected ~26.17°)")

# Sample along geodesic
n_steps = 100
t_vals = np.linspace(0, 1, n_steps)

# Slerp interpolation
omega = math.acos(np.clip(np.dot(v0, v9), -1, 1))
geo_points = []
for t in t_vals:
    if omega < 1e-10:
        vi = v0
    else:
        vi = (math.sin((1-t)*omega) * v0 + math.sin(t*omega) * v9) / math.sin(omega)
    geo_points.append(vi)
geo_vecs = np.array(geo_points)

# Convert to l, b
geo_l = np.degrees(np.arctan2(geo_vecs[:, 1], geo_vecs[:, 0])) % 360
geo_b = np.degrees(np.arcsin(geo_vecs[:, 2]))

# Check if smoothed maps exist in cache
smooth_dir = os.path.join(BASE, "o5_catalog_compare/data/smooth_cache")
smica_cache = os.path.join(smooth_dir, "smica2_smooth4.17.fits")
nilc_cache = os.path.join(smooth_dir, "nilc2_smooth4.17.fits")
comm_cache = os.path.join(smooth_dir, "commander_smooth4.17.fits")

geo_profiles = {"angular_distance_deg": [], "SMICA_uK": None, "NILC_uK": None, "Commander_uK": None}

for map_name, cache_path in [("SMICA", smica_cache), ("NILC", nilc_cache), ("Commander", comm_cache)]:
    if os.path.exists(cache_path):
        m = hp.read_map(cache_path, field=0)
        nside_map = hp.get_nside(m)
        geo_pix = hp.ang2pix(nside_map, geo_l, geo_b, lonlat=True)
        T_geo = m[geo_pix] * 1e6
        geo_profiles[f"{map_name}_uK"] = T_geo.tolist()
        print(f"  {map_name}: ✅ geodesic profile extracted ({len(T_geo)} pts)")
    else:
        print(f"  {map_name}: 🔴 cache not found at {cache_path}")

geo_profiles["angular_distance_deg"] = (t_vals * sep).tolist()

# Find ridge: max temperature between node 0 and node 9
if geo_profiles.get("SMICA_uK"):
    T_arr = np.array(geo_profiles["SMICA_uK"])
    mid_region = T_arr[20:80]  # exclude endpoints
    ridge_idx = np.argmax(mid_region) + 20
    ridge_T = mid_region.max()
    ridge_dist = geo_profiles["angular_distance_deg"][ridge_idx]
    print(f"\n  +75 μK ridge: T={ridge_T:.1f} μK at d={ridge_dist:.1f}° from node 0")

with open(os.path.join(DATA, "geodesic_profiles.json"), "w") as f:
    json.dump(geo_profiles, f, indent=2)
print(f"✅ Saved: geodesic_profiles.json")

# ─── 8. Summary ─────────────────────────────────────────────────────
print(f"\n{'='*66}")
print(f"O21 Bootstrap Complete")
print(f"{'='*66}")
print(f"Key findings:")
print(f"  Node 9 z-score: {z_node9:.2f}σ among 2nd-coldest distribution")
print(f"  P(T_2nd ≤ {T_node9_obs:.1f}): {p_T_le_obs:.4f} ({p_T_le_obs*100:.1f}%)")
print(f"  P_joint (hop=1 ∩ color=0): {p_joint:.6f} ({p_joint*100:.4f}%)")
print(f"  Random expectation (hop=1 ∩ color=0): {frac_hop1_color0:.4f} ({frac_hop1_color0*100:.2f}%)")
print(f"  Enrichment: {p_joint/frac_hop1_color0:.1f}×" if frac_hop1_color0 > 0 else "  N/A")