#!/usr/bin/env python3
"""
O57 十五期 83: ν/l 反向結構 — 隱藏統一?
===========================================
scripts/82 發現: ν/l 比世代方向相反
  ν_e/m_e = 4.0e-8 (最大)
  ν_τ/m_τ = 3.0e-11 (最細)

即: ν 世代 (τ>μ>e 質量) 但 ν/l 比 (e>μ>τ)
→ ν_e 相對最重 (同輕子比), ν_τ 相對最輕

測試統一:
  1. ν_i/l_i × γ_n_i 有冇結構?
  2. ν_i/l_i × (γ₆/γ_n_i)² 有冇結構?
  3. 反向結構 = φ 冪?
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 十五期 83: ν/l 反向結構")
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

# SM 實測
sm = {"e": 0.511, "mu": 105.66, "tau": 1776.86}  # MeV
sm_nu = {"e": 0.0205e-6, "mu": 0.0331e-6, "tau": 0.0536e-6}  # MeV (eV→MeV)

# ============ 2. ν/l 比 ============
print("\n[2] ν/l 比")
ratios = {
    "τ": m_nu_tau/m_tau,
    "μ": m_nu_mu/m_mu,
    "e": m_nu_e/m_e,
}
for k, r in ratios.items():
    print(f"  ν_{k}/l_{k} = {r:.3e}")

# ============ 3. 反向結構 ============
print("\n[3] 反向結構 (×γ_n)")
# ν/l × γ_n (輕子嘅 γ)
gamma_l = {"τ": gamma[20], "μ": gamma[7], "e": gamma[1]}
for k in ratios:
    r = ratios[k] * gamma_l[k]
    print(f"  (ν/l)_{k} × γ_{k} = {r:.3e}")

# ν/l × γ₆²/γ_n²?
print("\n[4] (ν/l) × (γ₆/γ_n)²:")
for k in ratios:
    n = gamma_l[k]
    g = (gamma[6]/n)**2
    r = ratios[k] * g
    print(f"  {k}: (ν/l)×(γ₆/γ_{k})² = {r:.3e}")

# ============ 5. φ 冪檢查 ============
print("\n[5] φ 冪結構")
# ν/l 比 有冇 φ 冪?
for k in ratios:
    r = ratios[k]
    # log_φ(r)
    log_phi_r = math.log(r)/math.log(phi)
    print(f"  {k}: ν/l = {r:.2e}, log_φ = {log_phi_r:.3f}")

# 比嘅比 (世代方向)
r_e_tau = ratios["e"]/ratios["τ"]
r_mu_tau = ratios["μ"]/ratios["τ"]
print(f"\n  反向比:")
print(f"  (ν/l)_e/(ν/l)_τ = {r_e_tau:.0f}")
print(f"  (ν/l)_μ/(ν/l)_τ = {r_mu_tau:.0f}")
print(f"  φ⁵ = {phi**5:.1f}, φ⁸ = {phi**8:.1f}, φ¹¹ = {phi**11:.1f}")

# ============ 6. 統一候選 ============
print("\n[6] 統一候選")
# 假設: m_ν_i/m_l_i = (γ₆²/γ_n_i²) × (γ₆×v/M_comp)² / (M0×C)?
# 或者更簡單: ν/l = (γ₆/γ_n)² × (v/M_comp) × (v/M0)?
vM = v/M_comp
vM0 = v/M0
print(f"  v/M_comp = {vM:.2e}")
print(f"  v/M0 = {vM0:.2e}")
print(f"  (v/M_comp)² = {vM**2:.2e}")

# 測試: ν/l = (γ₆/γ_n)² × K?
for k in ratios:
    n = gamma_l[k]
    g = (gamma[6]/n)**2
    K = ratios[k]/g
    print(f"  {k}: K = (ν/l)/(γ₆/γ_n)² = {K:.3e}")

# K 有冇結構?
# τ: K = ?, μ: K = ?, e: K = ?
Ks = {k: ratios[k]/((gamma[6]/gamma_l[k])**2) for k in ratios}
print(f"\n  K 值: { {k: f'{v:.2e}' for k, v in Ks.items()} }")
print(f"  K_τ/K_μ = {Ks['τ']/Ks['μ']:.3f}")
print(f"  K_μ/K_e = {Ks['μ']/Ks['e']:.3f}")
print(f"  φ = {phi:.3f}")

# ============ 7. 總結 ============
print("\n" + "=" * 72)
print("十五期 83 總結:")
print("=" * 72)
print(f"""
  ν/l 反向結構:
  ─────────────────────────────────
  1. ν/l 比: e最大 (4e-8), τ最細 (3e-11) — 反向!
  2. (ν/l)×(γ₆/γ_n)² 冇消除反向
  3. K = (ν/l)/(γ₆/γ_n)²: { {k: f'{v:.1e}' for k, v in Ks.items()} }

  {'✅ K 有 φ 結構!' if abs(Ks['τ']/Ks['μ'] - phi) < 0.3 else '❌ K 冇簡單 φ 結構'}
  {'✅ 反向 = φ 冪!' if abs(r_e_tau - phi**8) < 1000 else '❌ 反向唔係簡單 φ 冪'}

  誠實: 反向結構存在但統一公式未閉合
  → ν 同 l 嘅關係需要更深入機制 (O61/O62)
""")

results = {
    "test": "O57 十五期 83: 反向結構",
    "ratios": {k: float(v) for k, v in ratios.items()},
    "Ks": {k: float(v) for k, v in Ks.items()},
    "r_e_tau": float(r_e_tau),
    "passed": passed, "failed": failed
}
with open("data/83_nu_l_inverse.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 十五期 83 完成!")
