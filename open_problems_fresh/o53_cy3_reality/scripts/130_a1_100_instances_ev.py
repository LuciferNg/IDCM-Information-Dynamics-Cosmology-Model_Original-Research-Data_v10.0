#!/usr/bin/env python3
"""
O53 A1: 100 實例 block 譜比例 (dict 修正版)
=============================================
intersection_numbers() 返回 dict (1-based indices)
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53 A1: 100 實例 block 譜比例")
print("=" * 70)

from cytools import Polytope
from cytools.config import enable_experimental_features
enable_experimental_features()

with open(os.path.join(BASE, 'Jstar_36D.json')) as f:
    J0 = np.array(json.load(f)['Jstar_36D'])

# Read all instances
polytopes = []
with open(os.path.join(BASE, 'all_36_98.poly')) as f:
    lines = [l.strip() for l in f if l.strip()]
i = 0
while i < len(lines):
    parts = lines[i].split()
    if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
        n = int(parts[0])
        verts = [list(map(int, lines[i+1+j].split())) for j in range(n)]
        polytopes.append(np.array(verts))
        i += 1 + n
    else:
        i += 1

print(f"Total instances: {len(polytopes)}")

results = []
for k, verts in enumerate(polytopes[:10]):
    print(f"\n[{k}] {len(verts)}v:", end=" ")
    try:
        p = Polytope(verts)
        tri = p.triangulate()
        cy = tri.get_cy()
        
        K_dict = cy.intersection_numbers()
        if not K_dict:
            print("empty", end="")
            continue
        
        # Build Y = κ·J (36×36)
        Y = np.zeros((36, 36))
        for (i, j, kk), val in K_dict.items():
            # 1-based → 0-based
            i0, j0, k0 = i-1, j-1, kk-1
            if k0 < len(J0):
                Y[i0, j0] += val * J0[k0]
        Y = (Y + Y.T) / 2
        
        # Block 0/1/2
        B0 = Y[0:12, 0:12]
        B1 = Y[12:24, 12:24]
        B2 = Y[24:36, 24:36]
        
        ev0 = np.sort(np.linalg.eigvalsh(B0))[::-1]
        ev1 = np.sort(np.linalg.eigvalsh(B1))[::-1]
        ev2 = np.sort(np.linalg.eigvalsh(B2))[::-1]
        
        n13_0 = sum(1 for e in ev0 if abs(e - round(e*3)/3) < 0.01)
        n13_1 = sum(1 for e in ev1 if abs(e - round(e*3)/3) < 0.01)
        n13_2 = sum(1 for e in ev2 if abs(e - round(e*3)/3) < 0.01)
        
        ratio = ev0[0] / ev1[0] if ev1[0] != 0 else 0
        
        results.append({
            'idx': k, 'n_vert': len(verts),
            'ev0': ev0[:3].tolist(),
            'ev1': ev1[:3].tolist(),
            'ev2': ev2[:3].tolist(),
            'n13': [n13_0, n13_1, n13_2],
            'ratio': ratio
        })
        
        print(f"λ0/λ1 = {ratio:.3f}, top3=({ev0[0]:.3f},{ev1[0]:.3f},{ev2[0]:.3f}) 1/3={n13_0}/{n13_1}/{n13_2}")
        
    except Exception as e:
        print(f"FAIL: {str(e)[:60]}")

if results:
    ratios = [r['ratio'] for r in results]
    n13 = np.array([r['n13'] for r in results])
    print(f"\n\n=== 統計 ({len(results)} 個) ===")
    print(f"λ0/λ1 ratio: mean = {np.mean(ratios):.3f}, std = {np.std(ratios):.3f}")
    print(f"mean 1/3 per block: B0={np.mean(n13[:,0]):.1f} B1={np.mean(n13[:,1]):.1f} B2={np.mean(n13[:,2]):.1f}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)