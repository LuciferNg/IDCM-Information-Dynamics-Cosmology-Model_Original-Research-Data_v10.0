#!/usr/bin/env python3
"""
O143 #23 — ★ ℓ=3 (八極) 信號深挖 + 三圖交叉驗證
===============================================
#22 [C] 發現 A5 節點場 ℓ=3 功率 9458 vs null 3159 (p=0.002), ℓ=2 反相關 (p=0.990)。
本輪: 1) m-分解 + 軸向識別  2) 三圖 (SMICA/Commander/SEVEM) 交叉
      3) 穩健性 (移除極端節點)  4) 軸向 vs 結構方向對照
"""
import numpy as np, math, json
from collections import defaultdict, deque
from scipy.special import lpmv

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
O143 = f'{BASE}/open_problems_fresh/o143_phase_selection_mechanism'
D = f'{BASE}/main_problems/p4_cmb_cold_spot/data'
G = f'{BASE}/open_problems_fresh/o182_88grid_geometry/data'
rng = np.random.default_rng(77)

nodes = np.loadtxt(f'{D}/a5_nodes.txt')
vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])

def real_sph(l, m, v):
    theta = np.arccos(np.clip(v[:,2],-1,1)); phi = np.arctan2(v[:,1], v[:,0])
    am = abs(m)
    norm = math.sqrt((2*l+1)/(4*math.pi) * math.factorial(l-am)/math.factorial(l+am))
    P = lpmv(am, l, np.cos(theta))
    if m == 0: return norm * P
    if m > 0: return math.sqrt(2) * norm * P * np.cos(am*phi)
    return math.sqrt(2) * norm * P * np.sin(am*phi)

def l_power(T, l):
    Tz = T - T.mean()
    B = np.column_stack([real_sph(l,m,vecs) for m in range(-l,l+1)])
    coef, *_ = np.linalg.lstsq(B, Tz, rcond=None)
    return float((coef**2).sum()), coef

maps = {}
for m_ in ['SMICA','Commander','SEVEM']:
    maps[m_] = np.array(json.load(open(f'{G}/temps2_{m_}_4.17deg.json'))['A5_60'][:60])

print("="*78); print("  O143 #23 — ℓ=3 八極信號深挖"); print("="*78)

# ═══ 1. 三圖交叉 ═══
print(f"\n[1] 三圖交叉 (4.17°): ℓ=1..6 功率 p 值")
print(f"  {'ℓ':>3} " + " ".join(f"{m_:>18}" for m_ in maps))
res_pow = {}
for l in range(1,7):
    row = []
    for m_ in maps:
        p_obs, _ = l_power(maps[m_], l)
        B = np.column_stack([real_sph(l,mm,vecs) for mm in range(-l,l+1)])
        Tz = maps[m_]-maps[m_].mean()
        null = []
        for _ in range(2000):
            c, *_ = np.linalg.lstsq(B, rng.permutation(Tz), rcond=None)
            null.append((c**2).sum())
        null = np.array(null)
        pv = (1+(null>=p_obs).sum())/(1+len(null))
        row.append(f"{p_obs:>8.0f} p={pv:.3f}")
        res_pow[f"{m_}_{l}"] = {'power': p_obs, 'p': float(pv)}
    print(f"  {l:>3} " + " ".join(f"{x:>18}" for x in row))

# ═══ 2. ℓ=3 m-分解 + 軸向 ═══
print(f"\n[2] ℓ=3 m-分解 (SMICA 4.17°)")
_, coef3 = l_power(maps['SMICA'], 3)
names = [f"m={mm}" for mm in range(-3,4)]
for nm, cc in zip(names, coef3):
    print(f"    {nm}: {cc:>+9.2f}")
