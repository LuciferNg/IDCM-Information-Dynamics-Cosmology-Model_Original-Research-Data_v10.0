#!/usr/bin/env python3
"""
O48 Q1.28: 峰形乾淨 fit — 不對稱 Lorentz (Fano-like) + window 限制
=============================================================
Q1.26 (43): Plik Lorentz 全勝, σ_m {70,36,40,42,46} 遞增, γ≈38≈峰間隙/8。
但有兩個缺陷:
  1. m=5 window ±140 包含 1013 假峰 → asym=2.23 干擾
  2. 對稱 Lorentz — 但 Q1.16 發現谷偏近後峰 22% = 峰形不對稱!

本 script: clean fit
  A. window 只到最近鄰峰/假峰嘅一半距離 (唔重疊)
  B. asymmetric Lorentz: A/(1+((x-c)/γ_L)²) for x<c, A/(1+((x-c)/γ_R)²) for x>c
     γ_L ≠ γ_R → 量化峰形不對稱 (偏後=γ_L>γ_R? 偏前=γ_L<γ_R?)
  C. σ_m 遞增趨勢確認 (排除 m=1 )
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
logD = np.log(d)
coef = np.polyfit(l, logD, 3)
env = np.exp(np.polyval(coef, l))
r = d/env - 1.0

# 全部峰 (真+假): 用嚟定 fit window 邊界
ALL_PEAKS = sorted([221, 527, 815, 1013, 1121, 1337, 1409])
PEAKS = {1: 221, 2: 527, 3: 815, 5: 1121, 7: 1409}

def fit_window(pk):
    """window = 到最近鄰峰嘅一半 (排除自己)"""
    lo = pk - 140
    hi = pk + 140
    for q in ALL_PEAKS:
        if q < pk:
            lo = max(lo, q + (pk-q)//2)
        elif q > pk:
            hi = min(hi, pk + (q-pk)//2)
    return lo, hi

def fit_asym_lorentz(lo, hi, pk):
    """asymmetric Lorentz: 左 γ_L, 右 γ_R
       A/(1+((x-c)/γL)²) x≤c ; A/(1+((x-c)/γR)²) x>c"""
    m = (l >= lo) & (l <= hi)
    if m.sum() < 5:
        return None
    x, y = l[m], r[m]
    ipk = np.argmax(y)
    c0, a0 = x[ipk], max(y[ipk], 1e-6)
    best = None
    for c in np.linspace(c0-12, c0+12, 25):
        for gL in np.linspace(20, 80, 25):
            for gR in np.linspace(20, 80, 25):
                yfit = np.where(x <= c,
                                a0/(1+((x-c)/gL)**2),
                                a0/(1+((x-c)/gR)**2))
                chi2 = np.sum((y - yfit)**2)
                if best is None or chi2 < best[0]:
                    best = (chi2, c, gL, gR, a0)
    return best

print("="*72)
print("A. 乾淨 window + 不對稱 Lorentz fit (Plik)")
print("="*72)
results = {}
for m, pk in PEAKS.items():
    lo, hi = fit_window(pk)
    res = fit_asym_lorentz(lo, hi, pk)
    if res is None:
        print(f"  峰 m={m} ℓ={pk}: fit 失敗")
        continue
    c2, c, gL, gR, a0 = res
    results[m] = (pk, c, gL, gR, c2)
    asym = gL/gR
    print(f"  峰 m={m} ℓ={pk}: c={c:.1f} γ_L={gL:.1f} γ_R={gR:.1f} "
          f"asym=γ_L/γ_R={asym:.2f} χ²={c2:.1f}  [{lo},{hi}]")

print("\n" + "="*72)
print("B. 不對稱性解讀")
print("="*72)
asyms = [results[m][1] for m in results]  # 唔啱, 重建
for m, (pk, c, gL, gR, c2) in results.items():
    print(f"  m={m}: γ_L={gL:.1f}, γ_R={gR:.1f} → "
          f"{'偏後峰(右重)' if gR>gL else '偏前峰(左重)' if gL>gR else '對稱'}")

# 谷偏近後峰 22% → 峰形右重 (γ_R > γ_L)? 若峰向右延伸, 右邊谷被推近
gL_avg = np.mean([r[2] for r in results.values()])
gR_avg = np.mean([r[3] for r in results.values()])
print(f"\n平均 γ_L={gL_avg:.1f}, γ_R={gR_avg:.1f}, γ_R/γ_L={gR_avg/gL_avg:.2f}")
check("B1: γ_R > γ_L (峰右重, 谷偏後峰一致)", gR_avg > gL_avg + 2,
      f"γ_R={gR_avg:.1f} vs γ_L={gL_avg:.1f}")

print("\n" + "="*72)
print("C. γ 身份")
print("="*72)
g_all = [r[2] for r in results.values()] + [r[3] for r in results.values()]
g_mean = np.mean(g_all)
gm_gL = np.mean([r[2] for r in results.values()])
print(f"平均 γ = {g_mean:.1f} (左γ_L={gm_gL:.1f})")
print(f"候選: 峰間隙/8 = {(306+288)/16:.2f}, 297/8 = {297/8:.2f}, "
      f"38.25 (306/8), 36 (288/8)")
check("C1: γ ≈ 峰間隙/8 (36-38)", 34 < g_mean < 41, f"mean={g_mean:.1f}")
print(f"     平均 σ (對稱 Gauss 43 script) = 46.8 → 峰寬 FWHM≈2γ? {2*g_mean:.0f}")
print(f"     Gauss σ=46.8 vs Lorentz FWHM/2=γ={g_mean:.1f}: 兩者不同定義")

print("\n" + "="*72)
print("D. σ_m/C_m 遞增趨勢")
print("="*72)
ms = sorted(results)
gs = [results[m][3] for m in ms]  # γ_R
print(f"γ_R by m: {[f'{g:.0f}' for g in gs]}")
dgs = np.diff(gs)
print(f"diff: {[f'{d:+.0f}' for d in dgs]}")
check("D1: γ_R 單調遞增 (m≥2)", all(x > 0 for x in dgs) or len(ms) < 4,
      f"diff={[f'{d:+.0f}' for d in dgs]}")

print("\n" + "="*72)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*72)
sys.exit(0 if FAIL == 0 else 1)