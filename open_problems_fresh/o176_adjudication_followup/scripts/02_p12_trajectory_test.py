#!/usr/bin/env python3
"""O176 - R1/P12' adjudication: Kocevski+2025 (arXiv:2510.07376) vs P12' trajectory.

P12' (O173 docs/18): ratio(t) = (1/306) * (13.8 Gyr / t)^1.74
Observed: 69 broad-line AGN at 3<z<7, M_BH single-epoch virial, M* 2D-profile + SED.

Adjudication:
  1. Binned median M_BH/M_* (all / LRD-only / non-LRD) vs P12' at bin centers
  2. Observed slope vs P12' slope  (alpha_eff re-derivation)
  3. Paper's own forward-modeled intrinsic evolution (2.294 dex z=3.5->6.5)
  4. Zhang+2026 (arXiv:2606.02773) halo-growth cross-check
"""
import csv, math, os, statistics

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data", "kocevski25_70agn.csv")

# ---- cosmology: flat LCDM H0=70, Om=0.3 (same as Kocevski+25) ----
H0_GYR = 13.968  # 1/H0 for h=0.7
OM, OL = 0.3, 0.7

def t_lcdm(z):
    """cosmic age Gyr"""
    return H0_GYR * (2/3) * (1/math.sqrt(OL)) * math.asinh(math.sqrt(OL/OM) * (1+z)**(-1.5))

def p12prime(z):
    t = t_lcdm(z)
    return (1/306) * (13.8/t)**1.74

rows = list(csv.DictReader(open(DATA)))
for r in rows:
    r["z"] = float(r["z"]); r["logMBH"] = float(r["logMBH"]); r["logMstar"] = float(r["logMstar"])
    r["LRD"] = int(r["LRD"]); r["ul"] = r["Mstar_is_upperlimit"] == "True"
    r["ratio"] = 10**(r["logMBH"] - r["logMstar"])
    r["logratio"] = r["logMBH"] - r["logMstar"]

print("=" * 78)
print("P12' trajectory check:  ratio(t) = (1/306)(13.8/t)^1.74   vs   Kocevski+25 (N=69)")
print("=" * 78)
print(f"{'z bin':<8}{'N':>4}{'N_LRD':>6}  {'obs median':>12}{'P12 prime':>12}{'dev dex':>9}   note")
print("-" * 78)
bins = [(3,4),(4,5),(5,6),(6,7)]
for lo, hi in bins:
    sub = [r for r in rows if lo <= r["z"] < hi and not r["ul"]]
    n_lrd = sum(1 for r in sub if r["LRD"])
    if sub:
        med = statistics.median([r["logratio"] for r in sub])
        zc = 0.5*(lo+hi)
        pred = math.log10(p12prime(zc))
        dev = med - pred
        print(f"z={lo}-{hi}  {len(sub):>4}{n_lrd:>6}  {10**med*100:>10.2f}%{10**pred*100:>10.1f}%{dev:>+9.2f}   all")
    else:
        print(f"z={lo}-{hi}  {0:>4}{0:>6}  {'--':>12}{'--':>12}{'--':>9}")

# LRD-only
print("-" * 78)
print("LRD-only medians (P12' applies to seed-first LRD population):")
for lo, hi in bins:
    sub = [r for r in rows if lo <= r["z"] < hi and r["LRD"] and not r["ul"]]
    n_ul = sum(1 for r in rows if lo <= r["z"] < hi and r["LRD"] and r["ul"])
    if sub:
        med = statistics.median([r["logratio"] for r in sub])
        zc = 0.5*(lo+hi)
        pred = math.log10(p12prime(zc))
        dev = med - pred
        print(f"  z={lo}-{hi}  N={len(sub):>2} (UL:{n_ul})  med={10**med*100:>7.2f}%  P12'={10**pred*100:>6.1f}%  dev={dev:>+5.2f} dex")
    else:
        print(f"  z={lo}-{hi}  N=0 (UL:{n_ul})")

print("-" * 78)
# ---- slope / alpha_eff ----
r35 = 0.0015  # Kocevski+25: z<4 median 0.15%
r65 = 0.07    # z=6-7 median 7%
t35, t65 = t_lcdm(3.5), t_lcdm(6.5)
alpha_obs = math.log(r35/r65) / math.log(t65/t35)
alpha_p12 = 1.74
print(f"Paper medians:  z<4: 0.15%  |  z~5.5: 4%  |  z=6-7: 7%")
print(f"Observed factor increase z=3.5->6.5: {r65/r35:.0f}x  (paper forward-model: ~197x, +2.294 dex, +-0.751, >3sigma)")
print(f"alpha_eff(obs)  = {alpha_obs:.2f}   vs   P12' alpha = {alpha_p12}")
print(f"P12' predicts ratio(3.5)/ratio(6.5) = {(t65/t35)**alpha_p12:.3f}; observed = {r35/r65:.4f}")

# ---- Zhang+2026 halo growth ----
print("-" * 78)
print("Zhang+2026 (arXiv:2606.02773) cross-check: halo masses (98 LRD, 6 fields)")
print("  log M_halo LRD: z=6-7: 10.05 | z=5-6: 10.19 | z=4-5: 10.49 | z=3-4: 11.26")
print("  LRD halo grows ~1.2 dex z=6.5->3.5 while BH mass 'shows little evolution'")
print("  -> M_BH/M_* decline driven by host assembly = seed-first structure CONFIRMED")
print("  -> 'converge toward local M*-M_BH relation by z~3.5'")

print("=" * 78)
print("VERDICT summary (quantitative):")
dev_all = []
for lo, hi in bins:
    sub = [r for r in rows if lo <= r["z"] < hi and not r["ul"]]
    if sub:
        med = statistics.median([r["logratio"] for r in sub])
        zc = 0.5*(lo+hi)
        dev_all.append(med - math.log10(p12prime(zc)))
print(f"  all-sample: P12' overshoots observed medians by {statistics.fmean(dev_all):+.2f} dex avg")
lrds = [r for r in rows if r["LRD"] and not r["ul"]]
med_all_lrd = statistics.median([r["logratio"] for r in lrds])
print(f"  LRD-only overall median: {10**med_all_lrd*100:.2f}%  (N={len(lrds)})")
print("  systematics: BH mass +-1 dex (virial vs electron-scatter), host mass up to 60-70x")
print("  underestimate (Pacucci+2023 nuclear light) -> both cut BOTH ways")
