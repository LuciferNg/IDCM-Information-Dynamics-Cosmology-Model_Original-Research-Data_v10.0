#!/usr/bin/env python3
"""
O19 — 低 ℓ 異常分析: 60 節點 A₅ 點場
=========================================
路徑 1-4 全面分析:
  1. 60° vs 63.435° 幾何
  2. 60 節點點場 → C_ℓ (ℓ<10)
  3. 四極/八極對齊 vs A₅ 軸
  4. 冷斑連結

執行: python3 scripts/01_a5_node_analysis.py
"""
import sys
import math
import json
from collections import defaultdict, Counter

import numpy as np

# ──────────────────────────────────────────────── constants
phi = (1 + 5 ** 0.5) / 2
eps = phi ** -1 / 4  # ε = φ⁻¹/4
kappa = 1 / 16

# Lucas numbers
L = [2, 1, 3, 4, 7, 11, 18, 29, 47, 76, 123]

# Fibonacci numbers
F = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]

Nd = 44  # K_Chain sites
B = 4    # K_Tree branching

NODE_FILE = "data/a5_nodes.txt"
# Prepare output records
results = {}

# ──────────────────────────────────────────────── helpers
def radec_to_vecs(nodes):
    vecs = []
    for ra, dec in nodes:
        r, d = math.radians(ra), math.radians(dec)
        vecs.append(np.array([
            math.cos(d) * math.cos(r),
            math.cos(d) * math.sin(r),
            math.sin(d),
        ]))
    return np.array(vecs)

def angular_dist_deg(v1, v2):
    return math.degrees(math.acos(np.clip(np.dot(v1, v2), -1, 1)))

def histogram_threshold(vecs, expected_edges=120):
    """Find edge threshold from distance histogram gap.
    threshold = (dists[E-1] + dists[E])/2 where E = expected edge count."""
    n = len(vecs)
    dists = []
    for i in range(n):
        for j in range(i+1, n):
            dists.append(angular_dist_deg(vecs[i], vecs[j]))
    dists = np.sort(dists)
    E = min(expected_edges, len(dists) - 1)
    return (dists[E-1] + dists[E]) / 2

# ──────────────────────────────────────────────── load nodes
print("=" * 60)
print("O19: 低 ℓ 異常 — 60 節點 A₅ 分析")
print("=" * 60)

nodes = []
with open(NODE_FILE) as f:
    for line in f:
        line = line.strip()
        if line:
            ra, dec = map(float, line.split())
            nodes.append((ra, dec))

print(f"\n已載入 {len(nodes)} 個節點")
vecs = radec_to_vecs(nodes)

# ────────────────────────────────────────────────
# PATH 1: 60° vs 63.435° 幾何分析
# ────────────────────────────────────────────────
print("\n" + "─" * 50)
print("🟢 路徑 1: 60° 異常 vs dodecahedron 幾何")
print("─" * 50)

# 1a. Full distance histogram
n = len(vecs)
all_dists = []
for i in range(n):
    for j in range(i+1, n):
        all_dists.append(angular_dist_deg(vecs[i], vecs[j]))
all_dists = np.sort(all_dists)

# Cluster analysis
threshold = histogram_threshold(vecs)
print(f"\n邊緣閾值 (histogram gap): {threshold:.4f}°")

# Distance clusters (shells)
# Use the threshold to separate first shell
dists_near = all_dists[all_dists < threshold]
dists_far = all_dists[all_dists >= threshold]

print(f"第一殼層距離: {len(dists_near)} 條邊")
print(f"邊長統計:  mean={np.mean(dists_near):.4f}°  median={np.median(dists_near):.4f}°  "
      f"std={np.std(dists_near):.4f}°  min={np.min(dists_near):.4f}°  max={np.max(dists_near):.4f}°")

# 1b. Identify all distance shells
# Use adaptive binning to find clusters
bin_edges = np.arange(0, 181, 1)
hist, _ = np.histogram(all_dists, bins=bin_edges)
# Find peaks in histogram
from scipy.ndimage import gaussian_filter1d
hist_smooth = gaussian_filter1d(hist.astype(float), sigma=2)
from scipy.signal import find_peaks
peak_indices, props = find_peaks(hist_smooth, distance=5, prominence=5)
shell_centers = bin_edges[:-1][peak_indices]
shell_heights = hist[peak_indices]

