#!/usr/bin/env python3
"""
O102: Pentagon temperature — multi-scale, cross-map, permutation test
======================================================================
Build on the single-scale SMICA analysis: check if pentagon temperature
patterns are scale-dependent, consistent across maps, and statistically
significant.
"""
import os, math, json, glob
import numpy as np

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0"
CACHE = os.path.join(BASE, "open_problems_fresh", "o5_catalog_compare", "data", "smooth_cache")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O102: Pentagon temperature — multi-scale, cross-map, permutation")
print("=" * 72)

# ============================================================
# 1. Load pentagon geometry (same as before)
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

# ============================================================
# 2. Multi-scale SMICA analysis
# ============================================================
print("\n" + "=" * 72)
print("[1] Multi-scale SMICA pentagon face temperatures")
print("=" * 72)

scales = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 4.17, 5.0, 7.0, 10.0]
scale_results = {}

for s in scales:
    # Load smoothed map
    fname = f"smica2_smooth{s}.fits"
    fpath = os.path.join(CACHE, fname)
    if not os.path.exists(fpath):
        continue
    m = hp.read_map(fpath)
    nside = hp.get_nside(m)
    
    # Sample 60 nodes
    pix_nodes = hp.ang2pix(nside, nodes[:, 0], nodes[:, 1], lonlat=True)
    node_t = m[pix_nodes] * 1e6
    
    # Pentagon face temperature = mean of 5 vertices
    face_temps = np.array([np.mean([node_t[v] for v in verts]) for verts in pentagon_verts])
    centre_temps = []
    for i in range(12):
        pix = hp.ang2pix(nside, pc_ra[i], pc_dec[i], lonlat=True)
        centre_temps.append(m[pix] * 1e6)
    centre_temps = np.array(centre_temps)
    
    scale_results[s] = {
        'face_temps': face_temps,
        'centre_temps': centre_temps,
        'face_mean': float(np.mean(face_temps)),
        'face_std': float(np.std(face_temps)),
        'centre_mean': float(np.mean(centre_temps)),
        'centre_std': float(np.std(centre_temps))
    }
    
    # Find coldest and hottest pentagon at each scale
    coldest = np.argmin(face_temps)
    hottest = np.argmax(face_temps)
    print(f"  {s:>5}°: face mean={np.mean(face_temps):+6.1f}μK σ={np.std(face_temps):.1f}  "
          f"coldest=⬠{coldest}({face_temps[coldest]:+.1f}) hottest=⬠{hottest}({face_temps[hottest]:+.1f})")

# Check: which pentagon is consistently coldest/hottest across scales?
print(f"\n  Coldest pentagon at each scale:")
coldest_by_scale = {}
for s in scales:
    if s in scale_results:
        c = np.argmin(scale_results[s]['face_temps'])
        coldest_by_scale[s] = int(c)
        print(f"    {s:>5}°: ⬠{c}")
from collections import Counter
coldest_dist = Counter(coldest_by_scale.values())
print(f"  Coldest pentagon frequency: {dict(sorted(coldest_dist.items()))}")

print(f"\n  Hottest pentagon at each scale:")
hottest_by_scale = {}
for s in scales:
    if s in scale_results:
        h = np.argmax(scale_results[s]['face_temps'])
        hottest_by_scale[s] = int(h)
        print(f"    {s:>5}°: ⬠{h}")
hottest_dist = Counter(hottest_by_scale.values())
print(f"  Hottest pentagon frequency: {dict(sorted(hottest_dist.items()))}")

# ============================================================
# 3. Cross-map validation (SMICA vs NILC vs Commander at 4.17°)
# ============================================================
print("\n" + "=" * 72)
print("[2] Cross-map validation at 4.17° FWHM")
print("=" * 72)

maps = {
    'SMICA': os.path.join(CACHE, 'smica2_smooth4.17.fits'),
    'NILC': os.path.join(CACHE, 'nilc2_smooth4.17.fits'),
    'Commander': os.path.join(CACHE, 'commander_smooth4.17.fits')
}

