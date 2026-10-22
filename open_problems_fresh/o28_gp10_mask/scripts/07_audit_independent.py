#!/usr/bin/env python3
"""
O28 Audit: INDEPENDENT re-verification (2026-09-11 round)
==========================================================
Independent cross-check of the ENTIRE O28 derivation chain (gp10 mask correction).
Does NOT import any original script; does NOT read the data JSONs for the raw
recompute claims (JSONs are only used for self-consistency, section I).

Sections (mirror the derivation chain 00->04):
  A. Node distances + temperatures (raw from a5_nodes.txt + SMICA 4.17)
  B. Flood-fill cold components (INDEPENDENT algorithm: tangent-plane grid +
     scipy.ndimage.label, vs original spherical BFS)
  C. Planck Nside=16 statistics (region vs rest-of-sky)
  D. Fine-scale 0.5 deg peak scan
  E. Radial profile rings
  F. Cross-map at (32.4,-5.5) (SMICA/NILC/Commander 4.17 deg)
  G. Mask-corrected cold centroids + nearest-node distances
  H. Random control: same-seed exact reproduction + different-seed MC consistency
  I. JSON self-consistency (stored JSON vs raw recompute)
  J. Doc-claim coverage (NN_results.md / 01_problem_record.md / SESSION_START.md)
  K. Timeline-aware cross-doc (O5-origin registration values = legitimate history)

Path-relative (O15 rule): works from any checkout, no hardcoded repo path.
"""
import os, json, sys
import numpy as np
import healpy as hp
from scipy import ndimage
from scipy.stats import skew as scipy_skew
from astropy.coordinates import SkyCoord
import astropy.units as u

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
O28 = os.path.dirname(SCRIPT_DIR)              # .../o28_gp10_mask
FRESH = os.path.dirname(O28)                   # .../open_problems_fresh
CACHE = os.path.join(FRESH, 'o5_catalog_compare', 'data', 'smooth_cache')
NODE_FILE = os.path.join(FRESH, 'cmb_cold_spot', 'data', 'a5_nodes.txt')
DATA = os.path.join(O28, 'data')

GP_L, GP_B = 32.0, -8.0
checks = []
def chk(name, cond, detail=""):
    checks.append((name, bool(cond), detail))

def angdist_vec(l1, b1, l2_arr, b2_arr):
    v1 = hp.ang2vec(np.radians(90-b1), np.radians(l1))
    v2 = hp.ang2vec(np.radians(90-b2_arr), np.radians(l2_arr))
    return np.degrees(np.arccos(np.clip(v1 @ v2.T, -1, 1)))

def read_smooth(name):
    return hp.read_map(os.path.join(CACHE, name), field=0)

# ---------------------------------------------------------------- A. nodes
nodes = np.loadtxt(NODE_FILE)
ng = SkyCoord(ra=nodes[:,0]*u.deg, dec=nodes[:,1]*u.deg, frame='icrs').galactic
nl, nb = ng.l.deg, ng.b.deg
d = angdist_vec(GP_L, GP_B, nl, nb)
i_near = int(np.argmin(d))
chk("A1: nearest node = index 21 @ 10.05", i_near == 21 and abs(d[21]-10.05) < 0.05, f"idx {i_near} @ {d[i_near]:.2f}")
chk("A2: node26 @ 20.25, node22 @ 24.02", abs(d[26]-20.25) < 0.05 and abs(d[22]-24.02) < 0.05, f"{d[26]:.2f} / {d[22]:.2f}")
# node49 (1-indexed label from match_results) is file line 50 = nodes[49]: must be FAR
d49 = float(angdist_vec(GP_L, GP_B, np.array([nl[49]]), np.array([nb[49]]))[0])
chk("A3: nodes[49] ('node49' label) is NOT nearest (168 deg)", d49 > 100, f"{d49:.1f}")

m417 = read_smooth('smica2_smooth4.17.fits')
nside417 = hp.get_nside(m417)
def T_at(l, b):
    return m417[hp.ang2pix(nside417, l, b, lonlat=True)] * 1e6
chk("A4: node21 T(4.17) = +95.5", abs(T_at(nl[21], nb[21]) - 95.5) < 2.0, f"{T_at(nl[21],nb[21]):.1f}")
chk("A5: node26 T(4.17) = -48.3", abs(T_at(nl[26], nb[26]) + 48.3) < 2.0, f"{T_at(nl[26],nb[26]):.1f}")
chk("A6: node22 T(4.17) = -23.6", abs(T_at(nl[22], nb[22]) + 23.6) < 2.0, f"{T_at(nl[22],nb[22]):.1f}")
chk("A7: gp10 centre T = +10.4", abs(T_at(GP_L, GP_B) - 10.4) < 1.0, f"{T_at(GP_L,GP_B):.1f}")

