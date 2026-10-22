#!/usr/bin/env python3
"""
O102: Pentagon centre CMB temperature analysis on SMICA
========================================================
Sample pentagon centre temperatures, pentagon face temperatures,
and node temperatures from Planck SMICA map.
Check for temperature patterns related to ΔE=0 distribution.
"""
import os, math, json
import numpy as np

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0"
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O102: Pentagon CMB Temperature Analysis")
print("=" * 72)

# ============================================================
# 1. Load SMICA map
# ============================================================
smica_path = os.path.join(BASE, "open_problems_fresh", "o26_node57_region", "data", "smica_iqu_2048.fits")
smooth_cache = os.path.join(BASE, "open_problems_fresh", "o5_catalog_compare", "data", "smooth_cache")

# Try pre-smoothed 4.17° first
smooth_path = os.path.join(smooth_cache, "smica2_smooth4.17.fits")
if os.path.exists(smooth_path):
    import healpy as hp
    print(f"  Loading pre-smoothed SMICA from {smooth_path}")
    m_s = hp.read_map(smooth_path)
    nside = hp.get_nside(m_s)
    print(f"  nside={nside}, size={len(m_s)}")
elif os.path.exists(smica_path):
    import healpy as hp
    print(f"  Loading raw SMICA from {smica_path}")
    m = hp.read_map(smica_path, field=0)
    nside = hp.get_nside(m)
    print(f"  nside={nside}, size={len(m)}")
    # Smooth to 4.17° FWHM
    fwhm_rad = np.radians(4.17)
    sigma = fwhm_rad / (2 * np.sqrt(2 * np.log(2)))
    print(f"  Smoothing to 4.17° FWHM (sigma={np.degrees(sigma):.4f}°)")
    m_s = hp.remove_dipole(hp.smoothing(m, sigma=sigma))
else:
    print("  ❌ SMICA map not found!")
    print(f"  Tried: {smica_path}")
    print(f"  Tried: {smooth_path}")
    exit(1)

# ============================================================
# 2. Load 60-node network and pentagon data
# ============================================================
print("\n" + "=" * 72)
print("[1] Loading 60-node network and pentagon geometry")
print("=" * 72)

nodes_file = os.path.join(BASE, "open_problems_fresh", "o19_lowl_dodecahedron", "data", "a5_nodes.txt")
nodes = np.loadtxt(nodes_file)
ra, dec = np.radians(nodes[:, 0]), np.radians(nodes[:, 1])
vecs = np.column_stack([
    np.cos(ra) * np.cos(dec),
    np.sin(ra) * np.cos(dec),
    np.sin(dec)
])

# Adjacency
adj = {i: set() for i in range(60)}
for i in range(60):
    for j in range(i+1, 60):
        d = np.arccos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))
        if np.degrees(d) < 28.9225:
            adj[i].add(j)
            adj[j].add(i)

# Face traversal
ordered_neighbours = {}
for u in range(60):
    e1 = np.array([-vecs[u, 1], vecs[u, 0], 0.0])
    e1_norm = np.linalg.norm(e1)
    if e1_norm < 1e-10:
        e1 = np.array([1.0, 0.0, 0.0])
        e1 = e1 - np.dot(e1, vecs[u]) * vecs[u]
        e1_norm = np.linalg.norm(e1)
    e1 = e1 / e1_norm
    e2 = np.cross(vecs[u], e1)
    e2 = e2 / np.linalg.norm(e2)
    neighs = list(adj[u])
    angles = [(np.arctan2(np.dot(vecs[v], e2), np.dot(vecs[v], e1)), v) for v in neighs]
    angles.sort()
    ordered_neighbours[u] = [v for _, v in angles]

nxt = {}
for u in range(60):
    for idx, v in enumerate(ordered_neighbours[u]):
        v_neighs = ordered_neighbours[v]
        u_pos = v_neighs.index(u)
        w = v_neighs[(u_pos - 1) % len(v_neighs)]
        nxt[(u, v)] = (v, w)

