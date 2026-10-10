#!/usr/bin/env python3
"""
O48 Q1.29b: 峰形 joint fit v2 — μK² 空間 + bandpower bin 平均
=============================================================
Q1.29 錯誤: residual 空間 covariance 轉換 (Cr) 放大 scale (a=10-21, χ² 1.6e8)。
修正 (scripts/36 教訓三度應驗):
  - 全部 μK²: 模型 t(ℓ) = env(ℓ)·Σ Ap·shape(ℓ;γ), 用原 covariance C
  - Plik bandpower 係 bin 平均 (bin 寬 9) → 模型先做 uniform bin 平均
  - fit amplitude a ≈ 1 (O48 峰高公式應該自洽)

唯一自由參數 γ (共享峰寬), 峰位/峰高/谷位/谷深全閉合值。
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
raw = open(f"{DATA}/c_matrix_plik_v22.dat", 'rb').read()
nrec = np.frombuffer(raw, dtype=np.int32, count=1)[0]
cov = np.frombuffer(raw[4:4+nrec], dtype=np.float64).reshape(613, 613).copy()

mask = (D > 0) & (ells > 150) & (ells < 2500)
l, d = ells[mask], D[mask]
C = cov[mask][:, mask]

phi = (1+5**0.5)/2
F = lambda n: int(round((phi**n - (-phi)**(-n))/math.sqrt(5)))

PEAKS = np.array([221, 527, 815, 1121, 1409])
FALSE = np.array([1013, 1337])
V34 = np.array([221+0.75*306, 527+0.75*288, 815+0.75*306, 1121+0.75*288])

def peak_amp_frac(ell):
    eps = phi**(-1)/4
    j_of = {221: 0, 527: 1, 815: 2, 1121: 3, 1409: 4}
    if int(round(ell)) not in j_of:
        return 0.5
    j = j_of[int(round(ell))]
    geo = [1.0, 1.0/F(1), 1.0/F(2), 1.0/F(3), 1.0/F(4)][j]
    return 3*eps*geo*(33/34)*math.exp(-(ell/9055.0)**1.5)

# detrend env (log 3次, 全譜)
logD = np.log(d)
coef = np.polyfit(l, logD, 3)
env = np.exp(np.polyval(coef, l))
r = d - env  # μK² residual
Cinv = np.linalg.pinv(C + np.eye(len(C))*1e-8)

def shape_gauss(x, g):
    return np.exp(-0.5*(x/g)**2)

def shape_lorentz(x, g):
    return 1.0/(1.0 + (x/g)**2)

def frac_model(ells_arr, g, shape_fn, use_valley=True):
    """fractional 模型: Σ Ap·shape"""
    t = np.zeros_like(ells_arr, dtype=float)
    for p in PEAKS:
        t += peak_amp_frac(p)*shape_fn(ells_arr-p, g)
    for p in FALSE:
        t += 0.5*shape_fn(ells_arr-p, g)
    if use_valley:
        for v in V34:
            t -= 0.5*shape_fn(ells_arr-v, g)
    return t

def bin_average(ells_arr, model_frac, width=9.0):
    """uniform top-hat bin 平均: <model> over [l-w/2, l+w/2]"""
    out = np.zeros_like(ells_arr, dtype=float)
    xs = np.arange(ells_arr[0]-width, ells_arr[-1]+width, 0.5)
    frac = model_frac(xs)
    for i, c in enumerate(ells_arr):
        m = (xs >= c-width/2) & (xs <= c+width/2)
        out[i] = frac[m].mean()
    return out

def chi2_shape(g, shape_fn, use_valley=True):
    # 跟 scripts/36 成功框架:
    #   residual r = d − env (μK²), model t = env_x·frac (μK², bin 平均)
    #   tc = (t − mean)/std, fit a (μK²), χ² = (rr − a·tc)ᵀCinv(rr − a·tc)
    xs = np.arange(l[0]-10, l[-1]+10, 0.5)
    env_x = np.exp(np.polyval(coef, xs))
    frac_x = frac_model(xs, g, shape_fn, use_valley)
    T_x = env_x*frac_x          # μK² 峰模型 (不包 +1 基線!)
    Tb = np.array([T_x[(xs >= cc-4.5) & (xs <= cc+4.5)].mean() for cc in l])
    rr = r - r.mean()
    tc = (Tb - Tb.mean())/Tb.std()
    a = (tc @ Cinv @ rr) / (tc @ Cinv @ tc)
    res = rr - a*tc
    return float(res @ Cinv @ res), a

print("="*72)
print("A. 峰形 joint fit v2 — μK² + bin 平均 (共享 γ)")
print("="*72)
chi0 = float(d @ Cinv @ d)
print(f"null χ² = {chi0:.1f} (dof~{len(l)})")

gs = np.arange(15, 90, 2)
print("\nGauss:")
bestG = (1e18, None)
for g in gs:
    c2, a = chi2_shape(g, shape_gauss)
    if c2 < bestG[0]:
        bestG = (c2, g, a)
    if g in [30, 35, 40, 45, 50, 55]:
        print(f"  γ={g:3d}: χ²={c2:10.1f} Δχ²={chi0-c2:8.1f} a={a:.4f}")
print(f"  最佳 Gauss γ={bestG[1]} χ²={bestG[0]:.1f} a={bestG[2]:.4f}")

print("\nLorentz:")
bestL = (1e18, None)
for g in gs:
    c2, a = chi2_shape(g, shape_lorentz)
    if c2 < bestL[0]:
        bestL = (c2, g, a)
    if g in [30, 35, 40, 45, 50, 55]:
        print(f"  γ={g:3d}: χ²={c2:10.1f} Δχ²={chi0-c2:8.1f} a={a:.4f}")
print(f"  最佳 Lorentz γ={bestL[1]} χ²={bestL[0]:.1f} a={bestL[2]:.4f}")

print("\n" + "="*72)
print("B. 峰形族比較")
print("="*72)
dchi = bestG[0] - bestL[0]
print(f"Δχ²(G−L) = {dchi:+.1f} ({'Lorentz 勝' if dchi > 0 else 'Gauss 勝'})")
check("B1: 峰形族分辨 (|Δχ²|>6.6)", abs(dchi) > 6.6, f"|Δχ²|={abs(dchi):.1f}")

print("\n" + "="*72)
print("C. γ 結構身份")
print("="*72)
best_g = bestG[1] if bestG[0] < bestL[0] else bestL[1]
best_nm = "Gauss" if bestG[0] < bestL[0] else "Lorentz"
print(f"最佳 {best_nm} γ = {best_g}")
print(f"候選: 峰間隙/8=37.1, 297/8=37.1, 306/8=38.25, 288/8=36")
check("C1: γ ≈ 37.1±4 (峰間隙/8)", abs(best_g - 37.125) <= 4, f"γ={best_g} vs 37.1")

print("\n" + "="*72)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*72)
sys.exit(0 if FAIL == 0 else 1)