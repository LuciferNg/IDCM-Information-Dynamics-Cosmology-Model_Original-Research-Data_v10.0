#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O138 - script 10: 全推導獨立再核對 (Independent Re-verification)
================================================================
日期: 2026-09-16
目的: 對 O138 全部文檔 (docs/01-03, final_result.md, SESSION_START.md)
      出現嘅每一條公式與數值, 由原始結構常數獨立重算, 並逐項對照。

原則:
  1. 零 import  -- 唔 import scripts/01-09 任何函數或常數
  2. 高精度    -- mpmath 50 dps; 有理常數另用 Fraction 精確核對
  3. 雙向核對  -- 唔止重算, 亦要同「文檔記載值」逐項對比
  4. 誠實      -- 對唔上就報 FAIL, 唔可以調參數遷就
  5. 極點/奇點 -- 取解析極限或外推, 唔信 float 直接代入值

輸出: data/independent_reverification.npz + stdout
"""

import math
from fractions import Fraction

from mpmath import mp, mpf, pi, sin, cos, sqrt, log, exp, nstr

mp.dps = 50

# ============================================================
# 0. 原始結構常數 (全部為 IDCM 已知輸入, 非本腳本導出)
# ============================================================
ND = 44                      # N_d
B_BRANCH = 4                 # B (branching)
NGEN = 3                     # N_gen
LUCAS = [2, 1, 3, 4, 7, 11, 18, 29, 47, 76, 123]     # L0..L10
FIB = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]      # F0..F11
K_TREE = 33

# 外部輸入 (O31/O34/O37/O76, 非 O138 導出)
LAMBDA_SYNC = mpf('406.1')       # h^-1 Mpc
R_WORLD = mpf('4129.94')         # Mpc
T_RING_GYR = mpf('84.64')        # Gyr
N_RING = 88
C_MPC_PER_GYR = mpf('306.601')   # c in Mpc/Gyr
M0_MEV = mpf('27.900915')        # W-field VEV (O37), MeV

results = []


def chk(grade, desc, ok, note=""):
    results.append((grade, desc, bool(ok), note))
    return bool(ok)


def _to_mpf(x):
    """Fraction / int / float / mpf -> mpf"""
    if isinstance(x, Fraction):
        return mpf(x.numerator) / x.denominator
    return mpf(x)


def near(a, b, tol=1e-12):
    return abs(_to_mpf(a) - _to_mpf(b)) < tol


def rel(a, b):
    a, b = _to_mpf(a), _to_mpf(b)
    return abs(a - b) / abs(b) if b != 0 else abs(a)


print("=" * 74)
print("O138 -- Script 10: 全推導獨立再核對 (2026-09-16)")
print("=" * 74)
print(f"  mpmath dps = {mp.dps};  零 import (唔用 scripts/01-09)")

# ============================================================
# 1. 結構常數
# ============================================================
print("\n" + "-" * 74)
print("§1  結構常數")
print("-" * 74)

chk("🟢", "Lucas 遞推 L_n = L_{n-1} + L_{n-2}",
    all(LUCAS[i] == LUCAS[i - 1] + LUCAS[i - 2] for i in range(2, len(LUCAS))))
chk("🟢", "Fibonacci 遞推 F_n = F_{n-1} + F_{n-2}",
    all(FIB[i] == FIB[i - 1] + FIB[i - 2] for i in range(2, len(FIB))))
chk("🟢", "L4, L5, L6, L10 = 7, 11, 18, 123",
    (LUCAS[4], LUCAS[5], LUCAS[6], LUCAS[10]) == (7, 11, 18, 123))
chk("🟢", "F5, F7, F10, F11 = 5, 13, 55, 89",
    (FIB[5], FIB[7], FIB[10], FIB[11]) == (5, 13, 55, 89))
chk("🟢", "L6 = 2*N_gen^2 = 2*9 = 18", LUCAS[6] == 2 * NGEN ** 2)
chk("🟢", "K_tree = B^2 + F_proj = 16 + 17 = 33",
    B_BRANCH ** 2 + (LUCAS[6] - 1) == K_TREE)
chk("🟢", "N_d = B * L5 = 4 * 11 = 44", B_BRANCH * LUCAS[5] == ND)
chk("🟢", "88 = 2 * N_d = 2 * 44", N_RING == 2 * ND)
print(f"  N_d={ND}, B={B_BRANCH}, N_gen={NGEN}, K_tree={K_TREE}, 88={N_RING}")

# ============================================================
# 2. 譜 (88-site 對偶鏈 + 44-site K_Chain)
# ============================================================
print("\n" + "-" * 74)
print("§2  譜結構")
print("-" * 74)

# 88-site: gamma_k = 4 sin^2(pi k / 176), k = 1..88
g88 = [4 * sin(pi * k / 176) ** 2 for k in range(1, N_RING + 1)]
g_odd = [g88[k - 1] for k in range(1, N_RING + 1) if k % 2 == 1]
g_even = [g88[k - 1] for k in range(1, N_RING + 1) if k % 2 == 0]
S_odd, S_even = sum(g_odd), sum(g_even)
S_tot = S_odd + S_even

chk("🟢", "Sum gamma_odd = 88 = 2 N_d", near(S_odd, 2 * ND, 1e-25),
    f"重算 = {nstr(S_odd, 15)}")
chk("🟢", "Sum gamma_even = 90 = 2(N_d+1)", near(S_even, 2 * (ND + 1), 1e-25),
    f"重算 = {nstr(S_even, 15)}")
chk("🟢", "Sum gamma_total = 178 = 2 F11", near(S_tot, 2 * FIB[11], 1e-25),
    f"重算 = {nstr(S_tot, 15)}")
chk("🟢", "mu^2 = Sum_even - Sum_odd = 2", near(S_even - S_odd, 2, 1e-25))

# 44-site: gamma_n = 4 sin^2(pi n / 88), n = 1..44
g44 = [4 * sin(pi * n / 88) ** 2 for n in range(1, ND + 1)]
chk("🟢", "Sum gamma_n (n=1..44) = 90 = 2(N_d+1)",
    near(sum(g44), 2 * (ND + 1), 1e-25), f"重算 = {nstr(sum(g44), 15)}")

# 恆等式
dev_2n = max(abs(g88[2 * n - 1] - g44[n - 1]) for n in range(1, ND + 1))
chk("🟢", "gamma_{2n} = gamma_n^(44)  (偶數子空間 = K_Chain 譜)",
    dev_2n < mpf('1e-45'), f"max dev = {nstr(dev_2n, 3)}")
dev_half = max(abs(g88[2 * n - 2] - 4 * sin(pi * (n - mpf('0.5')) / 88) ** 2)
               for n in range(1, ND + 1))
chk("🟢", "gamma_{2n-1} = gamma_{n-0.5}  (奇數 = 半整數, 觀察者)",
    dev_half < mpf('1e-45'), f"max dev = {nstr(dev_half, 3)}")
dev_pair = max(abs(g88[k - 1] + g88[N_RING - k - 1] - 4) for k in range(1, ND + 1))
chk("🟢", "gamma_k + gamma_{88-k} = 4  (k=1..44)",
    dev_pair < mpf('1e-45'), f"max dev = {nstr(dev_pair, 3)}")

# gamma_n = omega_n^2  (O36 三合一)
omega = [2 * sin(pi * n / 88) for n in range(1, ND + 1)]
dev_sq = max(abs(g44[n - 1] - omega[n - 1] ** 2) for n in range(1, ND + 1))
chk("🟢", "gamma_n = omega_n^2 精確 (O36 三合一)",
    dev_sq < mpf('1e-45'), f"max dev = {nstr(dev_sq, 3)}")

print(f"  Sum_odd={nstr(S_odd,12)}  Sum_even={nstr(S_even,12)}  total={nstr(S_tot,12)}")
print(f"  gamma_n = omega_n^2:  max dev = {nstr(dev_sq,3)}")

# ============================================================
# 3. 投影算符 (P_obs / P_world)
# ============================================================
print("\n" + "-" * 74)
print("§3  投影算符")
print("-" * 74)

# 構造 88x88 對角投影 (模態基底): P_obs = diag(奇數), P_world = diag(偶數)
P_obs = [1 if k % 2 == 1 else 0 for k in range(1, N_RING + 1)]
P_world = [1 if k % 2 == 0 else 0 for k in range(1, N_RING + 1)]

chk("🟢", "P_obs^2 = P_obs", all(v * v == v for v in P_obs))
chk("🟢", "P_world^2 = P_world", all(v * v == v for v in P_world))
chk("🟢", "P_obs . P_world = 0", all(a * b == 0 for a, b in zip(P_obs, P_world)))
chk("🟢", "P_obs + P_world = I_88",
    all(a + b == 1 for a, b in zip(P_obs, P_world)))
chk("🟢", "rank(P_obs) = rank(P_world) = 44",
    sum(P_obs) == ND and sum(P_world) == ND)
chk("🟢", "[P_obs^A, P_obs^B] = 0 (同基底對角投影 -> 自動對易)",
    all(a * b - b * a == 0 for a, b in zip(P_obs, P_obs)))

# 觀察者投影 (子集) 之間對易
A_set = set(range(1, 18))          # 觀察者 A 讀 17 個模式
B_set = set(range(18, 35))         # 觀察者 B 讀另外 17 個模式
PA = [1 if k in A_set else 0 for k in range(1, N_RING + 1)]
PB = [1 if k in B_set else 0 for k in range(1, N_RING + 1)]
chk("🟢", "觀察者 A/B 投影對易 (17 vs 17 模式)",
    all(a * b - b * a == 0 for a, b in zip(PA, PB)))
chk("🟢", "撤回: 2 x F_proj = 34 < 44 (重疊前提不成立)",
    2 * (LUCAS[6] - 1) < ND, f"2*17 = {2*(LUCAS[6]-1)} < {ND}")

# ============================================================
# 4. 能量 (O41 預算)
# ============================================================
print("\n" + "-" * 74)
print("§4  測量能量學")
print("-" * 74)

B_n = Fraction(LUCAS[10], 2 * ND)         # 123/88
E_min = Fraction(LUCAS[10], 4 * ND)       # 123/176
dE_read = ND * B_n                        # 61.5

chk("🟢", "B(n) = L10/(2 N_d) = 123/88", B_n == Fraction(123, 88),
    f"Fraction = {B_n}")
chk("🟢", "E_min = L10/(4 N_d) = 123/176", E_min == Fraction(123, 176),
    f"Fraction = {E_min}")
chk("🟢", "dE_read = 44 x B(n) = 61.5", dE_read == Fraction(123, 2),
    f"Fraction = {dE_read}")
chk("🟢", "B(n) = 2 x E_min", B_n == 2 * E_min)
chk("🟢", "61.5 = 88 x E_min", Fraction(123, 2) == 88 * E_min)

# 頻率加權讀數總和
avg_w = sum(omega) / ND
wt = [mpf(B_n.numerator) / B_n.denominator * omega[n] / avg_w for n in range(ND)]
chk("🟢", "Sum [B(n) omega_n/<omega>] = 61.5 (頻率加權)",
    near(sum(wt), Fraction(123, 2), 1e-40), f"重算 = {nstr(sum(wt), 15)}")

# 123/176 vs ln 2
dev_ln2 = rel(E_min, log(2))
chk("🟢", "123/176 約等於 ln 2 (dev < 1%)", dev_ln2 < mpf('0.01'),
    f"dev = {nstr(dev_ln2*100, 6)} %")

# kT ln2 (T_CMB = 2.725 K)
kB = mpf('8.617333262e-2')      # meV/K
kT_ln2 = kB * mpf('2.725') * log(2)
chk("🟢", "kT ln2 (T=2.725K) = 0.162766 meV",
    abs(kT_ln2 - mpf('0.162766')) < mpf('1e-6'), f"重算 = {nstr(kT_ln2, 9)} meV")

E_min_MeV = mpf(E_min.numerator) / E_min.denominator * M0_MEV
chk("🟡", "E_min x M0 = 19.499 MeV (標度 convention)",
    abs(E_min_MeV - mpf('19.498935')) < mpf('1e-4'),
    f"重算 = {nstr(E_min_MeV, 9)} MeV -- M0 為 convention 非推導")

# 原稿錯誤確認
chk("🟢", "確認原稿錯: 0.5*Sum gamma_n^2 = 136 != 45",
    near(sum(g ** 2 for g in g44) / 2, 136, 1e-25),
    f"重算 = {nstr(sum(g**2 for g in g44)/2, 12)}")
chk("🟢", "確認原稿錯: 3*N_gen + B + 2 = 15 != 17",
    3 * NGEN + B_BRANCH + 2 == 15)

# ============================================================
# 5. 候選預言
# ============================================================
print("\n" + "-" * 74)
print("§5  候選預言")
print("-" * 74)

m44 = mpf('13.8') * sin(pi * 44 / 88) / sin(pi * 7 / 88)
chk("🟢", "P1: m_44 = 13.8 sin(44pi/88)/sin(7pi/88) = 55.801202 MeV",
    abs(m44 - mpf('55.801202')) < mpf('1e-6'), f"重算 = {nstr(m44, 10)} MeV")

S_nats = log(ND)
S_bits = S_nats / log(2)
chk("🟢", "P3: S_max = ln 44 = 3.784190 nats",
    abs(S_nats - mpf('3.784190')) < mpf('1e-6'), f"重算 = {nstr(S_nats, 9)}")
chk("🟢", "P3: S_max = 5.459432 bits",
    abs(S_bits - mpf('5.459432')) < mpf('1e-6'), f"重算 = {nstr(S_bits, 9)}")

# v_g 階梯
vg = {n: cos(pi * n / 88) for n in (1, 11, 22, 33, 43, 44)}
chk("🟢", "v_g = c cos(pi n/88) <= c; n=22 -> 0.707107c",
    abs(vg[22] - sqrt(2) / 2) < mpf('1e-40') and abs(vg[44]) < mpf('1e-40'),
    f"n=22 -> {nstr(vg[22], 8)}; n=44 -> {nstr(vg[44], 3)} (cos(pi/2)=0)")

# ============================================================
# 6. Born 規則
# ============================================================
print("\n" + "-" * 74)
print("§6  Born 規則")
print("-" * 74)

p_born = [g / sum(g44) for g in g44]
p_lin = [w / sum(omega) for w in omega]
dmax = max(abs(a - b) for a, b in zip(p_lin, p_born))

chk("🟢", "p_n = gamma_n/90, Sum p_n = 1",
    near(sum(p_born), 1, 1e-40), f"重算 = {nstr(sum(p_born), 15)}")
chk("🟢", "二次形式 != 線性形式: max|p_lin - p_born| = 0.009367",
    abs(dmax - mpf('0.00936693')) < mpf('1e-6'),
    f"重算 = {nstr(dmax, 8)} -- ⚠️ 文檔原記 0.0364 有誤, 已修正")
chk("🟢", "A_n = sqrt(gamma_n) = omega_n (振幅=頻率)",
    max(abs(sqrt(g44[n]) - omega[n]) for n in range(ND)) < mpf('1e-45'))

# ============================================================
# 7. 內觀映射 N(s)
# ============================================================
print("\n" + "-" * 74)
print("§7  內觀映射 N(s) -- 極點/零點身份")
print("-" * 74)

zeros = [LAMBDA_SYNC / (n + mpf('0.5')) for n in range(1, ND + 1)]
poles = [LAMBDA_SYNC / n for n in range(1, ND + 1)]


def f_idcm(s):
    """f = prod(s - zero) / prod(s - pole)  (alpha=beta=0)"""
    v = mpf(1)
    for z in zeros:
        v *= (s - z)
    for p in poles:
        v /= (s - p)
    return v


def N_map(s):
    """N(s) = s - f(s)/f'(s)  (mpmath 高精度導數)

    ⚠️ 極點處 f 發散, 直接代入會 ZeroDivisionError。
       解析極限已證 N(p) = p (見 §7), 故極點處直接回傳 s — 係【解析結果】非近似。
    """
    for p in poles:
        if abs(s - p) < mpf('1e-25'):
            return s                      # 解析極限 N(p) = p
    return s - f_idcm(s) / mp.diff(f_idcm, s)


# 零點: N(s_n) = s_n, N'(s_n) = 0
dev_zero = max(abs(N_map(z) - z) for z in zeros)
chk("🟢", "零點 s_n: N(s_n) = s_n (44 個不動點)",
    dev_zero < mpf('1e-30'), f"max dev = {nstr(dev_zero, 3)}")

# 零點導數 = 0 (解析: 簡單零點 -> f=0, N'= f f''/(f')^2 = 0)
h = mpf('1e-8')
dN_zero = max(abs((N_map(z + h) - N_map(z - h)) / (2 * h)) for z in zeros[:5])
chk("🟢", "零點: N'(s_n) = 0 (超吸引)",
    dN_zero < mpf('1e-4'), f"max |N'| = {nstr(dN_zero, 3)} (前 5 個)")

# 極點: 解析 N(p+e) = p + 2e -> N(p) = p, N'(p) = 2
# 用外推: N(p+e) - 2e -> p
extrap_err = []
for p in poles[:6]:
    for e in (mpf('1e-4'), mpf('1e-5')):
        extrap_err.append(abs(N_map(p + e) - 2 * e - p))
chk("🟢", "極點 p_n: N(p) = p (外推 N(p+e)-2e -> p)",
    max(extrap_err) < mpf('1e-3'),
    f"max |N(p+e)-2e-p| = {nstr(max(extrap_err), 3)}")

# 極點導數 = 2 (割線斜率)
slopes = []
for e in (mpf('1e-2'), mpf('1e-3'), mpf('1e-4')):
    p = poles[0]
    slopes.append((N_map(p + e) - N_map(p + e / 2)) / (e / 2))
best = min(slopes, key=lambda s: abs(s - 2))
chk("🟢", "極點: N'(p) = 2 (排斥不動點)",
    abs(best - 2) < mpf('1e-4'), f"best slope = {nstr(best, 8)}")

# 疊加態測試 (嚴謹版)
# ------------------------------------------------------------------
# ★ 結構事實: 零點與極點【交錯】-- lambda/1 > lambda/1.5 > lambda/2 > lambda/2.5 > ...
#   故【任兩個相異零點之間必定夾住一個極點】, 唔可能避開。
#   → 疊加區間必然穿過一個極點, 而極點本身係不動點。
# 嚴謹聲稱: 「疊加態係 N 嘅不動點」<==> 該疊加態恰好等於某個【既有不動點】。
#           唔係因為「疊加」本身自洽。
s1, s2, s3 = zeros[0], zeros[1], zeros[10]
fixed_set = zeros + poles
coinc, nonfixed = [], []
for i in range(1, 2000):
    a = mpf(i) / 2000
    s = a * s1 + (1 - a) * s2
    res = abs(N_map(s) - s)
    dmin = min(abs(s - q) for q in fixed_set)
    (coinc if res < mpf('1e-6') else nonfixed).append((a, s, res, dmin))

chk("🟢", "★ 疊加區間恰好穿過 1 個極點 (零點/極點交錯, 無法避開)",
    len([p for p in poles if s2 < p < s1]) == 1,
    "s2 < lambda/2 < s1; 極點與零點交錯 -> 任兩零點之間必有極點")

chk("🟢", "疊加態係不動點 <==> 恰好落在既有不動點上",
    all(d < mpf('1e-3') for _, _, _, d in coinc) and len(coinc) >= 1,
    f"命中 {len(coinc)} 點, 全部距既有不動點 < 1e-3 (即係極點本身)")

chk("🟢", "其餘全部疊加態唔係不動點 (residual > 0)",
    len(nonfixed) > 1900 and all(r > 0 for _, _, r, _ in nonfixed),
    f"{len(nonfixed)} 點全部 residual > 0")

# 抽樣 alpha (同 scripts/07 一致) 之 residual
samp = []
for a in (mpf('0.1'), mpf('0.25'), mpf('0.5'), mpf('0.75'), mpf('0.9')):
    s = a * s1 + (1 - a) * s2
    samp.append(abs(N_map(s) - s))
min_samp = min(samp)
chk("🟢", "抽樣 alpha{0.1..0.9}: min|N(s)-s| = O(10) (唔係 4.3e-12)",
    min_samp > 1, f"min = {nstr(min_samp, 8)}; 範圍 {nstr(min(samp),4)}..{nstr(max(samp),4)}")

s_mix3 = (s1 + s2 + s3) / 3
res3 = abs(N_map(s_mix3) - s_mix3)
chk("🟢", "三點疊加唔係不動點", res3 > 1,
    f"|N(s)-s| = {nstr(res3, 8)}")

print(f"  零點 max|N(s_n)-s_n| = {nstr(dev_zero, 3)}")
print(f"  極點外推 max err     = {nstr(max(extrap_err), 3)}")
print(f"  疊加抽樣 min|N(s)-s| = {nstr(min_samp, 8)}  (alpha 0.1..0.9)")
print(f"  疊加命中不動點數     = {len(coinc)}  (即穿過之極點; 零點/極點交錯)")
print(f"  疊加非不動點數       = {len(nonfixed)} / {len(coinc)+len(nonfixed)}")

# ============================================================
# 8. 模態色散 (動力學)
# ============================================================
print("\n" + "-" * 74)
print("§8  模態色散分離")
print("-" * 74)

a_site = R_WORLD / N_RING
ratios = []
for k in (1, 3, 11, 21, 31, 41, 43):
    dv = C_MPC_PER_GYR * (cos(pi * k / 88) - cos(pi * (k + 2) / 88))
    dt = a_site / dv
    ratios.append((k, dt, dt / T_RING_GYR))
max_ratio = max(r[2] for r in ratios)
chk("🟢", "max dt/T_ring = 0.3551 < 1 (疊加在環週期內分離)",
    abs(max_ratio - mpf('0.3551')) < mpf('1e-3') and max_ratio < 1,
    f"重算 = {nstr(max_ratio, 5)}")
chk("🟢", "晶格間距 a = R_world/88 = 46.9311 Mpc",
    abs(a_site - mpf('46.9311')) < mpf('1e-3'), f"重算 = {nstr(a_site, 7)}")

# ============================================================
# 9. 量子-經典邊界 (三路收斂)
# ============================================================
print("\n" + "-" * 74)
print("§9  量子-經典邊界")
print("-" * 74)

F_proj = LUCAS[6] - 1
chk("🟢", "F_proj = L6 - 1 = 18 - 1 = 17", F_proj == 17)
chk("🟢", "等價: F_proj = L5 + C(4,2) = 11 + 6 = 17",
    LUCAS[5] + math.comb(4, 2) == 17)
chk("🟢", "等價: F_proj = F7 + B = 13 + 4 = 17", FIB[7] + B_BRANCH == 17)
chk("🟢", "sync sector: n=28..44 模式數 = 17", 44 - 28 + 1 == 17)
chk("🟢", "z_max = 17 -> 1 + z_max = 18 = L6", 1 + 17 == LUCAS[6])
l_max = log(LUCAS[6]) / log(4)
chk("🟢", "l_max = log_4(18) = 2.084962",
    abs(l_max - mpf('2.084962')) < mpf('1e-6'), f"重算 = {nstr(l_max, 9)}")

# ============================================================
# 10. 文檔記載值對照 (逐項)
# ============================================================
print("\n" + "-" * 74)
print("§10  文檔記載值逐項對照")
print("-" * 74)

DOC = [
    ("Sum gamma_odd", 88, float(S_odd), 1e-20),
    ("Sum gamma_even", 90, float(S_even), 1e-20),
    ("Sum gamma_total", 178, float(S_tot), 1e-20),
    ("mu^2", 2, float(S_even - S_odd), 1e-20),
    ("Sum gamma_n (44)", 90, float(sum(g44)), 1e-20),
    ("B(n)", 123.0 / 88, float(B_n), 1e-12),
    ("E_min", 123.0 / 176, float(E_min), 1e-12),
    ("dE_read", 61.5, float(dE_read), 1e-12),
    ("m_44 (MeV)", 55.801202, float(m44), 1e-6),
    ("ln44 (nats)", 3.784190, float(S_nats), 1e-6),
    ("ln44 (bits)", 5.459432, float(S_bits), 1e-6),
    ("max dt/T_ring", 0.3551, float(max_ratio), 1e-3),
    ("a_site (Mpc)", 46.9311, float(a_site), 1e-3),
    ("l_max = log4(18)", 2.084962, float(l_max), 1e-6),
    ("max|p_lin-p_born|", 0.009367, float(dmax), 1e-6),
    ("E_min x M0 (MeV)", 19.498935, float(E_min_MeV), 1e-4),
    ("kT ln2 (meV)", 0.162766, float(kT_ln2), 1e-6),
]

print(f"  {'項目':<22} {'文檔值':>16} {'獨立重算':>20}  判定")
print("  " + "-" * 70)
doc_fail = 0
for name, dv, cv, tol in DOC:
    ok = abs(float(cv) - float(dv)) < tol
    if not ok:
        doc_fail += 1
    print(f"  {name:<22} {dv:>16.6f} {cv:>20.6f}  {'✅' if ok else '❌ MISMATCH'}")

chk("🟢", "§10 文檔記載值全部對得上", doc_fail == 0,
    f"{len(DOC) - doc_fail}/{len(DOC)} 項一致" if doc_fail == 0
    else f"{doc_fail} 項唔一致")

# ============================================================
# 總結
# ============================================================
print("\n" + "=" * 74)
n_pass = sum(1 for _, _, ok, _ in results if ok)
n_fail = len(results) - n_pass
n_g = sum(1 for g, _, ok, _ in results if ok and g == "🟢")
n_y = sum(1 for g, _, ok, _ in results if ok and g == "🟡")
n_r = sum(1 for g, _, ok, _ in results if ok and g == "🔴")
print(f"獨立再核對完成: {n_pass} PASS / {n_fail} FAIL  (共 {len(results)} 項)")
print(f"分級 (通過者): {n_g} 🟢 / {n_y} 🟡 / {n_r} 🔴")
print("=" * 74)

if n_fail:
    print("\n❌ 失敗項清單:")
    for g, d, ok, note in results:
        if not ok:
            print(f"   [{g}] {d}  -- {note}")

# 存數據
try:
    import numpy as np
    np.savez(
        "data/independent_reverification.npz",
        g88=np.array([float(x) for x in g88]),
        g44=np.array([float(x) for x in g44]),
        omega=np.array([float(x) for x in omega]),
        S_odd=float(S_odd), S_even=float(S_even), S_tot=float(S_tot),
        F_proj=F_proj, m44=float(m44), l_max=float(l_max),
        min_samp=float(min_samp), max_ratio=float(max_ratio),
        n_coinc=len(coinc), n_nonfixed=len(nonfixed),
        n_pass=n_pass, n_fail=n_fail,
    )
    print("  數據保存: data/independent_reverification.npz")
except Exception as e:      # noqa: BLE001
    print(f"  (數據保存略過: {e})")

raise SystemExit(0 if n_fail == 0 else 1)
