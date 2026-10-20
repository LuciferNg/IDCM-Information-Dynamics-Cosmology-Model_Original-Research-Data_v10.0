#!/usr/bin/env python3
"""O5 independent doc-audit (2026-09-11). Recompute every doc claim from
first principles: a5_nodes.txt + smoothed maps (data/smooth_cache) + raw
SMICA/NILC/Commander via /tmp symlinks. Does NOT read any script output as
source of truth; JSON files used only as comparison targets.

Doc refs: [PR]=01_problem_record, [NN]=NN_results, [N9]=NODE9_ANALYSIS,
[FRL]=FULL_RERUN_LOG, [VR]=VERIFIER_RESULT, [OI]=O5_OPEN_ISSUES.
"""
import numpy as np, json, os, sys
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'data')
CACHE = os.path.join(DATA, 'smooth_cache')
NODES = np.loadtxt(os.path.join(os.path.dirname(BASE), 'cmb_cold_spot/data/a5_nodes.txt'))
HIT = 5.0

passed, failed = [], []
def check(tag, cond, detail=''):
    (passed if cond else failed).append(tag)
    print(('  OK  ' if cond else '  FAIL') + f' {tag}  {detail}')

# ---- helpers ---------------------------------------------------------
def vecs_icrs(ra_deg, dec_deg):
    ra, dec = np.radians(ra_deg), np.radians(dec_deg)
    return np.stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)], axis=1)

def vecs_gal(l_deg, b_deg):
    return hp.ang2vec(np.asarray(l_deg), np.asarray(b_deg), lonlat=True)

def nearest(ra, dec, node_vecs_icrs, idx):
    v = vecs_icrs([ra], [dec])[0]
    dots = np.clip(node_vecs_icrs @ v, -1, 1)
    d = np.degrees(np.arccos(dots))
    return d[idx], d.argmin()

sc_gal = SkyCoord(ra=NODES[:,0]*u.deg, dec=NODES[:,1]*u.deg, frame='icrs').galactic
NL, NB = sc_gal.l.deg, sc_gal.b.deg
NV_icrs = vecs_icrs(NODES[:,0], NODES[:,1])
NV_gal = vecs_gal(NL, NB)

def nearest_gal(l, b, idx=None):
    v = hp.ang2vec(l, b, lonlat=True)
    dots = np.clip(NV_gal @ v, -1, 1)
    d = np.degrees(np.arccos(dots))
    return (d.min(), int(d.argmin())) if idx is None else (d[idx], int(d.argmin()))

def smooth_map(fwhm):
    return hp.read_map(os.path.join(CACHE, f'smica2_smooth{fwhm}.fits'), field=0)

def node_temps(fwhm):
    m = smooth_map(fwhm)
    nside = hp.get_nside(m)
    pix = hp.ang2pix(nside, NL, NB, lonlat=True)
    return m[pix]*1e6

print('='*70)
print('O5 INDEPENDENT DOC AUDIT — PART 1: nodes + literature')
print('='*70)

# [PR/NN] 60 nodes, 2 cols
check('A1 60 nodes x 2 cols', NODES.shape == (60, 2), str(NODES.shape))
check('A2 node0 ICRS (48.2999,-20.4373)', abs(NODES[0,0]-48.2999)<1e-3 and abs(NODES[0,1]+20.4373)<1e-3, str(NODES[0]))
check('A3 node0 gal (209,-57)', abs(NL[0]-209)<0.01 and abs(NB[0]+57)<0.01, f'({NL[0]:.3f},{NB[0]:.3f})')

# node spacing 26.09 deg (mean NN distance)
dmat = np.degrees(np.arccos(np.clip(NV_gal @ NV_gal.T, -1, 1)))
np.fill_diagonal(dmat, 360)
nn = dmat.min(axis=1)
check('A4 node spacing 26.09 (mean NN)', abs(nn.mean()-26.09)<0.05, f'mean={nn.mean():.3f}')
check('A5 Voronoi radius ~13.05', abs(nn.mean()/2-13.05)<0.03, f'{nn.mean()/2:.3f}')
# adjacency rule (25,28) used for BFS hops
adj_ok = ((nn > 25) & (nn < 28)).all()
check('A6 all NN distances in (25,28) deg', adj_ok, f'range {nn.min():.2f}-{nn.max():.2f}')