# ---------------------------------------------------------------- B. flood-fill (independent grid algorithm)
def grid_floodfill(name, fwhm, b_cut, search_rad=25.0, min_comp=5, res_deg=0.06):
    """Independent flood-fill: project disc pixels onto a local tangent-plane
    grid, threshold, scipy.ndimage.label (8-connectivity). Different code path
    from the original spherical BFS."""
    m = read_smooth(name)
    m10 = hp.ud_grade(m, nside_out=1024)
    ns = 1024
    l_all, b_all = hp.pix2ang(ns, np.arange(hp.nside2npix(ns)), lonlat=True)
    sky = np.abs(b_all) >= 25
    sigma = float(np.std(m10[sky]))
    th = 1.5 * sigma
    vec_gp = hp.ang2vec(np.radians(90-GP_B), np.radians(GP_L))
    disc = hp.query_disc(ns, vec_gp, np.radians(search_rad))
    ld, bd = hp.pix2ang(ns, disc, lonlat=True)
    Td = m10[disc]
    passpix = (Td < -th) & (np.abs(bd) >= b_cut)
    npass = int(passpix.sum())
    # tangent-plane gnomonic projection around gp10
    l0r, b0r = np.radians(GP_L), np.radians(GP_B)
    lr, br = np.radians(ld), np.radians(bd)
    cosc = np.sin(b0r)*np.sin(br) + np.cos(b0r)*np.cos(br)*np.cos(lr-l0r)
    x = np.cos(br)*np.sin(lr-l0r) / cosc
    y = (np.cos(b0r)*np.sin(br) - np.sin(b0r)*np.cos(br)*np.cos(lr-l0r)) / cosc
    xd, yd = np.degrees(x), np.degrees(y)
    half = search_rad + 2.0
    nx = int(2*half/res_deg) + 1
    grid = np.zeros((nx, nx), dtype=bool)
    ix = np.clip(((xd + half)/res_deg).astype(int), 0, nx-1)
    iy = np.clip(((yd + half)/res_deg).astype(int), 0, nx-1)
    grid[iy[passpix], ix[passpix]] = True
    lab, nlab = ndimage.label(grid, structure=np.ones((3,3)))
    comps = []
    for c in range(1, nlab+1):
        sel = lab == c
        if sel.sum() < min_comp:
            continue
        # map back to disc pixels
        idx = np.where(sel)
        # pixels in this component: intersect grid cells with disc pixels
        cells = set(zip(idx[0].tolist(), idx[1].tolist()))
        dpix = []
        for k in range(len(disc)):
            if (iy[k], ix[k]) in cells and passpix[k]:
                dpix.append(k)
        if len(dpix) < min_comp:
            continue
        Tcomp = Td[dpix]
        peakk = dpix[int(np.argmin(Tcomp))]
        lp, bp = hp.pix2ang(ns, disc[peakk], lonlat=True)
        comps.append(dict(peak_l=float(lp), peak_b=float(bp),
                          amp=float(Tcomp.min()*1e6), n=len(dpix)))
    return dict(sigma_uK=sigma*1e6, th_uK=th*1e6, npass=npass, comps=comps)

for fwhm in ['4.17', '5.0', '7.0']:
    r = grid_floodfill(f'smica2_smooth{fwhm}.fits', fwhm, 5)
    chk(f"B1: {fwhm} deg sigma/th ~ docs (40.3/60.4 etc)",
        abs(r['sigma_uK'] - {'4.17':40.3,'5.0':38.1,'7.0':34.1}[fwhm]) < 1.0, f"sigma {r['sigma_uK']:.1f}")
    chk(f"B2: {fwhm} deg ZERO cold pixels below -1.5sigma in disc (bcut5)", r['npass'] == 0,
        f"npass={r['npass']}")
    chk(f"B3: {fwhm} deg zero cold comps (independent label)", len(r['comps']) == 0)

r3 = grid_floodfill('smica2_smooth3.0.fits', '3.0', 5)
chk("B4: 3.0 deg has >=1 cold comp (bcut5)", len(r3['comps']) >= 1, f"{len(r3['comps'])} comps")
strong = sorted(r3['comps'], key=lambda c: c['amp'])[0]
chk("B5: 3.0 deg strongest comp peak ~ (22.4,-25.0)",
    abs(strong['peak_l']-22.4) < 0.6 and abs(strong['peak_b']+25.0) < 0.6,
    f"({strong['peak_l']:.2f},{strong['peak_b']:.2f})")
