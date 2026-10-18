#!/usr/bin/env python3
"""
P12 攻堅 — 路線 2 精化: CluMPR 3.0° Gaussian p 估計 + 更密 inner grid (2026-10-18)
=================================================================================
背景: P5 script 17 (2026-10-17) Phase B 3.0° p_raw=0 → clamp 1/(N_MC+1)=2e-4 做 Fisher5。
      交接建議: 3.0° p 改 Gaussian 估計 + 更密 inner grid (0.25° step 1.0-3.5)。
方法: 同 P5 script 17 (scramble RA keep dec null, seed 42) — 唔改方法, 只加:
  (a) inner grid 加密到 0.25° step;
  (b) Gaussian p = norm.sf(z) (z = (MC_mean − obs)/MC_sd) — MC 分佈 Gaussianity 檢驗先行;
  (c) Fisher5 三版 p → z5 敏感度 (clamp / p_raw / p_Gauss).
來源: CluMPR 2024 / DESI-Legacy DR9 (Yantovski-Barth+2023, Zenodo 8157751/10727242)
⚠️ 標籤: 數據係 DESI-Legacy 光度星系團 (非 DESI DR2 光譜), 部分天區; scramble-RA 先啱 null。
"""
import os, json, time
import numpy as np
from scipy.stats import chi2 as _chi2, norm as _norm

HERE = os.path.dirname(os.path.abspath(__file__))
P12  = os.path.dirname(HERE)
MAIN = os.path.dirname(P12)
FITS = os.path.join(MAIN, 'p5_crystal_stress', 'data', '_desi_clusters_2024_simple.fits')
NODES = os.path.join(MAIN, 'p4_cmb_cold_spot', 'data', 'a5_nodes.txt')
RV   = os.path.join(MAIN, 'p5_crystal_stress', 'data', 'reverify_cluster_vacuum.json')

assert os.path.exists(FITS), FITS
assert os.path.exists(NODES), NODES
from astropy.io import fits
t0 = time.time()
t = fits.open(FITS)[1].data
ra = np.asarray(t['RA_central'], dtype=float); dec = np.asarray(t['DEC_central'], dtype=float)
m = np.isfinite(ra) & np.isfinite(dec); ra, dec = ra[m], dec[m]
print(f"CluMPR 2024: {len(ra)} 團 (load {time.time()-t0:.1f}s)")

nodes = np.loadtxt(NODES)
a_ = np.radians(nodes[:, 0]).astype(np.float32); d_ = np.radians(nodes[:, 1]).astype(np.float32)
nv = np.empty((len(nodes), 3), np.float32)
nv[:, 0] = np.cos(d_)*np.cos(a_); nv[:, 1] = np.cos(d_)*np.sin(a_); nv[:, 2] = np.sin(d_)

def scan32(ras, decs):
    a = np.radians(ras).astype(np.float32); d = np.radians(decs).astype(np.float32)
    cd = np.cos(d)
    u = np.empty((len(ras), 3), np.float32)
    u[:, 0] = cd*np.cos(a); u[:, 1] = cd*np.sin(a); u[:, 2] = np.sin(d)
    c = np.clip(u @ nv.T, -1, 1).max(axis=1)
    return np.degrees(np.arccos(c.astype(np.float64)))

rng = np.random.default_rng(42)
obs_d = scan32(ra, dec)

# radius grid: inner 0.25° step + outer 對照 (Phase A/B/C 已做 3.0-8.5, 所以只須 4.0/4.5/5.0 對照)
radii = np.concatenate([np.arange(1.0, 3.75, 0.25), [4.0, 4.5, 5.0]])
N_MC = 6000
print(f"\n掃描 radii {len(radii)} 點, N_MC={N_MC}, null=scramble RA keep dec, seed=42")
mcs = {float(r): np.empty(N_MC, dtype=int) for r in radii}
t0 = time.time()
for i in range(N_MC):
    ras = rng.uniform(0, 360, len(ra)); ds = scan32(ras, dec)
    for r in radii:
        mcs[float(r)][i] = int((ds < r).sum())
print(f"MC done {time.time()-t0:.1f}s")