# [NN] literature catalog: 6 spots (2 confirmed + 4 sub-spots)
lit = json.load(open(os.path.join(DATA, 'literature_catalog.json')))['spots']
check('B1 lit 6 spots', len(lit) == 6, str(len(lit)))
conf = [s for s in lit if s['status'] == 'confirmed']
sub = [s for s in lit if s['status'] == 'sub-spot']
check('B2 lit 2 confirmed', len(conf) == 2, str(len(conf)))
check('B3 lit 4 sub-spots', len(sub) == 4, str(len(sub)))
cs = [s for s in lit if s['name'].startswith('The Cold Spot')][0]
check('B4 cold spot (209,-57)', abs(cs['l']-209)<1e-6 and abs(cs['b']+57)<1e-6)
d0, n0 = nearest_gal(cs['l'], cs['b'])
check('B5 cold spot -> nearest node 0.00 deg node0', d0 < 0.01 and n0 == 0, f'd={d0:.5f} node={n0}')
# [NN] gp10 nearest 10.1 deg (OI: node21)
gp = [s for s in lit if 'gp10' in s['name']][0]
dg, ng = nearest_gal(gp['l'], gp['b'])
check('B6 gp10 nearest ~10.05 deg', abs(dg-10.05) < 0.2, f'd={dg:.2f}')
check('B7 gp10 nearest node = 21 [OI]', ng == 21, f'node={ng}')
# sub-spots distances (rerun log: 3.655/1.142/3.206/3.458)
exp_sub = {'A': 3.65, 'B': 1.14, 'C': 3.21, 'D': 3.46}
for s in sub:
    d, n = nearest_gal(s['l'], s['b'])
    tag = s['name'].split('sub-spot ')[1][0]
    check(f'B8 sub-spot {tag} dist {exp_sub[tag]:.2f}', abs(d-exp_sub[tag]) < 0.05, f'd={d:.3f} node={n}')
# hit rates literature
lit_hits = sum(1 for s in lit if nearest_gal(s['l'], s['b'])[0] < HIT)
check('B9 lit all hits 5/6', lit_hits == 5, str(lit_hits))
conf_hits = sum(1 for s in conf if nearest_gal(s['l'], s['b'])[0] < HIT)
check('B10 lit confirmed hits 1/2', conf_hits == 1, str(conf_hits))

print(f'PART1: {len(passed)} passed, {len(failed)} failed')

# ======================================================================
# PART 2 — SMICA catalogue + hit rates + sky coverage [NN]
# ======================================================================
print('='*70)
print('PART 2: SMICA catalogue + hit rates + coverage')
print('='*70)
sm = json.load(open(os.path.join(DATA, 'smica_catalog.json')))
cold, hot = sm['cold'], sm['hot']
check('C1 SMICA 15 cold', len(cold) == 15, str(len(cold)))
check('C2 SMICA 14 hot', len(hot) == 14, str(len(hot)))
# cold #2 = cold spot: (208.40,-56.33) amp -126.6
c2 = cold[1]
check('C3 cold#2 = (208.40,-56.33)', abs(c2['peak_l']-208.40) < 0.05 and abs(c2['peak_b']+56.33) < 0.05,
      f"({c2['peak_l']:.2f},{c2['peak_b']:.2f})")
check('C4 cold#2 amp -126.6', abs(c2['amp_muK']+126.6) < 0.2, f"{c2['amp_muK']:.2f}")
dc2, nc2 = nearest_gal(c2['peak_l'], c2['peak_b'])
check('C5 cold#2 -> node0 0.75 deg', abs(dc2-0.75) < 0.05 and nc2 == 0, f'd={dc2:.3f} node={nc2}')
# all other cold: nearest 5.9-14.1 deg
other_cold = [nearest_gal(c['peak_l'], c['peak_b'])[0] for i, c in enumerate(cold) if i != 1]
check('C6 other cold nearest in 5.9-14.1', min(other_cold) > 5.5 and max(other_cold) < 14.5,
      f'min={min(other_cold):.2f} max={max(other_cold):.2f}')
# SMICA cold hits 1/15
n_cold_hits = sum(1 for c in cold if nearest_gal(c['peak_l'], c['peak_b'])[0] < HIT)
check('C7 SMICA cold hits 1/15', n_cold_hits == 1, str(n_cold_hits))
# hot: h2 1.11, h12 2.03 (match log); others >= 7.06
hotd = [nearest_gal(h['peak_l'], h['peak_b']) for h in hot]
n_hot_hits = sum(1 for d, n in hotd if d < HIT)
check('C8 SMICA hot hits 2/14', n_hot_hits == 2, str(n_hot_hits))
dh2 = sorted(d for d, n in hotd if d < HIT)
check('C9 hot hit dists 1.11 / 2.03', abs(dh2[0]-1.11) < 0.05 and abs(dh2[1]-2.03) < 0.05, str([round(x,2) for x in dh2]))
check('C10 hot non-hits min 7.06', min(d for d, n in hotd if d >= HIT) > 6.9,
      f'{min(d for d, n in hotd if d >= HIT):.2f}')
# sky coverage 11.4% (MC seed 42, 200k)
rng = np.random.default_rng(42)
z = rng.uniform(-1, 1, 200000)
phi = rng.uniform(0, 2*np.pi, 200000)
mc = np.stack([np.sqrt(1-z**2)*np.cos(phi), np.sqrt(1-z**2)*np.sin(phi), z], axis=1)
dots = np.clip(mc @ NV_icrs.T, -1, 1)
cov = (np.degrees(np.arccos(dots)) < HIT).any(axis=1).mean()
check('C11 coverage 11.4%', abs(cov-0.114) < 0.005, f'{cov*100:.2f}%')

