#!/usr/bin/env python3
"""
路線 1 預註冊 — CMB 偏振宇稱違反: 32 阻挫邊 edge-band 天區 mask (2026-10-17)
============================================================================
預言 (p12 data/polarization_parity.json): 偏振旋轉 ~1e-5 rad, 局限喺阻挫邊附近。
  falsifiable: edge bands 冇偏振異常 ⟹ 證偽。

本 script 將 32 條阻挫邊 (frustration_edges.txt, 端點 RA/Dec 已知) 轉為
HEALPix edge-band mask (+ control mask) — 純幾何、零新常數、凍結規格:
  - r_band = 2.0° (對應 DESI 節點核心真空最佳 ~2.5° 尺度, 凍結)
  - control: 離所有邊 > 5° 且離所有節點 > 5° (遠場, area-matched)
  - Nside = 128 (像素 ~0.46°)
輸出: data/edge_band_mask_20261017.json + .npz — CMB-S4/SO 數據到埗即直接套用。
"""
import os, json
import numpy as np
import healpy as hp

HERE = os.path.dirname(os.path.abspath(__file__))
CS   = os.path.dirname(HERE)
SIB  = os.path.dirname(CS)
DATA = os.path.join(CS, 'data')
P4   = os.path.join(SIB, 'p4_cmb_cold_spot', 'data')
NODES_FILE = os.path.join(P4, 'a5_nodes.txt')
EDGES_FILE = os.path.join(P4, 'frustration_edges.txt')

NSIDE = 128
R_BAND_DEG = 2.0
R_CONTROL_DEG = 5.0

nodes = np.loadtxt(NODES_FILE)                       # 60 x [RA, DEC]
ra_n, dec_n = np.radians(nodes[:,0]), np.radians(nodes[:,1])

rows = []
for line in open(EDGES_FILE):
    line = line.strip()
    if line.startswith('#') or not line: continue
    p = line.split()
    rows.append((int(p[0]), int(p[1]), float(p[4]), float(p[5]), float(p[6]), float(p[7])))
edges = np.array([(u, v, rau, decu, rav, decv) for u, v, rau, decu, rav, decv in rows])
print(f"節點 {len(nodes)}; 阻挫邊 {len(edges)}")

# ---------- 球面幾何 ----------
def unit(ra, dec):
    return np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])

def ang_sep(ra1, dec1, ra2, dec2):
    c = np.clip(np.cos(dec1)*np.cos(dec2)*np.cos(ra1-ra2) + np.sin(dec1)*np.sin(dec2), -1, 1)
    return np.arccos(c)

def dist_to_segment(ra0, dec0, ra1, dec1, ra2, dec2):
    """點到球面大圓線段嘅最短角距 (sliding 法向量平面投影, 保守實現)."""
    ra0, dec0 = np.atleast_1d(ra0), np.atleast_1d(dec0)
    # 線段端點 (scalar 輸入 → ravel 確保 (3,))
    A = unit(ra1, dec1).ravel(); B = unit(ra2, dec2).ravel()
    n_AB = np.cross(A, B); n_AB /= np.linalg.norm(n_AB)          # 線段所在大圓法向量
    p = unit(ra0, dec0)
    # p 到 AB 大圓嘅最短距離 = |arcsin(p·n_AB)|, 但需檢查係咪喺線段範圍
    d_great = np.abs(np.arcsin(np.clip(p @ n_AB, -1, 1)))
    # 端點檢查: 若投影位置喺段外, 距離 = 到最近端點
    # 用三點共面判據: p 喺段範圍 ⟺ A·p ≥ A·B 且 B·p ≥ A·B (對單位向量, 沿大圓有序)
    AB = A @ B
    d = np.where((A @ p.T >= AB) & (B @ p.T >= AB), d_great,
                 np.minimum(np.arccos(np.clip(A @ p.T, -1, 1)), np.arccos(np.clip(B @ p.T, -1, 1))))
    return d

