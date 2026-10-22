#!/usr/bin/env python3
"""
O143 #30 — Gemini Part III 步驟 1: 多頻段 ℓ=3 交叉 (前景排除) [修正座標版]
=========================================================================
scripts/29 有座標 bug: a5_nodes.txt 係 RA/Dec ICRS, 直接用做 (l,b) → 全錯。
本版對齊 O182 scripts/02b 正確管道:
  read_map → reorder 驗證 → smoothing(4.17°) → (銀河座標採樣, 最近像素) → ×1e6 μK
"""
import numpy as np, math, json
import healpy as hp
from scipy.special import lpmv
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
ROOT = f'{BASE}/open_problems_fresh'
O143 = f'{ROOT}/o143_phase_selection_mechanism'
FD = f'{ROOT}/o27_node47_foreground/data'
rng = np.random.default_rng(2026)

def to_gal(pts):
    sc = SkyCoord(ra=pts[:,0]*u.deg, dec=pts[:,1]*u.deg, frame='icrs')
    g = sc.galactic
    return np.column_stack([g.l.deg, g.b.deg])

LB = to_gal(np.loadtxt(f'{ROOT}/cmb_cold_spot/data/a5_nodes.txt'))
V = np.array([[math.cos(math.radians(b))*math.cos(math.radians(l)),
               math.cos(math.radians(b))*math.sin(math.radians(l)),
               math.sin(math.radians(b))] for l, b in LB])
T_smica = np.array(json.load(open(f'{ROOT}/o182_88grid_geometry/data/temps2_SMICA_4.17deg.json'))['A5_60'][:60])
print(f"a5_nodes → 銀河: l ∈ [{LB[:,0].min():.1f}, {LB[:,0].max():.1f}], b ∈ [{LB[:,1].min():.1f}, {LB[:,1].max():.1f}]")

FREQ = [('LFI_SkyMap_030_1024_R3.00_full', 30), ('LFI_SkyMap_044_1024_R3.00_full', 44),
        ('LFI_SkyMap_070_1024_R3.00_full', 70), ('HFI_SkyMap_100_2048_R3.01_full', 100),
        ('HFI_SkyMap_143_2048_R3.01_full', 143), ('HFI_SkyMap_217_2048_R3.01_full', 217),
        ('HFI_SkyMap_353_2048_R3.01_full', 353)]
SMICA_F = f'{ROOT}/o175_entropy_theorem/data/planck/COM_CMB_IQU-smica_2048_R3.00_full.fits'

def real_sph(l, m, v):
    theta = np.arccos(np.clip(v[:,2],-1,1)); p_ = np.arctan2(v[:,1], v[:,0])
    am = abs(m)
    norm = math.sqrt((2*l+1)/(4*math.pi) * math.factorial(l-am)/math.factorial(l+am))
    P = lpmv(am, l, np.cos(theta))
    if m == 0: return norm*P
    if m > 0: return math.sqrt(2)*norm*P*np.cos(am*p_)
    return math.sqrt(2)*norm*P*np.sin(am*p_)
B = {l: np.column_stack([real_sph(l,m,V) for m in range(-l,l+1)]) for l in range(7)}
def l3(T):
    x = T - T.mean(); c, *_ = np.linalg.lstsq(B[3], x, rcond=None)
    return float((c**2).sum())
def nullp(T, n=1500):
    x = T - T.mean(); v = []
    for _ in range(n):
        c, *_ = np.linalg.lstsq(B[3], rng.permutation(x), rcond=None)
        v.append((c**2).sum())
    return np.array(v)
def best_axis(T, nax=8192):
    x = T - T.mean(); idx = np.arange(nax) + 0.5
    z = 1 - 2*idx/nax; r_ = math.sqrt(2*nax*math.pi)
    az = r_*idx; el = np.arcsin(np.clip(z,-1,1))
    ax = np.column_stack([np.cos(el)*np.cos(az), np.cos(el)*np.sin(az), el])
    ct = V @ ax.T; P3 = (5*ct**3 - 3*ct)/2; P3 = P3 - P3.mean(0)
    rr = np.abs(P3.T @ x) / (np.linalg.norm(P3, axis=0)*np.linalg.norm(x) + 1e-30)
    i = int(np.argmax(rr))
    return float(rr[i]), math.degrees(math.atan2(ax[i,1], ax[i,0])) % 360, math.degrees(math.asin(ax[i,2]))

