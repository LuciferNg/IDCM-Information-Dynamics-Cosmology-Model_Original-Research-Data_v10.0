#!/usr/bin/env python3
"""
O57 九期 64: 推 1 — γ_n 譜統一結構 (ν-p6 ⊗ 輕子)
===================================================
探索: 中微子 (γ₆) 同輕子 (γ₁, γ₇, γ₂₀) 有冇統一嘅 γ_n 譜結構?

IDCM 已知:
  中微子 (p6): m_ν_τ = (γ₆v)²/M_comp, 世代 = φ-power
  輕子 (O54): m_e = M₀×γ₁×L₆/F₅ (0.16%)
             m_μ = M₀×γ₇×(Nd−Eₚ) (0.13%)
             m_τ = M₀×γ₂₀×(Nd−L₄) (0.34%)

γ_n = 4sin²(nπ/88), n=1..44

測試:
  1. γ_n 譜有冇 Lucas/Fibonacci 結構?
  2. γ₆ vs γ₁/γ₇/γ₂₀ 關係
  3. γ_n 譜嘅「世代」分組 (n=1,7,20 = 輕子; n=6 = 中微子?)
  4. 有冇統一代數公式?
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 九期 64: γ_n 譜統一結構")
print("=" * 72)

passed = 0
failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

# ============ 1. γ_n 譜 ============
print("\n[1] γ_n 譜 (n=1..44)")
gamma = {n: 4*math.sin(n*math.pi/88)**2 for n in range(1, 45)}
print(f"  γ₁ = {gamma[1]:.6f}")
print(f"  γ₆ = {gamma[6]:.6f}")
print(f"  γ₇ = {gamma[7]:.6f}")
print(f"  γ₂₀ = {gamma[20]:.6f}")
print(f"  γ₄₄ = {gamma[44]:.6f} (Nyquist)")

# γ_n 嘅小整數組合?
print(f"\n  γ_n 值:")
for n in [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 20, 22, 33, 44]:
    print(f"    γ_{n:2d} = {gamma[n]:.6f}")

# ============ 2. γ_n 同 φ 關係 ============
print("\n[2] γ_n 同 φ 關係")
# γ_n ≈ φ^k?
print(f"  φ⁻¹ = {phi**-1:.6f}")
print(f"  φ⁻² = {phi**-2:.6f}")
print(f"  φ⁻³ = {phi**-3:.6f}")
print(f"  φ⁻⁴ = {phi**-4:.6f}")
print(f"  φ⁻⁵ = {phi**-5:.6f}")

for n in [1, 2, 3, 6, 7, 20]:
    gn = gamma[n]
    # 揾最接近嘅 φ 冪
    best_k = None
    best_err = 999
    for k in range(-10, 1):
        err = abs(gn - phi**k)/gn
        if err < best_err:
            best_err = err
            best_k = k
    print(f"  γ_{n:2d} = {gn:.6f} ≈ φ^{best_k} = {phi**best_k:.6f} (誤差 {best_err*100:.1f}%)")

# ============ 3. 世代分組 ============
print("\n[3] 世代分組探索")
# 輕子: γ₁, γ₇, γ₂₀ (O54)
# 中微子: γ₆ (p6)
# 有冇模式?
print(f"  輕子 γ_n: 1, 7, 20")
print(f"  中微子 γ_n: 6")
print(f"  差: 7-1=6, 20-7=13, 6=γ₆ 指數")
print(f"  6 = B+2? {4+2}, 13 = L₄+6? {7+6}, 20 = 2L₅-2? {22-2}")

# n 值本身有冇結構?
print(f"\n  n 值結構:")
print(f"  1 = φ⁰? 7 = L₄? 20 = ? 6 = ?")
print(f"  7 = L₄ = 7 ✓ (Lucas)")
print(f"  20 = 5×4 = F₅×B? {5*4}")
print(f"  6 = 2×3 = 2N_gen? {2*3}")
print(f"  1 = 1 = φ⁰")

# ============ 4. 質量統一公式? ============
print("\n[4] 質量統一公式探索")
# 中微子: m_ν = (γ₆v)²/M_comp
# 輕子: m_l = M₀ × γ_n × (組合)
# 有冇 m_ν/m_l = f(γ)?

# m_ν_τ = 0.0536 eV, m_τ = 1776.86 MeV = 1.777e9 eV
m_nu_tau = 0.0536  # eV
m_tau = 1776.86e6  # eV
print(f"  m_ν_τ/m_τ = {m_nu_tau/m_tau:.3e}")
print(f"  (γ₆/γ₂₀)² = {(gamma[6]/gamma[20])**2:.3e}")
print(f"  (γ₆/γ₂₀)² × ? = {m_nu_tau/m_tau:.3e}")
print(f"  比: {(m_nu_tau/m_tau)/(gamma[6]/gamma[20])**2:.3e}")
print(f"  v²/M_comp/M₀ = {(246**2/3.6909e13)/(27.8553)}")
print(f"  v²/(M_comp×M₀) = {246**2/(3.6909e13*27.8553):.3e}")

# 統一: m_ν/m_l = (γ₆/γ_n)² × (v²/(M_comp·M₀)) × (1/組合)
print(f"\n  m_ν_τ/m_τ 分解:")
print(f"  (γ₆/γ₂₀)² = {(gamma[6]/gamma[20])**2:.6f}")
print(f"  v²/(M_comp·M₀) = {246**2/(3.6909e13*27.8553):.3e}")
print(f"  乘埋: {(gamma[6]/gamma[20])**2 * 246**2/(3.6909e13*27.8553):.3e}")
print(f"  目標: {m_nu_tau/m_tau:.3e}")
print(f"  比: {(gamma[6]/gamma[20])**2 * 246**2/(3.6909e13*27.8553)/(m_nu_tau/m_tau):.3f}")

# ============ 5. 總結 ============
print("\n" + "=" * 72)
print("九期 64 總結:")
print("=" * 72)
print(f"""
  γ_n 譜統一結構:
  ─────────────────────────────────
  1. γ_n = 4sin²(nπ/88) (n=1..44)
  2. 輕子: n=1,7,20; 中微子: n=6
  3. n 值: 7=L₄, 20=5×4=F₅×B, 6=2×3=2N_gen
  4. m_ν/m_l 分解: 睇上面

  開放: 統一公式需要更多約束
""")

results = {
    "test": "O57 九期 64: γ_n 統一",
    "gamma": {str(n): float(g) for n, g in gamma.items()},
    "m_nu_tau_ratio": float(m_nu_tau/m_tau),
    "passed": passed, "failed": failed
}
with open("data/64_gamma_spectrum.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 九期 64 完成!")
