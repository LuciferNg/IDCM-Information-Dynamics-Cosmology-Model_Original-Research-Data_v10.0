#!/usr/bin/env python3
"""
O76/23: 獨立重算驗證 — 從零核對記錄文檔所有數字
================================================================
唔用舊 code, 從第一性原理重算所有 O76 聲稱:

1. ℓ 身份: log₄(1+z) 喺 z=1,2,3,17
2. D_A(ℓ) 公式 + C=-0.1697
3. D_L = (1+z)^{1-n/p}·D_A
4. Nyquist 自洽: D_app(ℓ_nyq)/πR
5. H_eff(0) = c/R_world
6. DESI χ² 重算
7. α fit 重算 (用最小化)
8. Pantheon+ χ² 重算 (IDCM vs ΛCDM)
"""
import numpy as np
import math
import json
from scipy import optimize

PASS = 0
FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ PASS: {name}")
    else:
        FAIL += 1
        print(f"  ❌ FAIL: {name}")
    if detail:
        print(f"    {detail}")

print("=" * 70)
print("O76/23: 獨立重算驗證 (從零)")
print("=" * 70)

# ============ 1. 基本常數 ============
C_LIGHT = 299792.458
R_WORLD = 4129.94
PHI = (1 + math.sqrt(5)) / 2
OMEGA_RING = 72.59
N_D = 44

# ============ 2. ℓ 身份 ============
print("\n--- 1. ℓ = log₄(1+z) ---")
ell_1 = math.log(2, 4)
ell_3 = math.log(4, 4)
ell_17 = math.log(18, 4)
check("z=1 → ℓ=0.5", abs(ell_1 - 0.5) < 1e-9, f"{ell_1:.10f}")
check("z=3 → ℓ=1.0", abs(ell_3 - 1.0) < 1e-9, f"{ell_3:.10f}")
print(f"  z=17 → ℓ = {ell_17:.4f} (Nyquist)")
check("z=17 → ℓ=2.085", abs(ell_17 - 2.0850) < 0.001, f"{ell_17:.4f}")

# ============ 3. n/p = γ₇/γ₂₀ ============
print("\n--- 2. n/p = γ₇/γ₂₀ ---")
g7 = 4*math.sin(7*math.pi/88)**2
g20 = 4*math.sin(20*math.pi/88)**2
np_ratio = g7/g20
print(f"  γ₇ = {g7:.6f}, γ₂₀ = {g20:.6f}")
print(f"  n/p = {np_ratio:.6f}")
check("n/p = 0.14262 (O13)", abs(np_ratio - 0.14262) < 0.001, f"{np_ratio:.6f}")

# ============ 4. D_A(ℓ) 公式 ============
print("\n--- 3. D_A(ℓ) 公式 ---")
C_DELAY = -0.1697
def d_app(ell, C=C_DELAY):
    base = R_WORLD * (1 - 4**(-ell))
    proj = 1 + 2*PHI**(-1)*ell
    delta = C * (ell - 0.5) * (1 - 4**(-ell))
    return base * (proj + delta)

# 已知點: z=0.5 → D=1890.5, z=1 → 3341.2, z=2 → 5359.2 (script 01)
d05 = d_app(math.log(1.5, 4))
d1 = d_app(math.log(2, 4))
d2 = d_app(math.log(3, 4))
print(f"  D_A(ℓ=0.2925) = {d05:.1f} (記錄: 1890.5)")
print(f"  D_A(ℓ=0.5)    = {d1:.1f} (記錄: 3341.2)")
print(f"  D_A(ℓ=0.7925) = {d2:.1f} (記錄: 5359.2)")
check("D_A(z=0.5) = 1890.5", abs(d05 - 1890.5) < 1.0, f"{d05:.1f}")
check("D_A(z=1) = 3341.2", abs(d1 - 3341.2) < 1.0, f"{d1:.1f}")
check("D_A(z=2) = 5359.2", abs(d2 - 5359.2) < 1.0, f"{d2:.1f}")

# ============ 5. H_eff(0) ============
print("\n--- 4. H_eff(0) = c/R_world ---")
H0 = C_LIGHT / R_WORLD
print(f"  c/R_world = {H0:.4f}")
check("H_eff(0) = 72.59", abs(H0 - OMEGA_RING) < 0.01, f"{H0:.4f}")

# ============ 6. Nyquist 自洽 ============
print("\n--- 5. Nyquist 自洽 ---")
D_nyq = d_app(ell_17)
piR = math.pi * R_WORLD
ratio = D_nyq / piR
print(f"  D_app(ℓ_nyq) = {D_nyq:.1f}")
print(f"  πR_world = {piR:.1f}")
print(f"  比 = {ratio:.4f}")
check("D_app(ℓ_nyq) ≈ πR (0.9990)", abs(ratio - 0.9990) < 0.001, f"{ratio:.4f}")

# ============ 7. 載入 Pantheon+ ============
print("\n--- 6. Pantheon+ 載入 ---")
data_path = 'data/pantheon/Pantheon+SH0ES.dat'
cov_path = 'data/pantheon/Pantheon+SH0ES_STAT+SYS.cov'
with open(data_path) as f:
    header = f.readline().split()
col = {name: i for i, name in enumerate(header)}
zs, mb = [], []
with open(data_path) as f:
    f.readline()
    for line in f:
        parts = line.split()
        if len(parts) < len(header): continue
        zs.append(float(parts[col['zCMB']]))
        mb.append(float(parts[col['m_b_corr']]))
zs = np.array(zs); mb = np.array(mb)
N = len(zs)
with open(cov_path) as f:
    n_dim = int(f.readline().strip())
cov = np.loadtxt(cov_path, skiprows=1).reshape(n_dim, n_dim)
cov_inv = np.linalg.inv(cov)
check("1701 SNe", N == 1701, f"N={N}")

