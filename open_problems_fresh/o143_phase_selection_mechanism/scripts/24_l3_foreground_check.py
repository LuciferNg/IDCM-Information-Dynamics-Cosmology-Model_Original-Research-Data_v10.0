#!/usr/bin/env python3
"""
O143 #24 — ℓ=3 信號嘅銀河前景檢查 + 軸向一致性
=============================================
風險: 最佳軸 (l=241°, b=2.79°) 近銀河面 → 可能前景殘餘?
檢查: 1) 三圖各自最佳軸 (一致?)  2) 移除 |b|<20° 節點後 ℓ=3 是否存活
      3) 只留 |b|>20° / 只留 |b|<20° 分別  4) 用 O182 G88 集 (獨立方向集) 對照
"""
import numpy as np, math, json
from scipy.special import lpmv
from astropy.coordinates import SkyCoord
import astropy.units as u_ast

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
O143 = f'{BASE}/open_problems_fresh/o143_phase_selection_mechanism'
D = f'{BASE}/main_problems/p4_cmb_cold_spot/data'
G = f'{BASE}/open_problems_fresh/o182_88grid_geometry/data'
rng = np.random.default_rng(1234)

nodes = np.loadtxt(f'{D}/a5_nodes.txt')
gal = SkyCoord(ra=nodes[:,0]*u_ast.deg, dec=nodes[:,1]*u_ast.deg, frame='icrs').galactic
b_gal = np.array([float(g.b.deg) for g in gal])
vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])
g88 = np.loadtxt(f'{G}/g88_nodes.txt')
g88_gal = SkyCoord(ra=g88[:,0]*u_ast.deg, dec=g88[:,1]*u_ast.deg, frame='icrs').galactic
g88_vecs = np.array([[math.cos(math.radians(g.b.deg))*math.cos(math.radians(g.l.deg)),
                      math.cos(math.radians(g.b.deg))*math.sin(math.radians(g.l.deg)),
                      math.sin(math.radians(g.b.deg))] for g in g88_gal])

def real_sph(l, m, v):
    theta = np.arccos(np.clip(v[:,2],-1,1)); phi = np.arctan2(v[:,1], v[:,0])
    am = abs(m)
    norm = math.sqrt((2*l+1)/(4*math.pi) * math.factorial(l-am)/math.factorial(l+am))
    P = lpmv(am, l, np.cos(theta))
    if m == 0: return norm * P
    if m > 0: return math.sqrt(2) * norm * P * np.cos(am*phi)
    return math.sqrt(2) * norm * P * np.sin(am*phi)

def l3_test(T, V, nperm=3000):
    Tz = T - T.mean()
    B = np.column_stack([real_sph(3,m,V) for m in range(-3,4)])
    c, *_ = np.linalg.lstsq(B, Tz, rcond=None)
    pw = float((c**2).sum())
    null = []
    for _ in range(nperm):
        cc, *_ = np.linalg.lstsq(B, rng.permutation(Tz), rcond=None)
        null.append((cc**2).sum())
    null = np.array(null)
    return pw, (1+(null>=pw).sum())/(1+len(null)), float(null.mean())

maps = {}
for m_ in ['SMICA','Commander','SEVEM']:
    maps[m_] = np.array(json.load(open(f'{G}/temps2_{m_}_4.17deg.json'))['A5_60'][:60])

print("="*78); print("  O143 #24 — ℓ=3 前景檢查 + 軸向一致性"); print("="*78)