# 最大軸: 用 Y_3m 嘅 quadrupole-like 形式找軸 — 掃 Fibonacci 軸, 計 cos(3Θ) 相關
naxis = 8192
i = np.arange(naxis)+0.5
ph = np.arccos(1-2*i/naxis); th = np.pi*(1+5**0.5)*i
axes = np.column_stack([np.sin(ph)*np.cos(th), np.sin(ph)*np.sin(th), np.cos(ph)])
Tz = maps['SMICA']-maps['SMICA'].mean()
best = None
for a in axes:
    ct = np.clip(vecs @ a, -1, 1)
    for fn, lab in [(lambda x: np.cos(3*np.arccos(x)), 'cos3Θ'),
                    (lambda x: np.cos(np.arccos(x)), 'cosΘ')]:
        s = fn(ct)
        r = abs(np.corrcoef(s, Tz)[0,1])
        if best is None or r > best[0]: best = (r, lab, a.copy())
print(f"    最佳軸 ({best[1]}): r = {best[0]:.4f}")
l_ax = math.degrees(math.atan2(best[2][1], best[2][0])) % 360
b_ax = math.degrees(math.asin(best[2][2]))
print(f"    軸 (galactic): l = {l_ax:.2f}°, b = {b_ax:.2f}°")
# 對照已知方向
from astropy.coordinates import SkyCoord
import astropy.units as u_ast
for nm, (ra, dec) in [('冷斑', (209.0, -57.0)), ('北銀極', (192.86, 27.13))]:
    v = np.array([math.cos(math.radians(dec))*math.cos(math.radians(ra)),
                  math.cos(math.radians(dec))*math.sin(math.radians(ra)),
                  math.sin(math.radians(dec))])
    ang = math.degrees(math.acos(np.clip(np.dot(v, best[2]), -1, 1)))
    print(f"    軸 vs {nm}: {ang:.2f}°")

# ═══ 3. 穩健性 ═══
print(f"\n[3] 穩健性 (移除極端節點, SMICA)")
order = np.argsort(-np.abs(maps['SMICA']))
for nrm in [0, 1, 3, 5]:
    rm = set(order[:nrm].tolist())
    keep = np.array([i for i in range(60) if i not in rm])
    Tz2 = maps['SMICA'][keep] - maps['SMICA'][keep].mean()
    B = np.column_stack([real_sph(3,mm,vecs[keep]) for mm in range(-3,4)])
    c, *_ = np.linalg.lstsq(B, Tz2, rcond=None)
    pw = float((c**2).sum())
    null = []
    for _ in range(2000):
        cc, *_ = np.linalg.lstsq(B, rng.permutation(Tz2), rcond=None)
        null.append((cc**2).sum())
    null = np.array(null)
    pv = (1+(null>=pw).sum())/(1+len(null))
    print(f"    移除 {nrm} 個最極端 (n={len(keep)}): ℓ=3 功率 = {pw:.0f}, null = {null.mean():.0f}, p = {pv:.3f}")

# ═══ 4. 結構方向對照 ═══
print(f"\n[4] 軸向 vs A5 結構方向")
# A5 對稱軸: 6 C5, 10 C3, 15 C2 — 用頂點/面心/邊心近似
dirs = {'vertex': vecs, 'edge_mid': np.array([(vecs[i]+vecs[j])/np.linalg.norm(vecs[i]+vecs[j])
        for i in range(60) for j in range(i+1,60)
        if math.degrees(math.acos(np.clip(np.dot(vecs[i],vecs[j]),-1,1)))<28.0])}
for nm, Dv in dirs.items():
    dots = np.abs(Dv @ best[2])
    print(f"    {nm}: 最佳對齊 {math.degrees(math.acos(np.clip(dots.max(),-1,1))):.2f}° (最近 {len(Dv)} 個)")

res = {'three_map_power': res_pow, 'l3_m_coef': [float(x) for x in coef3],
       'best_axis_r': float(best[0]), 'best_axis_l': float(l_ax), 'best_axis_b': float(b_ax),
       'l3_robust': 'see output'}
with open(f'{O143}/data/step20_octupole.json', 'w') as f:
    json.dump(res, f, indent=2)
print(f"\n✅ 已存: {O143}/data/step20_octupole.json")
