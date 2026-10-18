#!/usr/bin/env python3
"""
P12 攻堅 — 路線 2 Golden Standard: exact Binomial tail 驗證 Gaussian p (2026-10-18)
=================================================================================
script 22 (N_MC=6000) 嘅 p_raw=0 因 MC 解像度不足 (z>4); p_gauss = norm.sf(z) 已過
Gaussianity (KS) 但係近似。本 script 用 exact Binomial CDF 做獨立確認:
  X ~ Binom(N, p̂), p̂ = MC_mean/N (由 22 個 MC 高精度掃描抽出)
  p_exact = P(X ≤ obs)  — 唔靠 Gaussian 假設, scipy boost 對大 N 精確。
同時用 P5 script 12 嘅 4 目錄 p 重算 Fisher5: clamp / Gaussian / exact 三版。
"""
import os, json, math
import numpy as np
from scipy.stats import binom, chi2 as _chi2, norm as _norm

HERE = os.path.dirname(os.path.abspath(__file__))
P12  = os.path.dirname(HERE)
MAIN = os.path.dirname(P12)
RV   = os.path.join(MAIN, 'p5_crystal_stress', 'data', 'reverify_cluster_vacuum.json')
G22  = os.path.join(P12, 'data', 'reverify_desi_inner_grid.json')

g = json.load(open(G22))['p12_inner_grid_gaussian_20261018']
N = g['N']
rows = g['rows']

targets = [1.75, 2.0, 2.25, 2.5, 3.0]
print(f"CluMPR N = {N}; exact Binomial tail (p̂ = MC_mean/N):\n")
exact = {}
for r in targets:
    q = rows[str(float(r))]  # json key 係 float str
    # json 圓整咗 mc_mean (1 decimal) — 由 mc_mean 推 p̂ 有微小誤差; 用 z 交叉檢查
    p_hat = q['mc_mean'] / N
    p_ex  = float(binom.cdf(q['obs'], int(N), p_hat))
    # 對照: Gaussian 直接由 z
    p_gz  = q['p_gauss']
    z_again = float(_norm.isf(p_ex))
    exact[str(float(r))] = {"obs": q['obs'], "mc_mean": q['mc_mean'],
                            "p_hat": round(p_hat, 9), "p_exact_binom": p_ex,
                            "z_exact": round(z_again, 3), "p_gauss_22": p_gz}
    print(f"  r={r:>4.2f}°  obs={q['obs']:>7}  p̂={p_hat:.6f}  p_exact={p_ex:.4g}  "
          f"(z_exact={z_again:.3f}σ | z_MC={q['z_deficit']}σ | p_gauss={p_gz:.3g})")

# Fisher5 三版 — 主報告用 3.0° (交接指定)
rv = json.load(open(RV))
def best_of(cat):
    return min(v['p_deficit'] for v in rv[cat].values())
p_abell, p_psz1, p_psz2, p_mcxc = best_of('Abell'), best_of('PSZ1'), best_of('PSZ2'), best_of('MCXC')

def fisher5(p_desi, tag):
    p_used = [p_psz1, p_psz2, p_mcxc, p_abell, float(p_desi)]
    c5 = -2*sum(math.log(p) for p in p_used)
    pf5 = float(_chi2.sf(c5, 10)); z5 = float(_norm.isf(pf5))
    print(f"  Fisher5 [{tag:>14}]: p_DESI={p_desi:.4g} -> χ²={c5:.2f} p={pf5:.3g} z={z5:.3f}σ")
    return {"tag": tag, "p_dei": round(float(p_desi), 8), "chi2": round(c5, 3),
            "p_fisher": pf5, "z_fisher": round(z5, 3)}

p30 = rows[str(3.0)]
out_fisher = [
    fisher5(2.0e-4, "clamp (P5)"),
    fisher5(exact[str(3.0)]['p_exact_binom'], "exact@3.0"),
    fisher5(exact[str(3.0)]['p_gauss_22'], "gauss@3.0"),
    fisher5(exact[str(2.0)]['p_exact_binom'], "exact@2.0 (最強)"),
]

out = {"p12_exact_binom_validation_20261018": {
    "N": N, "cat_p": {"PSZ1": p_psz1, "PSZ2": p_psz2, "MCXC": p_mcxc, "Abell": p_abell},
    "exact": exact, "fisher5": out_fisher,
    "note": "p_exact 由 Binom(N, p̂=MC_mean/N) CDF 得出, 唔靠 Gaussian; p_gauss 直接取自 script 22",
}}
dst = os.path.join(P12, 'data', 'reverify_desi_exact_p.json')
json.dump(out, open(dst, 'w'), indent=2)
print(f"\n已存 {dst}")