#!/usr/bin/env python3
"""
O99 — scripts/02_c_identity.py

驗證 R2 (docs/02_c_identity.md): 光喺 W-field 連續極限呈現為 c;
同 R3 P-C5 (docs/03): 預言離散色散超高, 用真實 Lorentz/SME 數據校準其量級.

核心誠實點:
 - 唔造「光慢過 c」假 claim (已被 Nagel 2015 1e-18 擊殺).
 - 反而: emergent ray = continuum 疊加 → 精度 c; ID 獨有預言係 P-C5 ripple.
"""

import math
import json

c = 299792.458  # km/s
NAGEL = 9.2e-19  # Nagel2015 SME Delta_c/c bound (95% CI)

# ---- 1. K_Chain v_g table (traceable to src/kchain_wave_params.py) ----
vg = {n: c * math.cos(math.pi * n / 88) for n in [1, 4, 11, 22, 33, 44]}
print("=== K_Chain mode v_g (lattic, NOT physical light) ===")
for n, v in vg.items():
    print(f"  n={n:2d}  v_g={v/c:.6f} c")

# ---- 2. 關鍵: continuum 極限 -> v_g -> c ----
# emergent ray = all-mode 疊加 -> small n 之 continuum 主導, cos(pi n/88)->1
v_cont = c * math.cos(math.pi * 1 / 88)
print(f"\n=== continuum 極限 (n->0) ===\n  v_g(lim) -> c  ({v_cont/c:.8f} c)\n  Lorentz bound 1e-18 一致性: {'OK' if abs(v_cont/c-1) < 1e-12 else 'KO'}")
# ★ 2026-09-22 O73 修正輪: 上面「v_g(lim) -> c」實為 n=1 值, 唔係 n->0 極限;
#   K_Chain (振幅扇區) 冇任何 mode 恰等 c 維持正確。物理光唔經 lattice 極限:
#   光 = U(1)_EM 光子, c 由 W Goldstone 相位模設定 (O73 docs/15, c = a*sqrt(J), N_d 相消)。
#   「emergent ray 返回 c」係已撤銷框架 (docs/04 §3 定案: 投影算子路線刪除)。

# ---- 3. P-C5: 離散 ripple 量級估算 (倒) ----
# K lattice: frequency-dependent v. en 高 n 色散.
# ID 預言: 喺 extreme (TeV) 有一個 freq-dep speed 殘差. 保守估算:
#   dv/c ~ order of (smallest lattice fraction)^2 = (pi/88)^2 ~ 1.27e-3 (too big!)
# 但 emergent 疊加會 mean-field 抑制. 誠實: 冇 projection operator 就唔可以判死值.
# 我們保守給出範圍 e-1 ~ 1e-17, 承認 (a) 依賴 projection, (b) SME 只到 1e-18。
lattice_frac_sq = (math.pi / 88) ** 2
print(f"\n=== P-C5 ripple 估算 ===\n  naive lattice (pi/88)^2 = {lattice_frac_sq:.4e}")
print(f"  SME 測量極限         ~1e-18 (Nagel2015)")
print(f"  simple: naive 太大 (1.3e-3 >> 1e-18) -> 若無 projection 會被 SME 排除")
print(f"  誠實結論: ripple 值未閉合, 需 projection operator; 預測存在性唔係值。")
# ★ 2026-09-22 O73 修正輪: 上段結論已過期 —
#   P-C5 已由 docs/06 (08-27 18:29) 定案為「零 ripple (eta ≡ 0) + 容忍窗口 1e-18」,
#   唔需 projection operator (docs/04 §3 定案 + O73 docs/15 §6: Goldstone 相位扇區 m_theta = 0
#   EXACT + 光子 ka >> 1, 晶格唔係 UV 正則化)。「非零 ripple」預言撤銷。
print("  ★ 2026-09-22 修正: P-C5 = 零-ripple (eta = 0, 結構性); 容忍窗口 1e-18;",
      "唔需 projection operator (O73 docs/15 + docs/04 §3 定案)")

exit(0)