# [NN] hit table: all 35 hits 8/35, expected 4.0 (11.4% x 35)
match = json.load(open(os.path.join(DATA, 'match_results.json')))['matches']
check('D1 35 spots total', len(match) == 35, str(len(match)))
n_hits_all = sum(1 for m in match if m['hit'])
check('D2 all hits = 8', n_hits_all == 8, str(n_hits_all))
check('D3 expected 4.0 = 0.114x35', abs(0.114*35 - 4.0) < 0.1, f'{0.114*35:.2f}')
# mean-nearest all = 8.60
dists_all = np.array([m['nearest_deg'] for m in match])
check('D4 mean-nearest 8.60', abs(dists_all.mean()-8.60) < 0.02, f'{dists_all.mean():.3f}')
check('D5 max nearest 17.80', abs(dists_all.max()-17.80) < 0.05, f'{dists_all.max():.3f}')

print(f'PART2: {len(passed)} passed, {len(failed)} failed')

# ======================================================================
# PART 3 — significance: 1000 rotations, seed 20260817 [NN]
# ======================================================================
print('='*70)
print('PART 3: significance (1000 rotations)')
print('='*70)

def rot_mat(rng):
    z = rng.uniform(-1, 1); phi = rng.uniform(0, 2*np.pi)
    ax = np.array([np.sqrt(1-z**2)*np.cos(phi), np.sqrt(1-z**2)*np.sin(phi), z])
    th = rng.uniform(0, 2*np.pi)
    K = np.array([[0,-ax[2],ax[1]],[ax[2],0,-ax[0]],[-ax[1],ax[0],0]])
    return np.eye(3) + np.sin(th)*K + (1-np.cos(th))*(K @ K)

cat = np.stack(vecs_icrs([m['ra'] for m in match], [m['dec'] for m in match]))
lit_conf = [i for i, m in enumerate(match) if m['kind'] == 'lit' and m['status'] != 'sub-spot']
c_idx = [i for i, m in enumerate(match) if m['kind'] == 'cold']
h_idx = [i for i, m in enumerate(match) if m['kind'] == 'hot']
nocs = [i for i, m in enumerate(match) if not (m['status'] == 'confirmed' and m['nearest_deg'] < 0.01)]
subsets = {'all (35)': list(range(35)), 'lit-confirmed (2)': lit_conf,
           'smica-cold (15)': c_idx, 'smica-hot (14)': h_idx,
           'all-minus-coldspot (34)': nocs}
exp = {'all (35)': (8, 4.0, 0.113, 8.60, 10.13, 0.87, -1.77, 0.042),
       'lit-confirmed (2)': (1, 0.2, 0.197, 5.03, 10.11, 2.91, -1.75, 0.046),
       'smica-cold (15)': (1, 1.7, 0.831, 9.23, 10.13, 0.96, -0.94, 0.173),
       'smica-hot (14)': (2, 1.6, 0.488, 10.07, 10.19, 1.14, -0.11, 0.424),
       'all-minus-coldspot (34)': (7, 4.0, 0.134, 8.85, 10.12, 0.80, -1.58, 0.072)}
rng = np.random.default_rng(20260817)
for label, idx in subsets.items():
    cv = cat[idx]
    dots = np.clip(cv @ NV_icrs.T, -1, 1)
    dd = np.degrees(np.arccos(dots))
    obs_h = int((dd < HIT).any(axis=1).sum())
    obs_m = float(dd.min(axis=1).mean())
    rh = np.zeros(1000, int); rm = np.zeros(1000)
    for k in range(1000):
        R = rot_mat(rng)
        rv = (R @ NV_icrs.T).T
        d2 = np.degrees(np.arccos(np.clip(cv @ rv.T, -1, 1)))
        rh[k] = (d2 < HIT).any(axis=1).sum()
        rm[k] = d2.min(axis=1).mean()
    e = exp[label]
    check(f'E1 {label} hits {e[0]} p={e[2]}', obs_h == e[0] and abs((rh >= obs_h).mean()-e[2]) < 0.005,
          f'obs={obs_h} p={(rh >= obs_h).mean():.4f}')
    check(f'E2 {label} mean-nearest {e[3]} p={e[7]} z={e[6]}',
          abs(obs_m-e[3]) < 0.05 and abs((rm <= obs_m).mean()-e[7]) < 0.005 and abs(rm.mean()-e[4]) < 0.05,
          f'obs={obs_m:.2f} rot={rm.mean():.2f}+-{rm.std():.2f} z={(obs_m-rm.mean())/rm.std():+.2f} p={(rm <= obs_m).mean():.4f}')
