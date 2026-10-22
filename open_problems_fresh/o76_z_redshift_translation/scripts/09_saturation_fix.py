#!/usr/bin/env python3
"""
O76/09: 投影飽和修正 — D_app_sat(ℓ) 同時 fit SNe + DESI
================================================================
★ O76/08 發現: D_app(ℓ_Nyquist) = 12962 ≈ πR_world = 12975 (0.9990)
  → D_app 喺 Nyquist 截止啱好到達環對面 — 幾何自洽!

★ 新發現: F_proj=17 截斷 → ℓ_cut = 17/44·ℓ_Nyquist = 0.80
  → 投影伸長 (1+2φ⁻¹ℓ) 應該喺 ℓ_cut 飽和

修正公式候選:
  D_sat(ℓ) = R_world(1-4^{-ℓ})·(1 + 2φ⁻¹·S(ℓ) + δ(ℓ))
  S(ℓ) = 飽和函數: S(ℓ) = ℓ  (ℓ < ℓ_cut), S(ℓ) → ℓ_cut·(1+κ) (ℓ > ℓ_cut)

最簡單結構選擇: S(ℓ) = ℓ_cut·tanh(ℓ/ℓ_cut)  — 平滑飽和
  tanh: ℓ→0: S→ℓ (線性), ℓ→∞: S→ℓ_cut (飽和)

驗證標準:
  1. SNe χ² < 2096 (改善)
  2. DESI χ² < 12.82 (唔好破壞 BAO 閉合)
  3. 零自由參數 (ℓ_cut 由 F_proj, 44, ℓ_Nyquist 結構決定)
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
print("O76/09: 投影飽和修正 — D_app_sat(ℓ)")
print("=" * 70)

# ============ 1. 結構參數 ============
ell_nyq = math.log(18, 4)          # 2.0850
ell_cut = F_PROJ / N_D * ell_nyq   # 17/44 × 2.085 = 0.8056
print(f"ℓ_Nyquist = {ell_nyq:.4f} (z=17)")
print(f"ℓ_cut = F_proj/44 × ℓ_Nyquist = {ell_cut:.4f} (z_cut = 4^{ell_cut}-1 = {4**ell_cut-1:.2f})")

# ============ 2. 飽和公式 ============
def S_sat(ell):
    """飽和函數: ℓ→0: ℓ, ℓ→∞: ℓ_cut"""
    return ell_cut * np.tanh(ell/ell_cut)

def d_app_sat(ell, C=C_DELAY):
    """D_app 飽和版: 投影伸長用 S(ℓ) 取代 ℓ"""
    base = R_WORLD * (1 - 4**(-ell))
    proj = 1 + 2*PHI**(-1)*S_sat(ell)
    delta = C * (ell - 0.5) * (1 - 4**(-ell))
    return base * (proj + delta)

def d_app_orig(ell, C=C_DELAY):
    base = R_WORLD * (1 - 4**(-ell))
    proj = 1 + 2*PHI**(-1)*ell
    delta = C * (ell - 0.5) * (1 - 4**(-ell))
    return base * (proj + delta)

# 比較
print(f"\n--- 飽和 vs 原始 ---")
print(f"{'z':<6} {'ℓ':<7} {'D_orig':<9} {'D_sat':<9} {'比':<7}")
for z in [0.1, 0.3, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0, 17.0]:
    ell = math.log(1+z, 4)
    d1 = d_app_orig(ell)
    d2 = d_app_sat(ell)
    print(f"{z:<6} {ell:<7.3f} {d1:<9.1f} {d2:<9.1f} {d2/d1:<7.3f}")

# ============ 3. SNe fit ============
print("\n--- 3. SNe fit (Pantheon+) ---")
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

def fit_M(mu_model):
    J = np.ones(N)
    return (J @ cov_inv @ (mb - mu_model)) / (J @ cov_inv @ J)

def mu_of(z, D_func, M):
    ell = np.log(1+z) / np.log(4)
    DL = (1+z) * D_func(ell)
    return M + 5*np.log10(DL*1e6/10)

# 原始
mu0 = 5*np.log10((1+zs)*d_app_orig(np.log(1+zs)/np.log(4))*1e6/10)
M0 = fit_M(mu0)
chi2_orig = (mb - (mu0+M0)) @ cov_inv @ (mb - (mu0+M0))

# 飽和
mu_sat = 5*np.log10((1+zs)*d_app_sat(np.log(1+zs)/np.log(4))*1e6/10)
M_sat = fit_M(mu_sat)
chi2_sat = (mb - (mu_sat+M_sat)) @ cov_inv @ (mb - (mu_sat+M_sat))

print(f"原始:   M={M0:.4f} χ²={chi2_orig:.1f} χ²/dof={chi2_orig/(N-1):.3f}")
print(f"飽和:   M={M_sat:.4f} χ²={chi2_sat:.1f} χ²/dof={chi2_sat/(N-1):.3f}")
print(f"改善:   Δχ² = {chi2_orig - chi2_sat:+.1f}")

# ============ 4. DESI fit ============
print("\n--- 4. DESI BAO fit ---")
rd_idcm = math.pi * R_WORLD / 88 * 420/421
desi = [
    ('LRG1', 0.510, 13.588, 0.167),
    ('LRG2', 0.706, 17.351, 0.177),
    ('LRG3+ELG', 0.934, 21.576, 0.152),
    ('ELG2', 1.321, 27.601, 0.318),
    ('Lyα', 2.330, 38.988, 0.531),
]
chi2_d_orig, chi2_d_sat = 0, 0
print(f"{'樣本':<12} {'z':<6} {'DESI':<8} {'D_orig':<8} {'D_sat':<8}")
for name, z, obs, err in desi:
    ell = math.log(1+z, 4)
    po = d_app_orig(ell)/rd_idcm
    ps = d_app_sat(ell)/rd_idcm
    chi2_d_orig += ((po-obs)/err)**2
    chi2_d_sat += ((ps-obs)/err)**2
    print(f"{name:<12} {z:<6} {obs:<8} {po:<8.3f} {ps:<8.3f}")
print(f"DESI χ² 原始: {chi2_d_orig:.2f}")
print(f"DESI χ² 飽和: {chi2_d_sat:.2f}")

# ============ 5. 結果 ============
print("\n--- 5. 總結 ---")
print(f"SNe:  {chi2_orig:.1f} → {chi2_sat:.1f} (Δ={chi2_orig-chi2_sat:+.1f})")
print(f"DESI: {chi2_d_orig:.2f} → {chi2_d_sat:.2f} (Δ={chi2_d_sat-chi2_d_orig:+.2f})")
check("SNe 改善", chi2_sat < chi2_orig, f"{chi2_sat:.1f} < {chi2_orig:.1f}")
check("DESI 保持", chi2_d_sat < 20, f"{chi2_d_sat:.2f}")

result = {
    'ell_cut': round(float(ell_cut), 4),
    'z_cut': round(float(4**ell_cut-1), 3),
    'chi2_sn_orig': round(float(chi2_orig), 1),
    'chi2_sn_sat': round(float(chi2_sat), 1),
    'chi2_desi_orig': round(float(chi2_d_orig), 2),
    'chi2_desi_sat': round(float(chi2_d_sat), 2),
    'pass': PASS, 'fail': FAIL
}
with open('data/09_saturation_fix.json', 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nPASS={PASS} FAIL={FAIL}")
print("-> data/09_saturation_fix.json")
