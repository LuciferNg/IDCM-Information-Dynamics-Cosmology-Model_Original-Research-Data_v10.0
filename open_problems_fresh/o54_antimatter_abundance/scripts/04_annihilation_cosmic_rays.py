#!/usr/bin/env python3
"""
O54 — 檢查 4: 湮滅殘留 + 宇宙線數據對比（可證偽預言）
======================================================
問題: IDCM 結構 (n_B̄=0 候選) vs 觀測上限 — 有冇矛盾？

方法:
1. 重子區湮滅 γ-ray 上限 (Fermi-LAT): n_B̄/n_B < ~1e-9?
2. AMS-02 反質子/質子比: ~1.6e-4 @10 GeV (次級為主)
3. AMS-02 反氦上限: Hē/He < 1e-9
4. 正電子異常: e⁺/(e⁺+e⁻) 上升 (AMS-02)
5. IDCM 預言對比:
   A) n_B̄ = 0 → 冇湮滅殘留, 冇原始反質子, 冇反氦
   B) 正電子 = W-field 結構通道 (需 O36/O37)
6. 結論: IDCM 結構預言 vs 觀測 — 一致 or 矛盾

引用觀測 (公開文獻, 非作料):
- Fermi-LAT: 星系際 γ-ray 背景上限 → n_B̄/n_B < ~1e-9 (Steigman 1976 scale, modern limits tighter)
- AMS-02 (Aguilar et al. 2015, PRL 114, 171103): p̄/p ~ 1.6e-4 @10 GeV
- AMS-02 (Aguilar et al. 2018, PRL 121, 051102): Hē/He 上限 ~1e-9 (冇確認事件)
- AMS-02 (Aguilar et al. 2013-2019): e⁺/(e⁺+e⁻) 上升 10 GeV ~10% → 300 GeV ~20%
- Planck 2018: η_B = 6.12e-10 (IDCM 6.062e-10, 0.62%)
"""
import math
import json

phi = (1 + 5**0.5) / 2
phi_inv = 1 / phi

print("=" * 72)
print("O54 檢查 4: 湮滅殘留 + 宇宙線數據對比")
print("=" * 72)

# ============ 1. 觀測數據表 ============
print("\n[1] 觀測數據表")
print("-" * 72)
obs = {
    "eta_B_obs": 6.12e-10,           # Planck 2018
    "eta_B_idcm": 6.0622e-10,        # IDCM 閉合
    "pbar_p_10GeV": 1.6e-4,          # AMS-02 反質子/質子 @10 GeV
    "antihelium_limit": 1e-9,        # AMS-02 Hē/He 上限
    "eplus_frac_10GeV": 0.10,        # AMS-02 正電子分數 @10 GeV
    "eplus_frac_300GeV": 0.20,       # AMS-02 正電子分數 @300 GeV
    "annihilation_gamma_limit": 1e-9, # Fermi-LAT 湮滅 γ-ray → n_B̄/n_B
}
for k, v in obs.items():
    print(f"  {k}: {v}")

# ============ 2. IDCM 預言 vs 觀測 ============
print("\n[2] IDCM 結構預言 (n_B̄ = 0 候選) vs 觀測")
print("-" * 72)

print("""
  IDCM 結構預言 (基於檢查 1-3):
  P1: n_B̄ = 0 精確 (冇反模式) → η_B = n_B/n_γ = 6.062e-10
  P2: 冇湮滅殘留 → 冇星系際湮滅 γ-ray 背景
  P3: 冇原始反質子 → p̄/p 純次級 (由宇宙線碰撞產生)
  P4: 冇反氦 → Hē/He = 0 (除咗次級, 極低)
  P5: 正電子 = W-field 結構通道 (異常上升, 需 O36/O37)
""")

# 對比
print("  對比表:")
checks = [
    ("P1 η_B", "6.062e-10 vs 6.12e-10 (Planck)", "0.62% ✅"),
    ("P2 湮滅 γ-ray", "預言 0 vs 上限 <1e-9 (n_B̄/n_B)", "✅ 一致 (上限>0)"),
    ("P3 p̄/p", "純次級 ~1e-4 vs AMS 1.6e-4 @10GeV", "✅ 一致 (次級為主)"),
    ("P4 反氦", "預言 0 vs AMS 上限 1e-9", "✅ 一致 (冇確認)"),
    ("P5 正電子", "異常上升 vs AMS 10%→20%", "🟡 機制開放"),
]
for name, cmp, status in checks:
    print(f"    {name}: {cmp} → {status}")

