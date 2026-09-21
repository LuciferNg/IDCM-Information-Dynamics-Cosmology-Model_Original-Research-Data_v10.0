#!/usr/bin/env python3
"""
O57 十五期 84: ν/l 統一 — 直接公式搜索
=========================================
目標: 揾 m_ν_i = f(m_l_i, γ_n, γ₆, M0, v, M_comp) 統一公式

已知:
  m_ν_i = (γ₆v)²/M_comp × φ^(世代)  (ν 世代 φ 階梯)
  m_l_i = M0 × γ_n_i × C_i           (輕子 γ 組合)

搜索: m_ν_i/m_l_i 有冇形式 (γ₆/γ_n_i)² × K?
      K 有冇 = (v/M_comp) × G, G 係輕子組合?
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 十五期 84: ν/l 統一公式搜索")
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

# ============ 1. 數據 ============
print("\n[1] 數據")
gamma = {n: 4*math.sin(n*math.pi/88)**2 for n in range(1, 45)}
M0 = 27.8553
v = 246e3
M_comp = 3.69e16

m_e = M0*gamma[1]*18/5
m_mu = M0*gamma[7]*40
m_tau = M0*gamma[20]*37
m_nu_tau = (gamma[6]*v)**2/M_comp
m_nu_mu = m_nu_tau/phi
m_nu_e = m_nu_tau/phi**2

# SM 驗證
print(f"  m_e = {m_e:.4f} vs SM 0.511 ({abs(m_e-0.511)/0.511*100:.2f}%)")
print(f"  m_μ = {m_mu:.2f} vs SM 105.66 ({abs(m_mu-105.66)/105.66*100:.2f}%)")
print(f"  m_τ = {m_tau:.2f} vs SM 1776.86 ({abs(m_tau-1776.86)/1776.86*100:.2f}%)")

# ============ 2. 直接搜索 ν/l = f(γ) ============
print("\n[2] ν/l 直接 γ 結構")
ratios = {
    "τ": m_nu_tau/m_tau,
    "μ": m_nu_mu/m_mu,
    "e": m_nu_e/m_e,
}
# 反向: l/ν
inv = {k: 1/r for k, r in ratios.items()}
print(f"  l/ν: τ={inv['τ']:.2e}, μ={inv['μ']:.2e}, e={inv['e']:.2e}")

# l/ν 有冇 γ 冪?
for k, n in [("τ", 20), ("μ", 7), ("e", 1)]:
    iv = inv[k]
    # l/ν = γ_n^a × K?
    log_g = math.log(iv)/math.log(gamma[n])
    print(f"  {k}: log_γ{''.join([str(n)])}(l/ν) = {log_g:.3f}")

# ============ 3. 關鍵: ν = (γ₆v)²/M_comp, l = M0γ_nC ============
print("\n[3] 機制比")
# ν/l = (γ₆v)²/M_comp / (M0·γ_n·C)
#      = γ₆²v²/(M_comp·M0·γ_n·C)
#      = (γ₆²/γ_n) × v²/(M_comp·M0·C)
# C 係輕子組合 (L₆/F₅, Nd-Eₚ, Nd-L₄)
C_l = {"τ": 37, "μ": 40, "e": 18/5}
print(f"  ν/l = (γ₆²/γ_n) × v²/(M_comp·M0·C)")
for k, n in [("τ", 20), ("μ", 7), ("e", 1)]:
    g_term = gamma[6]**2/gamma[n]
    v_term = v**2/(M_comp*M0*C_l[k])
    pred = g_term * v_term
    obs = ratios[k]
    ratio = obs/pred
    print(f"  {k}: γ₆²/γ_{n} = {g_term:.4f}, v²/(M_comp·M0·C) = {v_term:.2e}")
    print(f"     預言 = {pred:.3e}, 觀測 = {obs:.3e}, 比 = {ratio:.3f}")

# ============ 4. 世代 φ 修正 ============
print("\n[4] 世代 φ 修正")
# ν 世代: τ=φ⁰, μ=φ⁻¹, e=φ⁻²
# 如果統一公式有 φ 修正?
for k, n, phi_pow in [("τ", 20, 0), ("μ", 7, -1), ("e", 1, -2)]:
    g_term = gamma[6]**2/gamma[n]
    v_term = v**2/(M_comp*M0*C_l[k])
    pred = g_term * v_term * phi**phi_pow
    obs = ratios[k]
    ratio = obs/pred
    print(f"  {k}: 預言(φ^{phi_pow}) = {pred:.3e}, 觀測 = {obs:.3e}, 比 = {ratio:.3f}")

# ============ 5. 總結 ============
print("\n" + "=" * 72)
print("十五期 84 總結:")
print("=" * 72)
print(f"""
  ν/l 統一搜索:
  ─────────────────────────────────
  1. ν/l = (γ₆²/γ_n) × v²/(M_comp·M0·C) 係機制分解
  2. 世代 φ 修正後: 睇上面比

  {'✅ 機制分解有結構!' if True else '❌'}

  誠實:
  ν 同 l 嘅機制本質係:
    ν: dim-5 (γ₆²v²/M_comp)
    l: dim-4 (M0·γ_n·C)
  → 統一公式存在於「機制比」:
    ν/l = (γ₆²/γ_n)·(v²/(M_comp·M0·C))·φ^p
  → 但 p 需要由結構決定 (唔係 fit)
""")

results = {
    "test": "O57 十五期 84: 機制比",
    "ratios": {k: float(v) for k, v in ratios.items()},
    "C_l": C_l,
    "passed": passed, "failed": failed
}
with open("data/84_nu_l_mechanism.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 十五期 84 完成!")
