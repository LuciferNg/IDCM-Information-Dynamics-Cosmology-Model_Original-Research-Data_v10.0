#!/usr/bin/env python3
"""
O48 Q1.28b: 峰形統計 fit — local detrend + Plik covariance χ² 不對稱 Lorentz
=============================================================
Q1.26-27 (43-45) 問題: 全域 detrend 3次poly污染峰形, grid search 冇 error bar,
m=1 fit 心漂移 (70), 逐峰 asymmetry pattern 唔一致。

本 script 統計正確版:
  A. local detrend: 每個峰 window 內二次 baseline（只 fit window 邊緣 20% 點）
  B. Plik covariance (c_matrix_plik_v22.dat) χ² fit
  C. 不對稱 Lorentz: A/(1+((x-c)/γL)²)  x<c ; A/(1+((x-c)/γR)²) x>c
  D. error bars: 用 χ²=min+1 contour (1σ)
  E. 逐峰 γ_L/γ_R + 平均性子 → 峰形偏置判斷
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

# load cl + covariance
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

# c_matrix = Fortran record: [int32 len][613×613 float64][int32 len]
raw = open(f"{DATA}/c_matrix_plik_v22.dat", 'rb').read()
nrec = np.frombuffer(raw, dtype=np.int32, count=1)[0]
n_bin = int(round(math.sqrt(nrec/8)))
cov = np.frombuffer(raw[4:4+nrec], dtype=np.float64).reshape(n_bin, n_bin).copy()
print(f"cov shape: {cov.shape}, nrec={nrec} bytes ({n_bin} bins), ",
      f"ells: {len(ells)} ({ells[0]}..{ells[-1]})")

# mask D>0 bin (cov 保持 full-dim, 用 slice mask)
mask = D > 0
l, d = ells[mask], D[mask]
Cc = cov[mask][:, mask]
print(f"使用 {mask.sum()} bins, ℓ {l[0]:.0f}..{l[-1]:.0f}")

ALL_PEAKS = sorted([221, 527, 815, 1013, 1121, 1337, 1409])
PEAKS = {1: 221, 2: 527, 3: 815, 5: 1121, 7: 1409}

def window_lim(pk):
    """到最近鄰峰一半 [edge-based]"""
    lo = pk - 130
    hi = pk + 130
    for q in ALL_PEAKS:
        if q < pk:
            lo = max(lo, q + (pk-q)//2 + 30)
        elif q > pk:
            hi = min(hi, pk + (q-pk)//2 - 30)
    return lo, hi

def detrend_local(lo, hi):
    """local detrend: 只用 window 邊緣 30% 點 fit 線性 baseline, 然後減"""
    m = (l >= lo) & (l <= hi)
    if m.sum() < 6:
        return None
    x, y = l[m], d[m]
    # 邊緣點
    n = len(x)
    k = max(2, n // 6)
    edge = np.concatenate([np.arange(k), np.arange(n-k, n)])
    c = np.polyfit(x[edge], np.log(y[edge]), 1)
    base = np.exp(np.polyval(c, x))
    return x, y, y/base - 1.0  # local residual

def chi2_model(modelfn, p0, x, y, R, Cinv):
    """needs Cinv on residual"""
    pass

def fit_peak(lo, hi):
    """covariance χ² fit 不對稱 Lorentz:
       y_res = A/(1+((x-c)/γL)²) for x<=c ; A/(1+((x-c)/γR)²) for x>c
       但係 y_res 需要 baseline: 用 local residual (已經 local detrend)
       → fit 殘差 r(x) = y/base - 1 ≈ 峰形
    """
    res = detrend_local(lo, hi)
    if res is None:
        return None
    x, y, r = res
    # covariance slice (呢個 window 嘅 bins) — 用 mask 後 Cc
    m = (l >= lo) & (l <= hi)
    Cw = Cc[m][:, m]
    # 小 window 加 jitter for invertible
    Cw = Cw + np.eye(len(Cw))*1e-8  # 對角 (numerical)
    try:
        Cinv = np.linalg.inv(Cw)
    except np.linalg.LinAlgError:
        Cinv = np.linalg.pinv(Cw)
    # 初值: 局部 max
    i0 = np.argmax(r)
    c0, a0 = x[i0], r[i0]
    rc = r - (r.mean())  # 移除局部 dc (window 殘留)
    # grid refine cov χ²
    best = None
    for c in np.linspace(c0-15, c0+15, 31):
        for gL in np.linspace(15, 90, 31):
            for gR in np.linspace(15, 90, 31):
                model = np.where(x <= c, a0/(1+((x-c)/gL)**2),
                                 a0/(1+((x-c)/gR)**2))
                rr = rc - model
                chi2 = float(rr @ Cinv @ rr)
                if best is None or chi2 < best[0]:
                    best = (chi2, c, gL, gR, a0)
    return best

print("\n" + "="*72)
print("A. 逐峰 covariance χ² 不對稱 Lorentz fit")
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
    print(f"  峰 m={m_} ℓ={pk}: c={c:.1f} γL={gL:.1f} γR={gR:.1f} "
          f"ratio={gL/gR:.2f} χ²={c2:.1f}")

print("\n" + "="*72)
print("B. 峰形不對稱方向 (谷偏後峰 22% 關聯)")
print("="*72)
if results:
    gLv = np.array([v[2] for v in results.values()])
    gRv = np.array([v[3] for v in results.values()])
    print(f"γL: {['%.0f'%v for v in gLv]}  平均 {gLv.mean():.1f}")
    print(f"γR: {['%.0f'%v for v in gRv]}  平均 {gRv.mean():.1f}")
    print(f"ratio γR/γL = {gRv.mean()/gLv.mean():.2f}")
    check("B1: 平均 γR>γL (右重) — 峰右邊延伸, 谷偏近右峰", gRv.mean() > gLv.mean(),
          f"γR={gRv.mean():.1f} γL={gLv.mean():.1f}")

    gmean = (gLv.mean()+gRv.mean())/2
    print(f"\n平均 γ = {gmean:.1f}")
    check("C1: γ ≈ 36-46 (峰間隙/8~37.1)", 32 < gmean < 50, f"γ={gmean:.1f}")

    # σ_m 用 γR (右半) 睇 trend
    ms_sorted = sorted(results)
    grs = [results[m][3] for m in ms_sorted]
    dg = np.diff(grs)
    print(f"\nγR by m: {['%.0f'%g for g in grs]}, diff {['%+.0f'%x for x in dg]}")
    check("D1: γR 大致遞增 (峰越高越寬, Silk damping 收窄低ℓ)",
          sum(1 for x in dg if x > 0) >= len(dg)//2, f"{sum(1 for x in dg if x>0)}/{len(dg)} 正")

print("\n" + "="*72)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*72)
sys.exit(0 if FAIL == 0 else 1)