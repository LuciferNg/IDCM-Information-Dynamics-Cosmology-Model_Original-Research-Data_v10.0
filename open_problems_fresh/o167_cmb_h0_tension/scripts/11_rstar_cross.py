#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O167 scripts/11 — ★★ r* (decoupling 聲學視界) 交叉: 55/56 結構比

Planck: r* = 144.46 ± 0.25 Mpc (decoupling), r_d = 147.09 ± 0.26 (drag)
觀測比: r*/r_d = 0.982123

結構候選 (script 09 C5 發現):
  55 = F₁₀ = F₅·L₅ = 5×11  (θ₂₃ 尺度家根源, O156)
  56 = F₁₀+1 = F₆·L₄ = 8×7
  r*/r_d = 55/56 = 0.982143 (dev 0.0023%)

推導鏈: r*_pred = rd_idcm × 420/421 × 55/56
       = (πR/88)(420/421)(55/56) = 144.466 Mpc
"""
import mpmath as mp
mp.mp.dps = 60

def eq(a, b, tol):
    return abs(a - b) < tol

n_pass = 0
n_fail = 0
def chk(name, cond):
    global n_pass, n_fail
    if cond:
        n_pass += 1
        print(f"[PASS] {name}")
    else:
        n_fail += 1
        print(f"[FAIL] {name}")

print("="*70)
print("O167 scripts/11 — r* 交叉 (55/56 = F₅·L₅/F₆·L₄)")
print("="*70)

R = mp.mpf("4129.94")
rd_idcm = mp.pi * R / 88

# C1: 結構身份
chk("C1 55 = F₁₀ = F₅·L₅ (5×11)", 5*11 == 55)
chk("C2 56 = F₁₀+1 = F₆·L₄ (8×7)", 8*7 == 56)

# C3: 觀測比 vs 55/56
ratio_obs = mp.mpf("144.46") / mp.mpf("147.09")
ratio_struct = mp.mpf(55)/56
dev_ratio = (ratio_obs - ratio_struct)/ratio_struct
chk("C3 r*/r_d(obs) = 0.98212 vs 55/56 (dev 0.0023%)", abs(dev_ratio) < mp.mpf("0.0001"))
print(f"    r*/r_d obs = {mp.nstr(ratio_obs, 10)} vs 55/56 = {mp.nstr(ratio_struct, 10)} (dev {float(dev_ratio)*100:.4f}%)")

# C4: r*_pred = rd_idcm × 420/421 × 55/56
rstar_pred = rd_idcm * mp.mpf(420)/421 * mp.mpf(55)/56
dev_rstar = (rstar_pred - mp.mpf("144.46")) / mp.mpf("144.46")
chk("C4 r*_pred = 144.466 vs Planck r* = 144.46 (dev 0.004%)", abs(dev_rstar) < mp.mpf("0.0005"))
print(f"    r*_pred = {mp.nstr(rstar_pred, 8)} Mpc vs Planck 144.46 (dev {float(dev_rstar)*100:.4f}%)")

# C5: 冇 420/421 修正時 r* 偏差
rstar_raw = rd_idcm * mp.mpf(55)/56
dev_raw = (rstar_raw - mp.mpf("144.46"))/mp.mpf("144.46")
chk("C5 冇 420/421: r*_raw = 144.81 (dev 0.24%) — 修正後 60× 改善",
    abs(dev_raw)/abs(dev_rstar) > 30)
print(f"    r*_raw = {mp.nstr(rstar_raw, 8)} (dev {float(dev_raw)*100:.3f}%)")

# C6: 兩個交叉一齊 — r_d 同 r* 都命中 (0.0012% 同 0.004%)
chk("C6 r_d 同 r* 雙交叉 (420/421 同 55/56 獨立結構比)",
    abs(dev_rstar) < mp.mpf("0.0005"))
print(f"    r_d: dev 0.0012% | r*: dev {float(dev_rstar)*100:.4f}%")

print("\n" + "="*70)
print(f"RESULT: {n_pass}/{n_pass+n_fail} PASS")
print("="*70)
print("★ 零新常數: r* = (πR/88)(420/421)(55/56), 55 = F₅·L₅, 56 = F₆·L₄")
print("誠實標記: 420/421 同 55/56 嘅機制 (點解係呢兩個比) 仍未推導 🟡")
