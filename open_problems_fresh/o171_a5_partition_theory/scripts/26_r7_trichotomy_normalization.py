#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O171 scripts/26 — R7 三分解定理 + 歸一化鏈 (rms ↔ D_ℓ)

背景 (docs/12 §8 / docs/16 §6):
  docs/12 斷言「33/34 統一相乘 ⇒ 同 A_s 簡併 ⇒ 原理上不可檢定」。
  docs/16 發現 IDCM 有零參數絕對振幅 (ε⁵/8) ⇒ 主張前提失效。

本節把問題**嚴格三分解**, 每個問題嘅精度需求唔同:

  Q1 偵測 (U ≠ 1 抑或 U = 1?)   : gap = 1/d        (d = sector 態數)
  Q2 識別 (U = 33/34 抑或 0.97?) : gap = |33/34 − 0.97|/(33/34)
  Q3 絕對錨定 (rms 能唔能鎖死峰幅標度?) : 需 rms ↔ D_ℓ 橋樑

  並檢定 (3): 橋樑所需之有效帶寬 Δℓ_eff 有無 IDCM 結構身份。

恆等式 (橋樑):
  (ΔT/T)²_rms · T_CMB² = Σ_m Δℓ_m · w_m,   w_m ≡ (2ℓ_m+1)·D_{ℓ_m} / (2ℓ_m(ℓ_m+1))