# stability: different seed, 500 rotations, all-35 mean-nearest p must stay < 0.1
rng2 = np.random.default_rng(999)
rm2 = []
for k in range(500):
    R = rot_mat(rng2); rv = (R @ NV_icrs.T).T
    d2 = np.degrees(np.arccos(np.clip(cat @ rv.T, -1, 1)))
    rm2.append(d2.min(axis=1).mean())
rm2 = np.array(rm2)
p2 = (rm2 <= dists_all.mean()).mean()
check('E3 stability seed999 p<0.1', p2 < 0.1, f'p={p2:.3f}')

print(f'PART3: {len(passed)} passed, {len(failed)} failed')

# ======================================================================
# PART 4 — cross-scale component matching (independent flood-fill) [NN]
# ======================================================================
print('='*70)
print('PART 4: cross-scale flood-fill (independent)')
print('='*70)
from collections import deque
import gc

def ff_components(T, th, mask, nbrs):
    npix = len(T)
    pass_c = (T < -th) & mask
    pass_h = (T > th) & mask
    out = {}
    for kind, pm in (('cold', pass_c), ('hot', pass_h)):
        visited = np.zeros(npix, bool)
        comps = []
        for start in np.where(pm)[0]:
            if visited[start]:
                continue
            comp = []
            q = deque([start]); visited[start] = True
            while q:
                p = q.popleft(); comp.append(p)
                for nb in nbrs[:, p]:
                    if nb >= 0 and not visited[nb] and pm[nb]:
                        visited[nb] = True; q.append(nb)
            comps.append(comp)
        out[kind] = comps
    return out

config = [(1.0, 2.5), (3.0, 2.0), (5.0, 2.0)]
exp_xs = {'1.0': {'cold': (2, [0, 9]), 'hot': (1, [42])},
          '3.0': {'cold': (1, [0]), 'hot': (1, [53])},
          '5.0': {'cold': (1, [0]), 'hot': (2, [53, 54])}}
node9_peak_check = None
for fwhm, th_sig in config:
    m = smooth_map(fwhm)
    nside = hp.get_nside(m)
    T = m*1e6
    l_arr, b_arr = hp.pix2ang(nside, np.arange(hp.nside2npix(nside)), lonlat=True)
    mask = np.abs(b_arr) >= 25
    sigma = float(np.std(T[mask]))
    pix_area = hp.nside2pixarea(nside)
    print(f'  {fwhm} deg: sigma={sigma:.1f}')
    nbrs = hp.get_all_neighbours(nside, np.arange(hp.nside2npix(nside))).astype(np.int32)
    comps = ff_components(T, th_sig*sigma, mask, nbrs)
    del nbrs, l_arr, b_arr, mask; gc.collect()
    for kind in ('cold', 'hot'):
        cl = comps[kind]
        cl.sort(key=lambda c: T[c].min() if kind == 'cold' else -T[c].max())
        top = cl[:12]
        hits = []
        for c in top:
            pk = c[np.argmin(T[c])] if kind == 'cold' else c[np.argmax(T[c])]
            lp, bp = hp.pix2ang(nside, pk, lonlat=True)
            v = hp.ang2vec(float(lp), float(bp), lonlat=True)
            dots = np.clip(NV_gal @ v, -1, 1)
            d = float(np.degrees(np.arccos(dots)).min())
            n = int(dots.argmax())
            hits.append((d, n, float(lp), float(bp)))
        nh = sorted(d for d, n, lp, bp in hits if d < 5)
        nhits = len(nh)
        nodes = sorted({n for d, n, lp, bp in hits if d < 5})
        e = exp_xs[str(fwhm)][kind]
        check(f'F1 {fwhm} {kind} top12 {e[0]}/12 nodes={e[1]}',
              nhits == e[0] and nodes == e[1],
              f'got {nhits}/12 nodes={nodes} hitdists={[round(x,2) for x in nh]}')
    del m, T; gc.collect()

