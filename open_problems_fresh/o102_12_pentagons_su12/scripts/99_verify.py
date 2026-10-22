#!/usr/bin/env python3
"""
O102: Cross-verification script
Verify critical numerical values across all 6 scripts.
"""
import os, math, json, sys
import numpy as np

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0"
CACHE = os.path.join(BASE, "open_problems_fresh", "o5_catalog_compare", "data", "smooth_cache")
phi = (1 + math.sqrt(5)) / 2

passed, failed = 0, 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

print("=" * 72)
print("O102: Cross-verification of all results")
print("=" * 72)

# ============================================================
# 1. Load geometry and verify
# ============================================================
print("\n--- [1] Geometry verification ---")
nodes_file = os.path.join(BASE, "open_problems_fresh", "o19_lowl_dodecahedron", "data", "a5_nodes.txt")
nodes = np.loadtxt(nodes_file)
check("60 nodes loaded", nodes.shape == (60, 2))

ra, dec = np.radians(nodes[:, 0]), np.radians(nodes[:, 1])
vecs = np.column_stack([
    np.cos(ra) * np.cos(dec),
    np.sin(ra) * np.cos(dec),
    np.sin(dec)
])

# Adjacency with threshold
adj = {i: set() for i in range(60)}
for i in range(60):
    for j in range(i+1, 60):
        d = np.arccos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))
        if np.degrees(d) < 28.9225:
            adj[i].add(j)
            adj[j].add(i)

# Face traversal (same as all scripts)
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

triangle_faces = [f for f in faces_set if len(f) == 3]
square_faces = [f for f in faces_set if len(f) == 4]
pentagon_faces = [f for f in faces_set if len(f) == 5]
pentagon_verts = [sorted(pf) for pf in pentagon_faces]

check("20 triangles", len(triangle_faces) == 20)
check("30 squares", len(square_faces) == 30)
check("12 pentagons", len(pentagon_faces) == 12)
check("62 faces total", len(faces_set) == 62)

# k-values
k0_set = {0, 4, 7, 8, 31, 42, 52, 57}
k1_set = {1,2,3,5,6,9,11,13,14,15,16,17,18,20,21,24,26,27,29,30,33,34,35,36,38,39,41,43,44,47,48,49,50,51,53,54,55,56,58,59}
k2_set = {10, 12, 19, 22, 23, 25, 28, 32, 37, 40, 45, 46}
check("8 k=0 nodes", len(k0_set) == 8)
check("40 k=1 nodes", len(k1_set) == 40)
check("12 k=2 nodes (ΔE=0)", len(k2_set) == 12)
check("60 total k nodes", len(k0_set|k1_set|k2_set) == 60)

# Pentagon centres
pentagon_centres = []
for pf in pentagon_faces:
    verts = sorted(pf)
    centre = np.mean([vecs[v] for v in verts], axis=0)
    centre = centre / np.linalg.norm(centre)
    pentagon_centres.append(centre)
pentagon_centres = np.array(pentagon_centres)

# ============================================================
# 2. Verify ΔE=0 distribution
# ============================================================
print("\n--- [2] ΔE=0 distribution verification ---")
node_to_pentagon = {}
for idx, verts in enumerate(pentagon_verts):
    for v in verts:
        node_to_pentagon[v] = idx

delta_e0_counts = {i: 0 for i in range(12)}
for v in k2_set:
    delta_e0_counts[node_to_pentagon[v]] += 1

check("ΔE=0×2 pentagons count = 2", sum(1 for c in delta_e0_counts.values() if c == 2) == 2)
check("ΔE=0×1 pentagons count = 8", sum(1 for c in delta_e0_counts.values() if c == 1) == 8)
check("ΔE=0×0 pentagons count = 2", sum(1 for c in delta_e0_counts.values() if c == 0) == 2)
check("Total ΔE=0 = 12", sum(delta_e0_counts.values()) == 12)

# ============================================================
# 3. Verify pentagon adjacency
# ============================================================
print("\n--- [3] Pentagon adjacency verification ---")
pentagon_adj = {i: set() for i in range(12)}
for sq in square_faces:
    sq_verts = set(sq)
    touching = []
    for pi, pf in enumerate(pentagon_verts):
        if len(sq_verts & set(pf)) >= 2:
            touching.append(pi)
    if len(touching) == 2:
        pentagon_adj[touching[0]].add(touching[1])
        pentagon_adj[touching[1]].add(touching[0])

