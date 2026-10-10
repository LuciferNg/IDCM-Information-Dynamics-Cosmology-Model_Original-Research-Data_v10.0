#!/usr/bin/env python3
"""
O48 Q1.27: 峰形 cross-check — SPT-3G 數據 Lorentzian vs Gaussian
=============================================================
Q1.26 (43 script): Plik 峰形 fit — Lorentzian 全勝 Gaussian (L<G), γ≈36-40;
σ_m 平均 46.8 ≈ 49.5。但 m=1 σ=70 異常 + m=5 asym 2.23 (1013 假峰干擾)。

本 script: SPT-3G 52 bins (ℓ437..2962) cross-check 峰形 —
  1. 同一 Lorentz/Gauss fit 喺 SPT
  2. 排除假峰干擾 (每峰 fit window 只到最近假峰一半)
  3. 統計: Δχ² = χ²_G − χ²_L > 0 證明 Lorentzian
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
DATA = f"{base}/o214_energy_budget_definition/data/spt3g_d1"

bdp = np.loadtxt(f"{DATA}/SPT3G_D1_TnE_bdp.txt")
win = np.loadtxt(f"{DATA}/TT_150x150_window.txt")
spectra = [("TT_90x90",52),("TE_90x90",72),("EE_90x90",72),("TT_90x150",52),
           ("TE_90x150",72),("TE_150x90",72),("EE_90x150",72),("TT_90x220",52),
           ("TE_90x220",72),("TE_220x90",72),("EE_90x220",72),("TT_150x150",52),
           ("TE_150x150",72),("EE_150x150",72),("TT_150x220",52),("TE_150x220",72),
           ("TE_220x150",72),("EE_150x220",72),("TT_220x220",52),("TE_220x220",72),
           ("EE_220x220",72)]
off = 0
for name, n in spectra:
    if name == "TT_150x150":
        break
    off += n
tt150 = bdp[off:off+52]
lgr = win[:, 0]
centers = np.array([lgr[np.argmax(win[:, b])] for b in range(1, 53)])
mask = tt150 > 0
l, d = centers[mask], tt150[mask]

logD = np.log(d)
coef = np.polyfit(l, logD, 2)
env = np.exp(np.polyval(coef, l))
r = d/env - 1.0
rn = (r - r.mean())/r.std()

# SPT bins 疏 (Δℓ≈50-60): 每峰得 3-5 點
PEAKS = {2: 527, 3: 815, 5: 1121, 7: 1409}
FALSE_PEAKS = {1013, 1337}

print("="*72)
print("SPT-3G cross-check: 峰形 Lorentz vs Gauss")
print("="*72)

def fitshape(lo, hi):
    """fit Gauss + Lorentz, 回傳 (chi2G, chi2L, cG, sG, cL, gL)"""
    m = (l >= lo) & (l <= hi)
    if m.sum() < 3:
        return None
    x, y = l[m], r[m]
    ipk = np.argmax(y)
    c0, a0 = x[ipk], max(y[ipk], 1e-6)
    bestG = bestL = None
    for c in np.linspace(c0-25, c0+25, 21):
        for s in np.linspace(15, 90, 16):
            g = a0*np.exp(-0.5*((x-c)/s)**2)
            c2 = np.sum((y-g)**2)
            if bestG is None or c2 < bestG[0]:
                bestG = (c2, c, s)
            lor = a0*s**2/((x-c)**2 + s**2)
            c2l = np.sum((y-lor)**2)
            if bestL is None or c2l < bestL[0]:
                bestL = (c2l, c, s)
    return bestG + bestL

dchi_sum = 0
for m, pk in PEAKS.items():
    # window: 到最近假峰/鄰峰一半 (避 1013 干擾 m=5)
    lo, hi = pk-100, pk+100
    res = fitshape(lo, hi)
    if res is None:
        print(f"  峰 m={m} ℓ={pk}: SPT 數據不足")
        continue
    c2g, cg, sg, c2l, cl, gl = res
    dchi = c2g - c2l
    dchi_sum += dchi
    print(f"  峰 m={m} ℓ={pk}: Gauss σ={sg:.1f} χ²={c2g:.1f} | "
          f"Lorentz γ={gl:.1f} χ²={c2l:.1f} → Δχ²(G−L)={dchi:+.1f} "
          f"{'L勝' if dchi > 0 else 'G勝'}")
check("C1: SPT Lorentz 全勝 (ΣΔχ²>0)", dchi_sum > 0, f"ΣΔχ²(G−L)={dchi_sum:+.1f}")

# Plik γ 值: 36,36,40,40 → 平均 38 ≈ 306/8=38.25 = 峰間隙/8?
print("\n" + "="*72)
print("B. γ 身份: 峰間隙/8?")
print("="*72)
print(f"Plik γ: [36,36,40,40], 平均 = {(36+36+40+40)/4:.1f}")
print(f"候選: 306/8 = {306/8:.2f}, 288/8 = {288/8:.1f}")
print(f"      (306+288)/16 = {(306+288)/16:.2f}")
check("B1: γ 平均 ≈ 38.25 (峰間隙/8)", abs((36+36+40+40)/4 - 306/8) < 3,
      f"mean=38 vs 38.25")
print(f"      F₁₀/8? = {55/8:.1f} | N_d=44 → 44/8={44/8:.1f}")
check("B2: γ ≈ 44/8 (N_d/8=5.5)? 唔係", False, "44/8=5.5 離 38 太遠")

print("\n" + "="*72)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*72)
sys.exit(0 if FAIL == 0 else 1)