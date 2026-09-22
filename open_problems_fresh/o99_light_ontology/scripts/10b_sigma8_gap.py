#!/usr/bin/env python3
"""
O99-v2.0 — scripts/10b: A_φφ 振幅閉合 — 用 IDCM 真實 σ_8 differ解剖
================================================================
scripts/10 用 手 Ω_d=0.30 -> A~0.95. 但那唔夠: lensing power 除咗 Ω_m,
仲有 matter clustering σ_8². 用 IDCM 真 σ_8 (O91) 先係誠實.

真實 (O91/01): IDCM σ_8 = 0.0859; Ω_M=0.3045. Planck σ_8 ~ 0.80.
A_φφ ∝ Ω_m · σ_8²  => 用真 σ_8 -> A_φφ ~ (0.8/0.086)² 冇乜, 差極大.
"""

import json, os, math

log = print
res = []
def fc(lbl, ok, dt=""):
    res.append((lbl, ok)); log(("PASS" if ok else "FAIL") + " | " + lbl + (("  " + dt) if dt else ""))

A_obs = 1.01
sig_idcm = 0.0859
sig_obs = 0.80
Om_idcm = 0.3045
Om_obs = 0.314

A_fit = Om_idcm / Om_obs * (sig_idcm / sig_obs) ** 2
print(f"  IDCM σ_8  = {sig_idcm:.4f}")
print(f"  Planck σ_8= {sig_obs:.4f}")
print(f"  Ω_m(IDCM) = {Om_idcm:.4f}")
print(f"  A_φφ(σ)=Om/OmP × (σ/σP)² = {A_fit:.4f}")
print(f"  vs obs A_φφ={A_obs}  差 = {A_obs/A_fit:.0f}x 太細")

fc("IDCM σ_8=0.086 vs 0.8 -> 用佢 A_φφ 只有 obs 之 ~1%", A_fit > 0.9)
fc("A_φφ 嘅 σ_8 成分未閉合 (需 IDCM 推 σ_8→0.8, 係 O91 gap)", False)

print("""
  ★★ 誠實結論:
  A_φφ=1.01 嘅 ingredients:
    1. Ω_m: OK (0.95, 已閉合)
    2. σ_8: IDCM 0.086 vs obs 0.8 -> 差 9.3x -> A_φφ 差 ~0.01 (不可閉)
  → A_φφ 振幅嘅 sigma_8 成分唔可以閉到 1.01, 除非解決 O91 嘅 σ gap (~9×)。
    呢個係「已知張力」嘅餘波, 唔係新 bug, 但要誠實標記: v2.0 之 A 閉合只到 Ω_m 層。
""")

fail = sum(1 for _, ok in res if not ok)
log("==== %d/%d PASS ====" % (len(res) - fail, len(res)))
_jp = os.path.dirname(os.path.abspath(__file__)) + "/../data/10b_sigma8.json"
json.dump({"sigma8_idcm": sig_idcm, "sigma8_obs": sig_obs,
           "A_phiphi_omega_part": round(Om_idcm / Om_obs, 4),
           "A_phiphi_with_sigma8": round(A_fit, 5),
           "status": "RED_sigma8_gap_9x", "n_pass": len(res) - fail,
           "n_tot": len(res)}, open(_jp, "w"), indent=2)
exit(0 if fail == 0 else 1)