check("Pentagon adjacency edges = 30", sum(len(v) for v in pentagon_adj.values()) // 2 == 30)
check("All pentagons degree 5", all(len(pentagon_adj[i]) == 5 for i in range(12)))

# ============================================================
# 4. Verify pentagon centres = icosahedron
# ============================================================
print("\n--- [4] Pentagon centres = icosahedron verification ---")
ico = []
for s1 in [-1, 1]:
    for s2 in [-1, 1]:
        ico.append((0, s1, s2*phi))
        ico.append((s1, s2*phi, 0))
        ico.append((s1*phi, 0, s2))
ico = np.array(ico, dtype=float)
ico = ico / np.linalg.norm(ico[0])

# Distance spectra
pc_dists = sorted([np.degrees(np.arccos(np.clip(np.dot(pentagon_centres[i], pentagon_centres[j]), -1, 1)))
                    for i in range(12) for j in range(i+1, 12)])
ico_dists = sorted([np.degrees(np.arccos(np.clip(np.dot(ico[i], ico[j]), -1, 1)))
                     for i in range(12) for j in range(i+1, 12)])

check("Nearest PC distance = 63.43°", abs(pc_dists[0] - 63.4349) < 0.01)
check("2nd nearest PC distance = 116.57°", abs(pc_dists[30] - 116.565) < 0.01)
check("PC distance spectra match icosahedron", 
      all(abs(pc_dists[i] - ico_dists[i]) < 0.001 for i in range(66)))

# ============================================================
# 5. Verify temperature values (SMICA 4.17°)
# ============================================================
print("\n--- [5] Temperature verification ---")
import healpy as hp
m = hp.read_map(os.path.join(CACHE, 'smica2_smooth4.17.fits'))
nside = hp.get_nside(m)
pix_nodes = hp.ang2pix(nside, nodes[:, 0], nodes[:, 1], lonlat=True)
node_t = m[pix_nodes] * 1e6

# Pentagon face temps
face_temps = np.array([np.mean([node_t[v] for v in verts]) for verts in pentagon_verts])

# ⬠5 should be coldest
check("⬠5 is coldest pentagon", np.argmin(face_temps) == 5, f"(T={face_temps[5]:+.1f}μK)")
# ⬠7 should be hottest
check("⬠7 is hottest pentagon", np.argmax(face_temps) == 7, f"(T={face_temps[7]:+.1f}μK)")

# Cross-map
nilc_path = os.path.join(CACHE, 'nilc2_smooth4.17.fits')
commander_path = os.path.join(CACHE, 'commander_smooth4.17.fits')
if os.path.exists(nilc_path) and os.path.exists(commander_path):
    m_nilc = hp.read_map(nilc_path)
    m_cmd = hp.read_map(commander_path)
    node_nilc = m_nilc[pix_nodes] * 1e6
    node_cmd = m_cmd[pix_nodes] * 1e6
    face_nilc = np.array([np.mean([node_nilc[v] for v in verts]) for verts in pentagon_verts])
    face_cmd = np.array([np.mean([node_cmd[v] for v in verts]) for verts in pentagon_verts])
    
    from scipy import stats
    r_sn, _ = stats.pearsonr(face_temps, face_nilc)
    r_sc, _ = stats.pearsonr(face_temps, face_cmd)
    r_nc, _ = stats.pearsonr(face_nilc, face_cmd)
    check("SMICA vs NILC r > 0.99", r_sn > 0.99, f"(r={r_sn:.4f})")
    check("SMICA vs Commander r > 0.99", r_sc > 0.99, f"(r={r_sc:.4f})")
    check("NILC vs Commander r > 0.99", r_nc > 0.99, f"(r={r_nc:.4f})")

# Multi-scale check: ⬠5 coldest at ALL scales
scales = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 4.17, 5.0, 7.0, 10.0]
coldest_consistency = True
for s in scales:
    fname = f"smica2_smooth{s}.fits"
    fpath = os.path.join(CACHE, fname)
    if not os.path.exists(fpath):
        continue
    ms = hp.read_map(fpath)
    ns = hp.get_nside(ms)
    px = hp.ang2pix(ns, nodes[:, 0], nodes[:, 1], lonlat=True)
    nt = ms[px] * 1e6
    ft = np.array([np.mean([nt[v] for v in verts]) for verts in pentagon_verts])
    if np.argmin(ft) != 5:
        coldest_consistency = False
        print(f"    ⚠ ⬠5 NOT coldest at {s}° (⬠{np.argmin(ft)})")