def extract(path, ref):
    m = hp.read_map(path, field=0).astype(np.float64)
    mr = hp.reorder(m, n2r=True)
    ms = hp.smoothing(m, fwhm=math.radians(4.17), verbose=False)
    msr = hp.smoothing(mr, fwhm=math.radians(4.17), verbose=False)
    nside = hp.get_nside(ms)
    pix = hp.ang2pix(nside, LB[:,0], LB[:,1], lonlat=True)
    Ta = ms[pix]*1e6; Tb = msr[pix]*1e6
    ca = np.corrcoef(Ta, ref)[0,1]; cb = np.corrcoef(Tb, ref)[0,1]
    return (Ta, 'as-is') if ca >= cb else (Tb, 'reorder')

print("="*112); print("  O143 #30 — 多頻段 ℓ=3 交叉 (前景排除, 修正座標)"); print("="*112)
out = {}
T_ref, ord_ = extract(SMICA_F, T_smica)
print(f"\n[基準驗證] 自算 SMICA vs O182 temps2: corr = {np.corrcoef(T_ref,T_smica)[0,1]:.6f}, "
      f"max|Δ| = {np.abs(T_ref-T_smica).max():.3f} μK, ordering = {ord_}")
p3 = l3(T_ref); n = nullp(T_ref, 2000); r, l, b = best_axis(T_ref)
print(f"  SMICA: ℓ=3 = {p3:.0f} (null {n.mean():.0f}±{n.std():.0f}, p = {(1+(n>=p3).sum())/(1+len(n)):.4f}), 軸 ({l:.2f}°, {b:.2f}°), r = {r:.4f}")
out['SMICA'] = {'p3': p3, 'p': float((1+(n>=p3).sum())/(1+len(n))), 'axis': [l,b], 'r': r,
                'corr_temps2': float(np.corrcoef(T_ref,T_smica)[0,1]), 'ordering': ord_, 'T': T_ref.tolist()}

print(f"\n{'頻段':>7}{'ord':>8}{'ℓ=3功率':>11}{'ℓ=1-6總':>11}{'佔比':>8}{'null':>9}{'p':>9}{'軸(l,b)':>18}{'r':>8}{'corrSMICA':>11}")
for fn, nu in FREQ:
    try:
        T, od = extract(f'{FD}/{fn}.fits', T_smica)
        p3 = l3(T); tot = float(((T-T.mean())**2).sum()); n = nullp(T, 1000)
        r, l, b = best_axis(T); cc = float(np.corrcoef(T, T_smica)[0,1])
        pv = float((1+(n>=p3).sum())/(1+len(n)))
        print(f"{nu:>5}GHz{od:>8}{p3:>11.1f}{tot:>11.0f}{100*p3/tot:>7.1f}%{n.mean():>9.0f}{pv:>9.4f}{f'({l:.2f},{b:.2f})':>18}{r:>8.4f}{cc:>11.4f}")
        out[f'{nu}GHz'] = {'p3': p3, 'tot': tot, 'ratio': p3/tot, 'p': pv, 'axis': [l,b], 'r': r,
                           'corr_smica': cc, 'ordering': od, 'T': T.tolist()}
    except Exception as e:
        print(f"{nu:>5}GHz  ERR {e}"); out[f'{nu}GHz'] = {'error': str(e)}

print(f"\n[軸向一致性] vs SMICA 軸 夾角:")
l0, b0 = out['SMICA']['axis']
v0 = np.array([math.cos(math.radians(b0))*math.cos(math.radians(l0)),
               math.cos(math.radians(b0))*math.sin(math.radians(l0)), math.sin(math.radians(b0))])
for k in ['30GHz','44GHz','70GHz','100GHz','143GHz','217GHz','353GHz']:
    if 'axis' not in out.get(k, {}): continue
    l, b = out[k]['axis']
    vv = np.array([math.cos(math.radians(b))*math.cos(math.radians(l)),
                   math.cos(math.radians(b))*math.sin(math.radians(l)), math.sin(math.radians(b))])
    ang = math.degrees(math.acos(np.clip(np.dot(v0,vv),-1,1)))
    out[k]['ang_to_smica'] = ang
    print(f"    {k:>8}: ({l:7.2f}, {b:6.2f})  夾角 {ang:6.2f}°  corr(SMICA) = {out[k]['corr_smica']:+.4f}")

with open(f'{O143}/data/step27_multifreq_l3.json','w') as f:
    json.dump(out, f, indent=2)
print(f"\n✅ 已存: {O143}/data/step27_multifreq_l3.json")