chk("B6: 3.0 deg strongest comp amp ~ -83.2", abs(strong['amp'] + 83.2) < 2.0, f"{strong['amp']:.1f}")
# 3.0 deg comp distance from gp10 ~ 19-20 deg
compd = float(angdist_vec(GP_L, GP_B, np.array([strong['peak_l']]), np.array([strong['peak_b']]))[0])
chk("B7: 3.0 deg comp ~20 deg from gp10", 18.5 < compd < 21.0, f"{compd:.1f}")
r3b10 = grid_floodfill('smica2_smooth3.0.fits', '3.0', 10)
chk("B8: 3.0 deg bcut10 keeps only the (22.4,-25) comp", len(r3b10['comps']) == 1,
    f"{len(r3b10['comps'])} comps")

# ---------------------------------------------------------------- C. Nside16
m16 = hp.ud_grade(m417, nside_out=16)
npix16 = hp.nside2npix(16)
l16, b16 = hp.pix2ang(16, np.arange(npix16), lonlat=True)
vec_gp = hp.ang2vec(np.radians(90-GP_B), np.radians(GP_L))
disc16 = hp.query_disc(16, vec_gp, np.radians(30.0))
reg = m16[disc16]*1e6
rest = m16[np.abs(b16) >= 25]*1e6
var_ratio = np.var(reg)/np.var(rest)
sk_reg = float(scipy_skew(reg))
sk_rest = float(scipy_skew(rest))
chk("C1: region n = 205 pix", len(reg) == 205, f"{len(reg)}")
chk("C2: var ratio ~0.745 (doc 0.75x)", abs(var_ratio - 0.745) < 0.01, f"{var_ratio:.3f}")
chk("C3: region skew POSITIVE ~+0.12", 0.10 < sk_reg < 0.15, f"{sk_reg:.3f}")
chk("C4: rest skew negative ~-0.15", -0.20 < sk_rest < -0.10, f"{sk_rest:.3f}")
chk("C5: region mean +22.9, rest +0.3", abs(reg.mean()-22.9) < 0.5 and abs(rest.mean()-0.3) < 0.3,
    f"{reg.mean():.1f} / {rest.mean():.1f}")
chk("C6: 30-deg cap fsky = 6.7%", abs(0.5*(1-np.cos(np.radians(30.0))) - 0.06699) < 1e-4)

# ---------------------------------------------------------------- D. fine scan
m05 = read_smooth('smica2_smooth0.5.fits')
ns05 = hp.get_nside(m05)
d05 = hp.query_disc(ns05, vec_gp, np.radians(15.0))
Td05 = m05[d05]*1e6
k = int(np.argmin(Td05))
lp5, bp5 = hp.pix2ang(ns05, d05[k], lonlat=True)
chk("D1: 0.5 deg peak (32.4,-5.5)", abs(lp5-32.4) < 0.5 and abs(bp5+5.5) < 0.5, f"({lp5:.2f},{bp5:.2f})")
chk("D2: 0.5 deg peak amp -215", abs(Td05[k] + 215.0) < 8.0, f"{Td05[k]:.1f}")
pkd = float(angdist_vec(GP_L, GP_B, np.array([lp5]), np.array([bp5]))[0])
chk("D3: 0.5 deg peak ~2.5 deg from gp10 centre", 2.2 < pkd < 2.9, f"{pkd:.2f}")
# nearest node to the 0.5 deg peak (doc: >9.7 deg)
d_pk = angdist_vec(lp5, bp5, nl, nb)
chk("D4: 0.5 deg peak nearest node > 9.7 deg", float(np.min(d_pk)) > 9.7, f"{np.min(d_pk):.2f}")

# ---------------------------------------------------------------- E. radial
rad_means = {}
for r0 in [0, 5, 10, 15, 20, 25, 30]:
    ring = hp.query_disc(nside417, vec_gp, np.radians(r0+5))
    inner = hp.query_disc(nside417, vec_gp, np.radians(r0)) if r0 > 0 else np.array([], dtype=int)
    shell = np.setdiff1d(ring, inner)
    rad_means[f'{r0}-{r0+5}'] = (float(m417[shell].mean()*1e6), float(m417[shell].std()*1e6), int(len(shell)))
