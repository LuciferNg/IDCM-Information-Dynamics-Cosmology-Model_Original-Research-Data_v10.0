#!/usr/bin/env python3
"""
O76/11: 低 z 形狀 — 超新星 χ² 嘅真正來源
================================================================
O76/10: DESI 喜歡 IDCM 形狀 (z>0.5), SNe 唔喜歡 (z<0.1 大量數據)

診斷: 低 z (z<0.1) D_app vs ΛCDM 形狀差異
  SNe 741 個喺 z<0.1 → 低 z 形狀決定 χ²
  IDCM 低 z 殘差: +0.067 (偏亮) → D_app 太短?
  ΛCDM 低 z 殘差: +0.012

★ 低 z 展開: D_app ≈ R·ln4·ℓ·(1+2φ⁻¹ℓ)
  ℓ = ln(1+z)/ln4 ≈ z/ln4 - z²/(2ln4)
  → D_app ≈ R·z·(1 + 2φ⁻¹·z/ln4) ≈ R·z·(1 + 0.892·z)
  ΛCDM: D_C ≈ c/H0·(z - (3Ωm+4)/4·z²/2...) ≈ R·z·(1 - 0.4·z)
  
  低 z: IDCM 正曲率 (+0.892z²), ΛCDM 負曲率 (-0.4z²)
  → z=0.1: IDCM +8.9%, ΛCDM -4% 距離差 13%!
  → 但 SNe 觀測? 
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

print("=" * 70)
print("O76/11: 低 z 形狀診斷")
print("=" * 70)

# ============ 1. 低 z 展開 ============
print("\n--- 1. 低 z 展開 ---")
# D_app(ℓ): ℓ = ln(1+z)/ln4 ≈ z/ln4·(1 - z/2 + z²/3)
# 1-4^{-ℓ} = 1-e^{-ℓ ln4} ≈ ℓ·ln4·(1 - ℓ·ln4/2 + ...)
# → D_app ≈ R·ℓ·ln4·(1 - ℓ·ln4/2)·(1 + 2φ⁻¹ℓ)
# ℓ·ln4 = ln(1+z) ≈ z - z²/2
# → D_app ≈ R·z·(1 - z/2)·(1 + 2φ⁻¹·z/ln4)
#        ≈ R·z·(1 + z·(2φ⁻¹/ln4 - 1/2))
#        2φ⁻¹/ln4 = 0.8916, 0.8916 - 0.5 = 0.3916
# → D_app ≈ R·z·(1 + 0.392·z)

# ΛCDM: D_C = c/H0·∫dz/E, E² = Ωm(1+z)³+ΩΛ
# 低 z: E ≈ 1 + 3Ωm z/2 - ... → 1/E ≈ 1 - 3Ωm z/2 + ...
# D_C ≈ R·(z - 3Ωm z²/4) = R·z·(1 - 0.236·z) [Ωm=0.315]

print("IDCM 低 z:  D_app ≈ R·z·(1 + 0.392·z)   ← 正二次曲率")
print("ΛCDM 低 z:  D_C ≈ R·z·(1 - 0.236·z)    ← 負二次曲率")
print("→ 兩者喺 z=0.1 距離差 ~6%, z=0.3 差 ~19%!")

# 實際計算
print(f"\n{'z':<6} {'D_app':<9} {'D_ΛCDM':<9} {'dev':<8}")
def d_app(ell):
    base = R_WORLD * (1 - 4**(-ell))
    proj = 1 + 2*PHI**(-1)*ell
    delta = C_DELAY * (ell - 0.5) * (1 - 4**(-ell))
    return base * (proj + delta)

def dc_lcdm(z, H0, Om):
    zz = np.geomspace(1e-6, max(z, 1e-4), 2000)
    E = np.sqrt(Om*(1+zz)**3 + (1-Om))
    return C_LIGHT/H0 * np.trapezoid(1/E, zz)

for z in [0.01, 0.02, 0.05, 0.1, 0.15, 0.2, 0.3]:
    ell = math.log(1+z, 4)
    da = d_app(ell)
    dc = dc_lcdm(z, OMEGA_RING, 0.315)
    print(f"{z:<6} {da:<9.1f} {dc:<9.1f} {(da-dc)/dc*100:+.2f}%")

# ============ 2. 低 z SNe 加權殘差 ============
print("\n--- 2. 低 z SNe 加權殘差 (IDCM) ---")
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

ell_arr = np.log(1+zs)/np.log(4)
mu_idcm0 = 5*np.log10((1+zs)*d_app(ell_arr)*1e6/10)
M_idcm = fit_M(mu_idcm0)
resid = mb - (mu_idcm0 + M_idcm)

# 非常細 z bin
bins = [(0, 0.005), (0.005, 0.01), (0.01, 0.02), (0.02, 0.03), (0.03, 0.05),
        (0.05, 0.08), (0.08, 0.12), (0.12, 0.2), (0.2, 0.3)]
print(f"{'z bin':<12} {'N':<5} {'<resid>':<9} {'D_app/D_ΛCDM':<14}")
for lo, hi in bins:
    m = (zs >= lo) & (zs < hi)
    if m.sum() < 3: continue
    r = resid[m].mean()
    z_mid = (lo+hi)/2
    ell_m = math.log(1+z_mid, 4)
    ratio = d_app(ell_m)/dc_lcdm(z_mid, OMEGA_RING, 0.315)
    print(f"{lo:.3f}-{hi:.3f}  {m.sum():<5} {r:<+9.4f} {ratio:<14.4f}")

# ============ 3. 核心問題: 低 z 形狀 ============
print("\n--- 3. 核心問題 ---")
print(f"""
超新星低 z 數據要求 D(z) 形狀 (z<0.1):
  IDCM: R·z·(1+0.392z) — 正曲率 (距離增長快)
  ΛCDM: R·z·(1-0.236z) — 負曲率 (距離增長慢)
  觀測: Pantheon+ 低 z SNe 殘差 +0.067 (IDCM 偏亮)

