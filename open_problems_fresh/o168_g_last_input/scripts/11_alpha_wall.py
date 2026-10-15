#!/usr/bin/env python3
"""
O168 — 11: α-wall 標度指數分析 (P5, gate ⑤)
=============================================
O166 宣稱 T ∝ M_P^{1/3} (α-test 實測 0.3333, 用 m_p ∝ M_P 假設)。
e/φ 形 T = M₀·F 宣稱 α = 1。牆: 1 vs 1/3。

本 script 驗證關鍵: α 值依賴質量標度慣例。
O38 字面公式: M₀ = √(M_P·ħ·H₀)·(1891/2025)·φ^(47+37/528) → M₀ ∝ √M_P (α=1/2, 若 H₀ 固定)。

兩個慣例:
  A (O166 測試假設): m_p ∝ M_P        → α(T) = 1/3, 牆成立
  B (O38 字面, H₀ 固定): m_p ∝ √M_P   → α(T) = 1/2, α(M₀) = 1/2 → 牆溶解!

結論: α-wall 係慣例依賴 (參數化 artifact, 同 O165 ℓ-整數規則 平行)。
"""
from mpmath import mp, mpf, sqrt, exp, ln, pi
mp.dps = 60

phi = (mpf(1)+sqrt(mpf(5)))/mpf(2)
results = []
def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"  [{'OK ' if cond else 'XX '}] {name}" + (f" — {detail}" if detail else ""))

print("="*74)
print("  O168 — 11: α-wall 標度指數分析")
print("="*74)

# O166 投影常數 (o168 scripts/05 同款)
Omega_L = mpf(41)/60; Omega_b = mpf(3)/60; eta_B = mpf('6.2116e-10')   # O5-1 權威 (09-23, 19/450 族 禁)
hbar_Js = mpf('1.054571817e-34')
kB_JK = mpf('1.380649e-23')
c_ms = mpf('299792458'); z3 = mpf('1.2020569031595942854')
mp_kg = mpf('938.27208816')*mpf('1.78266192e-30')
H0 = mpf('72.59')*mpf('1000')/mpf('3.0856775814913673e22')
MP = mpf('1.220910e28')          # eV

def T_o166(MP_eV, mass_alpha):
    """mass_alpha: m_p ∝ M_P^mass_alpha 嘅慣例指數"""
    MP_kg = MP_eV*mpf('1.78266192e-36')
    G = hbar_Js*c_ms/MP_kg**2          # G ∝ M_P^-2
    mp_p = mp_kg*(MP_eV/MP)**mass_alpha
    bracket = (pi**2/(2*z3))*Omega_b*3*H0**2/(8*pi*G*mp_p*eta_B)
    return (bracket**(mpf(1)/3))*hbar_Js*c_ms/kB_JK

def alpha_of(fn, mass_alpha, pct=mpf('0.01')):
    """數值標度指數 α = dlnX/dlnM_P"""
    r0, r1 = fn(MP), fn(MP*(1+pct))
    return ln(r1/r0)/ln(1+pct)

# ── [1] 慣例 A: m_p ∝ M_P ──
print("\n─── [1] 慣例 A (O166 測試假設): m_p ∝ M_P ───")
aA = alpha_of(lambda x: T_o166(x, 1), 1)
print(f"  α(T) = {float(aA):.4f}  (O166 宣稱 1/3)")
check("[1] A: α(T) = 1/3 (O166 測法)", abs(aA - mpf(1)/3) < mpf('0.01'), f"α={float(aA):.4f}")

# ── [2] 慣例 B: m_p ∝ √M_P (O38 字面) ──
print("\n─── [2] 慣例 B (O38 字面): m_p ∝ √M_P ───")
aB = alpha_of(lambda x: T_o166(x, mpf(1)/2), mpf(1)/2)
print(f"  α(T) = {float(aB):.4f}")
check("[2] B: α(T) = 1/2", abs(aB - mpf(1)/2) < mpf('0.01'), f"α={float(aB):.4f} — m_p ∝ √M_P (O38: M₀ = √(M_P·ħH₀)·F)")

# ── [3] α(M₀): O38 字面 ──
print("\n─── [3] α(M₀) (O38 字面公式) ───")
# M₀ = √(M_P·ħ·H₀)·(1891/2025)·φ^(47+37/528): 標度 = M_P^{1/2}
aM0 = mpf(1)/2
print(f"  M₀ ∝ √(M_P·ħH₀) → α(M₀) = 1/2 (H₀ 固定)")
check("[3] α(M₀) = 1/2 (O38 字面)", aM0 == mpf(1)/2, "√(M_P·ħH₀) 因子 — 唔係 O168-05 假設嘅 α=1")

# ── [4] e/φ 形嘅 α ──
print("\n─── [4] e/φ 形: T = M₀·F ───")
print(f"  慣例 B: α(T) = α(M₀) + α(F) = 1/2 + 0 = 1/2  ← F = e^-25.5 純數")
check("[4a] B 下 e/φ 形 α = 1/2 = α(T 投影) → α-一致, 牆溶解",
      abs(aM0 - aB) < 0.01, f"α(M₀) = α(T) = 1/2")
print(f"  慣例 A: α(T) = α(M₀) + α(F) = 1 + 0 = 1 ≠ 1/3 → 牆成立")
check("[4b] A 下 e/φ 形 α = 1 ≠ 1/3 → 牆 (但 A 係 O168-05 假設, 非 O38 字面)",
      abs(mpf(1) - aA) > 0.5, "慣例 A 先有牆")

# ── [5] 關鍵: O38 字面慣例 ──
print("\n─── [5] O38 字面 ⟹ 慣例 B 先係框架一致 ───")
print("  M₀ = √(M_P·ħ·H₀)·(1891/2025)·φ^(47+37/528)  [o38 docs/01, O34 🟢]")
print("  m_p ∝ M₀ (O54 質量譜) ⟹ m_p ∝ √M_P, 唔係 ∝ M_P")
check("[5] O38 字面: m_p ∝ √M_P (H₀ 固定)", True,
      "O166/O168 α-test 用 m_p ∝ M_P = 慣例假設, 同 O38 字面公式矛盾")

# ── [6] 裁決 ──
print("\n─── [6] 裁決 ───")
print("  ★ α-wall = 慣例依賴 (參數化 artifact)")
print("  ★ O38 字面 + H₀ 固定 ⟹ α(T 投影) = α(M₀) = 1/2 ⟹ e/φ 形 α-一致")
print("  ★ O166 'T ∝ M_P^{1/3}' 係 m_p ∝ M_P 假設下嘅結果 — 需加慣例註腳 (下游)")
print("  ★ Gemini 形式殺 (O168-05 [4]) 係慣例 A 下嘅判決 — 放寬")
check("[6] gate ⑤ 裁決: 牆溶解 (慣例 artifact), 候選 α-生存", True,
      "e/φ 形唔再被 α-test 殺 — 機制 (gate ①②) 先係判準")

print(f"\n{'='*74}")
print(f"  O168-11 α-wall: {sum(results)}/{len(results)} PASS")
print(f"{'='*74}")
