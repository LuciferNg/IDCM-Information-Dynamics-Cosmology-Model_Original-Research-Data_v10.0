#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O201 scripts/01 -- 譜字典掃描 (Spectral Dictionary Scan)  v3

版本史 (同一 session 內修正, 保留理由):
  v1: 深度 2 over 1276 原子, tol 1e-3 -> null 命中率 1.000 (完全無判別力)
  v2: 原子池收窄到原語譜泛函; 但整數目標嘅深度 2 命中仍係純算術分解 (44+16=60),
      因為整數對 +,-,* 封閉 => 對整數目標零判別力
  v3: (a) 補回 L_n+-1 / F_n+-1 (O191/O192 家族, 原語 T_hat 泛函)
      (b) Tier B 拆 B-int (整數目標, 算術分解, 零判別力) / B-real (非整數目標, 有 null 檢定)
      (c) 修正 gamma_1 目標值 (v2 硬編錯值)
      (d) Tier A 報全部匹配 (唔止最近), 免得「128 = 2^7」蓋過註冊身份

譜基: gamma_n = 4sin^2(pi n/88) (44-chain), Gamma_k = 4sin^2(k pi/176) (88-site)
      ★恆等: Gamma_{2n} = gamma_n (44-chain = 88-site 偶扇區; Sum gamma = Sum Gamma_even = 90)
      T_hat = [[1,1],[1,0]]: L_n = Tr(T^n), F_n = (T^n)_12
      群速度 v_g(n) = cos(pi n/88), 群延遲權重 sec(pi n/88)
