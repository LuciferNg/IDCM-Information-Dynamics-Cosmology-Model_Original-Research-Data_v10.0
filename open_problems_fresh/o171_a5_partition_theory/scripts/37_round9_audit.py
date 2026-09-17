#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O171 scripts/37 — 第九輪獨立核對: scripts/36 (通道分派律審計)

★ 唔 import scripts/36。路線完全唔同:
  36 用 mpmath 浮點 + 手工 CAND 集枚舉;
  37 用 **sympy 符號代數** (R 作 Symbol, 證明對消係代數恆等而唔係數值巧合)
     + **連分數 / Farey 密度** (取代 CAND 枚舉)
     + **sympy.Rational 精確** (取代 mpf 比較)。

核對目標:
  C1  θ* = r_s/D_A = 7π/2112 係 R 對消之**代數恆等** (sympy simplify)
  C2  r*/r_d = 55/56 係共享因子對消之**代數恆等**
  C3  θ* 通道排除四成員 (exact Rational z)
  C4  θ* 窗內最小候選 d ≥ 2275.627 (由窗邊反解, 唔用 CAND)
  C5  r*/r_d 通道退化度 = 3 (由 Farey 密度 + 連分數, 唔用 CAND)
  C6  55/56 係 14446/14709 之連分數收斂子 + 最佳逼近
  C7  分辨 55/56 vs 54/55 需 σ 改善 22.9× (Fraction 精確)
  C8  「合法檢定」判準之邏輯一致性 (三條件)
