#!/usr/bin/env python3
"""
O56 - Phase 2: 獨立重算 verifier (mpmath dps=60)
=================================================
獨立性保證:
  - 不 import 任何 O56 推導腳本 (01/02/03/final_verification)
  - 所有常數由 x^2+x-1=0 第一性原理重算 (mpmath 高精度)
  - 不讀取推導輸出做為輸入 (只在 Section I 做交叉比對)
  - KS 數據直接由 o53 alltoric.spec 重讀

覆蓋:
  A 基本常數 (phi, B, L5, L6, F6)
  B K_Chain 譜 (Sigma_gamma 精確封閉形式)
  C Z2 對偶
  D Lucas 代數 (Nd, Sigma_gamma, Lucas 遞歸定理)
  E h11/h21 三方法 + chi
  F M_{36x44} 投影矩陣 (獨立建構, mpmath 基底)
  G N_gen 強制鎖定 + 虛無測試
  H KS 數據 B 變體虛無測試 (獨立讀檔)
  I 數據檔交叉比對
"""
import math
import json
import os
import sys

from mpmath import mp, mpf, sin, sqrt, pi, nstr

mp.dps = 60

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)                      # o56_kchain_moduli_lock
OPS = os.path.dirname(ROOT)                       # open_problems_fresh
KS = os.path.join(OPS, 'o53_cy3_reality', 'data', 'alltoric.spec')