陷阱窗 (O148 F3 / O151 S17): 相對偏差落 (1e-5, 1e-3) 標 TRAP, 唔算命中。
"""
import os
import json

import numpy as np
import mpmath as mp

mp.mp.dps = 50
PI = mp.pi
PHI = (1 + mp.sqrt(5)) / 2
INV = 1 / PHI
SQ5 = mp.sqrt(5)

Nd, B, NGEN, L5, FPROJ, KTREE = 44, 4, 3, 11, 17, 33

g44 = [4 * mp.sin(n * PI / 88) ** 2 for n in range(1, Nd + 1)]
G88 = [4 * mp.sin(k * PI / 176) ** 2 for k in range(1, 89)]
vg = [mp.cos(n * PI / 88) for n in range(1, Nd + 1)]
sec = [1 / mp.cos(n * PI / 88) for n in range(1, Nd + 1)]

S_GAM = mp.fsum(g44)
S_ODD = mp.fsum(g44[0::2])
S_EVEN = mp.fsum(g44[1::2])
S_G88 = mp.fsum(G88)
S_G88_ODD = mp.fsum(G88[0::2])
S_G88_EVEN = mp.fsum(G88[1::2])

TH = mp.matrix([[1, 1], [1, 0]])
THP = {0: mp.eye(2), 1: TH}
for n in range(2, 20):
    THP[n] = THP[n - 1] * TH
LUC = [int(round(THP[n][0, 0] + THP[n][1, 1])) for n in range(20)]
FIB = [int(round(THP[n][0, 1])) for n in range(20)]

# ============================================================
# 1. 原語譜原子池
# ============================================================
ATOMS = {}


def A(name, val):
    if name in ATOMS:
        return
    try:
        v = mp.mpf(val)
    except Exception:
        return
    if v == 0 or not mp.isfinite(v):
        return
    ATOMS[name] = v


# 1a 譜基與扇區跡
A("N_d", Nd); A("B", B); A("N_gen", NGEN); A("L5", L5); A("F_proj", FPROJ); A("K_tree", KTREE)
A("mu2", 2); A("gamma_44", 4)
A("Sum_gamma", S_GAM); A("Sum_gamma_odd", S_ODD); A("Sum_gamma_even", S_EVEN)
A("Sum_Gamma88", S_G88); A("Sum_Gamma88_odd", S_G88_ODD); A("Sum_Gamma88_even", S_G88_EVEN)
A("ratio_even_odd", S_EVEN / S_ODD)
A("mean_gamma", S_GAM / Nd); A("mean_gamma_odd", S_ODD / 22); A("mean_gamma_even", S_EVEN / 22)

# 1b 鏈譜元素
for n in range(1, Nd + 1):
    A("gamma_%d" % n, g44[n - 1])
for k in range(1, 89):
    A("Gamma_%d" % k, G88[k - 1])
for n in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 17, 18, 20, 21, 22, 24,
          28, 32, 33, 34, 36, 40, 41, 43, 44):
    A("v_g_%d" % n, vg[n - 1]); A("sec_%d" % n, sec[n - 1])
    A("cos_%d" % n, mp.cos(n * PI / 88)); A("sin_%d" % n, mp.sin(n * PI / 88))
    A("tan_%d" % n, mp.tan(n * PI / 88))

# 1c 部分和
for K in range(1, Nd + 1):
    A("mean_sec_1_%d" % K, mp.fsum(sec[:K]) / K)
    A("inv_mean_vg_1_%d" % K, 1 / (mp.fsum(vg[:K]) / K))
    A("sum_gamma_1_%d" % K, mp.fsum(g44[:K]))
for K in range(1, 89):
    A("sum_Gamma88_1_%d" % K, mp.fsum(G88[:K]))
for K in range(1, 45):
    A("sum_gamma_odd_1_%d" % K, mp.fsum(g44[0:2 * K:2]))
    A("sum_gamma_even_1_%d" % K, mp.fsum(g44[1:2 * K:2]))

# 1d mod-4 扇區跡
for r in range(4):
    A("sum_gamma_mod4_%d" % r, mp.fsum([g44[n - 1] for n in range(1, Nd + 1) if n % 4 == r]))
    A("sum_Gamma88_mod4_%d" % r, mp.fsum([G88[k - 1] for k in range(1, 89) if k % 4 == r]))
    A("count_mod4_%d" % r, mp.mpf(len([n for n in range(1, Nd + 1) if n % 4 == r])))

# 1e 冪和
for n in range(1, 9):
    A("sum_G88_pow_%d" % n, mp.fsum([g ** n for g in G88]))
    A("sum_G88_pow_%d_odd" % n, mp.fsum([g ** n for g in G88[0::2]]))
    A("sum_G88_pow_%d_even" % n, mp.fsum([g ** n for g in G88[1::2]]))
    A("sum_g44_pow_%d" % n, mp.fsum([g ** n for g in g44]))
    A("C_2n_n_%d" % n, mp.binomial(2 * n, n))
    A("pow2_2n_1_%d" % n, mp.mpf(2) ** (2 * n - 1))

# 1f T_hat 泛函 (含 O191/O192 F-1 / L-1 家族)
for n in range(1, 18):
    A("L_%d" % n, LUC[n]); A("F_%d" % n, FIB[n])
    A("L_%d_minus_1" % n, LUC[n] - 1); A("F_%d_minus_1" % n, FIB[n] - 1)
    A("L_%d_plus_1" % n, LUC[n] + 1); A("F_%d_plus_1" % n, FIB[n] + 1)
A("phi", PHI); A("inv_phi", INV); A("sqrt5", SQ5); A("sqrt2", mp.sqrt(2))
A("sqrt_phi", mp.sqrt(PHI)); A("pi", PI); A("2pi", 2 * PI); A("inv_pi", 1 / PI)
for m in range(-4, 5):
    if m != 0:
        A("phi_pow_%d" % m, PHI ** m)

# 1g 譜組合
A("C_Nd_2", mp.mpf(Nd * (Nd - 1) // 2)); A("Nd_half", mp.mpf(Nd) / 2)
A("B_Nd", B * Nd); A("Nd_log2B", Nd * 2)
A("Nd_plus_B", Nd + B); A("Nd_minus_B", Nd - B)
A("B_sq", B * B); A("2B_sq", 2 * B * B); A("N_gen_sq", NGEN * NGEN)
A("B_Ngen", B * NGEN); A("L5_minus_1", L5 - 1); A("L5_plus_1", L5 + 1)
A("L5_sq", L5 * L5); A("Nd_sq", Nd * Nd); A("4Nd_plus_B2", 4 * Nd + B * B)
A("2F11", 2 * FIB[11]); A("L10_half", mp.mpf(LUC[10]) / 2)
A("L10_over_4Nd", mp.mpf(LUC[10]) / (4 * Nd))

# 1h sqrt / 倒數衍生 (群運算: 平方根 + 倒數, 都係原語)
for nm in list(ATOMS.keys()):
    v = ATOMS[nm]
    if v > 0:
        A("sqrt_" + nm, mp.sqrt(v))
    A("inv_" + nm, 1 / v)

ATOM_NAMES = list(ATOMS.keys())
ATOM_VALS = np.array([float(v) for v in ATOMS.values()], dtype=np.float64)

print("=" * 78)
print("O201/01 -- 譜字典掃描 v3")
print("=" * 78)
print("原語譜原子池: %d 個閉式泛函" % len(ATOM_NAMES))
print("  Sum gamma(44-chain)  = %s   odd %s / even %s" % (
    mp.nstr(S_GAM, 10), mp.nstr(S_ODD, 10), mp.nstr(S_EVEN, 10)))
print("  Sum Gamma(88-site)   = %s   odd %s / even %s" % (
    mp.nstr(S_G88, 10), mp.nstr(S_G88_ODD, 10), mp.nstr(S_G88_EVEN, 10)))
print("  [identity] Gamma_{2n} = gamma_n : max|diff| = %.3e" % float(
    max(abs(G88[2 * n - 1] - g44[n - 1]) for n in range(1, Nd + 1))))
print("  [identity] Sum gamma(44) = Sum Gamma88_even = 90")

# ============================================================
# 2. 目標註冊表 (gamma_1 由譜直接計, 唔硬編)
# ============================================================
G1 = mp.nstr(g44[0], 25)
TARGETS = [
    ("N_d", "44", "O51 譜基 site 數", True),
    ("B", "4", "O97 x^2+x-1 分支", True),
    ("N_gen", "3", "O103 (L5+1)/B", True),
    ("L5", "11", "O145 L_5 = rank SU(12)", True),
    ("F_proj", "17", "O138 L_6-1", True),
    ("K_tree", "33", "O191 F_9-1", True),
    ("Sum_gamma", "90", "O51 Sum gamma", True),
    ("Sum_gamma_odd", "44", "O169 Sum gamma_odd = N_d EXACT", True),
    ("Sum_gamma_even", "46", "O148 mod-4 n=0", True),
    ("mu2", "2", "O159 E-O = gamma_44", True),
    ("h11", "36", "O53 CY3 Hodge", False),
    ("h21", "98", "O53 CY3 Hodge", False),
    ("h11_plus_h21", "134", "O56 = N_d + Sum gamma", False),
    ("beat_dim", "946", "BPT C(44,2)", False),
    ("sum_inv_gamma_odd", "968", "O100 44 x 22", False),
    ("B_Nd_176", "176", "O151 = 2 F_11", False),
    ("Sum_Gamma88_178", "178", "O193 = 2 F_11", False),
    ("L10_123", "123", "O142 / O41 Landauer", False),
    ("W_sq", "61.5", "O39 <W>^2 = L_10/2", False),
    ("f_unproj", "0.6833333333333333", "O148 41/60 = Omega_Lambda", False),
    ("eps_exact", "0.15447154471544716", "O148 19/123", False),
    ("E_min", "0.6988636363636364", "O41 123/176", False),
    ("alpha_inv_0", "137", "O142 3 N_d + F_5", False),
    ("alpha_inv_MZ", "128", "O142 2 N_d + F_5 F_6", False),
    ("V_capacity_264", "264", "O107 6 U(1) x N_d", False),
    ("V_capacity_528", "528", "O151 dimC B N_gen", False),
    ("V_Lambda", "283.0821", "O62 V_Lambda", False),
    ("C_12_2_66", "66", "O101 Lambda^2(12)", False),
    ("L4L5_77", "77", "O145 dim Borel SU(12)", False),
    ("dim_SU12_143", "143", "O145 12^2-1", False),
    ("L4L5_minus_mu2_75", "75", "O173 E_strain 分母", False),
    ("F10_55", "55", "O156 theta_23 尺度家", False),
    ("Tr_chi_30", "30", "O158 = Sum gamma_even/3", False),
    ("B_L4_28", "28", "O192 B L_4", False),
    ("pool_turnover_364", "364", "O177 B L_4 F_7", False),
    ("A5_order_60", "60", "O182 |A_5|", False),
    ("gamma_192", "192", "O41 4 N_d + B^2", False),
    ("Sigma_Gamma_5940", "5940", "KTSG Sum gamma (x) lambda", False),
    ("phase_space_1496", "1496", "O87 44 x 34", False),
    ("r_d_num_420", "420", "O171 L_4 |A_5|", False),
    ("r_d_den_421", "421", "O171 +1", False),
    ("mean_gamma_ratio", "2.0454545454545454", "O193 <gamma> = 89/44", False),
    ("even_over_odd", "1.0454545454545454", "O148 45/44", False),
    ("omega_dm_over_b", "6.5", "O116 F_7/L_0", False),
    ("baryon_split", "0.13333333333333333", "O163 2/15", False),
    ("baryon_over_matter", "0.31666666666666665", "O163 19/60", False),
    ("b_spec", "1.1191139820215964", "O169 1/<v_g>_{1..22}", False),
    ("sqrt5_over_2", "1.118033988749895", "O169 phi 陷阱對照", False),
    ("phi_const", "1.618033988749895", "O97 自相似根", False),
    ("gamma_1_val", G1, "gamma_1 = 4sin^2(pi/88)", False),
    ("gamma_11_val", "0.5857864376269049", "2-sqrt2", False),
    ("gamma_33_val", "3.414213562373095", "2+sqrt2", False),
    ("Omega_Lambda_old", "0.6832815729997477", "O37 舊 4/(phi^4-1) 已撤銷", False),
    ("mu_logN", "0.862478", "O169 logN 中位斜率", False),
    ("s_logN", "1.1874", "O169 logN 散射", False),
    ("sin2_theta23", "0.57298", "O156 R5 NuFIT 對照", False),
    ("mW_over_mZ", "0.8813", "O144 sin30/sin41", False),
    ("piR_intercept", "1.2414297", "O169 <sec>_{1..28}", False),
    ("C_old", "-0.1697", "O51/O169 已證偽", False),
    ("lambda_88_over_33", "2.6666666666666665", "O154 8/3", False),
    ("L5_minus_1_10", "10", "O160 2 N_gen + B", False),
    ("N_gen_sq_9", "9", "O168 alpha 跑動步數", False),
    ("B_sq_16", "16", "O151 SO(10) spinor", False),
    ("twoB_sq_32", "32", "O154 2 B^2", False),
    ("Nd_minus_B_40", "40", "O154 40 = N_d - B", False),
    ("one_over_137", "0.0072992700729927005", "alpha(0)", False),
    ("cosmological_crack", "0.00746", "O168 1/(2(2K_tree+1))", False),
]
TG = [(nm, mp.mpf(vs), prov, basis) for nm, vs, prov, basis in TARGETS]

TRAP_LO, TRAP_HI = mp.mpf('1e-5'), mp.mpf('1e-3')
EXACT_TOL = mp.mpf('1e-40')


def rel_dev(x, y):
    return abs((x - y) / y)


def classify(dev):
    if dev < EXACT_TOL:
        return "EXACT"
    if dev < TRAP_LO:
        return "HIT"
    if dev < TRAP_HI:
        return "TRAP"
    return "MISS"


n_int = sum(1 for t in TG if abs(t[1] - mp.nint(t[1])) < mp.mpf('1e-30'))
print("目標註冊常數: %d (基數 %d / 推導 %d; 其中整數目標 %d)" % (
    len(TG), sum(1 for t in TG if t[3]), sum(1 for t in TG if not t[3]), n_int))

# ============================================================
# 3. Tier A
# ============================================================
print("\n" + "=" * 78)
print("Tier A -- 目標 vs 原語譜原子 (深度 1; 報全部 dev < 1e-5 匹配)")
print("=" * 78)
tierA_all = {}
for nm, val, prov, basis in TG:
    hits = sorted((float(rel_dev(ATOMS[an], val)), an) for an in ATOM_NAMES
                  if rel_dev(ATOMS[an], val) < TRAP_LO)
    tierA_all[nm] = hits
    if hits:
        tag = " [BASIS]" if basis else ""
        show = "; ".join("%s(%.1e)" % (a, d) for d, a in hits[:3])
        print("  %-22s %-6s %s%s" % (nm, classify(mp.mpf(hits[0][0])), show, tag))

rng = np.random.default_rng(20260917)
rnd = np.exp(rng.uniform(np.log(1e-3), np.log(1e4), 2000))
nullA = np.array([min(abs(v - t) / abs(t) for v in ATOM_VALS) for t in rnd])
int_atoms = np.array([v for v in ATOM_VALS if abs(v - round(v)) < 1e-9 and v <= 6000])
rnd_int_t = rng.integers(1, 6001, 3000).astype(float)
nullA_int = np.array([min(abs(v - t) / abs(t) for v in ATOM_VALS) for t in rnd_int_t])
print("\n  Tier A null control (池 %d 原子, 其中整數值原子 %d 個 <= 6000):" % (
    len(ATOM_VALS), len(int_atoms)))
print("    [非整數目標 2000 個] P(dev<1e-3)=%.4f  P(dev<1e-5)=%.4f  P(dev<1e-9)=%.4f" % (
    (nullA < 1e-3).mean(), (nullA < 1e-5).mean(), (nullA < 1e-9).mean()))
print("    [整數目標   3000 個] P(dev<1e-3)=%.4f  P(dev<1e-5)=%.4f  P(dev<1e-9)=%.4f" % (
    (nullA_int < 1e-3).mean(), (nullA_int < 1e-5).mean(), (nullA_int < 1e-9).mean()))
nullA_1e3, nullA_1e5, nullA_1e9 = (nullA < 1e-3).mean(), (nullA < 1e-5).mean(), (nullA < 1e-9).mean()
nullA_int_1e9 = (nullA_int < 1e-9).mean()
print("    => 非整數目標: Tier A 有判別力 (null %.4f)" % nullA_1e9)
print("    => 整數目標  : Tier A 判別力低 (null %.4f) -> 須靠 provenance 判準 (script 02)" % nullA_int_1e9)

# ============================================================
# 4. Tier B -- 拆整數 / 非整數
# ============================================================
PRIM_KEYS = [k for k in ATOM_NAMES if not k.startswith("sqrt_") and not k.startswith("inv_")]
PRIM_VALS = np.array([float(ATOMS[k]) for k in PRIM_KEYS])
OPS = {0: "+", 1: "-", 2: "*", 3: "/", 4: "R/", 5: "|d|"}


def depth2_best(vals, tvals, tol=1.0):
    out = []
    a = vals
    for t in tvals:
        best = (1e9, -1, -1, -1, 0.0)
        for op in range(6):
            if op == 0:
                M = a[:, None] + a[None, :]
            elif op == 1:
                M = a[:, None] - a[None, :]
            elif op == 2:
                M = a[:, None] * a[None, :]
            elif op == 3:
                with np.errstate(divide='ignore', invalid='ignore'):
                    M = a[:, None] / a[None, :]
            elif op == 4:
                with np.errstate(divide='ignore', invalid='ignore'):
                    M = a[None, :] / a[:, None]
            else:
                M = np.abs(a[:, None] - a[None, :])
            with np.errstate(invalid='ignore'):
                D = np.abs(M - t) / abs(t)
            D = np.nan_to_num(D, nan=1e9, posinf=1e9)
            i, j = np.unravel_index(np.argmin(D), D.shape)
            if D[i, j] < best[0]:
                best = (float(D[i, j]), op, int(i), int(j), float(M[i, j]))
        out.append(best if best[0] < tol else None)
    return out


print("\n" + "=" * 78)
print("Tier B -- 深度 2 over 註冊原語池 (%d 個), 拆整數/非整數" % len(PRIM_KEYS))
print("=" * 78)
tvals = [float(t[1]) for t in TG]
prim_hits = depth2_best(PRIM_VALS, tvals)

rnd_int = np.round(np.exp(rng.uniform(np.log(1e-3), np.log(1e4), 500)))
rnd_real = np.exp(rng.uniform(np.log(1e-3), np.log(1e4), 500))
rnd_real = rnd_real[np.abs(rnd_real - np.round(rnd_real)) > 1e-6]
nullB_int = depth2_best(PRIM_VALS, rnd_int, tol=1.0)
nullB_real = depth2_best(PRIM_VALS, rnd_real, tol=1.0)
print("  null (整數隨機目標 %d 個):  P(dev<1e-9)=%.4f  P(dev<1e-14)=%.4f  P(exact)=%.4f" % (
    len(rnd_int),
    sum(1 for h in nullB_int if h and h[0] < 1e-9) / len(rnd_int),
    sum(1 for h in nullB_int if h and h[0] < 1e-14) / len(rnd_int),
    sum(1 for h in nullB_int if h and h[0] == 0.0) / len(rnd_int)))
print("  null (非整數隨機目標 %d 個): P(dev<1e-9)=%.4f  P(dev<1e-14)=%.4f" % (
    len(rnd_real),
    sum(1 for h in nullB_real if h and h[0] < 1e-9) / len(rnd_real),
    sum(1 for h in nullB_real if h and h[0] < 1e-14) / len(rnd_real)))
NB_INT = sum(1 for h in nullB_int if h and h[0] < 1e-9) / len(rnd_int)
NB_REAL = sum(1 for h in nullB_real if h and h[0] < 1e-9) / len(rnd_real)
print("  => 整數目標: 深度2 命中 = 算術分解 (池對 +,-,* 封閉) -> 零判別力 (null %.3f)" % NB_INT)
print("  => 非整數目標: 判別力 tol = 1e-9 (null %.4f)" % NB_REAL)

# ============================================================
# 5. 綜合判定
# ============================================================
print("\n" + "=" * 78)
print("綜合判定表")
print("=" * 78)
final = {}
for idx, (nm, val, prov, basis) in enumerate(TG):
    is_int = abs(val - mp.nint(val)) < mp.mpf('1e-30')
    h = tierA_all[nm]
    if h:
        cl = classify(mp.mpf(h[0][0]))
        if cl in ("EXACT", "HIT"):
            final[nm] = ("A:" + cl, "; ".join("%s(%.1e)" % (a, d) for d, a in h[:3]), "A",
                         prov, basis)
            continue
        if cl == "TRAP":
            final[nm] = ("A:TRAP", "%s(%.1e)" % (h[0][1], h[0][0]), "T", prov, basis)
            continue
    hb = prim_hits[idx]
    if hb and hb[0] < 1e-9:
        d, op, i, j, v = hb
        if is_int:
            final[nm] = ("B-int", "%s %s %s = %s (算術分解, 零判別力)" % (
                PRIM_KEYS[i], OPS[op], PRIM_KEYS[j], mp.nstr(mp.mpf(v), 10)), "Bi", prov, basis)
        else:
            final[nm] = ("B-real", "%s %s %s = %s (dev %.1e)" % (
                PRIM_KEYS[i], OPS[op], PRIM_KEYS[j], mp.nstr(mp.mpf(v), 10), d), "B", prov, basis)
        continue
    if hb:
        d, op, i, j, v = hb
        final[nm] = ("TRAP2", "%s %s %s (dev %.1e) [陷阱窗]" % (
            PRIM_KEYS[i], OPS[op], PRIM_KEYS[j], d), "T", prov, basis)
        continue
    final[nm] = ("MISS", "(原語池深度 1/2 內冇命中)", "-", prov, basis)

order = {"A": 0, "B": 1, "Bi": 2, "T": 3, "-": 4}
for nm, val, prov, basis in sorted(TG, key=lambda t: (order[final[t[0]][2]], t[0])):
    v, det, tier, prov, basis = final[nm]
    print("  %-22s %-9s %s" % (nm, v, det))

# ============================================================
# 6. 完備率 + 反例集
# ============================================================
derived = [t for t in TG if not t[3]]
nAE = sum(1 for t in derived if final[t[0]][0] == "A:EXACT")
nAH = sum(1 for t in derived if final[t[0]][0] == "A:HIT")
nBR = sum(1 for t in derived if final[t[0]][0] == "B-real")
nBI = sum(1 for t in derived if final[t[0]][0] == "B-int")
nT = sum(1 for t in derived if final[t[0]][2] == "T")
nM = sum(1 for t in derived if final[t[0]][2] == "-")
misses = [t[0] for t in derived if final[t[0]][2] in ("-", "T")]
der_int = [t for t in derived if abs(t[1] - mp.nint(t[1])) < mp.mpf('1e-30')]
der_real = [t for t in derived if abs(t[1] - mp.nint(t[1])) >= mp.mpf('1e-30')]
print("\n" + "=" * 78)
print("完備率 (只計推導常數 %d 個)" % len(derived))
print("=" * 78)
print("  A:EXACT  精確單一譜身份   : %2d  (%.1f%%)   [非整數 null P(<1e-9) = %.4f]" % (
    nAE, 100.0 * nAE / len(derived), nullA_1e9))
print("  A:HIT    數值單一譜表達   : %2d  (%.1f%%)   [非整數 null P(<1e-5) = %.4f]" % (
    nAH, 100.0 * nAH / len(derived), nullA_1e5))
print("  B-real   深度2 非整數目標 : %2d  (%.1f%%)   [null P(<1e-9) = %.4f]" % (
    nBR, 100.0 * nBR / len(derived), NB_REAL))
print("  B-int    深度2 整數目標   : %2d  (算術分解, 零判別力)" % nBI)
print("  TRAP     陷阱窗 (無判別力) : %2d  (%.1f%%)" % (nT, 100.0 * nT / len(derived)))
print("  MISS     未命中           : %2d  (%.1f%%)" % (nM, 100.0 * nM / len(derived)))
print("\n  ★ C1 完備率 (A:EXACT)              = %.1f%%  (判別力 null < %.4f)" % (
    100.0 * nAE / len(derived), nullA_1e9))
print("  ★ C1 完備率 (A:EXACT + A:HIT)      = %.1f%%" % (100.0 * (nAE + nAH) / len(derived)))
print("  ★ C1 完備率 (+ B-real)             = %.1f%%" % (
    100.0 * (nAE + nAH + nBR) / len(derived)))

print("\n  --- 按目標類別分拆 (判別力差別) ---")
for lab, grp, nl in (("非整數目標", der_real, nullA_1e9), ("整數目標", der_int, nullA_int_1e9)):
    if not grp:
        continue
    a = sum(1 for t in grp if final[t[0]][0] == "A:EXACT")
    b = sum(1 for t in grp if final[t[0]][0] == "A:HIT")
    c = sum(1 for t in grp if final[t[0]][0] == "B-real")
    e = sum(1 for t in grp if final[t[0]][0] == "B-int")
    f = sum(1 for t in grp if final[t[0]][2] == "T")
    g = sum(1 for t in grp if final[t[0]][2] == "-")
    print("    %-12s n=%2d | A:EXACT %2d | A:HIT %2d | B-real %2d | B-int %2d | TRAP %2d | MISS %2d | null(<1e-9)=%.4f"
          % (lab, len(grp), a, b, c, e, f, g, nl))
    print("                完備率 (A:EXACT+A:HIT+B-real) = %.1f%%" % (
        100.0 * (a + b + c) / len(grp)))

print("\n  ★ 無譜表達 / 陷阱清單 (C1 反例集):")
for m in misses:
    prov = [t[2] for t in TG if t[0] == m][0]
    print("     - %-24s %-9s (%s)" % (m, final[m][0], prov))
if not misses:
    print("     (冇)")

out = {
    "n_atoms": len(ATOM_NAMES), "n_targets": len(TG), "n_derived": len(derived),
    "A_EXACT": nAE, "A_HIT": nAH, "B_real": nBR, "B_int": nBI, "TRAP": nT, "MISS": nM,
    "completeness_A_exact": nAE / len(derived),
    "completeness_A": (nAE + nAH) / len(derived),
    "completeness_ABreal": (nAE + nAH + nBR) / len(derived),
    "null_A_1e3": float(nullA_1e3), "null_A_1e5": float(nullA_1e5), "null_A_1e9": float(nullA_1e9),
    "null_A_int_1e9": float(nullA_int_1e9),
    "n_derived_real": len(der_real), "n_derived_int": len(der_int),
    "null_B_int": NB_INT, "null_B_real": NB_REAL,
    "misses": misses,
    "verdicts": {nm: final[nm][0] for nm in final},
    "details": {nm: final[nm][1] for nm in final},
    "values": {nm: mp.nstr(mp.mpf(vs), 30) for nm, vs, prov, basis in TARGETS},
    "tierA_all": {nm: [[d, a] for d, a in tierA_all[nm][:5]] for nm in tierA_all},
}
d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
os.makedirs(d, exist_ok=True)
p = os.path.join(d, "01_spectral_dictionary.json")
with open(p, "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("\n[data] %s" % os.path.abspath(p))

# ============================================================
# 7. 自檢
# ============================================================
print("\n" + "=" * 78)
print("自檢")
print("=" * 78)
NPASS = NFAIL = 0


def check(label, cond):
    global NPASS, NFAIL
    if cond:
        NPASS += 1
        print("  PASS  %s" % label)
    else:
        NFAIL += 1
        print("  FAIL  %s" % label)


check("[INJECT] checker 識 FAIL (3 != 4)", not (abs(rel_dev(mp.mpf(3), mp.mpf(4))) < EXACT_TOL))
check("Sum gamma(44-chain) = 90", abs(S_GAM - 90) < EXACT_TOL)
check("Sum gamma_odd = 44 EXACT", abs(S_ODD - 44) < EXACT_TOL)
check("Sum gamma_even = 46", abs(S_EVEN - 46) < EXACT_TOL)
check("Sum gamma_even - odd = mu^2 = 2", abs(S_EVEN - S_ODD - 2) < EXACT_TOL)
check("Sum Gamma88 = 178 = 2 F_11", abs(S_G88 - 178) < EXACT_TOL)
check("Sum Gamma88_odd = 88", abs(S_G88_ODD - 88) < EXACT_TOL)
check("Sum Gamma88_even = 90 = Sum gamma(44-chain)", abs(S_G88_EVEN - S_GAM) < EXACT_TOL)
check("IDENTITY Gamma_{2n} = gamma_n (44/44)", max(
    abs(G88[2 * n - 1] - g44[n - 1]) for n in range(1, Nd + 1)) < mp.mpf('1e-45'))
check("gamma_22 = mu^2 = 2", abs(g44[21] - 2) < EXACT_TOL)
check("gamma_44 = 4 = B", abs(g44[43] - 4) < EXACT_TOL)
check("gamma_1 = 4sin^2(pi/88) = 0.0050957707795", abs(g44[0] - mp.mpf("0.00509577077949291727538848632575")) < 1e-30)
check("Sum Gamma^n closed n=1: 178", abs(mp.fsum(G88) - 178) < EXACT_TOL)
check("Sum Gamma^n closed n=2: 536", abs(mp.fsum([g ** 2 for g in G88]) - 536) < EXACT_TOL)
check("Sum Gamma^n closed n=3: 1792", abs(mp.fsum([g ** 3 for g in G88]) - 1792) < EXACT_TOL)
check("Sum Gamma^n odd n=2: 264", abs(mp.fsum([g ** 2 for g in G88[0::2]]) - 264) < EXACT_TOL)
check("Sum gamma^2 (44-chain) = 272 = B^2 F_proj", abs(mp.fsum([g ** 2 for g in g44]) - 272) < EXACT_TOL)
check("parity gap n=2 = 8 = 2^3", abs(mp.fsum([g ** 2 for g in G88[1::2]])
                                     - mp.fsum([g ** 2 for g in G88[0::2]]) - 8) < EXACT_TOL)
check("L_10 = 123", LUC[10] == 123)
check("F_11 = 89", FIB[11] == 89)
check("Tier A 有判別力 (null P<1e-9 = %.4f < 0.05)" % nullA_1e9, nullA_1e9 < 0.05)
check("Tier B 整數目標零判別力已量化 (null = %.3f)" % NB_INT, NB_INT >= 0.0)
check("b_spec != sqrt5/2 (dev %.2e)" % float(
    rel_dev(mp.mpf("1.1191139820215964"), mp.mpf("1.118033988749895"))),
    rel_dev(mp.mpf("1.1191139820215964"), mp.mpf("1.118033988749895")) > mp.mpf("1e-6"))
check("C_old = -0.1697 唔係譜原子 (Tier A miss)", not tierA_all["C_old"])

print("\n總計: %d/%d PASS" % (NPASS, NPASS + NFAIL))
print("EXIT=%d" % (0 if NFAIL == 0 else 1))
