#!/usr/bin/env python3
"""
執行 — 路線 2: DESI 星系團第 5 重節點核心真空測試 (2026-10-17, v2)
================================================================
背景: DESI DR2 (光譜) 無官方星系團 VAC → 用 CluMPR 2024 / DESI Legacy DR9
      光度星系團目錄 (Yantovski-Barth+2023, Zenodo, 298,487 團) 作第 5 重。
      ⚠️ 標籤更正: 數據係 DESI-Legacy Imaging (非 DESI DR2 光譜), 部分天區。
Method: 同 script 12 (節點核心真空): 每團最近 A₅ 節點角距 → 各半徑命中計數。
  null (主): MC scramble RA, keep dec — 預註冊保守 null, 啱部分天區 (footprint-safe)。
  null (參): 全天均勻 — 僅參考 (部分天區 footprint 效應, 見 log)。← 第一次跑已演示
v2: + per-radius z_deficit (用 MC std); + 聚焦高解析度確定 (r=2.5,3.0,3.5, N_MC=5000);
    + p clamp 1/(N_MC+1) (N_MC 解像度下限) 令 Fisher 可行。
"""
import os, json, math
import numpy as np
from scipy.stats import chi2 as _chi2, norm as _norm

HERE = os.path.dirname(os.path.abspath(__file__))
CS   = os.path.dirname(HERE)
SIB  = os.path.dirname(CS)
DATA = os.path.join(CS, 'data')
NODES = os.path.join(SIB, 'p4_cmb_cold_spot', 'data', 'a5_nodes.txt')
FITS = os.path.join(DATA, "_desi_clusters_2024_simple.fits")

assert os.path.exists(FITS), f"DESI fits 未下載: {FITS}"
from astropy.io import fits
t = fits.open(FITS)[1].data
cols = t.columns.names
ra = np.asarray(t['RA_central'], dtype=float); dec = np.asarray(t['DEC_central'], dtype=float)
m = np.isfinite(ra) & np.isfinite(dec); ra, dec = ra[m], dec[m]
print(f"DESI-LS CluMPR 2024: {len(ra)} 團; z_median 範圍 [{np.nanmin(t['z_median_central']):.3f},{np.nanmax(t['z_median_central']):.3f}] 中位 {np.median(t['z_median_central']):.3f}")

nodes = np.loadtxt(NODES)
def unit(a_deg, d_deg):
    a, d = np.radians(a_deg), np.radians(d_deg)
    return np.column_stack([np.cos(d)*np.cos(a), np.cos(d)*np.sin(a), np.sin(d)])
node_vec = unit(nodes[:,0], nodes[:,1])

radii_full = np.arange(3.0, 9.0, 0.5)
def scan(ras, decs):
    u = unit(ras, decs)
    c = np.clip(u @ node_vec.T, -1, 1).max(axis=1)
    return np.degrees(np.arccos(c))

rng = np.random.default_rng(42)
obs_d = scan(ra, dec)

# ---------- Phase A: 全半徑, N_MC=1000, 雙 null ----------
def mc_loop(n_iter, decs, keep_dec=True):
    out = {}
    for i in range(n_iter):
        if keep_dec:
            ras = rng.uniform(0, 360, len(decs)); ds = scan(ras, decs)
        else:
            ras = rng.uniform(0, 360, len(decs))
            dec2 = np.degrees(np.arcsin(rng.uniform(-1, 1, len(decs))))
            ds = scan(ras, dec2)
        for r in radii_full:
            out.setdefault(float(r), np.empty(n_iter, dtype=int))
            out[float(r)][i] = int((ds < r).sum())
    return out

def stats(obs, mcs, n_iter):
    rows = {}
    for r in radii_full:
        o = obs[float(r)]; a = mcs[float(r)]
        sd = float(a.std()); mn = float(a.mean())
        z = (mn - o)/sd if sd else 0.0
        rows[float(r)] = {"obs": o, "mc_mean": round(mn,1), "mc_sd": round(sd,1),
                          "z_deficit": round(z,3), "p": float((a <= o).mean())}
    return rows

N_A = 1000
print(f"\nPhase A: 全半徑 {len(radii_full)} 點, N_MC={N_A}, dual null...")
obs = {float(r): int((obs_d < r).sum()) for r in radii_full}
mcA = mc_loop(N_A, dec, True)
mcU = mc_loop(N_A, dec, False)
sA = stats(obs, mcA, N_A); sU = stats(obs, mcU, N_A)
print("  半徑°   obs     MC(mean±sd)     z-def    p(scramble)")
for r in radii_full:
    q = sA[float(r)]
    print(f"  {r:>5.1f} {q['obs']:>7} {q['mc_mean']:>10.1f}±{q['mc_sd']:<6.1f} {q['z_deficit']:>8.2f} {q['p']:>8.4f}")
print("  [參照 全天均勻 p] " + " ".join(f"{r}°={sU[float(r)]['p']:.3f}" for r in radii_full))
print("  ⚠ 全天均勻 null 喺部分天區目錄 = footprint artifact (obs<<null 全部半徑) — 只作參考")

# ---------- Phase B: 聚焦高解析度 (2.5-3.5°, N_MC=5000, scramble) ----------
radii_focus = np.array([2.5, 3.0, 3.5])
N_B = 5000
print(f"\nPhase B: 聚焦 {radii_focus.tolist()}°, N_MC={N_B}, scramble RA keep dec...")
obs_f = {float(r): int((obs_d < r).sum()) for r in radii_focus}
mcB = {float(r): np.empty(N_B, dtype=int) for r in radii_focus}
for i in range(N_B):
    ras = rng.uniform(0, 360, len(ra)); ds = scan(ras, dec)
    for r in radii_focus:
        mcB[float(r)][i] = int((ds < r).sum())