# node0 hit in >=2 scales (cold) [NN/VR]
xs = json.load(open(os.path.join(DATA, 'cross_scale_match.json')))
scales0 = [f for f, sh in xs.items() if 0 in sh['cold']['nodes']]
check('F2 node0 cold hit in >=2 scales', len(scales0) >= 2, f'{scales0}')
# NODE9 claim: 1.0 deg component peak (213.73,-32.53) at 1.71 deg from node9
lp9, bp9 = NL[9], NB[9]
d213 = np.degrees(np.arccos(np.clip(hp.ang2vec(213.73, -32.53, lonlat=True) @ hp.ang2vec(lp9, bp9, lonlat=True), -1, 1)))
check('F3 N9 peak (213.73,-32.53) at 1.71 deg from node9', abs(d213-1.71) < 0.1, f'd={d213:.2f}')
# is there a 1.0 deg component with that peak? recompute 1.0 cold comps and search
m1 = smooth_map(1.0); nside1 = hp.get_nside(m1); T1 = m1*1e6
l1, b1 = hp.pix2ang(nside1, np.arange(hp.nside2npix(nside1)), lonlat=True)
mask1 = np.abs(b1) >= 25
sigma1 = float(np.std(T1[mask1]))
nbrs1 = hp.get_all_neighbours(nside1, np.arange(hp.nside2npix(nside1))).astype(np.int32)
cc = ff_components(T1, 2.5*sigma1, mask1, nbrs1)['cold']
del nbrs1, l1, b1, mask1; gc.collect()
pix213 = hp.ang2pix(nside1, 213.73, -32.53, lonlat=True)
own = [c for c in cc if pix213 in c]
check('F4 1.0deg component contains peak (213.73,-32.53)', len(own) == 1, f'{len(own)} comps')
if own:
    c = own[0]
    pk = c[np.argmin(T1[c])]
    pl, pb = hp.pix2ang(nside1, pk, lonlat=True)
    rank = sum(1 for x in cc if T1[x].min() < T1[c].min()) + 1
    print(f'     peak of owning comp = ({float(pl):.2f},{float(pb):.2f}) amp={T1[pk]*1e6:.1f} uK rank={rank} top12={rank<=12}')
    check('F5 owning comp peak = (213.73,-32.53)', abs(float(pl)-213.73) < 1.0 and abs(float(pb)+32.53) < 1.0,
          f'({float(pl):.2f},{float(pb):.2f})')
del m1, T1; gc.collect()

print(f'PART4: {len(passed)} passed, {len(failed)} failed')

# ======================================================================
# PART 5a — node9 multi-scale temps/ranks + radial profile [N9]
# ======================================================================
print('='*70)
print('PART 5a: node9 multi-scale + radial profile')
print('='*70)
check('G1 node9 ICRS (75.268,-15.212)', abs(NODES[9,0]-75.268) < 0.01 and abs(NODES[9,1]+15.212) < 0.01,
      str(NODES[9]))
check('G2 node9 gal (214.923,-31.159)', abs(NL[9]-214.923) < 0.01 and abs(NB[9]+31.159) < 0.01,
      f'({NL[9]:.3f},{NB[9]:.3f})')
# BFS hop from node0 (adjacency 25-28 deg) -> hop(node9)=1
dmat2 = np.degrees(np.arccos(np.clip(NV_gal @ NV_gal.T, -1, 1)))
adj = {(i, j) for i in range(60) for j in range(60)
       if 25 < dmat2[i, j] < 28}
hop = {0: 0}
q = deque([0])
while q:
    uu = q.popleft()
    for v in range(60):
        if (uu, v) in adj and v not in hop:
            hop[v] = hop[uu] + 1; q.append(v)
check('G3 node9 BFS hop = 1', hop.get(9) == 1, str(hop.get(9)))
nbr9 = sorted(v for v in range(60) if (9, v) in adj)
check('G4 node9 neighbors = {0,16,33,58}', nbr9 == [0, 16, 33, 58], str(nbr9))

exp_ts = {0.5: (-163.7, -203.1, 4), 1.0: (-117.1, -174.4, 4), 1.5: (-112.2, -161.8, 4),
          2.0: (-113.8, -154.7, 4), 3.0: (-110.6, -145.0, 3), 4.0: (-107.4, -136.0, 3),
          5.0: (-105.0, -124.6, 3), 7.0: (-99.1, -99.7, 3), 10.0: (-90.3, -68.8, 1)}
for fwhm, (t9, t0, r9) in exp_ts.items():
    nt = node_temps(fwhm)
    v9, v0 = nt[9], nt[0]
    rk = int((nt < v9).sum()) + 1
    check(f'G5 {fwhm} node9={t9} node0={t0} rank={r9}',
          abs(v9-t9) < 0.5 and abs(v0-t0) < 0.5 and rk == r9,
          f'got n9={v9:.1f} n0={v0:.1f} rank={rk}')
# node0 rank 1/60 at 3.0 (doc: 1/60)
nt3 = node_temps(3.0)
check('G6 node0 3.0 rank 1/60', int((nt3 < nt3[0]).sum()) + 1 == 1)

# radial profile at 1.0 (great circle node0 -> node9; doc points at 0/20/50/90/100%)
m1r = smooth_map(1.0); ns1 = hp.get_nside(m1r); T1r = m1r*1e6
v0v = hp.ang2vec(NL[0], NB[0], lonlat=True); v9v = hp.ang2vec(NL[9], NB[9], lonlat=True)
exp_rad = [(0.00, -174.4, 209.00, -57.00), (0.20, -65.2, 210.67, -51.95), (0.50, +75.4, 212.62, -44.12),
           (0.90, -104.6, 214.53, -33.69), (1.00, -117.1, 214.92, -31.16)]
