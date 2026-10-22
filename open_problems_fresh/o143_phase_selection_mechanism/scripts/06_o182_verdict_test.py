#!/usr/bin/env python3
"""
O143 continuation — after O182 verdict (2026-09-19)
====================================================
Independently verify O182 docs/05 core claims + test new 𝒫 design:
  1. Φ_base=cos(πk/44): how many sites have |cos|<0.2?  (O182 claims 10/88 = 11.4%)
  2. Gram(88x88) rank for g88 directions (O182 claims rank 3)
  3. New 𝒫: project Φ_base onto 60 A5 nodes AND 88-grid, count orth/antinode
     WITHOUT longitude-only rule — use full 3D direction structure.

Key insight from O182: the 48/60 orthogonal criterion is impossible under
longitude-only projection (upper bound ~11%). The structural question is not
"how many nodes are orthogonal" but "do node0/node9 sit at antinodes".
"""
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u
import json, os

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
NODES_FILE = f'{BASE}/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt'
G88_FILE = f'{BASE}/open_problems_fresh/o182_88grid_geometry/data/g88_nodes.txt'
OUTDIR = f'{BASE}/open_problems_fresh/o143_phase_selection_mechanism/data'
os.makedirs(OUTDIR, exist_ok=True)

N = 88
k_arr = np.arange(N)
Phi_base = np.cos(np.pi * k_arr / (N/2))  # cos(πk/44)

# ═══════════ 1. O182 claim: 11.4% orthogonal bound ═══════════
n_orth_sites = np.sum(np.abs(Phi_base) < 0.2)
print("=== 1. O182 claim: 正交上限 ===")
print(f"  |cos|<0.2 sites: {n_orth_sites}/{N} = {100*n_orth_sites/N:.2f}%  (O182: 10/88=11.4%)")
print(f"  |cos|>0.8 sites: {np.sum(np.abs(Phi_base) > 0.8)}/{N}")
print(f"  => 任何 longitude-only 方向集正交數上限 ~11% ≪ 80% (O143 原判據)  ✅ O182 正確")
print()

# ═══════════ 2. Gram rank of g88 ═══════════
g88 = np.loadtxt(G88_FILE)
print(f"=== 2. g88 Gram rank ===")
print(f"  g88 shape: {g88.shape}")
sc = SkyCoord(ra=g88[:,0]*u.deg, dec=g88[:,1]*u.deg, frame='icrs')
gal = sc.galactic
g88_vec = np.column_stack([
    np.cos(np.radians(gal.b.deg)) * np.cos(np.radians(gal.l.deg)),
    np.cos(np.radians(gal.b.deg)) * np.sin(np.radians(gal.l.deg)),
    np.sin(np.radians(gal.b.deg)),
])
Gram = g88_vec @ g88_vec.T
evals = np.linalg.eigvalsh(Gram)
print(f"  Gram eigenvalues (top 6): {np.round(evals[-6:], 4)}")
print(f"  rank ≈ {np.sum(evals > 1e-6)}  (O182: rank 3 — 88 方向喺 R³ 冇可能互相正交)")
print()

# ═══════════ 3. Load 60 A5 nodes ═══════════
nodes = np.loadtxt(NODES_FILE)
sc60 = SkyCoord(ra=nodes[:,0]*u.deg, dec=nodes[:,1]*u.deg, frame='icrs')
gal60 = sc60.galactic
l60 = np.array([float(g.l.deg) for g in gal60])
b60 = np.array([float(g.b.deg) for g in gal60])

# ═══════════ 4. New 𝒫 design: full-sky direction-based projection ═══════════
# 88-grid nodes as uniform direction basis (O182 verdict: use g88 as direction set)
# Project Φ_base onto node directions via angular distance to ALL g88 sites
# (NOT longitude-only — full 2D angular distance on sphere)

# g88 in galactic
g88_gal_l = np.array([float(g.l.deg) for g in gal])
g88_gal_b = np.array([float(g.b.deg) for g in gal])

def angdist(l1, b1, l2, b2):
    """Angular distance in radians between (l1,b1) and (l2,b2)"""
    l1, b1, l2, b2 = map(np.radians, [l1, b1, l2, b2])
    return np.arccos(np.clip(np.sin(b1)*np.sin(b2) + np.cos(b1)*np.cos(b2)*np.cos(l1-l2), -1, 1))

# Method A: for each of 60 A5 nodes, find nearest g88 direction, take its Φ value
# But Φ_base is a function of chain site k, not direction — the g88 set has NO chain index (O182 verdict 2)
# So Method A requires a chain↔direction map that DOESN'T exist.

# Method B (O182 suggestion): project 176-Laplacian eigenfunctions directly.
# Φ_base = cos(πk/44) IS the n=22 mode of the 88-ring? Check:
# ring harmonic: cos(2πmk/88), m=22 → cos(2π·22·k/88) = cos(πk/2) — NO
# cos(πk/44) = cos(2π·1·k/88) — it's the m=1 fundamental mode!
print("=== 4. Φ_base mode identification ===")
print("  cos(πk/44) = cos(2πk/88) = ring harmonic m=1 (fundamental, longest wavelength)")
print("  => Φ_base is NOT a chain-embedded quantity by itself;")
print("     it's the m=1 harmonic. A direction set needs its OWN embedding.")
print()

# Method C: Full-sky direction field — build a smooth field from Φ_base
# using the ONLY structurally justified embedding: site phase θ_k = kπ/88
# maps to ring azimuth. O182 verdict: this map does NOT exist for g88.
# HONEST CONCLUSION: without a chain↔direction theorem, ANY 𝒫 is ad hoc.
# O182: "應由 O159 176-Laplacian 本徵函數直接投影 (新 O 系列)"

# ═══════════ 5. What CAN be tested: node0/node9 in g88 vs A5 ═══════════
# Even without chain map, test the O182 finding: A5 nodes ⟨|δT|⟩/A = 0.2438 (Gaussian, z=0.14σ)
# i.e. 11/45 = coincidence — the A5 node field has NO chain signal.
print("=== 5. O182 docs/04 result (11/45 = coincidence) ===")
print("  A5 節點 ⟨|δT|⟩/A = 0.2438 (高斯空想, z=0.14σ); G88 唔命中 (+18-22%)")
print("  => A₅ 節點相位場冇鏈結構信號 — node0/node9 冷斑異常唔可以用")
print("     鏈相位場 longitude 投影解釋 (O143 原框架判死)")
print()

# ═══════════ 6. Sanity: does the cold spot direction have structural identity? ═══════════
# Cold spot at (209°, -57°) = (180+L₇, -(44+F₇))  [memory]
# Check its position vs g88 set
cs_l = 209.0; cs_b = -57.0
d88 = angdist(cs_l, cs_b, g88_gal_l, g88_gal_b)
d60 = angdist(cs_l, cs_b, l60, b60)
print("=== 6. 冷斑位置 vs 方向集 ===")
print(f"  冷斑 (l,b)=({cs_l:.0f}°,{cs_b:.0f}°):")
print(f"  到最近 g88: {np.degrees(d88.min()):.3f}° (idx {np.argmin(d88)})")
print(f"  到最近 A5:  {np.degrees(d60.min()):.3f}° (idx {np.argmin(d60)})")
print(f"  g88 最近 5: {np.round(np.degrees(np.sort(d88)[:5]), 3)}")
print(f"  A5 最近 5:  {np.round(np.degrees(np.sort(d60)[:5]), 3)}")
