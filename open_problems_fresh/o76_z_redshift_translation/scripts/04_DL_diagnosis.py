#!/usr/bin/env python3
"""
O76/04: 光度距離 D_L 喺 IDCM 嘅定義 — 超新星殘差診斷
================================================================
發現 (O76/03): IDCM μ(z) fit Pantheon+ 有 S 形殘差
  z<0.1: +0.067 (偏亮)
  z~0.5: -0.03
  z~0.7: -0.10 (偏暗)
  z>1:   -0.06~-0.13 (偏暗)

問題: D_app 係「投影距離」— 但超新星量度嘅係「光度距離」D_L
ΛCDM: D_L = (1+z)²·D_A (Etherington 距離對偶)
IDCM 冇膨脹: 距離對偶仲成唔成立?

Etherington (1933) 距離對偶: D_L = (1+z)²·D_A
  依賴: 光子數守恆 + 無吸收 (喺任何時空都成立, 包括靜態!)
  所以 IDCM 都要有 D_L = (1+z)²·D_A
  → 但 IDCM 嘅 D_app 係「角直徑距離」定「光度距離」?

O51 用 D_app 做 DESI BAO (D_M = 角直徑距離!) ✅
O76/03 用 D_app 做超新星 (D_L = 光度距離!) ← 可能錯!

如果 D_app 係 D_A (角直徑), 咁 D_L = (1+z)²·D_A = (1+z)²·D_app
  → 但我喺 script 03 用 D_L = (1+z)·D_app ← 錯咗一倍 (1+z)!

修正: μ(z) = 5log10((1+z)²·D_app/10pc)
  → 比 script 03 暗 5·log10(1+z) mag
  → z=0.5: +0.88 mag!  z=1: +1.51 mag!

但係咁樣高 z 會暗好多 → 更加 fit 唔到?

等等 — 超新星 fit 到 ΛCDM 表示觀測 D_L 好接近 (1+z)²·D_A_ΛCDM
如果 IDCM D_A = D_app 同 ΛCDM D_A 差唔多 (DESI fit 好),
咁 D_L 應該都差唔多 → 點解 χ² 差 107?

關鍵: ΛCDM fit 咗 Ωm=0.38 (大過 Planck 0.315!)
  → 因為 H0 固定 72.59, ΛCDM 要調 Ωm 去 match IDCM 形狀
  → 但 Ωm=0.38 唔係 Planck 值 → 呢個 fit 係「作弊」?

公平比較應該係:
  A. IDCM 零參數 vs ΛCDM 2 參數 (H0, Ωm) — ΛCDM 有優勢
  B. IDCM 零參數 vs ΛCDM 固定 (H0=67.4, Ωm=0.315) — 真正零參數對決

先檢查 B: ΛCDM 固定 Planck 參數 fit 得點?
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
OMEGA_RING = 72.59
C_DELAY = -0.1697

print("=" * 70)
print("O76/04: 光度距離 D_L 定義 — Etherington 對偶診斷")
print("=" * 70)

# ============ 1. 載入數據 ============
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
        if len(parts) < len(header):
            continue
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

def d_app(ell):
    base = R_WORLD * (1 - 4**(-ell))
    proj = 1 + 2*PHI**(-1)*ell
    delta = C_DELAY * (ell - 0.5) * (1 - 4**(-ell))
    return base * (proj + delta)

def mu_idcm(z, M, DL_power):
    """DL_power = 1 → D_L=(1+z)·D_app (舊), = 2 → (1+z)²·D_app (Etherington)"""
    ell = np.log(1+z) / np.log(4)
    DL = (1+z)**DL_power * d_app(ell)
    return M + 5*np.log10(DL*1e6/10)

def dc_lcdm_vec(z, H0, Om):
    Ol = 1 - Om
    out = np.zeros_like(z)
    zz = np.geomspace(1e-6, max(z.max(), 1e-4), 2000)
    E = np.sqrt(Om*(1+zz)**3 + Ol)
    DC_int = C_LIGHT/H0 * np.trapezoid(1/E, zz)  # up to max
    # 插值
    from scipy.interpolate import interp1d
    dc_f = interp1d(zz, np.concatenate([[0], np.cumsum((zz[1:]-zz[:-1])/E[:-1])*C_LIGHT/H0]), 
                    bounds_error=False, fill_value='extrapolate')
    return dc_f(z)

print(f"\n載入 {N} 個 SNe")

# ============ 2. 三種距離定義比較 ============
print("\n--- 2. 距離定義比較 ---")
print(f"{'z':<6} {'D_app':<9} {'(1+z)D_app':<11} {'(1+z)²D_app':<12} {'ΛCDM D_L':<10}")
for z in [0.1, 0.3, 0.5, 1.0, 1.5, 2.0]:
    ell = math.log(1+z, 4)
    Da = d_app(ell)
    DL1 = (1+z)*Da
    DL2 = (1+z)**2 * Da
    DC = dc_lcdm_vec(np.array([z]), 67.4, 0.315)[0]
    DLl = (1+z)*DC
    print(f"{z:<6} {Da:<9.1f} {DL1:<11.1f} {DL2:<12.1f} {DLl:<10.1f}")

# ============ 3. Fit 三種 IDCM 變體 ============
print("\n--- 3. IDCM 變體 fit ---")
variants = {
    'IDCM D_L=(1+z)·D_app': 1,
    'IDCM D_L=(1+z)²·D_app': 2,
}
results = {}
for name, power in variants.items():
    mu0 = mu_idcm(zs, 0, power)
    M = fit_M(mu0)
    resid = mb - (mu0 + M)
    chi2 = resid @ cov_inv @ resid
    results[name] = chi2
    print(f"  {name:<28} M={M:.4f} χ²={chi2:.1f} χ²/dof={chi2/(N-1):.3f}")

# ============ 4. ΛCDM 固定 Planck 參數 ============
print("\n--- 4. ΛCDM 固定 Planck (H0=67.4, Ωm=0.315) — 零參數對決 ---")
mu_lcdm_planck = 5*np.log10((1+zs)*dc_lcdm_vec(zs, 67.4, 0.315)*1e6/10)
M_planck = fit_M(mu_lcdm_planck)
resid_p = mb - (mu_lcdm_planck + M_planck)
chi2_planck = resid_p @ cov_inv @ resid_p
print(f"  ΛCDM Planck: M={M_planck:.4f} χ²={chi2_planck:.1f} χ²/dof={chi2_planck/(N-1):.3f}")

# ΛCDM 用 ω_ring (H0=72.59, Ωm=0.315)
mu_lcdm_ring = 5*np.log10((1+zs)*dc_lcdm_vec(zs, OMEGA_RING, 0.315)*1e6/10)
M_ring = fit_M(mu_lcdm_ring)
resid_r = mb - (mu_lcdm_ring + M_ring)
chi2_ring = resid_r @ cov_inv @ resid_r
print(f"  ΛCDM H0=72.59 Ωm=0.315: M={M_ring:.4f} χ²={chi2_ring:.1f} χ²/dof={chi2_ring/(N-1):.3f}")

# ============ 5. 總結比較 ============
print("\n--- 5. 零參數對決 (全部只用 M 做歸一化) ---")
print(f"{'模型':<32} {'參數':<6} {'χ²':<10} {'χ²/dof':<8}")
print(f"{'─'*58}")
for name, chi2 in results.items():
    print(f"{name:<32} {'M':<6} {chi2:<10.1f} {chi2/(N-1):<8.3f}")
print(f"{'ΛCDM Planck':<32} {'M':<6} {chi2_planck:<10.1f} {chi2_planck/(N-1):<8.3f}")
print(f"{'ΛCDM H0=72.59':<32} {'M':<6} {chi2_ring:<10.1f} {chi2_ring/(N-1):<8.3f}")

# 加權殘差圖 (分 bin)
print("\n--- 6. 分 bin 加權殘差 ---")
bins = [(0, 0.1), (0.1, 0.3), (0.3, 0.5), (0.5, 1.0), (1.0, 2.3)]
mu_idcm_v2 = mu_idcm(zs, M_idcm := fit_M(mu_idcm(zs, 0, 2)), 2)
print(f"{'z bin':<12} {'N':<6} {'IDCM(1+z)²':<13} {'ΛCDM Planck':<14}")
for lo, hi in bins:
    m = (zs >= lo) & (zs < hi)
    if m.sum() == 0: continue
    r1 = (mb - mu_idcm_v2)[m].mean()
    r2 = (mb[m] - (mu_lcdm_planck[m] + M_planck)).mean()
    print(f"{lo:.1f}-{hi:.1f}      {m.sum():<6} {r1:<+13.4f} {r2:<+14.4f}")

result = {
    'N': int(N),
    'IDCM_DL_1z': round(results['IDCM D_L=(1+z)·D_app'], 1),
    'IDCM_DL_2z': round(results['IDCM D_L=(1+z)²·D_app'], 1),
    'LCDM_planck': round(float(chi2_planck), 1),
    'LCDM_ring': round(float(chi2_ring), 1),
    'pass': PASS, 'fail': FAIL
}
with open('data/04_DL_diagnosis.json', 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nPASS={PASS} FAIL={FAIL}")
print("-> data/04_DL_diagnosis.json")
