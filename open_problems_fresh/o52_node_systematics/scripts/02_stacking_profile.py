#!/usr/bin/env python3
"""
O52 Step 2 (v2): Stacking radial profile — 60 nodes vs random positions
=======================================================================
Fast bincount implementation. For a batch of directions, compute per-annulus
mean temperature in ONE pass:

  For nside=256 map (196k pixels), precompute for each pixel:
    - its unit vector
  For each direction, angular distance to all pixels is 196k dots.
  Batch: stack directions into a (B, 3) array → dots = dirs @ pixvecs.T
  is (B, 196k) — for B=60 that's 12M floats = 96 MB, fine.

  Annulus membership via cos thresholds → boolean masks → bincount sum.
  Mean per (direction, annulus) via bincount over pixel values.

  Total: 2000 random draws × 60 dirs = 120k directions, each 196k dots
  → 23.5 GFLOP → numpy matmul ~ minutes. To cut further, evaluate random
  stacks in batches of 500 dirs (same matmul efficiency).
"""
import numpy as np
import healpy as hp
import json, os, time
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
CACHE = os.path.join(BASE, 'open_problems_fresh/o5_catalog_compare/data/smooth_cache')
NODES_FILE = os.path.join(BASE, 'main_problems/p4_cmb_cold_spot/data/a5_nodes.txt')
MASK_R3 = os.path.join(BASE, 'open_problems_fresh/o27_node47_foreground/data/COM_Mask_CMB-common-Mask-Int_2048_R3.00.fits')
OUTDIR = os.path.join(BASE, 'open_problems_fresh/o52_node_systematics')
os.makedirs(os.path.join(OUTDIR, 'data'), exist_ok=True)

nodes = np.loadtxt(NODES_FILE)
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic
node_l, node_b = gal.l.deg, gal.b.deg
node_vecs = hp.ang2vec(node_l, node_b, lonlat=True)

mask_r3 = hp.read_map(MASK_R3, field=0)
nside_m = hp.get_nside(mask_r3)
unmasked = mask_r3[hp.ang2pix(nside_m, node_l, node_b, lonlat=True)] > 0.5
print(f"R3 mask: {unmasked.sum()}/60 unmasked")

FWHM = 3.0
m = hp.read_map(os.path.join(CACHE, f'smica2_smooth{FWHM}.fits'), field=0) * 1e6
nside_low = 128   # 27' pixels — far smaller than 2° annuli; fast (49k px)
m_low = hp.ud_grade(m, nside_low, order_in='RING', order_out='RING')
pix_vecs = np.stack(hp.pix2vec(nside_low, np.arange(hp.nside2npix(nside_low))), axis=1)

ANNULI = [(0, 2), (2, 4), (4, 6), (6, 8), (8, 10), (10, 12), (12, 14)]
cos_edges = [(np.cos(np.radians(r1)), np.cos(np.radians(r0)) if r0 > 0 else 1.0)
             for (r0, r1) in ANNULI]

def annulus_means(dirs, m, pix_vecs, cos_edges):
    """dirs: (N,3). Returns (N, len(annuli)) mean T per annulus (bincount)."""
    N = len(dirs)
    dots = np.clip(dirs @ pix_vecs.T, -1, 1)          # (N, npix)
    out = np.full((N, len(cos_edges)), np.nan)
    for a, (cos_r1, cos_r0) in enumerate(cos_edges):
        sel = (dots >= cos_r1) & (dots < cos_r0)       # (N, npix)
        cnt = sel.sum(axis=1)
        ok = cnt > 0
        # sum over selected pixels via einsum
        sums = np.einsum('ij,ij->i', sel, np.broadcast_to(m, (N, len(m))))
        out[ok, a] = sums[ok] / cnt[ok]
    return out

t0 = time.time()
print(f"\n=== 堆疊 radial profile @ {FWHM}° (nside={nside_low}) ===")
print(f"{'annulus':<12} {'obs(60)':>9} {'obs(um45)':>10} {'rand_mean':>10} {'rand_std':>9} {'z(60)':>7} {'z(um)':>7}")

obs_all = annulus_means(node_vecs, m_low, pix_vecs, cos_edges).mean(axis=0)
obs_um = annulus_means(node_vecs[unmasked], m_low, pix_vecs, cos_edges).mean(axis=0)

rng = np.random.default_rng(20260822)
N_RAND = 1000   # 1000 random stacks: std error ±0.03σ on z — plenty
rand_prof = np.zeros((N_RAND, len(ANNULI)))
BATCH = 50      # 50 stacks × 60 dirs per matmul batch
for b0 in range(0, N_RAND, BATCH):
    b1 = min(b0 + BATCH, N_RAND)
    n = b1 - b0
    zz = rng.uniform(-1, 1, n * 60)
    pp = rng.uniform(0, 2*np.pi, n * 60)
    rv = np.stack([np.sqrt(1-zz**2)*np.cos(pp), np.sqrt(1-zz**2)*np.sin(pp), zz], axis=1)
    rv = rv.reshape(n, 60, 3)
    prof = np.array([annulus_means(d, m_low, pix_vecs, cos_edges).mean(axis=0) for d in rv])
    rand_prof[b0:b1] = prof
    print(f"  random stacks {b1}/{N_RAND} done ({time.time()-t0:.0f}s)", flush=True)

out = {}
for i, (r0, r1) in enumerate(ANNULI):
    z_all = (obs_all[i] - rand_prof[:, i].mean()) / rand_prof[:, i].std()
    z_um = (obs_um[i] - rand_prof[:, i].mean()) / rand_prof[:, i].std()
    out[f'{r0}-{r1}'] = dict(
        obs_all=round(float(obs_all[i]), 3),
        obs_unmasked=round(float(obs_um[i]), 3),
        rand_mean=round(float(rand_prof[:, i].mean()), 3),
        rand_std=round(float(rand_prof[:, i].std()), 3),
        z_all=round(float(z_all), 2),
        z_unmasked=round(float(z_um), 2))
    print(f"  {r0:>2}-{r1:<2}°     {obs_all[i]:8.2f}  {obs_um[i]:9.2f}  "
          f"{rand_prof[:, i].mean():9.2f}  {rand_prof[:, i].std():8.2f}  {z_all:+6.2f}  {z_um:+6.2f}")

z_in = (obs_all[0] - rand_prof[:, 0].mean()) / rand_prof[:, 0].std()
p_in = float(np.mean(rand_prof[:, 0] <= obs_all[0]))
print(f"\n最內圈 (0-2°): z={z_in:+.2f}, p(≤)={p_in:.4f} "
      f"({'🟢' if abs(z_in) > 3 else ('🟡' if abs(z_in) > 2 else '🔴')})")

with open(os.path.join(OUTDIR, 'data/o52_stacking.json'), 'w') as f:
    json.dump(dict(fwhm=FWHM, annuli=[list(a) for a in ANNULI],
                   profile=out, inner_z=round(float(z_in), 2),
                   inner_p=p_in, n_random=N_RAND), f, indent=2)
print(f"\nSaved: data/o52_stacking.json ({time.time()-t0:.0f}s)")
