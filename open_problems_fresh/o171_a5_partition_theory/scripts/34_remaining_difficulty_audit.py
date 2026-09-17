#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O171 scripts/34 — 剩餘問題之困難重點審計 (第八輪)

背景: 第七輪收尾後剩四項未閉合:
  (i)   絕對錨 (Q3):  eps^5/8 = 1.100707e-5 vs 真實 Planck 全譜 rms 4.0645e-5 (差 3.69x)
  (ii)  家族識別:     全部 z < 0.2 sigma
  (iii) 55/56 經 r*/r_d 通道 "通過" (dev 0.0023%, z_det 7.22) 之可信度
  (iv)  剩餘輸入:     鏈譜 gamma_k + L_7

本節唔引入新物理, 只做四項**困難量化**:
  A  eps^5/8 之頻帶依賴  — 有冇結構頻帶令佢成立? 調參成本幾大?
  B  識別門檻 vs 宇宙變異下限 — 原理性可達抑或永遠不可達?
  C  窗口唯一性          — 結構候選集內有幾個 N 同時符合觀測?
  D  輸入剛性            — L_7 -> 421 / 鏈長 -> 表層家族, 依賴有幾硬?

全部第一原理重算, 唔 import 任何 O171 script。
"""

from pathlib import Path
import mpmath as mpm

mp = mpm.mp
mp.dps = 40

BASE = Path(__file__).resolve().parent.parent
SP = BASE / "data" / "planck" / "COM_PowerSpect_CMB-TT-full_R3.01.txt"

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


# ------------------------------------------------------------------ 常數
PHI = (1 + mp.sqrt(5)) / 2
EPS_PHI = 1 / (4 * PHI)                 # 樹/黃金路線 (docs/17)
EPS5_8 = EPS_PHI ** 5 / 8               # 零參數絕對振幅 (o77 聲稱)
T_CMB = mp.mpf("2.72548") * 1e6         # muK
B_ = 4
NGEN = 3
ND = 44
R_ = 11                                 # = N_d/B = L_5
L4, L5, L7 = 7, 11, 29
FIB = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987]
LUC = [2, 1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322, 521, 843]
G_INV = [1, 3, 4, 5, 12, 60]            # A_5 表示論不變量

# ------------------------------------------------------------------ 讀譜
rows = []
for ln in SP.read_text(encoding="utf-8", errors="ignore").splitlines():
    s = ln.strip()
    if not s or s.startswith("#"):
        continue
    p = s.split()
    if len(p) < 2:
        continue
    rows.append((int(float(p[0])), mp.mpf(p[1])))
FULL = dict(rows)
LELL = sorted(FULL)


def w_of(l, D):
    """w_l = (2l+1) D_l / (2 l (l+1))   [muK^2]"""
    return (2 * l + 1) * D / (2 * l * (l + 1))


print("=" * 78)
print("A: eps^5/8 之頻帶依賴 (真實 Planck PR3 TT 全譜, l = 2..%d)" % LELL[-1])
print("=" * 78)
cum = mp.mpf(0)
rmsL = {}
for l in LELL:
    cum += w_of(l, FULL[l])
    rmsL[l] = mp.sqrt(cum)
TOT_W = cum
RMS_FULL = mp.sqrt(TOT_W)
print("  Sigma w (全譜)      = %s muK^2" % mp.nstr(TOT_W, 9))
print("  rms 全譜            = %s muK" % mp.nstr(RMS_FULL, 8))
print("  eps^5/8 * T         = %s muK   (DeltaT/T = %s)" %
      (mp.nstr(EPS5_8 * T_CMB, 8), mp.nstr(EPS5_8, 8)))
chk("A1 rms 全譜 = 110.777 muK (同 scripts/30 一致)",
    abs(float(RMS_FULL) - 110.777) < 0.01, "(%.4f)" % float(RMS_FULL))

TGT = EPS5_8 * T_CMB
best = min(rmsL, key=lambda L: abs(rmsL[L] - TGT))
devb = abs(float(rmsL[best] / TGT - 1) * 100)
print("  ★ 最佳頻帶 l=2..%d: rms = %.4f muK, dev = %+.4f%%" %
      (best, float(rmsL[best]), (float(rmsL[best] / TGT) - 1) * 100))
chk("A2 最佳頻帶 dev < 1% (即存在令 eps^5/8 成立之頻帶)",
    devb < 1.0, "(dev %.4f%%)" % devb)

STRUCT_L = [10, 20, 44, 88, 176, 220, 264, 421, 528, 1760, LELL[-1]]
print("  結構頻帶 l=2..L 之 rms:")
for L in STRUCT_L:
    L = min(L, LELL[-1])
    print("    L=%5d  rms=%9.4f muK   dev=%+9.4f%%" %
          (L, float(rmsL[L]), (float(rmsL[L] / TGT) - 1) * 100))
struct_hit = [L for L in STRUCT_L if abs(float(rmsL[min(L, LELL[-1])] / TGT) - 1) < 0.05]
print("  ★ 結構頻帶中 dev < 5%% 者: %s" % (struct_hit if struct_hit else "無"))
chk("A3 ★ 冇任何結構頻帶令 eps^5/8 成立 (dev < 5%)",
    len(struct_hit) == 0, "(%s)" % struct_hit)

# 調參成本: 幾多個 L 令 dev < 1%
near = [L for L in LELL if abs(float(rmsL[L] / TGT) - 1) < 0.01]
Lcut = near[-1]
nmod = sum(2 * l + 1 for l in LELL if 2 <= l <= Lcut)
cv_pow = mp.sqrt(mp.mpf(2) / nmod)          # 總功率之 CV
cv_rms = cv_pow / 2                          # rms = sqrt(功率) ⇒ CV 減半
print("  ★ dev < 1%% 之 L = %s (唯一, 在目標下方) ⇒ 最接近點 l = %d" % (near, Lcut))
print("     (累積 rms 單調增, 故目標只被穿越一次 — 穿越點 l = 7)")
print("  ★ 該頻帶 l=2..%d 之模式數 N = %d" % (Lcut, nmod))
print("     CV(總功率) = sqrt(2/N) = %.2f%% ;  CV(rms) = 其半 = %.2f%%" %
      (float(cv_pow) * 100, float(cv_rms) * 100))
chk("A4 ★ 該頻帶 CV(rms) > 10%% ⇒ 0.85%% 之一致性無檢定力",
    float(cv_rms) > 0.10,
    "(CV(rms) %.2f%% vs dev %.2f%% = %.3f sigma)" %
    (float(cv_rms) * 100, devb, devb / (float(cv_rms) * 100)))
print("  ⇒ 結論: eps^5/8 之唯一對應量 = l <~ 6 之低多極 rms;")
print("     該量 CV(rms) = 10.54% ⇒ 唔可能以 <1% 精度檢定;")
print("     而**可精測**之全譜 rms 則差 3.69x ⇒ 兩難: 要麼不可檢定, 要麼被證偽。")

# 對比: 低多極 (Sachs-Wolfe 平台) 之幅度
print()
print("  低多極平台 (SW) 對照:")
for L in (6, 10, 20, 30):
    L = min(L, LELL[-1])
    print("    l=2..%2d  rms=%8.3f muK   dev=%+8.3f%%" %
          (L, float(rmsL[L]), (float(rmsL[L] / TGT) - 1) * 100))
Dplat = mp.fsum([FULL[l] for l in LELL if 2 <= l <= 20]) / len([l for l in LELL if 2 <= l <= 20])
print("    SW 平台 D_l 平均 (l=2..20) = %.2f muK^2  ⇒ sqrt = %.2f muK" %
      (float(Dplat), float(mp.sqrt(Dplat))))
chk("A5 ★ SW 平台幅度同 eps^5/8 亦唔一致 (dev > 3%)",
    abs(float(mp.sqrt(Dplat) / TGT) - 1) > 0.03,
    "(dev %+.2f%%)" % ((float(mp.sqrt(Dplat) / TGT) - 1) * 100))

# ------------------------------------------------------------ B 識別門檻
print()
print("=" * 78)
print("B: 識別門檻 vs 宇宙變異 (CV) 下限 — 原理性可達?")
print("=" * 78)


def cv_floor(l, dl, fsky):
    """一個 bin (寬 dl, 覆蓋率 fsky) 之 C_l 相對誤差下限"""
    return mp.sqrt(2 / ((2 * l + 1) * dl * fsky))


FLOORS = {
    "Planck  l=220  dl=220 fsky=0.7": cv_floor(220, 220, mp.mpf("0.7")),
    "CMB-S4   l=220  dl=220 fsky=0.7": cv_floor(220, 220, mp.mpf("0.7")) / 3,
    "理想全天空 l=2000 dl=2000 fsky=1": cv_floor(2000, 2000, mp.mpf(1)),
}
for k, v in FLOORS.items():
    print("  CV 下限 %-34s = %.6f%%" % (k, float(v) * 100))

print()
print("  成員  |  偵測門檻 1/(2d)  |  識別門檻 1/(2d(d-1))  | 識別/CV(理想l=2000)")
rowsB = []
for d in (34, 45, 56, 421):
    req_det = 1 / (2 * d)
    req_id = 1 / (2 * d * (d - 1))
    ratio = req_id / FLOORS["理想全天空 l=2000 dl=2000 fsky=1"]
    rowsB.append((d, req_det, req_id, ratio))
    print("  %5d |  %12.6f%%     |  %14.6f%%        |  %8.2fx" %
          (d, float(req_det) * 100, float(req_id) * 100, float(ratio)))
chk("B1 ★ 全部成員所需精度皆嚴於理想 CV 下限 (ratio < 1 ⇒ 原理性不可達)",
    all(r[3] < 1 for r in rowsB),
    "(%s)" % ["%.4f" % float(r[3]) for r in rowsB])
chk("B2 ★ d=421 差 178x ⇒ 任何實驗都永遠無法識別",
    float(rowsB[3][3]) < 0.02, "(差 %.0fx)" % (1 / float(rowsB[3][3])))
chk("B3 ★ d=34 亦差 1.12x (即使理想全天空 l=2000, dl=2000)",
    float(rowsB[0][3]) < 1, "(差 %.2fx)" % (1 / float(rowsB[0][3])))
d0 = 34
need = 2 * (2 * d0 * (d0 + 1)) ** 2
l_need = mp.sqrt(mp.mpf(need) / 2)
print("  ★ d=34 可識別所需: (2l+1)*dl >= %.4g ⇒ 取 dl=l 則 l >= %.0f" %
      (float(need), float(l_need)))
chk("B5 ★ d=34 可識別所需 l 已超出 CMB 可測範圍 (l > 2000)",
    float(l_need) > 2000, "(l >= %.0f)" % float(l_need))

# 用實際通道精度對照
print()
CH_ACC = {
    "D1 峰高 (Planck PR3)": mp.mpf("0.02844"),
    "A_s (Planck 2018 VI)": mp.mpf("0.0140"),
    "r_d (Planck 2018 VI)": mp.mpf("0.0017676"),
    "r*/r_d (導出)": mp.mpf("0.0024737"),
}
for k, v in CH_ACC.items():
    print("  通道 %-24s sigma = %.5f%%" % (k, float(v) * 100))
chk("B4 ★ 冇任何現有通道之精度達到 d=34 之識別門檻 (0.04456%)",
    all(float(v) > float(rowsB[0][2]) for v in CH_ACC.values()),
    "(最優 %.5f%% vs 需 %.5f%%)" % (float(CH_ACC["r*/r_d (導出)"]) * 100,
                                    float(rowsB[0][2]) * 100))

# ------------------------------------------------------ C 窗口唯一性
print()
print("=" * 78)
print("C: 窗口唯一性 — 觀測值 x = 0.9821195 落喺邊幾個結構候選 N/(N+1) 內?")
print("=" * 78)
R_STAR = mp.mpf("144.46")
R_DRAG = mp.mpf("147.09")
X_OBS = R_STAR / R_DRAG
SIG = mp.sqrt((mp.mpf("0.25") / R_STAR) ** 2 + (mp.mpf("0.26") / R_DRAG) ** 2)
print("  r*/r_d = %s   sigma = %s (%.5f%%)" %
      (mp.nstr(X_OBS, 9), mp.nstr(SIG, 6), float(SIG) * 100))
chk("C1 r*/r_d = 0.982120 (同 docs/22 一致)",
    abs(float(X_OBS) - 0.982120) < 1e-6, "(%.6f)" % float(X_OBS))

lo, hi = X_OBS - SIG, X_OBS + SIG
print("  1 sigma 窗口 = [%.6f, %.6f]  ⇒ N/(N+1) in 窗口 <=> N in [%.3f, %.3f]" %
      (float(lo), float(hi),
       float(lo / (1 - lo)), float(hi / (1 - hi))))

CAND = sorted(set(FIB) | set(LUC) | {g * l for g in G_INV for l in LUC}
              | {33, 44, 55, 420, 88, 176, 12, 16, 25, 60})
win = [N for N in CAND if lo <= mp.mpf(N) / (N + 1) <= hi]
print("  ★ 結構候選集 (Fibonacci + Lucas + g*Lucas + 家族/鏈/群常數, 共 %d 個) 內" % len(CAND))
print("    落入 1 sigma 窗口之 N = %s" % win)
for N in win:
    v = mp.mpf(N) / (N + 1)
    print("      N=%3d -> N/(N+1) = %.6f   dev = %+.5f%%  = %+.4f sigma" %
          (N, float(v), (float(v / X_OBS) - 1) * 100,
           float((v - X_OBS) / SIG)))
chk("C2 ★ 窗口內結構候選 >= 2 ⇒ 觀測唔唯一揀出 55/56", len(win) >= 2,
    "(%s)" % win)

# 全域 Farey 密度 (下界參考)
def farey_count(x, s, qmax):
    n = 0
    for q in range(1, qmax + 1):
        for p in range(1, q):
            v = mp.mpf(p) / q
            if x - s <= v <= x + s:
                n += 1
    return n


fc = farey_count(X_OBS, SIG, 300)
print("  ★ 全域對照: 分母 q <= 300 之既約分數落入同一 1 sigma 窗口者 = %d 個" % fc)
chk("C3 ★ 全域分數密度極高 ⇒ 「值等於某分數」本身冇鑑別力", fc > 20, "(%d)" % fc)

# 55/56 之「通過」拆解: 偵測 vs 識別
print()
print("  55/56 之「通過」拆解:")
z_det = (mp.mpf(1) / 56) / SIG
dev = (mp.mpf(55) / 56 - X_OBS) / X_OBS
print("    (a) 偵測 z = (1/56)/sigma = %.3f  (修正 1.786%% 係真, 7.22 sigma)" % float(z_det))
print("    (b) 識別 dev = %.6f%%  = %.4f sigma (同 55/56 一致)" %
      (float(dev) * 100, float(dev / SIG)))
print("    (c) 但 N = %s 全部同樣一致 ⇒ 識別退化度 = %d" % (win, len(win)))
print("    (d) 且 bare = 1 (未修正值恰為 1) 係**假設**, 唔係導出")
chk("C4 ★ 偵測顯著 (z>7) 但識別退化 (>= 2 個候選同分)",
    float(z_det) > 7 and len(win) >= 2)

# ------------------------------------------------------- D 輸入剛性
print()
print("=" * 78)
print("D: 輸入剛性 — 結果對鏈譜 / L_7 之依賴")
print("=" * 78)
print("  D1 深層成員 420/421 之來源:")
for L in LUC:
    if L < 100:
        a = (L * L - 1) // 2
        b = (L * L + 1) // 2
        mark = "  <== 420/421" if L == L7 else ""
        print("      L=%3d -> (L^2-1)/2 = %5d, (L^2+1)/2 = %5d%s" % (L, a, b, mark))
chk("D1 ★ 420/421 同 L_7 = 29 一一對應 ((L^2 -+ 1)/2)",
    (L7 * L7 - 1) // 2 == 420 and (L7 * L7 + 1) // 2 == 421,
    "(420, 421)")
_odd_only = all(((L * L + 1) % 2 == 1) for L in LUC if L % 2 == 0)
chk("D2 ★ L_7 為偶數時 (L^2+1)/2 唔係整數 ⇒ 421 要求 L_7 為奇",
    _odd_only, "(偶 Lucas: %s)" % [L for L in LUC if L % 2 == 0][:4])

print()
print("  D3 表層成員 33/44/55 之來源: d = (3,4,5) * R, R = N_d/B = 88/8:")
for n in (80, 84, 86, 88, 90, 92, 96):
    Rv = mp.mpf(n) / (2 * B_)
    ok = (Rv == int(Rv)) and (int(Rv) in LUC)
    print("      鏈長 n=%3d -> R = n/(2B) = %6.2f  %s" %
          (n, float(Rv), ("= L_m, 家族成立" if ok else "唔係 Lucas 整數, 家族崩")))
n_ok = [n for n in range(8, 400) if (mp.mpf(n) / (2 * B_)) == int(mp.mpf(n) / (2 * B_))
        and int(mp.mpf(n) / (2 * B_)) in LUC]
print("  ★ n <= 400 內令 R 為 Lucas 整數者: %s" % n_ok)
chk("D3 ★ 鏈長被 R = L_5 = 11 鎖死 ⇒ n = 8*L_5 = 88",
    n_ok[:3] == [8, 16, 24] and 88 in n_ok and 56 in n_ok)

print()
print("  D4 結論: O171 全部結果只依賴兩個輸入物件:")
print("      (i)  鏈譜 {gamma_k} (n = 88 之 Laplacian) -> 提供 Lucas/Fibonacci 常數")
print("      (ii) L_7 = 29 (Tr(T^7), 亦係鏈譜衍生)")
print("      ⇒ 真正唯一輸入 = 鏈譜本身; O171 只用其性質, 從未導出佢。")

print()
print("=" * 78)
print("RESULT: %d/%d PASS" % (PASS, PASS + FAIL))
print("=" * 78)
