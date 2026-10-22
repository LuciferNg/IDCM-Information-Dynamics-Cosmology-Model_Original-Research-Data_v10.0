#!/usr/bin/env python3
"""
O143 #33 — 修正軸掃描 (歸一化) + 對齊顯著性 + 頻段軸重算
=======================================================
Bug 根源 (#30/#31): best_axis 用 Fibonacci 構造 [cos(el)cos(az), cos(el)sin(az), el]
  → 第三分量應為 sin(el), 實際寫 el → |a| = sqrt(cos²el+el²) ≈ 1.027 ≠ 1
  → (i) 報出 b0 = asin(el) 偏差; (ii) 對齊角度錯 (script31 嘅 6.85° 係假象)
本輪: 正確歸一化軸掃描 → 真軸 + 對齊顯著性 + 頻段軸重算
"""
import numpy as np, math, json
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
ROOT = f'{BASE}/open_problems_fresh'
O143 = f'{ROOT}/o143_phase_selection_mechanism'
rng = np.random.default_rng(2026)

def to_gal(p):
    sc = SkyCoord(ra=p[:,0]*u.deg, dec=p[:,1]*u.deg, frame='icrs')
    return np.column_stack([sc.galactic.l.deg, sc.galactic.b.deg])
def uvec(lb):
    return np.array([[math.cos(math.radians(b))*math.cos(math.radians(l)),
                      math.cos(math.radians(b))*math.sin(math.radians(l)), math.sin(math.radians(b))] for l,b in lb])

A5 = uvec(to_gal(np.loadtxt(f'{ROOT}/cmb_cold_spot/data/a5_nodes.txt')))
G88 = uvec(to_gal(np.loadtxt(f'{ROOT}/o182_88grid_geometry/data/g88_nodes.txt')))
G32 = uvec(to_gal(np.loadtxt(f'{ROOT}/o182_88grid_geometry/data/g32_frustration_midpoints.txt')))
J = json.load(open(f'{O143}/data/step27_multifreq_l3.json'))
T = np.array(J['SMICA']['T'])

print("="*95); print("  O143 #33 — 修正軸掃描 (歸一化) + 對齊顯著性"); print("="*95)

# 正確 Fibonacci 球面 (單位向量)
def fib_sphere(n):
    idx = np.arange(n) + 0.5
    z = 1 - 2*idx/n                      # z ∈ (−1,1)
    az = math.pi*(1+5**0.5)*idx          # 黃金角
    r_ = np.sqrt(np.clip(1-z*z, 0, None))
    return np.column_stack([r_*np.cos(az), r_*np.sin(az), z])   # ★ 單位向量
def axis_scan(T_, nax=200000):
    x = T_ - T_.mean(); ax = fib_sphere(nax)
    ct = A5 @ ax.T                        # (60, nax) — 單位向量 → ct = cosΘ ✓
    P3 = (5*ct**3 - 3*ct)/2
    P3 = P3 - P3.mean(0)
    rr = np.abs(P3.T @ x) / (np.linalg.norm(P3, axis=0)*np.linalg.norm(x) + 1e-30)
    i = int(np.argmax(rr))
    v = ax[i]
    return float(rr[i]), v, math.degrees(math.atan2(v[1], v[0])) % 360, math.degrees(math.asin(v[2]))
r, axv, l0, b0 = axis_scan(T)
print(f"\n[A] SMICA ℓ=3 真軸 (歸一化掃描, 200k 點) = ({l0:.2f}°, {b0:.2f}°), r = {r:.4f}")
print(f"    |â| = {np.linalg.norm(axv):.10f} (應 = 1)")

# ── 對齊顯著性 ──
print(f"\n[B] 軸向結構對齊顯著性")
N = 50000
RA = fib_sphere(N)
print(f"    {'集合':>14}{'最近':>10}{'null mean':>12}{'null 1%':>10}{'p':>10}")
out = {'axis': [l0, b0], 'r': r}
for name, S in [('A5 60 節點', A5), ('G88 中點', G88), ('G32 阻挫中點', G32), ('120 邊中點', np.vstack([G88,G32]))]:
    d = float(np.degrees(np.arccos(np.clip(np.abs(S @ axv), -1, 1))).min())
    dn = np.degrees(np.arccos(np.clip(np.abs(S @ RA.T), -1, 1))).min(0)
    p = float((1+(dn<=d).sum())/(1+len(dn)))
    out[name] = {'d': d, 'null_mean': float(dn.mean()), 'p': p}
    print(f"    {name:>14}{d:>9.2f}°{dn.mean():>11.2f}°{np.percentile(dn,1):>9.2f}°{p:>10.4f}")
for name, v in [('冷斑 node0', A5[0]), ('銀河北極', np.array([0,0,1.0]))]:
    d = math.degrees(math.acos(np.clip(abs(np.dot(v, axv)),-1,1)))
    out[name] = {'d': d}
    print(f"    {name:>14}{d:>9.2f}°")

# ── 頻段軸重算 (歸一化) ──
print(f"\n[C] 頻段 ℓ=3 軸重算 (歸一化) + 與 SMICA 夾角")
print(f"    {'頻段':>8}{'軸(l,b)':>18}{'r':>9}{'夾角SMICA':>12}{'舊(錯)軸':>18}")
old = {k: (v.get('axis') if isinstance(v, dict) else None) for k, v in J.items()}
old = {k: v for k, v in old.items() if isinstance(v, list)}
out['freq'] = {}
for k in ['30GHz','44GHz','70GHz','100GHz','143GHz','217GHz','353GHz']:
    if k not in J or 'T' not in J[k]: continue
    Tf = np.array(J[k]['T'])
    rf, av, lf, bf = axis_scan(Tf, 60000)
    ang = math.degrees(math.acos(np.clip(np.dot(av, axv), -1, 1)))
    out['freq'][k] = {'axis': [lf, bf], 'r': rf, 'ang_to_smica': ang}
    print(f"    {k:>8}{f'({lf:.2f},{bf:.2f})':>18}{rf:>9.4f}{ang:>11.2f}°{str([round(x,2) for x in old.get(k, [])]):>18}")

# 銀河面距離
print(f"\n[D] 軸向銀河緯度 |b|: SMICA {abs(b0):.2f}°; 頻段 " +
      ", ".join(f"{k[:3]} {abs(out['freq'][k]['axis'][1]):.1f}°" for k in out['freq']))
with open(f'{O143}/data/step30_axis_corrected.json','w') as f:
    json.dump(out, f, indent=2)
print(f"\n✅ 已存: {O143}/data/step30_axis_corrected.json")
