#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O182 scripts/15 — 探索: 理想 Rhombicosidodecahedron vs 實測 a5_nodes 結構比對
==============================================================================
目的 (O213 第五輪交接): 建立理想代數座標 + 對稱群 det 判別量。
本步: 確認 (a) 理想多面體結構 (b) 實測 a5_nodes 係咪同一軌道 (c) 對稱群工具校準。
"""
import numpy as np, math
from pathlib import Path
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
phi = (1 + 5**0.5)/2

def rot(axis, ang):
    a = np.asarray(axis, float); a = a/np.linalg.norm(a)
    c, s = math.cos(ang), math.sin(ang)
    K = np.array([[0,-a[2],a[1]],[a[2],0,-a[0]],[-a[1],a[0],0]])
    return np.eye(3) + s*K + (1-c)*K@K

# ── 1. icosahedral rotation group I (60) ──
g1 = rot([0,1,phi], 2*math.pi/5)
g2 = rot([1,1,1], 2*math.pi/3)
group = [np.eye(3)]; seen = {tuple(np.round(np.eye(3).ravel(),12))}; i = 0
while i < len(group):
    M = group[i]; i += 1
    for gen in (g1, g2):
        N = gen @ M; k = tuple(np.round(N.ravel(),12))
        if k not in seen:
            seen.add(k); group.append(N)
I_group = np.array(group)
print(f"icosahedral rotation group I: |I| = {len(group)} (期望 60)")
print(f"  det 全部 +1: {np.allclose([np.linalg.det(M) for M in group], 1)}")

# ── 2. 理想 rhombicosidodecahedron: orbit of (1,1,φ³) under I ──
v0 = np.array([1.0, 1.0, phi**3])
R_ideal = math.sqrt(11 + 4*5**0.5)
print(f"\n(1,1,φ³) norm = {np.linalg.norm(v0):.10f}, √(11+4√5) = {R_ideal:.10f}")
orbit = []
for M in I_group:
    w = M @ v0
    if not any(np.allclose(w, o, atol=1e-9) for o in orbit): orbit.append(w)
Rhombi = np.array(orbit)
print(f"orbit size = {len(Rhombi)} (期望 60)")
Rhombi_u = Rhombi / np.linalg.norm(Rhombi, axis=1, keepdims=True)

# 邊結構
D = np.degrees(np.arccos(np.clip(Rhombi_u @ Rhombi_u.T, -1, 1)))
np.fill_diagonal(D, np.inf)
nn = D.min(axis=1)
print(f"理想 Rhombi: 最近鄰 min {nn.min():.4f}° max {nn.max():.4f}° (應全部相等)")
edges = [(i,j) for i in range(60) for j in range(i+1,60) if D[i,j] < nn.max()+1e-6]
deg = np.bincount(np.array(edges).ravel(), minlength=60)
print(f"  邊數 {len(edges)} (期望 120), 度數集合 {set(deg.tolist())} (期望 4)")
# 下一層距離
d_next = min(D[i,j] for i in range(60) for j in range(i+1,60) if D[i,j] > nn.max()+1e-6)
print(f"  下一層距離 {d_next:.4f}° (gap {d_next-nn.max():.3f}°)")

# 三角面數 (rhombicosidodecahedron: 20 三角 + 30 方 + 12 五邊)
adj = [set() for _ in range(60)]
for i,j in edges: adj[i].add(j); adj[j].add(i)
tri = sum(1 for i in range(60) for j in adj[i] for k in adj[j] if i<k and k in adj[i] and i<j<k)
print(f"  三角形數 {tri} (期望 20)")

# 距離譜 (由節點 0 到其他 59 點, 排序)
spec_ideal = np.sort(D[0][np.isfinite(D[0])])
print(f"  距離譜 (前 8): {np.round(spec_ideal[:8], 3)}")

# ── 3. 實測 a5_nodes ──
a5 = np.loadtxt(BASE/"cmb_cold_spot/data/a5_nodes.txt")
ra, dec = np.radians(a5[:,0]), np.radians(a5[:,1])
Vobs = np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])
Do = np.degrees(np.arccos(np.clip(Vobs @ Vobs.T, -1, 1)))
np.fill_diagonal(Do, np.inf)
nno = Do.min(axis=1)
print(f"\n實測 a5_nodes: 最近鄰 min {nno.min():.4f}° max {nno.max():.4f}°")
edges_o = [(i,j) for i in range(60) for j in range(i+1,60) if Do[i,j] < 28.0]
dego = np.bincount(np.array(edges_o).ravel(), minlength=60)
print(f"  邊數(28°閾值) {len(edges_o)}, 度數集合 {set(dego.tolist())}")
spec_obs = np.sort(Do[0][np.isfinite(Do[0])])
print(f"  距離譜 (前 8): {np.round(spec_obs[:8], 3)}")
print(f"  距離譜 (8-16):  {np.round(spec_obs[8:16], 3)}")
print(f"\n★ 譜比對 (理想 vs 實測): max |Δ| = {np.abs(spec_ideal-spec_obs).max():.4f}°")

# ── 4. 冷斑軌道 (script 08 方式) 對照 ──
cs = SkyCoord(l=209*u.deg, b=-57*u.deg, frame='galactic').icrs
v_cs = np.array([math.cos(math.radians(cs.dec.deg))*math.cos(math.radians(cs.ra.deg)),
                 math.cos(math.radians(cs.dec.deg))*math.sin(math.radians(cs.ra.deg)),
                 math.sin(math.radians(cs.dec.deg))])
# 用同一 canonical frame 嘅 group
orb_cs = []
for M in I_group:
    w = M @ v_cs
    if not any(np.allclose(w,o,atol=1e-9) for o in orb_cs): orb_cs.append(w)
orb_cs = np.array(orb_cs)
print(f"\n冷斑 A₅ 軌道大小: {len(orb_cs)}")
Dc = np.degrees(np.arccos(np.clip(orb_cs @ orb_cs.T, -1, 1)))
np.fill_diagonal(Dc, np.inf)
nnc = Dc.min(axis=1)
print(f"  最近鄰 min {nnc.min():.4f}° max {nnc.max():.4f}°")
spec_cs = np.sort(Dc[0][np.isfinite(Dc[0])])
print(f"  距離譜 (前 8): {np.round(spec_cs[:8],3)}")
print(f"★ 冷斑軌道 vs 實測 a5: max |Δ| = {np.abs(np.sort(spec_cs)-spec_obs).max():.4f}°")
print(f"★ 理想 Rhombi vs 冷斑軌道: max |Δ| = {np.abs(spec_ideal-np.sort(spec_cs)).max():.4f}°")
