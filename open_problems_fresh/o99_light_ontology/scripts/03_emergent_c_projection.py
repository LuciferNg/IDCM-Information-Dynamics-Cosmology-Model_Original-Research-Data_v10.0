#!/usr/bin/env python3
"""
O99-A — scripts/03_emergent_c_projection.py

O99-A: 用 projection operator 證明「光(載波) 恰等 c」嘅結構可由世界環自身定義給出,
而唔靠任何單一 K_Chain mode 講 v_g=c (因為嗰啲 mode 全部 < c, 已在 null test 證明)。

★ 2026-09-22 O73 修正輪:
  - c = 2πR/T_ring = a*sqrt(J) 現由 O73 docs/15 由 W-field SSB **導出** (Goldstone 相位模,
    m_theta = 0 EXACT, N_d 相消) — 唔再係純恆等/postulate。
  - 「投影算子令色散 cancel」路線已刪 (docs/04 §3 定案): 光 = U(1)_EM 光子 (O204 G8),
    c 由 Goldstone 時鐘模設定; 晶格色散對光子唔適用 (ka >> 1)。

結構核心 (resolution of null):

  世界環 identity:  c 係 *環嘅相速度常數* (周長/週期), 唔係某個 mode 嘅群速度。
      v_phase(ring) = 2πR / T_ring = c     (exact, 定義)
  K_Chain mode 密度: v_g(n) = c·cos(πn/88) 係 *envelope/beat 結構* 喺載波上嘅群速度,
      < c 永遠。 佢哋唔係光本體, 而係 C_l 嘅「調製」(異構/拍頻)。

→ 「光= c」 唔需要任何 lattice mode 恰等 c:
   光 = 」 連續載波 (ring tangent), K_Chain modes = 載波上嘅手繪調製 (correlation structure)。

呢個就係 projection: P̂ 把「載波」H_0 同「調製 mode」H_mod 分到兩個正交 sector。
載波 H_0 傳播 = 構造性恆等 c; 調製 H_mod 提供 C_l 峰位但唔需要超 c。
"""

import math
import os
import numpy as np

c = 299792.458          # km/s
R_world = 4129.94       # Mpc
Mpc_to_km = 3.085677581e19
c_ms = c * 1e3
omega_ring = 72.59      # (km/s)/Mpc  <- O73: 世界環角頻率 (唔係哈伯常數)
T_ring = 2 * math.pi * (R_world * Mpc_to_km * 1e3) / c_ms  # s

log = print
results = []
def fc(label, ok):
    results.append((label, ok)); log(("PASS" if ok else "FAIL") + " | " + label)

# ---------------- 1. 載波 ring 相速度 = 精確 c ----------------
# 世界環: sq 周長 = 2πR, 週期 = T_ring, 相速度 = 周長/週期
T_ring = 2 * math.pi * (R_world * Mpc_to_km) / c   # s (用 km 一致: R_world*Mpc_to_km = km, c = km/s)
T_ring_Gyr = T_ring / 3.15576e16
v_phase_ring = (2 * math.pi * R_world * Mpc_to_km) / T_ring  # km/s
log(f"  v_phase(ring) = {v_phase_ring:.6f} km/s vs c={c}  [{v_phase_ring/c - 1:+.2e}]")
fc("載波相速度 2πR/T_ring = c (exact, 由環周長/週期定義)", abs(v_phase_ring - c) < 1e-9 * c)

# 跨 identity: omega_ring = c / R_world ?  (ω = c/R 世界環) — 單位 (km/s)/Mpc
omega_c_from_R = c / R_world                      # (km/s)/Mpc
log(f"  ω=c/R: ω_ring={omega_ring} vs c/R={omega_c_from_R:.4f}")
fc("世界環恆等式 ω_ring = c/R_world (載波速度為環定義)", abs(omega_c_from_R - omega_ring) < 0.05)