sB = {}
for r in radii_focus:
    o = obs_f[float(r)]; a = mcB[float(r)]
    sd = float(a.std()); mn = float(a.mean())
    z = (mn - o)/sd if sd else 0.0
    sB[float(r)] = {"obs": o, "mc_mean": round(mn,1), "mc_sd": round(sd,1),
                    "z_deficit": round(z,3), "p": float((a <= o).mean())}
    q = sB[float(r)]
    print(f"  {r:>5.1f} {q['obs']:>7} {q['mc_mean']:>10.1f}±{q['mc_sd']:<6.1f} {q['z_deficit']:>8.2f} {q['p']:>8.4f}")

if all(sB[float(r)]['p'] == 0 for r in radii_focus):
    best_r = float(max(radii_focus, key=lambda r: sB[float(r)]['z_deficit']))
else:
    best_r = float(min(radii_focus, key=lambda r: sB[float(r)]['p']))
best_q = sB[best_r]
p_desi_raw = best_q['p']
p_desi = max(p_desi_raw, 1/(N_B+1))        # MC 解像度下限 (保守 clamp)
print(f"\n最佳半徑 (Phase A+B): r<{best_r}°  obs={best_q['obs']}  z_def={best_q['z_deficit']}σ  p_raw={p_desi_raw:.4f} (clamp→{p_desi:.6f})")

# ---------- Phase C: 內層確認 1.0-2.0°, N_MC=3000, scramble ----------
radii_inner = np.array([1.0, 1.5, 2.0])
N_C = 3000
print(f"\nPhase C: 內層 {radii_inner.tolist()}°, N_MC={N_C}, scramble RA keep dec...")
obs_i = {float(r): int((obs_d < r).sum()) for r in radii_inner}
mcC = {float(r): np.empty(N_C, dtype=int) for r in radii_inner}
for i in range(N_C):
    ras = rng.uniform(0, 360, len(ra)); ds = scan(ras, dec)
    for r in radii_inner:
        mcC[float(r)][i] = int((ds < r).sum())
sC = {}
for r in radii_inner:
    o = obs_i[float(r)]; a = mcC[float(r)]
    sd = float(a.std()); mn = float(a.mean())
    z = (mn - o)/sd if sd else 0.0
    sC[float(r)] = {"obs": o, "mc_mean": round(mn,1), "mc_sd": round(sd,1),
                    "z_deficit": round(z,3), "p": float((a <= o).mean())}
    q = sC[float(r)]
    print(f"  {r:>5.1f} {q['obs']:>7} {q['mc_mean']:>10.1f}±{q['mc_sd']:<6.1f} {q['z_deficit']:>8.2f} {q['p']:>8.4f}")

# ---------- Fisher 5 目錄合併 (PSZ1/PSZ2/MCXC/Abell 由 script 12 輸出提取) ----------
rv = json.load(open(os.path.join(DATA, 'reverify_cluster_vacuum.json')))
def best_of(cat):
    return min(v['p_deficit'] for k, v in rv[cat].items())
p_abell = best_of('Abell'); p_psz1 = best_of('PSZ1'); p_psz2 = best_of('PSZ2'); p_mcxc = best_of('MCXC')
p_used = [p_psz1, p_psz2, p_mcxc, p_abell, p_desi]
chi2_4 = -2*sum(math.log(p) for p in p_used[:4]); pf4 = float(_chi2.sf(chi2_4, 8)); z4 = float(_norm.isf(pf4))
chi2_5 = -2*sum(math.log(p) for p in p_used);     pf5 = float(_chi2.sf(chi2_5, 10)); z5 = float(_norm.isf(pf5))
print(f"\nFisher 合併 (p 由 reverify_cluster_vacuum.json 提取 + DESI clamp):")
print(f"  PSZ1={p_psz1:.4f} PSZ2={p_psz2:.4f} MCXC={p_mcxc:.4f} Abell={p_abell:.4f} DESI={p_desi:.6f}")
print(f"  Fisher4: p={pf4:.6e} z={z4:.3f}σ (script 12 應 3.43σ)")
print(f"  Fisher5: χ²={chi2_5:.3f} df=10 p={pf5:.6e} z={z5:.3f}σ")

out = {
    "desi_5th_vacuum_20261017": {
        "catalog": "CluMPR 2024 / DESI-Legacy DR9 photometric clusters (Yantovski-Barth+2023, Zenodo 8157751/10727242, DESI_clusters_2024_simple.fits)",
        "label_note": "DESI DR2 光譜無官方星系團 VAC → 以此作獨立第 5 族; ⚠ 非 DESI DR2 光譜數據, 部分天區",
        "N": len(ra),
        "z_median_range": [round(float(np.nanmin(t['z_median_central'])),3), round(float(np.nanmax(t['z_median_central'])),3)],
        "phaseA_NMC": N_A, "phaseB_NMC": N_B, "seed": 42,
        "phaseA_scramble": sA, "phaseA_uniform_ref": sU,
        "phaseB_focus": sB, "phaseC_inner": sC,
        "best_r": best_r, "best_obs": best_q['obs'], "best_z": best_q['z_deficit'],
        "best_p_raw": p_desi_raw, "best_p_clamped": p_desi,
        "fisher4_p": pf4, "fisher4_z": z4,
        "fisher5_p": pf5, "fisher5_z": z5, "fisher5_chi2": chi2_5,
        "p_used": [round(p,6) for p in p_used],
    },
}
json.dump(out, open(os.path.join(DATA, 'reverify_desi_dr2.json'), 'w'), indent=2)
print(f"\n已存 {os.path.join(DATA,'reverify_desi_dr2.json')}")