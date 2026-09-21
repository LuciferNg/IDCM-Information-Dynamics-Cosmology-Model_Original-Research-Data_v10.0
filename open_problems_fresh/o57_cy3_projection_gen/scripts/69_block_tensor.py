#!/usr/bin/env python3
"""
O57 十一期 69: 推 3+4 — 3-Block Flavour 矩陣 + Seesaw-Dirac Tensor
====================================================================
Gemini 方向 3: 3-Block Flavour Matrix
  F_ab = G_generation ⊗ T_type
  G: (1, φ², φ⁴) 世代壓抑
  T: u-type ~ g_s, d-type ~ g_s/√5, lepton ~ g_s/φ²

Gemini 方向 4: Seesaw-Dirac Tensor 統一
  m_f = v·γ_n^p × (v/Λ_comp)^(p-1)/45
  p=1 (輕子): 退化到 m_l ~ v·γ_n
  p=6 (中微子): 高階項 (v/Λ_comp)^5 ≈ 1/45 消去 45 倍

測試:
  1. 3-Block 結構重 fit 9 費米子
  2. Seesaw-Dirac 統一公式
  3. χ² 對比 (vs 單一階梯 2.2e6)
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 十一期 69: 3-Block + Seesaw-Dirac")
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

# ============ 1. SM 質量 ============
print("\n[1] SM 9 費米子質量 (MeV)")
m_SM = {
    "u": 2.2, "c": 1270, "t": 172760,
    "d": 4.7, "s": 93, "b": 4180,
    "e": 0.511, "mu": 105.66, "tau": 1776.86,
}
for k, v in m_SM.items():
    print(f"  {k:3s}: {v:10.2f} MeV")

# ============ 2. 3-Block 結構 ============
print("\n[2] 3-Block Flavour 矩陣")
# G: 世代階梯 (1, φ², φ⁴) — 但 SM 係 (1, φ⁴, φ⁸)? 試
# T: type 因子
# 模型: m = M_type × G_gen × (Lucas 修正)
# 每 type 有自己嘅 M_type, 每 gen 有 G_gen

# 3 個 type 嘅幾何基線 (用已知 IDCM 結構)
# u-type: γ₂₀ (top 用 γ₂₀?)
# d-type: γ₇
# lepton: γ₁
gamma = {n: 4*math.sin(n*math.pi/88)**2 for n in range(1, 45)}

# 三代因子: 用 curve volumes (五期 Lucas 結構)
# V1=1.0, V2=9.47, V3=22.18... 但呢啲係 curve 唔係 fermion
# 改用 Lucas: L_nφ+L_{n-1}
L = [2, 1]
for i in range(2, 20):
    L.append(L[i-1] + L[i-2])
V_lucas = [L[n]*phi + L[n-1] for n in range(1, 10)]

# 模型: m_type,gen = M0 × γ_type × e^{-V_gen} ?
# 或者: m = M0 × γ_type × φ^{-2(gen-1)}
print(f"  φ 世代階梯: 1, φ⁻², φ⁻⁴ = 1, {phi**-2:.3f}, {phi**-4:.3f}")

# 試: m = M0 × γ_n × φ^{-2(gen-1)}
# M0 用最佳 fit
for type_name, n in [("u", 20), ("d", 7), ("l", 1)]:
    masses = [m_SM[k] for k in {"u": ["u","c","t"], "d": ["d","s","b"], "l": ["e","mu","tau"]}[type_name]]
    # fit M0: m = M0 × γ_n × φ^{-2(gen-1)}
    # ln m = ln(M0 γ_n) - 2(gen-1) ln φ
    # M0 = m_t / (γ_n × 1) (top 用 gen3 = φ⁰)
    M0 = masses[2] / gamma[n]  # top/bottom/tau 用 φ⁰
    pred = [M0 * gamma[n] * phi**(-2*g) for g in range(3)]
    log_err = np.mean([abs(math.log(pred[i]/masses[i])) for i in range(3)])
    print(f"  {type_name}-type (γ_{n}): M0={M0:.1f}, pred={[f'{p:.1f}' for p in pred]}, "
          f"log-err={log_err:.3f}")

# ============ 3. Seesaw-Dirac Tensor ============
print("\n[3] Seesaw-Dirac Tensor 統一")
# m_f = v·γ_n^p × (v/Λ_comp)^(p-1)
# p=1: m = v·γ_n (Dirac)
# p=6: m = v·γ₆^6 × (v/Λ_comp)^5
v = 246e3  # MeV (246 GeV)
M_comp = 3.69e13  # GeV = 3.69e16 MeV
L_comp = M_comp / v  # = 1.5e11

# 輕子 (p=1): m_e = v·γ₁ × (Lucas 修正?)
m_e_pred = v * gamma[1]
print(f"  p=1 輕子: m_e = v·γ₁ = {m_e_pred:.1f} MeV (SM 0.511) — 差 {m_e_pred/0.511:.0f} 倍")
# 要 M0 修正: m_e = M0·γ₁·L₆/F₅ (O54)
M0 = 27.8553
m_e_o54 = M0 * gamma[1] * 18/5
print(f"  O54: m_e = M0·γ₁·L₆/F₅ = {m_e_o54:.3f} MeV (0.16%)")

# 中微子 (p=6): m_ν = v·γ₆⁶ × (v/Λ_comp)^5?
m_nu_pred = v * gamma[6]**6 * (v/M_comp)**5
print(f"  p=6 中微子: v·γ₆⁶·(v/Λ_comp)^5 = {m_nu_pred:.3e} MeV = {m_nu_pred*1000:.3e} eV")
print(f"  (真實 m_ν_τ = 0.0536 eV)")

# 比較: (v/Λ_comp)^5 = ?
ratio = (v/M_comp)**5
print(f"  (v/Λ_comp)^5 = {ratio:.3e} ≈ 1/45? {1/45:.3e}")
print(f"  1/45 = {1/45:.5f}")

# Gemini: (v/Λ_comp) ≈ 1/45?
print(f"  v/Λ_comp = {v/M_comp:.3e}")
print(f"  (v/Λ_comp) vs 1/45: {(v/M_comp)/(1/45):.2f}")
print(f"  (v/Λ_comp)² vs 1/45: {(v/M_comp)**2/(1/45):.2f}")

# ============ 4. 統一公式 ============
print("\n[4] 統一公式")
# m_f = M0 × γ_n^p × φ^{-2(gen-1)} × (v/Λ)^(p-1)
# p=1: m_l = M0·γ_n·φ^{-2(g-1)}
# p=6: m_ν = M0·γ₆^6·(v/Λ)^5·φ^{-2(g-1)}

# 輕子 p=1 fit (用 M0)
for type_name, n, keys in [("u", 20, ["u","c","t"]), ("d", 7, ["d","s","b"]), ("l", 1, ["e","mu","tau"])]:
    masses = [m_SM[k] for k in keys]
    M0_fit = masses[2] / (gamma[n] * 1)  # gen3 = φ⁰
    pred = [M0_fit * gamma[n] * phi**(-2*g) for g in range(3)]
    log_err = np.mean([abs(math.log(pred[i]/masses[i])) for i in range(3)])
    print(f"  {type_name} (γ_{n}): M0={M0_fit:.2f} MeV, log-err={log_err:.3f}")

# 中微子 p=6
# m_ν_τ = M0 × γ₆^6 × (v/Λ)^5 × φ⁰
m_nu_model = M0 * gamma[6]**6 * (v/M_comp)**5
print(f"  ν_τ = M0·γ₆⁶·(v/Λ)^5 = {m_nu_model:.3e} MeV = {m_nu_model*1e6:.3e} eV")
print(f"  (真實 {0.0536:.4f} eV)")

# ============ 5. 總結 ============
print("\n" + "=" * 72)
print("十一期 69 總結:")
print("=" * 72)
print(f"""
  3-Block + Seesaw-Dirac:
  ─────────────────────────────────
  1. 3-Block: 每 type 有 M0, 世代 φ⁻² 階梯
  2. u/d/l 用 γ₂₀/γ₇/γ₁
  3. Seesaw-Dirac: (v/Λ_comp)^5 ≈ {ratio:.1e} (唔係 1/45)
  4. ν p=6 模型: {m_nu_model*1e6:.1e} eV vs 0.0536

  誠實: (v/Λ_comp) ≈ {v/M_comp:.1e} 唔等於 1/45
  → Gemini 嘅 1/45 猜測需要重新評估
""")

results = {
    "test": "O57 十一期 69: 3-Block + Seesaw-Dirac",
    "v_over_Lambda": float(v/M_comp),
    "m_nu_model_eV": float(m_nu_model*1e6),
    "m_nu_real": 0.0536,
    "passed": passed, "failed": failed
}
with open("data/69_block_tensor.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 十一期 69 完成!")
