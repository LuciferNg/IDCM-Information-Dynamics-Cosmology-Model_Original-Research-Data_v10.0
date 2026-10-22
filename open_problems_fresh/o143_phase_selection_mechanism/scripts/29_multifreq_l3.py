#!/usr/bin/env python3
"""
O143 #29 — Gemini Part III 步驟 1: 多頻段 ℓ=3 交叉 (前景排除)
=============================================================
⛔ 本腳本已作廢 (09-19): 座標 bug — a5_nodes.txt 係 RA/Dec (ICRS), 直接當 (l,b) 用。
   輸出 (data/step26_multifreq_l3.json) 無效。修正版 = scripts/30_multifreq_l3_fixed.py。
   (ℓ=3 功率統計對整體旋轉不變, 故功率/p 值本身無影響; 但軸向全錯。見 docs/07 §3.2)
Gemini 框架: 若 ℓ=3 軸向/顯著性跨頻段漂移 → 前景。
項目內已有 LFI 30/44/70 + HFI 100/143/217/353 GHz full maps。
本輪: 每頻段 → 平滑 4.17° → 60 節點採樣 → ℓ=3 功率/軸向/與 SMICA 相關
"""
import numpy as np, math, json, os
import healpy as hp
from scipy.special import lpmv

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
O143 = f'{BASE}/open_problems_fresh/o143_phase_selection_mechanism'
FD = f'{BASE}/open_problems_fresh/o27_node47_foreground/data'
D = f'{BASE}/main_problems/p4_cmb_cold_spot/data'
G = f'{BASE}/open_problems_fresh/o182_88grid_geometry/data'
rng = np.random.default_rng(2026)

a5 = np.loadtxt(f'{D}/a5_nodes.txt')
th = np.radians(90.0 - a5[:,1]); ph = np.radians(a5[:,0])
V = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
               math.cos(math.radians(d))*math.sin(math.radians(r)),
               math.sin(math.radians(d))] for r, d in a5])
T_smica = np.array(json.load(open(f'{G}/temps2_SMICA_4.17deg.json'))['A5_60'][:60])

FREQ = [('LFI_SkyMap_030_1024_R3.00_full', 30), ('LFI_SkyMap_044_1024_R3.00_full', 44),
        ('LFI_SkyMap_070_1024_R3.00_full', 70), ('HFI_SkyMap_100_2048_R3.01_full', 100),
        ('HFI_SkyMap_143_2048_R3.01_full', 143), ('HFI_SkyMap_217_2048_R3.01_full', 217),
        ('HFI_SkyMap_353_2048_R3.01_full', 353)]

def real_sph(l, m, v):
    theta = np.arccos(np.clip(v[:,2],-1,1)); p_ = np.arctan2(v[:,1], v[:,0])
    am = abs(m)
    norm = math.sqrt((2*l+1)/(4*math.pi) * math.factorial(l-am)/math.factorial(l+am))
    P = lpmv(am, l, np.cos(theta))
    if m == 0: return norm*P
    if m > 0: return math.sqrt(2)*norm*P*np.cos(am*p_)
    return math.sqrt(2)*norm*P*np.sin(am*p_)
B = {l: np.column_stack([real_sph(l,m,V) for m in range(-l,l+1)]) for l in range(7)}

def l3power(T):
    x = T - T.mean()
    c, *_ = np.linalg.lstsq(B[3], x, rcond=None)
    return float((c**2).sum()), float((x**2).sum())
def best_axis(T, nax=8192):
    x = T - T.mean()
    idx = np.arange(nax) + 0.5
    z = 1 - 2*idx/nax; r_ = math.sqrt(2*nax*math.pi)
    az = r_*idx; el = np.arcsin(np.clip(z,-1,1))
    ax = np.column_stack([np.cos(el)*np.cos(az), np.cos(el)*np.sin(az), el])
    ct = V @ ax.T
    P3 = (5*ct**3 - 3*ct)/2
    P3 = P3 - P3.mean(0)
    nrm = np.linalg.norm(P3, axis=0)
    r = np.abs(P3.T @ x) / (nrm*np.linalg.norm(x) + 1e-30)
    i = int(np.argmax(r))
    bb = math.degrees(math.asin(ax[i,2]))
    ll = math.degrees(math.atan2(ax[i,1], ax[i,0])) % 360
    return float(r[i]), ll, bb
def nullp(T, n=2000):
    x = T - T.mean(); v = []
    for _ in range(n):
        c, *_ = np.linalg.lstsq(B[3], rng.permutation(x), rcond=None)
        v.append((c**2).sum())
    return np.array(v)

