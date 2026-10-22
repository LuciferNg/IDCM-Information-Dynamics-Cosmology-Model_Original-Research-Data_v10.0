"""
O72 自我質疑 05: 「生存閉合」H₀ 依賴性審計
=====================================================================
動機: docs/07 質疑 3 發現 H₀ 係隱藏自由參數。
      而家要查證「生存下嚟」嘅閉合 (BBN, V_Λ, CMB ℓ_m, 冷斑 A,
      D_app, 質量閉合) 到底有冇 H₀ 依賴 — 冇 H₀ 依賴先算真正獨立。

每個閉合要答:
  1. 公式有冇 H₀ (或 R_H = c/H₀, λ_sync, T_sync)?
  2. 如果冇 H₀, 係咪仍然成立?
  3. 如果有 H₀, 係咪用咗特定值 (72.59)?
"""
import numpy as np

phi = (1 + np.sqrt(5)) / 2

print("=" * 72)
print("生存閉合 H₀ 依賴性審計")
print("=" * 72)

# 用 grep 搵公式來源 (實際核查, 唔靠記憶)
import subprocess, os

base = os.path.expanduser("~/Projects/IDCM/IDCM-v10.0/open_problems_fresh")

def grep(pattern, path, maxlines=3):
    """搵 pattern 喺 path 入面嘅行"""
    r = subprocess.run(["grep", "-rn", pattern, path],
                       capture_output=True, text=True)
    lines = r.stdout.strip().split("\n")[:maxlines] if r.stdout.strip() else ["(冇搵到)"]
    return lines

print("\n--- 1. BBN η_B = 6.062e-10 ---")
for l in grep("6.062", f"{base}/bbn")[:3] + grep("6.062", f"{base}")[:2]:
    print(f"  {l[:150]}")

print("\n--- 2. V_Λ = 283.0821 (O62) ---")
for l in grep("283.08", f"{base}/o62_lambda_first_principles")[:3]:
    print(f"  {l[:150]}")

print("\n--- 3. CMB ℓ_m 峰值位置 ---")
for l in grep("44×(33", f"{base}/o9_high_ell_peaks")[:2] + grep("ℓ_5 = 1121", f"{base}")[:2]:
    print(f"  {l[:150]}")

print("\n--- 4. 冷斑 A = 134.2μK ---")
for l in grep("134.2", f"{base}/o42_independent_measurement_A")[:3]:
    print(f"  {l[:150]}")

print("\n--- 5. D_app(ℓ) ---")
for l in grep("D_app", f"{base}/o51_kchain_origin")[:3]:
    print(f"  {l[:150]}")

print("\n--- 6. Ω_DM/Ω_b = 13/2 ---")
for l in grep("13/2", f"{base}/o51_kchain_origin")[:2] + grep("13/2", f"{base}/bbn")[:2]:
    print(f"  {l[:150]}")

print()
print("=" * 72)
print("分析: 每個閉合嘅 H₀ 依賴")
print("=" * 72)
print("""
  1. BBN η_B: 需要查公式 (上面 grep 結果)
  2. V_Λ: F(γ)+44−F₈−B = 264.0821+44−21−4 — γ 係 K_Chain 譜 (冇 H₀)
     → 但 264.0821 = (1/6)κγ³ — κ 係 CY₃ 相交數 (冇 H₀) ✅
     → V_Λ 數值 283.0821 冇 H₀? (要確認單位/定義)
  3. CMB ℓ_m: 44×(33−C(9−m,2)) — 純整數公式, 冇 H₀ ✅
  4. 冷斑 A: 88×61/40 = 134.2 μK — 純結構, 冇 H₀ ✅
  5. D_app(ℓ): (44−44/4^ℓ)(R_H/44)(1+2φ⁻¹ℓ) — 有 R_H = c/H₀ ❌
     → D_app 依賴 H₀! 但 χ²=1.00 用咗 72.59?
  6. Ω_DM/Ω_b = 13/2: 比例, 冇 H₀ ✅
""")

print("=" * 72)
print("初步判決")
print("=" * 72)
print("""
  ✅ 冇 H₀ 依賴 (真正獨立):
     - CMB ℓ_m 峰值位置 (純整數)
     - 冷斑 A = 134.2 μK (純結構)
     - Ω_DM/Ω_b = 13/2 (比例)
     - V_Λ = 283.0821 (γ 譜 + κ, 冇 H₀ — 待確認)
     - 質量閉合 (γ_k 譜, 冇 H₀)

  ❌ 有 H₀ 依賴:
     - D_app(ℓ) (R_H 入面)
     - 所有 λ_sync/T_sync 系 (r_drag, hop, SYNC)

  → 剔除 H₀ 後, K_Chain 仍然有: CMB ℓ_m + 冷斑 A + Ω 比例 + V_Λ
  → 但呢啲係咪全部 44 系 re-label? 要逐個查:
     - CMB ℓ_m = 44×(33−C(9−m,2)) — 44 係輸入! 又係 44 re-label?
     - 冷斑 A = 88×61/40 — 88 = 2×44 輸入; 61 = L₁₀? 40 = ?
     - V_Λ = F(γ)+44−F₈−B — 44, F₈=21, B=4 全部結構輸入
""")