exp = {'0-5': (24.7, 24.5, 95769), '5-10': (25.5, 36.4, 286556), '10-15': (25.4, 40.7, 475178),
       '15-20': (26.9, 39.7, 660185), '20-25': (20.6, 33.0, 840146), '25-30': (20.9, 30.3, 1013757),
       '30-35': (3.0, 35.8, 1179581)}
for key, (em, es, en) in exp.items():
    gm, gs, gn = rad_means[key]
    chk(f"E1: radial {key} mean {em}", abs(gm-em) < 0.5, f"{gm:.1f}")
    chk(f"E2: radial {key} n {en}", gn == en, f"{gn}")
chk("E3: all 7 rings positive (hot) mean", all(v[0] > 0 for v in rad_means.values()))

# ---------------------------------------------------------------- F. cross-map
def T_cross(l, b):
    out = {}
    for name, f in [('SMICA','smica2_smooth4.17.fits'), ('NILC','nilc2_smooth4.17.fits'),
                    ('Commander','commander_smooth4.17.fits')]:
        m = hp.read_map(os.path.join(CACHE, f), field=0)
        out[name] = m[hp.ang2pix(hp.get_nside(m), l, b, lonlat=True)]*1e6
    return out
c1 = T_cross(32.4, -5.5)
chk("F1: SMICA at peak -12.3", abs(c1['SMICA'] + 12.3) < 1.5, f"{c1['SMICA']:.1f}")
chk("F2: NILC at peak -9.0", abs(c1['NILC'] + 9.0) < 1.5, f"{c1['NILC']:.1f}")
chk("F3: Commander at peak -17.2", abs(c1['Commander'] + 17.2) < 1.5, f"{c1['Commander']:.1f}")
chk("F4: all three WEAK (-9..-17) vs -215 at 0.5 deg = amplitude collapse",
    all(abs(v) < 25 for v in c1.values()))
c0 = T_cross(32.0, -8.0)
chk("F5: gp10 centre all maps mildly positive", all(v > 0 for v in c0.values()),
    f"{c0['SMICA']:.1f}/{c0['NILC']:.1f}/{c0['Commander']:.1f}")

# ---------------------------------------------------------------- G. centroids
def cold_centroid(bcut, rmax=15.0):
    disc = hp.query_disc(nside417, vec_gp, np.radians(rmax))
    ld_, bd_ = hp.pix2ang(nside417, disc, lonlat=True)
    sel = disc[(m417[disc] < 0) & (np.abs(bd_) >= bcut)]
    v = hp.pix2vec(nside417, sel)
    vc = np.mean(v, axis=1); vc /= np.linalg.norm(vc)
    cl, cb = hp.vec2ang(vc, lonlat=True)
    cl = float(np.atleast_1d(cl)[0]); cb = float(np.atleast_1d(cb)[0])
    dd = angdist_vec(cl, cb, nl, nb)
    i0 = int(np.argmin(dd))
    return cl, cb, i0, float(dd[i0])
cl5, cb5, n5, d5n = cold_centroid(5)
chk("G1: bcut5 centroid (38.9,-11.9), nearest node21 17.9",
    abs(cl5-38.9) < 0.3 and abs(cb5+11.9) < 0.3 and n5 == 21 and abs(d5n-17.9) < 0.3,
    f"({cl5:.1f},{cb5:.1f}) node{n5} {d5n:.2f}")
cl10, cb10, n10, d10n = cold_centroid(10)
chk("G2: bcut10 centroid (38.4,-16.1), nearest node21 19.7",
    abs(cl10-38.4) < 0.3 and abs(cb10+16.1) < 0.3 and n10 == 21 and abs(d10n-19.7) < 0.3,
    f"({cl10:.1f},{cb10:.1f}) node{n10} {d10n:.2f}")
cl15, cb15, n15, d15n = cold_centroid(15)
chk("G3: bcut15 centroid (37.5,-18.9), nearest node22 18.1",
    abs(cl15-37.5) < 0.3 and abs(cb15+18.9) < 0.3 and n15 == 22 and abs(d15n-18.1) < 0.3,
    f"({cl15:.1f},{cb15:.1f}) node{n15} {d15n:.2f}")
d26_c10 = float(angdist_vec(cl10, cb10, np.array([nl[26]]), np.array([nb[26]]))[0])
chk("G4: node26 from bcut10 centroid ~23 (mask moves it further)",
    22.5 < d26_c10 < 23.5, f"{d26_c10:.1f}")
