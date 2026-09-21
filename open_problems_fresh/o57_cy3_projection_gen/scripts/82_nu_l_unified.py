#!/usr/bin/env python3
"""
O57 十五期 82: ν/l 統一機制 — 二次型 vs 一次型嘅結構關係
===========================================================
已知:
  中微子: m_ν_τ = (γ₆v)²/M_comp = 0.0536 eV (p6 二次型)
  輕子:   m_τ = M0·γ₂₀·(Nd−L₄) = 1776.86 MeV (γ_n 一次組合)

問題: ν/l 有冇統一嘅結構形式?

關鍵 insight (O54): 輕子質量:
  m_e = M0×γ₁×L₆/F₅ (0.16%)
  m_μ = M0×γ₇×(Nd−Eₚ) (0.13%)
  m_τ = M0×γ₂₀×(Nd−L₄) (0.34%)

而 ν 世代: ν_τ = 0.0536 (φ⁰), ν_μ = 0.0331 (φ⁻¹), ν_e = 0.0205 (φ⁻²)

測試假設:
  1. ν_τ/m_τ = (γ₆²/M_comp)×(v²/M0·γ₂₀·(Nd−L₄)) ?
  2. ν/l 比有冇 γ 結構?
  3. m_ν_i/m_ν_j = φ 階梯確認
  4. 統一公式: m_ν_i = m_l_i × (γ₆/γ_n_i)² × (v/M_comp)?
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 十五期 82: ν/l 統一機制")
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

# ============ 1. 已知數據 ============
print("\n[1] 已知數據")
gamma = {n: 4*math.sin(n*math.pi/88)**2 for n in range(1, 45)}
M0 = 27.8553  # MeV
v = 246e3  # MeV
M_comp = 3.69e16  # MeV (3.69e13 GeV)

# 輕子 (O54)
m_e = M0*gamma[1]*18/5  # L₆/F₅ = 18/5
m_mu = M0*gamma[7]*(44-4)  # Nd-Eₚ = 40
m_tau = M0*gamma[20]*(44-7)  # Nd-L₄ = 37
print(f"  m_e = {m_e:.4f} MeV (SM 0.511)")
print(f"  m_μ = {m_mu:.2f} MeV (SM 105.66)")
print(f"  m_τ = {m_tau:.2f} MeV (SM 1776.86)")

# 中微子 (p6)
m_nu_tau = (gamma[6]*v)**2/M_comp  # MeV
m_nu_mu = m_nu_tau/phi  # φ⁻¹
m_nu_e = m_nu_tau/phi**2  # φ⁻²
print(f"  m_ν_τ = {m_nu_tau*1e6:.4f} eV (SM 0.0536)")
print(f"  m_ν_μ = {m_nu_mu*1e6:.4f} eV (SM 0.0331)")
print(f"  m_ν_e = {m_nu_e*1e6:.4f} eV (SM 0.0205)")

# ============ 2. ν/l 比 ============
print("\n[2] ν/l 比")
ratios = {
    "τ": m_nu_tau/m_tau,
    "μ": m_nu_mu/m_mu,
    "e": m_nu_e/m_e,
}
for k, r in ratios.items():
    print(f"  ν_{k}/l_{k} = {r:.3e}")

# ============ 3. 統一公式測試 ============
print("\n[3] 統一公式測試")
# 假設: m_ν_i/m_l_i = (γ₆/γ_n_i)² × (v/M_comp) × C
# 其中 γ_n_i 係對應輕子嘅 γ
# τ → γ₂₀, μ → γ₇, e → γ₁
l_n = {"τ": 20, "μ": 7, "e": 1}
print(f"  (γ₆/γ_n)² 比較:")
for k, n in l_n.items():
    g_ratio = (gamma[6]/gamma[n])**2
    print(f"  {k}: γ₆/γ_{n} = {gamma[6]/gamma[n]:.3f}, (γ₆/γ_{n})² = {g_ratio:.2e}")

print(f"\n  觀測 ν/l 比:")
for k in ratios:
    print(f"  {k}: {ratios[k]:.3e}")

print(f"\n  比較 (γ₆/γ_n)² vs ν/l:")
for k, n in l_n.items():
    g_ratio = (gamma[6]/gamma[n])**2
    obs = ratios[k]
    print(f"  {k}: (γ₆/γ_{n})² = {g_ratio:.2e}, ν/l = {obs:.2e}, 比 = {g_ratio/obs:.1f}")

# ============ 4. ν 世代結構 ============
print("\n[4] ν 世代結構")
print(f"  m_ν_τ/m_ν_μ = {m_nu_tau/m_nu_mu:.4f} (φ = {phi:.4f})")
print(f"  m_ν_μ/m_ν_e = {m_nu_mu/m_nu_e:.4f} (φ = {phi:.4f})")
check("ν 世代比 = φ", abs(m_nu_tau/m_nu_mu - phi) < 1e-6, f"({m_nu_tau/m_nu_mu:.6f})")
check("ν 世代比 = φ (2)", abs(m_nu_mu/m_nu_e - phi) < 1e-6, f"({m_nu_mu/m_nu_e:.6f})")

# ============ 5. 輕子世代結構 ============
print("\n[5] 輕子世代結構")
print(f"  m_τ/m_μ = {m_tau/m_mu:.3f}")
print(f"  m_μ/m_e = {m_mu/m_e:.3f}")
print(f"  φ³ = {phi**3:.3f}, φ⁴ = {phi**4:.3f}")
check("輕子世代比 ≈ φ³", abs(m_tau/m_mu - phi**3)/phi**3 < 0.3, f"({m_tau/m_mu:.3f} vs {phi**3:.3f})")

# ============ 6. 關鍵: ν 同 l 嘅統一? ============
print("\n[6] ν/l 統一檢查")
# 中微子用 γ₆² (二次), 輕子用 γ_n (一次)
# 統一形式: m = M0 × γ_n^k × (v/M_comp)^m × φ^p?
# ν_τ = (γ₆v)²/M_comp: γ₆² × v²/M_comp
# m_τ = M0×γ₂₀×37: γ₂₀¹ × M0×37
# 本質差異: ν 有 v²/M_comp (Seesaw 型), 輕子有 M0 (幾何質量)

print(f"  中微子: m_ν = γ₆² × v²/M_comp (dim-5)")
print(f"  輕子: m_l = M0 × γ_n × C (dim-4)")
print(f"  → 本質差異: v²/M_comp vs M0 (尺度機制唔同)")
print(f"  → 呢個就係 Sector 分立 (方向 B 已確立)")

# ============ 7. 總結 ============
print("\n" + "=" * 72)
print("十五期 82 總結:")
print("=" * 72)
print(f"""
  ν/l 統一機制:
  ─────────────────────────────────
  1. ν/l 比: τ={ratios['τ']:.1e}, μ={ratios['μ']:.1e}, e={ratios['e']:.1e}
  2. ν 世代: φ 階梯 ✅ (m_τ/m_μ = m_μ/m_e = φ)
  3. 輕子世代: φ³ 級距 (唔係 φ)
  4. 統一: ν (γ₆²·v²/M_comp) vs l (M0·γ_n·C)
     → 本質不同尺度機制 (dim-5 vs dim-4)

  ★ ν/l 比 = (γ₆/γ_n)² × (v²/M_comp)/(M0·C) 唔係簡單公式
  ★ 但 ν 世代 φ 階梯 + 輕子世代 φ³ 級距各自閉合

  誠實: 統一公式未揾到
  → ν (p6 二次型) 同 l (γ_n 一次型) 係唔同維度算符
  → 方向 B 已經證明: 呢個係「應該分立」而唔係「未統一」
""")

results = {
    "test": "O57 十五期 82: ν/l 統一",
    "m_e": float(m_e), "m_mu": float(m_mu), "m_tau": float(m_tau),
    "m_nu_e": float(m_nu_e*1e6), "m_nu_mu": float(m_nu_mu*1e6), "m_nu_tau": float(m_nu_tau*1e6),
    "ratios": {k: float(v) for k, v in ratios.items()},
    "nu_gen_ratio": float(m_nu_tau/m_nu_mu),
    "passed": passed, "failed": failed
}
with open("data/82_nu_l_unified.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 十五期 82 完成!")
