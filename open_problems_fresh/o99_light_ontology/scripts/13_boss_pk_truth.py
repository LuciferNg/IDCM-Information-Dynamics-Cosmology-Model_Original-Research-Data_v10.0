#!/usr/bin/env python3
"""
O99-v2.0 — scripts/13: σ_8 正確校準 — BOSS DR12 P(k) 積分 + O83 母函對照
=====================================================================
scripts/12 用單點 ξ(8) 開方係錯 (過度校正)。正確 σ_8:
   σ_8² = ∫₀^∞ dk/k · (k³ P(k)/2π²) · |W_R(k)|² ,  R = 8 h⁻¹ Mpc
         W_R(k) = 3(sin kR - kR cos kR)/(kR)³   (top-hat 窗)

用真 BOSS DR12 P(k) (wiggle 分解) 積 σ_8, 並同 IDCM O83 母函數對照.

關鍵: IDCM O83 嘅振幅母函數要能復現 P(k) 嘅形狀 (beat series) 先算閉合.
本 script:
  1) 真 BOSS P(k) → σ_8 (積分)   [obs]
  2) IDCM 母函數預測 → σ_8_ID    [conjecture]
  3) 誠實比較 + 判斷係「能用 BOSS 校準」定「仍 sub-grid gap」.
"""

import math, os, json
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__)) + "/../data/"
log = print
res = []
def fc(lbl, ok, dt=""):
    res.append((lbl, ok)); log(("PASS" if ok else "FAIL") + " | " + lbl + (("  " + dt) if dt else ""))

D = os.path.expanduser("~/IDCM/sync_bump_analysis")
wig_path = D + "/boss_dr12_bao_wiggles.txt"

k_arr, P_arr, Ps, wig = [], [], [], []
for line in open(wig_path):
    if line.startswith('#') or not line.strip():
        continue
    p = line.split()
    if len(p) < 4: continue
    k_arr.append(float(p[0])); P_arr.append(float(p[1]))
    Ps.append(float(p[2])); wig.append(float(p[3]))
k = np.array(k_arr); P = np.array(P_arr); Ps = np.array(Ps)
print(f"  BOSS P(k): {len(k)} 點, k∈[{k.min():.4f}, {k.max():.3f}] h/Mpc")

# ---- 1. 真 σ_8 via P(k) 積分 (linear P_in) ----
def top_hat(x):
    """top-hat window W_R(k) = 3(sin x - x cos x)/x³"""
    out = 3*(np.sin(x)-x*np.cos(x))/x**3
    return out

R8 = 8.0
x = k*R8
WH = top_hat(x)
# σ_8² = ∫ d ln k · (k³/(2π²)) P(k) W²
dlnk = np.diff(np.log(k))
mid = 0.5*(k[1:]+k[:-1]); P_mid = 0.5*(P[1:]+P[:-1]); WH_mid = 0.5*(WH[1:]+WH[:-1])
integrand = (mid**3/(2*np.pi**2)) * P_mid * WH_mid**2
sigma8_zeff = math.sqrt(abs(np.sum(integrand*dlnk)))
print(f"  未處理 σ_8(z_eff) = {sigma8_zeff:.3f}  (BOSS DR12 P(k) 積分)")

# ---- 3. IDCM O83 母函數 ----
# O83: A_{2k}/A = ((k+1)/(4k-1))² 在 beat 系統 但非 power spectrum amplitude.
# ID P(k) 之振幅未有: O83 給 峰位 beat (C_ℓ), 唔係 3D P(k). 
# => 咁先係問題核心: ID 冇 P(k) 功率譜 model (只有 相關 beat), σ_8 唔可能由 O83 直接推.
print("\n  ★ 核心誠實: O83 係「beat 頻譜」(C_ℓ 峰值), 唔係「3D matter P(k)」")
print("     ID 目前冇 P(k) model → σ_8 不能由 ID 母函 直接給 (sub-grid gap 真正來源)")

fc("BOSS P(k) 可用 (真 data)", len(k) > 50)
fc("ID (O83) 提供 3D P(k) model for σ_8?", False, "O83=beat谱 C_ℓ, 唔係 P(k)")
fc("σ_8 via P(k) 積分可行 (obs)", sigma8_zeff > 0.5)

print("""
  ★★ 誠實判決 (scripts/13):
  - 真 BOSS P(k) 在, 可用 top-hat 積 σ_8 (obs) -- 唔受 sub-grid 影響（P(k)已係連續函數）
  - 但 IDCM O83 mother 係「C_ℓ 峰位」(beat system), 唔係「3D P(k)」。
     → ID 根本無 3D matter power spectrum 模型 → σ_8 無法由 ID 直接推 (咁先係真 gap).
  - 路線E 能給 obs σ_8 (0.81 已知), 但唔係 ID 閉合: 只係「用資料校準 as 外澀函數」。
  - 真正閉合需: ID 由 母神→ P(k) 3D 轉換, 而家未建。標 🔴。
""")

fail = sum(1 for _, ok in res if not ok)
log("==== %d/%d ====" % (len(res)-fail, len(res)))
_jp = OUT + "13_boss_pk_mode.json"
json.dump({"k_n":int(len(k)),"sigma8_zeff": float(sigma8_zeff),
           "id_Pk_model":"NONE (O83=C_ℓ only)",
           "status":"RED_no_Pk_model", "n_pass":len(res)-fail,"n_tot":len(res)},
          open(_jp,"w"), indent=2)
exit(0 if fail==0 else 1)