cross_map_face = {}
cross_map_centre = {}

for name, fpath in maps.items():
    if not os.path.exists(fpath):
        print(f"  ⚠ {name} not found at {fpath}")
        continue
    m = hp.read_map(fpath)
    nside = hp.get_nside(m)
    
    # Sample 60 nodes
    pix_nodes = hp.ang2pix(nside, nodes[:, 0], nodes[:, 1], lonlat=True)
    node_t = m[pix_nodes] * 1e6
    
    # Face temps
    face_temps = np.array([np.mean([node_t[v] for v in verts]) for verts in pentagon_verts])
    cross_map_face[name] = face_temps
    
    # Centre temps
    centre_temps = []
    for i in range(12):
        pix = hp.ang2pix(nside, pc_ra[i], pc_dec[i], lonlat=True)
        centre_temps.append(m[pix] * 1e6)
    cross_map_centre[name] = np.array(centre_temps)

if len(cross_map_face) >= 2:
    names = list(cross_map_face.keys())
    print(f"\n  {'⬠':<4} ", end="")
    for n in names:
        print(f" {n:>10}", end="")
    print(f"  {'ΔE=0':>6} {'Σk':>4}")
    print(f"  {'-'*4} ", end="")
    for _ in names:
        print(f" {'-'*10}", end="")
    print(f" {'-'*6} {'-'*4}")
    
    for i in range(12):
        verts = pentagon_verts[i]
        nd = sum(1 for v in verts if v in k2_set)
        ks = sum(0 if v in k0_set else (1 if v in k1_set else 2) for v in verts)
        print(f"  ⬠{i:<2} ", end="")
        for n in names:
            print(f" {cross_map_face[n][i]:>+9.1f}μK", end="")
        print(f" {nd:>6} {ks:>4}")
    
    # Cross-map correlation
    print(f"\n  Cross-map face temperature correlations:")
    for i, n1 in enumerate(names):
        for n2 in names[i+1:]:
            from scipy import stats
            r, p = stats.pearsonr(cross_map_face[n1], cross_map_face[n2])
            print(f"    {n1} vs {n2}: r={r:.4f}, p={p:.4f}")

# ============================================================
# 4. Permutation test: are pentagon face temps significant?
# ============================================================
print("\n" + "=" * 72)
print("[3] Permutation test — pentagon face temps vs random 5-node groupings")
print("=" * 72)

# Load SMICA 4.17°
m = hp.read_map(os.path.join(CACHE, 'smica2_smooth4.17.fits'))
nside = hp.get_nside(m)
pix_nodes = hp.ang2pix(nside, nodes[:, 0], nodes[:, 1], lonlat=True)
node_t = m[pix_nodes] * 1e6

# Real pentagon face temps
real_face_temps = np.array([np.mean([node_t[v] for v in verts]) for verts in pentagon_verts])

# Permutation test: randomly assign 60 nodes into 12 groups of 5, compute face temps
# Repeat 10000 times, check if real variance is different from random
np.random.seed(42)
n_perm = 10000
real_var = np.var(real_face_temps)
real_max_minus_min = np.max(real_face_temps) - np.min(real_face_temps)

count_var_extreme = 0
count_range_extreme = 0
for perm in range(n_perm):
    # Shuffle node indices
    shuffled = np.random.permutation(60)
    # Reshape into 12 groups of 5
    groups = shuffled.reshape(12, 5)
    rand_temps = np.array([np.mean([node_t[v] for v in grp]) for grp in groups])
    rand_var = np.var(rand_temps)
    rand_range = np.max(rand_temps) - np.min(rand_temps)
    
    if rand_var >= real_var:
        count_var_extreme += 1
    if rand_range >= real_max_minus_min:
        count_range_extreme += 1

p_var = count_var_extreme / n_perm
p_range = count_range_extreme / n_perm