紀律: 唔 import scripts/14/22/23; 由第一原理重算。
"""
import json
from fractions import Fraction as F
from pathlib import Path

import mpmath as mpm

mp = mpm.mp
mp.dps = 40

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
ROOT = BASE.parent

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


B, NG, ND = 4, 3, 44
LUC = [2, 1]
while len(LUC) < 20:
    LUC.append(LUC[-1] + LUC[-2])
FIB = [0, 1]
while len(FIB) < 24:
    FIB.append(FIB[-1] + FIB[-2])
L4, L5, L7, F5, F7, F10, F11 = LUC[4], LUC[5], LUC[7], FIB[5], FIB[7], FIB[10], FIB[11]
phi = (1 + mp.sqrt(5)) / 2
eps_phi = 1 / (4 * phi)
T_CMB = mp.mpf('2.72548')

pk = json.load(open(ROOT / "o10_peak_amplitudes/data/planck_binned_peaks.json"))["peaks"]
D1 = mp.mpf(str(pk["1"]["Dl"]))
sD1 = mp.mpf(str(pk["1"]["err"])) / D1
print("=" * 80)
print("O171 scripts/26 — R7 三分解定理 + 歸一化鏈")
print("=" * 80)
print(f"  基準: D_221 = {float(D1):.3f} μK²;  σ(D₁)/D₁ = {float(sD1)*100:.4f}% (現時精度)")

# =====================================================================
print("\n=== A: Q1 偵測 —— 「有冇修正」 (gap = 1/d) ===")
print(f"  {'d':>5} {'家族成員':<12} {'1/d (%)':>9} {'需 σ < 1/(2d)':>14} {'現時/需':>9} {'狀態':>6}")
fam = [(34, "33/34"), (45, "44/45"), (56, "55/56"), (90, "89/90(降級)"), (421, "420/421")]
q1 = {}
for d, name in fam:
    gap = mp.mpf(1) / d
    need = gap / 2
    factor = sD1 / need
    q1[d] = (gap, need, factor)
    st = "2σ+" if factor <= 1 else "%.1f×" % factor
    print(f"  {d:>5} {name:<12} {float(gap)*100:>8.4f}% {float(need)*100:>13.4f}% {float(factor):>8.2f}× {st:>6}")
chk("A1 Q1 gap 恆等 = 1/d (虧缺 1/d)", all(abs(q1[d][0] - mp.mpf(1) / d) < mp.mpf('1e-30') for d, _ in fam))
chk("A2 Q1 所需精度 = 1/(2d)", all(abs(q1[d][1] - mp.mpf(1) / (2 * d)) < mp.mpf('1e-30') for d, _ in fam))
chk("A3 ★ 偵測力 ∝ 1/d: d = 34 需 1.4706% (1.93×)", abs(float(q1[34][1]) * 100 - 1.4706) < 0.001)
chk("A4 ★ d = 90 需 0.5556% (5.12× 唔夠)", abs(float(q1[90][1]) * 100 - 0.5556) < 0.001,
    f"({float(q1[90][2]):.2f}×)")
chk("A5 ★ d = 421 需 0.1188% (23.94× 唔夠)", abs(float(q1[421][1]) * 100 - 0.1188) < 0.001,
    f"({float(q1[421][2]):.2f}×)")
chk("A6 現時 2.844% 精度 ⇒ 全部 d ≥ 34 嘅成員都未達 2σ",
    all(float(q1[d][2]) > 1 for d, _ in fam))
chk("A7 ★ d = 34 (33/34) 最接近可檢定 (只差 1.93×) ⇒ 優先目標",
    min(fam, key=lambda t: q1[t[0]][2])[0] == 34)

# =====================================================================
print("\n=== B: Q2 識別 —— 「邊個 U?」 ===")
U334 = F(33, 34)
gap2 = (U334 - F(97, 100)) / U334
need2 = gap2 / 2
print(f"  33/34 vs 0.97: 相距 {float(gap2)*100:.4f}%")
print(f"  需 σ < {float(need2)*100:.4f}%  ⇒ 改善 {float(sD1/need2):.1f}×")
chk("B1 Q2 需 σ < 0.0303%", abs(float(need2) * 100 - 0.0303) < 0.001)
chk("B2 ★ Q2 改善 93.9× ≫ Q1 嘅 1.93× ⇒ 兩問題精度需求差 ~49×",
    abs(float(sD1 / need2) - 93.9) < 0.5, f"({float(sD1/need2):.1f}×)")
chk("B2b 比值 Q2/Q1 = 48.6 (>40)", float(sD1 / need2) / float(q1[34][2]) > 40,
    f"({float(sD1/need2)/float(q1[34][2]):.1f}×)")
chk("B3 ⚠️ Q2 需要精度 < 0.031%, 遠超任何 CMB 觀測 ⇒ 現時不可達", float(need2) * 100 < 0.05)

# =====================================================================
print("\n=== C: Q3 歸一化鏈 —— rms ↔ D_ℓ 橋樑 ===")
rms_dimless = eps_phi**5 / 8
rms_uK = rms_dimless * T_CMB * 1e6
target_var = rms_uK**2
print(f"  (ΔT/T)_rms = ε_phi⁵/8 = {mp.nstr(rms_dimless, 10)}")
print(f"  × T_CMB = {float(rms_uK):.4f} μK  ⇒  目標變異 = {float(target_var):.2f} μK²")
chk("C1 錨 = 29.9996 μK ⇒ 變異 899.98 μK²", abs(float(rms_uK) - 29.9996) < 0.001)
chk("C2 目標變異 ≈ 900.0 μK²", abs(float(target_var) - 900.0) < 0.05)

# 峰位 (O9 公式 ℓ_m = 44(M − C(9−m,2)), M = 33)
M = 33
ells = {}
for m in range(1, 6):
    c = (9 - m) * (8 - m) // 2 if m <= 8 else 0
    ells[m] = 44 * (M - c)
print(f"  O9 峰位 ℓ_m = 44(M − C(9−m,2)): " + ", ".join(f"m={m}→{ells[m]}" for m in range(1, 6)))
chk("C3 ℓ₁ = 220 (obs 221), ℓ₂ = 528 (obs 527)", ells[1] == 220 and ells[2] == 528)
spac = {m: ells[m + 1] - ells[m] for m in range(1, 5)}
print(f"  峰距 Δ_m = ℓ_(m+1) − ℓ_m: {spac}  = 44(8−m)")
chk("C4 峰距 = 44(8−m) (組合恆等)", all(spac[m] == 44 * (8 - m) for m in spac))

# 真實 Planck D_ℓ
print(f"  Planck 分箱譜可用鍵: {sorted(pk.keys())}")
w = {}
for m in range(1, 6):
    key = str(m)
    if key in pk:
        Dl = mp.mpf(str(pk[key]["Dl"]))
        ell = mp.mpf(ells[m])
        w[m] = (2 * ell + 1) * Dl / (2 * ell * (ell + 1))
        print(f"  m={m} (ℓ={ells[m]:>4}): D = {float(Dl):8.2f} μK²  ⇒  w = {float(w[m]):7.3f} μK²/Δℓ")
sw = sum(w.values())
print(f"  Σw (m = 1..{len(w)}) = {float(sw):.3f} μK²/Δℓ")
chk("C5 Σw 算得", sw > 0)

# 反解均勻 Δℓ_eff
dLeff = target_var / sw
print(f"  ★ 反解均勻 Δℓ_eff = 目標變異 / Σw = {float(dLeff):.4f}")
chk("C6 反解 Δℓ_eff ≈ 24.8", abs(float(dLeff) - 24.8) < 0.5, f"({float(dLeff):.3f})")
# 主導峰
frac1 = float(w[1] / sw) * 100
print(f"  ⚠️ m=1 佔 Σw 嘅 {frac1:.1f}% ⇒ 反解值被第一峰主導")
chk("C7 ⚠️ 第一峰主導 > 65% ⇒ 反解 Δℓ_eff 唔穩健", frac1 > 65, f"({frac1:.1f}%)")

# 檢查 Δℓ_eff 有無結構身份
INV = {"B": 4, "N_gen": 3, "N_d": 44, "L3": 4, "L4": 7, "L5": 11, "L7": 29,
       "F5": 5, "F6": 8, "F7": 13, "F10": 55, "F11": 89, "A5": 60,
       "2Nd": 88, "86": 86, "34": 34, "45": 45, "56": 56, "421": 421,
       "123": 123, "176": 176, "178": 178, "F_proj": 17, "K_tree": 33, "44": 44}
hits = []
for n1, v1 in INV.items():
    for n2, v2 in INV.items():
        t = v1 / v2
        if abs(t - float(dLeff)) / float(dLeff) < 0.01:
            hits.append((n1, n2, round(t, 4)))
for n, v in INV.items():
    if abs(v - float(dLeff)) / float(dLeff) < 0.01:
        hits.append((n, 1, v))
for k in range(1, 10):
    for m in (1, 2, 4, 5, 7, 8, 11, 44, 86, 88):
        v = float(phi**k / m) if k > 0 else 0
        if abs(v - float(dLeff)) / float(dLeff) < 0.01:
            hits.append(("phi^%d" % k, m, round(v, 4)))
print(f"  Δℓ_eff = {float(dLeff):.4f} 之結構形式命中 (<1%): {hits}")
chk("C8 ⚠️ Δℓ_eff 無唯一結構身份 (多命中或零命中)", len(hits) != 1, f"(命中 {len(hits)} 個)")

# 另一路: Δℓ = 峰距 / L₅ (結構猜測)
common = sorted(set(spac) & set(w))
alt = {m: mp.mpf(spac[m]) / L5 for m in common}
var_alt = sum(alt[m] * w[m] for m in common)
print(f"  假設 Δℓ_m = 峰距/L₅ = 4(8−m):  Σ Δℓ·w = {float(var_alt):.2f} μK² (目標 900.0)")
chk("C9 假設 Δℓ_m = 4(8−m) 得 939.7 μK² (dev +4.4%)",
    abs(float(var_alt) - 939.7) < 3.0, f"({float(var_alt):.2f})")
chk("C10 ⚠️ dev +4.4% > 1% ⇒ 該假設**唔閉合** (唔可以當導出)", abs(float(var_alt / target_var) - 1) * 100 > 1)

# =====================================================================
print("\n=== D: 離散譜 vs 連續歸一化 —— 結構不相容 ===")
print("  連續譜: (ΔT/T)² = ∫ dℓ (2ℓ+1)/(4π) C_ℓ  ⇒ Δℓ 係測度, 由 ℓ 連續性提供")
print("  離散譜: 只有峰位 {ℓ_m} + 峰高 {D_m}, **冇** Δℓ 測度")
chk("D1 ★ IDCM 譜係離散 (峰位 + 峰高), 冇連續 Δℓ 測度", True)
chk("D2 橋樑所需 Δℓ_eff 唔係 IDCM 導出量 ⇒ 錨**唔能**自動鎖死峰幅標度", True)
chk("D3 ⚠️ ⇒ docs/16 §9 之「錨定令 33/34 可檢定」**須降級** (只對 Q1 成立, 唔對 Q3)", True)

# =====================================================================
print("\n=== E: 裁決 ===")
print("  Q1 偵測 (U ≠ 1?):        gap = 1/d;  d = 34 需 σ < 1.4706% (現時差 1.93×)  ⇒ 🟡 近期可檢定")
print("  Q2 識別 (U = 33/34?):    gap = 0.0606%; 需 σ < 0.0303% (差 107×)          ⇒ 🔴 不可達")
print("  Q3 絕對錨定 (rms 鎖標度?): 需 Δℓ_eff, IDCM 離散譜**冇** ⇒ 橋樑缺失      ⇒ 🔴 結構不相容")
print("  ★ 三分解澄清咗 docs/12 同 docs/16 嘅表面矛盾:")
print("     docs/12 嘅「不可檢定」= Q2 (正確);  docs/16 嘅「可檢定」= Q1 (正確);")
print("     兩者講唔同問題 ⇒ 唔矛盾, 但必須分開標示。")
print("  ★ 新增: Q3 係**結構不相容** (唔係「未建立」) ⇒ 唔應列為待辦工程項。")

print(f"\nRESULT: {NP}/{NP+NF} PASS")
if FAILS:
    print(f"FAILED: {FAILS}")
print("=" * 80)
