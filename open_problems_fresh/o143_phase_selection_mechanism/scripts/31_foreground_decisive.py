#!/usr/bin/env python3
"""
O143 #31 — 決定性前景檢定 + 修正座標重做 (軸/緯度切分/LOO)
=========================================================
scripts 23/24 用錯座標 (a5_nodes = RA/Dec 當 (l,b))。ℓ=3 功率係旋轉不變 → p 值有效;
但「軸向」「|b| 切分」全部要重做。
A. 正確 ℓ=3 軸 + 與結構方向對齊檢查
B. ★ 前景檢定: ℓ=3 pattern 跨頻段相關 (SMICA vs 353/217/143/100/70/44/30 GHz)
C. 修正銀河緯度切分
D. 修正 LOO

⚠️ 有效性附註 (09-19 後續, 見 docs/07 §3.2):
   [A] 段嘅軸向數字**無效** — best_axis 嘅 Fibonacci 球面構造用 [cos(el)cos(az),
   cos(el)sin(az), el] (第三分量應為 sin(el)) → ‖â‖ = 1.027 ≠ 1
   → 報出軸 (13.63°, 40.26°) 及「最近 88 格中點 6.85°」皆為假象。
   修正版 (歸一化掃描) = scripts/33: 真軸 **(193.45°, −37.85°)**, 最近 G88 15.19° (p = 0.962)。
   有效部分: [0] 緯度分佈 / [B] pattern 相關 (唔用軸) / [C] 緯度切分 / [D] LOO。
"""
import numpy as np, math, json
import healpy as hp
from scipy.special import lpmv
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
ROOT = f'{BASE}/open_problems_fresh'
O143 = f'{ROOT}/o143_phase_selection_mechanism'
rng = np.random.default_rng(2026)

def to_gal(pts):
    sc = SkyCoord(ra=pts[:,0]*u.deg, dec=pts[:,1]*u.deg, frame='icrs')
    g = sc.galactic
    return np.column_stack([g.l.deg, g.b.deg])

a5raw = np.loadtxt(f'{ROOT}/cmb_cold_spot/data/a5_nodes.txt')
LB = to_gal(a5raw)
V = np.array([[math.cos(math.radians(b))*math.cos(math.radians(l)),
               math.cos(math.radians(b))*math.sin(math.radians(l)),
               math.sin(math.radians(b))] for l, b in LB])
T = np.array(json.load(open(f'{O143}/data/step27_multifreq_l3.json'))['SMICA']['T'])
Tfreq = {k: np.array(v['T']) for k, v in json.load(open(f'{O143}/data/step27_multifreq_l3.json')).items() if 'T' in v and k != 'SMICA'}

print("="*100); print("  O143 #31 — 決定性前景檢定 + 修正座標重做"); print("="*100)
print(f"\n[0] A5 節點正確銀河座標: b ∈ [{LB[:,1].min():.2f}°, {LB[:,1].max():.2f}°]; "
      f"|b|<20° 有 {int((np.abs(LB[:,1])<20).sum())}/60; |b|<10° 有 {int((np.abs(LB[:,1])<10).sum())}/60")
print(f"    對比錯誤版本 (用 Dec 當 b): Dec ∈ [{a5raw[:,1].min():.2f}°, {a5raw[:,1].max():.2f}°]")

def real_sph(l, m, v):
    theta = np.arccos(np.clip(v[:,2],-1,1)); p_ = np.arctan2(v[:,1], v[:,0])
    am = abs(m)
    norm = math.sqrt((2*l+1)/(4*math.pi) * math.factorial(l-am)/math.factorial(l+am))
    P = lpmv(am, l, np.cos(theta))
    if m == 0: return norm*P
    if m > 0: return math.sqrt(2)*norm*P*np.cos(am*p_)
    return math.sqrt(2)*norm*P*np.sin(am*p_)
B = {l: np.column_stack([real_sph(l,m,V) for m in range(-l,l+1)]) for l in range(7)}
def p3(T_):
    x = T_ - T_.mean(); c, *_ = np.linalg.lstsq(B[3], x, rcond=None); return float((c**2).sum()), c
def proj3(T_):
    x = T_ - T_.mean(); c, *_ = np.linalg.lstsq(B[3], x, rcond=None); return B[3] @ c

# ── A. 正確軸 + 結構對齊 ──
print(f"\n[A] 正確 ℓ=3 軸 + 結構方向對齊")
def best_axis(T_, nax=16384):
    x = T_ - T_.mean(); idx = np.arange(nax) + 0.5
    z = 1 - 2*idx/nax; r_ = math.sqrt(2*nax*math.pi)
    az = r_*idx; el = np.arcsin(np.clip(z,-1,1))
    ax = np.column_stack([np.cos(el)*np.cos(az), np.cos(el)*np.sin(az), el])
    ct = V @ ax.T; P3 = (5*ct**3 - 3*ct)/2; P3 = P3 - P3.mean(0)
    rr = np.abs(P3.T @ x) / (np.linalg.norm(P3, axis=0)*np.linalg.norm(x)+1e-30)
    i = int(np.argmax(rr)); return float(rr[i]), ax[i], math.degrees(math.atan2(ax[i,1],ax[i,0]))%360, math.degrees(math.asin(ax[i,2]))