def gauss_tail_check(a):
    """MC 分佈與同 mean/std Gaussian 嘅尾部對照 (KS + z=2/3/4 經驗尾 vs norm.sf)."""
    from scipy.stats import kstest, norm as _n
    mn, sd = float(a.mean()), float(a.std())
    ks = kstest((a - mn)/sd, 'norm')
    # 經驗尾: z 由 MC 內部 Z-score 嚟 (避免睇落尾唔到)
    zs = np.sort((a - mn)/sd)[::-1]
    emp = {2: (zs >= 2).mean(), 3: (zs >= 3).mean(), 4: (zs >= 4).mean()}
    th  = {2: _n.sf(2), 3: _n.sf(3), 4: _n.sf(4)}
    return {"ks_stat": round(ks.statistic, 4), "ks_p": round(ks.pvalue, 4), "emp": emp, "th": th}

rows = {}
for r in radii:
    o = int((obs_d < float(r)).sum()); a = mcs[float(r)]
    sd = float(a.std()); mn = float(a.mean())
    z = (mn - o)/sd if sd else 0.0
    p_raw = float((a <= o).mean())                    # MC 直接 (下限 1/(N_MC+1))
    p_cl = max(p_raw, 1/(N_MC+1))
    p_g  = float(_norm.sf(z))                          # Gaussian 尾 (視乎 Gaussianity)
    rows[float(r)] = {"obs": o, "mc_mean": round(mn,1), "mc_sd": round(sd,1),
                      "z_deficit": round(z,3), "p_raw": p_raw, "p_clamped": p_cl,
                      "p_gauss": p_g, "gauss_check": gauss_tail_check(a)}
    print(f"  r={r:>4.2f}° obs={o:>7} MC={mn:>9.1f}±{sd:<6.1f} z={z:>6.2f} p_raw={p_raw:.4g} p_gauss={p_g:.3g} ks_p={gauss_tail_check(a)['ks_p']:.3g}")

# 重點: 3.0° (交接指定) 同最佳 inner z 嘅 Gaussianity 明細
for target in (2.0, 3.0):
    q = rows[float(target)]
    print(f"\n-- r={target}° Gaussianity: KS p={q['gauss_check']['ks_p']:.4g}; "
          f"emp tail {q['gauss_check']['emp']} vs Gaussian {q['gauss_check']['th']}")

# Fisher5 敏感度: 4 cat p (script 12 輸出) + DESI p 三版 (取 z 最大嘅 inner radius 用 3.0° 做基準)
rv = json.load(open(RV))
def best_of(cat):
    return min(v['p_deficit'] for v in rv[cat].values())
p_abell, p_psz1, p_psz2, p_mcxc = best_of('Abell'), best_of('PSZ1'), best_of('PSZ2'), best_of('MCXC')
def fisher5(p_desi, tag):
    p_used = [p_psz1, p_psz2, p_mcxc, p_abell, p_desi]
    c5 = -2*sum(float(np.log(p)) for p in p_used)
    pf5 = float(_chi2.sf(c5, 10)); z5 = float(_norm.isf(pf5))
    print(f"  Fisher5 [{tag:>10}]: p_DESI={p_desi:.3g} -> p={pf5:.3g} z={z5:.3f}σ")
    return {"tag": tag, "p_used": [round(p,6) for p in p_used], "chi2": round(c5,3), "p_fisher": pf5, "z_fisher": z5}

fisher_out = [
    fisher5(2.0e-4, "clamp_2e-4"),
    fisher5(rows[3.0]['p_raw'], "p_raw@3.0"),
    fisher5(rows[3.0]['p_gauss'], "p_gauss@3.0"),
]

out = {
    "p12_inner_grid_gaussian_20261018": {
        "catalog": "CluMPR 2024 / DESI-Legacy DR9 (Yantovski-Barth+2023)",
        "N": len(ra), "N_MC": N_MC, "seed": 42, "null": "scramble RA keep dec",
        "radii": [float(r) for r in radii], "rows": rows, "fisher5": fisher_out,
        "note": "p_gauss = norm.sf(z) 需 Gaussianity 檢驗支持; p_raw 下限 1/(N_MC+1)=%.2e" % (1/(N_MC+1)),
    },
}
dst = os.path.join(P12, 'data', 'reverify_desi_inner_grid.json')
json.dump(out, open(dst, 'w'), indent=2)
print(f"\n已存 {dst}")