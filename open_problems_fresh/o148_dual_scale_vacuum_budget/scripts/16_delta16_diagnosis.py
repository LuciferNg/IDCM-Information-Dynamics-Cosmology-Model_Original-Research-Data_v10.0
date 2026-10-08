#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O148 scripts/16 — δ16 偏移診斷 (S14)
=====================================
問題: 三個獨立 CMB 實驗 (Planck/SPT-3G/ACT DR6) 嘅 Ω_c h² 全部低過 IDCM 16/60·h_cmb²
      ACT DR6 (±0.001 最緊): 0.118 → +3.17σ

候選偏移源:
 (A) 閘極 κ = γ_max⁻² = 1/16 太闊 → n≥3 隱藏應該更深?  κ' = γ_max⁻³ = 1/64
 (B) 16 份額本身 → 15.1 (ACT 中心換算) 或 15 = B²−1
 (C) h 三投影: h_cmb 0.67407 / h_lad 0.73130 / h_o1700 0.71157 (O127)
 (D) IDCM Ω_c h² 嘅定義: κ⁻¹ = B² 係「份額分子」, 唔係 Ω_c h² 本身:
     其實 O214 用 Ω_c = 16/60 → omch2 = (16/60)·h² 係一個「ΛCDM 字典映射」 (docs/02),
     但 IDCM 結構份額可能唔係咁直接 translate — 呢個要釐清.