chk("G5: mask correction pushes centroid AWAY (nearest >= 17.9)", d5n >= 17.5 and d10n >= 17.5)

# ---------------------------------------------------------------- H. random control
node_vec = hp.ang2vec(np.radians(90-nb), np.radians(nl))
def nearest_dist_for(vecs):
    dots = np.clip(vecs @ node_vec.T, -1, 1)
    return np.degrees(np.arccos(dots)).min(axis=1)
# H1: same seeds -> exact reproduction of stored JSON
rng = np.random.default_rng(42)
z = rng.uniform(-1, 1, 20000); phi = rng.uniform(0, 2*np.pi, 20000)
b_r = 90 - np.degrees(np.arccos(z))
sel = np.abs(b_r) < 20
l_r = np.degrees(phi) % 360
l_r, b_r = l_r[sel][:10000], b_r[sel][:10000]
v1 = hp.ang2vec(np.radians(90-b_r), np.radians(l_r))
nd_plane = nearest_dist_for(v1)
z2 = rng.uniform(-1, 1, 10000); phi2 = rng.uniform(0, 2*np.pi, 10000)
v2 = np.stack([np.sin(np.arccos(z2))*np.cos(phi2), np.sin(np.arccos(z2))*np.sin(phi2), z2], axis=1)
nd_full = nearest_dist_for(v2)
chk("H1: same-seed plane P(<=10.05) = 0.477", abs((nd_plane <= 10.05).mean() - 0.477) < 0.005,
    f"{(nd_plane<=10.05).mean():.4f}")
chk("H2: same-seed plane P(<=5) = 0.117", abs((nd_plane <= 5).mean() - 0.117) < 0.005,
    f"{(nd_plane<=5).mean():.4f}")
chk("H3: same-seed full P(<=10.05) = 0.454", abs((nd_full <= 10.05).mean() - 0.454) < 0.005,
    f"{(nd_full<=10.05).mean():.4f}")
# H4: DIFFERENT seed consistency (MC error tolerance)
rng2 = np.random.default_rng(20260911)
z = rng2.uniform(-1, 1, 20000); phi = rng2.uniform(0, 2*np.pi, 20000)
b_r2 = 90 - np.degrees(np.arccos(z))
sel2 = np.abs(b_r2) < 20
l_r2, b_r2 = (np.degrees(phi) % 360)[sel2], b_r2[sel2]
v1b = hp.ang2vec(np.radians(90-b_r2), np.radians(l_r2))
nd_p2 = nearest_dist_for(v1b)
z2b = rng2.uniform(-1, 1, 10000); phi2b = rng2.uniform(0, 2*np.pi, 10000)
v2b = np.stack([np.sin(np.arccos(z2b))*np.cos(phi2b), np.sin(np.arccos(z2b))*np.sin(phi2b), z2b], axis=1)
nd_f2 = nearest_dist_for(v2b)
chk("H4: different-seed plane P(<=10.05) within 0.02 of 0.477",
    abs((nd_p2 <= 10.05).mean() - 0.477) < 0.02, f"{(nd_p2<=10.05).mean():.4f}")
chk("H5: different-seed full P(<=10.05) within 0.02 of 0.454",
    abs((nd_f2 <= 10.05).mean() - 0.454) < 0.02, f"{(nd_f2<=10.05).mean():.4f}")
chk("H6: 10.05 deg is NOT an empty void (P>=0.4 everywhere)", 
    (nd_plane <= 10.05).mean() >= 0.4 and (nd_full <= 10.05).mean() >= 0.4)

# ---------------------------------------------------------------- I. JSON self-consistency
with open(os.path.join(DATA, 'gp10_extract.json')) as f:
    ext = json.load(f)
chk("I1: extract 4.17/5.0/7.0 all-empty at 4 bcuts",
    all(len(ext[f'{x}°'][f'bcut{b}']) == 0 for x in ['4.17','5.0','7.0'] for b in [5,10,15,20]))
e3 = ext['3.0°']['bcut5']
chk("I2: extract 3.0 bcut5 = 2 comps", len(e3) == 2, f"{len(e3)}")
chk("I3: extract 3.0 strongest amp stored -83.2", abs(e3[0]['amp_muK'] + 83.2) < 0.1,
    f"{e3[0]['amp_muK']}")
with open(os.path.join(DATA, 'gp10_planck_style.json')) as f:
    ps = json.load(f)
