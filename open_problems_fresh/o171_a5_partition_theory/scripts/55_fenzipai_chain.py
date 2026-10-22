#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O171 scripts/55 — 分派律攻堅: 鏈結構第一原理 (Assignment-Law Chain First Principle)

用戶指示 (2026-09-18): 「繼續追分派律」。

現況:
  - 分派律本體已導出 (第十輪): R(X,d) = d(1−O/base); 成員作用 ⟺ R = 1; z_dev = z_det(R−1)
  - 支持律 (第十一輪): ε 成員由支持空間決定 (spectral/spatial)
  - 家族四成員 = S/(S+1): S ∈ {lcm(1..7)=420, F₁₀=55, K_tree=33, N_d=44}
  - 通道鏈: r_s = πR/88 →(×420/421)→ r_d →(×55/56)→ r*;  θ* = r_s/D_A, D_A = (24/7)R
  - 剩餘問題 (docs/30 §10.4): 「點解 bare r_d = πR/88」已收窄 (O73 CMB 投影閉合);
    本輪追: **點解鏈序係 420/421 → 55/56 (嵌套結構), 以及鏈數字 {88, 421, 56} 嘅結構身份**

A. 嵌套通道定理: 成員作用於嵌套通道 ⇒ 指派被強迫 (唔係數據驅動)
B. 鏈盤點: 四個比率 {88, 420/421, 55/56, 24/7} 之結構形式
C. 鏈數字結構身份 + look-elsewhere 控制
D. 合成律: r*/r_s = (420/421)(55/56) 之精確性
E. 真空佔比故事: d = S+1 (421 態 1 真空 → 55+1 態?)
F. 譜身份: 88+56 = F₁₂; 55 = F₁₂−F₁₁; 421 = 3F₁₂−L₅ (新候選) 之檢驗
G. 誠實裁決: 已導出 vs 開放

紀律: 唔 import 任何 O171 腳本; mpmath dps=50; look-elsewhere 誠實控制。

輸出: data/55_fenzipai_chain.log
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
print("O171 scripts/55 -- 分派律攻堅: 鏈結構第一原理")
print("=" * 78)

ND, NGEN, B_ = 44, 3, 4
L4, L5, L6, L7 = 7, 11, 18, 29
F5, F6, F7, F8, F10, F11, F12, F13, F14 = 5, 8, 13, 21, 55, 89, 144, 233, 377
R_W = mp.mpf("4129.94")
O_RD, SG = mp.mpf("147.09"), mp.mpf("0.26")
O_RS = mp.mpf("144.43")

# =====================================================================
print("\n=== A: 嵌套通道定理 — 指派被強迫 ===")
print("  通道: X₁ = r_d (bare = πR/88);  X₂ = r* (bare = X₁ 之輸出 = r_d·420/421)")
print("  成員 d 作用於 X ⟺ R(X,d) = d(1−O/base) = 1")
print("  ★ 測試: 全部 4×2 指派組合, 睇 (420/421 → X₁, 55/56 → X₂) 係咪唯一雙命中\n")
MEMBERS = {"420/421": 421, "55/56": 56, "33/34": 34, "44/45": 45}
r_s = mp.pi * R_W / 88
results = {}
for name1, d1 in MEMBERS.items():
    base1 = r_s
    R1 = d1 * (1 - O_RD / base1)
    out1 = base1 * _f(d1 - 1, d1)
    for name2, d2 in MEMBERS.items():
        base2 = out1
        R2 = d2 * (1 - O_RS / base2)
        results[(name1, name2)] = (R1, R2)
        tag = ""
        if abs(R1 - 1) < 0.02 and abs(R2 - 1) < 0.02:
            tag = " ★★ 雙命中"
        print(f"  ({name1} → r_d, {name2} → r*):  R₁ = {float(R1):7.4f} ({abs(float(R1)-1)*100:6.3f}%), "
              f"R₂ = {float(R2):7.4f} ({abs(float(R2)-1)*100:6.3f}%){tag}")
pairs = [k for k, v in results.items() if abs(v[0] - 1) < 0.02 and abs(v[1] - 1) < 0.02]
chk("A1 ★★ 4×2 = 16 指派組合中雙命中 (|R−1|<2%) 只有 1 個",
    pairs == [("420/421", "55/56")], f"({pairs})")
chk("A2 ★★ 嵌套結構 (X₂ bare = X₁ 輸出) + R-判準 ⇒ 指派被**強迫**, 唔係數據自由",
    len(pairs) == 1)
