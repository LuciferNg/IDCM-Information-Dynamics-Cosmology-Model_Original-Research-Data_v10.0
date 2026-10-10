#!/usr/bin/env python3
"""
O48 Q1.30: 峰形 joint MLE — 平滑背景 + 峰梳 + 谷梳 一次過 fit
=============================================================
47b 問題: detrend-then-fit 嘅背景誤差污染 χ²。正路 (統計正當):
  D_model(l) = B(l; knots) + Σ_p A_p·shape(l−p; γ) + 谷梳
  B = 線性插值 spline (knots 喺峰谷之間) — 自由 knots 值
  峰位/峰高/谷位/谷深 = 閉合值; 自由參數 = knots(8) + γ(1) + scale(1)
  μK² (C_ℓ) covariance χ²

Plik-lite 第二欄 = C_ℓ (μK²), cov 對應 C_ℓ — 單位齊。
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
l, dd = ells[mask], D[mask]
C = cov[mask][:, mask] + np.eye(mask.sum())*1e-10
Cinv = np.linalg.pinv(C)

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

def shape_gauss(x, g):
    return np.exp(-0.5*(x/g)**2)

def shape_lorentz(x, g):
    return 1.0/(1.0 + (x/g)**2)

# knots: 峰谷之間 (6 段) + 邊緣
KNOTS = np.array([150, 370, 660, 950, 1240, 1460, 2000, 2500])

def base_spline(x, knot_vals):
    """線性插值背景"""
    return np.interp(x, KNOTS, knot_vals)

def frac_peaks(x, g, shape_fn, use_valley=True):
    t = np.zeros_like(x, dtype=float)
    for p in PEAKS:
        t += peak_amp_frac(p)*shape_fn(x-p, g)
    for p in FALSE:
        t += 0.5*shape_fn(x-p, g)
    if use_valley:
        for v in V34:
            t -= 0.5*shape_fn(x-v, g)
    return t

def model_full(x, g, knot_vals, shape_fn, scale, use_valley=True):
    return base_spline(x, knot_vals) + scale*frac_peaks(x, g, shape_fn, use_valley)

def fit_shape(g, shape_fn, use_valley=True):
    """joint MLE: knots (8) + scale (1) fit at fixed γ → min χ²"""
    # 設計矩陣: [spline basis (8)] + [peak model (1)]
    A = np.zeros((len(l), len(KNOTS)+1))
    for i, k in enumerate(KNOTS):
        A[:, i] = np.interp(l, KNOTS, np.array([1.0 if j == i else 0.0 for j in range(len(KNOTS))]))
    A[:, -1] = frac_peaks(l, g, shape_fn, use_valley)
    # 廣義最小二乘: θ = (AᵀC⁻¹A)⁻¹AᵀC⁻¹d
    Ac = Cinv @ A
    lhs = A.T @ Ac
    rhs = A.T @ (Cinv @ dd)
    try:
        theta = np.linalg.solve(lhs, rhs)
    except np.linalg.LinAlgError:
        theta = np.linalg.lstsq(lhs, rhs, rcond=None)[0]
    resid = dd - A @ theta
    chi2 = float(resid @ Cinv @ resid)
    scale = theta[-1]
    return chi2, scale, theta[:-1]

print("="*72)
print("A. 峰形 joint MLE (knots 背景 + 峰梳 + 谷梳, C_ℓ cov)")
print("="*72)
dof = len(l) - (len(KNOTS)+1)
# 真 null: knots-only fit
A0 = np.zeros((len(l), len(KNOTS)))
for i, k in enumerate(KNOTS):
    A0[:, i] = np.interp(l, KNOTS, np.array([1.0 if j == i else 0.0 for j in range(len(KNOTS))]))
Ac0 = Cinv @ A0
th0 = np.linalg.solve(A0.T @ Ac0, A0.T @ (Cinv @ dd))
res0 = dd - A0 @ th0
chi0 = float(res0 @ Cinv @ res0)
print(f"null (背景 only) χ² = {chi0:.1f} (dof={len(l)-len(KNOTS)})")

gs = np.arange(20, 90, 2)
print("\nGauss:")
bestG = (1e18, None)
for g in gs:
    chi2, sc, _ = fit_shape(g, shape_gauss)
    if chi2 < bestG[0]:
        bestG = (chi2, g, sc)
    if g in [30, 35, 40, 45, 50, 55]:
        print(f"  γ={g:3d}: χ²={chi2:10.1f} Δχ²={chi0-chi2:8.1f} scale={sc:.3f}")
print(f"  最佳 Gauss γ={bestG[1]} χ²={bestG[0]:.1f} Δχ²={chi0-bestG[0]:.1f}")

print("\nLorentz:")
bestL = (1e18, None)
for g in gs:
    chi2, sc, _ = fit_shape(g, shape_lorentz)
    if chi2 < bestL[0]:
        bestL = (chi2, g, sc)
    if g in [30, 35, 40, 45, 50, 55]:
        print(f"  γ={g:3d}: χ²={chi2:10.1f} Δχ²={chi0-chi2:8.1f} scale={sc:.3f}")
print(f"  最佳 Lorentz γ={bestL[1]} χ²={bestL[0]:.1f} Δχ²={chi0-bestL[0]:.1f}")

print("\n" + "="*72)
print("B. 峰形族比較")
print("="*72)
dchi = bestG[0] - bestL[0]
print(f"Δχ²(G−L) = {dchi:+.1f} ({'Lorentz 勝' if dchi > 0 else 'Gauss 勝'})")
check("B1: 峰形族分辨 (|Δχ²|>6.6)", abs(dchi) > 6.6, f"|Δχ²|={abs(dchi):.1f}")
print(f"null→峰梳改善: Δχ²(G)={chi0-bestG[0]:.1f}, Δχ²(L)={chi0-bestL[0]:.1f}")
check("B2: 峰梳 vs null 顯著 (Δχ²≫6.6)", chi0 - min(bestG[0], bestL[0]) > 6.6,
      f"Δχ²={chi0-min(bestG[0],bestL[0]):.1f}")

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
print(f"dof = {dof}")
print("="*72)
sys.exit(0 if FAIL == 0 else 1)