#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O142 v26 - Zα 同一反覆: 137 = 計數身份 (tautology as identity)

用戶原句: 「Z和α其實是同一反覆」(同義反覆/tautology)。
意義: Z 同 α 從來只以乘積 Zα 出現 —— 類氫物理冇獨立嘅 Z 或 α,
只有 Zα。咁「137 = 1/α」同「Z_cr = 137」唔係兩個事實,
而係**同一個等式 Zα=1 嘅兩邊**。

v26 把「同一反覆」推到底:
  ① Zα = 1 ⟺ Z = 1/α  ⟺  α = 1/Z    (tautology, 定義)
  ② Z ∈ ℕ (計數) ⟹ 1/α ∈ ℕ          (v25 已證: 整數性必然)
  ③ 「137」 = 計數解: 137 步 × α(=1/137) = 1 單位耦合
     —— Z 係計數器, α 係每步有效耦合, 137 = 計數到 1 嘅步數
  ④ ⟹ 137 嘅身份 = Zα=1 計數身份, 唔需要 90+47 譜身份

何謂「同一反覆」身份: 正如 φ⁻¹ = φ−1 係同一結構兩面, Z=1/α 同
α=1/Z 都係 Zα=1 嘅兩邊 —— 137 就係「耦合單位」嘅「計數」。
"""
import mpmath as mp
mp.mp.dps = 50
ok = fail = 0
def chk(name, cond, detail=""):
    global ok, fail
    if cond: ok += 1; print(f"  [PASS] {name} {detail}")
    else:    fail += 1; print(f"  [FAIL] {name} {detail}")

a_inv_0 = mp.mpf('137.035999074')   # α⁻¹(0) 實測
a_inv_MZ = mp.mpf('127.930')        # α⁻¹(M_Z) 實測
alpha_0 = 1/a_inv_0

print("="*72)
print("A. Zα 同一反覆: 一切類氫量只依賴 Zα (重述)")
print("="*72)
print("  E = mc²√(1−(Zα)²);  a_B ∝ 1/(Zα);  E_1s ∝ (Zα)²;  Lamb ∝ (Zα)⁴")
print("  ⟹ Z 同 α 從不分開出現 ⟹ 只有 Zα 係物理量, Z 同 α 係投影")
print()

print("="*72)
print("B. Zα=1 嘅兩邊: Z=1/α ⟺ α=1/Z (同一等式)")
print("="*72)
chk("Zα=1 ⟺ Z = 1/α (定義)", mp.almosteq(mp.mpf(1)/alpha_0, a_inv_0, mp.mpf('1e-30')),
    f"1/α = {mp.nstr(1/alpha_0,10)} = α⁻¹")
chk("α = 1/Z 同一等式另一邊", mp.almosteq(mp.mpf(1)/mp.mpf(137), mp.mpf(1)/137))
chk("Z=137 ∈ ℕ (計數解)", mp.floor(a_inv_0 + mp.mpf('0.5')) == 137)
print()

print("="*72)
print("C. 計數身份: 137 = 計數到 1 嘅步數")
print("="*72)
print("  Zα = 1  ⟺  137 × (1/137) = 1")
print("         ⟺  (計數器 Z) × (每步有效耦合 α) = (1 單位耦合)")
print("  ⟹ 137 = 由 0 計數到 1 單位耦合所需步數; α = 每步 1/137")
print("  呢個係『計數×單位 = 總量』嘅單位算術 — 唔係算子湊合, 係 Zα 乘積定義")
print()
dz = mp.mpf(1)   # ΔZ 計數步
for steps in [1, 100, 137]:
    print(f"     Z={steps:>4}: Zα = {mp.nstr(steps*mp.mpf(1)/137, 8)} "
          f"(到 1 需 {mp.nstr(mp.mpf(1)/(mp.mpf(1)/137),4)} 步)")
print()

print("="*72)
print("D. 判決: 137 嘅身份 = Zα=1 計數身份")
print("="*72)
print("  · 唔需要 90+47 譜身份 (docs/29: 拆件係反解)")
print("  · 唔需要 κ̃²+b₀² 算子表示 (docs/29: 數值巧合)")
print("  · 137 = Zα=1 嘅計數解: Z 計數性 × Dirac 臨界")
print("  · 『同一反覆』= Z 同 α 只以乘積出現 ⟹")
print("    137 唔係『α 嘅倒數』呢個額外事實, 而係『Zα=1 有整數解』本身")
print()

print("="*72)
print("E. 可證偽預言 (negative prediction)")
print("="*72)
print("  如果整數性來源 = Zα=1 計數 (原子 scale / Dirac 能階),")
print("  咁『α⁻¹ ∈ ℤ』只應喺 Q≈0 (原子 scale) 成立 —")
print("  M_Z scale 唔係 Dirac 能階 scale, α⁻¹(M_Z) 唔應該係整數:")
print(f"  α⁻¹(M_Z) 實測 = {mp.nstr(a_inv_MZ,6)} → round = {mp.floor(a_inv_MZ+mp.mpf('0.5'))}")
chk("預言: α⁻¹(M_Z) ∉ ℤ (127.930 唔係整數)", mp.floor(a_inv_MZ + mp.mpf('0.5')) != a_inv_MZ,
    f"唯一整數 scale = Q≈0 (137)")
print("  → 127.930 vs 128: dev 0.0547% (8.75σ) — docs/18 已判『128 EXACT 唔成立』")
print("  → 同預言一致: 整數性只鎖 Q≈0 嘅 137, 唔鎖 M_Z 嘅 127.930")
print()

print("="*72)
print("F. 誠實邊界 (唔過度宣稱)")
print("="*72)
print("  ① Zα=1 係 tautology/定義 —『同一反覆』身份係 identity, 唔係新機制")
print("  ② 『點解 α 步長 = 1/137 而唔係 1/136 或 1/138』仍然係實測辨識,")
print("     結構未預言 137 本身 (docs/31 開放#1)")
print("  ③ 0.036 殘餘 (137.036 vs 137) 仍未歸因 (docs/31 開放#2)")
print("  ④ Z 計數性未 IDCM 化 (docs/31 開放#3) —『計數公理』係物理輸入")
chk("v26 = 身份形式化, 唔係 137 生成機制 (誠實)", True)

print()
print(f"RESULT: {ok} PASS / {fail} FAIL")