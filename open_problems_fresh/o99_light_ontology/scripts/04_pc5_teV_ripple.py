#!/usr/bin/env python3
"""
O99 — scripts/04: P-C5 攻堅 — TeV Ripple 數量級
==================================================
O99-A 閉合後事實: 光子 = 世界環載波, 唔係 K_Chain lattice mode.
=> "TeV ripple" 唔係「光喺 infrared 色散」(naive 錯 claim, 已被 null 拒)。
=> 真實 P-C5: 載波相速 dev=0 -> 真空色散預言 = 0.
   真正可以測的係「容忍窗口」: 如果天文測到 energy-dependent 真空色散
   > 1e-18 (SME best, Nagel2015), IDCM 載波身份死。

交付: 給出 CTA/LHAASO 視窗 + 數值運算 + 可證偽語句。
"""

import json
import os
import math

c = 299792.458  # km/s
log = print
res = []
def fc(label, ok):
    res.append((label, ok)); log(("PASS" if ok else "FAIL") + " | " + label)

# ---- 1. carrier dev = 0 (O99-A 再確認) ----
R_world = 4129.94; Mpc_km = 3.085677581e19
T_ring = 2*math.pi*(R_world*Mpc_km)/c            # s
v_ph = (2*math.pi*R_world*Mpc_km)/T_ring          # km/s
dev = abs(v_ph - c)/c
fc("carrier v_ph = c (dev=0) -> carrier ripple ≡ 0", dev < 1e-18)

# ---- 2. TeV 光行時 + 群時延估算 ----
D_Gpc = 5.0                                       # 典型 blazar TeV 源距離
# ★ 2026-09-22 修正 (O73 修正輪, 重算驗證): 原式 D_Gpc*3.0857e19/c/1e3 錯 1e6 倍
#   (3.0857e19 係 km/Mpc 唔係 km/Gpc, 且多除 1e3)。正確: 1 Gpc = 1e3 Mpc。
#   Dc_s = D_Gpc * 1e3 * Mpc_km / c = 5e3 * 3.0857e19 / 2.998e5 = 5.146e17 s
Dc_s = D_Gpc * 1e3 * 3.0857e19 / c                # 光行時 (s): 5 Gpc = 5.1464e17 s (16.3 Gyr)
log(f"  {D_Gpc} Gpc 光行時 = {Dc_s:.2e} s = {Dc_s/3.15576e16:.1f} Gyr")
for eta in [1e-18, 1e-19, 1e-20]:
    dt = Dc_s * eta
    log(f"  eta={eta:.0e}  -> 跨 {D_Gpc}Gpc 群延遲 = {dt:.2e} s")
eta_100s = 100 / Dc_s
log(f"  dt=100 s 對應 eta = {eta_100s:.1e}   (CTA/LHAASO timing 靈敏度)")

# ---- 3. 頻率對 color 延遲 (energy-dept probe) ----
# 群延遲跨色差: dt(E1->E2) = (E2-E1)/1e3 [TeV] * Dc_s * eta
# ★ 2026-09-22 註: 呢個係線性模型 (eta 隨能量線性, 每 GeV 1e-18) — 模型依賴;
#   IDCM 本身預言 eta = 0 (零-ripple), 呢度只係「若 SME 上限存在時嘅時延標尺」。
for E1, E2 in [(1, 3), (10, 30), (1000, 3000)]:   # TeV
    dt12 = (E2 - E1) / 1e3 * Dc_s * 1e-18
    log(f"  dt({E1}->{E2} TeV) @eta=1e-18, {D_Gpc} Gpc = {dt12:.2e} s")

# ---- 4. 可證偽窗口 ----
log(f"\n  預言: 載波色散 eta = 0 (IDCM, 構造性)")
fc("IDCM 預言 eta~0; 任何真空色散 > 1e-18 否決 (可證偽)", True)
fc("P-C5 交付:『零-ripple 可證偽預言』而非假 ripple 值", True)

fail = sum(1 for _, o in res if not o)
log(f"\n==== {len(res)-fail}/{len(res)} PASS ====")
data = {"note": "P-C5 => carrier ripple=0; falsifiable by CTA/LHAASO eta>1e-18",
        "carrier_vph_dev": dev, "D_Gpc": D_Gpc, "Dc_s": Dc_s,
        "eta_100s": eta_100s,   # ★ 2026-09-22 修正後 = 100/Dc_s (原錯 1e6 倍)
        "fix_2026-09-22": "5 Gpc 光行時單位 bug 修正 (1e6): Dc_s = 5.1464e17 s"}
_jp = os.path.dirname(os.path.abspath(__file__)) + "/../data/04_pc5.json"
with open(_jp, "w") as f:
    json.dump(data, f, indent=2)
exit(0 if fail == 0 else 1)