sreg = ps['nside16_stats']['region']
chk("I4: JSON region stats match recompute",
    abs(sreg['mean']-22.8986) < 1e-3 and abs(sreg['var']-1081.48) < 0.1 and abs(sreg['skew']-0.12483) < 1e-3,
    f"{sreg['mean']:.3f}/{sreg['var']:.2f}/{sreg['skew']:.4f}")
chk("I5: JSON fine 0.5 deg stored (32.43,-5.51) -214.98",
    abs(ps['fine']['0.5°']['amp'] + 214.984) < 1e-3, f"{ps['fine']['0.5°']['amp']}")
chk("I6: JSON radial 0-5 stored 24.7378", abs(ps['radial']['0-5°']['mean'] - 24.7378) < 1e-3)
with open(os.path.join(DATA, 'random_control.json')) as f:
    rc = json.load(f)
chk("I7: JSON control plane median 10.316", abs(rc['plane']['median'] - 10.3161) < 1e-3,
    f"{rc['plane']['median']:.4f}")
chk("I8: JSON control near-gp10 P 0.447 / 0.0894",
    abs(rc['near_gp10']['p_le_1005'] - 0.447) < 1e-3 and abs(rc['near_gp10']['p_le_5'] - 0.0894) < 1e-3)

# ---------------------------------------------------------------- J. doc-claim coverage
def load_doc(p):
    with open(os.path.join(O28, p), encoding='utf-8') as f:
        return f.read()
nn = load_doc('NN_results.md')
rec = load_doc('01_problem_record.md')
ss = load_doc('SESSION_START.md')
doc_claims = {
    'NN_results.md': [
        '0 / 0 / 0 / 0', '(22.4,-25.0)', '+10.4', '0.75', '+0.12', '+22.9', '+0.3',
        '(32.4,-5.5)', '-215.0', '-12.3', '-9.0', '-17.2', '(38.4, -16.1)', '19.7',
        '18.1', '10.32', '0.477', '0.454', '0.447', '10.05', '+95.5', '20.25',
        '-48.3', '24.02', '-23.6', '20/20', '32/32', '2.5'],
    '01_problem_record.md': [
        '10.05', '20.25', '24.02', '+95.5', '-48.3', '-23.6', '0.477', '0.75',
        '+0.12', '+10.4', '20/20', '32/32', '(38.9, -11.9)', '19.7'],
    'SESSION_START.md': [
        '10.05', '20.25', '24.02', '+95.5', '-48.3', '-23.6', '0.477', '20/20', '32/32'],
}
for docname, tokens in doc_claims.items():
    txt = {'NN_results.md': nn, '01_problem_record.md': rec, 'SESSION_START.md': ss}[docname]
    missing = [t for t in tokens if t not in txt]
    chk(f"J1: {docname} covers all claim tokens", len(missing) == 0, f"missing {missing}")

# ---------------------------------------------------------------- K. timeline-aware cross-doc
# Registration-time (2026-08-17) problem statement quotes O5 values (10.1 deg, +93.3 uK)
# which differ from the frame-corrected closure values (10.05, +95.5) in the table.
# Both are legitimate history: early doc paragraph = O5 framing; closure table = O28 values.
chk("K1: problem statement holds O5-era values (10.1/+93.3) ONLY in the 問題陳述 paragraph",
    rec.count('10.1') == 1 and rec.count('93.3') == 1,
    f"10.1 x{rec.count('10.1')}, 93.3 x{rec.count('93.3')}")
chk("K2: final values (10.05/+95.5) present in record tables",
    rec.count('10.05') >= 2 and rec.count('95.5') >= 2)
chk("K3: NN_results holds ONLY final values (no 93.3 leakage)", '93.3' not in nn and '10.1°' not in nn)
chk("K4: SESSION_START O5-era framing marked + closure values present",
    'O5-era framing' in ss and '10.05°' in ss and '+95.5' in ss)
chk("K5: verdict consistent across 3 docs (no node correspondence)",
    '冇節點對應' in nn and '冇節點對應' in rec and '冇節點對應' in ss)

# ---------------------------------------------------------------- summary
print("=" * 70)
print("O28 INDEPENDENT AUDIT (2026-09-11) - raw-map recompute, no script imports")
print("=" * 70)
npass = sum(1 for _, c, _ in checks if c)
for name, c, detail in checks:
    print(f"  {'PASS' if c else 'FAIL'}  {name}" + (f"  [{detail}]" if detail else ""))
print(f"\n{npass}/{len(checks)} PASS")
sys.exit(0 if npass == len(checks) else 1)