for frac, (fexp, t, el, eb) in zip([0, 0.2, 0.5, 0.9, 1.0], exp_rad):
    vv = v0v + frac*(v9v - v0v); vv /= np.linalg.norm(vv)
    lp, bp = hp.vec2ang(vv, lonlat=True)
    lp, bp = float(lp[0]), float(bp[0])
    pix = hp.ang2pix(ns1, lp, bp, lonlat=True)
    check(f'G7 radial {frac*100:.0f}% = {t} @({el},{eb})',
          abs(T1r[pix]-t) < 2 and abs(lp-el) < 0.5 and abs(bp-eb) < 0.5,
          f'got {T1r[pix]:.1f} @({lp:.2f},{bp:.2f})')
del m1r, T1r
# full-map sigma at 3.0 (|b|>=25) = 44.6 -> z = -2.48
m3s = smooth_map(3.0); ns3s = hp.get_nside(m3s)
l3s, b3s = hp.pix2ang(ns3s, np.arange(hp.nside2npix(ns3s)), lonlat=True)
sig3full = float(np.std((m3s*1e6)[np.abs(b3s) >= 25]))
check('G8 3.0 full-map sigma 44.6', abs(sig3full-44.6) < 1.0, f'{sig3full:.1f}')
check('G9 node9 global z -2.48', abs(nt3[9]/sig3full + 2.48) < 0.1, f'{nt3[9]/sig3full:.2f}')
del m3s, l3s, b3s
# hop1 z: node9 vs hop1 siblings
h1 = np.array([nt3[i] for i in range(60) if hop.get(i) == 1])
z9 = (nt3[9]-h1.mean())/h1.std()
check('G10 hop1 z -1.70', abs(z9+1.70) < 0.1, f'{z9:.2f}')
others = sorted([nt3[i] for i in range(60) if hop.get(i) == 1 and i != 9])
check('G11 hop1 others +4.9/+32.7/+34.0', abs(others[0]-4.9) < 1 and abs(others[1]-32.7) < 1 and abs(others[2]-34.0) < 1,
      f'{[round(x,1) for x in others]}')
# 3.0 ranking: node0(-145) > node47(-135.7) > node9(-110.6)
order = np.argsort(nt3)
check('G12 rank order node0,node47,node9 = top3',
      list(order[:3]) == [0, 47, 9], str(list(order[:3])))
check('G13 node47 3.0 = -135.7', abs(nt3[47]+135.7) < 0.5, f'{nt3[47]:.1f}')

print(f'PART5a: {len(passed)} passed, {len(failed)} failed')

# ======================================================================
# PART 5b — node9 null (26 deg ring) + antipode + cross-map [N9][VR]
# ======================================================================
print('='*70)
print('PART 5b: null test + antipode + cross-map')
print('='*70)
m3b = smooth_map(3.0); ns3 = hp.get_nside(m3b); T3b = m3b*1e6
# 26 deg ring null, seed 9, 2000 samples (script 09)
rng9 = np.random.default_rng(9)
v0v = hp.ang2vec(NL[0], NB[0], lonlat=True)
Ts = []
for _ in range(2000):
    r = rng9.normal(size=3); r = r - (r @ v0v)*v0v; r /= np.linalg.norm(r)
    v = np.cos(np.radians(26.166))*v0v + np.sin(np.radians(26.166))*r
    pix = hp.vec2pix(ns3, *v)
    if abs(hp.pix2ang(ns3, pix, lonlat=True)[1]) < 25:
        continue
    Ts.append(T3b[pix])
Ts = np.array(Ts)
p26 = float((Ts <= T3b[hp.ang2pix(ns3, NL[9], NB[9], lonlat=True)]).mean())
check('H1 26 ring mean +5.8', abs(Ts.mean()-5.8) < 2, f'{Ts.mean():.1f}')
check('H2 26 ring std 59.0', abs(Ts.std()-59.0) < 3, f'{Ts.std():.1f}')
check('H3 26 ring p=0.018', abs(p26-0.018) < 0.01, f'p={p26:.4f} (n={len(Ts)})')
# antipode of node9: (34.92,+31.16) = +24.0 uK
anti = -hp.ang2vec(NL[9], NB[9], lonlat=True)
la, ba = hp.vec2ang(anti, lonlat=True)
la, ba = float(la[0]), float(ba[0])
pix_a = hp.ang2pix(ns3, la, ba, lonlat=True)
check('H4 antipode (34.92,+31.16)', abs(la-34.92) < 0.5 and abs(ba-31.16) < 0.5, f'({la:.2f},{ba:.2f})')
check('H5 antipode T = +24.0', abs(T3b[pix_a]-24.0) < 5, f'{T3b[pix_a]:.1f}')
del m3b, T3b
# cross-map verification: smooth raw SMICA/NILC/Commander at 3.0 [N9]
import subprocess
maps = {'SMICA': ('/tmp/smica2.fits', False), 'NILC': ('/tmp/nilc.fits', True),
        'Commander': ('/tmp/commander.fits', True)}