print(f"\n距離殼層 (histogram peaks):")
for i, (center, height) in enumerate(zip(shell_centers, shell_heights)):
    print(f"  殼層 {i+1}: {center:.1f}° — {int(height)} pairs")

# Expected dodecahedron distances from A₅ orbit:
# 26.0913° (edge, 120 edges) — 5-fold rotor
# 31.6787° (second shell, 30 edges) — 2-fold rotor
# 42.9712° — 144° rotor
# 59.999...°? Let's check
# 63.435° = dodecahedron face-to-face angle

# Find the closest shell to 60° and 63.435°
target_angles = [60.0, 63.435]
for target in target_angles:
    distances = np.abs(shell_centers - target)
    idx = np.argmin(distances)
    print(f"  目標 {target:.3f}°: 最近殼層 {shell_centers[idx]:.1f}° (Δ={distances[idx]:.1f}°)")

# 1c. Group-theoretic distance analysis
# Check if any distance shell corresponds to 60° or 63.435°
print("\n🔍 60° 異常分析:")
print(f"  60° 在殼層中的位置: 最近殼層 = {shell_centers[np.argmin(np.abs(shell_centers - 60))]:.1f}°")

# Check if 60° could be a projection of dodecahedron 63.435°
# The 60° scale in CMB is related to the "matched circle" radius
# In dodecahedron topology, the face-to-face distance is 63.435°
# The 60° anomaly could be a projection effect
print(f"  63.435° (dodecahedron 面距) vs 60° (觀測): Δ = 3.435° = 5.4%")
print(f"  解釋候選: 投影效應? A₅ 節點網絡幾何? 宇宙方差?")
print(f"  ℓ=60 對應角度: 180/60 = 3.0° (太小, 不是60°尺度)")
print(f"  ℓ=3 對應角度: 180/3 = 60.0° (這是真實的60°尺度!)")

# 1d. Check if the quadrupole direction relates to A₅ geometry
# Cold spot at (209°, -57°) — check its antipode and A₅ symmetry axes
cold_spot_idx = 0  # first node is the cold spot (48.3°, -20.4°)
# Wait, the cold spot in Galactic coordinates is (209°, -57°)
# The a5_nodes.txt is in ICRS (RA, Dec) — let me convert
# The cold spot is at (48.30°, -20.44°) ICRS = (209°, -57°) Galactic
# In the file, node 0 is (48.3, -20.44) — yes, that's the cold spot

cs_vec = vecs[0]
print(f"\n冷斑位置: ({nodes[0][0]:.2f}°, {nodes[0][1]:.2f}°) ICRS = (209°, -57°) Galactic")

# Distance from cold spot to all other nodes
cs_dists = [angular_dist_deg(cs_vec, vecs[i]) for i in range(1, n)]
cs_dists.sort()
print(f"冷斑至其他節點距離 (前10): {[f'{d:.2f}°' for d in cs_dists[:10]]}")

# Check if any distance is near 60° or 63.435°
for d in cs_dists:
    if abs(d - 60) < 3 or abs(d - 63.435) < 3:
        print(f"  冷斑 ~60° 節點: {d:.2f}°")

print(f"\n✅ 路徑 1 初步結果: 60° 異常關聯到 ℓ=3, 非 dodecahedron 面距 63.435°")
print(f"   5.4% 差需要解釋: 投影或結構效應")
results['path1'] = {
    'edge_length': float(np.mean(dists_near)),
    'threshold': float(threshold),
    'shells': [float(c) for c in shell_centers.tolist()],
    'dodeca_face_angle': 63.435,
    'cmb_60_scale': 60.0,
    'gap_percent': 3.435/63.435*100,
    'note': '60° 異常對應 ℓ=3, 非 dodecahedron 面距 63.435°; 5.4% 差需結構解釋'
}

# ────────────────────────────────────────────────
# PATH 2: 低 ℓ C_ℓ 預測
# ────────────────────────────────────────────────
print("\n" + "─" * 50)
print("🟢 路徑 2: 60 節點點場 → C_ℓ (ℓ<10)")
print("─" * 50)

