#!/usr/bin/env python3
"""
O252 — Script 10: depth gap — SNR bias 假設檢驗 (2026-10-17)
============================================================
問題: R3 depth 中位 0.816 < 預言 τ_w=⟨hop⟩=4 → depth=0.9817.
假設: 低 SNR (低 ΔAIC) fit 嘅 dip 深度被低估 (noise 將 dip 拉淺),
      結構真值 = 0.9817; 高 ΔAIC 源應趨近 0.982.
檢驗:
  [G1] corr(depth, ΔAIC) > 0.3 (正相關 — SNR bias 存在)
  [G2] 高 ΔAIC 群 (≥100) depth 中位 ≈ 0.982±0.05
  [G3] depth 上限群 (top 3) 中位 ≈ 0.982 (dev < 10%)
另查: A Hα m(0.82)/h(0.94) 同源分歧 — 都係 SNR 問題?
"""
import json, math, os
import numpy as np

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
LOG = []
def ck(name, cond, detail=''):
    LOG.append((name, bool(cond), detail))
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")

with open(f"{DATA}/07_full_sample_scan.json") as f:
    d7 = json.load(f)
res = [r for r in d7["results"] if r["sig"] and abs(r["dv"]) < 700 and r["depth"] < 1.2]

depths = np.array([r["depth"] for r in res])
aics = np.array([r["dAIC"] for r in res])
sigs = np.array([r["sig_dip"] for r in res])
dvs = np.array([abs(r["dv"]) for r in res])
N = len(res)
print("="*84)
print("O252/10 — depth gap: SNR bias 檢驗")
print("="*84)
print(f"N={N}: depth 中位={np.median(depths):.3f}, 均值={depths.mean():.3f}, "
      f"max={depths.max():.3f}  (預言 0.9817)")

# G1: corr(depth, ΔAIC)
rho = np.corrcoef(depths, aics)[0,1]
tau_k = None
# Kendall tau (穩健)
from itertools import combinations
conc, disc = 0, 0
for (i,j) in combinations(range(N), 2):
    dd = (depths[i]-depths[j])*(aics[i]-aics[j])
    if dd > 0: conc += 1
    elif dd < 0: disc += 1
tau_k = (conc-disc)/(conc+disc) if (conc+disc) else 0
print(f"corr(depth, ΔAIC) = {rho:.3f}, Kendall τ = {tau_k:.3f}")
ck("G1 corr(depth, ΔAIC) > 0.3", tau_k > 0.3, f"τ={tau_k:.3f}")

# G2: 高 ΔAIC 群
hi = [r for r in res if r["dAIC"] >= 100]
if len(hi) > 0:
    hd = np.array([r["depth"] for r in hi])
    md = np.median(hd)
    print(f"高 ΔAIC(≥100) n={len(hi)}: depth 中位={md:.3f}")
    ck("G2 高 ΔAIC 群 depth ≈ 0.982±0.05", abs(md-0.9817) < 0.05, f"中位 {md:.3f}")
else:
    ck("G2 高 ΔAIC 群 depth ≈ 0.982", False, "冇源")

# G3: top 3 depth
top3 = sorted(res, key=lambda r: -r["depth"])[:3]
print("Top 3 depth:", [(r["src"], r["line"], round(r["depth"],3), round(r["dAIC"],1)) for r in top3])
ck("G3 top-3 depth ≈ 0.982 (dev<10%)",
   abs(np.mean([r["depth"] for r in top3]) - 0.9817)/0.9817 < 0.10,
   f"mean top3={np.mean([r['depth'] for r in top3]):.3f}")

# G4: A 同源 grating 分歧 (m 0.82 vs h 0.94) — 高解像 h 深啲?
a_alpha = [r for r in res if r["src"]=="A" and r["line"]=="Hα"]
if len(a_alpha) == 2:
    dm, dh = a_alpha[0]["depth"], a_alpha[1]["depth"]
    dAIC_m, dAIC_h = a_alpha[0]["dAIC"], a_alpha[1]["dAIC"]
    print(f"A Hα m: depth={dm:.3f} ΔAIC={dAIC_m:.0f} | h: depth={dh:.3f} ΔAIC={dAIC_h:.0f}")
    ck("G4 A Hα 高解像 h 深 (ΔAIC 高)", dh > dm, f"{dm:.2f}→{dh:.2f}")

# 深度 vs SNR 嘅 fits: depth = a + b·ΔAIC (log)
# 用 Δχ² ≈ ΔAIC obs; 近似 noise ∝ 1/√ΔAIC
data = {"N": N, "corr_pearson": rho, "kendall_tau": tau_k,
        "median_depth": float(np.median(depths)),
        "max_depth": float(depths.max()),
        "high_AIC_n": len(hi),
        "high_AIC_median_depth": float(np.median([r["depth"] for r in hi])) if len(hi) else None,
        "top3_depth": [r["depth"] for r in top3],
        "conclusion": ("SNR bias 存在" if tau_k > 0.3 else "SNR bias 唔明顯") +
                      " — depth gap " + ("由 fit bias 解釋 (結構 0.982 成立)" if tau_k > 0.3 and abs(np.median([r['depth'] for r in hi])-0.9817) < 0.05 else "仍然係結構 gap"),
        "checks": [{"name": n, "pass": p, "detail": d} for n,p,d in LOG]}
with open(f"{DATA}/10_depth_snr.json","w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
np_ok = sum(1 for _,p,_ in LOG if p)
print(f"\n結果: {np_ok}/{len(LOG)} PASS → data/10_depth_snr.json")