faces_set = set()
remaining = set(nxt.keys())
while remaining:
    start_edge = next(iter(remaining))
    visited = set()
    path = []
    e = start_edge
    while e not in visited:
        visited.add(e)
        path.append(e[0])
        e = nxt.get(e)
        if e is None:
            break
    faces_set.add(frozenset(path))
    remaining -= visited

pentagon_faces = [f for f in faces_set if len(f) == 5]
print(f"  Pentagons: {len(pentagon_faces)}")

# k-values
k0_set = {0, 4, 7, 8, 31, 42, 52, 57}
k1_set = {1,2,3,5,6,9,11,13,14,15,16,17,18,20,21,24,26,27,29,30,33,34,35,36,38,39,41,43,44,47,48,49,50,51,53,54,55,56,58,59}
k2_set = {10, 12, 19, 22, 23, 25, 28, 32, 37, 40, 45, 46}
delta_e0 = k2_set

# Pentagon centres
pentagon_centres = []
pentagon_verts = []
for pf in pentagon_faces:
    verts = sorted(pf)
    pentagon_verts.append(verts)
    centre = np.mean([vecs[v] for v in verts], axis=0)
    centre = centre / np.linalg.norm(centre)
    pentagon_centres.append(centre)
pentagon_centres = np.array(pentagon_centres)

# Pentagon centre RA/Dec
pc_ra = np.degrees(np.arctan2(pentagon_centres[:, 1], pentagon_centres[:, 0])) % 360
pc_dec = np.degrees(np.arcsin(pentagon_centres[:, 2]))

# ============================================================
# 3. Sample temperatures
# ============================================================
print("\n" + "=" * 72)
print("[2] Pentagon centre temperatures (SMICA 4.17° FWHM)")
print("=" * 72)

# Sample pentagon centres
pix_pc = hp.ang2pix(nside, pc_ra, pc_dec, lonlat=True)
pc_temps = m_s[pix_pc] * 1e6  # μK

# Sample 60 nodes
pix_nodes = hp.ang2pix(nside, nodes[:, 0], nodes[:, 1], lonlat=True)
node_temps = m_s[pix_nodes] * 1e6

# Sample pentagon faces (mean of 5 vertices)
face_temps = []
for verts in pentagon_verts:
    face_temps.append(np.mean([node_temps[v] for v in verts]))
face_temps = np.array(face_temps)

# Cold spot temperature
cs_ra, cs_dec = 209, -57
pix_cs = hp.ang2pix(nside, cs_ra, cs_dec, lonlat=True)
cs_t = m_s[pix_cs] * 1e6

print(f"\n  {'⬠':<4} {'RA':>8} {'Dec':>8} {'centre T':>10} {'face T':>10} {'ΔE=0':>6} {'Σk':>4}")
print(f"  {'-'*4} {'-'*8} {'-'*8} {'-'*10} {'-'*10} {'-'*6} {'-'*4}")

pentagon_data = []
for i in range(12):
    verts = pentagon_verts[i]
    n_delta = sum(1 for v in verts if v in k2_set)
    k_sum = sum(0 if v in k0_set else (1 if v in k1_set else 2) for v in verts)
    pentagon_data.append({
        'idx': i, 'verts': verts, 'n_delta_e0': n_delta, 'k_sum': k_sum,
        'centre_t': pc_temps[i], 'face_t': face_temps[i]
    })
    print(f"  ⬠{i:<2} {pc_ra[i]:>8.2f} {pc_dec[i]:>8.2f} {pc_temps[i]:>+9.2f}μK {face_temps[i]:>+9.2f}μK {n_delta:>6} {k_sum:>4}")

print(f"\n  Cold spot: {cs_t:+.2f} μK")

# ============================================================
# 4. Temperature analysis by ΔE=0 group
# ============================================================
print("\n" + "=" * 72)
print("[3] Temperature by ΔE=0 group")
print("=" * 72)

