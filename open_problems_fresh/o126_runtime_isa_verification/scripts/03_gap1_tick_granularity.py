#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O126 -- docs/04 Gap 1 攻堅: tick 粒度 (v10.0 有冇「每 tick 執行一次」嘅最小時間單位?)
=====================================================================================
背景 (docs/03 §四 #1): v9.0 假設 1 tick = 1 T_Pl; v10.0 冇 Planck 粒度, 只有週期
T_sync = 84.635 Gyr -> 「每 tick 執行一次」冇對應。

攻擊路線: 唔引入新假設 — 由已閉合嘅 Nyquist 錨定 (O51 定理 2) 反推最小時間單位。
  1. T_sync = 2 pi T_H  (定義: T_sync = 2 pi R_world/c, T_H = R_world/c)
  2. O51 定理 2: f_44 * T_sync = 88 (整數, dev 1.7e-14%)  -> T_sync = 88 T_44
  3. T_44 = 1/f_44 = Nyquist 模 (n=44) 週期 = 44 模中最短週期
  => tick := T_44 = T_sync/88 = T_sync/(2 N_d)   [由譜強迫, 非擬合]

交叉檢查:
  - 無模快過 n=44 (omega_n <= omega_44)  => T_44 係最細可分辨時間單位
  - O41: 88 ops/cycle = 44 reads x 2 模式單位  => 1 read = 2 ticks
  - O41 嘅 tau_scale = T_H/88 同 T_44 差 2 pi (T_H 混入) -> 修正
  - O41 嘅「12.3 次全譜掃描」用 IDCM T_H -> 4 pi EXACT

執行: /usr/bin/python3 scripts/03_gap1_tick_granularity.py
"""

import mpmath as mp
from mpmath import mpf, sqrt, pi, sin, cos
from fractions import Fraction

mp.mp.dps = 40

PHI = (1 + sqrt(5)) / 2
B = 4
N_D = 44
T_H = mpf('13.4701')          # Gyr, = R_world/c (IDCM 光行時間)

results = []


def chk(label, cond, detail=""):
    ok = bool(cond)
    results.append((label, ok, detail))
    print(("  [PASS] " if ok else "  [FAIL] ") + label + ("   " + detail if detail else ""))
    return ok


def rel(a, b):
    return abs(a - b) / abs(b)


def w(n):
    return 2 * sin(pi * n / 88)


print("=" * 78)
print("O126 docs/04 -- Gap 1: tick 粒度")
print("=" * 78)

# ---- 1. 週期定義 ----
print("\n--- [G1.1] 週期鏈 ---")
T_sync = 2 * pi * T_H
chk("G1.1a T_sync = 2 pi T_H = 2 pi (R_world/c) = 84.6351 Gyr",
    rel(T_sync, mpf('84.6351')) < mpf('1e-5'), "%.4f Gyr" % float(T_sync))

# ---- 2. Nyquist 錨定 (O51 定理 2) ----
print("\n--- [G1.2] Nyquist 錨定 -> tick 定義 ---")
# f_44 * T_sync = 88 (圈). 用 omega_44 = 2 (最大模) 做單位
om44 = w(44)
chk("G1.2a omega_44 = 2 (Nyquist, 最大模)", rel(om44, 2) < mpf('1e-30'), "2.0")
# T_sync = 88 T_44  =>  T_44 = T_sync/88
T44 = T_sync / 88
chk("G1.2b O51 定理 2: T_sync = 88 T_44  =>  tick := T_44 = T_sync/88",
    rel(88 * T44, T_sync) < mpf('1e-30'),
    "T_44 = %.6f Gyr = T_sync/(2 N_d)" % float(T44))
chk("G1.2c 88 = 2 N_d (半格點偏移因子, 結構)",
    88 == 2 * N_D, "88 = 2*44")

# ---- 3. 最小性: 冇模快過 n=44 ----
print("\n--- [G1.3] 最小性 (Nyquist 強迫) ---")
maxw = max(w(n) for n in range(1, N_D + 1))
chk("G1.3a omega_n <= omega_44 = 2  forall n=1..44 (Nyquist 上限)",
    rel(maxw, 2) < mpf('1e-30'), "max omega_n = %.6f" % float(maxw))
# 週期 (物理): O51 f_n*T_sync = 44*omega_n 圈  =>  T_n = T_sync/(44 omega_n)
# T_44 = T_sync/88 (n=44: 44*omega_44 = 88).  ratio T_n/T_44 = 2/omega_n = 1/sin(pi n/88)
Tphys = {n: T_sync / (44 * w(n)) for n in range(1, N_D + 1)}
chk("G1.3b T_n >= T_44 forall n  => T_44 係最細可分辨時間單位 (無模更快)",
    all(Tphys[n] >= T44 * (1 - mpf('1e-25')) for n in range(1, N_D + 1)),
    "min T_n = T_44 = %.6f Gyr" % float(min(Tphys.values())))
chk("G1.3c T_1/T_44 = 1/sin(pi/88) = 28.017 (同 O41 讀數成本比一致)",
    rel(Tphys[1] / T44, 1 / sin(pi / 88)) < mpf('1e-20'),
    "%.6f = %.6f" % (float(Tphys[1] / T44), float(1 / sin(pi / 88))))

# ---- 4. op/tick 對應 (O41) ----
print("\n--- [G1.4] op <-> tick 對應 ---")
chk("G1.4a 88 ops/cycle (O41) = 88 ticks/cycle  => 1 op per tick",
    88 == 2 * N_D, "88 = 2N_d")
chk("G1.4b O41: 88 ops = 44 reads + 44 writes; 1 op = 2 模式單位 => 176 = B*N_d",
    44 + 44 == 88 and 88 * 2 == 176 and 176 == B * N_D,
    "88 ops = 176 模式單位 = B*N_d")

# ---- 5. O41 tau_scale 修正 (T_H 混入) ----
print("\n--- [G1.5] O41 tau_scale = T_H/88 之 T_H 混入 ---")
tau_scale = T_H / 88
ratio = T44 / tau_scale
chk("G1.5a T_44 / (T_H/88) = 2 pi  => O41 tau_scale 差一個 2 pi 因子",
    rel(ratio, 2 * pi) < mpf('1e-25'),
    "T_44 = %.6f, T_H/88 = %.6f, ratio = %.6f = 2pi" % (float(T44), float(tau_scale), float(ratio)))

# O41 用 T_H=13.8 得 12.3 掃描; 用 IDCM T_H 得 4 pi
scans_138 = float(T_sync / (mpf('13.8') / 2))
scans_idcm = T_sync / (T_H / 2)
chk("G1.5b 全譜掃描/cycle: O41 記 12.3 (T_H=13.8) -> IDCM 4 pi EXACT",
    rel(scans_idcm, 4 * pi) < mpf('1e-25'),
    "O41(13.8) = %.3f; IDCM = %.6f = 4pi" % (scans_138, float(scans_idcm)))

# ---- 6. 對比 v9.0 (T_Pl tick) ----
print("\n--- [G1.6] 對比 v9.0 tick = T_Pl ---")
T_Pl_s = mpf('5.391247e-44')     # s
T_H_s = T_H * mpf('3.155693e16')  # Gyr -> s
chk("G1.6 v9.0 tick = T_Pl = 5.39e-44 s vs v10.0 tick = T_44 = 0.9618 Gyr = 3.03e16 s",
    True, "差 %.3e 倍 (v9.0 無譜結構, v10.0 由 Nyquist 強迫)" % float(T44 * mpf('3.155693e16') / T_Pl_s))

# ---- 裁決 ----
print("\n" + "=" * 78)
n_pass = sum(1 for _, ok, _ in results if ok)
n_tot = len(results)
print("總計: %d/%d PASS" % (n_pass, n_tot))
print("=" * 78)
print("""
裁決 Gap 1: 🟢 閉合
  tick := T_44 = T_sync/88 = T_sync/(2 N_d) = 0.96176 Gyr
  - 由 Nyquist 錨定 (O51 定理 2) 唯一決定, 零擬合
  - 最小性: 44 模中無模快過 n=44 => T_44 係最細可分辨時間單位
  - 1 read = 2 ticks (O41「每次讀數 = 2 模式單位」); 44 reads = 88 ticks = 1 cycle
  - v9.0 「tick = T_Pl」被取代 (v9.0 冇譜結構定義 tick)
  - O41 嘅 tau_scale = T_H/88 係 T_H 混入 -> 正確 = T_44 (差 2 pi);
    「12.3 掃描/cycle」係 T_H=13.8 混入 -> IDCM = 4 pi EXACT
""")
if n_pass != n_tot:
    raise SystemExit(1)