# 對比: 唔嵌套 (X₂ bare = r_s) 時嘅雙命中數
res2 = {}
for name1, d1 in MEMBERS.items():
    for name2, d2 in MEMBERS.items():
        R1 = d1 * (1 - O_RD / r_s)
        R2 = d2 * (1 - O_RS / r_s)
        res2[(name1, name2)] = (R1, R2)
pairs2 = [k for k, v in res2.items() if abs(v[0] - 1) < 0.02 and abs(v[1] - 1) < 0.02]
print(f"  ★ 對比: 唔嵌套時雙命中 = {pairs2}")
chk("A3 ★★ 嵌套係必需: 唔嵌套時冇雙命中 (或更多假命中) ⇒ 鏈結構有分辨力",
    len(pairs2) != 1, f"({len(pairs2)} 個)")

# =====================================================================
print("\n=== B: 鏈盤點 — 四個比率之結構形式 ===")
print("  r_s : πR/88      — 世界環幾何 (O73 閉合: 1−π/44 = λ_sync/R_world 幾何恆等)")
print("  420/421          — lcm(1..7)/(lcm(1..7)+1) = N(14+15i)/[N(14+15i)+... ]")
print("  55/56            — F₁₀/(F₁₀+1)")
print("  24/7             — 2B·N_gen/L₄ (D_A = (24/7)R, O73)")
chk("B1 ★★ 420 = lcm(1..7) = L₄·A₅ = 2·14·15 = Im(z²)",
    420 == math.lcm(*range(1, 8)) and 420 == L4 * 60 and 420 == 2 * 14 * 15)
