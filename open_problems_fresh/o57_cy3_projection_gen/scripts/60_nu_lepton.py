#!/usr/bin/env python3
"""
O57 八期 60: 推 1 — 中微子 p6 vs 帶電費米子關係
=================================================
用戶: 中微子喺 IDCM 唔係 seesaw → p6 機制已確認 (scripts/59)

而家推: 帶電費米子 (e, μ, τ) 同中微子 (ν_e, ν_μ, ν_τ)
有咩結構關係?

IDCM 已知:
  輕子質量 (O54): m_e = M₀×γ₁×L₆/F₅ (0.16%)
                 m_μ = M₀×γ₇×(Nd−Eₚ) (0.13%)
                 m_τ = M₀×γ₂₀×(Nd−L₄) (0.34%)
  中微子 (p6): m_ν_τ = (γ₆v)²/M_comp (0.66%)
              m_ν_μ = m_ν_τ·φ⁻¹
              m_ν_e = m_ν_τ·φ⁻²

測試:
  1. γ₆ (p6) 同 γ₁/γ₇/γ₂₀ (輕子) 嘅關係
  2. m_ν/m_l 比 (Dirac 比?)
  3. 世代結構: ν 用 φ-power, 輕子用 γ_n 組合
  4. 有冇統一公式?
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 八期 60: ν-p6 vs 帶電輕子")
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

# ============ 1. 已知質量 ============
print("\n[1] 已知 IDCM 質量")
# 輕子 (O54)
M0 = 27.8553  # MeV (scripts/55 校準)
gamma = {n: 4*math.sin(n*math.pi/88)**2 for n in range(1, 45)}
L6, F5 = 18, 5
Nd = 44
m_e_MeV = M0 * gamma[1] * L6 / F5
print(f"  m_e = M₀×γ₁×L₆/F₅ = {m_e_MeV:.4f} MeV (SM 0.511)")
print(f"  γ₁ = {gamma[1]:.6f}")

# 中微子 (p6)
m_nu_tau = 0.0536  # eV
m_nu_mu = m_nu_tau * phi**-1
m_nu_e = m_nu_tau * phi**-2
print(f"  ν_τ = {m_nu_tau:.4f} eV, ν_μ = {m_nu_mu:.4f} eV, ν_e = {m_nu_e:.4f} eV")

# ============ 2. γ₆ 同 γ₁ 關係 ============
print("\n[2] γ₆ vs γ₁ (p6 同輕子基線)")
gamma6 = gamma[6]
gamma1 = gamma[1]
print(f"  γ₆ = {gamma6:.8f}")
print(f"  γ₁ = {gamma1:.8f}")
print(f"  γ₆/γ₁ = {gamma6/gamma1:.6f}")
# 有冇 Lucas/Fibonacci?
print(f"  γ₆/γ₁ vs Lucas:")
for n, Ln in enumerate([2,1,3,4,7,11,18,29,47,76,123,199]):
    for m, Lm in enumerate([2,1,3,4,7,11,18,29,47,76,123,199]):
        if abs(Ln/Lm - gamma6/gamma1) < 0.05:
            print(f"    L{n}/L{m} = {Ln/Lm:.4f} (誤差 {abs(Ln/Lm-gamma6/gamma1)/gamma6/gamma1*100:.1f}%)")
            break

# ============ 3. m_ν/m_l 比 ============
print("\n[3] m_ν/m_l 比")
m_e_eV = m_e_MeV * 1e6
m_mu_MeV = M0 * gamma[7] * (Nd - 4)  # E_p=4? 用 docs 值
print(f"  m_ν_τ/m_e = {m_nu_tau/(m_e_eV):.3e}")
print(f"  m_ν_τ/m_μ = {m_nu_tau/(105.66e6):.3e}")
print(f"  m_ν_τ/m_τ = {m_nu_tau/(1776.86e6):.3e}")

# Dirac 比: m_ν/m_l = ?
# seesaw 典型: m_ν = m_l²/M_R → m_ν/m_l = m_l/M_R
# 但 IDCM 唔係 seesaw → 睇直接比
print(f"\n  直接比:")
for name, ml in [("e", 0.511e6), ("μ", 105.66e6), ("τ", 1776.86e6)]:
    mnu = {"e": m_nu_e, "μ": m_nu_mu, "τ": m_nu_tau}[name]
    r = mnu / ml
    print(f"  m_ν_{name}/m_{name} = {r:.3e}")

# ============ 4. 統一結構? ============
print("\n[4] 統一結構探索")
# 輕子用 γ_n 組合, 中微子用 γ₆ + φ-power
# γ_n 值:
for n in [1, 6, 7, 20]:
    print(f"  γ_{n} = {gamma[n]:.6f}")
print(f"  φ⁻¹ = {phi**-1:.6f}")
print(f"  φ⁻² = {phi**-2:.6f}")

# 中微子 φ-power 係咪 γ 比?
print(f"\n  ν 世代比 vs γ 比:")
print(f"  γ₆/γ₁ = {gamma6/gamma1:.4f} (ν_τ/ν_e 應該係 φ² = {phi**2:.4f})")
print(f"  γ₆/γ₂ = {gamma6/gamma[2]:.4f} (ν_τ/ν_μ 應該係 φ = {phi:.4f})")
print(f"  γ₆/γ₃ = {gamma6/gamma[3]:.4f}")
print(f"  γ₆/γ₄ = {gamma6/gamma[4]:.4f}")

# 有趣: ν 世代比 = φ 冪 — 呢個係「連續」比, 而 γ_n 係「離散」譜
# φ-power = γ 嘅包絡?
print(f"\n  γ_n 包絡 vs φ-power:")
for n in range(1, 10):
    print(f"  γ_{n} = {gamma[n]:.4f},  γ_{n}·φ² = {gamma[n]*phi**2:.4f}")

# ============ 5. 總結 ============
print("\n" + "=" * 72)
print("八期 60 總結:")
print("=" * 72)
print(f"""
  ν-p6 vs 帶電輕子:
  ─────────────────────────────────
  1. γ₆ = {gamma6:.6f} (p6 諧波)
  2. ν/l 比: 睇上面
  3. 世代: ν 用 φ-power, 輕子用 γ_n 組合
  4. γ₆/γ₁ = {gamma6/gamma1:.4f}

  開放: 中微子同輕子嘅統一機制未明
""")

results = {
    "test": "O57 八期 60: ν-p6 vs 輕子",
    "gamma6": float(gamma6),
    "gamma1": float(gamma1),
    "ratio_g6_g1": float(gamma6/gamma1),
    "m_nu_tau_eV": float(m_nu_tau),
    "passed": passed, "failed": failed
}
with open("data/60_nu_lepton.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 八期 60 完成!")
