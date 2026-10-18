#!/usr/bin/env python3
"""
路線 1: CMB 偏振宇稱違反 — A₅ 晶格手性結構推導
================================================
物理邏輯 (Gemini):
  如果宇宙底層係有手性 (Chirality) 嘅 A₅ 晶格網格, CMB 嘅 E/B-mode 偏振
  唔可能完全隨機或宇稱守恆。偏振旋轉角 (Polarization Rotation) 應該
  同 32 條阻挫邊嘅幾何分佈產生位相鎖定。

IDCM 結構預測:
  1. 宇稱違反源: A₅ 節點嘅 2-coloring 有手性 (冷/熱阻挫)
     - 32 條阻挫邊 = 同色相連 (16 冷-冷 + 16 熱-熱)
     - 呢啲邊係「手性缺陷」— 喺度偏振會異常
  2. 偏振旋轉角 α ∝ ε⁵ (同冷斑 RMS 同一量級! ε⁵/8 = 1.10e-5)
     - 冷斑 RMS = ε⁵/8 = 1.1007e-5 (0.06% vs 觀測!)
     - 偏振旋轉應該同量級: ~1e-5 rad = 0.0006°
  3. 空間分佈: 旋轉角喺 32 條阻挫邊附近有系統性偏離
     - 阻挫邊 = 手性集中線
     - 每條邊 ±5° 帶狀區域內 α ≠ 0
  4. 宇稱檢驗統計量: 
     - C(α) 相關函數: 阻挫邊內 vs 邊外
     - 或者: 冷-冷邊 vs 熱-熱邊嘅偏振差異 (直接宇稱測試)

對比文獻:
  - Planck 2018: 冇偵測到全域偏振旋轉 (|α| < 1°)
  - 但局部/空間變化嘅旋轉未排除!
  - IDCM 預測: 局部旋轉 ~1e-5 rad, 需要 CMB-S4 靈敏度 (σ_α ~ 0.01°?)
"""
import math
import os

phi = (1 + 5**0.5)/2
inv_phi = phi - 1
eps = inv_phi/4
kappa = 1/16

print("="*70)
print("CMB 偏振宇稱違反 — A₅ 手性結構推導")
print("="*70)

# ============ 1. 宇稱違反量級預測 ============
print(f"\n1. 偏振旋轉角量級預測")
# 冷斑 RMS = ε⁵/8 = 1.1007e-5 (已驗證 0.06%)
rms_cold = eps**5/8
print(f"   冷斑 RMS = ε⁵/8 = {rms_cold:.6e} (已驗證 0.06%)")

# 偏振旋轉角: 宇稱違反來源 = 阻挫邊嘅手性
# 候選: α_chiral = ε⁵ × (32/60) = ε⁵ × 0.533 (阻挫邊比例)
alpha1 = eps**5 * (32/60)
print(f"   α₁ = ε⁵×(32/60) = {alpha1:.6e} rad = {math.degrees(alpha1)*3600:.4f} arcsec")

# 候選: α = ε⁵/4 (類似 κ 結構)
alpha2 = eps**5/4
print(f"   α₂ = ε⁵/4 = {alpha2:.6e} rad = {math.degrees(alpha2)*3600:.4f} arcsec")

# 候選: α = κ×ε³ = 1/16 × ε³
alpha3 = kappa * eps**3
print(f"   α₃ = κ×ε³ = {alpha3:.6e} rad = {math.degrees(alpha3)*3600:.4f} arcsec")

# ============ 2. 宇稱檢驗設計 ============
print(f"\n2. 宇稱檢驗設計")
print(f"""
檢驗 A: 阻挫邊帶狀區 vs 隨機場
  取 32 條阻挫邊, 每條 ±δ° 帶狀區
  比較帶內 vs 帶外嘅偏振角 ψ 分佈
  IDCM 預測: 帶內 ψ 有系統性偏離 Δψ ≈ α_chiral

檢驗 B: 冷-冷邊 vs 熱-熱邊 (直接宇稱測試)
  16 條冷-冷邊 vs 16 條熱-熱邊
  如果手性: 兩組偏振旋轉方向相反!
  Δψ(cold-cold) ≈ -Δψ(hot-hot)
  → 直接測試宇稱違反

檢驗 C: 節點手性相關
  60 節點: 每個節點嘅偏振角 ψ
  計算 ψ 同節點手性 (冷/熱) 嘅相關
  IDCM 預測: 冷節點 +α, 熱節點 -α (或相反)
""")

# ============ 3. 靈敏度需求 ============
print(f"3. 靈敏度需求")
# CMB-S4 目標: σ(α) ~ 0.01° = 36 arcsec = 1.7e-4 rad
# IDCM 預測: α ~ 1e-5 rad
sigma_s4 = math.radians(0.01)
print(f"   CMB-S4 σ(α) ≈ 0.01° = {sigma_s4:.2e} rad")
print(f"   IDCM 預測 α ≈ {alpha1:.2e} rad")
print(f"   S/N = {alpha1/sigma_s4:.2f} → 需要更高靈敏度 或 累積統計")
print(f"   但!! 如果用 32 條邊累積: S/N × √32 = {alpha1/sigma_s4*math.sqrt(32):.1f}")

# ============ 4. 與文獻對比 ============
print(f"\n4. 文獻對比")
print(f"""
   Planck 2018: 全域偏振旋轉 |α| < 1° (95% CL)
   → IDCM 預測 α ~ 1e-5 rad = 0.0006° << 1° ✅ 一致!
   
   BICEP/Keck: B-mode 冇偵測到原初引力波
   → IDCM 預測 B-mode 唔係來自引力波, 而係晶格手性散射
   → 小尺度 B-mode 可能有異常! (可檢驗)
   
   ACT/SPT: 冇全域宇稱違反
   → 但冇做「阻挫邊帶狀」檢驗! 呢個係新統計
""")

# ============ 5. 可證偽預測 ============
print(f"5. 可證偽預測")
print(f"""
   P1. 32 條阻挫邊 ±5° 帶內, 偏振角 ψ 有系統性偏離
      偏離量級 ~ 1e-5 rad (需累積統計)
   P2. 冷-冷邊 vs 熱-熱邊: 偏振旋轉方向相反 (宇稱違反!)
   P3. 60 節點附近: 偏振角同節點手性 (冷/熱) 相關
   P4. 小尺度 B-mode 有異常 (晶格手性散射, 非引力波)
   
   證偽條件:
   - 如果 32 條阻挫邊帶內冇任何偏振異常 (帶內=帶外)
   - 如果冷-冷/熱-熱邊偏振冇方向差異
   → IDCM 手性結構假設錯
""")

# ============ 保存 ============
import json
results = {
    "alpha_candidates_rad": {
        "eps5_32_60": alpha1,
        "eps5_4": alpha2,
        "kappa_eps3": alpha3
    },
    "rms_cold_spot": rms_cold,
    "prediction": "Polarization rotation ~1e-5 rad near frustration edges",
    "falsifiable": "No polarization anomaly in edge bands would falsify",
    "cmb_s4_sensitivity": "0.01 deg = 1.7e-4 rad (S/N needs stacking)"
}
os.makedirs('data', exist_ok=True)
with open('data/polarization_parity.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f"\n已保存 data/polarization_parity.json")
