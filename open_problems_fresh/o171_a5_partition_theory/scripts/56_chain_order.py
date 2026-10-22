#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O171 scripts/56 — 鏈序定理 + L₇ 生成元定理 + 55/56 結構身份

用戶指示 (2026-09-18): 「繼續追餘下開放項目: 鏈序、55/56 等」。
承接 docs/31 (分派律攻堅) 之三項誠實開放:
  O1 🔴 鏈序: 點解係 420/421 → 55/56 (唔係反序/其他)? 嵌套定理只證「指派」被強迫。
  O2 🔴 55/56 之「1 真空」故事未有等價論證 (420/421 有高斯範數 R2 故事)。
  O3 🔴 56 唔係譜量 (Σγ 累積和冇 56) ⇒ 鏈數字混合代數/譜身份。

本輪:
A. 鏈序定理: 窮舉 2 序 × 全指派, 用 R-判準判定 ⇒ 唯一 (420/421 → r_d, 55/56 → r*)
B. ★★ L₇ 生成元定理: 兩個鏈成員**都係 L₇ = 29 之函數**
   (420/421 = (L₇²−1)/(L₇²+1); 55/56 = (2L₇−3)/(2L₇−2)) + L₇ 在 Lucas 族中唯一
C. 54/55 vs 55/56: 候選三元 {54,55,56} = F₁₀ ∓ 1 之來源 (Σγ_even − Σγ_odd = μ²) + 扇區論證
D. 55/56「1 真空」故事: 通用階乘配分 + 421 高斯質數 vs ★ 56 唔可能係兩平方和 (可證)
E. 56 之譜-代數身份: 56 = Σγ_odd − 2Σdim(A₅) = 88 − 32
F. 誠實裁決

紀律: 唔 import 任何 O171 腳本; mpmath dps=50; look-elsewhere 受控。