def fit_M(mu_model):
    J = np.ones(N)
    return (J @ cov_inv @ (mb - mu_model)) / (J @ cov_inv @ J)

# ============ 8. IDCM χ² (α=-n/p) ============
print("\n--- 7. IDCM χ² (零參數) ---")
ell_arr = np.log(1+zs)/np.log(4)
Da = d_app(ell_arr)
DL_idcm = (1+zs)**(1-np_ratio) * Da
mu_idcm0 = 5*np.log10(DL_idcm*1e6/10)
M_idcm = fit_M(mu_idcm0)
chi2_idcm = (mb - (mu_idcm0+M_idcm)) @ cov_inv @ (mb - (mu_idcm0+M_idcm))
print(f"  M = {M_idcm:.4f}")
print(f"  χ² = {chi2_idcm:.1f}")
check("IDCM χ² = 2006.8", abs(chi2_idcm - 2006.8) < 1.0, f"{chi2_idcm:.1f}")

# ============ 9. ΛCDM χ² ============
print("\n--- 8. ΛCDM Planck χ² ---")
def dc_lcdm(z, H0, Om):
    zz = np.geomspace(1e-6, max(z, 1e-4), 2000)
    E = np.sqrt(Om*(1+zz)**3 + (1-Om))
    return C_LIGHT/H0 * np.trapezoid(1/E, zz)
mu_lcdm_p = 5*np.log10((1+zs)*np.array([dc_lcdm(zi, 67.4, 0.315) for zi in zs])*1e6/10)
M_lp = fit_M(mu_lcdm_p)
chi2_lp = (mb - (mu_lcdm_p+M_lp)) @ cov_inv @ (mb - (mu_lcdm_p+M_lp))
print(f"  χ² = {chi2_lp:.1f}")
check("ΛCDM χ² = 2002.1", abs(chi2_lp - 2002.1) < 1.0, f"{chi2_lp:.1f}")
delta = chi2_idcm - chi2_lp
print(f"  Δχ² = {delta:+.1f}")
check("Δχ² = +4.7", abs(delta - 4.7) < 0.5, f"{delta:+.1f}")

# ============ 10. DESI χ² ============
print("\n--- 9. DESI BAO χ² ---")
rd_idcm = math.pi * R_WORLD / 88 * 420/421
desi = [
    ('LRG1', 0.510, 13.588, 0.167),
    ('LRG2', 0.706, 17.351, 0.177),
    ('LRG3+ELG', 0.934, 21.576, 0.152),
    ('ELG2', 1.321, 27.601, 0.318),
    ('Lyα', 2.330, 38.988, 0.531),
]
chi2_d = 0
for name, z, obs, err in desi:
    ell = math.log(1+z, 4)
    pred = d_app(ell)/rd_idcm
    chi2_d += ((pred-obs)/err)**2
print(f"  χ² = {chi2_d:.2f}")
check("DESI χ² = 12.82", abs(chi2_d - 12.82) < 0.1, f"{chi2_d:.2f}")

# ============ 11. α fit 重算 ============
print("\n--- 10. α fit 重算 ---")
def loss(params):
    alpha, M = params
    DL = (1+zs)**(1+alpha) * Da
    mu = M + 5*np.log10(DL*1e6/10)
    return (mb - mu) @ cov_inv @ (mb - mu)
best = None
for a0 in [-0.2, -0.15, -0.1, -0.05]:
    r = optimize.minimize(loss, [a0, -19.3], method='Nelder-Mead',
                          options={'maxiter': 400, 'xatol': 1e-8, 'fatol': 1e-3})
    if best is None or r.fun < best.fun:
        best = r
alpha_fit, M_fit = best.x
chi2_min = best.fun
print(f"  α_fit = {alpha_fit:.6f} (記錄: -0.1377)")
print(f"  χ²_min = {chi2_min:.1f}")
check("α_fit ≈ -0.1377", abs(alpha_fit - (-0.1377)) < 0.002, f"{alpha_fit:.6f}")
check("χ²_min = 2006.7", abs(chi2_min - 2006.7) < 1.0, f"{chi2_min:.1f}")

# ============ 12. 分 bin 殘差 ============
print("\n--- 11. 分 bin 殘差 (α=-n/p) ---")
resid = mb - (mu_idcm0 + M_idcm)
bins = [(0, 0.05), (0.05, 0.1), (0.1, 0.2), (0.2, 0.3), (0.3, 0.5), (0.5, 0.8)]
all_ok = True
for lo, hi in bins:
    m = (zs >= lo) & (zs < hi)
    if m.sum() < 3: continue
    r = resid[m].mean()
    ok = abs(r) < 0.05
    all_ok &= ok
    print(f"  {lo:.2f}-{hi:.2f}: N={m.sum():<4} <resid>={r:+.4f} {'✅' if ok else '❌'}")
check("全部 z<0.8 殘差 <0.05", all_ok)

# ============ 總結 ============
print(f"\n{'=' * 70}")
print(f"獨立重算: PASS={PASS} FAIL={FAIL}")
print(f"{'=' * 70}")
result = {
    'n_p': round(float(np_ratio), 6),
    'alpha_fit': round(float(alpha_fit), 6),
    'chi2_idcm': round(float(chi2_idcm), 1),
    'chi2_lcdm': round(float(chi2_lp), 1),
    'delta_chi2': round(float(delta), 1),
    'chi2_desi': round(float(chi2_d), 2),
    'nyquist_ratio': round(float(ratio), 4),
    'pass': PASS, 'fail': FAIL
}
with open('data/23_independent_recheck.json', 'w') as f:
    json.dump(result, f, indent=2)
print(f"-> data/23_independent_recheck.json")