print("="*100); print("  O143 #29 — 多頻段 ℓ=3 交叉 (Gemini Part III)"); print("="*100)
out = {}
# SMICA 基準 (重算, 驗證 pipeline)
_p1 = f'{FD}/../o175_entropy_theorem/data/planck/COM_CMB_IQU-smica_2048_R3.00.full.fits'
_p2 = f'{BASE}/open_problems_fresh/o26_node57_region/data/smica_iqu_2048.fits'
m = hp.read_map(_p1 if os.path.exists(_p1) else _p2, field=0)
sm = hp.smoothing(m.astype(np.float64), fwhm=math.radians(4.17))
T_rec = hp.get_interp_val(sm, th, ph)
print(f"\n[基準] 自算 SMICA 60 節點 vs O182 temps2: corr = {np.corrcoef(T_rec, T_smica)[0,1]:.6f}, "
      f"max|Δ| = {np.abs(T_rec-T_smica).max():.3f} μK")
p3, tot = l3power(T_rec); n = nullp(T_rec, 2000)
r, l, b = best_axis(T_rec)
print(f"  自算 SMICA: ℓ=3 功率 = {p3:.0f} (null {n.mean():.0f}±{n.std():.0f}, p={(1+(n>=p3).sum())/(1+len(n)):.4f}), 軸 ({l:.2f}°,{b:.2f}°), r={r:.4f}")
out['SMICA_recomputed'] = {'p3': p3, 'p': float((1+(n>=p3).sum())/(1+len(n))), 'axis': [l,b], 'r': r,
                           'corr_temps2': float(np.corrcoef(T_rec, T_smica)[0,1])}
del m, sm

print(f"\n{'頻段':<8}{'ℓ=3功率':>12}{'ℓ=1-6總':>12}{'ℓ=3佔比':>10}{'null':>10}{'p':>9}{'軸(l,b)':>20}{'r':>8}{'corr SMICA':>12}")
for fn, nu in FREQ:
    path = f'{FD}/{fn}.fits'
    try:
        mm = hp.read_map(path, field=0)
        smm = hp.smoothing(mm.astype(np.float64), fwhm=math.radians(4.17))
        T = hp.get_interp_val(smm, th, ph)
        p3, tot = l3power(T); n = nullp(T, 1000)
        r, l, b = best_axis(T)
        cc = float(np.corrcoef(T, T_smica)[0,1])
        pv = float((1+(n>=p3).sum())/(1+len(n)))
        print(f"{nu:>5}GHz{p3:>12.1f}{tot:>12.0f}{100*p3/tot:>9.1f}%{n.mean():>10.0f}{pv:>9.4f}{f'({l:.2f},{b:.2f})':>20}{r:>8.4f}{cc:>12.4f}")
        out[f'{nu}GHz'] = {'p3': p3, 'tot': tot, 'ratio': p3/tot, 'p': pv, 'axis': [l,b], 'r': r, 'corr_smica': cc}
        del mm, smm
    except Exception as e:
        print(f"{nu:>5}GHz  ERR {e}")
        out[f'{nu}GHz'] = {'error': str(e)}

# 軸向一致性
print(f"\n[軸向一致性] 各頻段最佳軸 vs SMICA 軸 夾角:")
axes = {k: v['axis'] for k, v in out.items() if 'axis' in v}
if 'SMICA_recomputed' in axes:
    l0, b0 = axes['SMICA_recomputed']
    v0 = np.array([math.cos(math.radians(b0))*math.cos(math.radians(l0)),
                   math.cos(math.radians(b0))*math.sin(math.radians(l0)), math.sin(math.radians(b0))])
    for k, (l, b) in sorted(axes.items(), key=lambda x: int(''.join(c for c in x[0] if c.isdigit()) or 0)):
        vv = np.array([math.cos(math.radians(b))*math.cos(math.radians(l)),
                       math.cos(math.radians(b))*math.sin(math.radians(l)), math.sin(math.radians(b))])
        ang = math.degrees(math.acos(np.clip(np.dot(v0,vv),-1,1)))
        out.setdefault(k, {})['ang_to_smica'] = ang
        print(f"    {k:>18}: ({l:7.2f}, {b:6.2f})  夾角 {ang:6.2f}°")

with open(f'{O143}/data/step26_multifreq_l3.json','w') as f:
    json.dump(out, f, indent=2)
print(f"\n✅ 已存: {O143}/data/step26_multifreq_l3.json")