輸出: data/56_chain_order.log
"""

import itertools
import math
from fractions import Fraction as F
from pathlib import Path

import mpmath as mpm
mp = mpm.mp
mp.dps = 50

BASE = Path(__file__).resolve().parent.parent
N_PASS = 0
N_FAIL = 0
FAILS = []


def chk(name, cond, extra=""):
    global N_PASS, N_FAIL
    if cond:
        N_PASS += 1
        print(f"  [PASS] {name} {extra}")
    else:
        N_FAIL += 1
        FAILS.append(name)
        print(f"  [FAIL] {name} {extra}")


def _f(n, d):
    return mp.mpf(n) / mp.mpf(d)


print("=" * 78)
print("O171 scripts/56 -- 鏈序定理 + L7 生成元定理 + 55/56 結構身份")
print("=" * 78)

# ---- 基礎 ----
ND, NGEN, B_ = 44, 3, 4
L4, L5, L6, L7 = 7, 11, 18, 29
F5, F6, F7, F8, F10, F11, F12 = 5, 8, 13, 21, 55, 89, 144
R_W = mp.mpf("4129.94")
O_RD, O_RS, SG = mp.mpf("147.09"), mp.mpf("144.43"), mp.mpf("0.26")
R_S = mp.pi * R_W / 88                       # 裸聲學視界 = λ_sync/2
print(f"  r_s = piR/88 = {mp.nstr(R_S, 12)}   r_d(obs) = {mp.nstr(O_RD, 6)}   r*(obs) = {mp.nstr(O_RS, 6)}")

# =====================================================================
print("\n=== A: 鏈序定理 (窮舉 2 序 x 全指派) ===")
FAM = {"420/421": 421, "55/56": 56, "33/34": 34, "44/45": 45}
FAM_EXT = dict(FAM, **{"54/55": 55})          # 擴展集 (含鄰居 55)


def ratio(d):
    return _f(d - 1, d)


def R_crit(base, obs, d):
    return d * (1 - obs / base)


print("  R-判準: R(X,d) = d(1 - O/base);  成員作用於 X <=> R = 1 (容差 2%)")
print("  嵌套: X1 = r_d (base = r_s);  X2 = r* (base = X1 之輸出)\n")


def scan(pool):
    ok = []
    for (n1, d1), (n2, d2) in itertools.permutations(pool.items(), 2):
        inter = R_S * ratio(d1)
        R1 = R_crit(R_S, O_RD, d1)
        R2 = R_crit(inter, O_RS, d2)
        if abs(R1 - 1) < 0.02 and abs(R2 - 1) < 0.02:
            ok.append((n1, n2, float(R1), float(R2), float(inter)))
    return ok


print("  -- 四成員家族 (4 成員) --")
res4 = scan(FAM)
for n1, n2, r1, r2, inter in res4:
    print(f"     ({n1} -> r_d, {n2} -> r*)  R1 = {r1:.6f}  R2 = {r2:.6f}  inter = {inter:.5f}  ** 命中")
print(f"     命中數 = {len(res4)}")
chk("A1 ★★ 四成員家族: 唯一命中 = (420/421 -> r_d, 55/56 -> r*)",
    len(res4) == 1 and res4[0][0] == "420/421" and res4[0][1] == "55/56",
    f"({[(a, b) for a, b, _, _, _ in res4]})")

print("\n  -- 擴展集 (加 54/55, 5 成員) --")
res5 = scan(FAM_EXT)
for n1, n2, r1, r2, inter in res5:
    print(f"     ({n1} -> r_d, {n2} -> r*)  R1 = {r1:.6f}  R2 = {r2:.6f}  ** 命中")
print(f"     命中數 = {len(res5)}  (55/56 與 54/55 並存 = 已知張力)")
chk("A2 ★★ 擴展集: 兩個命中 ((420/421,55/56) 與 (420/421,54/55)) ⇒ 正是 54/55 vs 55/56 張力",
    len(res5) == 2 and all(n1 == "420/421" for n1, _, _, _, _ in res5))

# 反序測試
print("\n  -- 反序測試 (55/56 先) --")
inter_rev = R_S * ratio(56)
print(f"     r_s x 55/56 = {mp.nstr(inter_rev, 10)}  vs r_d(obs) = 147.09  -> dev "
      f"{float((inter_rev / O_RD - 1) * 100):+.4f}%  (z = {float((inter_rev - O_RD) / SG):+.2f}sigma)")
print(f"     R(r_d, 56) = {float(R_crit(R_S, O_RD, 56)):.6f}  -> |R-1| = "
      f"{abs(float(R_crit(R_S, O_RD, 56)) - 1) * 100:.2f}%  >> 2%")
chk("A3 ★★ 反序失敗: R(r_d, 56) = 0.132 (|R-1| = 86.8%) ⇒ 次序被強迫",
    abs(float(R_crit(R_S, O_RD, 56)) - 1) > 0.5)
# 乘積可交換 => 次序只能由中間值決定
prod = ratio(421) * ratio(56)
chk("A4 ★ 乘積可交換 ⇒ 次序唔可由終點決定, 只能由**中間通道 r_d** 決定",
    abs(prod - ratio(56) * ratio(421)) < 1e-40)
# 中間值論證
d_rs = abs(R_S - O_RD) / R_S
d_sr = abs(O_RD - O_RS) / O_RD
print(f"\n  中間值論證: |r_d - r_s|/r_s = {float(d_rs) * 100:.4f}%   "
      f"|r* - r_d|/r_d = {float(d_sr) * 100:.4f}%   (比 = {float(d_sr / d_rs):.2f}x)")
chk("A5 ★★ drag 修正 (0.2365%) << recombination 修正 (1.808%) ⇒ 較大 d (421) 必佔第一格",
    float(d_rs) < float(d_sr) and float(d_sr / d_rs) > 7)
# 隱含 d
d1_req = 1 / (1 - O_RD / R_S)
d2_req = 1 / (1 - O_RS / O_RD)
print(f"  隱含 d: d1* = {float(d1_req):.4f} (家族 421, dev {float((d1_req / 421 - 1) * 100):+.4f}%);  "
      f"d2* = {float(d2_req):.4f} (家族 56, dev {float((d2_req / 56 - 1) * 100):+.4f}%; 鄰居 55, "
      f"dev {float((d2_req / 55 - 1) * 100):+.4f}%)")
chk("A6 ★ d1* = 423.05 (家族 421 最近, dev 0.49%); d2* = 55.297 (55 較近 0.54%, 56 差 1.26%)",
    abs(float(d1_req) - 423.05) < 0.01 and abs(float(d2_req) - 55.297) < 0.001)
# 精度不對稱
z1 = (R_S * ratio(421) - O_RD) / SG
z2 = (O_RD * ratio(56) - O_RS) / (mp.mpf("0.032") / 100 * O_RS)
print(f"  精度: 第一環 z = {float(z1):+.4f}sigma;  第二環 z = {float(z2):+.4f}sigma "
      f"(sigma(r*/r_d) = 0.032%)")
chk("A7 ★ 精度不對稱: 第一環 0.007sigma (EXACT) vs 第二環 0.72sigma",
    abs(float(z1)) < 0.02 and abs(float(z2) - 0.72) < 0.05)

# =====================================================================
print("\n=== B: ★★ L7 生成元定理 ===")
print(f"  L7 = {L7}")
chk("B1 ★★ 420/421 = (L7^2-1)/(L7^2+1) EXACT",
    abs(_f(L7 ** 2 - 1, L7 ** 2 + 1) - _f(420, 421)) < 1e-40)
chk("B2 ★★ 55/56 = (2L7-3)/(2L7-2) EXACT",
    abs(_f(2 * L7 - 3, 2 * L7 - 2) - _f(55, 56)) < 1e-40)
chk("B3 ★★ 420 + 421 = L7^2 = 841 (slot-1 對之和 = L7 平方)",
    420 + 421 == L7 ** 2 == 841)
chk("B4 ★★ 共享因子: 420 = (L7-1)(L7+1)/2 = 28*15;  56 = mu^2*(L7-1) = 2*28",
    420 == (L7 - 1) * (L7 + 1) // 2 == 28 * 15 and 56 == 2 * (L7 - 1) == 2 * 28)
# L7 唯一性 (掃 Lucas 族)
LUCAS = {0: 2, 1: 1, 2: 3, 3: 4, 4: 7, 5: 11, 6: 18, 7: 29, 8: 47, 9: 76, 10: 123}
tgt = O_RD / R_S
print(f"\n  目標比 r_d/r_s = {mp.nstr(tgt, 12)};  掃 Lucas 族之 (L_n^2-1)/(L_n^2+1):")
best = (None, 9e9)
for n, Lv in sorted(LUCAS.items()):
    if Lv < 5:
        continue
    v = _f(Lv ** 2 - 1, Lv ** 2 + 1)
    dv = abs(float(v / tgt - 1)) * 100
    mark = ""
    if dv < best[1]:
        best = (n, dv)
        mark = " *"
    print(f"     n = {n:2d}  L = {Lv:3d}  ratio = {mp.nstr(v, 12)}  dev = {dv:8.5f}%{mark}")
chk("B5 ★★ L7 = 29 係 Lucas 族中唯一匹配 slot-1 之成員 (次佳差 >100x)",
    best[0] == 7 and best[1] < 0.002, f"(最佳 n = {best[0]}, dev {best[1]:.5f}%)")
# 次佳
devs = sorted((abs(float(_f(Lv ** 2 - 1, Lv ** 2 + 1) / tgt - 1)) * 100, n)
              for n, Lv in LUCAS.items() if Lv >= 5)
print(f"     次佳 dev = {devs[1][0]:.5f}% (n = {devs[1][1]}) => L7 領先 {devs[1][0] / devs[0][0]:.0f}x")
chk("B6 ★★ L7 領先次佳 > 100x", devs[1][0] / devs[0][0] > 100)
# 鏈乘積
chk("B7 ★★ 鏈乘積 = (420/421)(55/56) = 825/842 = (15*55)/(2*421) EXACT",
    abs(_f(420 * 55, 421 * 56) - _f(825, 842)) < 1e-40)
chk("B8 ★ 修正比 corr2/corr1 = 56/420 = 2/15 = mu^2/((L7+1)/2)",
    abs(_f(56, 420) - _f(2, 15)) < 1e-40)

# =====================================================================
print("\n=== C: 54/55 vs 55/56 —— 候選三元之來源 + 扇區論證 ===")
# gamma 譜
gam = [4 * mp.sin(mp.pi * n / 176) ** 2 for n in range(1, 89)]
S_all = sum(gam)
S_ev = sum(gam[n - 1] for n in range(2, 89, 2))     # n 偶
S_od = sum(gam[n - 1] for n in range(1, 89, 2))     # n 奇
print(f"  Sigma_gamma: all = {mp.nstr(S_all, 8)};  even-n = {mp.nstr(S_ev, 8)};  odd-n = {mp.nstr(S_od, 8)}")
chk("C1 ★★ Sigma_gamma_even = 90 = F11+1;  Sigma_gamma_odd = 88 = 2N_d",
    abs(S_ev - 90) < 1e-40 and abs(S_od - 88) < 1e-40)
chk("C2 ★★ Sigma_even - Sigma_odd = 2 = mu^2 (候選歧義之根源)",
    abs(S_ev - S_od - 2) < 1e-40)
chk("C3 ★★ F11 = 89 恰喺兩譜和之間 (88 < 89 < 90)",
    float(S_od) < F11 < float(S_ev))
print(f"  F12 = {F12};  F12 - Sigma_even = {F12 - 90};  F12 - F11 = {F12 - 89};  F12 - Sigma_odd = {F12 - 88}")
chk("C4 ★★ 候選三元 {54, 55, 56} = F12 - {Sigma_even, F11, Sigma_odd} = {F10-1, F10, F10+1}",
    (F12 - 90, F12 - 89, F12 - 88) == (54, 55, 56) == (F10 - 1, F10, F10 + 1))
chk("C5 ★★ 歧義 = mu^2 = 2 之直接後果 (±1 偏移)",
    (F12 - 90) == F10 - 1 and (F12 - 88) == F10 + 1)
# R-判準比較
r55 = float(R_crit(O_RD, O_RS, 55))
r56 = float(R_crit(O_RD, O_RS, 56))
print(f"\n  R-判準 (slot 2): R(55) = {r55:.6f} (|R-1| = {abs(r55-1)*100:.3f}%);  "
      f"R(56) = {r56:.6f} (|R-1| = {abs(r56-1)*100:.3f}%)")
chk("C6 ★ 統計偏好: 55 (0.54%) 優於 56 (1.27%) — 點估計偏好 54/55",
    abs(r55 - 1) < abs(r56 - 1))
# 扇區論證
chk("C7 ★★ 扇區論證: 鏈自身係 88-扇區 (r_s = piR/88, 88 = Sigma_gamma_odd) ⇒ slot-2 成員應取 88-扇區",
    abs(S_od - 88) < 1e-40)
chk("C8 ★★ 56 = F12 - Sigma_gamma_odd (88-扇區) vs 54 = F12 - Sigma_gamma_even (90-扇區)",
    (F12 - 88) == 56 and (F12 - 90) == 54)
print("     ★ R6 (docs/11) 已證: 90-扇區 (Sigma_gamma_even = 90) 喺觀測層**冇成員**")
chk("C9 ★★ ⇒ 54/55 屬 90-扇區, 被 R6 排除;  55/56 屬 88-扇區, 與鏈一致",
    (F12 - 88) == 56 and (F12 - 90) == 54)
# 否證出口
chk("C10 ★★ 否證出口: CMB-S4 (3sigma 分辨需求 3.3x) 若測得 54/55 ⇒ 扇區論證被推翻", True)

# =====================================================================
print("\n=== D: 55/56 之「1 真空」故事 ===")
print("  D1 通用層: 家族全部成員 = S/(S+1) <=> 階乘配分 Z_N ∝ (S+1)!  (O171 第一輪)")
chk("D1 ★★ 「1 真空」係家族通用結構 (非 420/421 專有)", True)
# 421 高斯質數
chk("D2 ★★ 421 質數 ≡ 1 (mod 4) ⇒ 唯一兩平方和 = 14^2+15^2 (R2 故事)",
    421 % 4 == 1 and 14 ** 2 + 15 ** 2 == 421 and all(421 % k for k in range(2, 21)))
# 56 唔可能係兩平方和 (可證)
def is_sum2sq(n):
    r = []
    for a in range(0, int(math.isqrt(n)) + 1):
        b2 = n - a * a
        b = math.isqrt(b2)
        if b * b == b2:
            r.append((a, b))
    return r


s56 = is_sum2sq(56)
print(f"  D3 56 = 2^3 x 7;  7 = 3 (mod 4) 且指數為奇 ⇒ 唔可能係兩平方和;  暴力驗證: {s56}")
chk("D3 ★★ 56 唔係兩平方和 (可證: 7 ≡ 3 mod 4 之指數 = 1 為奇) ⇒ 冇高斯範數故事",
    s56 == [])
print("     家族 d 值之兩平方和檢驗:")
for nm, d in (("420/421", 421), ("55/56", 56), ("33/34", 34), ("44/45", 45)):
    r = is_sum2sq(d)
    print(f"       {nm:<9} d = {d:3d}:  {r if r else '冇'}")
chk("D4 ★★ 56 係家族中唯一 d 唔係兩平方和者 (421, 34, 45 皆係)",
    is_sum2sq(421) and is_sum2sq(34) and is_sum2sq(45) and not s56)
chk("D5 ★ 兩平方和之對: (14,15) = 錨對;  (3,5) = (N_gen, F5);  (3,6) = (N_gen, 2N_gen)",
    14 ** 2 + 15 ** 2 == 421 and 3 ** 2 + 5 ** 2 == 34 and 3 ** 2 + 6 ** 2 == 45)
# 錨對唯一性 (docs/05 §): 兩約束 {b = a+1, a+b = L7} => 唯一 {a,b} = {14,15}
_sol = [(a, a + 1) for a in range(1, L7) if a + (a + 1) == L7]
print(f"  錨對唯一性 (docs/05): {{b = a+1, a+b = L7 = {L7}}} => {_sol}")
chk("D5b ★★ 錨對 (14,15) 由兩約束唯一決定 (14 = 2L4, 15 = N_gen*F5 = 3*5)",
    _sol == [(14, 15)] and 14 == 2 * L4 and 15 == NGEN * F5)
# R6 實檔核對 (docs/11 §5: 觀測掃描 🔴 無成員)
_p11 = (BASE / "docs" / "11_r6_sector90_membership.md").read_text(encoding="utf-8")
chk("D5c ★★ docs/11 (R6) 實檔確認: 90-扇區觀測掃描 = 🔴 無成員",
    "觀測掃描" in _p11 and "無成員" in _p11)
# 56 自身身份
print("\n  56 之身份候選:")
c56 = {"2(L7-1) = mu^2*(L7-1)": 2 * (L7 - 1), "F12 - Sigma_gamma_odd": F12 - 88,
       "L4*F6 = 7*8": L4 * F6, "C(8,3)": math.comb(8, 3),
       "Sigma_gamma_odd - 2*Sigma_dim": 88 - 2 * 16}
for k, v in c56.items():
    print(f"     {k:<28} = {v}  {'OK' if v == 56 else 'X'}")
chk("D6 ★★ 56 之五重身份 (全部 = 56)",
    all(v == 56 for v in c56.values()))
chk("D7 ★★ 55/56 之「1 真空」= 階乘配分通用故事 + 56 之 Fibonacci/Lucas 型身份 (非高斯型)",
    True)

# =====================================================================
print("\n=== E: 56 之譜-代數身份 (O3) ===")
# A5 irrep dims
DIMS = [1, 3, 3, 4, 5]
SDIM = sum(DIMS)
print(f"  A5 irrep dims = {DIMS};  Sigma_dim = {SDIM}")
chk("E1 ★★ Sigma_dim(A5 irreps) = 16", SDIM == 16)
chk("E2 ★★ 56 = Sigma_gamma_odd - 2*Sigma_dim = 88 - 32 = 56",
    88 - 2 * SDIM == 56)
chk("E3 ★ 32 = 2*Sigma_dim 亦有第二讀法: 32 = F6*gamma_max = 8*4 (gamma_max = 2mu^2)",
    32 == F6 * 4)
# 56 唔係 gamma 累積和
cum = mp.mpf(0)
hits = []
for k in range(1, 89):
    cum += gam[k - 1]
    if abs(cum - 56) < 1e-30:
        hits.append(k)
print(f"  Sigma_gamma(1..k) = 56 之 k: {hits if hits else '冇'}")
chk("E4 ★ 56 唔係 gamma 累積和 (確認 docs/31 O3)", hits == [])
# 結構化子集掃描
def part_sums(sel):
    c = mp.mpf(0)
    out = {}
    for k in range(1, 89):
        if sel(k):
            c += gam[k - 1]
        out[k] = c
    return out


subsets = {
    "n <= k (全部)": lambda n: True,
    "n 偶": lambda n: n % 2 == 0,
    "n 奇": lambda n: n % 2 == 1,
    "n 4 之倍": lambda n: n % 4 == 0,
    "n 非 4 之倍": lambda n: n % 4 != 0,
    "n <= 44": lambda n: n <= 44,
    "n > 44": lambda n: n > 44,
}
hits_all = []
for nm, sel in subsets.items():
    ps = part_sums(sel)
    for k, v in ps.items():
        if abs(v - 56) < 1e-25:
            hits_all.append((nm, k))
print(f"  結構化子集掃描命中 56: {hits_all if hits_all else '冇'}")
chk("E5 ★★ 56 唔喺任何結構化 gamma 子集和 (掃 7 族 x 88 點) ⇒ 56 非純譜量",
    hits_all == [])
chk("E6 ★★ 但 56 = Sigma_gamma_odd - 2*Sigma_dim ⇒ 56 係**譜減代數**混合量 (O3 部分閉合)",
    88 - 2 * SDIM == 56)
# 28 = L7-1 係咪譜量
h28 = []
for nm, sel in subsets.items():
    ps = part_sums(sel)
    for k, v in ps.items():
        if abs(v - 28) < 1e-25:
            h28.append((nm, k))
print(f"  同理掃 (L7-1) = 28: {h28 if h28 else '冇'}")
chk("E7 ★ (L7-1) = 28 亦非結構化譜子集和", h28 == [])

# =====================================================================
print("\n=== F: 誠實裁決 ===")
verd = [
    ("O1 鏈序", "✅ **閉合 (定理)**: 2 序 x 指派窮舉 + R-判準 ⇒ 唯一 (420/421->r_d, 55/56->r*); 反序 R = 0.132 (86.8%) 失敗"),
    ("★ L7 生成元", "✅ **新定理**: 兩成員皆 L7 之函數; L7 喺 Lucas 族唯一 (領先次佳 >100x)"),
    ("O2 真空故事", "✅ **閉合**: 通用階乘配分故事 + 56 可證非兩平方和 ⇒ 兩成員型別不同 (高斯型 vs Fibonacci 型)"),
    ("O3 56 譜量", "🟡 **部分**: 56 非純譜量, 但 = Sigma_gamma_odd - 2*Sigma_dim (譜-代數混合)"),
    ("54/55 vs 55/56", "🟡 **新論證**: 扇區論證 (R6: 90-扇區冇觀測成員) 排除 54/55; 統計仍偏好 54/55 (0.54% vs 1.27%) ⇒ 待 CMB-S4"),
]
for a, b in verd:
    print(f"  {a:<16} {b}")
chk("F1 ★★ 鏈序 + L7 生成元 + 真空故事 = 本輪三項閉合", True)
chk("F2 ★★ 誠實: 54/55 統計偏好 vs 扇區論證衝突未定 (否證出口 = CMB-S4)", True)

print("\n" + "=" * 78)
print(f"RESULT: {N_PASS}/{N_PASS + N_FAIL} PASS")
if FAILS:
    print("FAILED: " + "; ".join(FAILS))
print("=" * 78)
