#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O171 scripts/35 — 第八輪獨立核對 (scripts/34)

紀律: **唔 import** scripts/34; 全部第一原理重算, 並刻意走唔同路線:
  A  rms 改由 C_l 積分路線 (D_l -> C_l -> w_l -> 累積), 並同 binned 譜交叉
  B  CV 下限改由 sympy 精確有理 + 卡方自由度推導 (唔用現成公式)
  C  窗口唯一性改用 Fraction 精確比較 + 連分數收斂子 (唔用浮點掃描)
  D  420/421 改用 Lucas 閉式 L_n = phi^n + psi^n (sympy 精確) + 模算術
"""

from pathlib import Path
from fractions import Fraction as F
import mpmath as mpm
import sympy as sp

mp = mpm.mp
mp.dps = 50

BASE = Path(__file__).resolve().parent.parent
SP_FULL = BASE / "data" / "planck" / "COM_PowerSpect_CMB-TT-full_R3.01.txt"
SP_BIN = BASE / "data" / "planck" / "COM_PowerSpect_CMB-TT-binned_R3.01.txt"

PASS = 0
FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print("  [PASS] " + name + " " + detail)
    else:
        FAIL += 1
        print("  [FAIL] " + name + " " + detail)


PHI = (1 + mp.sqrt(5)) / 2
EPS5_8 = (1 / (4 * PHI)) ** 5 / 8
T_CMB = mp.mpf("2.72548") * 1e6
L7 = 29


def load(path):
    d = {}
    for ln in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        p = s.split()
        if len(p) < 2:
            continue
        d[int(float(p[0]))] = mp.mpf(p[1])
    return d


FULL = load(SP_FULL)
BIN = load(SP_BIN)
print("  載入: full %d 點, binned %d 點" % (len(FULL), len(BIN)))

print("=" * 78)
print("A: rms 之 C_l 積分路線 (獨立重算)")
print("=" * 78)
# 路線: C_l = 2 pi D_l / (l(l+1));  w_l = (2l+1)/(4pi) C_l  =>  必須還原出 (2l+1)D/(2l(l+1))
totA = mp.mpf(0)
for l in sorted(FULL):
    Cl = 2 * mp.pi * FULL[l] / (l * (l + 1))
    wl = (2 * l + 1) / (4 * mp.pi) * Cl
    totA += wl
rmsA = mp.sqrt(totA)
print("  Sigma w = %s muK^2 ;  rms = %s muK" % (mp.nstr(totA, 10), mp.nstr(rmsA, 9)))
chk("A1 C_l 路線 rms = 110.77703 muK (同 scripts/34 之 110.77703)",
    abs(float(rmsA) - 110.77703) < 5e-5, "(%.6f)" % float(rmsA))

# 交叉: binned 譜獨立算 -- ★ 分箱 D_l 係 bin 內平均, 必須乘 bin 寬 dl
# (這正是 docs/18 之「測度問題」在实務上再現)
cents = sorted(BIN)
totB = mp.mpf(0)
for i, l in enumerate(cents):
    if i + 1 < len(cents):
        dl = mp.mpf(cents[i + 1] - l)
    else:
        dl = mp.mpf(l - cents[i - 1])
    totB += (2 * l + 1) * BIN[l] / (2 * l * (l + 1)) * dl
rmsB = mp.sqrt(totB)
lmin_bin = cents[0]
totA_same = mp.mpf(0)
for l in sorted(FULL):
    if l >= lmin_bin:
        totA_same += (2 * l + 1) * FULL[l] / (2 * l * (l + 1))
print("  binned 譜 (%d bins, l = %.1f..%d, 含 bin 寬): Sigma w = %s, rms = %s muK" %
      (len(cents), lmin_bin, max(cents), mp.nstr(totB, 8), mp.nstr(rmsB, 8)))
print("  full 譜同範圍 (l >= %.1f): Sigma w = %s, rms = %s muK" %
      (lmin_bin, mp.nstr(totA_same, 8), mp.nstr(mp.sqrt(totA_same), 8)))
# 偏差來源: 低 l 區 bin 寬 ~ l (例 l=47, dl=30), 權重 1/l 在 bin 內變化 ~12%,
# 用 bin 中心 l 代表整個 bin 會有此級偏差 —— 亦即「測度問題」
chk("A2 ★ binned(含 bin 寬) 同 full 同範圍之 Sigma w 差 < 10% (低 l bin 寬偏差)",
    abs(float(totB / totA_same) - 1) < 0.10, "(差 %+.2f%%)" % ((float(totB / totA_same) - 1) * 100))

# 目標頻帶: 用精確部分和搵唯一穿越點
cum = mp.mpf(0)
cross = []
for l in sorted(FULL):
    cum += (2 * l + 1) * FULL[l] / (2 * l * (l + 1))
    if cum >= (EPS5_8 * T_CMB) ** 2:
        cross.append(l)
        break
print("  eps^5/8 * T = %s muK;  累積 rms 首次超過佢: l = %s" %
      (mp.nstr(EPS5_8 * T_CMB, 8), cross))
chk("A3 ★ 穿越點 l = 7; 最接近者 l = 6 (dev -0.85%) ⇒ 两者同屬 l <~ 7 之低多極區",
    cross == [7], "(穿越 %s)" % cross)

# 宇宙變異: 模式數 N = Sigma (2l+1) for l = 2..6
Nmod = sum(2 * l + 1 for l in range(2, 7))
cv_pow = mp.sqrt(mp.mpf(2) / Nmod)
cv_rms = cv_pow / 2
print("  N(2..6) = %d;  CV(power) = sqrt(2/N) = %.4f%%;  CV(rms) = %.4f%%" %
      (Nmod, float(cv_pow) * 100, float(cv_rms) * 100))
chk("A4 N = 45 (精確整數)", Nmod == 45, "(%d)" % Nmod)
chk("A5 CV(rms) = 10.5407% (精確 sqrt(2/45)/2)",
    abs(float(cv_rms) * 100 - 10.5407) < 0.001, "(%.4f%%)" % (float(cv_rms) * 100))
chk("A6 ★ 全譜 rms / 目標 = 3.69262 (差 > 3.6x)",
    abs(float(rmsA / (EPS5_8 * T_CMB)) - 3.69262) < 1e-4,
    "(%.5f)" % float(rmsA / (EPS5_8 * T_CMB)))

print("=" * 78)
print("B: CV 下限之精確推導 (唔用現成公式)")
print("=" * 78)
# 對 C_l 之估計量 hat C_l = (1/(2l+1)) Sigma_m |a_lm|^2, a_lm ~ N(0, C_l)
# => 2(2l+1) hat C_l / C_l ~ chi^2_{2(2l+1)}  => Var(hat C) = 2 C^2/(2l+1)
# 分箱 (dl 個獨立 l) + 覆蓋率 fsky: 有效自由度 nu = (2l+1) dl fsky
l_, dl_, fsky_ = sp.symbols("l dl fsky", positive=True)
nu = (2 * l_ + 1) * dl_ * fsky_
var_expr = sp.simplify(2 / nu)
print("  Var(hat C)/C^2 = 2 / ((2l+1) dl fsky)   [卡方自由度 nu = (2l+1) dl fsky]")
chk("B1 公式推導 = 2/((2l+1) dl fsky)",
    sp.simplify(var_expr - 2 / ((2 * l_ + 1) * dl_ * fsky_)) == 0)
f_ideal = sp.sqrt(var_expr.subs({l_: 2000, dl_: 2000, fsky_: 1}))
f_planck = sp.sqrt(var_expr.subs({l_: 220, dl_: 220, fsky_: sp.Rational(7, 10)}))
print("  理想全天空 l=2000, dl=2000: sigma/C = %s = %.6f%%" %
      (sp.nsimplify(f_ideal), float(f_ideal) * 100))
print("  Planck l=220, dl=220, fsky=0.7: sigma/C = %.6f%%" % (float(f_planck) * 100))
chk("B2 理想下限 = 0.049994% (同 scripts/34 一致)",
    abs(float(f_ideal) * 100 - 0.049994) < 1e-5, "(%.6f%%)" % (float(f_ideal) * 100))

# 識別門檻: 分辨 d 同 d+1 => 分辨 1/d 同 1/(d+1), 差 = 1/(d(d+1)); 2 sigma 判準
print("  識別門檻 (分辨 d 同 d+1, 2 sigma): sigma < 1/(2 d(d+1))")
for d in (34, 45, 56, 421):
    req = F(1, 2 * d * (d + 1))
    print("    d=%3d -> sigma < %s = %.6f%%" % (d, req, float(req) * 100))
req34 = F(1, 2 * 34 * 35)
chk("B3 d=34 之識別門檻 = 1/2380 (精確 Fraction)",
    req34 == F(1, 2380), "(%s)" % req34)
chk("B4 ★ 1/2380 = %.6f%% < 理想 CV 下限 0.049994%% ⇒ 原理性不可達" %
    (float(req34) * 100), float(req34) < float(f_ideal))
# 所需 l
need_prod = 2 * (2 * 34 * 35) ** 2
l_need = sp.sqrt(sp.Integer(need_prod) / 2)
print("  所需 (2l+1) dl >= %d ⇒ dl = l 時 l >= %s" % (need_prod, sp.nsimplify(l_need)))
chk("B5 l_need = 2380 (精確整數, sympy)", l_need == 2380, "(%s)" % l_need)
chk("B6 ★ l_need 2380 > 2000 ⇒ d=34 亦超出 CMB 可測範圍", l_need > 2000)

print("=" * 78)
print("C: 窗口唯一性 (精確 Fraction + 連分數)")
print("=" * 78)
R_STAR, R_DRAG = F(14446, 100), F(14709, 100)
X = R_STAR / R_DRAG
print("  r*/r_d = %s = %.9f" % (X, float(X)))
sig = mp.sqrt((mp.mpf("0.25") / 144.46) ** 2 + (mp.mpf("0.26") / 147.09) ** 2)
chk("C1 r*/r_d 精確有理 = 14446/14709 = 0.982119791...",
    abs(float(X) - 0.982119791) < 1e-9, "(%.9f)" % float(X))
# 用 mpmath 精確窗界 -> Fraction 有理化 (保守: 取 1e-12 精度)
lo = mp.mpf(str(float(X))) - sig
hi = mp.mpf(str(float(X))) + sig
loF = F(int(mp.floor(lo * 10 ** 12)), 10 ** 12)
hiF = F(int(mp.ceil(hi * 10 ** 12)), 10 ** 12)
print("  1 sigma 窗 (有理化) = [%s, %s]" % (loF, hiF))
# 結構候選
FIB = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987]
LUC = [2, 1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322, 521, 843]
G = [1, 3, 4, 5, 12, 60]
CAND = sorted(set(FIB) | set(LUC) | {g * l for g in G for l in LUC}
              | {33, 44, 55, 420, 88, 176, 12, 16, 25, 60})
win = [N for N in CAND if loF <= F(N, N + 1) <= hiF]
print("  結構候選 %d 個, 落入窗內 N = %s" % (len(CAND), win))
chk("C2 ★ 窗內結構候選 = [54, 55, 60] (3 個 ⇒ 識別退化)",
    win == [54, 55, 60], "(%s)" % win)
# 連分數收斂子 (獨立路線)
cf = sp.continued_fraction_convergents(sp.continued_fraction(sp.Rational(int(round(float(X) * 10 ** 9)), 10 ** 9)))
conv = []
for i, c in enumerate(cf):
    if i > 12:
        break
    conv.append((int(c.p), int(c.q)))
print("  連分數收斂子 (p, q): %s" % conv[:10])
small = [(p, q) for p, q in conv if q <= 70 and q > 1]
print("  q <= 70 之收斂子: %s" % small)
chk("C3 ★ 55/56 係連分數收斂子 (最優有理逼近族) — 但 54/55 同樣係",
    (55, 56) in conv and (54, 55) in conv, "(%s)" % small)
# 最優逼近係邊個?
best_den = min(range(2, 200), key=lambda q: abs(F(round(float(X) * q), q) - X))
print("  分母 <= 200 之最佳逼近 = %s = %.9f (dev %.6f%%)" %
      (F(round(float(X) * best_den), best_den), float(F(round(float(X) * best_den), best_den)),
       float(abs(F(round(float(X) * best_den), best_den) - X) / X) * 100))
chk("C4 ★ 55/56 確係分母 <= 200 之最佳逼近 (對框架有利) — 但次佳 54/55 亦在 1 sigma 窗內",
    F(55, 56) == F(round(float(X) * best_den), best_den) and
    abs(float(F(54, 55) - X) / float(X)) < float(sig) * 3,
    "(最佳 = %s, 次佳 54/55 dev %.5f%%)" %
    (F(round(float(X) * best_den), best_den), float(abs(F(54, 55) - X) / X) * 100))

print("=" * 78)
print("D: 420/421 之 Lucas 閉式核對 (sympy 精確)")
print("=" * 78)
phi, psi = (1 + sp.sqrt(5)) / 2, (1 - sp.sqrt(5)) / 2
for n in (5, 7):
    Ln = sp.simplify(phi ** n + psi ** n)
    print("  L_%d = phi^%d + psi^%d = %s = %d" % (n, n, n, Ln, int(Ln)))
    chk("D1 L_%d 閉式 = %s" % (n, [11, 29][0 if n == 5 else 1]),
        int(Ln) == (11 if n == 5 else 29))
chk("D2 (L_7^2 - 1)/2 = 420 且 (L_7^2 + 1)/2 = 421 (精確)",
    (29 ** 2 - 1) // 2 == 420 and (29 ** 2 + 1) // 2 == 421)
# 模算術: 29^2 = -1 mod 421 (高斯整數範數)
chk("D3 29^2 mod 421 = -1 mod 421 = 420 (高斯整數範數身份)",
    pow(29, 2, 421) == 420, "(%d)" % pow(29, 2, 421))
# 反向: 421 係質數?
chk("D4 421 係質數 (sympy isprime)", sp.isprime(421) is True)
# 只有 L_7 = 29 令 (L^2+1)/2 落喺 421
hits = [L for L in range(1, 200) if (L * L + 1) % 2 == 0 and (L * L + 1) // 2 == 421]
chk("D5 ★ 唯一解 L = 29", hits == [29], "(%s)" % hits)
# 鏈長鎖定: R = n/(2B) 必須係 Lucas
n_ok = [n for n in range(1, 400) if (n % 8 == 0) and (n // 8) in LUC]
print("  n <= 400 令 R = n/8 in Lucas: %s" % n_ok)
chk("D6 ★ 88 in 該集且 88 = 8 * L_5 = 8 * 11", 88 in n_ok and 8 * 11 == 88)
chk("D7 ★ 88 唔係唯一 (n=8,16,24,32,56,144,232,376 亦合格) ⇒ 需 R = L_5 額外輸入",
    len(n_ok) > 1, "(%d 個)" % len(n_ok))

print()
print("=" * 78)
print("RESULT: %d/%d PASS" % (PASS, PASS + FAIL))
print("=" * 78)