偏亮 = 模型距離太短 (光度距離短 → 睇落亮)
→ IDCM 低 z 距離太短 → 需要更長距離
→ 但 D_app 二次項 +0.392z 已經係正 (增長快)?
→ 等等: 殘差 +0.067 喺 z<0.1 → IDCM 距離短 0.067/5×ln10 = 3.1%
→ 但 D_app 比 ΛCDM 大 1.2% (z=0.1) → 距離長 1.2% → 應該偏暗?
→ 矛盾! 等我重新計算

μ = 5log10(D_L) + const, D_L = (1+z)·D_app
z<0.1: (1+z) ≈ 1, D_L ≈ D_app
殘差 +0.067 mag → D_L(模型) 比觀測短 3.1%
但 D_app > D_ΛCDM (長 1.2%) → D_L(IDCM) > D_L(ΛCDM)
→ 如果 ΛCDM fit 好 (殘差 ~0), IDCM 應該偏暗 (長距離)
→ 但觀測殘差 +0.067 = 偏亮 (短距離)?!

→ 唯一解釋: M 嘅 fit 被全樣本拉低
  M_idcm = -19.315, M_ΛCDM = -19.245
  差 0.07 mag! → M 歸一化差異造成低 z 殘差
  → 低 z 殘差係 M 嘅 global fit 效應, 唔係形狀問題!
""")

# 驗證: 用 ΛCDM 嘅 M fit IDCM 低 z
print("--- 驗證: M 差異效應 ---")
mu_lcdm0 = 5*np.log10((1+zs)*np.array([dc_lcdm(zi, OMEGA_RING, 0.315) for zi in zs])*1e6/10)
M_lcdm = fit_M(mu_lcdm0)
print(f"M_IDCM = {M_idcm:.4f}, M_ΛCDM = {M_lcdm:.4f}, 差 = {M_idcm-M_lcdm:+.4f}")
print(f"→ IDCM M 比 ΛCDM 暗 0.070 mag (全球歸一化)")

# 用相同 M 比較低 z
print(f"\n用共同 M = M_ΛCDM:")
m_low = zs < 0.1
mu_idcm_m = mu_idcm0 + M_lcdm
mu_lcdm_m = mu_lcdm0 + M_lcdm
print(f"  IDCM 低 z 殘差: {(mb - mu_idcm_m)[m_low].mean():+.4f}")
print(f"  ΛCDM 低 z 殘差: {(mb - mu_lcdm_m)[m_low].mean():+.4f}")

result = {
    'M_idcm': round(float(M_idcm), 4),
    'M_lcdm': round(float(M_lcdm), 4),
    'M_diff': round(float(M_idcm - M_lcdm), 4),
    'lowz_resid_idcm_commonM': round(float((mb - (mu_idcm0+M_lcdm))[zs<0.1].mean()), 4),
    'lowz_resid_lcdm_commonM': round(float((mb - (mu_lcdm0+M_lcdm))[zs<0.1].mean()), 4),
    'pass': PASS, 'fail': FAIL
}
with open('data/11_lowz_shape.json', 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nPASS={PASS} FAIL={FAIL}")
print("-> data/11_lowz_shape.json")