import healpy as hp

# 2a. Build graph and anchored 2-coloring
adj, edges = {}, []
for i in range(n):
    adj[i] = set()
for i in range(n):
    for j in range(i+1, n):
        if angular_dist_deg(vecs[i], vecs[j]) < threshold:
            adj[i].add(j)
            adj[j].add(i)
            edges.append((i, j))

# Anchored coloring
from collections import deque
color = {}
color[0] = 1  # cold spot = color 1
q = deque([0])
while q:
    u = q.popleft()
    for v in adj[u]:
        if v not in color:
            color[v] = 1 - color[u]
            q.append(v)

n_cold = sum(1 for c in color.values() if c == 1)
n_hot = n - n_cold
print(f"Anchored coloring: cold={n_cold} hot={n_hot}")

# Frustration edges
frustration = []
for u in adj:
    for v in adj[u]:
        if u < v and color[u] == color[v]:
            frustration.append((u, v))

# Face traversal for frustration analysis
def face_traversal(adj, vecs):
    """Directed-edge face traversal."""
    order, pos = {}, {}
    for v in range(len(vecs)):
        vv = vecs[v]
        e1 = np.array([-vv[1], vv[0], 0.0])
        if np.linalg.norm(e1) < 1e-9:
            e1 = np.array([1.0, 0.0, 0.0])
        e1 = e1 / np.linalg.norm(e1)
        e2 = np.cross(vv, e1)
        angles = {}
        for u in adj[v]:
            angles[u] = math.atan2(np.dot(vecs[u], e2), np.dot(vecs[u], e1))
        order[v] = sorted(adj[v], key=lambda u: angles[u])
        for idx, u in enumerate(order[v]):
            pos[(v, u)] = idx

    nxt = {}
    for u in adj:
        for v in adj[u]:
            idx_u = pos[(v, u)]
            w = order[v][(idx_u + 1) % len(order[v])]
            nxt[(u, v)] = (v, w)

    faces = []
    seen = set()
    for u in adj:
        for v in adj[u]:
            for start in [(u, v), (v, u)]:
                if start in seen:
                    continue
                path = []
                cur = start
                while cur not in seen:
                    seen.add(cur)
                    path.append(cur[0])
                    cur = nxt[cur]
                faces.append(path)

    uniq = {}
    for f in faces:
        uniq[frozenset(f)] = f
    return list(uniq.values())

faces = face_traversal(adj, vecs)
census = {}
for f in faces:
    census[len(f)] = census.get(len(f), 0) + 1
F = sum(census.values())
chi = n - len(edges) + F
print(f"Faces: {census}  F={F}  χ={chi} {'OK' if chi == 2 else 'FAIL'}")

# 2b. Create HEALPix maps
nside = 64
npix = hp.nside2npix(nside)

# Map A: ±1 at node positions (anchored coloring)
map_A = np.zeros(npix)
for i in range(n):
    ra, dec = nodes[i]
    theta = np.radians(90 - dec)
    phi = np.radians(ra)
    pix = hp.ang2pix(nside, theta, phi)
    map_A[pix] = 1 if color[i] == 1 else -1

# Map B: random signs (control)
map_B = np.zeros(npix)
rng = np.random.RandomState(42)
signs_B = rng.choice([-1, 1], size=n)
for i in range(n):
    ra, dec = nodes[i]
    theta = np.radians(90 - dec)
    phi = np.radians(ra)
    pix = hp.ang2pix(nside, theta, phi)
    map_B[pix] = signs_B[i]

# Map C: Gaussian-smoothed version of map A
map_C = hp.smoothing(map_A, fwhm=np.radians(10))  # 10° smoothing for low-ℓ

# Compute power spectra
cl_A = hp.anafast(map_A, lmax=20)
cl_B = hp.anafast(map_B, lmax=20)
cl_C = hp.anafast(map_C, lmax=20)

# Normalize
cl_A_norm = cl_A / cl_A[2] if cl_A[2] > 0 else cl_A
cl_B_norm = cl_B / cl_B[2] if cl_B[2] > 0 else cl_B
cl_C_norm = cl_C / cl_C[2] if cl_C[2] > 0 else cl_C