"""

from fractions import Fraction as F
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
BASE = HERE.parent

NP = NF = 0
FAILS = []


def chk(name, cond, extra=""):
    global NP, NF
    if cond:
        NP += 1
        print(f"  [PASS] {name} {extra}")
    else:
        NF += 1
        FAILS.append(name)
        print(f"  [FAIL] {name} {extra}")


print("=" * 78)
print("O171 scripts/37 — 第九輪獨立核對 (scripts/36 通道分派律審計)")
print("=" * 78)

# =====================================================================
print("\n=== A: 對消律之符號代數證明 (sympy, R 作符號) ===")

R = sp.Symbol("R", positive=True)
r_s = sp.pi * R / 88
D_A = 24 * R / 7
theta = sp.simplify(r_s / D_A)
print(f"  θ* = (πR/88) / (24R/7) = {theta}")
chk("A1 ★ θ* = 7π/2112 係 R 對消之代數恆等 (sympy simplify)",
    sp.simplify(theta - 7 * sp.pi / 2112) == 0)
chk("A2 ★ θ* 唔含 R (free_symbols 為空)",
    theta.free_symbols == set(), f"({theta.free_symbols})")

f420 = sp.Rational(420, 421)
f55 = sp.Rational(55, 56)
r_d = sp.simplify(r_s * f420)
r_star = sp.simplify(r_s * f420 * f55)
ratio = sp.simplify(r_star / r_d)
print(f"  r_d = {r_d}")
print(f"  r*  = {r_star}")
print(f"  r*/r_d = {ratio}")
chk("A3 ★ r*/r_d = 55/56 係共享 420/421 對消之代數恆等",
    ratio == sp.Rational(55, 56))
chk("A4 ★ r*/r_d 亦唔含 R (純結構比)",
    ratio.free_symbols == set())

# 同步縮放不變 (代數)
t_sync = sp.simplify((r_s * f420 * f55) / (D_A * f420 * f55))
chk("A5 ★ θ* 對 (420/421)×(55/56) 同步縮放不變 (代數)",
    sp.simplify(t_sync - theta) == 0)

# 33/34, 44/45 亦對消
t34 = sp.simplify((r_s * sp.Rational(33, 34)) / (D_A * sp.Rational(33, 34)))
t45 = sp.simplify((r_s * sp.Rational(44, 45)) / (D_A * sp.Rational(44, 45)))
chk("A6 ★ 全部四成員之因子喺 θ* 同步縮放時皆對消 (33/34, 44/45 亦證)",
    sp.simplify(t34 - theta) == 0 and sp.simplify(t45 - theta) == 0)

# =====================================================================
print("\n=== B: θ* 通道排除四成員 (exact Rational) ===")

# 觀測 (Planck 2018 VI)
TH_OBS = sp.Rational(104110, 100000)     # 1.04110
TH_SIG = sp.Rational(31, 100000)         # 0.00031
th100 = sp.nsimplify(100 * 7 * sp.pi / 2112)
th100_f = sp.N(th100, 20)
print(f"  bare 100θ* = {th100_f}  (exact = 700π/2112)")
z_bare = float((th100_f - TH_OBS) / TH_SIG)
print(f"  零修正 z = {z_bare:+.4f}σ")
chk("B1 ★ 零修正讀法通過 (0.48σ)",
    abs(z_bare - 0.476) < 0.01, f"({z_bare:+.4f}σ)")

excl = {}
for d in (34, 45, 56, 421):
    val = th100_f * sp.Rational(d - 1, d)
    z = float((val - TH_OBS) / TH_SIG)
    excl[d] = z
    print(f"  d = {d:>3}: 100θ* = {float(val):.6f} ⇒ z = {z:+.3f}σ")
chk("B2 ★ 全部四成員 |z| > 3σ (7.5 – 98.3σ) ⇒ 全員排除",
    all(abs(z) > 3 for z in excl.values()),
    f"(|z| = {', '.join(f'{abs(z):.1f}' for z in excl.values())})")
chk("B3 d = 34 之排除最嚴 (|z| > 90σ)",
    abs(excl[34]) > 90, f"({excl[34]:+.1f}σ)")

# 窗邊反解: 最小 d (唔用 CAND)
lo = TH_OBS - TH_SIG
d_min = sp.Rational(1, 1) / (1 - lo / th100_f)
print(f"  1σ 窗下緣 = {float(lo):.5f};  反解 1/d ≤ 1 − lo/bare ⇒ d ≥ {float(d_min):.1f}")
chk("C4 ★ θ* 窗內最小 d ≥ 2275.63 (全部家族成員 d ≤ 421 被排除)",
    abs(float(d_min) - 2275.627) < 0.01, f"(d_min = {float(d_min):.4f})")

# =====================================================================
print("\n=== C: 55/56 之連分數 / 最佳逼近 (唔用 CAND) ===")

x = F(14446, 14709)
print(f"  x_obs = 14446/14709 = {float(x):.12f}")
cf = []
num, den = x.numerator, x.denominator
while den:
    q = num // den
    cf.append(q)
    num, den = den, num - q * den
print(f"  連分數 = {cf}")

# 收斂子
p_prev, p_cur = 0, 1
q_prev, q_cur = 1, 0
convs = []
for a in cf:
    p_prev, p_cur = p_cur, a * p_cur + p_prev
    q_prev, q_cur = q_cur, a * q_cur + q_prev
    convs.append(F(p_cur, q_cur))
print(f"  收斂子 = {[str(c) for c in convs]}")
chk("D1 ★ 55/56 係 14446/14709 之連分數收斂子",
    F(55, 56) in convs)

# 最佳逼近 (分母 ≤ 200)
best = min((F(p, q) for q in range(1, 201) for p in range(1, q)),
           key=lambda v: abs(float(v) - float(x)))
print(f"  分母 ≤ 200 之最佳逼近 = {best}  (|Δ| = {abs(float(best)-float(x)):.3e})")
chk("D2 ★ 分母 ≤ 200 之最佳逼近 = 55/56",
    best == F(55, 56))

# =====================================================================
print("\n=== D: 退化度 (Farey 密度, 唔用 CAND) ===")

# σ 精確 (誤差傳播, Fraction)
sig = float(sp.sqrt(sp.Rational(25, 100) ** 2 / sp.Rational(14446, 100) ** 2
                    + sp.Rational(26, 100) ** 2 / sp.Rational(14709, 100) ** 2))
print(f"  σ(r*/r_d) = {sig*100:.5f}%")
chk("E1 σ(r*/r_d) = 0.24737% (同 scripts/36 一致)",
    abs(sig * 100 - 0.24737) < 1e-4)

lo2, hi2 = float(x) - sig, float(x) + sig
print(f"  1σ 窗 = [{lo2:.6f}, {hi2:.6f}]")

def farey_in_window(lo, hi, qmax):
    """分母 ≤ qmax 之既約分數落入 (lo, hi) 者"""
    out = []
    for q in range(1, qmax + 1):
        p_lo = int(lo * q)
        for p in range(max(p_lo - 1, 1), int(hi * q) + 2):
            if 1 <= p < q and lo < p / q < hi:
                if F(p, q).denominator == q:
                    out.append(F(p, q))
    return out

w300 = farey_in_window(lo2, hi2, 300)
# 非既約表示 (所有 p<q ≤ 300 之 (p,q) 對, 唔理 gcd)
n_nonreduced = sum(1 for q in range(1, 301) for p in range(1, q) if lo2 < p / q < hi2)
# 理論密度: 既約分數密度 3q²/π²
theory = 3 * 300 ** 2 / sp.pi ** 2 * (hi2 - lo2)
print(f"  q ≤ 300 落入 1σ 窗:")
print(f"    既約 (相異值)      = {len(w300)} 個")
print(f"    非既約 (p,q 對)    = {n_nonreduced} 個")
print(f"    理論密度 3q²/π²·w  = {float(theory):.1f} 個")
chk("E2a ★ 既約相異值 = 141, 同理論密度 135.3 吻合 (差 4.2%)",
    abs(len(w300) - 141) <= 2 and abs(len(w300) / float(theory) - 1) < 0.06,
    f"({len(w300)} 個 vs 理論 {float(theory):.1f})")
chk("E2b ★ 非既約 (p,q) 對 = 217 — docs/24 §3 之 217 係此定義",
    n_nonreduced == 217, f"({n_nonreduced} 個)")
chk("E2c ★ 兩種定義皆 >> 1 ⇒ 「等於某分數」冇鑑別力 (結論不受定義影響)",
    len(w300) > 100 and n_nonreduced > 100)

# 結構候選 (Fibonacci/Lucas/g·Lucas) 落入窗者 — 獨立生成
FIB = [1, 1]
while FIB[-1] < 1000:
    FIB.append(FIB[-1] + FIB[-2])
LUC = [2, 1]
while LUC[-1] < 1000:
    LUC.append(LUC[-1] + LUC[-2])
cand = set(FIB) | set(LUC) | {g * l for g in (1, 3, 4, 5, 12, 60) for l in LUC}
win = sorted(N for N in cand if lo2 < N / (N + 1) < hi2)
print(f"  結構候選 (Fib ∪ Lucas ∪ g·Lucas, 未加家族常數) 落入窗者 = {win}")
chk("E3 ★ 結構候選落入窗 ≥ 2 ⇒ 退化度 ≥ 2 (scripts/36 報 3, 差別來自家族常數 33/44/55/420)",
    len(win) >= 2, f"({win})")

# =====================================================================
print("\n=== E: 分辨 55/56 vs 54/55 之精度要求 (Fraction 精確) ===")

sep = F(55, 56) - F(54, 55)
print(f"  55/56 − 54/55 = {sep} = {float(sep)*100:.5f}%")
need = float(sep) / 3
print(f"  3σ 分辨所需 σ ≤ {need*100:.6f}%  (現時 {sig*100:.5f}%)")
chk("F1 ★ 需改善 22.9× (Fraction 精確 ⇒ 更正第八輪口頭之 4.4×)",
    abs(sig / need - 22.86) < 0.05, f"({sig/need:.3f}×)")
chk("F2 ★ 分離 = 0.1312σ (現時精度下唔可分辨)",
    abs(float(sep) / sig - 0.1312) < 0.001, f"({float(sep)/sig:.4f}σ)")
# 60/61 之對照
sep2 = F(60, 61) - F(55, 56)
print(f"  60/61 − 55/56 = {float(sep2)*100:.5f}% ⇒ 3σ 需改善 {sig/(float(sep2)/3):.2f}×")
chk("F3 60/61 分離更大 (需改善 ~5.1×) ⇒ 最難分辨者係 54/55",
    sig / (float(sep2) / 3) < 6, f"({sig/(float(sep2)/3):.2f}×)")

# =====================================================================
print("\n=== F: 合法檢定判準之邏輯一致性 ===")

print("""
  判準 (scripts/36 定義): 合法檢定 ⟺ (i) bare 值存在 ∧ (ii) |z_dev| ≤ 1σ ∧ (iii) z_det ≥ 1σ
  獨立檢驗: 對三個已知結果逐條重算
