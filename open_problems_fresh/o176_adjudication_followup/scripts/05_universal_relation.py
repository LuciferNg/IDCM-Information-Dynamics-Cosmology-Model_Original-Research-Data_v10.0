#!/usr/bin/env python3
"""O176 - Universal relation test: is M_BH/M_* a function of HOST MASS (not z)?

P12'-v2 unification hypothesis (docs/07):
  ratio = f(host completion);  completion halo = 306*M_BH/f_bar ~ 3060*M_BH
  -> ratio(M_*) should be z-INDEPENDENT (single relation)
  -> the observed 'redshift evolution' (0.15% z<4 -> 7% z=6-7) is host-mass
     evolution: LRDs = low M_* (incomplete), non-LRDs = high M_* (complete)

Test with Kocevski+25 (69 sources): bin by M_* (not z); check
  (a) median ratio decreases monotonically with M_*  [expected]
  (b) LRD vs non-LRD collapse onto the same relation [key test]
  (c) no residual z-trend at fixed M_*              [key test]
"""
import csv, os, statistics, math

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data", "kocevski25_70agn.csv")
rows = [r for r in csv.DictReader(open(DATA)) if r["Mstar_is_upperlimit"] == "False"]
for r in rows:
    r["z"] = float(r["z"]); r["logMstar"] = float(r["logMstar"])
    r["logratio"] = float(r["logMBH"]) - float(r["logMstar"])
    r["LRD"] = int(r["LRD"])

print("="*80)
print("(a) Median ratio vs host mass bins (all 60 sources with measured M*)")
print("="*80)
bins = [(7.5,8.0),(8.0,8.5),(8.5,9.0),(9.0,9.5),(9.5,10.0),(10.0,10.5),(10.5,11.1)]
print(f"{'logM* bin':<14}{'N':>4}{'LRD':>5}  {'med ratio':>10}{'med z':>7}")
for lo, hi in bins:
    sub = [r for r in rows if lo <= r["logMstar"] < hi]
    if len(sub) >= 3:
        med_r = statistics.median([r["logratio"] for r in sub])
        med_z = statistics.median([r["z"] for r in sub])
        n_lrd = sum(1 for r in sub if r["LRD"])
        print(f"{lo}-{hi:<9}{len(sub):>4}{n_lrd:>5}  {10**med_r*100:>8.2f}%{med_z:>7.2f}")

print()
print("="*80)
print("(b) LRD vs non-LRD at same M*: do they collapse?")
print("="*80)
for lo, hi in [(7.5,8.5),(8.5,9.5),(9.5,11.1)]:
    l = [r for r in rows if lo <= r["logMstar"] < hi and r["LRD"]]
    n = [r for r in rows if lo <= r["logMstar"] < hi and not r["LRD"]]
    ml = statistics.median([r["logratio"] for r in l]) if len(l)>=2 else None
    mn = statistics.median([r["logratio"] for r in n]) if len(n)>=2 else None
    def pct(x): return f"{10**x*100:.2f}%" if x is not None else "--"
    print(f"M* {lo}-{hi}:  LRD N={len(l):>2} med={pct(ml):>8}  |  non-LRD N={len(n):>2} med={pct(mn):>8}"
          f"  {'COLLAPSE' if ml is not None and mn is not None and abs(ml-mn)<0.5 else 'split'}")

print()
print("="*80)
print("(c) Residual z-trend at fixed M* (within bin 8.0-9.0, split by z)")
print("="*80)
sub = [r for r in rows if 8.0 <= r["logMstar"] < 9.0]
lo_z, hi_z = [r for r in sub if r["z"] < 5.2], [r for r in sub if r["z"] >= 5.2]
if len(lo_z) >= 2 and len(hi_z) >= 2:
    mlo = statistics.median([r["logratio"] for r in lo_z])
    mhi = statistics.median([r["logratio"] for r in hi_z])
    print(f"  M* 8.0-9.0, z<5.2: N={len(lo_z):>2} med={10**mlo*100:.2f}%   |   z>=5.2: N={len(hi_z):>2} med={10**mhi*100:.2f}%")
    print(f"  residual z-trend at fixed M*: {abs(mlo-mhi):.2f} dex  -> {'UNIVERSAL (no residual)' if abs(mlo-mhi)<0.4 else 'residual z-trend'}")
else:
    print("  insufficient N for split test")

print()
print("="*80)
print("Completion halo check: M_halo(completion) = 306*M_BH/f_bar, f_bar=0.1")
print("="*80)
for lmbh in [6.5, 7.0, 7.5, 8.0]:
    mbh = 10**lmbh
    mh = 306*mbh/0.1
    print(f"  M_BH=10^{lmbh}: M_host_final={306*mbh:.1e}, M_halo(compl)={mh:.1e} = 10^{math.log10(mh):.2f}")
print("  observed: LRD halos 10^10.1(z=7.5) -> 10^11.3(z=3.5) (Zhang+26)")
print("  -> completion at M_BH~6e7 consistent with 10^11.3")