# ---------- HEALPix 像素 ----------
npix = hp.nside2npix(NSIDE)
pix_ra, pix_dec = hp.pix2ang(NSIDE, np.arange(npix), lonlat=True)
pix_ra_r, pix_dec_r = np.radians(pix_ra), np.radians(pix_dec)

# 全天空到每條邊嘅最短距離: 32 x npix — 記憶體 32*196608 = 6.3M float = 50MB, 可行
d_edge = np.full((len(edges), npix), np.inf)
for i, (_, _, rau, decu, rav, decv) in enumerate(edges):
    d_edge[i] = dist_to_segment(pix_ra_r, pix_dec_r, np.radians(rau), np.radians(decu),
                                 np.radians(rav), np.radians(decv))
d_edge_min = d_edge.min(axis=0)                          # 每像素到最近邊距離
d_node_min = np.full(npix, np.inf)
for j in range(len(nodes)):
    d_node_min = np.minimum(d_node_min, ang_sep(pix_ra_r, pix_dec_r, ra_n[j], dec_n[j]))

band = np.degrees(d_edge_min) < R_BAND_DEG
control = (np.degrees(d_edge_min) > R_CONTROL_DEG) & (np.degrees(d_node_min) > R_CONTROL_DEG)
# area-match control: 隨機抽同 band 面積
n_band = int(band.sum()); n_control = int(control.sum())
rng = np.random.default_rng(20261017)
ctrl_idx = np.where(control)[0]
ctrl_sample = ctrl_idx[rng.choice(len(ctrl_idx), size=n_band, replace=False)]
ctrl_mask = np.zeros(npix, bool); ctrl_mask[ctrl_sample] = True

edge_len = np.degrees(ang_sep(np.radians(edges[:,2]), np.radians(edges[:,3]),
                              np.radians(edges[:,4]), np.radians(edges[:,5])))
print(f"\nedge-band mask: Nside={NSIDE}, r_band={R_BAND_DEG}°")
print(f"  band pixels = {n_band} ({100*n_band/npix:.2f}% 天空, {n_band*4*np.pi/npix:.1f} deg²)")
print(f"  control(area-matched) = {ctrl_mask.sum()} pixels")
print(f"  邊長統計: min {edge_len.min():.2f}° median {np.median(edge_len):.2f}° max {edge_len.max():.2f}°")
print(f"  每條邊獨立 band 面積: ~{n_band*4*np.pi/npix/32* (180/np.pi)**2:.1f} deg²")

out = {
    "route1_edge_band_prereg_20261017": {
        "prediction": "CB→EB 偏振旋轉 ~1e-5 rad 局限喺 32 阻挫邊 ±2.0° 帶 (frozen)",
        "falsifier": "edge bands 冇偏振異常 (旋轉統計 = control) ⟹ 證偽",
        "nside": NSIDE, "r_band_deg": R_BAND_DEG, "r_control_deg": R_CONTROL_DEG,
        "n_edges": len(edges), "n_band_pix": n_band, "band_frac_sky": round(float(n_band/npix),5),
        "n_control_pix": int(ctrl_mask.sum()), "seed": 20261017,
        "edge_lengths_deg_min": round(float(edge_len.min()),2),
        "edge_lengths_deg_median": round(float(np.median(edge_len)),2),
        "edge_lengths_deg_max": round(float(edge_len.max()),2),
        "edge_endpoints_radec": [[int(u),int(v),round(rau,4),round(decu,4),round(rav,4),round(decv,4)]
                                 for u,v,rau,decu,rav,decv in edges],
        "sensitivity_note": "CMB-S4 0.01°≈1.7e-4 rad; 預言 1e-5 rad 需 32 邊 stacking (p12 json)"
    }
}
json.dump(out, open(os.path.join(DATA, 'edge_band_mask_20261017.json'), 'w'))
np.savez_compressed(os.path.join(DATA, 'edge_band_mask_20261017.npz'),
                    band=band, ctrl_mask=ctrl_mask, d_edge_min=d_edge_min.astype(np.float32))
print(f"\n已存 edge_band_mask_20261017.json + .npz")