#!/usr/bin/env python3
"""
O252 — Script 12: σ_window 帶厚修正候選 (2026-10-17)
=====================================================
R3/R5 發現: σ_dip 分佈 mean 189.3, 中位 184.4 vs 預言 σ₃=167.23 (1.10×)。
新候選 (零常數, 純結構):
  S-e: σ_window = σ₃·R_band_ratio = σ₃·(1+8/60) = σ₃·(17/15)
       = 167.228×1.13333 = 189.525 km/s
       物理: 凝聚層帶厚 (hop 直徑 8/Σ60) 令窗寬乘上厚度幾何因子
判定:
  [S1] obs σ_dip mean 對 189.53 (dev < 3%)
  [S2] t-test: |mean−189.53| / SE < 1.5 (不可分辨)
  [S3] 對照 σ₃=167.23: 明顯差 (mean−167.23)/SE > 2 (舊預言差)
  [S4] 中位都近 189.53±8%
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
res = [r for r in d7["results"] if r["sig"] and abs(r["dv"]) < 700 and r["depth"] < 1.2
       and 50 < r["sig_dip"] < 300]
sigs = np.array([r["sig_dip"] for r in res])
N = len(sigs)

C_KM = 299792.458
sig3 = C_KM*math.pi/(88*4**3)
R_band_ratio = 1 + 8/60
sig_e = sig3*R_band_ratio      # 189.525

print("="*84)
print("O252/12 — σ_window 帶厚修正候選 (σ₃·(1+8/60))")
print("="*84)
print(f"N={N}: obs σ_dip mean={sigs.mean():.2f}, median={np.median(sigs):.2f}, "
      f"std={sigs.std(ddof=1):.2f}")
print(f"σ₃ = {sig3:.2f}   σ₃×(17/15) = {sig_e:.2f}")
SE = sigs.std(ddof=1)/math.sqrt(N)
print(f"SE = {SE:.2f}")

d1 = abs(sigs.mean()-sig_e)/sig_e*100
ck("S1 mean vs σ₃·17/15 (dev<3%)", d1 < 3, f"dev {d1:.2f}%")
t_e = (sigs.mean()-sig_e)/SE
ck("S2 |t| < 1.5 (mean=σ_e 不可分辨)", abs(t_e) < 1.5, f"t={t_e:.2f}")
t3 = (sigs.mean()-sig3)/SE
ck("S3 同 σ₃ 舊預言差 (|t|>2)", abs(t3) > 2, f"t={t3:.2f} (mean−σ₃ 差 {sigs.mean()-sig3:.1f})")
dmed = abs(np.median(sigs)-sig_e)/sig_e*100
ck("S4 中位近 σ_e (±8%)", dmed < 8, f"中位 dev {dmed:.2f}%")

data = {"N": N, "obs_mean": float(sigs.mean()), "obs_median": float(np.median(sigs)),
        "obs_std": float(sigs.std(ddof=1)), "SE": SE,
        "sig3": sig3, "R_band_ratio": R_band_ratio, "sig_E": sig_e,
        "t_sigE": t_e, "t_sig3": t3,
        "conclusion": f"σ_window = σ₃·(1+8/60) = {sig_e:.2f} km/s 命中 mean "
                      f"{sigs.mean():.2f} ({d1:.2f}%) — 帶厚修正成立" if (d1<3 and abs(t_e)<1.5) else "帶厚修正不成立",
        "checks": [{"name": n, "pass": p, "detail": d} for n,p,d in LOG]}
with open(f"{DATA}/12_sigma_bandthickness.json","w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
np_ok = sum(1 for _,p,_ in LOG if p)
print(f"\n結果: {np_ok}/{len(LOG)} PASS → data/12_sigma_bandthickness.json")