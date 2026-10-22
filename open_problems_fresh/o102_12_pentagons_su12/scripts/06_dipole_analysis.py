#!/usr/bin/env python3
"""
O102: Pentagon temperature — dipole/quadrupole fit, position analysis, node drivers
===================================================================================
Why is ⬠5 cold and ⬠7 hot? Is it just the CMB dipole, or is there structure?
"""
import os, math, json
import numpy as np

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0"
CACHE = os.path.join(BASE, "open_problems_fresh", "o5_catalog_compare", "data", "smooth_cache")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O102: Pentagon temperature — dipole analysis, position, node drivers")
print("=" * 72)

# ============================================================
# 1. Load geometry
# ============================================================
nodes_file = os.path.join(BASE, "open_problems_fresh", "o19_lowl_dodecahedron", "data", "a5_nodes.txt")
nodes = np.loadtxt(nodes_file)
ra, dec = np.radians(nodes[:, 0]), np.radians(nodes[:, 1])
vecs = np.column_stack([
    np.cos(ra) * np.cos(dec),
    np.sin(ra) * np.cos(dec),
    np.sin(dec)
])

adj = {i: set() for i in range(60)}
for i in range(60):
    for j in range(i+1, 60):
        d = np.arccos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))
        if np.degrees(d) < 28.9225:
            adj[i].add(j)
            adj[j].add(i)

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
pentagon_verts = [sorted(pf) for pf in pentagon_faces]

# Pentagon centres
pentagon_centres = []
for pf in pentagon_faces:
    verts = sorted(pf)
    centre = np.mean([vecs[v] for v in verts], axis=0)
    centre = centre / np.linalg.norm(centre)
    pentagon_centres.append(centre)
pentagon_centres = np.array(pentagon_centres)
pc_ra = np.degrees(np.arctan2(pentagon_centres[:, 1], pentagon_centres[:, 0])) % 360
pc_dec = np.degrees(np.arcsin(pentagon_centres[:, 2]))

# k-values
k0_set = {0, 4, 7, 8, 31, 42, 52, 57}
k1_set = {1,2,3,5,6,9,11,13,14,15,16,17,18,20,21,24,26,27,29,30,33,34,35,36,38,39,41,43,44,47,48,49,50,51,53,54,55,56,58,59}
k2_set = {10, 12, 19, 22, 23, 25, 28, 32, 37, 40, 45, 46}

import healpy as hp

# Load SMICA 4.17°
m = hp.read_map(os.path.join(CACHE, 'smica2_smooth4.17.fits'))
nside = hp.get_nside(m)
pix_nodes = hp.ang2pix(nside, nodes[:, 0], nodes[:, 1], lonlat=True)
node_t = m[pix_nodes] * 1e6
face_temps = np.array([np.mean([node_t[v] for v in verts]) for verts in pentagon_verts])

# ============================================================
# 2. Pentagon temperature map — dipole fit
# ============================================================
print("\n" + "=" * 72)
print("[1] Dipole fit to 12 pentagon temperatures")
print("=" * 72)

# Fit dipole to pentagon centre temperatures
# T(θ,φ) = T₀ + d·n̂ where d = dipole vector, n̂ = direction
# Use least squares: T_i = T₀ + d_x·n̂_ix + d_y·n̂_iy + d_z·n̂_iz

A = np.column_stack([np.ones(12), pentagon_centres])
coeff, residuals, rank, sv = np.linalg.lstsq(A, face_temps, rcond=None)
T0_dipole = coeff[0]
dipole_vec = coeff[1:4]

# Dipole magnitude and direction
dipole_mag = np.linalg.norm(dipole_vec)
dipole_ra = np.degrees(np.arctan2(dipole_vec[1], dipole_vec[0])) % 360
dipole_dec = np.degrees(np.arcsin(dipole_vec[2] / dipole_mag))

# Fitted temperatures
fitted_temps = A @ coeff
residual_temps = face_temps - fitted_temps

print(f"  Dipole magnitude: {dipole_mag:.2f} μK")
print(f"  Dipole direction: (RA={dipole_ra:.1f}°, Dec={dipole_dec:.1f}°)")
print(f"  Monopole T₀: {T0_dipole:+.2f} μK")
print(f"  Residual std: {np.std(residual_temps):.2f} μK")
print(f"  Original std: {np.std(face_temps):.2f} μK")

