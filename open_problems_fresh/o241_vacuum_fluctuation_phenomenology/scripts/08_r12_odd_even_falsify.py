#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O241 R12 — F-Q4.2 奇偶峰比樣本外盲測實跑 (ACT DR6, 未用於建構)
================================================================================
判準 F-Q4.2 (docs/04): 奇偶峰比譜 —— 零參數預言 vs ACT 樣本外數據.
預言:
  (a) 偶峰: A_{2k}/A₁ = ((k+1)/(4k−1))²   (O9, k=1..3 已驗證 0.24/1.04/1.48%)
      k=4: (5/15)² = 1/9 = 0.11111  (m=8)
      k=5: (6/19)² = 36/361 = 0.09972 (m=10)
      k=6: (7/23)² = 49/529 = 0.09263 (m=12)
  (b) 奇峰: A_{2k+1} 級聯? O213 docs/07 盲測表: m=9: 3/28=0.10714; m=11: 3/35;
      m=13: 1/14 —— 但峰位公式只涵蓋 m<=7 (O83), 高 ℓ 阻尼區峰位未定義,
      樣本外執行以「ACT 可辨識峰」為準.
  (c) O9 已記錄: A₅/A₄ = 7/6 = 1.1667 vs ACT DR4 0.949 (3.0σ FAIL);
      A₇/A₆ = 121/112 = 1.0804 vs ACT DR4 0.852 (3.5σ FAIL) —— R12 用 ACT DR6 重驗.

方法:
  用 ACT DR6 sacc (45 TT bins), 直接取 bin 值做峰比:
    m=5 bin (ell~1098.5) vs m=4 bin (ell~1048.5) -> A₅/A₄
    m=7 bin (ell~1348.5) vs m=6 bin (ell~1198.5) -> A₇/A₆
    m=1 bin? ACT 由 598 起 -> A₁ 用 m=2 峰 (ell~537? 超出 ACT) -> 偶峰比用
    Planck TT (planck_tt.txt) 同數據源度 A_{2k}/A₁ 樣本外 k=4..
  注意: ACT bin 係帶寬 ~50, 峰位未必正中 bin; 用最近 bin + 註明 uncertainty.
