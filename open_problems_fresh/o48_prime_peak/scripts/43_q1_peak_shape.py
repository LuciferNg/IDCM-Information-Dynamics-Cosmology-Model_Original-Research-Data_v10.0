#!/usr/bin/env python3
"""
O48 Q1.26: 峰形測量 — Planck Plik-lite 每個峰嘅實際寬度/形狀
=============================================================
Q1.25: σ≈50 = 峰自然寬度 (唔係 instrument)。本 script 用 Plik-lite
高分辨數據實測每個峰嘅形狀:

  1. detrend (log-二次包絡) → 殘差起伏
  2. 每個 IDCM 峰位附近 (window ±150) fit 峰形:
     - Gaussian 中心/寬度 (σ_m)
     - Lorentzian 對比 (峰形係 Gauss 定 Cauchy?)
     - asymmetry (左右半寬)
  3. 睇 σ_m 隨峰序 m 嘅 pattern (恆定? 遞增?)
  4. 對比結構候選: 297/6=49.5, L₄²=49, 峰間隙/6

數據: Planck Plik-lite 613 bins (ℓ 32..2492, bin 9/17)
山峰: 221, 527, 815, 1121, 1409 (真峰)
"""
import math, sys
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

plik = []
with open(f"{DATA}/cl_cmb_plik_v22.dat") as f:
    for line in f:
        p = line.split()
        if len(p) >= 2:
            try:
                plik.append((float(p[0]), float(p[1])))
            except ValueError:
                pass
plik = sorted(plik)
ells = np.array([e for e, d in plik])
D = np.array([d for e, d in plik])
mask = D > 0
l, d = ells[mask], D[mask]

# detrend (log 二次 + 小幅 smooth 落)
logD = np.log(d)
coef = np.polyfit(l, logD, 3)
env = np.exp(np.polyval(coef, l))
r = d/env - 1.0   # 相對起伏 (0 中心)
rn = (r - r.mean())/r.std()

PEAKS = {1: 221, 2: 527, 3: 815, 5: 1121, 7: 1409}

print("="*72)
print("A. 每個峰嘅峰形 fit (Plik-lite detrend residual)")
print("="*72)

def fit_gauss(lo, hi):
    """喺 [lo,hi] 內 fit Gaussian a·exp(-(l-c)²/2σ²) + b"""
    m = (l >= lo) & (l <= hi)
    if m.sum() < 5:
        return None
    x, y = l[m], r[m]
    # 用 peak 附近做初值
    ipk = np.argmax(y)
    c0, a0 = x[ipk], max(y[ipk], 1e-6)
    sig0 = 50.0
    # simple grid refine: scan center/width
    best = None
    for c in np.linspace(c0-20, c0+20, 41):
        for s in np.linspace(20, 90, 36):
            g = a0*np.exp(-0.5*((x-c)/s)**2)
            chi2 = np.sum((y - g)**2)
            if best is None or chi2 < best[0]:
                best = (chi2, c, s, a0)
    return best

def fit_lorentz(lo, hi):
    """Lorentzian 對比"""
    m = (l >= lo) & (l <= hi)
    if m.sum() < 5:
        return None
    x, y = l[m], r[m]
    ipk = np.argmax(y)
    c0, a0 = x[ipk], max(y[ipk], 1e-6)
    best = None
    for c in np.linspace(c0-20, c0+20, 41):
        for g in np.linspace(20, 90, 36):
            lor = a0*g**2/((x-c)**2 + g**2)
            chi2 = np.sum((y - lor)**2)
            if best is None or chi2 < best[0]:
                best = (chi2, c, g, a0)
    return best

widths = {}
for m, pk in PEAKS.items():
    # window: 峰間距 306/288 → 用 ±150 (半峰間隙)
    lo, hi = pk-140, pk+140
    g = fit_gauss(lo, hi)
    lo2, hi2 = pk-140, pk+140
    lz = fit_lorentz(lo2, hi2)
    if g:
        chi2g, cg, sg, ag = g
        widths[m] = sg
        # asymmetry: 左半寬 vs 右半寬 (喺半高處)
        half = ag/2 + (r[np.abs(l-pk) < 10].min() if np.abs(l-pk).min() < 10 else 0)
        # 半高 crossing (用 detrend data)
        mw = (l >= pk-140) & (l <= pk+140)
        xw, yw = l[mw], r[mw]
        # 粗略: 峰位 ± 左右 1σ 寬
        lsigma = cg - sg
        rsigma = cg + sg
        asym = (rsigma - pk)/(pk - lsigma)
        msg = f"峰 m={m} ℓ={pk}: Gauss c={cg:.1f} σ={sg:.1f}  χ²={chi2g:.1f}"
        if lz:
            chi2lz, clz, glz, alz = lz
            msg += f" | Lorentz γ={glz:.1f} χ²={chi2lz:.1f} {'(L<G)' if chi2lz<chi2g else '(G≤L)'}"
        msg += f" asym={asym:.2f}"
        print(f"  {msg}")
    else:
        print(f"  峰 m={m} ℓ={pk}: fit 失敗 (數據不足)")

print("\n" + "="*72)
print("B. σ_m pattern")
print("="*72)
if widths:
    ms = sorted(widths)
    sw = [widths[m] for m in ms]
    print(f"σ_m: {[f'{s:.1f}' for s in sw]}")
    print(f"平均 σ = {np.mean(sw):.1f}, 範圍 [{min(sw):.1f}, {max(sw):.1f}]")
    print(f"候選: 297/6={297/6:.1f}, L₄²=49, 峰間隙/6=306/6=51, 288/6=48")
    check("B1: σ_m 平均 ≈ 49.5±5 (297/6)", abs(np.mean(sw) - 297/6) < 5,
          f"mean={np.mean(sw):.1f} vs 49.5")
    # monotonic?
    if len(sw) >= 4:
        dsw = np.diff(sw)
        mono = all(x > 0 for x in dsw) or all(x < 0 for x in dsw)
        check("B2: σ_m 單調 (遞增/遞減)", mono, f"diff={[f'{x:.1f}' for x in dsw]}")
    print(f"σ/峰間距: {[f'{s/306:.3f}' if (m in (1,3)) else f'{s/288:.3f}' for m,s in zip(ms,sw)]}")

print("\n" + "="*72)
print("C. peak 形狀: Gauss vs Lorentz 比較")
print("="*72)
print("  (fit 內比較 chi2 已列喺 A 段)")

print("\n" + "="*72)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*72)
sys.exit(0 if FAIL == 0 else 1)