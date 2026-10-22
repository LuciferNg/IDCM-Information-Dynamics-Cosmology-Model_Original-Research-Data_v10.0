#!/usr/bin/env python3
"""
O143 #32 — ℓ=3 軸向結構對齊顯著性
=================================
#31 [A]: 正確軸 (13.63°, 40.26°) 距最近 88 格中點 = 6.85° → 隨機期望?
檢定: 軸向 vs {A5 60 節點, G88 中點, 120 邊中點, 冷斑, 銀河極} 嘅最近距離
      + 隨機軸 null
"""
import numpy as np, math, json
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
ROOT = f'{BASE}/open_problems_fresh'
O143 = f'{ROOT}/o143_phase_selection_mechanism'
rng = np.random.default_rng(2026)

def to_gal(pts):
    sc = SkyCoord(ra=pts[:,0]*u.deg, dec=pts[:,1]*u.deg, frame='icrs')
    return np.column_stack([sc.galactic.l.deg, sc.galactic.b.deg])
def uvec(lb):
    return np.array([[math.cos(math.radians(b))*math.cos(math.radians(l)),
                      math.cos(math.radians(b))*math.sin(math.radians(l)), math.sin(math.radians(b))] for l,b in lb])

a5 = uvec(to_gal(np.loadtxt(f'{ROOT}/cmb_cold_spot/data/a5_nodes.txt')))
g88 = uvec(to_gal(np.loadtxt(f'{ROOT}/o182_88grid_geometry/data/g88_nodes.txt')))
g32 = uvec(to_gal(np.loadtxt(f'{ROOT}/o182_88grid_geometry/data/g32_frustration_midpoints.txt')))
res = json.load(open(f'{O143}/data/step28_foreground_decisive.json'))
l0, b0 = res['axis']
axv = np.array([math.cos(math.radians(b0))*math.cos(math.radians(l0)),
                math.cos(math.radians(b0))*math.sin(math.radians(l0)), math.sin(math.radians(b0))])

print("="*90); print("  O143 #32 — ℓ=3 軸向結構對齊顯著性"); print("="*90)
print(f"\n軸 = ({l0:.2f}°, {b0:.2f}°), r = {res['r']:.4f}")

SETS = {'A5 60 節點': a5, 'G88 中點': g88, 'G32 阻挫中點': g32, '120 邊中點': np.vstack([g88,g32])}
N = 20000
def rand_axes(n):
    z = rng.uniform(-1,1,n); ph = rng.uniform(0,2*np.pi,n)
    r_ = np.sqrt(1-z**2)
    return np.column_stack([r_*np.cos(ph), r_*np.sin(ph), z])
RA = rand_axes(N)
print(f"\n{'集合':>14}{'最近距離':>12}{'null mean':>12}{'null 5%':>10}{'p':>10}")
out = {}
for name, S in SETS.items():
    d = np.degrees(np.arccos(np.clip(np.abs(S @ axv), -1, 1))).min()   # 軸無方向性 → 用 |dot|
    dn = np.degrees(np.arccos(np.clip(np.abs(S @ RA.T), -1, 1))).min(0)
    p = float((1+(dn<=d).sum())/(1+len(dn)))
    out[name] = {'d': float(d), 'null_mean': float(dn.mean()), 'p': p}
    print(f"{name:>14}{d:>11.2f}°{dn.mean():>11.2f}°{np.percentile(dn,5):>9.2f}°{p:>10.4f}")

# 冷斑 / 銀河極
for name, v in [('冷斑 node0', a5[0]), ('銀河北極', np.array([0,0,1.0])), ('銀河南極', np.array([0,0,-1.0]))]:
    d = math.degrees(math.acos(np.clip(abs(np.dot(v, axv)),-1,1)))
    print(f"{name:>14}{d:>11.2f}°")
    out[name] = {'d': float(d)}

with open(f'{O143}/data/step29_axis_alignment.json','w') as f:
    json.dump(out, f, indent=2)
print(f"\n✅ 已存: {O143}/data/step29_axis_alignment.json")