# Group by ΔE=0 count
groups = {0: [], 1: [], 2: []}
for p in pentagon_data:
    groups[p['n_delta_e0']].append(p)

print(f"  Pentagon centre temperatures by ΔE=0 count:")
for n in [0, 1, 2]:
    temps = [p['centre_t'] for p in groups[n]]
    print(f"    ΔE=0×{n} ({len(groups[n])} pentagons): mean={np.mean(temps):+.2f}μK, std={np.std(temps):.2f}μK, range=[{min(temps):+.1f},{max(temps):+.1f}]")

print(f"\n  Pentagon face temperatures (mean of 5 vertices) by ΔE=0 count:")
for n in [0, 1, 2]:
    temps = [p['face_t'] for p in groups[n]]
    print(f"    ΔE=0×{n} ({len(groups[n])} pentagons): mean={np.mean(temps):+.2f}μK, std={np.std(temps):.2f}μK, range=[{min(temps):+.1f},{max(temps):+.1f}]")

# ============================================================
# 5. ⬠6 temperature analysis
# ============================================================
print("\n" + "=" * 72)
print("[4] ⬠6 anomaly — temperature analysis")
print("=" * 72)

p6 = pentagon_data[6]
print(f"  ⬠6 centre T: {p6['centre_t']:+.2f} μK")
print(f"  ⬠6 face T:   {p6['face_t']:+.2f} μK")
print(f"  ⬠6 vertices: {p6['verts']}")
print(f"  ⬠6 vertex temperatures:")
for v in p6['verts']:
    k = 0 if v in k0_set else (1 if v in k1_set else 2)
    print(f"    node {v}: T={node_temps[v]:+.2f} μK, k={k}")
print(f"  ⬠6 Σk={p6['k_sum']} (lowest in network)")

# Compare with all other pentagons
other_face_temps = [p['face_t'] for p in pentagon_data if p['idx'] != 6]
print(f"\n  Vs other 11 pentagons: mean={np.mean(other_face_temps):+.2f}μK, std={np.std(other_face_temps):.2f}μK")
print(f"  ⬠6 face T percentile: {sum(1 for t in other_face_temps if t < p6['face_t'])}/11")

# ============================================================
# 6. Pentagon temperature vs k-sum correlation
# ============================================================
print("\n" + "=" * 72)
print("[5] Temperature vs Σk correlation")
print("=" * 72)

# Pentagon centre T vs Σk
k_sums = np.array([p['k_sum'] for p in pentagon_data])
centre_T_vals = np.array([p['centre_t'] for p in pentagon_data])
face_T_vals = np.array([p['face_t'] for p in pentagon_data])

# Pearson correlation
from scipy import stats
r_centre, p_centre = stats.pearsonr(k_sums, centre_T_vals)
r_face, p_face = stats.pearsonr(k_sums, face_T_vals)

print(f"  Pentagon centre T vs Σk: r={r_centre:.4f}, p={p_centre:.4f}")
print(f"  Pentagon face T vs Σk:   r={r_face:.4f}, p={p_face:.4f}")

# Spearman (non-parametric)
rho_centre, sp_centre = stats.spearmanr(k_sums, centre_T_vals)
rho_face, sp_face = stats.spearmanr(k_sums, face_T_vals)
print(f"  Spearman R (centre): ρ={rho_centre:.4f}, p={sp_centre:.4f}")
print(f"  Spearman R (face):   ρ={rho_face:.4f}, p={sp_face:.4f}")

# ============================================================
# 7. 2-pentagon vs 0-pentagon temperature comparison
# ============================================================
print("\n" + "=" * 72)
print("[6] 2-pentagon vs 0-pentagon temperature comparison")
print("=" * 72)

two_pent = [p for p in pentagon_data if p['n_delta_e0'] == 2]
zero_pent = [p for p in pentagon_data if p['n_delta_e0'] == 0]