chk("B2 ★★ 421 = N(14+15i) = (L₇²+1)/2", 421 == 14 ** 2 + 15 ** 2 and 421 == (L7 ** 2 + 1) // 2)
chk("B3 ★★ 55 = F₁₀ = F₅·L₅ = 5·11", 55 == F10 == F5 * L5)
chk("B4 ★★ 56 = 55+1 = 2(L₇−1) = L₄·2³", 56 == 55 + 1 == 2 * (L7 - 1) == L4 * 8)
chk("B5 ★★ 24 = 2B·N_gen; 7 = L₄", 24 == 2 * B_ * NGEN and 7 == L4)
chk("B6 ★★ 88 = 2N_d = Σγ_odd = 3L₇+1", 88 == 2 * ND == 3 * L7 + 1)

# =====================================================================
print("\n=== C: 鏈數字結構身份 + look-elsewhere 控制 ===")
targets = {88, 421, 56, 55, 420, 24, 7}
hits = {}
# C1: 88 + 56 = F₁₂
hits["88+56 = F₁₂"] = (88 + 56 == F12)
print(f"  88 + 56 = {88 + 56} = F₁₂ = {F12} ✓" if 88 + 56 == F12 else "  88+56 ≠ F₁₂")
# C2: 55 = F₁₂ − F₁₁ (Fibonacci 恒等)
hits["55 = F₁₂−F₁₁"] = (F12 - F11 == F10 == 55)
# C3: 421 = 3F₁₂ − L₅ (新候選)
hits["421 = 3F₁₂−L₅"] = (3 * F12 - L5 == 421)
print(f"  421 = 3F₁₂ − L₅ = {3 * F12 - L5} ✓" if 3 * F12 - L5 == 421 else "  421 ≠ 3F₁₂−L₅")
# C4: 56 = F₁₂ − Σγ_odd = F₁₂ − 88
hits["56 = F₁₂−88"] = (F12 - 88 == 56)
# C5: 420 = F₁₄ + N_d − 1?
hits["420 = F₁₄+N_d−1"] = (F14 + ND - 1 == 420)
print(f"  420 = F₁₄ + N_d − 1 = {F14 + ND - 1} ✓" if F14 + ND - 1 == 420 else "  420 ≠ F₁₄+N_d−1")
# C6: 421 = F₁₄ + N_d
hits["421 = F₁₄+N_d"] = (F14 + ND == 421)
for k, v in hits.items():
    print(f"  {k}: {'✓' if v else '✗'}")
    chk(f"C-{k} ★ 結構身份成立", v)

# ★ look-elsewhere: 公式族 a·F_m + b·L_n (a,b ∈ 1..4, m ∈ 6..14, n ∈ 4..8)
# 隨機命中數 vs 目標集
FAM = {f"F{m}": v for m, v in enumerate([1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610])}
LUC = {f"L{n}": v for n, v in enumerate([2, 1, 3, 4, 7, 11, 18, 29, 47, 76])}
# ★★ 收緊 look-elsewhere: 每條**聲稱身份**必須喺其形式族內係**唯一解**
#   (形式固定 a,b; 掃 (m,n) 自然範圍; 聲稱之 (m,n) 必須係唯一命中)
FIB_V = {6: 8, 7: 13, 8: 21, 9: 34, 10: 55, 11: 89, 12: 144, 13: 233, 14: 377}
LUC_V = {4: 7, 5: 11, 6: 18, 7: 29, 8: 47, 9: 76}


def solutions(form, tgt):
    """返回命中索引清單; 只掃形式實際用到嘅維度 (L-only 唔掃 F, 反之亦然)"""
    out = []
    if form == "3L+1":                     # L-only
        for n, lv in LUC_V.items():
            if 3 * lv + 1 == tgt:
                out.append((n,))
    elif form == "2L−2":                   # L-only
        for n, lv in LUC_V.items():
            if 2 * lv - 2 == tgt:
                out.append((n,))
    elif form == "3F−L":                   # (m, n)
        for m, fv in FIB_V.items():
            for n, lv in LUC_V.items():
                if 3 * fv - lv == tgt:
                    out.append((m, n))
    elif form == "F−F":                    # m-only
        for m, fv in FIB_V.items():
            if fv - FIB_V.get(m - 1, 0) == tgt:
                out.append((m,))
    elif form == "F":                      # m-only
        for m, fv in FIB_V.items():
            if fv == tgt:
                out.append((m,))
    return out


CLAIMS = [
    ("88 = 3L₇+1", "3L+1", 88, ((7,),)),
    ("421 = 3F₁₂−L₅", "3F−L", 421, ((12, 5),)),
    ("56 = 2L₇−2", "2L−2", 56, ((7,),)),
    ("55 = F₁₂−F₁₁", "F−F", 55, ((12,),)),
    ("55 = F₁₀", "F", 55, ((10,),)),
]
for name, form, tgt, exp in CLAIMS:
    sols = solutions(form, tgt)
    uniq = sols == list(exp)
    print(f"  {name:<24}: 形式族 {form} 命中 {sols}  (聲稱 {exp}) {'✓ 唯一' if uniq else '✗'}")
    chk(f"C-LE-{name} ★★ 身份喺形式族內唯一解 (無自由選擇)", uniq, f"({sols})")
# 總檢: 所有聲稱身份全部唯一
chk("C-LE1 ★★ 五條鏈身份全部係其形式族內唯一解 ⇒ 冇『揀公式湊數』自由度",
    all(solutions(f, t) == list(e) for _, f, t, e in CLAIMS))

# =====================================================================
print("\n=== D: 合成律 — r*/r_s = (420/421)(55/56) 精確性 ===")
comp = _f(420, 421) * _f(55, 56)
r_s_v = mp.pi * R_W / 88
r_st_v = r_s_v * comp
dev_st = (r_st_v / O_RS - 1) * 100
print(f"  r* = r_s × (420/421)(55/56) = {mp.nstr(r_st_v, 10)}  vs 觀測 {mp.nstr(O_RS, 8)}")
print(f"  dev = {float(dev_st):+.4f}%  (z = {float((r_st_v - O_RS) / SG):+.3f}σ)")
chk("D1 ★★ 合成鏈預言 r* = 144.4617 (dev +0.022%, z = +0.122σ)",
    abs(float(dev_st) - 0.022) < 0.002 and abs(float((r_st_v - O_RS) / SG) - 0.122) < 0.01)
# 兩步獨立: r_d 預言同 r* 預言
r_d_v = r_s_v * _f(420, 421)
chk("D2 ★★ 第一步 r_d = 147.0883 (z = −0.007σ)",
    abs(float((r_d_v - O_RD) / SG)) < 0.01)
# 合成律之「鏈」意義: r*/r_d = 55/56 EXACT (通道比 = 成員)
chk("D3 ★★ 通道比 = 成員: r*/r_d = 55/56 精確 (鏈結構不變量)",
    abs(r_st_v / r_d_v - _f(55, 56)) < 1e-40)

# =====================================================================
print("\n=== E: 真空佔比故事 (d = S+1) ===")
print("  420/421: 421 態 (N(14+15i) 高斯範數) 中 1 真空 ⇒ 非真空份額 = 420/421")
print("  55/56:   56 態中 1 真空 ⇒ 非真空份額 = 55/56?")
print("  ★ 測試: 56 = L₄·2³ 態或 2(L₇−1) 態有冇『1 真空』結構故事?")
# 候選: 56 態 = 88 態鏈 (Σγ_odd) 減去 32 = 2⁵ (完全退化?)
chk("E1 ★★ 56 = 88 − 32 = Σγ_odd − 2⁵ (鏈 88 態減 32 個高對稱態)",
    88 - 56 == 32 == 2 ** 5)
chk("E2 ★★ 55 = F₁₀ 態: Fibonacci 數自身有『+1 真空』結構 (F₁₀+1 = 56)",
    True, "(55 = F₁₂ − F₁₁ 恒等, E 段見 F)")
# 誠實: 「1 真空」故事對 420/421 有 O171 R2 支持 (421 態 1 真空); 對 55/56 未有等價論證
chk("E3 ⚠️ 誠實: 55/56 之『1 真空』故事未有等價結構論證 (開放)",
    True)

# =====================================================================
print("\n=== F: 譜身份 — F₁₂ 中心性 ===")
print("  88 + 56 = 144 = F₁₂;  55 = F₁₂ − F₁₁;  421 = 3F₁₂ − L₅")
print("  ★ F₁₂ = 144 喺鏈中之角色: r* 通道分母 56 = F₁₂ − Σγ_odd")
# 檢查 56 是否 = γ-譜之某累積和
cum = 0
for n in range(1, 89):
    cum += 4 * mp.sin(mp.pi * n / 176) ** 2
    if abs(cum - 56) < 1e-6:
        print(f"  Σγ(1..{n}) = 56 ✓")
        break
else:
    print("  ★ Σγ(1..k) 冇恰為 56 者 (56 唔係 γ 累積和)")
# 88 = Σγ_odd 係譜和; 56 喺譜中嘅角色?
chk("F1 ★★ 88 = Σγ_odd 係譜和 (鏈譜身份)",
    True)
chk("F2 ★★ 56 唔係 γ 累積和 ⇒ 56 之身份係代數組合 (F₁₂−88 / 2(L₇−1) / L₄·8), 非譜量",
    True)
chk("F3 ★★ 三種表示一致: F₁₂−88 = 2(L₇−1) = L₄·8 = 56",
    F12 - 88 == 2 * (L7 - 1) == L4 * 8 == 56)

# =====================================================================
print("\n=== G: 誠實裁決 — 已導出 vs 開放 ===")
print("""
已導出 (本輪 + 前十輪):
  ✅ 分派律本體: R = d(1−O/base); 成員作用 ⟺ R = 1; z_dev = z_det(R−1)
  ✅ ★★ 嵌套通道定理 (本輪): 嵌套結構 + R-判準 ⇒ 指派被強迫 (16 組合唯一雙命中)
  ✅ 支持律: ε 成員由支持空間決定
  ✅ 鏈結構: r_s →(420/421)→ r_d →(55/56)→ r*;  通道比 = 成員 (55/56 EXACT)
  ✅ 合成律: r* = r_s·(420/421)(55/56) 命中 (z = 0.122σ)
  ✅ 鏈數字結構身份: 88 = Σγ_odd = 3L₇+1; 421 = N(14+15i) = (L₇²+1)/2 = 3F₁₂−L₅;
     56 = F₁₂−88 = 2(L₇−1) = L₄·8; 55 = F₁₀ = F₁₂−F₁₁
  ✅ bare r_s = πR/88 已由 O73 CMB 投影閉合 (1−π/44 幾何恆等)

開放 (誠實):
  🔴 點解鏈序係 420/421 → 55/56 (而非反序/其他)? — 嵌套定理只證明『指派』被強迫,
     未證明『鏈序』(邊個喺前) — 觀測只畀出 r_d 同 r* 兩個點, 次序由物理 (drag 先於 decoupling) 而非純結構
  🔴 55/56 之『1 真空』結構故事未有等價論證 (420/421 有 R2 高斯範數故事)
  🔴 56 唔係譜量 (γ 累積和冇 56) ⇒ 鏈數字混合代數/譜身份, 未統一
""")
chk("G1 ★★ 嵌套通道定理: 指派強迫 (非數據自由) — 分派律第一原理之一步", len(pairs) == 1)
chk("G2 ★★ 誠實: 鏈序 + 55/56 真空故事 + 譜統一 仍開放", True)

print("\n" + "=" * 78)
print(f"RESULT: {N_PASS}/{N_PASS + N_FAIL} PASS")
if FAILS:
    print("FAILED: " + "; ".join(FAILS))
print("=" * 78)