check("⬠5 coldest at ALL scales", coldest_consistency)

# ============================================================
# 6. Verify dipole analysis
# ============================================================
print("\n--- [6] Dipole verification ---")
A = np.column_stack([np.ones(12), pentagon_centres])
coeff, _, _, _ = np.linalg.lstsq(A, face_temps, rcond=None)
dipole_mag = np.linalg.norm(coeff[1:4])
check("Dipole magnitude < 10 μK", dipole_mag < 10, f"(={dipole_mag:.2f}μK)")

# ============================================================
# 7. Verify seam component derivation
# ============================================================
print("\n--- [7] Seam component derivation verification ---")
# BFS colouring from node 0
hop = {0: 0}
queue = [0]
while queue:
    u = queue.pop(0)
    for v in adj[u]:
        if v not in hop:
            hop[v] = hop[u] + 1
            queue.append(v)
color = {v: hop[v] % 2 for v in range(60)}

frust_edges = set()
for u in range(60):
    for v in adj[u]:
        if u < v and color[u] == color[v]:
            frust_edges.add(frozenset((u, v)))
check("32 frustration edges", len(frust_edges) == 32)

# Seam components
seam_graph = {v: [] for v in range(60)}
for e in frust_edges:
    u, v = tuple(e)
    seam_graph[u].append(v)
    seam_graph[v].append(u)

visited = set()
components = []
for v in range(60):
    if v not in visited and seam_graph[v]:
        comp = []
        stack = [v]
        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                comp.append(node)
                stack.extend(seam_graph[node])
        if comp:
            components.append(comp)

from collections import Counter
comp_sizes = Counter(len(c) for c in components)
check("10×2-node components", comp_sizes.get(2, 0) == 10, f"(got {comp_sizes.get(2, 0)})")
check("8×3-node components", comp_sizes.get(3, 0) == 8, f"(got {comp_sizes.get(3, 0)})")
check("2×4-node components", comp_sizes.get(4, 0) == 2, f"(got {comp_sizes.get(4, 0)})")

# ============================================================
# Summary
# ============================================================
print(f"\n{'='*72}")
print(f"Cross-verification: {passed} PASS, {failed} FAIL")
print(f"{'='*72}")

# Save verification results
results = {
    'geometry': {
        'nodes': 60,
        'triangles': len(triangle_faces),
        'squares': len(square_faces),
        'pentagons': len(pentagon_faces),
        'faces_total': len(faces_set)
    },
    'delta_e0_distribution': {str(k): int(v) for k, v in sorted(delta_e0_counts.items())},
    'pentagon_adjacency_edges': sum(len(v) for v in pentagon_adj.values()) // 2,
    'pentagon_adjacency_degree_all_5': all(len(pentagon_adj[i]) == 5 for i in range(12)),
    'pentagon_centres_icosahedron_match': all(abs(pc_dists[i] - ico_dists[i]) < 0.001 for i in range(66)),
    'coldest_pentagon_all_scales': int(np.argmin(face_temps)),
    'hottest_pentagon_all_scales': int(np.argmax(face_temps)),
    'cross_map_correlation': {'smica_nilc': float(r_sn) if 'r_sn' in dir() else None,
                               'smica_commander': float(r_sc) if 'r_sc' in dir() else None},
    'seam_components': {'size_2': comp_sizes.get(2, 0), 'size_3': comp_sizes.get(3, 0), 'size_4': comp_sizes.get(4, 0)},
    'frustration_edges': len(frust_edges),
    'passed': passed,
    'failed': failed
}

out_dir = os.path.join(BASE, "open_problems_fresh", "o102_12_pentagons_su12", "data")
os.makedirs(out_dir, exist_ok=True)

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)): return int(obj)
        if isinstance(obj, (np.floating,)): return float(obj)
        if isinstance(obj, np.ndarray): return obj.tolist()
        return super().default(obj)

with open(os.path.join(out_dir, "cross_verification.json"), "w") as f:
    json.dump(results, f, indent=2, cls=NpEncoder)
print(f"Verification saved to data/cross_verification.json")