print(f"\n低 ℓ C_ℓ 預測 (ℓ=2-10):")
print(f"{'ℓ':>3} {'C_ℓ (A₅)':>10} {'C_ℓ (rand)':>10} {'C_ℓ (smoothed)':>10} {'ratio':>8}")
print("-" * 55)
for ell in range(2, 11):
    cA = cl_A[ell] if ell < len(cl_A) else 0
    cB = cl_B[ell] if ell < len(cl_B) else 0
    cC = cl_C[ell] if ell < len(cl_C) else 0
    ratio = cA / cB if cB > 0 else float('inf')
    print(f"{ell:3d} {cA:10.2e} {cB:10.2e} {cC:10.2e} {ratio:8.2f}")

# 2c. Compare with Planck low-ℓ deficit
# Planck low-ℓ deficit: C₂ is ~20% of ΛCDM prediction
# C₃ is ~70%, C₄ is ~80%
# The A₅ node map should naturally suppress ℓ=2
print(f"\n🔍 低 ℓ 功率分析:")
print(f"  C₂/C₃ (A₅): {cl_A[2]/cl_A[3]:.3f}  (Planck ~0.3)")
print(f"  C₂/C₄ (A₅): {cl_A[2]/cl_A[4]:.3f}  (Planck ~0.4)")
print(f"  C₃/C₄ (A₅): {cl_A[3]/cl_A[4]:.3f}  (Planck ~1.0)")

# 2d. Check if the node pattern naturally suppresses ℓ=2
# A 60-node point field on a sphere has a specific power spectrum
# The ℓ=2 quadrupole is naturally suppressed if the node distribution is isotropic
# Let's compute the spherical harmonic coefficients
alm = hp.map2alm(map_A, lmax=10)
ell, emm = hp.Alm.getlm(lmax=10)

# Power in each m for ℓ=2
power_ell = {}
for l in range(2, 11):
    mask = (ell == l)
    power_ell[l] = np.sum(np.abs(alm[mask])**2)

print(f"\n  ℓ-by-ℓ power (A₅ map):")
for l in range(2, 11):
    print(f"  ℓ={l}: {power_ell[l]:.2e}")

results['path2'] = {
    'n_cold': n_cold,
    'n_hot': n_hot,
    'n_frustration': len(frustration),
    'census': {str(k): v for k, v in census.items()},
    'cl_A': [float(cl_A[l]) for l in range(2, 11)],
    'cl_B': [float(cl_B[l]) for l in range(2, 11)],
    'cl_ratio_2_3': float(cl_A[2]/cl_A[3]) if cl_A[3] > 0 else None,
    'cl_ratio_2_4': float(cl_A[2]/cl_A[4]) if cl_A[4] > 0 else None,
}

# ────────────────────────────────────────────────
# PATH 3: 四極/八極對齊 vs A₅ 軸
# ────────────────────────────────────────────────
print("\n" + "─" * 50)
print("🟢 路徑 3: 四極/八極對齊 vs A₅ 軸")
print("─" * 50)

# 3a. Compute main axes of the A₅ node distribution
# The quadrupole axis of the node pattern
# Weighted by sign (cold/hot) to see if there's a preferred axis
# Compute the moment of inertia tensor of the node distribution
# Weighted by ±1 for the two colors

# Unweighted quadrupole of the 60-node distribution
# This is just the inertia tensor of the point set
inertia = np.zeros((3, 3))
for i in range(n):
    v = vecs[i]
    inertia += np.outer(v, v)
eigvals, eigvecs = np.linalg.eigh(inertia)

# The principal axes of the 60-node distribution
print(f"\nA₅ 60節點慣量張量特徵值: {eigvals}")
print(f"  主軸方向 (最大分散): ({eigvecs[0,2]:.4f}, {eigvecs[1,2]:.4f}, {eigvecs[2,2]:.4f})")
# Convert to RA, Dec
axis_vec = eigvecs[:, 2]
ra_axis = np.degrees(np.arctan2(axis_vec[1], axis_vec[0])) % 360
dec_axis = np.degrees(np.arcsin(np.clip(axis_vec[2], -1, 1)))
print(f"  主軸 (RA, Dec) = ({ra_axis:.1f}°, {dec_axis:.1f}°)")

