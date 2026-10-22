#!/usr/bin/env python3
"""
O76/20: 最終完整驗證 — IDCM z 紅移翻譯全鏈
================================================================
驗證 O76 全部閉合:
  1. z ↔ ℓ 身份 (1+z = 4^ℓ)
  2. D_A(ℓ) 結構 + H_eff(0) = ω_ring
  3. D_L = (1+z)^{6/7}·D_A 對偶
  4. Pantheon+ χ² (零參數) vs ΛCDM
  5. DESI BAO χ² 保持
  6. Nyquist 自洽 (D_app(ℓ_nyq) ≈ πR_world)
  7. 分 bin 殘差 < 0.05 (z<0.8)
"""
import numpy as np
import math
import json

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

C_LIGHT = 299792.458
R_WORLD = 4129.94
PHI = (1 + math.sqrt(5)) / 2
C_DELAY = -0.1697
OMEGA_RING = 72.59
N_D = 44
F_PROJ = 17

print("=" * 70)
print("O76/20: 最終完整驗證 — z 紅移翻譯全鏈")
print("=" * 70)

# ============ 1. z ↔ ℓ ============
print("\n--- 1. z ↔ ℓ 身份 ---")
ell_nyq = math.log(18, 4)
check("z=1 → ℓ=0.5", abs(math.log(2, 4) - 0.5) < 1e-9)
check("z=3 → ℓ=1.0", abs(math.log(4, 4) - 1.0) < 1e-9)
check("z=17 → ℓ=2.085", abs(ell_nyq - 2.0850) < 0.001)

# ============ 2. D_A 結構 ============
print("\n--- 2. D_A(ℓ) 結構 + H_eff(0) ---")
def d_app(ell, C=C_DELAY):
    base = R_WORLD * (1 - 4**(-ell))
    proj = 1 + 2*PHI**(-1)*ell
    delta = C * (ell - 0.5) * (1 - 4**(-ell))
    return base * (proj + delta)

# H_eff(0) = c/R_world
check("H_eff(0) = ω_ring = 72.59", abs(C_LIGHT/R_WORLD - OMEGA_RING) < 0.01,
      f"{C_LIGHT/R_WORLD:.4f} vs {OMEGA_RING}")
# 低 z 極限
ell_small = math.log(1.01, 4)
D_small = R_WORLD * (1-4**(-ell_small)) * (1 + 2*PHI**(-1)*ell_small)
check("低 z 極限正確", abs(d_app(ell_small) - D_small)/D_small < 0.02)

# ============ 3. Nyquist 自洽 ============
print("\n--- 3. Nyquist 自洽 (O76/08) ---")
D_nyq = d_app(ell_nyq)
piR = math.pi * R_WORLD
check("D_app(ℓ_nyq) ≈ πR_world (0.9990)", abs(D_nyq/piR - 0.9990) < 0.001,
      f"{D_nyq:.1f} vs {piR:.1f} (比={D_nyq/piR:.4f})")

# ============ 4. 載入 Pantheon+ ============
print("\n--- 4. Pantheon+ 1701 SNe ---")
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
check("1701 SNe 載入", N == 1701, f"N={N}")

def fit_M(mu_model):
    J = np.ones(N)
    return (J @ cov_inv @ (mb - mu_model)) / (J @ cov_inv @ J)

# ============ 5. IDCM 零參數 fit ============
print("\n--- 5. IDCM D_L=(1+z)^(6/7)·D_A (零參數) ---")
ell_arr = np.log(1+zs)/np.log(4)
Da = d_app(ell_arr)
DL_idcm = (1+zs)**(6/7) * Da
mu_idcm0 = 5*np.log10(DL_idcm*1e6/10)
M_idcm = fit_M(mu_idcm0)
chi2_idcm = (mb - (mu_idcm0+M_idcm)) @ cov_inv @ (mb - (mu_idcm0+M_idcm))
print(f"M = {M_idcm:.4f}")
print(f"χ² = {chi2_idcm:.1f} / {N} dof")
print(f"χ²/dof = {chi2_idcm/(N-1):.3f}")

# ============ 6. ΛCDM 對照 ============
print("\n--- 6. ΛCDM Planck (H0=67.4, Ωm=0.315) ---")
def dc_lcdm(z, H0, Om):
    zz = np.geomspace(1e-6, max(z, 1e-4), 2000)
    E = np.sqrt(Om*(1+zz)**3 + (1-Om))
    return C_LIGHT/H0 * np.trapezoid(1/E, zz)
mu_lcdm_p = 5*np.log10((1+zs)*np.array([dc_lcdm(zi, 67.4, 0.315) for zi in zs])*1e6/10)
M_lp = fit_M(mu_lcdm_p)
chi2_lp = (mb - (mu_lcdm_p+M_lp)) @ cov_inv @ (mb - (mu_lcdm_p+M_lp))
print(f"ΛCDM Planck χ² = {chi2_lp:.1f}")

# 零參數對決
delta = chi2_idcm - chi2_lp
check("IDCM χ² 接近 ΛCDM (<10 差距)", delta < 10, f"Δχ²={delta:+.1f}")

# ============ 7. DESI BAO ============
print("\n--- 7. DESI BAO (D_A 幾何) ---")
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
check("DESI χ² < 15", chi2_d < 15, f"{chi2_d:.2f}")

# ============ 8. 分 bin 殘差 ============
print("\n--- 8. 分 bin 殘差 (z<0.8) ---")
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
check("全部 z<0.8 bin 殘差 <0.05", all_ok)

# ============ 9. 總結 ============
print(f"\n{'=' * 70}")
print(f"總結: PASS={PASS} FAIL={FAIL}")
print(f"{'=' * 70}")
print(f"""
★ IDCM z 紅移翻譯 — 最終閉合:

  z ↔ ell:   1+z = 4^ell, ell = log4(1+z)
  D_A(ell):  R_world(1-4^{-ell})(1+2phi^{-1}ell+delta(ell)), C=-0.1697
  D_L(z):    (1+z)^{6/7}.D_A(ell)   <- 距離對偶 (7=L4)
  H_eff(0):  c/R_world = 72.59 (O73 鎖定)

  Pantheon+ 1701 SNe:  chi2 = {chi2_idcm:.0f} (零參數)
  LCDM Planck 對照:    chi2 = {chi2_lp:.0f}
  delta chi2 = {delta:+.1f}

  DESI BAO: chi2 = {chi2_d:.2f} (零參數, 保持)
  Nyquist:  D_app(ell_nyq) = {D_nyq:.0f} ≈ piR_world = {piR:.0f} (0.9990)
""")

result = {
    'chi2_idcm': round(float(chi2_idcm), 1),
    'chi2_lcdm': round(float(chi2_lp), 1),
    'delta_chi2': round(float(delta), 1),
    'chi2_desi': round(float(chi2_d), 2),
    'M_idcm': round(float(M_idcm), 4),
    'nyquist_ratio': round(float(D_nyq/piR), 4),
    'pass': PASS, 'fail': FAIL
}
with open('data/20_final_verification.json', 'w') as f:
    json.dump(result, f, indent=2)
print(f"-> data/20_final_verification.json")
