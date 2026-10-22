"""
O72 自我質疑 04: H₀ 值選擇 — 最大嘅隱藏自由參數?
=====================================================================
動機: K_Chain 物理尺度 R_H = c/H₀ 依賴單一輸入 H₀。
      IDCM 用 H₀ = 72.59 (SH0ES 距離階梯), 但 Planck 用 H₀ = 67.36。
      宇宙學有 H₀ 張力 (5σ): 67.4 (CMB) vs 73.0 (距離階梯)。

質疑假說:
  H1: 如果 H₀ 變, K_Chain 嘅「閉合」仲成唔成立?
      → λ_sync, r_drag, T_sync, R_H 全部 ∝ 1/H₀
      → 如果 BAO r_drag = 147.44 Mpc 係「閉合」, 用 Planck H₀ 會變幾多?
  H2: 72.59 係咪「揀出嚟」嘅? 定係有結構原因?
      → 如果 72.59 係 SH0ES 值, 咁 IDCM 只係 fit 咗距離階梯
      → 但 O11 話 IDCM 預言 72.59 (Maser 幾何) — 呢個係 post-diction 定 prediction?
  H3: 如果 H₀ 唔係 72.59, 邊啲閉合死?
      → 逐個閉合計: 用 67.36, 68.0, 70.0, 72.59, 73.0, 74.0 掃描
"""
import numpy as np

c = 299792.458  # km/s
Gyr_s = 3.15576e16
Mpc_km = 3.085677581e19

print("=" * 72)
print("H₀ 掃描: 閉合量 vs H₀")
print("=" * 72)

def quantities(H0):
    R_H = c / H0                       # Mpc
    T_sync = 2*np.pi * Mpc_km / (H0 * Gyr_s)   # Gyr
    lam_sync = c * T_sync * Gyr_s / (88 * Mpc_km)  # Mpc
    r_drag_half = lam_sync / 2         # BAO 對應
    return R_H, T_sync, lam_sync, r_drag_half

targets = {
    "R_H": 4129.94,
    "T_sync": 84.64,
    "λ_sync": 294.88,
    "r_drag (λ_sync/2)": 147.44,
}

print(f"{'H₀':>8} | {'R_H':>10} | {'T_sync':>10} | {'λ_sync':>10} | {'r_drag':>10} | 閉合狀態")
print("-" * 80)
for H0 in [67.36, 68.0, 70.0, 72.59, 73.0, 74.0]:
    R_H, T_sync, lam_sync, r_drag = quantities(H0)
    # 檢查 BAO r_drag 觀測值 147.09±0.26 (Planck) 或 147.44?
    bao_ok = abs(r_drag - 147.44) < 0.5
    print(f"{H0:8.2f} | {R_H:10.2f} | {T_sync:10.3f} | {lam_sync:10.2f} | {r_drag:10.2f} | {'✅ 147.44' if bao_ok else '❌'}")

print()
print("=" * 72)
print("H1 分析: BAO r_drag 閉合對 H₀ 嘅敏感度")
print("=" * 72)
print(f"""
  IDCM: r_drag = λ_sync/2 = c·T_sync/176 = c·(2π/H₀)/176
       = π·c/(88·H₀) × (單位轉換)

  觀測: r_drag = 147.09 ± 0.26 Mpc (Planck 2020, 由 CMB fit)
       r_drag = 147.44 Mpc (DESI 2024, 假設 ΛCDM)

  如果 H₀ = 67.36 (Planck):
    r_drag(IDCM) = 147.44 × (72.59/67.36) = {147.44*72.59/67.36:.2f} Mpc
    → 距離觀測 147.09 偏差 {(147.44*72.59/67.36 - 147.09)/147.09*100:.1f}% ❌

  如果 H₀ = 72.59 (SH0ES):
    r_drag(IDCM) = 147.44 Mpc
    → 距離觀測 147.09 偏差 {(147.44-147.09)/147.09*100:.2f}% ✅
""")

print("=" * 72)
print("H2 分析: 72.59 係咪「揀」出嚟?")
print("=" * 72)
print("""
  72.59 來源:
    - 2020 年代 SH0ES 距離階梯後期值 (Riess et al.)
    - 唔係 Planck (67.36), 唔係 CCHP (69.8), 唔係 TRGB (69.6)
    - IDCM 選 72.59 而唔係其他值 — 點解?

  O11 (Maser) 聲稱: IDCM 預言 72.59, MCP XIII = 73.9±3.0 含 72.59
    → 但 72.59 本身係 post-diction 定 prediction?
    → 如果 IDCM 結構「需要」72.59 先閉合, 咁 72.59 就係 fit
    → 如果 IDCM 由 R_H 推 H₀, 咁 H₀ 先係預言

  🔴 關鍵: R_H = c/H₀ 係定義, 唔係推導!
    → 「R_H = c/H₀」冇獨立於 H₀ 嘅 R_H 來源
    → 即係 H₀ 仍然係輸入, 只係個名叫做「環頻率」
    → 呢個正正係 Q1 (re-label) 質疑嘅核心
""")

print("=" * 72)
print("H3: 如果 H₀ 係自由參數, IDCM 剩返幾多閉合?")
print("=" * 72)
print("""
  依賴 H₀ 嘅閉合 (H₀ 一變就死):
    R_H, λ_sync, r_drag, T_sync, 44-tone SYNC, hop = 6.70 Mpc
    D_app(ℓ) 距離, Maser H₀ 預言

  唔依賴 H₀ 嘅閉合 (純結構):
    γ_k 譜 (離散), Σγ=90/88, 946 拍頻, 87 原子
    φ 階梯, 33, 1496
    BBN η_B? (要查: η_B 有冇 H₀ 依賴)
    Ω_DM/Ω_b = 13/2 (比例, 冇 H₀)
    V_Λ = 283.0821? (要查: 有冇 H₀)

  → 如果 H₀ 係自由參數, 依賴 H₀ 嘅閉合全部係「1 參數 fit」
  → 剩返純結構閉合 — 但嗰啲 (90/88/946) 已經被證明係平凡恆等式!
  → 即係: 剔除 H₀ 後, K_Chain 冇剩返任何非平凡閉合 🔴
""")

print("=" * 72)
print("總結: H₀ 質疑")
print("=" * 72)
print("""
🔴 致命發現:
   [1] R_H = c/H₀ 係定義, 唔係推導 — H₀ 仍然係輸入
   [2] BAO r_drag 閉合只喺 H₀ ≈ 72.59 成立 — 用 Planck 67.36 偏差 ~8%
   [3] 72.59 係 SH0ES 值 — IDCM 選距離階梯而唔係 CMB, 冇結構原因
   [4] 剔除 H₀ 依賴後, K_Chain 冇剩返非平凡閉合 (90/88/946 係恆等式)

🟡 未質疑倒:
   - 如果 IDCM 有獨立 R_H 推導 (唔係 c/H₀), H₀ 就係預言
     → 但呢個未見 (O40 話 R_H = λ₁ 環頻率, 但仍以 c/H₀ 定義)
   - H₀ 張力本身 (67.4 vs 73.0) 可能支持「H₀ 唔係單一膨脹率」
     → 如果 H₀ 係「環頻率」, 咁 CMB/距離階梯分歧就係預期? (需要解釋)

結論: H₀ 選擇係 IDCM 最大嘅隱藏自由參數 — 必須有獨立 R_H 推導
      否則「零參數」claim 唔成立 (最少 1 參數: H₀)
""")
