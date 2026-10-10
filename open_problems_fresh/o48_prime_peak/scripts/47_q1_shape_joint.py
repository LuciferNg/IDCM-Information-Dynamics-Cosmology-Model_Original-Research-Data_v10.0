#!/usr/bin/env python3
"""
O48 Q1.29: 峰形 joint fit — 全譜共享單一峰形寬度 γ (閉合級測試)
=============================================================
Q1.26-28 教訓: 逐峰獨立 fit 喺 Plik binning 下 over-parameterized
(fit 心漂走, A 收縮)。正確做法:
  - 固定峰位 (44N+s 鋸齒, 閉合) + 固定峰高 (A=3ε/F_j, 閉合)
  - 只剩 1 個自由參數: 共享峰形寬度 γ
  - covariance 正確轉到 residual 空間: C'_ij = C_ij/(env_i·env_j)

比較峰形族: Gauss, Lorentz, 混合? (掃 γ 計 full χ²)

峰 + 谷梳一齊用 (峰梳正 + 谷梳負, vdepth=½ 閉合), 谷位 V¾ 閉合
→ 唯一自由度 = 峰形寬度 γ (峰同谷共享同一寬度)

目標:
  A. 最佳 γ (全譜 covariance χ²)
  B. 峰形族比較: Gauss vs Lorentz (Δχ²)
  C. γ 結構身份: γ vs 峰間隙/8=37.1, vs 297/8, vs Q1.25 σ≈50
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

# 峰位/谷位閉合值 (零參數)
PEAKS = np.array([221, 527, 815, 1121, 1409])          # 真峰
FALSE = np.array([1013, 1337])                          # 假峰 (半高)
V34 = np.array([221+0.75*306, 527+0.75*288, 815+0.75*306, 1121+0.75*288])

def peak_amp_frac(ell):
    """峰高 (fractional, 閉合公式) — 喺 residual 空間用"""
    eps = phi**(-1)/4
    j_of = {221: 0, 527: 1, 815: 2, 1121: 3, 1409: 4}
    if int(round(ell)) not in j_of:
        return 0.5
    j = j_of[int(round(ell))]
    geo = [1.0, 1.0/F(1), 1.0/F(2), 1.0/F(3), 1.0/F(4)][j]
    return 3*eps*geo*(33/34)*math.exp(-(ell/9055.0)**1.5)

# detrend env (log 3次)
logD = np.log(d)
coef = np.polyfit(l, logD, 3)
env = np.exp(np.polyval(coef, l))
r = d - env                      # μK² residual
Cinv = np.linalg.pinv(C + np.eye(len(C))*1e-12)

def shape_gauss(x, g):
    return np.exp(-0.5*(x/g)**2)

def shape_lorentz(x, g):
    return 1.0/(1.0 + (x/g)**2)

def model_t(ells_arr, g, shape_fn, use_valley=True):
    t = np.zeros_like(ells_arr, dtype=float)
    for p in PEAKS:
        t += peak_amp_frac(p)*env  # 峰 (μK²): frac × env
    return t  # placeholder 唔啱 — 峰模型要乘 env? 峰 frac 對應 r/env

def model_residual(ells_arr, g, shape_fn, use_valley=True):
    """residual 空間模型: r/env = Σ Ap·shape + 谷"""
    t = np.zeros_like(ells_arr, dtype=float)
    for p in PEAKS:
        t += peak_amp_frac(p)*shape_fn(ells_arr-p, g)
    for p in FALSE:
        t += 0.5*shape_fn(ells_arr-p, g)
    if use_valley:
        for v in V34:
            t -= 0.5*shape_fn(ells_arr-v, g)
    return t

rn = r/env  # fractional residual (dimensionless)
# covariance 轉 residual 空間: C'_ij = C_ij/(env_i env_j)
Cr = C / np.outer(env, env)
Cr_inv = np.linalg.pinv(Cr + np.eye(len(Cr))*1e-8)

def chi2_shape(g, shape_fn, use_valley=True):
    t = model_residual(l, g, shape_fn, use_valley)
    # 唯一 fit: 整體 amplitude scale a
    tc = t  # 唔減 mean — 模型係絕對 fractional
    a = (tc @ Cr_inv @ rn) / (tc @ Cr_inv @ tc)
    res = rn - a*tc
    return float(res @ Cr_inv @ res), a

print("="*72)
print("A. 峰形 joint fit — 共享寬度 γ (covariance, residual 空間)")
print("="*72)
chi0 = float(rn @ Cr_inv @ rn)
print(f"null χ² = {chi0:.1f} (dof~{len(l)})")

gs = np.arange(15, 90, 2)
print("\nGauss 峰形:")
bestG = (1e18, None)
for g in gs:
    c2, a = chi2_shape(g, shape_gauss)
    if c2 < bestG[0]:
        bestG = (c2, g, a)
    if g in [30, 35, 40, 45, 50, 55, 60]:
        print(f"  γ={g:3d}: χ²={c2:10.1f} Δχ²={chi0-c2:8.1f} a={a:.3f}")
print(f"  最佳 Gauss γ={bestG[1]} χ²={bestG[0]:.1f} (Δχ²={chi0-bestG[0]:.1f})")

print("\nLorentz 峰形:")
bestL = (1e18, None)
for g in gs:
    c2, a = chi2_shape(g, shape_lorentz)
    if c2 < bestL[0]:
        bestL = (c2, g, a)
    if g in [30, 35, 40, 45, 50, 55, 60]:
        print(f"  γ={g:3d}: χ²={c2:10.1f} Δχ²={chi0-c2:8.1f} a={a:.3f}")
print(f"  最佳 Lorentz γ={bestL[1]} χ²={bestL[0]:.1f} (Δχ²={chi0-bestL[0]:.1f})")

print("\n" + "="*72)
print("B. 峰形族比較")
print("="*72)
dchi = bestG[0] - bestL[0]
print(f"Gauss(γ={bestG[1]}) χ²={bestG[0]:.1f} vs Lorentz(γ={bestL[1]}) χ²={bestL[0]:.1f}")
print(f"Δχ²(G−L) = {dchi:+.1f} ({'Lorentz 勝' if dchi > 0 else 'Gauss 勝'})")
check("B1: 峰形族分辨 (|Δχ²|>6.6)", abs(dchi) > 6.6, f"|Δχ²|={abs(dchi):.1f}")

print("\n" + "="*72)
print("C. γ 結構身份")
print("="*72)
best_g = bestG[1] if bestG[0] < bestL[0] else bestL[1]
best_name = "Gauss" if bestG[0] < bestL[0] else "Lorentz"
print(f"最佳 {best_name} γ = {best_g}")
print(f"候選: 峰間隙/8=37.1, 297/8=37.1, 306/8=38.25, 288/8=36, Q1.25 σ≈50")
check("C1: γ ≈ 37.1±3 (峰間隙/8)", abs(best_g - 37.125) <= 3, f"γ={best_g} vs 37.1")

print("\n" + "="*72)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*72)
sys.exit(0 if FAIL == 0 else 1)