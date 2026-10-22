#!/usr/bin/env python3
"""O176 audit — INDEPENDENT re-verification of every key number in docs/01-08.
Deliberately does NOT import/reuse scripts/01-05 code paths; recomputes from
the raw CSV + formula definitions to cross-check the docs' claims.
"""
import csv, math, statistics

DATA = "data/kocevski25_70agn.csv"
rows = [r for r in csv.DictReader(open(DATA))]
print(f"CSV rows: {len(rows)}")
for r in rows:
    r["z"] = float(r["z"]); r["logMBH"] = float(r["logMBH"])
    r["logMstar"] = float(r["logMstar"]); r["LRD"] = int(r["LRD"])
    r["ul"] = r["Mstar_is_upperlimit"] == "True"
    r["ratio"] = 10**(r["logMBH"] - r["logMstar"])

def med_ratio(sub):
    return 10**statistics.median([r["logMBH"]-r["logMstar"] for r in sub])

ok = fail = 0
def check(name, got, expect, tol=0.02):
    global ok, fail
    if isinstance(expect, str):
        good = abs(got - float(expect))/max(abs(float(expect)),1e-9) < tol
    else:
        good = abs(got - expect)/max(abs(expect),1e-9) < tol
    print(f"  [{'OK ' if good else 'FAIL'}] {name}: got={got:.6g} expect={expect} (rel {abs(got-float(expect))/max(abs(float(expect)),1e-9)*100:.3f}%)")
    ok += good; fail += (not good)

print("\n=== 1. docs/02 table: all-sample z-bin medians ===")
for lo,hi,exp in [(3,4,0.17),(4,5,2.29),(5,6,6.84),(6,7,5.82)]:
    sub = [r for r in rows if lo<=r["z"]<hi and not r["ul"]]
    check(f"z={lo}-{hi} median % (N={len(sub)})", med_ratio(sub)*100, exp, 0.03)

print("\n=== 2. docs/02+06: LRD-only z-bin medians ===")
for lo,hi,exp in [(3,4,6.03),(4,5,8.13),(5,6,7.85),(6,7,9.44)]:
    sub = [r for r in rows if lo<=r["z"]<hi and r["LRD"] and not r["ul"]]
    check(f"LRD z={lo}-{hi} median % (N={len(sub)})", med_ratio(sub)*100, exp, 0.03)

print("\n=== 3. docs/02: paper medians + alpha_eff ===")
r35 = med_ratio([r for r in rows if r["z"]<4 and not r["ul"]])  # z<4 all
print(f"  z<4 all-sample median: {r35*100:.3f}%")
# alpha_eff from paper medians 0.15% (z<4) -> 7% (z~6.5)
def t_lcdm(z):
    return 13.968*(2/3)*(1/math.sqrt(0.7))*math.asinh(math.sqrt(0.7/0.3)*(1+z)**-1.5)
alpha = math.log(7/0.15)/math.log(t_lcdm(3.5)/t_lcdm(6.5))
check("alpha_eff(obs) vs 5.04", alpha, 5.04, 0.02)
print(f"  t(3.5)={t_lcdm(3.5):.3f} t(6.5)={t_lcdm(6.5):.3f}")

print("\n=== 4. docs/02+06: P12' predictions (1/306)(13.8/t)^1.74 ===")
for z,exp in [(3.5,11.6),(4.5,19.5),(5.5,30.2),(6.5,43.8)]:
    p = (1/306)*(13.8/t_lcdm(z))**1.74*100
    check(f"P12' z={z}", p, exp, 0.02)

print("\n=== 5. docs/06: v2 Phase B free-fall + z_c ===")
for z,exp in [(3.5,7.09),(3,5.46),(2,2.89),(1,1.21),(0.5,0.68),(0,0.34)]:
    p = (1/306)*(13.8/t_lcdm(z))**1.5*100
    check(f"free-fall z={z} %", p, exp, 0.02)
t_c = 13.8*(306*3/40)**(-2/3)
print(f"  t_c = {t_c:.4f} Gyr  (docs: 1.71)")
# invert z
lo,hi=0.,12.
for _ in range(100):
    mid=(lo+hi)/2
    if t_lcdm(mid)>t_c: lo=mid
    else: hi=mid
zc=(lo+hi)/2
check("z_c (3/40) vs 3.61", zc, 3.61, 0.01)

print("\n=== 6. docs/07: M* bin medians ===")
bins = [(7.5,8.0,5.25),(8.0,8.5,6.53),(8.5,9.0,2.29),(9.0,9.5,2.29),(9.5,10.0,0.11),(10.0,10.5,0.0372),(10.5,11.1,0.0135)]
meds=[]; mids=[]
for lo,hi,exp in bins:
    sub=[r for r in rows if lo<=r["logMstar"]<hi and not r["ul"]]
    m=med_ratio(sub)*100
    check(f"M* {lo}-{hi} median % (N={len(sub)})", m, exp, 0.05)
    if len(sub)>=3: meds.append(math.log10(m/100)); mids.append((lo+hi)/2)
# slope: linear fit log10(ratio) vs log10(M*)  (docs: -0.88)
n=len(meds)
mx=sum(mids)/n; my=sum(meds)/n
sx=math.sqrt(sum((x-mx)**2 for x in mids)/n); sy=math.sqrt(sum((y-my)**2 for y in meds)/n)
cov=sum((x-mx)*(y-my) for x,y in zip(mids,meds))/n
slope = cov/sx**2 if sx>0 else float('nan')
print(f"  raw slope (log10 ratio vs log10 M*): {slope:.3f}  (docs: -0.88; note: M* bin widths vary)")
# Also slope in natural-log space
meds_ln=[m*math.log(10) for m in meds]
cov2=sum((x-mx)*(y-my) for x,y in zip(mids,meds_ln))/n
print(f"  ln-slope: {cov2/sx**2:.3f}")

print("\n=== 7. docs/08 D1: A5 60-node write = budget/N_gen ===")
Bn = 123/88
for obs,label in [(0.2443,"SMICA obs")]:
    cost = 60*Bn*obs
    check(f"60-node budget cost ({label}) = 61.5/3=20.5", cost, 20.5, 0.01)
check("11/45 vs 0.2443", 11/45, 0.2443, 0.001)
print(f"  11/15 = {11/15:.4f} (old candidate, factor {11/15/0.2443:.4f} off = ~N_gen)")

print("\n=== 8. docs/07: completion halo 3060*M_BH ===")
for lmbh,exp in [(7.5,"10^10.99"),(8.0,"10^11.49")]:
    mh=306*10**lmbh/0.1
    check(f"M_BH=1e{lmbh} -> halo 1e{math.log10(mh):.2f}", math.log10(mh), float(exp.split("^")[1]), 0.01)

print("\n=== 9. structural constants ===")
check("3/40 = N_gen/(N_d-B)", 3/40, 3/(44-4), 1e-9)
check("1/306 = 1/(L6*F_proj)", 1/306, 1/(18*17), 1e-9)
check("3060 = 306/f_bar(0.1)", 3060, 306/0.1, 1e-9)
check("61.5 = 44*B(n)", 61.5, 44*123/88, 1e-9)
check("B(n) = 123/88 = L10/N_gen/(N_d-B)? ", 123/88, 1.3977272727, 1e-6)

print(f"\n===== RESULT: {ok} OK / {fail} FAIL =====")
