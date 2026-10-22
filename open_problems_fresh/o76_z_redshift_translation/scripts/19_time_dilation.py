#!/usr/bin/env python3
"""
O76/19: Time dilation 預言 — IDCM 機制 B 完整分析
================================================================
z 紅移翻譯嘅核心可證偽預言: 超新星 time dilation

ΛCDM: 宇宙膨脹拉長光變曲線 → Δt_obs = (1+z)·Δt_rest
IDCM (機制 B, W-field 能量損失):
  光子能量 E = hν 沿傳播損失
  所有週期過程 (SN 光變, 譜線振盪) 跟同一能量標尺
  → Δt_obs = (1+z)·Δt_rest  (同 ΛCDM 一樣嘅觀測預言!)

★ 但係: 有冇二階修正? 如果 D_L = (1+z)^{6/7}·D_A
  時間 dilation 因子係咪都係 (1+z)^{6/7}?

物理: 光子能量損失率 dE/ds ∝ E → E(s) = E₀e^{-αs}
  紅移: 1+z = E₀/E(s) = e^{αs}
  時間 dilation: 週期過程嘅時間標尺 τ ∝ 1/E (能量標尺)
  → Δt_obs = τ_obs = τ_rest·(E₀/E(s)) = (1+z)·τ_rest

  但 W-field 修正: 如果能量演化有 (1+z)^{1/7} 修正
  → 時間 dilation 都應該跟 6/7?
  → Δt_obs = (1+z)^{6/7}·Δt_rest? 定 (1+z)?

文獻 (Goldhaber 2001): Δt ∝ (1+z)^{1.07±0.06}
  Blondin 2008: (1+z)^{1.00±0.07}
  → 現有數據 1.0-1.07, 分辨唔到 1.0 vs 6/7=0.857 (差 14%)
  → 需要 z>1 高精度樣本

★ 可證偽預言:
  P1: Δt ∝ (1+z)  (IDCM 機制 B 基本預言)
  P2: 如果有 W-field 修正: Δt ∝ (1+z)^{6/7}
  P3: 距離-紅移同 ΛCDM 喺 z>1 分歧 (D_L 短 10-20%)
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

print("=" * 70)
print("O76/19: Time dilation 預言")
print("=" * 70)

# ============ 1. 機制分析 ============
print("""
★ Time dilation 喺 IDCM 機制 B (W-field 能量損失):

  光子能量: E(s) = E₀·e^{-αs}, 1+z = e^{αs}
  時間標尺: τ ∝ 1/E (能量-時間不確定性, 所有週期過程)
  → Δt_obs/Δt_rest = E₀/E(s) = (1+z)

  → IDCM 預言 Δt ∝ (1+z) — 同 ΛCDM 一樣!
  → 呢個唔係巧合: 兩者都係「能量標尺」效應
     ΛCDM: 膨脹拉長波長 (能量跌) → 時間跌
     IDCM: W-field 能量損失 → 時間跌
  → 分辨方法: 距離-紅移 (唔係 time dilation)
""")

# ============ 2. 文獻對照 ============
print("--- 2. 文獻對照 ---")
# Goldhaber 2001 (42 SNe, 0.18<z<0.83): (1+z)^{1.07±0.06}
# Blondin 2008 (35 SNe): (1+z)^{1.00±0.07}
# Hayden 2010: (1+z)^{1.0±0.1}
# 最新: DES 2024 (z<1): 一致 (1+z)
print("""
Goldhaber 2001: Δt ∝ (1+z)^{1.07±0.06}  (0.18<z<0.83)
Blondin 2008:   Δt ∝ (1+z)^{1.00±0.07}
Hayden 2010:    Δt ∝ (1+z)^{1.0±0.1}
DES 2024:       Δt ∝ (1+z)  (z<1)

→ 全部支持 (1+z), 誤差 ±0.06-0.1
→ IDCM 預言 (1+z) → 相容 ✅
→ 分辨 1.0 vs 6/7=0.857: 需要 σ<0.07 嘅高 z 樣本
""")

# ============ 3. 幾何 vs 能量: D_L 差異 ============
print("\n--- 3. IDCM vs ΛCDM D_L 差異 (可證偽) ---")
C_LIGHT = 299792.458
R_WORLD = 4129.94
PHI = (1 + math.sqrt(5)) / 2
C_DELAY = -0.1697
OMEGA_RING = 72.59

def d_app(ell):
    base = R_WORLD * (1 - 4**(-ell))
    proj = 1 + 2*PHI**(-1)*ell
    delta = C_DELAY * (ell - 0.5) * (1 - 4**(-ell))
    return base * (proj + delta)

def dc_lcdm(z, H0, Om):
    zz = np.geomspace(1e-6, max(z, 1e-4), 2000)
    E = np.sqrt(Om*(1+zz)**3 + (1-Om))
    return C_LIGHT/H0 * np.trapezoid(1/E, zz)

print(f"{'z':<6} {'D_L(IDCM)':<10} {'D_L(ΛCDM)':<10} {'dev':<8}")
for z in [0.5, 1.0, 1.5, 2.0, 3.0, 5.0]:
    ell = math.log(1+z, 4)
    DL_idcm = (1+z)**(6/7) * d_app(ell)
    DL_lcdm = (1+z) * dc_lcdm(z, OMEGA_RING, 0.315)
    print(f"{z:<6} {DL_idcm:<10.1f} {DL_lcdm:<10.1f} {(DL_idcm-DL_lcdm)/DL_lcdm*100:+.2f}%")

# ============ 4. 可證偽預言總結 ============
print("\n--- 4. 可證偽預言 ---")
print(f"""
★ IDCM z 紅移翻譯 — 可證偽預言清單:

P1 (time dilation): Δt_obs = (1+z)·Δt_rest
   → 同 ΛCDM, 現有數據支持 ✅ (Goldhaber/Blondin/DES)
   → 分辨唔到兩模型 (機制唔同但預言一樣)

P2 (距離-紅移): D_L(z) = (1+z)^{6/7}·D_A(ℓ)
   → Pantheon+ χ²=2006.9 (零參數, 同 ΛCDM 差 4.7) ✅
   → z>1 同 ΛCDM 分歧: D_L 短 {abs((DL_idcm-DL_lcdm)/DL_lcdm*100):.0f}% (z=3)
   → JWST/Roman 高 z SNe 可以分辨!

P3 (BAO 幾何): D_A(ℓ) 保持, DESI χ²=12.82 ✅
   → z=2.33 Lyα 係關鍵測試點

P4 (Nyquist 截止): z=17 係最大紅移
   → 高 z 源 (z>17) 唔應該存在 (O51)
   → JWST 極高 z 搜尋可以分辨

P5 (CMB T(z)): T(z) = T₀(1+z) (能量損失)
   → 同 ΛCDM 一樣 (CMB 溫度-紅移)
   → 分辨唔到

P6 (距離對偶): D_L/D_A = (1+z)^{6/7} ≠ (1+z)²
   → 可證偽: 量度 D_L (SNe) + D_A (BAO) 直接比!
   → 現有: O76/06 表支持 IDCM (觀測 D_L/D_A 喺 (1+z) 同 (1+z)² 之間)
""")

result = {
    'time_dilation': '(1+z) 同 ΛCDM',
    'P2_DL_ratio_z3': round(float((DL_idcm-DL_lcdm)/DL_lcdm*100), 2),
    'pass': PASS, 'fail': FAIL
}
with open('data/19_time_dilation.json', 'w') as f:
    json.dump(result, f, indent=2)
print(f"PASS={PASS} FAIL={FAIL}")
print("-> data/19_time_dilation.json")