print(f"  2-pentagons (⬠{two_pent[0]['idx']}, ⬠{two_pent[1]['idx']}):")
for p in two_pent:
    print(f"    ⬠{p['idx']}: centre T={p['centre_t']:+.2f}μK, face T={p['face_t']:+.2f}μK")

print(f"\n  0-pentagons (⬠{zero_pent[0]['idx']}, ⬠{zero_pent[1]['idx']}):")
for p in zero_pent:
    print(f"    ⬠{p['idx']}: centre T={p['centre_t']:+.2f}μK, face T={p['face_t']:+.2f}μK")

# Difference
two_t = np.mean([p['centre_t'] for p in two_pent])
zero_t = np.mean([p['centre_t'] for p in zero_pent])
print(f"\n  2-pentagon mean: {two_t:+.2f}μK")
print(f"  0-pentagon mean: {zero_t:+.2f}μK")
print(f"  Difference: {two_t - zero_t:+.2f}μK")

# ============================================================
# 8. Full table
# ============================================================
print("\n" + "=" * 72)
print("[7] Complete temperature table")
print("=" * 72)

print(f"\n  {'⬠':<4} {'ΔE=0':>6} {'Σk':>4} {'centre_T':>9} {'face_T':>9} {'coldest':>8} {'hottest':>8}")
print(f"  {'-'*4} {'-'*6} {'-'*4} {'-'*9} {'-'*9} {'-'*8} {'-'*8}")
for p in pentagon_data:
    verts = p['verts']
    coldest = min(verts, key=lambda v: node_temps[v])
    hottest = max(verts, key=lambda v: node_temps[v])
    print(f"  ⬠{p['idx']:<2} {p['n_delta_e0']:>6} {p['k_sum']:>4} {p['centre_t']:>+8.1f} {p['face_t']:>+8.1f} {node_temps[coldest]:>+7.1f} {node_temps[hottest]:>+7.1f}")

# ============================================================
# 9. Summary
# ============================================================
print("\n" + "=" * 72)
print("Summary")
print("=" * 72)

print(f"""
  ★ Pentagon centre temperatures (SMICA 4.17°):
     Mean: {np.mean(centre_T_vals):+.2f} μK
     Std:  {np.std(centre_T_vals):.2f} μK
     Range: [{centre_T_vals.min():+.1f}, {centre_T_vals.max():+.1f}] μK

  ★ Pentagon face temperatures (mean of 5 vertices):
     Mean: {np.mean(face_T_vals):+.2f} μK
     Std:  {np.std(face_T_vals):.2f} μK
     Range: [{face_T_vals.min():+.1f}, {face_T_vals.max():+.1f}] μK

  ★ Cold spot: {cs_t:+.2f} μK

  ★ Correlation between Σk and temperature:
     Centre T: r={r_centre:.4f}, p={p_centre:.4f}
     Face T:   r={r_face:.4f}, p={p_face:.4f}

  ★ ⬠6 (lowest Σk=2): face T = {p6['face_t']:+.2f} μK
""")

# Save results
results = {
    'pentagon_centre_temps': {f'⬠{p["idx"]}': float(p['centre_t']) for p in pentagon_data},
    'pentagon_face_temps': {f'⬠{p["idx"]}': float(p['face_t']) for p in pentagon_data},
    'cold_spot_temp': float(cs_t),
    'correlation_centre_T_vs_Σk': {'r': float(r_centre), 'p': float(p_centre)},
    'correlation_face_T_vs_Σk': {'r': float(r_face), 'p': float(p_face)},
    'spearman_centre': {'rho': float(rho_centre), 'p': float(sp_centre)},
    'spearman_face': {'rho': float(rho_face), 'p': float(sp_face)}
}

out_dir = os.path.join(BASE, "open_problems_fresh", "o102_12_pentagons_su12", "data")
os.makedirs(out_dir, exist_ok=True)

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

with open(os.path.join(out_dir, "pentagon_temperatures.json"), "w") as f:
    json.dump(results, f, indent=2, cls=NpEncoder)
print(f"Results saved to data/pentagon_temperatures.json")