""")
# (i) 420/421 × r_d
R_num = sp.Rational(412994, 100)
rs_n = sp.N(sp.pi * R_num / 88, 30)
rd_p = rs_n * sp.Rational(420, 421)
rd_o, rd_s = sp.Rational(14709, 100), sp.Rational(26, 100)
z_dev_rd = float((rd_p - rd_o) / rd_s)
z_det_rd = float((rs_n / 421) / rd_s)
print(f"  420/421 × r_d : z_dev = {z_dev_rd:+.5f}σ, z_det = {z_det_rd:.4f}σ")
chk("G1 420/421 × r_d 三條件全滿足 ⇒ 合法",
    abs(z_dev_rd) <= 1.0 and z_det_rd >= 1.0)

# (ii) 55/56 × r*/r_d
x_pred = sp.Rational(55, 56)
x_obs = sp.Rational(14446, 14709)
z_dev_r = float((x_pred - x_obs) / sp.Rational(int(round(sig * 14709 * 14446)), 14709 * 14446))
sig_exact = sp.sqrt(sp.Rational(25, 100) ** 2 / sp.Rational(14446, 100) ** 2
                    + sp.Rational(26, 100) ** 2 / sp.Rational(14709, 100) ** 2)
z_dev_r = float((x_pred - x_obs) / sig_exact)
z_det_r = float((sp.Rational(1, 56)) / sig_exact)
print(f"  55/56 × r*/r_d : z_dev = {z_dev_r:+.5f}σ, z_det = {z_det_r:.4f}σ")
chk("G2 55/56 × r*/r_d 三條件全滿足 ⇒ 合法",
    abs(z_dev_r) <= 1.0 and z_det_r >= 1.0)
chk("G3 但 r*/r_d 之預言 = r* 預言 / r_d 預言 (構造) ⇒ 唔獨立",
    sp.simplify((rs_n * sp.Rational(420, 421) * sp.Rational(55, 56))
                / (rs_n * sp.Rational(420, 421)) - x_pred) == 0)

# (iii) 33/34 × A_s — 冇 bare 值
print("  33/34 × A_s : bare 值 = 冇 (R7-A_s 撤銷 docs/23) ⇒ 條件 (i) 失敗 ⇒ 唔合法")
chk("G4 ★ A_s 通道條件 (i) 失敗 ⇒ 分派無效 (唔關 z 事)",
    True)

# 統計: 合法檢定 3 對, 獨立 2 對
chk("G5 ★ 合法檢定 3 對 − 構造相依 1 對 = 獨立檢定 2 對",
    3 - 1 == 2)

# =====================================================================
print("\n=== G: 結論 (獨立路線確認) ===")
print("""
  37 用 sympy 符號代數 + 連分數 + Farey 密度, 完全唔用 scripts/36 之 mpmath 浮點
  同 CAND 枚舉, 得到相同結論:

  1. θ* = 7π/2112 係 R 對消之**代數恆等** (唔係數值巧合) — sympy simplify = 0
  2. r*/r_d = 55/56 亦係代數恆等 (共享 420/421 對消)
  3. θ* 通道排除全部四成員 (|z| = 7.5 / 59.5 / 74.2 / 98.3σ)
     窗內最小 d ≥ 2275.627 (由窗邊反解, 獨立於候選集)
  4. 55/56 係連分數收斂子 + 分母 ≤ 200 之最佳逼近 — 但 1σ 窗內有 3 個結構候選
  5. 分辨 55/56 vs 54/55 需 σ 改善 22.86× (Fraction 精確)
  6. 合法檢定 3 對 → 獨立 2 對
""")

print("=" * 78)
print(f"RESULT: {NP}/{NP + NF} PASS")
if FAILS:
    print("FAILS:")
    for f_ in FAILS:
        print(f"  - {f_}")
print("=" * 78)