sig = np.radians(3.0)/(2*np.sqrt(2*np.log(2)))
res = {}
for name, (path, nested) in maps.items():
    if not os.path.exists(path):
        check(f'H6 {name} map present', False, 'MISSING')
        continue
    m = hp.read_map(path, field=0, nest=nested)
    if nested:
        m = hp.reorder(m, n2r=True)
    ms = hp.remove_dipole(hp.smoothing(m, sigma=sig))
    nside = hp.get_nside(ms)
    T = ms*1e6
    pix = hp.ang2pix(nside, NL, NB, lonlat=True)
    nt = T[pix]
    res[name] = (nt[9], nt[0], int((nt < nt[9]).sum())+1)
    check(f'H6 {name} rank 3/60', res[name][2] == 3, f'rank={res[name][2]}')
    del m, ms, T
n9v = np.array([v[0] for v in res.values()])
n0v = np.array([v[1] for v in res.values()])
sp9 = (n9v.max()-n9v.min())/abs(n9v.mean())*100
sp0 = (n0v.max()-n0v.min())/abs(n0v.mean())*100
check('H7 node9 spread 2.6%', abs(sp9-2.6) < 0.5, f'{sp9:.1f}%')
check('H8 node0 spread 0.7%', abs(sp0-0.7) < 0.3, f'{sp0:.1f}%')
check('H9 SMICA n9 -110.6 / NILC -110.8 / Comm -107.9',
      abs(res['SMICA'][0]+110.6) < 0.5 and abs(res['NILC'][0]+110.8) < 0.5 and abs(res['Commander'][0]+107.9) < 0.5,
      {k: round(v[0], 1) for k, v in res.items()})
check('H10 SMICA n0 -145.0 / Comm -144.0',
      abs(res['SMICA'][1]+145.0) < 0.5 and abs(res['Commander'][1]+144.0) < 0.5,
      {k: round(v[1], 1) for k, v in res.items()})
# verifier p=0.0215 reproduction (seed 42, 2000 pts, 26 deg ring)
rng42 = np.random.default_rng(42)
m3c = smooth_map(3.0); ns3c = hp.get_nside(m3c); T3c = m3c*1e6
v_c = hp.ang2vec(209, -57, lonlat=True)
tmp = np.array([1.0, 0.0, 0.0])
if abs(np.dot(tmp, v_c.flatten())) > 0.9:
    tmp = np.array([0.0, 1.0, 0.0])
u1 = np.cross(v_c.flatten(), tmp); u1 /= np.linalg.norm(u1)
u2 = np.cross(v_c.flatten(), u1); u2 /= np.linalg.norm(u2)
angs = rng42.uniform(0, 2*np.pi, 2000)
ring = np.cos(np.radians(26))*v_c.flatten()[None, :] + np.sin(np.radians(26))*(
    np.cos(angs)[:, None]*u1[None, :] + np.sin(angs)[:, None]*u2[None, :])
rl, rb = hp.vec2ang(ring, lonlat=True)
rl = np.asarray(rl).flatten(); rb = np.asarray(rb).flatten()
rt = T3c[hp.ang2pix(ns3c, rl, rb, lonlat=True)]
T9c = T3c[hp.ang2pix(ns3c, NL[9], NB[9], lonlat=True)]
p42 = float((rt < T9c).mean())
check('H11 verifier p=0.0215 repro', abs(p42-0.0215) < 0.005, f'p={p42:.4f}')
del m3c, T3c

print(f'PART5b: {len(passed)} passed, {len(failed)} failed')

# ======================================================================
# PART 6 — open-issues values [OI][PR] + node-index bug check [03]
# ======================================================================
print('='*70)
print('PART 6: open-issues values + node-index bug')
print('='*70)
nt3b = node_temps(3.0)
# node47: l=313.47, b=-8.58 (|b|<30 near plane)
check('I1 node47 gal (313.47,-8.58)', abs(NL[47]-313.47) < 0.1 and abs(NB[47]+8.58) < 0.1,
      f'({NL[47]:.2f},{NB[47]:.2f})')