方法: 用 exact Fraction, 唔用 float fit.
"""
from fractions import Fraction

h_cmb = Fraction(67407112, 100000000)   # 0.67407112
h_lad = Fraction(73130, 100000)          # 0.73130  (O127 第二投影)
h_o17 = Fraction(71157, 100000)          # 0.71157  (O127 第三投影)

# 實驗中心値 (官方)
OBS = {
    "planck":  (Fraction(1200, 10000),  Fraction(12, 10000)),    # 0.1200 ± 0.0012
    "spt3g":   (Fraction(1188, 10000),  Fraction(2, 1000)),      # 0.1188 ± 0.0020
    "act":     (Fraction(118, 1000),    Fraction(1, 1000)),      # 0.118 ± 0.001
}

# ---- 候選 A: κ' = γ_max⁻³ (n≥4 閘走) ----
# 原本: κ = γ_max⁻² = 1/16 ⟹ DM 份額分子 = 16 = κ⁻¹
# 如果閘極係 γ_max⁻³: DM 分子 = κ⁻¹ 唔再係 16...
# 閘極語義: 「可見」= weight > κ, 「隱藏」= weight < κ
# e⁻ⁿ < κ ⟺ n > ln(1/κ). κ=1/16 → ln16 = 2.77 → n≥3 隱藏
# κ=1/64 → ln64 = 4.16 → n≥4 隱藏 (更深閘極 → 隱藏更多 → 份額更大, 錯方向)
# κ=1/4  → ln4 = 1.39 → n≥2 隱藏 (更淺 → 份額細啲, 啱方向!)
print("""
=== 候選 A: 閘極深度 ===
語義: 隱藏份額 = Σ e⁻ⁿ for n ≥ n_gate (正規化到可觀測總和)
κ = γ_max⁻² = 1/16 ⟹ e⁻ⁿ < κ ⟺ n ≥ 3 (n=3: e⁻³=0.0498 < 0.0625 ✓)
""")

def hidden_fraction(n_gate):
    """Σ_{n≥n_gate} e⁻ⁿ / Σ_{n≥1} e⁻ⁿ  (全譜正規化)"""
    # Σ_{n≥1} e⁻ⁿ = e⁻¹/(1−e⁻¹)
    # Σ_{n≥N} e⁻ⁿ = e⁻ᴺ/(1−e⁻¹)
    from decimal import Decimal, getcontext
    getcontext().prec = 30
    e = Decimal(1).exp()
    total = e**(-1) / (1 - e**(-1))
    hid = e**(-n_gate) / (1 - e**(-1))
    return hid / total

for ng in [1, 2, 3, 4]:
    f = hidden_fraction(ng)
    print(f"  n_gate = {ng}: 隱藏份額 = {float(f):.6f}  (目標 ≈ {float(Fraction(16,60)):.4f} = 16/60)")

# e⁻ⁿ 求和閉式: f(n_gate) = e^-(n_gate-1) — 精確驗證
from decimal import Decimal, getcontext
getcontext().prec = 30
e = Decimal(1).exp()
print(f"\n  閉式檢查: f(ng) = e^-(ng-1): f(2) = {float(e**(-1)):.6f}, f(3) = {float(e**(-2)):.6f}, f(4) = {float(e**(-3)):.6f}")
print(f"  目標 16/60 = {float(Fraction(16,60)):.6f}")
print(f"  ⟹ 冇任何整數 n_gate 啱好出 16/60 = 0.2667")
print(f"  ⚠️ O214/O163「e⁻ⁿ < κ ⟺ n≥3」係『閘極判準』(邊啲模態隱藏), 唔係『份額計算法』")
print(f"  ⟹ 份額 = κ⁻¹/(Σγ_odd+κ⁻¹) = 16/(44+16) = 16/60 — 縮放倒數, 唔係 e⁻ⁿ 求和")
print(f"  ⟹ 候選 A (閘極深度) 唔係 δ16 來源 — 語義已釐清, 份額計算法不變")

# ---- 候選 B: 15 vs 16 ----
print("""
=== 候選 B: 份額分子 15 vs 16 ===
""")
act_omch2, act_err = OBS["act"]
# ACT Ω_c 份額 (用 ACT 自己 h): Ω_c = omch2/h²
h_act = Fraction(6843, 10000)  # 68.43 km/s/Mpc → 0.6843
act_omega_c = act_omch2 / h_act**2
print(f"  ACT Ω_c 份額 = 0.118/{float(h_act)**2:.6f} = {float(act_omega_c):.5f} = {float(act_omega_c*60):.2f}/60")
print(f"  ⟹ ACT 中心 ≈ {act_omega_c*60} /60 (份額分子 ≈ 15.14)")
print(f"  16 vs 15.14: 差 {abs((16/60-float(act_omega_c))/float(act_omega_c))*100:.2f}%")

for num in [15, 16]:
    omch2 = Fraction(num, 60) * h_cmb**2
    s = (float(omch2) - 0.118) / 0.001
    print(f"  Ω_c = {num}/60 → omch2 = {float(omch2):.6f} vs ACT 0.118±0.001 → {s:+.2f}σ")

# ---- 候選 C: h 投影 ----
print("""
=== 候選 C: h 三投影 ===
""")
for name, h in [("h_cmb", h_cmb), ("h_lad", h_lad), ("h_o1700", h_o17)]:
    omch2 = Fraction(16, 60) * h**2
    s_act = (float(omch2) - 0.118) / 0.001
    s_pl  = (float(omch2) - 0.1200) / 0.0012
    print(f"  {name} = {float(h):.6f}: Ω_c h² = {float(omch2):.6f} → ACT {s_act:+.2f}σ, Planck {s_pl:+.2f}σ")

# ---- 候選 D: 字典映射問題 ----
print("""
=== 候選 D: 「份額」vs「物理密度」字典映射 ===
IDCM 10 份額: 3:16:41 /60 係「能量份額」 (Σγ 預算)
ΛCDM Ω_c h² = ρ_c/(critical density) × h² 係「物理密度」 (有 h²)
O214 docs/02 嘅映射: Ω_c = 16/60 → omch2 = (16/60)·h²
但如果 IDCM 嘅「16/60」係「譜能量份額」而唔係「ΛCDM 密度份額」,
咁 omch2 = (16/60)·h² 可能唔係正確 translate...
測試: 邊個 translate 啱 ACT?
a) omch2 = (16/60)·h_cmb²   = 0.121166  → ACT +3.17σ
b) omch2 = (16/60)·h_ACT²   = 0.12486   → ACT +6.9σ (錯方向!)
c) omch2 用「份額×密度」= (16/60)·(h²/Ω_γ·...)? → 需要完整字典
""")

print("""
=== 判決摘要 ===
(A) e⁻ⁿ 閘極: ✅ 語義釐清 — 「e⁻ⁿ < κ ⟺ n≥3」係『閘極判準』(邊啲模態隱藏),
     唔係『份額計算法』。份額 = κ⁻¹/(Σγ_odd+κ⁻¹) = 16/60 係縮放倒數, 唔係 e⁻ⁿ 求和。
     冇整數 n_gate 出 0.2667 — 但 0.2667 = 16/60 位於 f(2)=0.368 同 f(3)=0.135 之間!
     後續: 如果「份額」有 e⁻ⁿ 級數根源, κ⁻¹ 純倒數可能係近似——但 O214 定義層已定案,
     呢度唔改 (無新證據前唔好重推已閉合 O163/O165)
(B) 份額分子: ACT 中心 ≈ 15.14/60 — 16 高 5.8%; 但 15/60 = −4.41σ 更差!
     ⟹ 構造分子 {15,16} 都唔喺 ACT ±2σ 內 (15 → −4.4σ, 16 → +3.2σ)
     ⟹ δ16 唔係『16 份額本身錯』 — 冇整數份額分子啱 ACT
(C) h 投影: h_cmb 係三投影中最接近 ACT Ω_c h² 嘅 (0.1212 vs 0.1249/0.1350)
     ⟹ h_cmb 收斂方向正確; 但 δ16 (+3.17σ) 同 H₀ 偏差 (−3.79σ) 同方向!
     ⟹ δ16 主因候選 = h 世界 (Hubble 張力: IDCM 企 Planck 側 67.4, ACT+DESI 68.43)
(D) 字典映射: (16/60)·h² 直接用 h_cmb 係最保守; 用 ACT h 會更差 (6.9σ — 方向錯)
     但「份額」定義層面嘅 translate 可能本身就要修正 — 需要完整 IDCM↔ΛCDM 密度字典
""")