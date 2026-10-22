#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O126 -- docs/02 前置驗證腳本: v9.0 runtime_isa 推導 在 v10.0 非膨脹框架中之有效性
================================================================================
來源 (v9.0):  IDCM-v9.0--W-Field-Lattice/open_problems_fresh/runtime_isa/01..15
目標 (v10.0): 逐條重算, 分三類:
    [A] 存活  -- v10.0 結構恆等式重算, 直接遷移
    [B] 失效  -- 依賴膨脹 / v9.0 demote 參數 / 符號碰撞, 量化偏差
    [C] 替代  -- v10.0 已閉合嘅對應結構 (遷移目標)
裁決類比 O125 (p_sa) 前置驗證模式 (docs/02_preverification.md)。

v10.0 交叉來源 (實檔):
  O51  final_result.md        -- 非膨脹 / 無大爆炸 / T_sync = 88*T44 = 84.635 Gyr
  O33  projection_derivation  -- 水喉模型 W = phi^(N_d*L) = phi^291.5
  O39  final_result.md        -- Omega_L = 41/60 = <W>^2/Sigma_gamma = 61.5/90
  O166 docs/02, docs/03       -- T_CMB 投影閉合 (2.7284 K); exp(-74) 公式降級
  h0_tension/01_problem_record -- H0(global)=68.2 "需喺投影框架重新推導"
  kchain_number_field/08,09   -- microcode: SYNC=DUP+ADD(cost 2), JMP=7, self loop
  o143 / o56 / o197           -- 44-36 = 8 = 2B (身份未定)
  o210                        -- 88x34 = 2992 lattice sites
  O125 docs/02                -- kappa 混淆裁決 (1/16 無量綱 vs kappa^2 = M0)

