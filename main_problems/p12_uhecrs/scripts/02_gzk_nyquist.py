#!/usr/bin/env python3
"""
GZK 截斷 = Nyquist 結構推導 (關鍵驗證)
========================================
核心假設: GZK 截斷 (~5e19 eV) 唔係「CMB 光子碰撞衰減」,
         而係宇宙晶格能承載嘅最細波長 (Nyquist cutoff)。

IDCM 晶格: 44-step 黃金層級 L_P × φ^44
  (D_H/L_P = φ^(N_d·L), 44 = N_d 係晶格基本深度)

推導:
  λ_min (晶格可承載最細波長) = L_P × φ^44
  E_GZK = hc / λ_min

如果 λ_min 對應嘅能量 ≈ 5e19 eV → GZK = Nyquist 成立!

同時驗證 Oh-My-God 粒子上限: E_max = 4φ × E_GZK
  (4φ = (φ³-φ⁻³)×φ = MERA 分支 × φ)
"""
import math

# ============ 常數 ============
phi = (1 + 5**0.5) / 2
inv_phi = 1/phi
eps = inv_phi / 4
N_d = 44
L = 53/8  # MERA 深度

# 物理常數
h = 6.62607015e-34     # J·s
c = 2.99792458e8       # m/s
L_P = 1.616255e-35     # m (Planck 長度)
eV_J = 1.602176634e-19 # J/eV
GeV_J = 1.602176634e-10

print("=" * 70)
print("GZK = Nyquist: 晶格最細承載波長推導")
print("=" * 70)

# ============ Step 1: λ_min = L_P × φ^44 ============
phi_44 = phi**44
lambda_min = L_P * phi_44
print(f"\nφ^44 = {phi_44:.6e}")
print(f"λ_min = L_P × φ^44 = {lambda_min:.6e} m")

# ============ Step 2: E_GZK = hc/λ_min ============
E_gzk = h * c / lambda_min  # J
E_gzk_eV = E_gzk / eV_J
print(f"\nE_GZK = hc/λ_min = {E_gzk_eV:.4e} eV")
print(f"觀測 GZK ≈ 5.0e19 eV")
print(f"偏差 = {abs(E_gzk_eV/5e19 - 1)*100:.3f}%")

# ============ Step 3: Oh-My-God 上限 ============
E_max = 4 * phi * E_gzk_eV  # 4φ × E_GZK
print(f"\nE_max = 4φ × E_GZK = {E_max:.4e} eV")
print(f"Oh-My-God 粒子 = 3.2e20 eV")
print(f"偏差 = {abs(E_max/3.2e20 - 1)*100:.3f}%")

# ============ Step 4: 交叉驗證 ============
# Auger 最高能量事件 ~ 1.66e20 eV (2021)
# TA 最高 ~ 3.2e20 eV (Oh-My-God, Fly's Eye 1991)
print(f"\n{'='*70}")
print("交叉驗證:")
print(f"{'='*70}")
print(f"  GZK (IDCM)          = {E_gzk_eV:.3e} eV")
print(f"  GZK (文獻)          = 5.0e19 eV       偏差 {abs(E_gzk_eV/5e19-1)*100:.2f}%")
print(f"  E_max (IDCM)        = {E_max:.3e} eV")
print(f"  Oh-My-God (觀測)    = 3.2e20 eV       偏差 {abs(E_max/3.2e20-1)*100:.2f}%")
print(f"  E_max/E_GZK (IDCM)  = 4φ = {4*phi:.4f}")
print(f"  E_max/E_GZK (觀測)  = 3.2e20/5e19 = 6.40")

# ============ Step 5: 物理詮釋 ============
print(f"\n{'='*70}")
print("物理詮釋:")
print(f"{'='*70}")
print(f"""
1. 晶格承載極限: λ_min = L_P × φ^44 = {lambda_min:.2e} m
   44 = N_d = K_Chain 站點數 (φ 層級最細可分辨尺度)

2. GZK = 喺呢個晶格上穩定傳播嘅能量上限
   超過 E_GZK 嘅應力釋放 → 波長短過 λ_min → 無法穩定傳播
   (同 z≈17 嘅 Nyquist cutoff 同一物理: 離散網格嘅固有極限)

3. E_max = 4φ × E_GZK = 應力釋放嘅絕對上限
   4φ = (φ³-φ⁻³)×φ = MERA 分支因子 × φ
   → 單一拓撲激發最多凝聚 4φ 個「GZK 單位」

4. UHECR 來源唔需要極端天體加速器
   就係晶格應力釋放: 相位滑動/阻挫邊斷裂 → 拓撲張力 → 單一激發
""")

# ============ 保存 ============
import json, os
results = {
    "phi_44": phi_44,
    "lambda_min_m": lambda_min,
    "E_GZK_eV": E_gzk_eV,
    "E_GZK_obs_eV": 5e19,
    "E_GZK_dev_pct": abs(E_gzk_eV/5e19 - 1)*100,
    "E_max_eV": E_max,
    "E_OMG_eV": 3.2e20,
    "E_max_dev_pct": abs(E_max/3.2e20 - 1)*100,
    "ratio_max_gzk": 4*phi,
    "ratio_obs": 6.4,
}
os.makedirs('data', exist_ok=True)
with open('data/gzk_nyquist_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f"\n結果已保存至 data/gzk_nyquist_results.json")
