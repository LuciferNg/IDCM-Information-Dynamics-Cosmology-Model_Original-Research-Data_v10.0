#!/usr/bin/env python3
"""
O52 independent re-derivation — fresh sample from SMICA smooth maps
===================================================================
Purpose: verify O52 claims by RE-SAMPLING the smooth FITS maps directly
(fresh code path, not re-reading saved JSONs).

Re-derives:
  1. Frame-corrected node temperatures at 3.0° (Galactic lonlat)
  2. 60-node mean vs sky (|b|>25°) — z
  3. High-lat 31 subset z
  4. R3 mask 45/60 (Galactic lonlat sampling)
  5. Removing node0/9 residual mean
  6. Cold/hot counts
  7. Stacking inner annulus (0-2°) vs 500 random stacks (fresh seed)
"""
import numpy as np
import healpy as hp
import json, os
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
CACHE = f'{BASE}/open_problems_fresh/o5_catalog_compare/data/smooth_cache'
NODES_FILE = f'{BASE}/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt'
MASK_R3 = f'{BASE}/open_problems_fresh/o27_node47_foreground/data/COM_Mask_CMB-common-Mask-Int_2048_R3.00.fits'

nodes = np.loadtxt(NODES_FILE)
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic
node_l, node_b = gal.l.deg, gal.b.deg
theta_g = np.radians(90.0 - node_b)
phi_g = np.radians(node_l)
high_lat = np.abs(node_b) >= 30.0

mask_r3 = hp.read_map(MASK_R3, field=0)
nside_m = hp.get_nside(mask_r3)
unmasked = mask_r3[hp.ang2pix(nside_m, node_l, node_b, lonlat=True)] > 0.5

print("=" * 70)
print("O52 INDEPENDENT RE-DERIVATION (fresh fits sampling)")
print("=" * 70)
print(f"R3 mask: {unmasked.sum()}/60 unmasked  (record: 45)")
assert unmasked.sum() == 45

fwhm = 3.0
m = hp.read_map(f'{CACHE}/smica2_smooth{fwhm}.fits', field=0) * 1e6
nside = hp.get_nside(m)
pix = hp.ang2pix(nside, theta_g, phi_g)
node_T = m[pix]

npix = hp.nside2npix(nside)
l_arr, b_arr = hp.pix2ang(nside, np.arange(npix), lonlat=True)
sky_mask = np.abs(b_arr) >= 25.0
sky_mean = np.mean(m[sky_mask])
sky_sigma = np.std(m[sky_mask])

node_mean = np.mean(node_T)
z_all = (node_mean - sky_mean) / (np.std(node_T)/np.sqrt(60))
hl_mean = np.mean(node_T[high_lat])
z_hl = (hl_mean - sky_mean) / (np.std(node_T[high_lat])/np.sqrt(31))
um_mean = np.mean(node_T[unmasked])
z_um = (um_mean - sky_mean) / (np.std(node_T[unmasked])/np.sqrt(45))

keep = np.ones(60, bool)
keep[0] = keep[9] = False
rem_mean = np.mean(node_T[keep])
z_rem = (rem_mean - sky_mean) / (np.std(node_T[keep])/np.sqrt(58))

n_cold = int(np.sum(node_T < sky_mean))
n_hot = int(np.sum(node_T > sky_mean))
n_cold2 = int(np.sum(node_T < sky_mean - 2*sky_sigma))
n_hot2 = int(np.sum(node_T > sky_mean + 2*sky_sigma))

print(f"\n3.0° node mean = {node_mean:.3f} vs sky {sky_mean:.3f} → z={z_all:+.2f}  (record: -1.522, -0.27)")
print(f"high-lat 31 mean = {hl_mean:.3f} → z={z_hl:+.2f}  (record: -4.25, -0.51)")
print(f"unmasked 45 mean = {um_mean:.3f} → z={z_um:+.2f}  (record: -2.62, -0.39)")
print(f"remove 0,9: mean = {rem_mean:.3f} → z={z_rem:+.2f}  (record: +2.83, +0.46)")
print(f"cold/hot = {n_cold}/{n_hot}  2σ = {n_cold2}/{n_hot2}  (record: 29/31, 4/2)")

# Stacking inner annulus (0-2°) — vectorized
print("\n" + "=" * 70)
print("STACKING INNER ANNULUS (0-2°) vs 500 random stacks (seed=888)")
print("=" * 70)
nside_low = 128
m_low = hp.ud_grade(m, nside_low, order_in='RING', order_out='RING')
pix_vecs = np.stack(hp.pix2vec(nside_low, np.arange(hp.nside2npix(nside_low))), axis=1)

def inner_annulus_mean(dirs, m, pix_vecs, r0=0.0, r1=2.0):
    dots = np.clip(dirs @ pix_vecs.T, -1, 1)
    cos_r1 = np.cos(np.radians(r1))
    cos_r0 = np.cos(np.radians(r0)) if r0 > 0 else 1.0
    sel = (dots >= cos_r1) & (dots < cos_r0)
    cnt = sel.sum(axis=1)
    ok = cnt > 0
    sums = np.einsum('ij,ij->i', sel, np.broadcast_to(m, (len(dirs), len(m))))
    out = np.full(len(dirs), np.nan)
    out[ok] = sums[ok] / cnt[ok]
    return out

node_vecs = hp.ang2vec(node_l, node_b, lonlat=True)
obs_inner = inner_annulus_mean(node_vecs, m_low, pix_vecs).mean()
rng = np.random.default_rng(888)
rand_inner = np.zeros(500)
for k in range(500):
    zz = rng.uniform(-1, 1, 60)
    pp = rng.uniform(0, 2*np.pi, 60)
    rv = np.stack([np.sqrt(1-zz**2)*np.cos(pp), np.sqrt(1-zz**2)*np.sin(pp), zz], axis=1)
    rand_inner[k] = inner_annulus_mean(rv, m_low, pix_vecs).mean()
z_in = (obs_inner - rand_inner.mean()) / rand_inner.std()
p_in = float(np.mean(rand_inner <= obs_inner))
print(f"obs inner 0-2° = {obs_inner:.3f} vs random {rand_inner.mean():.3f}±{rand_inner.std():.3f} → z={z_in:+.2f}, p={p_in:.3f}")
print(f"  (record: -1.29, rand -0.05±5.90, z=-0.21, p=0.411)")

print("\n✅ O52 independent re-derivation complete")