r, axv, l0, b0 = best_axis(T)
print(f"    SMICA ℓ=3 最佳軸 = ({l0:.2f}°, {b0:.2f}°), r = {r:.4f}")
cs = to_gal(np.array([[209.0, -57.0]]))[0]  # 冷斑 (RA/Dec 常引用值) — 改用實際 cold spot 方向
# 冷斑實際方向: 由 node0
cs_lb = LB[0]
def ang(a, b_):
    return math.degrees(math.acos(np.clip(np.dot(a, b_), -1, 1)))
vcs = V[0]
vngp = np.array([0,0,1.0])
print(f"    夾角: 冷斑(node0) = {ang(axv, vcs):.2f}°; 銀河北極 = {ang(axv, vngp):.2f}°")
# A5 結構方向: 節點 & 邊中點
d_n = min(ang(axv, V[i]) for i in range(60))
print(f"    最近 A5 節點 = {d_n:.2f}°")
# 88 格中點
g88 = to_gal(np.loadtxt(f'{ROOT}/o182_88grid_geometry/data/g88_nodes.txt'))
V88 = np.array([[math.cos(math.radians(b))*math.cos(math.radians(l)),
                 math.cos(math.radians(b))*math.sin(math.radians(l)), math.sin(math.radians(b))] for l,b in g88])
print(f"    最近 88 格中點 = {min(ang(axv, V88[i]) for i in range(88)):.2f}°")
# 對極 (反方向)
d_anti = min(ang(-axv, V[i]) for i in range(60))
print(f"    最近 A5 節點 (反方向 −â) = {d_anti:.2f}°")

# ── B. ★ 前景檢定 ──
print(f"\n[B] ★ 前景檢定: ℓ=3 pattern 跨頻段相關")
P3_smica = proj3(T)
print(f"    {'頻段':>8}{'corr(P3)':>12}{'corr(T)':>10}{'dust?':>10}")
res = {'axis': [l0, b0], 'r': r, 'angle_coldspot': ang(axv, vcs), 'angle_ngp': ang(axv, vngp),
       'dist_nearest_a5node': d_n, 'dist_nearest_g88': min(ang(axv, V88[i]) for i in range(88))}
freqres = {}
for k in ['30GHz','44GHz','70GHz','100GHz','143GHz','217GHz','353GHz']:
    if k not in Tfreq: continue
    Tf = Tfreq[k]
    P3f = proj3(Tf)
    cp = float(np.corrcoef(P3_smica, P3f)[0,1])
    ct = float(np.corrcoef(T, Tf)[0,1])
    freqres[k] = {'corr_P3': cp, 'corr_T': ct}
    print(f"    {k:>8}{cp:>12.4f}{ct:>10.4f}")
res['freq_pattern_corr'] = freqres

# ── C. 修正緯度切分 ──
print(f"\n[C] 修正銀河緯度切分 (用正確 b)")
for lo, hi, lab in [(20, 90, '|b|>20°'), (30, 90, '|b|>30°'), (40, 90, '|b|>40°')]:
    sel = np.abs(LB[:,1]) > lo
    if sel.sum() < 12: continue
    Ts = T[sel]; Bs = B[3][sel]
    p_ = float((np.linalg.lstsq(Bs, Ts-Ts.mean(), rcond=None)[0]**2).sum()); v_ = []
    for _ in range(2000):
        c, *_ = np.linalg.lstsq(Bs, rng.permutation(Ts-Ts.mean()), rcond=None)
        v_.append((c**2).sum())
    v_ = np.array(v_)
    print(f"    {lab}: n={int(sel.sum())}, ℓ=3 = {p_:.0f}, null = {v_.mean():.0f}±{v_.std():.0f}, p = {(1+(v_>=p_).sum())/(1+len(v_)):.4f}")
    res[f'latcut_{lab}'] = {'n': int(sel.sum()), 'p3': p_, 'null': float(v_.mean()), 'p': float((1+(v_>=p_).sum())/(1+len(v_)))}

# ── D. LOO ──
print(f"\n[D] Leave-one-out (60 次)")
ps = []
for i in range(60):
    sel = np.ones(60, bool); sel[i] = False
    Ts = T[sel]; Bs = B[3][sel]
    p_ = float((np.linalg.lstsq(Bs, Ts-Ts.mean(), rcond=None)[0]**2).sum()); v_ = []
    for _ in range(400):
        c, *_ = np.linalg.lstsq(Bs, rng.permutation(Ts-Ts.mean()), rcond=None)
        v_.append((c**2).sum())
    ps.append((1+(np.array(v_)>=p_).sum())/(1+len(v_)))
ps = np.array(ps)
print(f"    p 範圍 [{ps.min():.4f}, {ps.max():.4f}], 中位 {np.median(ps):.4f}, <0.05 比例 = {(ps<0.05).mean():.3f}")
res['loo_p_range'] = [float(ps.min()), float(ps.max())]

with open(f'{O143}/data/step28_foreground_decisive.json','w') as f:
    json.dump(res, f, indent=2)
print(f"\n✅ 已存: {O143}/data/step28_foreground_decisive.json")