# Compare with CMB dipole (from Planck 2018)
# Planck 2018 dipole: 6.4 mK toward (264.0°, +48.3°) in Galactic
# In ICRS: roughly (168°, -7°) — but let's check
cmb_dipole_ra, cmb_dipole_dec = 168.0, -7.0  # approximate CMB dipole in ICRS
d_angle = np.degrees(np.arccos(np.clip(np.dot(
    dipole_vec / dipole_mag,
    np.array([math.cos(math.radians(cmb_dipole_ra))*math.cos(math.radians(cmb_dipole_dec)),
              math.sin(math.radians(cmb_dipole_ra))*math.cos(math.radians(cmb_dipole_dec)),
              math.sin(math.radians(cmb_dipole_dec))])
), -1, 1)))
print(f"\n  CMB dipole direction (approx ICRS): (RA={cmb_dipole_ra}°, Dec={cmb_dipole_dec}°)")
print(f"  Angular distance from CMB dipole: {d_angle:.1f}°")

# Check if the pentagon dipole is aligned with the 60-node dipole
# 60-node dipole
A60 = np.column_stack([np.ones(60), vecs])
coeff60, _, _, _ = np.linalg.lstsq(A60, node_t, rcond=None)
dipole60 = coeff60[1:4]
d60_mag = np.linalg.norm(dipole60)
d60_ra = np.degrees(np.arctan2(dipole60[1], dipole60[0])) % 360
d60_dec = np.degrees(np.arcsin(dipole60[2] / d60_mag))
print(f"\n  60-node dipole: magnitude={d60_mag:.2f}μK, direction=(RA={d60_ra:.1f}°, Dec={d60_dec:.1f}°)")

# Angle between dipoles
d_angle_60 = np.degrees(np.arccos(np.clip(np.dot(dipole_vec/dipole_mag, dipole60/d60_mag), -1, 1)))
print(f"  Pentagon dipole vs 60-node dipole: {d_angle_60:.1f}° apart")

# ============================================================
# 3. Quadrupole fit
# ============================================================
print("\n" + "=" * 72)
print("[2] Quadrupole + dipole fit")
print("=" * 72)

# Build quadrupole terms: n̂_i·n̂_j (5 independent components)
# Q = [n̂_x² - n̂_y², 2n̂_x·n̂_y, 2n̂_x·n̂_z, 2n̂_y·n̂_z, n̂_x²+n̂_y²-2n̂_z²] / √3
x, y, z = pentagon_centres[:, 0], pentagon_centres[:, 1], pentagon_centres[:, 2]
Q = np.column_stack([
    np.ones(12),
    x, y, z,  # dipole
    x**2 - y**2, 2*x*y, 2*x*z, 2*y*z, x**2 + y**2 - 2*z**2  # quadrupole
])
coeff_q, _, _, _ = np.linalg.lstsq(Q, face_temps, rcond=None)
fitted_q = Q @ coeff_q
residual_q = face_temps - fitted_q

print(f"  Dipole+quadrupole fit:")
print(f"    Residual std: {np.std(residual_q):.2f} μK")
print(f"    Original std: {np.std(face_temps):.2f} μK")
print(f"    Variance explained: {1 - np.var(residual_q)/np.var(face_temps):.1%}")

# Compare with dipole-only fit
print(f"  Dipole-only residual std: {np.std(residual_temps):.2f} μK")
print(f"  Dipole+quadrupole: {np.std(residual_q):.2f} μK")
print(f"  Improvement: {(1 - np.std(residual_q)/np.std(residual_temps)):.1%}")

# ============================================================
# 4. Individual pentagon analysis
# ============================================================
print("\n" + "=" * 72)
print("[3] Individual pentagon analysis")
print("=" * 72)

# ⬠5 analysis (coldest)
print(f"  ⬠5 (coldest, face T={face_temps[5]:+.1f}μK):")
print(f"    Vertices: {pentagon_verts[5]}")
for v in pentagon_verts[5]:
    k = 0 if v in k0_set else (1 if v in k1_set else 2)
    print(f"      node {v}: (RA={nodes[v,0]:.2f}°, Dec={nodes[v,1]:.2f}°), T={node_t[v]:+.1f}μK, k={k}")
print(f"    Centre: (RA={pc_ra[5]:.1f}°, Dec={pc_dec[5]:.1f}°)")

# ⬠7 analysis (hottest)
print(f"\n  ⬠7 (hottest, face T={face_temps[7]:+.1f}μK):")
print(f"    Vertices: {pentagon_verts[7]}")
for v in pentagon_verts[7]:
    k = 0 if v in k0_set else (1 if v in k1_set else 2)
    print(f"      node {v}: (RA={nodes[v,0]:.2f}°, Dec={nodes[v,1]:.2f}°), T={node_t[v]:+.1f}μK, k={k}")
print(f"    Centre: (RA={pc_ra[7]:.1f}°, Dec={pc_dec[7]:.1f}°)")

# ⬠4 analysis (contains cold spot)
print(f"\n  ⬠4 (contains cold spot node 0, face T={face_temps[4]:+.1f}μK):")
print(f"    Vertices: {pentagon_verts[4]}")
for v in pentagon_verts[4]:
    k = 0 if v in k0_set else (1 if v in k1_set else 2)
    print(f"      node {v}: (RA={nodes[v,0]:.2f}°, Dec={nodes[v,1]:.2f}°), T={node_t[v]:+.1f}μK, k={k}")

