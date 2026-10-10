#!/usr/bin/env python3
"""
O48 Q1.43: 峰形不對稱 Lorentz — 純 TT + cov TT block（46b 污染修正版）
================================================================
46b 用 613-rows data (mask=D>0 保留 TE/EE) → fit 心漂 (m=1 c=96 vs 221)。
修正: 純 TT 215 bins（每 ℓ max value）+ cov TT block (215×215)。
框架保持 46b: 逐峰 window / local baseline / asymmetric Lorentz / μK² cov χ²。
"""
import math, sys
import numpy as np
from collections import defaultdict

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

# ---------- 純 TT loader (每 ℓ max) ----------
plik = []
for line in open(f"{DATA}/cl_cmb_plik_v22.dat"):
    p = line.split()
    if len(p) >= 2:
        try: plik.append((float(p[0]), float(p[1])))
        except ValueError: pass
d = defaultdict(list)
for e, v in plik: d[e].append(v)
tt = np.array(sorted((e, max(vs)) for e, vs in d.items()))
ells = tt[:, 0]; D = tt[:, 1]
print(f"純 TT: {len(ells)} bins, ℓ {ells[0]:.0f}..{ells[-1]:.0f}")

# ---------- cov TT block ----------
raw = open(f"{DATA}/c_matrix_plik_v22.dat", 'rb').read()
nrec = np.frombuffer(raw, dtype=np.int32, count=1)[0]
cov = np.frombuffer(raw[4:4+nrec], dtype=np.float64).reshape(613, 613).copy()
covTT = cov[:215, :215]
print(f"cov TT block: {covTT.shape}, diag@ℓ221 idx: {covTT[27,27]:.2e}")

ALL_PEAKS = sorted([221, 527, 815, 1013, 1121, 1337, 1409])
PEAKS = {1: 221, 2: 527, 3: 815, 5: 1121, 7: 1409}

def window_lim(pk):
    lo = pk - 130
    hi = pk + 130
    for q in ALL_PEAKS:
        if q < pk:
            lo = max(lo, q + (pk-q)//2 + 30)
        elif q > pk:
            hi = min(hi, pk + (q-pk)//2 - 30)
    return lo, hi

def local_base(x, y, frac=0.30):
    n = len(x)
    k = max(2, int(n*frac)//2)
    edge = np.concatenate([np.arange(k), np.arange(n-k, n)])
    if len(edge) < 3 or (y[edge] <= 0).any():
        return None
    c = np.polyfit(x[edge], np.log(y[edge]), 1)
    return np.exp(np.polyval(c, x))

def asym_lorentz(x, c, gL, gR, A):
    return np.where(x <= c, A/(1+((x-c)/gL)**2), A/(1+((x-c)/gR)**2))

def fit_peak(lo, hi):
    m = (ells >= lo) & (ells <= hi)
    if m.sum() < 7:
        return None
    x, y = ells[m], D[m]
    # idx 對應 covTT 行 (純 TT 直接 0..214)
    idx = np.where(m)[0]
    Cw = covTT[np.ix_(idx, idx)] + np.eye(m.sum())*1e-12
    try:
        Cinv = np.linalg.inv(Cw)
    except np.linalg.LinAlgError:
        Cinv = np.linalg.pinv(Cw)
    basel = local_base(x, y)
    if basel is None:
        return None
    rr = y - basel
    i0 = np.argmax(rr)
    c0, a0 = x[i0], max(rr[i0], 1e-6)
    if a0 <= 0:
        return None
    best = None
    for c in np.linspace(max(c0-15, lo+5), min(c0+15, hi-5), 21):
        for gL in np.linspace(15, 100, 35):
            for gR in np.linspace(15, 100, 35):
                model = asym_lorentz(x, c, gL, gR, a0)
                r2 = rr - model
                chi2 = float(r2 @ Cinv @ r2)
                if best is None or chi2 < best[0]:
                    best = (chi2, c, gL, gR, a0)
    return best

print("="*72)
print("μK² cov χ² 不對稱 Lorentz fit (純 TT 215 bins + cov TT block)")
print("="*72)
results = {}
for m_, pk in PEAKS.items():
    lo, hi = window_lim(pk)
    res = fit_peak(lo, hi)
    if res is None:
        print(f"  峰 m={m_} ℓ={pk}: fit 失敗")
        continue
    c2, c, gL, gR, a0 = res
    results[m_] = (pk, c, gL, gR, c2)
    nm = int(((ells >= window_lim(pk)[0]) & (ells <= window_lim(pk)[1])).sum())
    print(f"  峰 m={m_} ℓ={pk}: c={c:.1f} γL={gL:.1f} γR={gR:.1f} "
          f"γR/γL={gR/gL:.2f} A={a0:.2f} χ²={c2:.1f} ({nm} pts)")

print("\n" + "="*72)
print("B. 峰形不對稱方向")
print("="*72)
if results:
    gLv = np.array([v[2] for v in results.values()])
    gRv = np.array([v[3] for v in results.values()])
    print(f"γL: {['%.0f'%v for v in gLv]}  平均 {gLv.mean():.1f}")
    print(f"γR: {['%.0f'%v for v in gRv]}  平均 {gRv.mean():.1f}")
    print(f"ratio γR/γL = {gRv.mean()/gLv.mean():.2f}")
    check("B1: 平均 γR>γL (右重)", gRv.mean() > gLv.mean(),
          f"γR={gRv.mean():.1f} γL={gLv.mean():.1f}")
    gmean = (gLv.mean()+gRv.mean())/2
    print(f"平均 γ = {gmean:.1f}")
    check("C1: γ ∈ (30, 55) (峰間隙/8=37.1, σ≈50)", 30 < gmean < 55,
          f"γ={gmean:.1f}")
    ms = sorted(results)
    gms = [(results[m][2]+results[m][3])/2 for m in ms]
    dg = np.diff(gms)
    print(f"γ by m: {['%.0f'%g for g in gms]}, diff {['%+.0f'%x for x in dg]}")
    check("D1: γ 大致遞增", sum(1 for x in dg if x > 0) >= len(dg)//2,
          f"{sum(1 for x in dg if x>0)}/{len(dg)} 正")

print("\n" + "="*72)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*72)
sys.exit(0 if FAIL == 0 else 1)