print(f"  Real pentagon face temp variance: {real_var:.2f} μK²")
print(f"  Real pentagon face temp range: {real_max_minus_min:.2f} μK")
print(f"  Permutation test (n={n_perm}):")
print(f"    Variance p = {p_var:.4f} ({'SIGNIFICANT' if p_var < 0.05 else 'NOT significant'})")
print(f"    Range p    = {p_range:.4f} ({'SIGNIFICANT' if p_range < 0.05 else 'NOT significant'})")

# Also test: are the pentagon groupings special compared to random groupings
# of the same 60 nodes? Check if the pentagon variance is lower than expected
# (pentagons should group nodes with similar T?)
print(f"\n  Direction: pentagon variance is {'' if real_var < np.median([np.var(np.mean(np.random.permutation(60).reshape(12,5), axis=1)) for _ in range(1000)]) else 'NOT '}lower than random")
print(f"  (Expected: pentagon groups nodes at ~26° separation, so variance should be LARGER than random)")

# ============================================================
# 5. Node-level temperature depth per pentagon
# ============================================================
print("\n" + "=" * 72)
print("[4] Node-level temperature depth per pentagon (SMICA 4.17°)")
print("=" * 72)

print(f"\n  {'⬠':<4} {'nodes':<24} {'face_T':>8} {'min':>8} {'max':>8} {'Δ':>8} {'ΔE=0':>6}")
print(f"  {'-'*4} {'-'*24} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*6}")
for i in range(12):
    verts = pentagon_verts[i]
    t_nodes = [node_t[v] for v in verts]
    nd = sum(1 for v in verts if v in k2_set)
    t_min = min(t_nodes)
    t_max = max(t_nodes)
    t_range = t_max - t_min
    print(f"  ⬠{i:<2} {str(verts):<24} {real_face_temps[i]:>+7.1f} {t_min:>+7.1f} {t_max:>+7.1f} {t_range:>7.1f} {nd:>6}")

# Find pentagon with largest internal ΔT
max_range_idx = np.argmax([max([node_t[v] for v in pentagon_verts[i]]) - min([node_t[v] for v in pentagon_verts[i]]) for i in range(12)])
print(f"\n  Largest internal ΔT: ⬠{max_range_idx} ({max([node_t[v] for v in pentagon_verts[max_range_idx]]) - min([node_t[v] for v in pentagon_verts[max_range_idx]]):.1f}μK)")

# ============================================================
# 6. Summary
# ============================================================
print("\n" + "=" * 72)
print("Summary")
print("=" * 72)

print(f"""
  ★ Multi-scale (0.5°-10.0°):
     Coldest pentagon: most freq ⬠{coldest_dist.most_common(1)[0][0]} ({coldest_dist.most_common(1)[0][1]}/{len(scales)} scales)
     Hottest pentagon: most freq ⬠{hottest_dist.most_common(1)[0][0]} ({hottest_dist.most_common(1)[0][1]}/{len(scales)} scales)

  ★ Cross-map correlation:
     {'Available' if len(cross_map_face) >= 2 else 'N/A'}

  ★ Permutation test:
     Variance p = {p_var:.4f}
     Range p = {p_range:.4f}
""")

# Save results
results = {
    'multi_scale': scale_results,
    'coldest_by_scale': {str(s): int(c) for s, c in coldest_by_scale.items()},
    'hottest_by_scale': {str(s): int(h) for s, h in hottest_by_scale.items()},
    'cross_map_face': {n: [float(t) for t in temps] for n, temps in cross_map_face.items()},
    'cross_map_centre': {n: [float(t) for t in temps] for n, temps in cross_map_centre.items()},
    'permutation_test': {'variance_p': float(p_var), 'range_p': float(p_range)},
    'node_level_temps': {
        str(i): {
            'verts': pentagon_verts[i],
            'temps': [float(node_t[v]) for v in pentagon_verts[i]],
            'face_t': float(real_face_temps[i])
        } for i in range(12)
    }
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

with open(os.path.join(out_dir, "pentagon_temperature_multi.json"), "w") as f:
    json.dump(results, f, indent=2, cls=NpEncoder)
print(f"Results saved to data/pentagon_temperature_multi.json")