# ============================================================
# 5. Cold node distribution across pentagons
# ============================================================
print("\n" + "=" * 72)
print("[4] Coldest 12 nodes — pentagon distribution")
print("=" * 72)

# Sort 60 nodes by temperature
sorted_nodes = np.argsort(node_t)
print(f"  Coldest 12 nodes:")
for rank in range(12):
    v = sorted_nodes[rank]
    # Which pentagon?
    p_idx = next(i for i, verts in enumerate(pentagon_verts) if v in verts)
    print(f"    #{rank+1}: node {v} T={node_t[v]:+.1f}μK → ⬠{p_idx}")

# Check: are cold nodes clustered in a few pentagons?
cold_node_pentagons = [next(i for i, verts in enumerate(pentagon_verts) if v in verts) for v in sorted_nodes[:12]]
from collections import Counter
cold_dist = Counter(cold_node_pentagons)
print(f"\n  Coldest 12 nodes pentagon distribution: {dict(sorted(cold_dist.items()))}")
print(f"  Expected if uniform: ~1 per pentagon")

# Hot nodes
hot_node_pentagons = [next(i for i, verts in enumerate(pentagon_verts) if v in verts) for v in sorted_nodes[-12:]]
hot_dist = Counter(hot_node_pentagons)
print(f"\n  Hottest 12 nodes pentagon distribution: {dict(sorted(hot_dist.items()))}")

# ============================================================
# 6. Galactic plane proximity
# ============================================================
print("\n" + "=" * 72)
print("[5] Galactic plane proximity of pentagon vertices")
print("=" * 72)

# Convert node positions to galactic coordinates
from astropy.coordinates import SkyCoord
import astropy.units as u

for i in range(12):
    verts = pentagon_verts[i]
    # Check how many vertices are near the galactic plane (|b| < 20°)
    # Convert ICRS (RA, Dec) to Galactic
    coords = SkyCoord(ra=nodes[verts, 0]*u.degree, dec=nodes[verts, 1]*u.degree, frame='icrs')
    gal_b = coords.galactic.b.degree
    in_plane = sum(1 for b in gal_b if abs(b) < 20)
    print(f"  ⬠{i}: {in_plane}/5 vertices in galactic plane (|b|<20°), face T={face_temps[i]:+.1f}μK")

# ============================================================
# 7. Summary
# ============================================================
print("\n" + "=" * 72)
print("Summary")
print("=" * 72)

print(f"""
  ★ Dipole fit to 12 pentagon face temps:
     Magnitude: {dipole_mag:.2f} μK
     Direction: (RA={dipole_ra:.1f}°, Dec={dipole_dec:.1f}°)
     Distance from CMB dipole: {d_angle:.1f}°
     Distance from 60-node dipole: {d_angle_60:.1f}°

  ★ Dipole+quadrupole fit:
     Residual std: {np.std(residual_q):.2f} μK (from {np.std(face_temps):.2f} μK)
     Variance explained: {1 - np.var(residual_q)/np.var(face_temps):.1%}

  ★ Coldest 12 nodes pentagon distribution: {dict(sorted(cold_dist.items()))}
  ★ Hottest 12 nodes pentagon distribution: {dict(sorted(hot_dist.items()))}

  ★ Key driver of ⬠5 cold: node 26 ({node_t[26]:+.1f}μK at RA={nodes[26,0]:.1f}°,Dec={nodes[26,1]:.1f}°)
  ★ Key driver of ⬠7 hot: node 47 ({node_t[47]:+.1f}μK) and node 51 ({node_t[51]:+.1f}μK)
""")

# Save
results = {
    'dipole': {
        'magnitude_uK': float(dipole_mag),
        'direction_ra': float(dipole_ra),
        'direction_dec': float(dipole_dec),
        'monopole_uK': float(T0_dipole),
        'residual_std_uK': float(np.std(residual_temps)),
        'angle_from_cmb_dipole_deg': float(d_angle)
    },
    'dipole_quadrupole': {
        'residual_std_uK': float(np.std(residual_q)),
        'variance_explained': float(1 - np.var(residual_q)/np.var(face_temps))
    },
    'coldest_12_nodes_pentagon_dist': {str(k): int(v) for k, v in cold_dist.items()},
    'hottest_12_nodes_pentagon_dist': {str(k): int(v) for k, v in hot_dist.items()}
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

with open(os.path.join(out_dir, "pentagon_dipole_analysis.json"), "w") as f:
    json.dump(results, f, indent=2, cls=NpEncoder)
print(f"Results saved to data/pentagon_dipole_analysis.json")