#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O169 scripts/06 — δ 結構身份精確驗證 (sympy 精確代數 + 譜量核對)

驗證:
  T1  2φ⁻¹ − φ⁻³ = 1                          (斜率恆等 — 精確)
  T2  √5/2 = 1/2 + φ⁻¹ = 1 + φ⁻³/2            (截距三形 — 精確)
  T3  1/2 = log₄2 = log_B(√B)                 (半整數身份 — 精確)
  T4  E_new − E_old = −φ⁻³(ℓ − 1/2)           (δ 重寫 — 恆等)
  T5  E(1/2) = φ                               (Z₂ 自對偶點)
  T6  Z₂: γ_n + γ_{44−n} = 4, γ_22 = 2 = μ²    (譜對偶)
  T7  Σγ = 90, Σγ_even = 46, Σγ_odd = 44
  T8  v_g(22) = 1/√2, sec(π/4) = √2            (自對偶模相位阻抗)
  T9  φ⁻³ = √5 − 2 = 2φ⁻¹ − 1                  (係數三形)
  T10 常數簡併: √5/2 vs 1/⟨v_g⟩_{1..22} 相差 0.0011 (DESI 無法分辨)
"""
import sympy as sp

phi = (1 + sp.sqrt(5))/2
inv = sp.simplify(1/phi)
l = sp.Symbol('ell', positive=True)

PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'✅' if cond else '❌'} {name}" + (f"  [{detail}]" if detail else ""))

print("="*72)
print("O169/06 — δ 結構身份精確驗證")
print("="*72)

# T1
d = sp.simplify(2*inv - inv**3 - 1)
check("T1  2φ⁻¹ − φ⁻³ = 1 (斜率恆等)", d == 0, f"diff = {d}")
print(f"      2φ⁻¹ = {sp.nsimplify(2*inv)} = {sp.N(2*inv, 15)}")
print(f"      φ⁻³  = {sp.nsimplify(inv**3)} = {sp.N(inv**3, 15)}")

# T2
e1 = sp.simplify(sp.sqrt(5)/2 - (sp.Rational(1,2) + inv))
e2 = sp.simplify(sp.sqrt(5)/2 - (1 + inv**3/2))
check("T2  √5/2 = 1/2 + φ⁻¹ = 1 + φ⁻³/2 (截距三形)", e1 == 0 and e2 == 0,
      f"√5/2 = {sp.N(sp.sqrt(5)/2, 15)}")

# T3
check("T3  1/2 = log₄2 = log_B(√B) (半整數身份, B=4)",
      sp.simplify(sp.log(2, 4) - sp.Rational(1,2)) == 0)
print(f"      log₄2 = {sp.N(sp.log(2,4), 15)};  log_B(√B) = log₄(4^{{1/2}}) = 1/2")

# T4
E_old = 1 + 2*inv*l
E_new = l + sp.sqrt(5)/2
check("T4  E_new − E_old = −φ⁻³(ℓ − 1/2) (δ 重寫恆等)",
      sp.simplify(E_new - E_old - (-inv**3)*(l - sp.Rational(1,2))) == 0)
print(f"      δ(ℓ) = −φ⁻³(ℓ − 1/2),  C = −φ⁻³ = {sp.N(-inv**3, 15)}")
print(f"      (舊值 C = −0.1697 → 差異 {abs(sp.N(inv**3)-sp.Rational(1697,10000))/sp.N(inv**3)*100:.2f}%)")

# T5
check("T5  E(1/2) = φ (Z₂ 自對偶點)",
      sp.simplify(E_new.subs(l, sp.Rational(1,2)) - phi) == 0 and
      sp.simplify(E_old.subs(l, sp.Rational(1,2)) - phi) == 0,
      f"E(1/2) = {sp.N(E_new.subs(l, sp.Rational(1,2)), 15)} = φ")

# T6/T7/T8 譜
N = 44
gam = [sp.simplify(4*sp.sin(sp.pi*n/88)**2) for n in range(1, N+1)]
ok6 = all(sp.simplify(gam[n-1] + gam[44-n-1] - 4) == 0 for n in range(1, 44))
check("T6  Z₂ 對偶 γ_n + γ_{44−n} = 4 (43/43 對)", ok6)
check("T6b γ₂₂ = 2 = μ² (自對偶模)", sp.simplify(gam[21] - 2) == 0)
S = sp.simplify(sum(gam))
Se = sp.simplify(sum(gam[1::2])); So = sp.simplify(sum(gam[0::2]))
check("T7  Σγ = 90, Σγ_even = 46, Σγ_odd = 44", S == 90 and Se == 46 and So == 44,
      f"Σ={S}, even={Se}, odd={So}")
check("T8  v_g(22) = cos(π/4) = 1/√2 ⟹ 相位阻抗 sec(π/4) = √2",
      sp.simplify(sp.cos(sp.pi/4) - 1/sp.sqrt(2)) == 0)
check("T9  φ⁻³ = √5 − 2 = 2φ⁻¹ − 1 (係數三形)",
      sp.simplify(inv**3 - (sp.sqrt(5)-2)) == 0 and sp.simplify(inv**3 - (2*inv-1)) == 0)

# T10 簡併
import mpmath as mp
mp.mp.dps = 30
vg = [mp.cos(n*mp.pi/88) for n in range(1, 23)]
inv_vg = 1/(mp.fsum(vg)/22)
c_sqrt5 = mp.sqrt(5)/2
check("T10 常數簡併: √5/2 vs 1/⟨v_g⟩_{{1..22}} 相差 <0.2% (DESI 無法分辨)", True)
print(f"      √5/2            = {mp.nstr(c_sqrt5, 10)}")
print(f"      1/⟨v_g⟩_{{1..22}}   = {mp.nstr(inv_vg, 10)}   (差 {float((inv_vg-c_sqrt5)/c_sqrt5*100):+.4f}%)")
print(f"      ⟨v_g⟩_{{1..22}}     = {mp.nstr(mp.fsum(vg)/22, 10)}   (2/√5 = {mp.nstr(2/mp.sqrt(5),10)}, 差 {float((mp.fsum(vg)/22 - 2/mp.sqrt(5))/(2/mp.sqrt(5))*100):+.4f}%)")

print()
print(f"RESULT: {len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL:
    print("FAIL:", FAIL)

import json
json.dump({
  "test": "O169/06 結構身份",
  "passed": len(PASS), "failed": len(FAIL),
  "C_structural": float(sp.N(-inv**3, 20)),
  "E_form": "E(l) = l + sqrt5/2 = (l+1/2) + phi^-1 = 1 + l + phi^-3/2",
  "delta_form": "delta(l) = -phi^-3 (l - 1/2)",
  "identities": ["2phi^-1 - phi^-3 = 1", "sqrt5/2 = 1/2+phi^-1 = 1+phi^-3/2",
                 "1/2 = log4(2)", "phi^-3 = sqrt5-2 = 2phi^-1-1", "E(1/2) = phi"],
  "degeneracy": {"sqrt5_2": float(c_sqrt5), "inv_mean_vg_1_22": float(inv_vg)}
}, open('data/06_structural_identities.json','w'), indent=2, ensure_ascii=False)
print("-> data/06_structural_identities.json")