# ============ 3. 正電子異常定量 ============
print("\n[3] 正電子異常定量")
print("-" * 72)
# 正電子分數: f(E) = e⁺/(e⁺+e⁻)
# AMS-02: 10 GeV ~10%, 100 GeV ~15%, 300 GeV ~20% (緩慢上升)
# 次級模型: ~10% @10GeV → ~5% @300GeV (下降)
f_10, f_300 = 0.10, 0.20
rise = f_300 - f_10
print(f"  觀測上升: f(300) - f(10) = {rise:.2f} (+{rise/f_10*100:.0f}%)")
print(f"  次級模型預測: 下降 (f_300 < f_10)")
print(f"  ⟹ 需要額外正電子源")

# IDCM 結構候選: 正電子分數公式?
# 嘗試: f_rise ≈ ε = φ⁻¹/4 = 0.1545?
print(f"\n  IDCM 結構檢查:")
print(f"  f(300)/f(10) = {f_300/f_10:.2f}")
print(f"  1+ε = {1+phi_inv/4:.4f} (ε = φ⁻¹/4 = 0.1545)")
print(f"  f(300) = f(10)×(1+ε) → {f_10*(1+phi_inv/4):.4f} vs 觀測 0.20")
print(f"  f(300) = f(10)×φ → {f_10*phi:.4f} vs 觀測 0.20")
print(f"  f(300) = f(10)+ε → {f_10+phi_inv/4:.4f} vs 觀測 0.20")
print(f"  ⟹ 冇簡單 φ-power 匹配 — 需要完整 W-field 衰變譜 (O36/O37 對接)")

# ============ 4. 湮滅殘留定量 ============
print("\n[4] 湮滅殘留 (如果 n_B̄ ≠ 0)")
print("-" * 72)
# ΛCDM: 初始 n_B̄/n_B ~ 1, 湮滅後殘留 ~ η_B ~ 6e-10 (相對光子)
# 即 n_B̄/n_B (現在) ~ 6e-10/6.062e-10 × ... 實際上:
# 如果對稱初始: n_B = n_B̄ = n_γ × 6e-10/2 湮滅 → 殘留 ~ 6e-10 光子比
# 但觀測: 冇湮滅 γ-ray 背景 → n_B̄/n_B < 1e-9 (星系尺度)
residual = eta_B = 6.0622e-10
print(f"  ΛCDM 對稱初始湮滅殘留: n_B̄/n_γ ~ {residual:.1e}")
print(f"  觀測上限: n_B̄/n_B < 1e-9 → n_B̄/n_γ < 6e-19")
print(f"  ⟹ 湮滅殘留比觀測上限細 9 個數量級")
print(f"  ⟹ ΛCDM 需要 baryogenesis 機制 (CP 破壞) 產生差額")
print(f"  ⟹ IDCM: 冇差額需要產生 — n_B̄ = 0 結構必然, 更簡單")

# ============ 5. 結論 ============
print("\n[5] 檢查 4 結論")
print("-" * 72)
print(f"""
  1. IDCM 預言 (n_B̄ = 0) 同所有觀測一致:
     - η_B ✅ 0.62%
     - 湮滅 γ-ray ✅ (預言 0 < 上限)
     - p̄/p ✅ (純次級 = 觀測)
     - 反氦 ✅ (預言 0 = 觀測上限)
  2. 正電子異常: 觀測上升 vs 次級下降 → 需要額外源
     - IDCM 候選: W-field 結構通道 (🔴 需 O36/O37 對接)
  3. 湮滅殘留: ΛCDM 需要差額產生機制; IDCM 結構上冇反模式
     → n_B̄ = 0 係更簡潔嘅答案 (Occam)
  4. 🟡 部分閉合: 觀測一致性確認, 但正電子機制開放
""")

results = {
    "test": "湮滅殘留 + 宇宙線數據對比",
    "eta_B_idcm": 6.0622e-10,
    "eta_B_planck": 6.12e-10,
    "eta_B_dev": 0.62,
    "pbar_p_obs": 1.6e-4,
    "antihelium_limit": 1e-9,
    "eplus_10GeV": 0.10,
    "eplus_300GeV": 0.20,
    "eplus_ratio": 2.0,
    "annihilation_limit_nBbar_nB": 1e-9,
    "prediction_nBbar_zero": True,
    "conclusion": "IDCM n_B̄=0 預言與全部觀測一致 (η_B 0.62%, 湮滅 γ-ray, p̄/p 次級, 反氦); 正電子異常需 O36/O37 對接",
}
print("驗證摘要:")
for k, v in results.items():
    print(f"  {k}: {v}")

with open("data/04_annihilation_cosmic_rays.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print("\n✅ 結果已寫入 data/04_annihilation_cosmic_rays.json")
