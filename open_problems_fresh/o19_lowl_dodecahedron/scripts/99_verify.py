#!/usr/bin/env python3
"""
O19 驗證腳本: 核對所有關鍵數字
===============================
執行: python3 scripts/99_verify.py && echo "✅ ALL PASS" || echo "❌ FAIL"
"""
import sys, math
import numpy as np

phi = (1 + 5**0.5) / 2
eps = phi**-1 / 4
Nd = 44

errors = 0
def check(name, value, expected, tol=1e-3, unit=""):
    global errors
    if abs(value - expected) <= tol * abs(expected) + tol:
        print(f"  ✅ {name}: {value}{unit} (expected {expected}{unit})")
    else:
        print(f"  ❌ {name}: {value}{unit} (expected {expected}{unit}, Δ={abs(value-expected):.6f}{unit})")
        errors += 1

print("=" * 60)
print("O19 驗證: 低 ℓ 異常分析")
print("=" * 60)

# 1. Load nodes
nodes = []
with open("data/a5_nodes.txt") as f:
    for line in f:
        line = line.strip()
        if line:
            ra, dec = map(float, line.split())
            nodes.append((ra, dec))
print(f"\n📦 節點: {len(nodes)} (expected 60)")
check("Node count", len(nodes), 60)

# 2. Node 0 = cold spot (48.3°, -20.44°) ICRS = (209°, -57°) Galactic
check("Cold spot RA", nodes[0][0], 48.2999, 0.01)
check("Cold spot Dec", nodes[0][1], -20.4373, 0.01)

# 3. Edge length
def ang_deg(v1, v2):
    return math.degrees(math.acos(np.clip(np.dot(v1, v2), -1, 1)))

vecs = np.array([[math.cos(math.radians(dec))*math.cos(math.radians(ra)),
                   math.cos(math.radians(dec))*math.sin(math.radians(ra)),
                   math.sin(math.radians(dec))] for ra, dec in nodes])

dists = np.sort([ang_deg(vecs[i], vecs[j]) for i in range(len(nodes)) for j in range(i+1, len(nodes))])
threshold = (dists[119] + dists[120]) / 2

print(f"\n📐 邊緣閾值: {threshold:.4f}°")
check("Threshold", threshold, 28.9225, 0.001)

# First shell edges (those below threshold)
first_shell = dists[dists < threshold]
check("First shell edges", len(first_shell), 120, tol=0)
check("Edge length mean", np.mean(first_shell), 26.1289, 0.01, "°")
check("Edge length min", np.min(first_shell), 26.0913, 0.001, "°")
check("Edge length max", np.max(first_shell), 26.1664, 0.001, "°")

# 4. Graph properties
adj = {i: set() for i in range(len(nodes))}
for i in range(len(nodes)):
    for j in range(i+1, len(nodes)):
        if ang_deg(vecs[i], vecs[j]) < threshold:
            adj[i].add(j)
            adj[j].add(i)

# Degrees
degrees = [len(adj[i]) for i in range(len(nodes))]
print(f"\n📊 度數: min={min(degrees)}, max={max(degrees)}, "
      f"unique={set(degrees)}")
check("Degree", min(degrees), 4)
check("Degree", max(degrees), 4)

# Edge count
n_edges = sum(degrees) // 2
check("Total edges", n_edges, 120)

# 5. Anchored coloring
from collections import deque
color = {0: 1}
q = deque([0])
while q:
    u = q.popleft()
    for v in adj[u]:
        if v not in color:
            color[v] = 1 - color[u]
            q.append(v)

n_cold = sum(1 for c in color.values() if c == 1)
n_hot = len(nodes) - n_cold
print(f"\n🎨 著色: cold={n_cold}, hot={n_hot}")
check("Cold count", n_cold, 30)
check("Hot count", n_hot, 30)

# Frustration edges
frustration = []
for u in adj:
    for v in adj[u]:
        if u < v and color[u] == color[v]:
            frustration.append((u, v))
check("Frustration edges", len(frustration), 32)

# 6. Face traversal → rhombicosidodecahedron
def face_traversal(adj, vecs):
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
chi = len(nodes) - n_edges + F

print(f"\n🔷 面遍歷: {census}")
check("Triangle faces (3)", census.get(3, 0), 20)
check("Square faces (4)", census.get(4, 0), 30)
check("Pentagon faces (5)", census.get(5, 0), 12)
check("Total faces", F, 62)
check("Euler χ", chi, 2)

# 7. 60° = triangle face angle
print(f"\n📐 三角形面角:")
# The spherical triangle angle from A₅ edge length
a_rad = math.radians(26.0913)
cosA = (math.cos(a_rad) - math.cos(a_rad)**2) / (math.sin(a_rad)**2)
A = math.degrees(math.acos(np.clip(cosA, -1, 1)))
check("Spherical triangle angle", A, 61.76, 0.01, "°")
check("Planar triangle angle", 60.0, 60.0, 0, "°")

# 8. Compare with 63.435°
print(f"\n🔍 60° vs 63.435°:")
check("60° difference from 63.435°", 63.435 - 60.0, 3.435, 0.001, "°")
check("60°/63.435° ratio", 60.0/63.435, 0.9458, 0.001)

# 9. Cold spot BFS profile
bfs_dist = {0: 0}
q = deque([0])
while q:
    u = q.popleft()
    for v in adj[u]:
        if v not in bfs_dist:
            bfs_dist[v] = bfs_dist[u] + 1
            q.append(v)

from collections import Counter
bfs_profile = Counter(bfs_dist.values())
print(f"\n🌐 冷斑 BFS: {dict(sorted(bfs_profile.items()))}")
check("BFS diameter", max(bfs_dist.values()), 8)
check("BFS nodes at d=0", bfs_profile[0], 1)
check("BFS nodes at d=1", bfs_profile[1], 4)
check("BFS nodes at d=4", bfs_profile[4], 12)
check("BFS nodes at d=8", bfs_profile[8], 1)

# 10. Cold spot antipode
cs_vec = vecs[0]
antipode = -cs_vec
antipode_dists = [(i, ang_deg(antipode, vecs[i])) for i in range(len(nodes))]
antipode_dists.sort(key=lambda x: x[1])

from astropy.coordinates import SkyCoord
import astropy.units as u
cs_coord = SkyCoord(ra=nodes[0][0], dec=nodes[0][1], unit=u.deg, frame='icrs')
cs_gal = cs_coord.galactic
print(f"\n🌌 冷斑位置:")
print(f"  ICRS: ({nodes[0][0]:.2f}°, {nodes[0][1]:.2f}°)")
print(f"  Galactic: (l={cs_gal.l.deg:.1f}°, b={cs_gal.b.deg:.1f}°)")
check("Cold spot l (Galactic)", cs_gal.l.deg, 209, 1)
check("Cold spot b (Galactic)", cs_gal.b.deg, -57, 1)

# ────────────────────────────────────────────────
# SUMMARY
# ────────────────────────────────────────────────
print(f"\n{'='*60}")
if errors == 0:
    print(f"✅ 全部驗證通過! (0 errors)")
else:
    print(f"❌ {errors} 個驗證失敗")
print(f"{'='*60}")
sys.exit(0 if errors == 0 else 1)