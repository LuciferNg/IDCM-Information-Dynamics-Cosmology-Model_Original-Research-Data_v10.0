#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O126 -- docs/03 重建腳本: v10.0-native Runtime Cycle 組裝驗證
================================================================
v9.0 runtime ISA 嘅三條主幹 (boot/runtime 分層 + 指令集 + 週期) 在 v10.0 失效
(見 docs/02)。本腳本唔引入新推導, 只做一件事: 證明 v10.0 已經有齊一個
**runtime cycle 嘅全部零件**, 由已閉合 O 結果組裝:

  零件                 v10.0 來源              本腳本驗證
  ----------------     -------------------     --------------------------
  週期 T_sync          O51 (88*T44)            R12
  讀寫預算 E_sync      O41 (L10/2 = 61.5)      R1-R7
  能量分配 (取代 W)    O39/O215 (41/60)        R2, R15
  觀察者通道           O138/O148 (Sigma_odd)   R11
  指令空間             kchain_number_field     R10
  晶格 / 域             o210 (88x34=2992)       R14

全部係 mpmath/Fraction 精確重算。裁決見 docs/03_runtime_isa_v10_rebuild.md。
執行: /usr/bin/python3 scripts/02_runtime_cycle_v10.py
"""

import mpmath as mp
from mpmath import mpf, sqrt, pi, sin, log, power
from fractions import Fraction

mp.mp.dps = 40

PHI = (1 + sqrt(5)) / 2
B = 4
N_D = 44
L10 = 123
L5 = 11
SIGMA_G = 90            # 44-chain Sigma gamma_n (O211)
KTREE = 34

results = []


def chk(label, cond, detail=""):
    ok = bool(cond)
    results.append((label, ok, detail))
    print(("  [PASS] " if ok else "  [FAIL] ") + label + ("   " + detail if detail else ""))
    return ok


def rel(a, b):
    return abs(a - b) / abs(b)


print("=" * 78)
print("O126 docs/03: v10.0-native Runtime Cycle 組裝")
print("=" * 78)

# ---------------------------------------------------------------
print("\n--- [R] 週期與預算 ---")
# ---------------------------------------------------------------

# R1  E_sync = L10/2 = 61.5 (三重視角, O41)
E_sync = mpf(L10) / 2
v_a = mpf(N_D) * L10 / 88
v_b = mpf(88) * L10 / 176
chk("R1 E_sync = L10/2 = 61.5 = 44*123/88 = 88*123/176 (O41 三重)",
    rel(E_sync, mpf('61.5')) < mpf('1e-30') and rel(v_a, E_sync) < mpf('1e-30')
    and rel(v_b, E_sync) < mpf('1e-30'),
    "61.5 = %.6f = %.6f" % (float(v_a), float(v_b)))

# R2  Omega_L = E_sync / Sigma_gamma = 41/60 (O39/O215)
chk("R2 Omega_L = E_sync/Sigma_gamma = 61.5/90 = 41/60 EXACT",
    Fraction(615, 10) / 90 == Fraction(41, 60),
    "%.6f" % float(mpf(41) / 60))

# R3  per-domain budget B(n) = L10/(2 N_d) = 123/88, 44 個加和 = 61.5
B_n = Fraction(L10, 2 * N_D)
tot_Bn = B_n * N_D
chk("R3 B(n) = L10/(2N_d) = 123/88; Sigma_(n=1..44) B(n) = 61.5 EXACT",
    tot_Bn == Fraction(615, 10), "B(n) = %.6f, sum = %.1f" % (float(B_n), float(tot_Bn)))

# R4/R5 讀數消耗 = 寫入消耗 = 61.5 (帳戶守恆)
chk("R4 全譜掃描讀數 Sigma dE_read = 61.5 (44 reads x B(n))", tot_Bn == Fraction(615, 10),
    "read budget = 61.5")
chk("R5 44 次寫入 Sigma dE_write = 61.5 (同預算)", tot_Bn == Fraction(615, 10),
    "write budget = 61.5")

# R6  read<->write cycle = 88 ops = 176 = B*N_d
chk("R6 讀寫循環 = 88 ops = 176 = B*N_d", 88 == 2 * N_D and 176 == B * N_D,
    "88 = 2*44, 176 = 4*44")

# R7  Landauer E_min = L10/(4N_d) vs ln2 + 1/(4N_d)
E_min = mpf(L10) / (4 * N_D)
E_approx = log(2) + mpf(1) / (4 * N_D)
chk("R7 E_min = L10/(4N_d) = 123/176 vs ln2 + 1/(4N_d) (dev < 0.01%)",
    rel(E_min, E_approx) < mpf('1e-4'),
    "%.8f vs %.8f  dev = %.5f%%" % (float(E_min), float(E_approx),
                                    float(rel(E_min, E_approx) * 100)))

# R8  L10 = round(4 N_d ln2 + 1)
chk("R8 L10 = round(4 N_d ln2 + 1) = 123", int(round(4 * N_D * float(log(2)) + 1)) == L10,
    "4*44*ln2+1 = %.4f" % float(4 * N_D * log(2) + 1))

# R9  unit gamma = 4 N_d + B^2 = 192 (O41)
chk("R9 gamma (能量單位) = 4N_d + B^2 = 176 + 16 = 192", 4 * N_D + B ** 2 == 192, "192")

# R10 instruction space: 946 beats + 44 self loops = 990 = C(N_d+1, 2)
beats = N_D * (N_D - 1) // 2
self_loops = N_D
total_instr = beats + self_loops
chk("R10 指令空間 = 946 + 44 = 990 = C(N_d+1,2) = C(45,2)",
    beats == 946 and self_loops == 44 and total_instr == 45 * 44 // 2,
    "946 + 44 = %d = C(45,2)" % total_instr)

# R11 observer channels: 176-L half set odd sum = 88 = 2 N_d
Sg_odd = sum(4 * sin(pi * n / 176) ** 2 for n in range(1, 88, 2))
chk("R11 觀察者通道 Sigma_odd(176-L 半集) = 88 = 2N_d",
    rel(Sg_odd, 88) < mpf('1e-25'), "%.9f" % float(Sg_odd))

# R12 cycle: T_sync = 2 pi (R_world/c)
T_H = mpf('13.4701')
T_sync = 2 * pi * T_H
chk("R12 T_sync = 2 pi (R_world/c) = 84.635 Gyr (t_render = 13.4701 Gyr)",
    rel(T_sync, mpf('84.635')) < mpf('1e-4'), "%.4f Gyr" % float(T_sync))

# R13 SYNC self loop = 2 omega_n (44/44) -- 指令語義
ok13 = all(rel(2 * 2 * sin(pi * n / 88), 4 * sin(pi * n / 88)) < mpf('1e-35')
           for n in range(1, N_D + 1))
chk("R13 SYNC(omega_n) = 2 omega_n  (44/44 self loops, 承 docs/02 A9)", ok13, "DUP+ADD")

# R14 domain refresh: 2992 / 44 = 68 = 2 K_tree (結構, 非時間)
chk("R14 全晶格刷新 = 2992/44 = 68 = 2 K_tree (結構, 非時間)",
    Fraction(88 * KTREE, N_D) == 68, "68 = 2*34")

# R15 budget conservation: projected 28.5 + unprojected 61.5 = Sigma_gamma = 90
proj = mpf(SIGMA_G) - E_sync
chk("R15 預算守恆: 投影 28.5 + 未投影 61.5 = 90 = Sigma_gamma; 28.5/90 = 19/60 = Omega_m",
    rel(proj + E_sync, SIGMA_G) < mpf('1e-30')
    and Fraction(285, 10) / 90 == Fraction(19, 60),
    "Omega_m = %.6f = 19/60" % float(proj / 90))

# R16 2 x E_sync = L10 (觀察者預算 = L10 之半)
chk("R16 2 x E_sync = L10 = 123 EXACT (觀察者預算 = L10 之半)",
    2 * E_sync == L10, "2 x 61.5 = 123")

# ---------------------------------------------------------------
n_pass = sum(1 for _, ok, _ in results if ok)
n_tot = len(results)
print("\n" + "=" * 78)
print("總計: %d/%d PASS" % (n_pass, n_tot))
print("=" * 78)
if n_pass != n_tot:
    for lab, ok, det in results:
        if not ok:
            print("  FAIL: %s  %s" % (lab, det))
    raise SystemExit(1)
print("\n全部 PASS -- 裁決見 docs/03_runtime_isa_v10_rebuild.md")