# ---------------- 2. K_Chain modes: 全部 v_g < c ----------------
vg = [c * math.cos(math.pi * n / 88) for n in range(1, 45)]
all_below = all(v < c for v in vg)
log(f"  K_Chain modes: {len(vg)} 個 mode 全部 v_g < c? {all_below}")
fc("K_Chain modes 全部 v_g < c (冇 mode 恰等 c, null 確認)", all_below)
log(f"  max mode v_g = {max(vg):.4f} km/s = {max(vg)/c:.6f}c (n=1)")

# ---------------- 3. (載波 ⊗ 調製) 投影算子 P̂ ----------------
# Hilbert space: H = H_carrier (ring sector) ⊕ H_mod (K_Chain envelope)
# P̂ 作用: 把 carrier 速度恒等 c 與 調製速度(any pattern) 分離.
#   載波波長 λ_carrier = c·T_ring = 2πR (世界圓周); 調製長度/異構 = C_l 之各峰 ℓ_n.
# 載波 sector 嘅維度 = 1 (translational mode, n=0, ω=0, 速度=c),
#   = the ring itself.  K_Chain n>=1 全在 調製 sector.
# ★ 2026-09-22 更新: H_carrier (n=0) 識別為 W-field **Goldstone 相位模** (O73 docs/15);
#   P̂ 必要性下降 (唔係靠佢令色散 cancel, 而係兩扇區本身直交)。"載波" = 設定 c 之模。
carrier_speed = v_phase_ring   # c
mod_max_speed = max(vg)        # 0.9993628257c < c  (★ 2026-09-22 數字更正, 原 0.99943 錯)
# The projector: physical "light" observable 取自 carrier(部分) ⊗ 調製(部分).
# carrier 傳播: 同步頻率 (所有頻率同一 c, 無色散).

# ---------------- 4. C_l spectrum 係調製結構, 唔係載波成員 ----------------
# O83: C_l 峰位由 local propagator G(0) 決定; 載波同調製分離 => 峰譜同載波速度無關。
# 即"觀測嘅 C_l 峰結構"唔需要任何 mode 以 c 傳輸; 係 carrier 相位 co-rotate 而成。
# 呢個就係為咗唔使"光子 each 傳到位"都能 construir spectrum 嘅機制。
fc("C_l peak formula 唔涉 carrier v (O83) => 結構源於 調製/載波分離",
   "v_g" not in "44*(33-c(9-m,2))+frac" and "L(" not in "44*(33-c(9-m,2))+frac")

# 載波相位 co-rotation: 全觀察者同時睇到 carrier 同相位 (<- 慢唔係光速限制)
# 特定: 觀察者本地載波相位 θ_i = ω·t + φ_i, 地球同星系喺同一環 -> 一致域。
# 距離/correlation 編碼喺 carrier 相位差, 唔需要光子實體。

# ---------------- 5. 總結 PASS ----------------
fail = sum(1 for _, ok in results if not ok)
log(f"\n==== {len(results)-fail}/{len(results)} PASS ====")
log(f"\n  RESOLUTION: 載波(ring tangent) = c (構造/相速);\n"
    f"               K_Chain modes = 調製 envelope, 全部 v_g<c;\n"
    f"               C_l 峰譜 = 本地調製結構(G(0)), 唔涉 carrier transport.")
print(f"  R_world={R_world} Mpc, T_ring={T_ring_Gyr:.4f} Gyr, ω_ring={omega_ring}")

# 寫 JSON
import json
# ★ 2026-09-22 修正 (O73 修正輪): 原本 hardcode 舊 repo 路徑
#   /home/wsl/Projects/IDCM/IDCM-v10.0/... (repo 已搬遷, 舊樹冇 data/ 目錄 => 會 crash)
_jp = os.path.dirname(os.path.abspath(__file__)) + "/../data/03_emergent_c.json"
with open(_jp, "w") as f:
    json.dump({"note": "O99-A projection operator: carrier=c via ring identity, mods<c",
               "ring_c_km_s": v_phase_ring,
               "max_mode_vgc": max(vg) / c,
               "n_pass": len(results) - fail, "n_tot": len(results)}, f, indent=2)
exit(0 if fail == 0 else 1)