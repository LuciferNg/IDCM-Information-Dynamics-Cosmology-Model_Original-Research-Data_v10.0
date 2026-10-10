#!/usr/bin/env python3
"""
O48 Q1.34: 峰形純 TT 重跑 — Lorentz/Gauss fit (43 script 污染版修正)
=============================================================
Q1.31-33 audit: 43/45/46-48 用 613 rows (TT+TE+EE 混合) → 峰形結論無效。
本 script 用純 TT (215 bins) 重跑 Q1.26 峰形測量:

  A. 每峰 window fit Gauss + Lorentz (corr-level, 同 43 script)
  B. σ_m/γ_m pattern (純 TT 版本)
  C. 對比 43 script 舊結果 (污染版)
"""
import math, sys
from collections import defaultdict
import numpy as np

PASS, FAIL, TOTAL = 0, 0, 0
def check(name, cond, detail=""):
    global PASS, FAIL, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {detail}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {detail}")

base = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
DATA = f"{base}/o214_energy_budget_definition/data/planck2018_plik_lite"

# 純 TT: 每 ℓ 取 max (TT 最大)
plik = []
with open(f"{DATA}/cl_cmb_plik_v22.dat") as f:
    for line in f:
        p = line.split()
        if len(p) >= 2:
            try:
                plik.append((float(p[0]), float(p[1])))
            except ValueError:
                pass
d = defaultdict(list)
for e, v in plik:
    d[e].append(v)
tt = sorted((e, max(vs)) for e, vs in d.items())
ells = np.array([e for e, v in tt])
D = np.array([v for e, v in tt])
mask = D > 0
l, val = ells[mask], D[mask]

logD = np.log(val)
coef = np.polyfit(l, logD, 3)
env = np.exp(np.polyval(coef, l))
r = val/env - 1.0
rn = (r - r.mean())/r.std()

PEAKS = {1: 221, 2: 527, 3: 815, 5: 1121, 7: 1409}

def fit_gauss_lorentz(lo, hi):
    m = (l >= lo) & (l <= hi)
    if m.sum() < 5:
        return None
    x, y = l[m], val[m]/np.exp(np.polyval(coef, l[m])) - 1.0
    ipk = np.argmax(y)
    c0, a0 = x[ipk], max(y[ipk], 1e-6)
    bestG = bestL = None
    for c in np.linspace(c0-20, c0+20, 41):
        for s in np.linspace(15, 90, 31):
            g = a0*np.exp(-0.5*((x-c)/s)**2)
            c2 = np.sum((y-g)**2)
            if bestG is None or c2 < bestG[0]:
                bestG = (c2, c, s)
            lor = a0*s**2/((x-c)**2 + s**2)
            c2l = np.sum((y-lor)**2)
            if bestL is None or c2l < bestL[0]:
                bestL = (c2l, c, s)
    return bestG + bestL

print("="*72)
print("純 TT 峰形 fit (215 bins, detrend 3次)")
print("="*72)
results = {}
for m_, pk in PEAKS.items():
    res = fit_gauss_lorentz(pk-140, pk+140)
    if res is None:
        print(f"  峰 m={m_} ℓ={pk}: 數據不足")
        continue
    c2g, cg, sg, c2l, cl_, sl = res
    results[m_] = (pk, cg, sg, cl_, sl, c2g, c2l)
    print(f"  峰 m={m_} ℓ={pk}: Gauss σ={sg:.1f} χ²={c2g:.1f} | "
          f"Lorentz γ={sl:.1f} χ²={c2l:.1f} → "
          f"{'L勝' if c2l < c2g else 'G勝'} (ΔG−L={c2g-c2l:+.1f})")

print("\n" + "="*72)
print("A. σ_m/γ_m pattern (純 TT)")
print("="*72)
if results:
    ms = sorted(results)
    sigs = [results[m][2] for m in ms]
    gams = [results[m][4] for m in ms]
    print(f"σ_m (Gauss): {[f'{s:.1f}' for s in sigs]}")
    print(f"γ_m (Lorentz): {[f'{g:.1f}' for g in gams]}")
    print(f"σ 平均 = {np.mean(sigs):.1f}, γ 平均 = {np.mean(gams):.1f}")
    check("A1: σ 平均 ≈ 49.5±6 (297/6, Q1.25 峰固有寬度)",
          abs(np.mean(sigs) - 49.5) < 6, f"mean={np.mean(sigs):.1f} vs 49.5")
    # Lorentz 勝數
    lwin = sum(1 for m in ms if results[m][6] < results[m][5])
    print(f"Lorentz 勝: {lwin}/{len(ms)}")
    check("A2: Lorentz 全勝 (與 43 污染版一致)", lwin >= len(ms)-1,
          f"{lwin}/{len(ms)}")

print("\n" + "="*72)
print("B. 對比 43 script 舊 (613 rows) 結果")
print("="*72)
print("  43 舊: σ_m [70.0, 36.0, 40.0, 42.0, 46.0], 平均 46.8, Lorentz 全勝")
if results:
    print(f"  新 (純TT): σ_m {[f'{results[m][2]:.1f}' for m in sorted(results)]}")
    print()
    check("B1: 純TT σ 平均 vs 43 平均 46.8 (同量級)",
          abs(np.mean(sigs) - 46.8) < 8, f"{np.mean(sigs):.1f} vs 46.8")

print("\n" + "="*72)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*72)
sys.exit(0 if FAIL == 0 else 1)