d47_0 = np.degrees(np.arccos(np.clip(NV_gal[47] @ NV_gal[0], -1, 1)))
check('I2 node47-coldspot 90.5', abs(d47_0-90.5) < 0.5, f'{d47_0:.1f}')
d47_gp = np.degrees(np.arccos(np.clip(NV_gal[47] @ hp.ang2vec(32, -8, lonlat=True), -1, 1)))
check('I3 node47-gp10 77.6', abs(d47_gp-77.6) < 0.5, f'{d47_gp:.1f}')
# gp10 nearest nodes: 21 (10.1), 26 (20.2, -49.0), 22 (24.0, -31.2)
gpv = hp.ang2vec(32, -8, lonlat=True)
dg = np.degrees(np.arccos(np.clip(NV_gal @ gpv, -1, 1)))
order5 = np.argsort(dg)
check('I4 gp10 nearest node21 10.1', order5[0] == 21 and abs(dg[21]-10.1) < 0.5, f'node{order5[0]} d={dg[order5[0]]:.1f}')
check('I5 gp10 node26 20.2 -49.0', abs(dg[26]-20.2) < 0.5 and abs(nt3b[26]+49.0) < 2, f'd={dg[26]:.1f} T={nt3b[26]:.1f}')
check('I6 gp10 node22 24.0 -31.2', abs(dg[22]-24.0) < 0.5 and abs(nt3b[22]+31.2) < 2, f'd={dg[22]:.1f} T={nt3b[22]:.1f}')
# node57: PR says antipode +8.2 uK. Check temp at all scales + geometry vs node0/cold spot
nt57 = {f: node_temps(f)[57] for f in [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 7.0, 10.0]}
d57_0 = np.degrees(np.arccos(np.clip(NV_gal[57] @ NV_gal[0], -1, 1)))
d57_cs = np.degrees(np.arccos(np.clip(NV_gal[57] @ hp.ang2vec(209, -57, lonlat=True), -1, 1)))
print(f'  node57: d(node0)={d57_0:.2f} d(coldspot)={d57_cs:.2f} temps={ {k: round(v,1) for k,v in nt57.items()} }')
# SESSION_START: node57 = antipode 174.66 deg opposite — d(node0,node57) = 174.66
check('I7 node57 174.66 deg from node0 [SS]', abs(d57_0-174.66) < 0.05, f'{d57_0:.2f}')
# PR +8.2 uK matches 4.0 deg (+8.4); 3.0 deg = +4.8 (different scale, historical quote)
check('I8 node57 +8.2 uK ~= 4.0 deg value', abs(nt57[4.0]-8.2) < 1.5, f'4.0deg={nt57[4.0]:.1f} 3.0deg={nt57[3.0]:.1f}')
# node47 -123.4 (PR, from 26_anchor_control.py) is a different-scale quote; O5 standard 3.0 = -135.7
nt47 = {f: node_temps(f)[47] for f in [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 7.0, 10.0]}
print(f'  node47 all scales: { {k: round(v,1) for k,v in nt47.items()} }')
check('I9 node47 -123.4 not at O5 3.0 (=-135.7); nearest 4.0 (-125.0)',
      abs(nt47[3.0]+135.7) < 0.5 and abs(nt47[4.0]+123.4) > 1.0, f'3.0={nt47[3.0]:.1f} 4.0={nt47[4.0]:.1f}')
# 03_match_nodes argmin bug: 'node' field = argmin(dots) = FARTHEST node
match2 = match
d_mat = np.degrees(np.arccos(np.clip(np.stack(vecs_icrs([m['ra'] for m in match2], [m['dec'] for m in match2])) @ NV_icrs.T, -1, 1)))
nearest_idx = d_mat.argmin(axis=1)   # smallest distance = NEAREST
farthest_idx = d_mat.argmax(axis=1)  # largest distance = FARTHEST
rec_idx = np.array([m['node'] for m in match2])
check('J1 03 node field = FARTHEST (argmin-dots bug confirmed)', (rec_idx == farthest_idx).all(),
      f'{sum(rec_idx==farthest_idx)}/35 = farthest, {sum(rec_idx==nearest_idx)}/35 = nearest')
check('J2 distances in match are correct', np.allclose(np.array([m["nearest_deg"] for m in match2]),
      d_mat.min(axis=1), atol=1e-6))
# cross_scale node fields correct (argmin of distance)
xs2 = json.load(open(os.path.join(DATA, 'cross_scale_match.json')))
ok_node = True
for f in ['1.0', '3.0', '5.0']:
    for k in ['cold', 'hot']:
        for h in xs2[f][k]['details']:
            d2, n2 = nearest_gal(h['l'], h['b'])
            if n2 != h['node'] or abs(d2 - h['dist']) > 0.01:
                ok_node = False
                print(f'  MISMATCH {f} {k} node={h["node"]} vs computed {n2}')
check('J3 cross_scale node fields = nearest', ok_node)
# sigma claims from FRL: 5.0=38.1, 1.0=64.9, 3.0=44.6
m5s = smooth_map(5.0); n5s = hp.get_nside(m5s)
l5, b5 = hp.pix2ang(n5s, np.arange(hp.nside2npix(n5s)), lonlat=True)
m5k = np.abs(b5) >= 25
check('K1 FRL sigma 5.0 = 38.1', abs(np.std(m5s[m5k]*1e6)-38.1) < 1.0, f'{np.std(m5s[m5k]*1e6):.2f}')
del m5s, l5, b5, m5k
# cold-spot family: all 5 lit hits + SMICA c2 nearest node0 (OI p=0.072 attribution)
near0 = [m['name'] for m in match2 if m['nearest_deg'] < 5 and (m['kind'] == 'lit' or m['name'] == 'SMICA-c2')]
check('K2 cold-spot family = lit hits + c2', len(near0) >= 5, str(near0))

print()
print('='*70)
print(f"FINAL: {len(passed)} passed, {len(failed)} failed  (total {len(passed)+len(failed)})")
sys.exit(0 if not failed else 1)






