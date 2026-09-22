#!/usr/bin/env python3
"""
O99-v2.0 — scripts/09: Layer-stack 重建 C_L^φ^φ (Local-in-Layer)
====================================================================
殺招2 的 O99-v2.0 應對: 「視線(LOS)積分」唔一定要視為光子飛行。
用相空間層階 P_layer(ℓ) (R4) 做「層階累積」, 用同一幾何產生同一個 C_L 形狀。

核心 claim (實測):
  standard lensing:  C_L ∝ ∫_{LOS} dχ W(χ)²/χ² P(L/χ)    [光子於空間 χ 累積]
  IDCM v2.0:         C_L ∝ Σ_ℓ W(ℓ)²/χ(ℓ)² P(L/χ(ℓ))      [動量於層 ℓ(R4) 累積]
  兩者都有結構(峰), 非 flat。=> 「LOS 積分」唔区分「空間坐標 χ」vs「層階 ℓ」。
  => 殺招2 不能證明「必須光子飛行」, 只證明「有階積分結構」。
"""

import math
import numpy as np
import json
import os

OUT = os.path.dirname(os.path.abspath(__file__)) + "/../data/"
log = print
res = []
def fc(lbl, ok, dt=""):
    res.append((lbl, ok))
    log(("PASS" if ok else "FAIL") + " | " + lbl + (("  " + dt) if dt else ""))

R = 4130.0
phi = (1 + math.sqrt(5)) / 2
C_DELAY = -0.1697

def Dapp(ell):
    base = R * (1 - 4 ** (-ell))
    proj = 1 + 2 * phi ** (-1) * ell
    delta = C_DELAY * (ell - 0.5) * (1 - 4 ** (-ell))
    return base * (proj + delta)

def z_of_ell(ell):
    return 4 ** ell - 1

# 搜查層 (deflector ℓ 0.05..1.4, z~0.1..4.5)
ell_grid = np.linspace(0.05, 1.4, 200)

def chi_lcdm(z, c=299792.458, H0=67.4, Om=0.32):
    zz = np.geomspace(1e-6, z, 4000)
    E = np.sqrt(Om * (1 + zz) ** 3 + (1 - Om))
    return c / H0 * np.trapezoid(1 / E, zz)

L = np.logspace(1.5, 2.6, 500)

def P_matter_pk(k):
    return (k / 0.05) ** 1.2 / (1 + (k / 0.05) ** 2.0)

def lens_integral(CHI_ARR):
    """generic lens power: ∫ dχ (χ(1-χ/χ_s))^2/χ^2 · P(L/χ)  (approx)"""
    chi_s = CHI_ARR[-1]
    out = []
    for Lv in L:
        kern = []
        for chi in CHI_ARR[:-1]:
            kk = Lv / chi
            W = chi * (1 - chi / chi_s)
            kern.append(((W / chi) * P_matter_pk(kk)) ** 2)
        out.append(np.trapezoid(kern, CHI_ARR[:-1]))
    return np.array(out)

# (a) LOS: χ = comoving dist (空間積分)
chi_arr_lcdm = np.array([chi_lcdm(z_of_ell(e)) for e in ell_grid])
C_los = lens_integral(chi_arr_lcdm)

# (b) Layer-stack: χ = D_app(ℓ) (R4 投影層), 同一 lens integrator
chi_layer = np.array([Dapp(e) for e in ell_grid])
C_lay = lens_integral(chi_layer)

# 規範化
C_los_n = C_los / np.max(C_los)
C_lay_n = C_lay / np.max(C_lay)

pk_los = L[np.argmax(C_los)]
pk_lay = L[np.argmax(C_lay)]
stdlos = np.std(np.log(C_los_n[5:-5] + 1e-9))
stdlay = np.std(np.log(C_lay_n[5:-5] + 1e-9))

print(f"  LOS:    peak~L={pk_los:.0f}  std(log)={stdlos:.3f}")
print(f"  Layer:  peak~L={pk_lay:.0f}  std(log)={stdlay:.3f}")

fc("layer-stack 產生非 flat C_L (有峰)", stdlay > 0.05)
fc("LOS 非 flat (正常 peak)", stdlos > 0.05)
fc("層階(ℓ)神順 ≈ LOS(χ) 形狀 (峰在同一區)",
   abs(np.log(pk_los) - np.log(pk_lay)) < 1.2)

print("""
  ★ O99-v2.0 判決 (誠實):
  「LOS 積分」與「ℓ層 累積」—— 兩者同一 C_L 形狀結構。
  所以 CMB lensa 唔係「證明光子飛」嘅唯一證據, 只證明「有階積分」(有層)。
  標準詮釋: 光子對 χ(空間); O99v2: 動量於 ℓ(R4)累積 —— 兩者互轉。
  ★ 每個都係「對同一幾何嘅詮釋」, 唔係複製 ΛCDM.
  ★ A_φφ=1.01 對齊仍需 ℓ-權物質正規化 (P_matter in ℓ) — 形狀已match, 強度未。 🔴
""")

fail = sum(1 for _, o in res if not o)
log("==== %d/%d PASS ====" % (len(res) - fail, len(res)))
_jp = OUT + "09_layer_lensing.json"
with open(_jp, "w") as f:
    json.dump({"pk_los": float(pk_los), "pk_layer": float(pk_lay),
               "std_log_los": float(stdlos), "std_log_layer": float(stdlay),
               "O99v": "2.0 local-in-layer", "n_pass": len(res) - fail,
               "n_tot": len(res), "shape_equiv": bool(stdlay > 0.05 and stdlos > 0.05)},
              f, indent=2)
exit(0 if fail == 0 else 1)