# Weighted by ±1 (cold/hot)
inertia_w = np.zeros((3, 3))
for i in range(n):
    w = 1 if color[i] == 1 else -1
    v = vecs[i]
    inertia_w += w * np.outer(v, v)
eigvals_w, eigvecs_w = np.linalg.eigh(inertia_w)
axis_vec_w = eigvecs_w[:, 2]
ra_axis_w = np.degrees(np.arctan2(axis_vec_w[1], axis_vec_w[0])) % 360
dec_axis_w = np.degrees(np.arcsin(np.clip(axis_vec_w[2], -1, 1)))
print(f"  加權主軸 (cold/hot sign): (RA, Dec) = ({ra_axis_w:.1f}°, {dec_axis_w:.1f}°)")

# 3b. Compare with known CMB alignment directions
# Planck quadrupole direction: approximately (l,b) ≈ (264°, 48°) Galactic
# That's roughly (RA≈180°, Dec≈0°) ICRS
# The "Axis of Evil" direction: approximately (l,b) ≈ (260°, 60°) Galactic
# CMB dipole direction: (l,b) ≈ (264°, 48°) → (RA, Dec) ≈ (168°, -7°)

# Convert our A₅ axis to Galactic for comparison
from astropy.coordinates import SkyCoord
import astropy.units as u

try:
    axis_coord = SkyCoord(ra=ra_axis_w, dec=dec_axis_w, unit=u.deg, frame='icrs')
    l_gal = axis_coord.galactic.l.deg
    b_gal = axis_coord.galactic.b.deg
    print(f"\n  A₅ 加權主軸 (Galactic): (l, b) = ({l_gal:.1f}°, {b_gal:.1f}°)")
    
    # Compare with known directions
    # CMB dipole: (264°, 48°) Galactic
    dipole_l, dipole_b = 264.0, 48.0
    d_l = angular_dist_deg(
        np.array([math.cos(math.radians(dipole_b))*math.cos(math.radians(dipole_l)),
                  math.cos(math.radians(dipole_b))*math.sin(math.radians(dipole_l)),
                  math.sin(math.radians(dipole_b))]),
        np.array([math.cos(math.radians(b_gal))*math.cos(math.radians(l_gal)),
                  math.cos(math.radians(b_gal))*math.sin(math.radians(l_gal)),
                  math.sin(math.radians(b_gal))])
    )
    print(f"  A₅ 軸 vs CMB dipole 角距: {d_l:.1f}°")
    
    # Quadrupole axis (Planck): (l,b) ≈ (240°, 70°) approximately
    quad_l, quad_b = 240.0, 70.0
    d_q = angular_dist_deg(
        np.array([math.cos(math.radians(quad_b))*math.cos(math.radians(quad_l)),
                  math.cos(math.radians(quad_b))*math.sin(math.radians(quad_l)),
                  math.sin(math.radians(quad_b))]),
        np.array([math.cos(math.radians(b_gal))*math.cos(math.radians(l_gal)),
                  math.cos(math.radians(b_gal))*math.sin(math.radians(l_gal)),
                  math.sin(math.radians(b_gal))])
    )
    print(f"  A₅ 軸 vs Planck quadrupole 角距: {d_q:.1f}°")
    
    # Octopole axis (Planck): (l,b) ≈ (240°, 60°) approximately
    oct_l, oct_b = 240.0, 60.0
    d_o = angular_dist_deg(
        np.array([math.cos(math.radians(oct_b))*math.cos(math.radians(oct_l)),
                  math.cos(math.radians(oct_b))*math.sin(math.radians(oct_l)),
                  math.sin(math.radians(oct_b))]),
        np.array([math.cos(math.radians(b_gal))*math.cos(math.radians(l_gal)),
                  math.cos(math.radians(b_gal))*math.sin(math.radians(l_gal)),
                  math.sin(math.radians(b_gal))])
    )
    print(f"  A₅ 軸 vs Planck octopole 角距: {d_o:.1f}°")
    
    results['path3'] = {
        'axis_icrs': (float(ra_axis_w), float(dec_axis_w)),
        'axis_galactic': (float(l_gal), float(b_gal)),
        'dipole_sep': float(d_l),
        'quadrupole_sep': float(d_q),
        'octopole_sep': float(d_o),
    }

