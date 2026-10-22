#!/usr/bin/env python3
"""
O187 Route C — 中微子扇區 out-of-sample 測試 (盲測, 預註冊判準)
================================================================
前設 (O209 docs/07, G3 閾值定理, 質量無關):
  n_ν = min{¬G2} = l_first(even) = 6   ← 由 A₅ 幾何鎖定, 唔係 fit
  中微子 = 1 鏈模式 (n=6) + 2 能隙束縛態;  質量值屬 O49/O57 機制

O187 語言 (γ·P_f):
  帶電費米子: m = M₀·γ_n·P_f,  M₀ = 27.900915 MeV
  P_f 結構池: {L₆/F₅, N_d−E_proj, N_d−L₄, N_d−L₅, F₇, N_d} = {3.6, 15.5, 37, 33, 13, 44}

預註冊判準:
  C1 (O187 線性語言延伸): m_ν = M₀·γ₆·P_f, P_f ∈ 池
      若 min(m_ν) 仍 >> 觀測 (~0.02-0.05 eV) ⟹ O187 線性公式喺中微子扇區 FAIL
      (唔係框架死亡, 係適用域判明: 公式只覆蓋 A₅ 保護帶電模式)
  C2 (deterministic selection 角度): n_ν=6 由 G3 鎖定(非 fit)
      ⟹ O187「n 後驗搜索」問題喺中微子扇區已解決 — 至少一個扇區有質量無關 n 選擇
  C3 (標度橋, 探索性): A = v²/M_comp (eV) vs M₀ (MeV) — 有冇結構比?
      A/M₀ 對照 φ^k、2^k、準確定結構常數。純探索, 唔聲稱。
"""
import math, json
from pathlib import Path

OUT = Path(__file__).parent.parent / "data"
RES = {}

M0 = 27.900915          # O136-labeled MeV
V = 246.22e9            # eV (O209 docs/07 §五)
M_COMP = 3.689e22       # eV = 3.689e13 GeV
A = V*V/M_COMP          # = 1.643380 eV
G6 = 4*math.sin(6*math.pi/88)**2   # γ₆
POOL = {"L6/F5":18/5, "Nd-Eproj":44-28.5, "Nd-L4":44-7, "Nd-L5":44-11, "F7":13.0, "Nd":44.0}
OBS_NU = {"m3_quasi": 0.05, "m1_approx": 0.0209, "m2_approx": 0.0227}  # eV 量級

print("="*100)
print("C1: O187 線性語言 m = M₀·γ_n·P_f 延伸去中微子 (n=6)")
print("="*100)
print(f"γ₆ = {G6:.6f}   M₀ = {M0} MeV")
min_m = None; min_pf = None
for lab, pf in POOL.items():
    m_mev = M0*G6*pf
    m_ev = m_mev*1e6
    if min_m is None or m_ev < min_m:
        min_m = m_ev; min_pf = lab
    print(f"  P_f={lab:>10} = {pf:>6.1f}  ⟹  m_ν = {m_ev:>12.3e} eV")
print(f"  ▶ 池內最小預言 = {min_m:.3e} eV (P_f={min_pf})")
print(f"  ▶ 觀測 (O49/O57) = {OBS_NU['m1_approx']:.4f} ~ {OBS_NU['m3_quasi']:.3f} eV")
ratio = min_m/OBS_NU["m3_quasi"]
print(f"  ▶ 比例 = {ratio:.3e}  (差距 {math.log10(ratio):.1f} 個數量級)")
c1_fail = min_m > 1.0   # ≥1 eV 就叫 FAIL (觀測 0.05 eV, 10+ 倍為 FAIL)
RES["C1"] = {"gamma6": G6, "min_m_ev": min_m, "min_pf": min_pf, "obs": OBS_NU,
             "ratio_min_over_obs": ratio, "L1_linear_lang_fails_neutrino": c1_fail}
print(f"C1 判定: O187 線性公式喺中微子扇區 {'FAIL (m_ν >> 0.05 eV)' if c1_fail else 'OK'}")
print("         ⟹ 適用域 = 帶電(A₅保護)模式; 中微子(A₅敏感)用 seesaw 二次方 — 出域")

print()
print("="*100)
print("C2: deterministic selection — n_ν 由質量無關規則鎖定?")
print("="*100)
# G3: n_ν = min{n: ¬G2(n)} = l_first(even) = 6 (A₅ 動差等向破缺閾值, 無質量輸入)
# 對照: O187 帶電 n ∈ {1,7,14,20,33,34} 係後驗 fit (264 組合搜索)
res2 = {}
print("  G3 定理 (O209 docs/07): n_ν = min{¬G2} = l_first(even) = 6  ✅ 零質量輸入")
print("  帶電扇區: n ∈ {1,7,14,20,33,34} — 後驗 fit (O187 原投訴對象)")
print("  ⟹ O187 'n 後驗' 問題喺 中微子扇區 已由結構解決; 帶電扇區仍未解")
RES["C2"] = {"n_nu_struct": 6, "source": "O209 G3 threshold thm", "mass_free": True,
             "charged_n": [1,7,14,20,33,34], "charged_n_posthoc": True}

print()
print("="*100)
print("C3: 標度橋 (探索性, 純觀察) — A(eV) vs M₀(MeV)")
print("="*100)
print(f"A = v²/M_comp = {A:.6f} eV")
print(f"M₀ = {M0} MeV = {M0*1e6:.6f} eV")
ratio_AM = A/(M0*1e6)
print(f"A/M₀ = {ratio_AM:.6e}")
# 結構常數對照
import numpy as np
cands = {}
for k in range(1, 60):
    c = 2**(-k)
    cands[f"2^-{k}"] = c
    c = (math.sqrt(5)-1)/2  # φ⁻¹
    cands[f"φ^-{k}"] = math.exp(-k*math.log((1+math.sqrt(5))/2))
    cands[f"φ^-{k}"] = ((1+math.sqrt(5))/2)**(-k)
    cands[f"γ₁^k"] = (4*math.sin(math.pi/88)**2)**k
best = sorted((abs(ratio_AM-v), k_) for k_, v in cands.items())  # k_ 係 label
top = best[:5]
for d, lab in top:
    print(f"  {lab:>8} = {cands[lab]:.6e}  (diff {d:.1e})")
RES["C3"] = {"A_eV": A, "A_over_M0": ratio_AM,
             "top_candidates": [(lab, cands[lab], d) for d, lab in top]}

(OUT/"04_neutrino_outofsample.json").write_text(
    json.dumps(RES, ensure_ascii=False, indent=2))
print(f"\n✅ 寫入 data/04_neutrino_outofsample.json")