# ── 1. 三圖各自最佳軸 ──
print(f"\n[1] 三圖各自最佳軸 (cos3Θ 掃 8192 Fibonacci 軸)")
naxis = 8192
i = np.arange(naxis)+0.5
ph = np.arccos(1-2*i/naxis); th = np.pi*(1+5**0.5)*i
axes = np.column_stack([np.sin(ph)*np.cos(th), np.sin(ph)*np.sin(th), np.cos(ph)])
best_axes = {}
for m_ in maps:
    Tz = maps[m_]-maps[m_].mean()
    bs = None
    for a in axes:
        ct = np.clip(vecs @ a, -1, 1)
        r = abs(np.corrcoef(np.cos(3*np.arccos(ct)), Tz)[0,1])
        if bs is None or r > bs[0]: bs = (r, a.copy())
    l_ = math.degrees(math.atan2(bs[1][1], bs[1][0])) % 360
    b_ = math.degrees(math.asin(bs[1][2]))
    best_axes[m_] = (bs[0], l_, b_, bs[1])
    print(f"    {m_}: r = {bs[0]:.4f}, 軸 (l,b) = ({l_:.2f}°, {b_:.2f}°)")
# 軸間夾角
ks = list(best_axes)
for a1 in range(len(ks)):
    for a2 in range(a1+1, len(ks)):
        v1, v2 = best_axes[ks[a1]][3], best_axes[ks[a2]][3]
        ang = math.degrees(math.acos(np.clip(abs(np.dot(v1,v2)),-1,1)))
        print(f"    夾角 {ks[a1]}–{ks[a2]}: {ang:.2f}°")

# ── 2. 銀河面切除 ──
print(f"\n[2] 銀河面切除 (SMICA 4.17°)")
for lab, mask in [('全部 60', np.ones(60,bool)),
                  ('|b|>20°', np.abs(b_gal)>20),
                  ('|b|<20°', np.abs(b_gal)<20),
                  ('|b|>30°', np.abs(b_gal)>30)]:
    V = vecs[mask]; T = maps['SMICA'][mask]
    if len(T) < 12: continue
    pw, pv, nm = l3_test(T, V, 3000)
    print(f"    {lab:>10} (n={mask.sum():>2}): ℓ=3 功率 = {pw:>7.0f}, null = {nm:>7.0f}, p = {pv:.3f}")

# ── 3. G88 獨立方向集對照 ──
print(f"\n[3] G88 (O182 獨立方向集, 88 點) 對照")
T88 = np.array(json.load(open(f'{G}/temps2_SMICA_4.17deg.json'))['G88'][:88])
for l in [1,2,3,4]:
    Tz = T88 - T88.mean()
    B = np.column_stack([real_sph(l,m,g88_vecs) for m in range(-l,l+1)])
    c, *_ = np.linalg.lstsq(B, Tz, rcond=None)
    pw = float((c**2).sum())
    null = []
    for _ in range(2000):
        cc, *_ = np.linalg.lstsq(B, rng.permutation(Tz), rcond=None)
        null.append((cc**2).sum())
    null = np.array(null)
    print(f"    ℓ={l}: 功率 = {pw:>8.0f}, null = {null.mean():>8.0f}, p = {(1+(null>=pw).sum())/(1+len(null)):.3f}")

# ── 4. ℓ=3 訊號係咪 node0 驅動 (逐節點 leave-one-out) ──
print(f"\n[4] Leave-one-out (SMICA, ℓ=3 p 值穩定性)")
ps = []
for i in range(60):
    keep = np.array([j for j in range(60) if j != i])
    _, pv, _ = l3_test(maps['SMICA'][keep], vecs[keep], 800)
    ps.append(pv)
ps = np.array(ps)
print(f"    p 範圍 [{ps.min():.3f}, {ps.max():.3f}], 中位 {np.median(ps):.3f}")
print(f"    全部 p < 0.05? {np.all(ps<0.05)}; 最差 (移除節點 {int(np.argmax(ps))}) p = {ps.max():.3f}")

res = {'best_axes': {m_: {'r': best_axes[m_][0], 'l': best_axes[m_][1], 'b': best_axes[m_][2]} for m_ in best_axes},
       'loo_p_min': float(ps.min()), 'loo_p_max': float(ps.max()), 'loo_p_median': float(np.median(ps)),
       'loo_all_sig': bool(np.all(ps<0.05))}
with open(f'{O143}/data/step21_l3_foreground_check.json', 'w') as f:
    json.dump(res, f, indent=2)
print(f"\n✅ 已存: {O143}/data/step21_l3_foreground_check.json")