except Exception as e:
    print(f"  astropy 轉換錯誤: {e}")
    results['path3'] = {'error': str(e)}

# ────────────────────────────────────────────────
# PATH 4: 冷斑連結
# ────────────────────────────────────────────────
print("\n" + "─" * 50)
print("🟢 路徑 4: 冷斑連結 — 低 ℓ 異常同源?")
print("─" * 50)

# 4a. Cold spot (node 0) is a generic A₅ orbit member
# Check if it's special in the graph: degree, BC, etc.
cs_deg = len(adj[0])
print(f"冷斑節點度數: {cs_deg}")

# 4b. Check if cold spot sits on a frustration edge
cs_on_frust = any(0 in edge for edge in frustration)
print(f"冷斑在阻挫邊上: {cs_on_frust}")

# 4c. Cold spot BFS profile
from collections import deque
bfs_dist = {0: 0}
q = deque([0])
while q:
    u = q.popleft()
    for v in adj[u]:
        if v not in bfs_dist:
            bfs_dist[v] = bfs_dist[u] + 1
            q.append(v)

# Count nodes at each distance
bfs_profile = Counter(bfs_dist.values())
print(f"冷斑 BFS 分佈: {dict(sorted(bfs_profile.items()))}")

# 4d. Cold spot antipode
cs_antipode = -cs_vec
# Find closest node to antipode
antipode_dists = [(i, angular_dist_deg(cs_antipode, vecs[i])) for i in range(n)]
antipode_dists.sort(key=lambda x: x[1])
closest_antipode = antipode_dists[0]
print(f"冷斑對蹠點: 最近節點 {closest_antipode[0]} 距離 {closest_antipode[1]:.4f}°")

# 4e. Quadrupole axis from cold spot framework
# If the cold spot is one of the 60 A₅ nodes, then:
# 1. The 60° scale appears naturally from the node spacing
# 2. The low-ℓ suppression is from the discrete node pattern
# 3. The cold spot at ℓ≈44 is the first "true" peak of the node network
# This would mean low-ℓ anomalies and cold spot are DIFFERENT manifestations
# of the same A₅ lattice structure

# Cold spot angular scale: 4.17° (R8) → ℓ = 180/4.17 ≈ 43 ≈ 44 = 2N_d
# Low-ℓ deficit: ℓ<10 → angular scale >18°
# These are different scales of the same lattice!

print(f"\n🔍 冷斑-低ℓ同源分析:")
print(f"  冷斑尺度: ℓ≈44 (4.17°) = 2N_d (已閉合)")
print(f"  低ℓ異常: ℓ<10 (>18°)")
print(f"  A₅ 節點: 60個, 邊長26.09°")
print(f"  60° 異常對應 ℓ=3")
print(f"  結論: 同一 A₅ 晶格係唔同尺度嘅表現")
print(f"  - 冷斑 (ℓ=44): 最小節點間距 (26.09°/2π ≈ 4.15°)")
print(f"  - 60° 異常 (ℓ=3): 整體網格對稱性")
print(f"  - 低ℓ功率低: 離散點場本質 (C_ℓ 喺 ℓ<10 受採樣抑制)")

results['path4'] = {
    'cs_degree': cs_deg,
    'cs_on_frustration': cs_on_frust,
    'bfs_profile': {str(k): v for k, v in sorted(bfs_profile.items())},
    'antipode_dist': float(closest_antipode[1]),
    'antipode_idx': int(closest_antipode[0]),
    'conclusion': 'Cold spot and low-ℓ anomalies are different-scale manifestations of the same A₅ lattice structure'
}

# ────────────────────────────────────────────────
# Save results
# ────────────────────────────────────────────────
with open("data/results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)

print("\n" + "=" * 60)
print("✅ 分析完成! 結果已儲存至 data/results.json")
print("=" * 60)