passed = 0
failed = 0
def chk(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  OK   {name} {detail}")
    else:
        failed += 1
        print(f"  FAIL {name} {detail}")

print("=" * 74)
print("O56 Phase 2: 獨立重算 verifier (mpmath dps=60)")
print("=" * 74)

# ============================================================
# A. 基本常數 - 由 x^2+x-1=0 第一性原理
# ============================================================
print("\n" + "=" * 74)
print("[A] 基本常數 (x^2+x-1=0 -> phi)")
print("=" * 74)

# 解 x^2+x-1=0 的根 (不用預設 phi)
#   x^2+x-1=0 的根 = (sqrt(5)-1)/2 = 1/phi  (正根) 及 -(1+sqrt(5))/2 = -phi (負根)
#   故 phi = 1/(正根) ; 亦等價於 x^2-x-1=0 的正根
disc = sqrt(mpf(5))
r_pos = (disc - 1) / 2        # = 1/phi = 0.618...
r_neg = -(disc + 1) / 2       # = -phi = -1.618...
res_pos = r_pos**2 + r_pos - 1
res_neg = r_neg**2 + r_neg - 1
print(f"  x^2+x-1=0 正根 = {nstr(r_pos, 25)}  residual = {nstr(res_pos, 5)}")
print(f"  x^2+x-1=0 負根 = {nstr(r_neg, 25)}  residual = {nstr(res_neg, 5)}")
chk("A1 兩根殘差 ~ 0", abs(res_pos) < mpf(10)**-55 and abs(res_neg) < mpf(10)**-55)

phi = 1 / r_pos               # = 1.618...
psi = -1 / phi                # = -0.618...  (= r_pos 的負)
chk("A1b phi = 1/正根 = 1.618...", abs(phi - (1 + disc) / 2) < mpf(10)**-55)
chk("A1c phi 滿足 phi^2 = phi+1", abs(phi**2 - phi - 1) < mpf(10)**-55)
chk("A1d 負根 = -phi", abs(r_neg + phi) < mpf(10)**-55)

# Binet: L_n = phi^n + (-phi)^-n = phi^n + psi^n  (n 偶時 psi^n 正, 奇時負)
def lucas(n):
    return phi**n + psi**n

def fib(n):
    return (phi**n - psi**n) / disc

B_exact = phi**3 - phi**-3
L5_exact = lucas(5)
L6_exact = lucas(6)
L3_exact = lucas(3)
L4_exact = lucas(4)
F6_exact = fib(6)

print(f"\n  B  = phi^3 - phi^-3 = {nstr(B_exact, 30)}")
print(f"  L3 = {nstr(L3_exact, 30)}")
print(f"  L4 = {nstr(L4_exact, 30)}")
print(f"  L5 = {nstr(L5_exact, 30)}")
print(f"  L6 = {nstr(L6_exact, 30)}")
print(f"  F6 = {nstr(F6_exact, 30)}")

chk("A2 B = 4 (exact)", abs(B_exact - 4) < mpf(10)**-55)
chk("A3 L5 = 11 (exact)", abs(L5_exact - 11) < mpf(10)**-55)
chk("A4 L6 = 18 (exact)", abs(L6_exact - 18) < mpf(10)**-55)
chk("A5 F6 = 8 (exact)", abs(F6_exact - 8) < mpf(10)**-55)
chk("A6 B = L3 (身份)", abs(B_exact - L3_exact) < mpf(10)**-55, "=> B = L3 = 4")

B = 4
L3 = 4
L4 = 7
L5 = 11
L6 = 18
F6 = 8

# ============================================================
# B. K_Chain 譜
# ============================================================
print("\n" + "=" * 74)
print("[B] K_Chain 44-site 譜 (Sigma_gamma 精確封閉形式)")
print("=" * 74)

N_dual = 88
Nd = 44

# 高精度直接求和
Sg = mpf(0)
for n in range(1, Nd + 1):
    Sg += 4 * sin(pi * n / N_dual)**2
print(f"  Sigma_gamma (mpmath dps=60 直接求和) = {nstr(Sg, 30)}")
chk("B1 Sigma_gamma = 90", abs(Sg - 90) < mpf(10)**-55, f"({nstr(Sg, 20)})")

# 精確封閉形式推導:
#   sum_{n=1}^{N-1} sin^2(pi n / N) = N/2   (標準三角恆等式)
#   N = 88: sum_{n=1}^{87} = 44
#   對稱 sin^2(pi n/88) = sin^2(pi(88-n)/88)
#   => 2 * sum_{n=1}^{43} + sin^2(pi*44/88) = 44
#   sin^2(pi/2) = 1  =>  sum_{n=1}^{43} = 43/2
#   sum_{n=1}^{44} = 43/2 + 1 = 45/2
#   Sigma_gamma = 4 * 45/2 = 90  EXACT
s_1_87 = sum(sin(pi * n / N_dual)**2 for n in range(1, N_dual))
s_1_43 = sum(sin(pi * n / N_dual)**2 for n in range(1, 44))
print(f"\n  封閉形式檢查:")
print(f"    sum_(n=1..87) sin^2 = {nstr(s_1_87, 25)}  (期望 88/2 = 44)")
print(f"    sum_(n=1..43) sin^2 = {nstr(s_1_43, 25)}  (期望 43/2 = 21.5)")
chk("B2 sum_(1..87) = 44", abs(s_1_87 - 44) < mpf(10)**-55)
chk("B3 sum_(1..43) = 43/2", abs(s_1_43 - mpf(43)/2) < mpf(10)**-55)
chk("B4 sum_(1..44) = 45/2", abs(s_1_43 + 1 - mpf(45)/2) < mpf(10)**-55)
chk("B5 Sigma_gamma = 4*45/2 = 90 EXACT", 4 * mpf(45)/2 == 90)

# 88-site 全譜
Sg88 = sum(4 * sin(pi * n / N_dual)**2 for n in range(1, N_dual + 1))
print(f"  88-site 全譜 Sigma = {nstr(Sg88, 25)}")
chk("B6 88-site Sigma = 176", abs(Sg88 - 176) < mpf(10)**-55)

# ============================================================
# C. Z2 對偶
# ============================================================
print("\n" + "=" * 74)
print("[C] Z2 對偶 gamma_n + gamma_(44-n) = 4")
print("=" * 74)

z2_ok = 0
max_dev = mpf(0)
for n in range(1, 23):
    gn = 4 * sin(pi * n / N_dual)**2
    gd = 4 * sin(pi * (44 - n) / N_dual)**2
    dev = abs(gn + gd - 4)
    max_dev = max(max_dev, dev)
    if dev < mpf(10)**-55:
        z2_ok += 1
print(f"  Z2 對偶對數: {z2_ok}/22, max dev = {nstr(max_dev, 5)}")
chk("C1 Z2 對偶 22/22", z2_ok == 22, f"(max dev {nstr(max_dev,3)})")

# ============================================================
# D. Lucas 代數
# ============================================================
print("\n" + "=" * 74)
print("[D] Lucas 代數 (Nd, Sigma_gamma, Lucas 遞歸定理)")
print("=" * 74)

Nd_calc = B * L5
Sg_calc = 5 * L6
print(f"  Nd = B*L5 = {B}*{L5} = {Nd_calc}")
print(f"  Sigma_gamma = 5*L6 = 5*{L6} = {Sg_calc}")
chk("D1 Nd = B*L5 = 44", Nd_calc == 44)
chk("D2 Sigma_gamma = 5*L6 = 90", Sg_calc == 90)

# ★ 新驗證: 5L6 + 2B = B*L5 + 3L6 係 Lucas 遞歸定理
lhs = 5 * L6 + 2 * B
rhs = B * L5 + 3 * L6
print(f"\n  Lucas identity: 5L6+2B = {lhs} ; B*L5+3L6 = {rhs}")
chk("D3 5L6+2B = B*L5+3L6", lhs == rhs, f"({lhs} = {rhs})")

# 代數歸約: 2L6 = B(L5-2) ; B = L3 ; L6 = L5+L4
#   => 2(L5+L4) = L3*L5 - 2L3
#   => L5(L3-2) = 2(L3+L4)
#   => L5 = 2(L3+L4)/(L3-2) ; L3=4 => = (L3+L4) = 11
red_lhs = 2 * (L5 + L4)
red_rhs = L3 * L5 - 2 * L3
print(f"  歸約 (用 L6 = L5+L4, B = L3):")
print(f"    2(L5+L4) = {red_lhs} ; L3*L5 - 2*L3 = {red_rhs}")
chk("D4 歸約式成立", red_lhs == red_rhs, f"({red_lhs} = {red_rhs})")
chk("D5 歸約等價於 Lucas 遞歸 L5 = L4+L3",
    L5 == L4 + L3, f"({L5} = {L4}+{L3})")
# 一般形式驗證 (L3 = 4 時分母 L3-2 = 2, 故 L5 = L3+L4)
chk("D6 L5 = 2(L3+L4)/(L3-2) 代入", 2 * (L3 + L4) // (L3 - 2) == L5)

# 能量守恆: 2L6 + 3L6 = 5L6
chk("D7 2L6 + 3L6 = 5L6", 2 * L6 + 3 * L6 == 5 * L6)

# ============================================================
# E. h11/h21 三方法
# ============================================================
print("\n" + "=" * 74)
print("[E] h11/h21 三方法 + chi")
print("=" * 74)

h11_A = Nd - 2 * B
h21_A = 90 + 2 * B
h11_B = 2 * L6
h21_B = B * L5 + 3 * L6
S = Nd + 90
D = Nd + L6
h11_C = (S - D) // 2
h21_C = (S + D) // 2
chi = 2 * (h11_A - h21_A)

print(f"  A 分支耦合:   h11 = Nd-2B = {h11_A}, h21 = Sigma+2B = {h21_A}")
print(f"  B Lucas 分解: h11 = 2L6 = {h11_B}, h21 = B*L5+3L6 = {h21_B}")
print(f"  C 結構約束:   h11 = (134-62)/2 = {h11_C}, h21 = (134+62)/2 = {h21_C}")
print(f"  chi = 2(h11-h21) = {chi}")

chk("E1 方法A: (36,98)", h11_A == 36 and h21_A == 98)
chk("E2 方法B: (36,98)", h11_B == 36 and h21_B == 98)
chk("E3 方法C: (36,98)", h11_C == 36 and h21_C == 98)
chk("E4 三方法一致", h11_A == h11_B == h11_C and h21_A == h21_B == h21_C)
chk("E5 chi = -124", chi == -124)
chk("E6 h11+h21 = 134", h11_A + h21_A == 134)
chk("E7 h21-h11 = 62", h21_A - h11_A == 62)
chk("E8 h11 = 3x12", h11_A == 3 * 12)
chk("E9 12 = (Nd-2B)/3", (Nd - 2 * B) // 3 == 12)
chk("E10 Sigma_gamma + 4B = 2Nd + L6", 90 + 4 * B == 2 * Nd + L6,
    f"({90+4*B} = {2*Nd+L6})")

# ============================================================
# F. M_{36x44} 投影矩陣 (獨立建構)
# ============================================================
print("\n" + "=" * 74)
print("[F] M_{36x44} 投影矩陣 (mpmath 基底獨立建構)")
print("=" * 74)

import numpy as np

# 獨立建構: psi_n(j) = sin(pi*n*(2j-1)/88), n=1..44, j=1..44
# 用 mpmath 高精度算, 再轉 float64 做線性代數
U = np.zeros((Nd, Nd), dtype=float)
for j in range(Nd):
    for n in range(Nd):
        U[j, n] = float(sin(pi * (n + 1) * (2 * (j + 1) - 1) / N_dual))

# 正交性檢查 (mpmath 高精度直接算 Gram 矩陣)
#   DST 恆等式: sum_{j=1}^{N} sin^2(pi*n*(2j-1)/(2N)) = N/2  for n = 1..N-1
#                                                      = N    for n = N
#   本處 2N = 88 => N = 44: 對角 = 22 (n=1..43), 44 (n=44)
max_off = mpf(0)
diag_wrong = 0
diag_profile = []
for n in range(Nd):
    for m in range(Nd):
        s = mpf(0)
        for j in range(Nd):
            s += sin(pi * (n + 1) * (2 * (j + 1) - 1) / N_dual) * \
                 sin(pi * (m + 1) * (2 * (j + 1) - 1) / N_dual)
        if n == m:
            diag_profile.append(s)
        else:
            max_off = max(max_off, abs(s))
exp_diag = mpf(Nd) / 2 if (n + 1) < Nd else mpf(Nd)
for n in range(Nd):
    exp_diag = mpf(Nd) / 2 if (n + 1) < Nd else mpf(Nd)
    if abs(diag_profile[n] - exp_diag) > mpf(10)**-55:
        diag_wrong += 1
print(f"  Gram off-diagonal max (mpmath) = {nstr(max_off, 5)}")
print(f"  對角剖面: n=1..43 -> {nstr(diag_profile[0], 10)}, "
      f"n=44 -> {nstr(diag_profile[43], 10)}")
print(f"  對角偏離 DST 恆等式嘅個數 = {diag_wrong}")
chk("F1 基底正交 (off-diag = 0)", max_off < mpf(10)**-55)
chk("F2 對角 = N/2 (n<44) / N (n=44)", diag_wrong == 0,
    f"(43x22 + 1x44, DST 恆等式)")

# 正規化
U_n = U / np.linalg.norm(U, axis=0)

# 按 eigenvalue 排序
gam = np.array([4 * float(sin(pi * (n + 1) / N_dual))**2 for n in range(Nd)])
order = np.argsort(gam)
act = order[:36]
nul = order[36:]

M = U_n[:, act].T          # 36 x 44
rank_M = np.linalg.matrix_rank(M)
s_vals = np.linalg.svd(M, compute_uv=False)
nullity = int(np.sum(s_vals > 1e-10))
proj = M @ U_n[:, nul]
proj_norm = float(np.linalg.norm(proj))
MM = M @ M.T
mm_dev = float(np.abs(MM - np.eye(36)).max())

print(f"\n  M shape = {M.shape}")
print(f"  rank(M) = {rank_M}")
print(f"  nonzero singular values = {nullity}")
print(f"  ||M . nullspace|| = {proj_norm:.3e}")
print(f"  ||M.M^T - I36||   = {mm_dev:.3e}")

chk("F3 M shape 36x44", M.shape == (36, 44))
chk("F4 rank(M) = 36", rank_M == 36)
chk("F5 非零奇異值數 = 36", nullity == 36)
chk("F6 nullity = 44-36 = 8 = 2B", M.shape[1] - rank_M == 8 and 8 == 2 * B)
chk("F7 M . nullspace = 0", proj_norm < 1e-12, f"({proj_norm:.2e})")
chk("F8 M.M^T = I36", mm_dev < 1e-12, f"({mm_dev:.2e})")
chk("F9 active modes = n=1..36", list(act + 1) == list(range(1, 37)))
chk("F10 null modes = n=37..44", list(nul + 1) == list(range(37, 45)))

# 3x12 block 正交
blk_ok = True
for g1 in range(3):
    for g2 in range(g1 + 1, 3):
        B1 = U_n[:, act[g1*12:(g1+1)*12]].T
        B2 = U_n[:, act[g2*12:(g2+1)*12]].T
        if float(np.linalg.norm(B1 @ B2.T)) > 1e-12:
            blk_ok = False
chk("F11 3x12 blocks 兩兩正交", blk_ok)

# nullspace 能量分佈 (診斷, 唔計 pass/fail)
print("\n  [診斷] null modes gamma 範圍: "
      f"{gam[nul].min():.4f} ~ {gam[nul].max():.4f}")
print(f"  [診斷] active modes gamma 範圍: {gam[act].min():.4f} ~ {gam[act].max():.4f}")

# ============================================================
# G. N_gen 強制鎖定
# ============================================================
print("\n" + "=" * 74)
print("[G] N_gen 強制鎖定 + 虛無測試")
print("=" * 74)

# h11 = N*12, h21 = B*L5 + N*L6, h21-h11 = Nd+L6
sols = []
for N in range(1, 9):
    h11t = N * 12
    h21t = B * L5 + N * L6
    if h21t - h11t == Nd + L6:
        sols.append(N)
    print(f"    N_gen={N}: h11={h11t}, h21={h21t}, diff={h21t-h11t} "
          f"(期望 {Nd+L6}) {'MATCH' if h21t-h11t == Nd+L6 else ''}")

chk("G1 唯一解 N_gen = 3", sols == [3], f"(sols={sols})")
chk("G2 N_gen=3 from h11/12", h11_A // 12 == 3)
chk("G3 N_gen=3 from h21", (h21_A - B * L5) // L6 == 3)
chk("G4 解析式 N_gen = (62-44)/6 = 3", (62 - 44) // 6 == 3)

# ============================================================
# H. KS 數據判別力分析 (獨立讀檔) — 取代原本 B 變體「存在性」虛無測試
# ============================================================
print("\n" + "=" * 74)
print("[H] KS 數據判別力分析 (獨立讀 alltoric.spec)")
print("=" * 74)
print("""
  背景: 原 docs/01 §4.2 聲稱「B=3 -> (38,96) 不存在 / B=5 -> (34,100) 不存在,
  只有 B=4 對應嘅 (36,98) 存在」。本節獨立核實此聲稱。
""")

if os.path.exists(KS):
    pairs = []
    with open(KS) as f:
        for line in f:
            p = line.split()
            if len(p) >= 3:
                try:
                    pairs.append((int(p[0]), int(p[1]), int(p[2])))
                except ValueError:
                    pass
    print(f"  KS pair 總數 = {len(pairs)}")
    arr = np.array(pairs)

    m_exact = (arr[:, 0] + arr[:, 1] == 134) & (arr[:, 1] - arr[:, 0] == 62)
    print(f"  h11+h21=134 & h21-h11=62 嘅 pair 數 = {int(m_exact.sum())}")
    for b in arr[m_exact]:
        print(f"    ({b[0]}, {b[1]}) chi={b[2]}")
    chk("H1 KS 唯一解 = (36,98)", int(m_exact.sum()) == 1 and
        tuple(arr[m_exact][0][:2]) == (36, 98))

    # H2: B 變體 pair 嘅存在性 (原聲稱嘅核實)
    variant_hits = {}
    for Bv, hv11, hv21 in [(3, 38, 96), (4, 36, 98), (5, 34, 100)]:
        hit = int(np.sum((arr[:, 0] == hv11) & (arr[:, 1] == hv21)))
        variant_hits[Bv] = hit
        print(f"    B={Bv} -> ({hv11},{hv21}) 喺 KS 出現 {hit} 次 "
              f"(sum={hv11+hv21}, diff={hv21-hv11})")
    chk("H2 B=4 -> (36,98) 存在", variant_hits[4] >= 1)
    # ★ 原聲稱被證偽: B=3 / B=5 變體同樣存在
    chk("H3 ★原聲稱證偽: B=3 -> (38,96) 實際存在", variant_hits[3] >= 1,
        f"(hit={variant_hits[3]}) => 原「不存在」聲稱 FALSE")
    chk("H4 ★原聲稱證偽: B=5 -> (34,100) 實際存在", variant_hits[5] >= 1,
        f"(hit={variant_hits[5]}) => 原「不存在」聲稱 FALSE")

    # H5: sum 約束係 B-獨立 (2B 相消) -> 無判別力
    sum_only = int(np.sum(arr[:, 0] + arr[:, 1] == 134))
    print(f"\n  判別力分解:")
    print(f"    sum=134 單獨: {sum_only} 個 pair (B 無關, 因 2B 相消)")
    print(f"    sum=134 & diff=62: {int(m_exact.sum())} 個 pair (唯一)")
    print(f"    => 判別力完全來自 diff 約束 (即 2B 耦合)")
    chk("H5 sum=134 非唯一 (無判別力)", sum_only > 1, f"({sum_only} 個)")
    chk("H6 sum+diff 聯合唯一", int(m_exact.sum()) == 1)

    # H7: 三個 B 變體都滿足 sum=134 (代數必然)
    chk("H7 所有 B 變體滿足 sum=134",
        all(hv11 + hv21 == 134 for _, hv11, hv21 in
            [(3, 38, 96), (4, 36, 98), (5, 34, 100)]),
        "(2B 相消 => sum 約束唔含 B)")

    # H8: h11=36 家族喺 alltoric 嘅 h21 鄰域 (孤島聲稱嘅數據集依賴性)
    fam = sorted(int(v) for v in arr[arr[:, 0] == 36][:, 1])
    nb = {v: fam.count(v) for v in [96, 97, 98, 99, 100, 101]}
    print(f"\n  alltoric 中 h11=36 家族 h21 鄰域: {nb}")
    print(f"    => 「h21=98 孤島」喺 alltoric.spec 唔成立 (鄰域全部存在)")
    chk("H8 孤島聲稱係 HF 數據集專屬 (alltoric 不成立)",
        all(c >= 1 for c in nb.values()),
        "(O53 docs/29 之 366,599 係 HF polytopes-4d 20-vertex, 非 alltoric)")
else:
    print(f"  [WARN] KS 數據不存在: {KS}")
    chk("H1 KS 數據可讀", False, "(檔案缺失)")

# ============================================================
# I. 數據檔交叉比對
# ============================================================
print("\n" + "=" * 74)
print("[I] 數據檔交叉比對 (重算值 vs 記錄 JSON)")
print("=" * 74)

def load(fn):
    p = os.path.join(ROOT, 'data', fn)
    if not os.path.exists(p):
        return None
    with open(p) as f:
        return json.load(f)

d1 = load('01_moduli_lock_derivation.json')
d2 = load('02_projection_matrix.json')
d3 = load('03_gen3_proof.json')
d4 = load('final_verification.json')

for nm, dd in [('01', d1), ('02', d2), ('03', d3), ('final', d4)]:
    chk(f"I1 data/{nm} 存在", dd is not None)

if d1:
    chk("I2 d1.h11_A = 重算 36", d1['h11_A'] == h11_A)
    chk("I3 d1.h21_A = 重算 98", d1['h21_A'] == h21_A)
    chk("I4 d1.chi = 重算 -124", d1['chi'] == chi)
    chk("I5 d1.Nd = 重算 44", d1['Nd'] == Nd)
    chk("I6 d1.Sigma_gamma = 90", abs(d1['Sigma_gamma'] - 90) < 1e-9)
    chk("I7 d1.Z2_dual_pairs = 22", d1['Z2_dual_pairs'] == 22)
    chk("I8 d1.B_test B=4 = (36,98)", d1['B_test']['4'] == "h11=36, h21=98")

if d2:
    chk("I9 d2.rank_M = 重算 36", d2['rank_M'] == rank_M)
    chk("I10 d2.nullity = 重算 8", d2['nullity'] == 8)
    chk("I11 d2.M_orthogonal = True", d2['M_orthogonal'] is True)
    chk("I12 d2.null_projection_zero = True", d2['null_projection_zero'] is True)
    chk("I13 d2.block_structure = 3x12", d2['block_structure'] == "3x12")

if d3:
    chk("I14 d3.N_gen_from_proof = 3", d3['N_gen_from_proof'] == 3)
    chk("I15 d3.h11 = 重算 36", d3['h11'] == h11_A)
    chk("I16 d3.h21 = 重算 98", d3['h21'] == h21_A)

if d4:
    chk("I17 d4.total_checks = 128", d4.get('total_checks') == 128)
    chk("I18 d4.all_passed = True", d4.get('all_passed') is True)

# ============================================================
# 總結
# ============================================================
print("\n" + "=" * 74)
print(f"Phase 2 獨立重算: 通過 {passed}, 失敗 {failed}")
print("=" * 74)
if failed:
    sys.exit(1)
print("Phase 2 全部通過")