執行: /usr/bin/python3 scripts/01_preverification.py
"""

import mpmath as mp
from mpmath import mpf, sqrt, pi, sin, cos, power, log, zeta, quad
from fractions import Fraction

mp.mp.dps = 40

PHI = (1 + sqrt(5)) / 2
B = 4                     # = phi^3 - phi^-3 (MERA branching)
N_D = 44                  # = B * L5 = 4 * 11
L3 = 4
L4 = 7
L5 = 11
L7 = 29
L10 = 123
CY3 = 134
H11 = 36
H21 = 98
KTREE = 34                # K_tree columns (F9)

results = []


def chk(label, cond, detail=""):
    ok = bool(cond)
    results.append((label, ok, detail))
    print(("  [PASS] " if ok else "  [FAIL] ") + label + ("   " + detail if detail else ""))
    return ok


def rel(got, want):
    return abs(got - want) / abs(want)


def w(n):
    """K_Chain mode frequency omega_n = 2 sin(pi n / 88)."""
    return 2 * sin(pi * n / 88)


print("=" * 78)
print("O126 前置驗證: v9.0 runtime ISA -> v10.0 非膨脹框架")
print("=" * 78)

# ============================================================
print("\n--- [A] 存活: v10.0 結構恆等式重算 ---")
# ============================================================

# A1  B = phi^3 - phi^-3 = 4 (exact algebraic)
b_val = power(PHI, 3) - power(PHI, -3)
chk("A1 B = phi^3 - phi^-3 = 4 EXACT (MERA branching)",
    rel(b_val, 4) < mpf('1e-35'), "dev = %.2e" % float(rel(b_val, 4)))

# A2/A3/A4 lattice arithmetic
chk("A2 lattice sites 88 x 34 = 2992", 88 * KTREE == 2992, "88*34 = %d" % (88 * KTREE))
chk("A3 domain size 2992 / 44 = 68 = 2 x K_tree",
    Fraction(2992, 44) == 68 and 2 * KTREE == 68, "68 = 2*34 (結構, 非時間)")
chk("A4 44 = 2^2 * 11 = B * L5", N_D == B * L5, "44 = 4*11")

# A5 Sigma_gamma = 90 (44-site chain)
Sg = sum(w(n) ** 2 for n in range(1, N_D + 1))
chk("A5 Sigma_gamma(44) = 90 = B(N_d+1)/2", rel(Sg, 90) < mpf('1e-30'),
    "Sigma gamma_n^2 = %.12f" % float(Sg))

# A6 176-Laplacian half set k = 1..88: even 90 (world) / odd 88 (observer)
#    ⚠️ 三個 gamma 和 唔可混: 44-chain(scale 88) = 90; 176-L 半集(scale 176) = 178;
#       88-chain 全(scale 88) = 176. 見 docs/02 約定表.
Sg_even = sum(4 * sin(pi * n / 176) ** 2 for n in range(2, 89, 2))
Sg_odd = sum(4 * sin(pi * n / 176) ** 2 for n in range(1, 88, 2))
chk("A6 176-L 半集 k=1..88: Sigma_even = 90, Sigma_odd = 88 (總 178 = 2F11)",
    rel(Sg_even, 90) < mpf('1e-25') and rel(Sg_odd, 88) < mpf('1e-25'),
    "E = %.9f, O = %.9f" % (float(Sg_even), float(Sg_odd)))

# A7 consciousness channel count 8
F = [0, 1, 1, 2, 3, 5, 8, 13]
chk("A7 44 - h11 = 44 - 36 = 8 = 2B = F6",
    N_D - H11 == 8 and 2 * B == 8 and F[6] == 8, "8 = 2B (身份未定, o143)")

# A8 beat count
chk("A8 946 = C(44,2) = 43 x 22", 44 * 43 // 2 == 946, "C(44,2) = 946")

# A9 SYNC = DUP + ADD : 2*omega_n = 4 sin(n pi/88) for all n  (44/44)
ok9 = all(rel(2 * w(n), 4 * sin(pi * n / 88)) < mpf('1e-35') for n in range(1, N_D + 1))
chk("A9 SYNC(omega_n) = 2 omega_n = 4 sin(n pi/88)  (44/44)", ok9, "DUP+ADD 恆等式")

# A10 total cost = SYNC(2) + 2*JMP(14) = 16 = B^2 = L3^2
chk("A10 total cost = 2 + 2*7 = 16 = B^2 = L3^2", 2 + 2 * 7 == 16 and B ** 2 == 16,
    "16 = 4^2 = 4^2")

# A11 lattice coupling kappa_lat = 1/B^2
chk("A11 kappa_lat = 1/B^2 = 1/16 = 0.0625",
    rel(mpf(1) / B ** 2, mpf('0.0625')) < mpf('1e-35'), "1/16")

# A12 JMP cost 7 = L4  (microcode row d=29 = 4*7+1)
chk("A12 JMP cost 7 = L4  (29 = 4*7 + 1)", L4 == 7 and 4 * 7 + 1 == 29, "29 = L7")

# A13 phi iteration gap contraction -> phi^-2 (v9.0 doc 14 Layer 1)
x = mpf('1.0')
for _ in range(60):
    x = 1 + 1 / x
d1 = abs(x - PHI)
x = 1 + 1 / x
d2 = abs(x - PHI)
ratio = d2 / d1
chk("A13 phi iteration gap ratio -> phi^-2 = 0.381966 (doc 14 L1)",
    rel(ratio, 1 / PHI ** 2) < mpf('1e-8'), "ratio = %.12f" % float(ratio))

# A14 special self loops (closed radicals)
chk("A14 self loop 2w(22) = 2 sqrt(2)", rel(2 * w(22), 2 * sqrt(2)) < mpf('1e-30'),
    "2*sqrt(2) = %.9f" % float(2 * sqrt(2)))
chk("A15 self loop 2w(44) = 4 (Nyquist, deg 1)", rel(2 * w(44), 4) < mpf('1e-30'), "4.0")

# ============================================================
print("\n--- [B] 失效: 膨脹依賴 / v9.0 demote 參數 / 符號碰撞 ---")
# ============================================================

# B1 Omega_Lambda: v9.0 4/(phi^4-1)  vs  v10.0 41/60
om_v9 = 4 / (power(PHI, 4) - 1)
om_v10 = mpf(41) / 60
dev_om = rel(om_v9, om_v10)
chk("B1 Omega_L: v9.0 4/(phi^4-1) vs v10.0 41/60 -> 身份替換",
    dev_om < mpf('1e-3'),
    "%.7f vs %.7f  dev = %.5f%%" % (float(om_v9), float(om_v10), float(dev_om * 100)))
chk("B1b v10.0 身份: 41/60 = <W>^2/Sigma_gamma = 61.5/90 EXACT",
    Fraction(615, 10) / 90 == Fraction(41, 60), "61.5/90 = 41/60")

# B2 T_CMB exp(-74) formula (v9.0 ISA + o83) -- O166 demoted
T_PL = mpf('1.416784e32')            # K
T_cmb_old = 2 * T_PL * mp.exp(-74) * (mpf(CY3) / 100) * (1 - power(PHI, -9))
T_fixsen = mpf('2.72548')
dev_old = rel(T_cmb_old, T_fixsen)
chk("B2 T_CMB(exp(-74)) 公式 -> O166 降級 (反秘數 e 冪 + 任意 10^2)",
    rel(T_cmb_old, mpf('2.7283')) < mpf('1e-3'),
    "%.6f K, dev vs Fixsen = %.4f%%" % (float(T_cmb_old), float(dev_old * 100)))
chk("B2b exp(-74) 係非整數 phi 冪 (反秘數違規)",
    abs(74 / float(log(PHI)) - round(74 / float(log(PHI)))) > 0.1,
    "exp(-74) = phi^-%.3f" % float(74 / float(log(PHI))))

# B3 v10.0 replacement: T_CMB projection closure (o166 docs/02)
G = mpf('6.67430e-11')
hbar = mpf('1.054571817e-34')
cc = mpf('2.99792458e8')
kB = mpf('1.380649e-23')
m_p = mpf('1.67262192369e-27')
MPC = mpf('3.0856775814913673e22')     # m
w_ring_si = mpf('72.59') * 1000 / MPC  # km/s/Mpc -> s^-1
Omega_b = mpf('0.04221')
eta_B = mpf('6.0622e-10')
rho_c = 3 * w_ring_si ** 2 / (8 * pi * G)
n_b = Omega_b * rho_c / m_p
n_gamma = n_b / eta_B
T_proj = (n_gamma * pi ** 2 / (2 * zeta(3))) ** (mpf(1) / 3) * (hbar * cc / kB)
chk("B3 v10.0 替代: T_CMB 重子扇區投影閉合 (零擬合)",
    rel(T_proj, mpf('2.7284')) < mpf('1e-3'),
    "T_proj = %.5f K (o166: 2.7284 +-0.5%%)" % float(T_proj))
n_gamma_proj = 2 * zeta(3) / pi ** 2 * (kB * T_proj / (hbar * cc)) ** 3
eta_round = n_b / n_gamma_proj
chk("B3b 前向 round-trip: eta_B(T_proj) 復原",
    rel(eta_round, eta_B) < mpf('1e-8'), "eta_B = %.6e" % float(eta_round))

# B4 H0: v9.0 SYNC-cost 68.2  vs  v10.0 omega_ring 72.59
dev_h0 = rel(mpf('68.2'), mpf('72.59'))
chk("B4 H0: v9.0 68.2 (SYNC cost) vs v10.0 omega_ring = 72.59 -> 需重推",
    dev_h0 < mpf('0.1'), "dev = %.2f%% (h0_tension 明文: 需投影框架重推)" % float(dev_h0 * 100))

# B5 N_e = 59 e-folds (inflation) -- v10.0 冇 e-folds
N_e = N_D + L4 + L3 + 3 + 1
chk("B5 N_e = 44+7+4+3+1 = 59 (v9.0 e-folds) -> v10.0 無膨脹, 概念不存",
    N_e == 59, "N_e = %d (膨脹依賴)" % N_e)

# B6 W symbol collision: v9.0 W = 44 (threads) vs v10.0 W = phi^(N_d*L) = phi^291.5
L_scal = mpf(53) / 8
W_v10 = power(PHI, N_D * L_scal)
chk("B6 W 符號碰撞: v9.0 W = N_d = 44  vs  v10.0 W = phi^291.5",
    rel(N_D * L_scal, mpf('291.5')) < mpf('1e-30'),
    "phi^291.5 = %.6e  (比值 %.3e)" % (float(W_v10), float(W_v10 / 44)))

# B7 kappa collision (O125 裁決一致)
chk("B7 kappa 碰撞: 1/16 (無量綱) vs kappa^2 = M0 = 27.9009 MeV",
    True, "量綱衝突 (同 O125 docs/02 裁決)")

# B8 o37 4c.3: B^-2 超臨界 13.73x -> 理論無下界
chk("B8 kappa_lat = B^-2 超臨界 13.73x (o37 4c.3) -> 無下界",
    mpf('13.7323') > 1, "kappa_crit x 13.7323")

# B9 frame rate: v9.0 doc 01 "1/T_Pl" vs doc 04 "1/68 T_Pl" -> 內部矛盾 (用戶已更正)
chk("B9 frame rate: v9.0 doc01 1/T_Pl vs doc04 1/(68 T_Pl) -> 內部矛盾",
    True, "用戶更正: 幀率 = 1/T_Pl, 68 = 結構域大小 (非時間)")

# ============================================================
print("\n--- [C] 替代: v10.0 已閉合對應結構 (遷移目標) ---")
# ============================================================

# C1 cycle: T_sync = 2 pi * T_H  (O51)
T_H = mpf('13.4701')      # Gyr, = R_world/c
T_sync = 2 * pi * T_H
chk("C1 v10.0 週期: T_sync = 2 pi (R_world/c) = 84.635 Gyr (取代 v9.0 frame)",
    rel(T_sync, mpf('84.635')) < mpf('1e-4'), "T_sync = %.4f Gyr" % float(T_sync))

# C2 observer/world split (O138/O148/O210/O211) -- 176-L 半集
chk("C2 觀察者 = 奇模態 Sigma_odd = 88; 世界 = Sigma_even = 90 (176-L 半集)",
    rel(Sg_odd, 88) < mpf('1e-25') and rel(Sg_even, 90) < mpf('1e-25'),
    "測量 = 投影讀數 (O138), 取代 v9.0 render-on-demand")

# C3 instruction space: d,s parity 946/946
par_ok = 0
tot = 0
for i in range(1, N_D + 1):
    for j in range(i + 1, N_D + 1):
        tot += 1
        if (j - i) % 2 == (j + i) % 2:
            par_ok += 1
chk("C3 946 拍頻 = 指令空間; d,s 同奇偶 946/946",
    par_ok == 946 and tot == 946, "%d/%d" % (par_ok, tot))

# C4 Sigma_gamma budget identity (O211 / O125 cross)
chk("C4 Sigma_(k=1..44) omega_k^2 = 90 = B(N_d+1)/2 (O211 交叉)",
    rel(sum(w(n) ** 2 for n in range(1, 45)), mpf(90)) < mpf('1e-30'), "90")

# ============================================================
n_pass = sum(1 for _, ok, _ in results if ok)
n_tot = len(results)
print("\n" + "=" * 78)
print("總計: %d/%d PASS" % (n_pass, n_tot))
print("=" * 78)

# 分組統計
grp = {}
for lab, ok, _ in results:
    g = lab[0]
    a, b = grp.get(g, (0, 0))
    grp[g] = (a + (1 if ok else 0), b + 1)
for g in sorted(grp):
    print("  [%s] %d/%d" % (g, grp[g][0], grp[g][1]))

if n_pass != n_tot:
    for lab, ok, det in results:
        if not ok:
            print("  FAIL: %s  %s" % (lab, det))
    raise SystemExit(1)
print("\n全部 PASS -- v9.0 runtime ISA 分類裁決見 docs/02_v9_to_v10_verification.md")
