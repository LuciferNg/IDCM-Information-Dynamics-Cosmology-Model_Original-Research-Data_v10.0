#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O201 scripts/o201_basis.py -- 共用譜基模組 (唔係 numbered script, 係 library)

提供: 譜基計算 + 原語譜原子池 + 深度 1/2 搜索 + null control。
scripts 03+ 全部 import 呢個模組, 避免重複實作 (v1 教訓: 每個 script 自帶池會漂移)。

零新常數: 只用 gamma_n = 4sin^2(pi n/88), Gamma_k = 4sin^2(k pi/176),
          T_hat = [[1,1],[1,0]] (L_n, F_n), v_g = cos(pi n/88), sec, 結構數。
"""
import mpmath as mp

mp.mp.dps = 50
PI = mp.pi
PHI = (1 + mp.sqrt(5)) / 2
INV_PHI = 1 / PHI

Nd, B, NGEN, L5, FPROJ, KTREE = 44, 4, 3, 11, 17, 33

g44 = [4 * mp.sin(n * PI / 88) ** 2 for n in range(1, Nd + 1)]
G88 = [4 * mp.sin(k * PI / 176) ** 2 for k in range(1, 89)]
VG = [mp.cos(n * PI / 88) for n in range(1, Nd + 1)]
SEC = [1 / mp.cos(n * PI / 88) for n in range(1, Nd + 1)]

S_GAM = mp.fsum(g44)
S_ODD = mp.fsum(g44[0::2])
S_EVEN = mp.fsum(g44[1::2])
S_G88 = mp.fsum(G88)
S_G88_ODD = mp.fsum(G88[0::2])
S_G88_EVEN = mp.fsum(G88[1::2])

TH = mp.matrix([[1, 1], [1, 0]])
_THP = {0: mp.eye(2), 1: TH}
for _n in range(2, 20):
    _THP[_n] = _THP[_n - 1] * TH
LUC = [int(round(_THP[n][0, 0] + _THP[n][1, 1])) for n in range(20)]
FIB = [int(round(_THP[n][0, 1])) for n in range(20)]


def build_atoms(with_derived=True):
    """原語譜原子池 (with_derived=True 加 sqrt/inv 衍生)"""
    A = {}

    def add(name, val):
        if name in A:
            return
        try:
            v = mp.mpf(val)
        except Exception:
            return
        if v == 0 or not mp.isfinite(v):
            return
        A[name] = v

    add("N_d", Nd); add("B", B); add("N_gen", NGEN); add("L5", L5)
    add("F_proj", FPROJ); add("K_tree", KTREE); add("mu2", 2); add("gamma_44", 4)
    add("Sum_gamma", S_GAM); add("Sum_gamma_odd", S_ODD); add("Sum_gamma_even", S_EVEN)
    add("Sum_Gamma88", S_G88); add("Sum_Gamma88_odd", S_G88_ODD); add("Sum_Gamma88_even", S_G88_EVEN)
    add("ratio_even_odd", S_EVEN / S_ODD)
    add("mean_gamma", S_GAM / Nd); add("mean_gamma_odd", S_ODD / 22); add("mean_gamma_even", S_EVEN / 22)

    for n in range(1, Nd + 1):
        add("gamma_%d" % n, g44[n - 1])
    for k in range(1, 89):
        add("Gamma_%d" % k, G88[k - 1])
    for n in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 17, 18, 20, 21, 22, 24,
              28, 32, 33, 34, 36, 40, 41, 43, 44):
        add("v_g_%d" % n, VG[n - 1]); add("sec_%d" % n, SEC[n - 1])
        add("cos_%d" % n, mp.cos(n * PI / 88)); add("sin_%d" % n, mp.sin(n * PI / 88))
        add("tan_%d" % n, mp.tan(n * PI / 88))

    for K in range(1, Nd + 1):
        add("mean_sec_1_%d" % K, mp.fsum(SEC[:K]) / K)
        add("inv_mean_vg_1_%d" % K, 1 / (mp.fsum(VG[:K]) / K))
        add("sum_gamma_1_%d" % K, mp.fsum(g44[:K]))
    for K in range(1, 89):
        add("sum_Gamma88_1_%d" % K, mp.fsum(G88[:K]))
    for K in range(1, 45):
        add("sum_gamma_odd_1_%d" % K, mp.fsum(g44[0:2 * K:2]))
        add("sum_gamma_even_1_%d" % K, mp.fsum(g44[1:2 * K:2]))

    for r in range(4):
        add("sum_gamma_mod4_%d" % r, mp.fsum([g44[n - 1] for n in range(1, Nd + 1) if n % 4 == r]))
        add("sum_Gamma88_mod4_%d" % r, mp.fsum([G88[k - 1] for k in range(1, 89) if k % 4 == r]))
        add("count_mod4_%d" % r, mp.mpf(len([n for n in range(1, Nd + 1) if n % 4 == r])))

    for n in range(1, 9):
        add("sum_G88_pow_%d" % n, mp.fsum([g ** n for g in G88]))
        add("sum_G88_pow_%d_odd" % n, mp.fsum([g ** n for g in G88[0::2]]))
        add("sum_G88_pow_%d_even" % n, mp.fsum([g ** n for g in G88[1::2]]))
        add("sum_g44_pow_%d" % n, mp.fsum([g ** n for g in g44]))
        add("C_2n_n_%d" % n, mp.binomial(2 * n, n))
        add("pow2_2n_1_%d" % n, mp.mpf(2) ** (2 * n - 1))

    for n in range(1, 18):
        add("L_%d" % n, LUC[n]); add("F_%d" % n, FIB[n])
        add("L_%d_minus_1" % n, LUC[n] - 1); add("F_%d_minus_1" % n, FIB[n] - 1)
        add("L_%d_plus_1" % n, LUC[n] + 1); add("F_%d_plus_1" % n, FIB[n] + 1)
    add("phi", PHI); add("inv_phi", INV_PHI); add("sqrt5", mp.sqrt(5)); add("sqrt2", mp.sqrt(2))
    add("sqrt_phi", mp.sqrt(PHI)); add("pi", PI); add("2pi", 2 * PI); add("inv_pi", 1 / PI)
    for m in range(-4, 5):
        if m != 0:
            add("phi_pow_%d" % m, PHI ** m)

    add("C_Nd_2", mp.mpf(Nd * (Nd - 1) // 2)); add("Nd_half", mp.mpf(Nd) / 2)
    add("B_Nd", B * Nd); add("Nd_log2B", Nd * 2)
    add("Nd_plus_B", Nd + B); add("Nd_minus_B", Nd - B)
    add("B_sq", B * B); add("2B_sq", 2 * B * B); add("N_gen_sq", NGEN * NGEN)
    add("B_Ngen", B * NGEN); add("L5_minus_1", L5 - 1); add("L5_plus_1", L5 + 1)
    add("L5_sq", L5 * L5); add("Nd_sq", Nd * Nd); add("4Nd_plus_B2", 4 * Nd + B * B)
    add("2F11", 2 * FIB[11]); add("L10_half", mp.mpf(LUC[10]) / 2)
    add("L10_over_4Nd", mp.mpf(LUC[10]) / (4 * Nd))
    add("A5_order", mp.mpf(60)); add("Tr_chi", mp.mpf(30))
    add("3Nd_plus_F5", 3 * Nd + FIB[5]); add("2Nd_plus_F5F6", 2 * Nd + FIB[5] * FIB[6])

    if with_derived:
        for nm in list(A.keys()):
            v = A[nm]
            if v > 0:
                add("sqrt_" + nm, mp.sqrt(v))
            add("inv_" + nm, 1 / v)
    return A


def dev(x, y):
    return abs((x - y) / y)


def classify(d, trap_lo=mp.mpf('1e-5'), trap_hi=mp.mpf('1e-3'), exact=mp.mpf('1e-40')):
    if d < exact:
        return "EXACT"
    if d < trap_lo:
        return "HIT"
    if d < trap_hi:
        return "TRAP"
    return "MISS"


def search_depth1(atoms, target, tol=mp.mpf('1e-3')):
    hits = sorted((float(dev(v, target)), k) for k, v in atoms.items() if dev(v, target) < tol)
    return hits


def depth2_best(vals, tvals, tol=1.0):
    """vals: numpy float array; 回傳每目標最佳 (dev, op, i, j, value)"""
    import numpy as np
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