"""

import json, os, math
import numpy as np
from astropy.io import fits

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
O9 = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o9_high_ell_peaks"
results = []
def check(name, cond, detail=""):
    results.append({"check": name, "pass": bool(cond), "detail": detail})
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}  {detail}")

# ---- ACT DR6
hdul = fits.open(os.path.join(O9, "data", "act_dr6_cmb_sacc.fits"))
d = hdul["data:cl_00"].data
ell_act = np.array([r[4] for r in d])
val_act = np.array([r[2] for r in d])
hdul.close()
print("="*72)
print("R12: F-Q4.2 奇偶峰比樣本外實跑 (ACT DR6)")
print("="*72)

def act_at(ell_target):
    i = int(np.argmin(np.abs(ell_act - ell_target)))
    return ell_act[i], val_act[i]

# ---- (c) 奇峰比重驗 (O9 FAIL 記錄 vs ACT DR6)
# m=5: ℓ=1121 (Planck); ACT bin 1098.5 (m=5 附近)
# m=4: 1013; ACT bin 998.5/1048.5
e4, v4 = act_at(1013.0)
e5, v5 = act_at(1121.0)
e6, v6 = act_at(1337.0)
e7, v7 = act_at(1400.0)
print(f"\n  ACT DR6 bins: m4→ell{e4:.0f}={v4:.1f}, m5→ell{e5:.0f}={v5:.1f}, m6→ell{e6:.0f}={v6:.1f}, m7→ell{e7:.0f}={v7:.1f}")
r54_act = v5/v4
r76_act = v7/v6
print(f"  A₅/A₄ (ACT DR6) = {r54_act:.4f}  vs 預言 7/6 = {7/6:.4f}  dev={(abs(r54_act-7/6)/(7/6)):.1%}")
print(f"  A₇/A₆ (ACT DR6) = {r76_act:.4f}  vs 預言 121/112 = {121/112:.4f}  dev={(abs(r76_act-121/112)/(121/112)):.1%}")
check("F-Q4.2a: A₅/A₄ = 7/6 樣本外 (ACT DR6, dev<10% 為過)",
      abs(r54_act-7/6)/(7/6) < 0.10, f"實測 {r54_act:.4f} vs 預言 {(7/6):.4f}: dev={abs(r54_act-7/6)/(7/6):.1%}")
check("F-Q4.2b: A₇/A₆ = 121/112 樣本外 (ACT DR6, dev<10% 為過)",
      abs(r76_act-121/112)/(121/112) < 0.10, f"實測 {r76_act:.4f} vs 預言 {(121/112):.4f}: dev={abs(r76_act-121/112)/(121/112):.1%}")

# ---- (a) 偶峰比: Planck 同一數據源 (A₁ = 第一峰 221)
planck = np.loadtxt(os.path.join(O9, "data", "planck_tt.txt"))
ell_p = planck[:, 0]; c_p = planck[:, 1]
D_p = c_p * ell_p*(ell_p+1)/(2*math.pi)

def pl_at(t):
    i = int(np.argmin(np.abs(ell_p - t)))
    return ell_p[i], D_p[i]

# A₁ (m=2, 偶峰公式 k=1) 用 ℓ=221 峰
e1, v1 = pl_at(221.0)
print(f"\n  偶峰比 (Planck, 同源): A₁(ℓ~{e1:.0f}) = {v1:.1f}")
pred_even = {4: (5/15)**2, 5: (6/19)**2, 6: (7/23)**2}
for k in [4, 5, 6]:
    m = 2*k
    # 峰位: m=8 → ?  用 O83 公式延伸到 m=8..14 (C(9-m,2): m>9 為 0)
    # 直接睇 Planck 高 ℓ 區局部峰
    pass

# 高 ℓ 峰: 由 Planck 數據搵 m=8..14 峰 (阻尼區低峰, 用局部極大)
peaks = []
for i in range(1, len(D_p)-1):
    if D_p[i] > D_p[i-1] and D_p[i] > D_p[i+1] and ell_p[i] > 1400 and ell_p[i] < 2500:
        peaks.append((ell_p[i], D_p[i]))
print(f"  高 ℓ 局部峰 (ℓ>1400): {[(f'{l:.0f}', f'{v:.1f}') for l, v in peaks]}")

# 用第一個高 ℓ 峰做 m=8 候選 (實際聲學峰 m=8 喺 ℓ~1900?)
even_results = {}
if peaks:
    l8, v8 = peaks[0]
    r_ev = v8/v1
    print(f"  m=8 候選: ℓ={l8:.0f}, A={v8:.1f}, A/A₁ = {r_ev:.4f} vs 預言 1/9 = {1/9:.4f}")
    check("F-Q4.2c: 偶峰 m=8 樣本外 (dev<20% 為過, 阻尼區)",
          abs(r_ev-1/9)/(1/9) < 0.20, f"實測 {r_ev:.4f} vs 1/9: dev={abs(r_ev-1/9)/(1/9):.1%}")

with open(os.path.join(BASE, "data", "12_r12_odd_even.json"), "w") as f:
    json.dump({"r54_act": r54_act, "r76_act": r76_act,
               "pred_7_6": 7/6, "pred_121_112": 121/112,
               "act_bins": {"m4": [e4, v4], "m5": [e5, v5], "m6": [e6, v6], "m7": [e7, v7]},
               "high_l_peaks": peaks}, f, indent=2, default=str)

npass = sum(1 for r in results if r["pass"])
nfail = sum(1 for r in results if not r["pass"])
print(f"\n{'='*72}\nRESULT: {npass}/{len(results)} PASS\n{'='*72}")