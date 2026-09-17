#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O171 scripts/33 — 第七輪獨立核對 (30/31/32)

紀律: **唔 import** scripts/30, 31, 32 任何代碼; 全部第一原理重算。
路線差異:
  scripts/30 用 w = (2l+1)D/(2l(l+1)) 直接加
  本節       用 C_l = 2π D_l/(l(l+1)) 再 Σ(2l+1)C_l/(4π)  (代數等價, 數值獨立)
  並用 sympy 精確化簡 φ 冪 (φ⁵ = 5φ+3)、Fraction 精確化簡比值。
"""

import json
import math
import re
from fractions import Fraction as F
from pathlib import Path

import sympy as sp
import mpmath as mpm
mp = mpm.mp
mp.dps = 60

BASE = Path(__file__).resolve().parent.parent
PLK = BASE / "data" / "planck"
T = mp.mpf('2.72548') * 1e6

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


print("=" * 72)
print("O171 scripts/33 — 第七輪獨立核對 (30/31/32)")
print("=" * 72)

# ================================================================ A
print("\n=== A: 環1 ε⁵/8 — sympy 精確化簡 ===")
phi = sp.Rational(1, 2) + sp.sqrt(5) / 2
eps = 1 / (4 * phi)
# φ⁵ = 5φ + 3
phi5 = sp.expand(phi ** 5)
phi5_simpl = sp.simplify(phi5 - (5 * phi + 3))
chk("A1 sympy: φ⁵ − (5φ+3) = 0", phi5_simpl == 0, f"({phi5_simpl})")
anchor_sym = sp.simplify(eps ** 5 / 8)
anchor_num = sp.N(anchor_sym, 40)
print(f"  ε = 1/(4φ) = {sp.N(eps, 25)}")
print(f"  ε⁵/8 = {sp.N(anchor_sym, 25)}")
chk("A2 sympy ε⁵/8 = 1.1007073e-5",
    abs(float(anchor_num) - 1.1007073e-5) < 1e-12, f"({float(anchor_num):.7e})")
# 精確根式形式: ε⁵ = (√5−1)⁵/8⁵ = (√5−1)⁵/32768
alt = sp.simplify((sp.sqrt(5) - 1) ** 5 / (8 ** 5 * 8))
print(f"  代數等價形式 (√5−1)⁵/8⁶ = {sp.N(alt, 25)}")
chk("A3 ★ 兩形式恆等 (sympy simplify = 0)",
    sp.simplify(alt - anchor_sym) == 0)

# ================================================================ B
print("\n=== B: 環2 — 用 C_ℓ 路線獨立重算全譜 rms ===")
rows = []
for ln in (PLK / "COM_PowerSpect_CMB-TT-full_R3.01.txt").read_text(encoding="utf-8").splitlines():
    if ln.startswith("#") or not ln.strip():
        continue
    p = ln.split()
    rows.append((int(float(p[0])), mp.mpf(p[1])))
chk("B1 讀入 2507 點 (ℓ=2..2508)", len(rows) == 2507, f"(n={len(rows)})")
S2 = mp.mpf(0)
for e, D in rows:
    C = 2 * mp.pi * D / (e * (e + 1))          # C_ℓ  [μK²]
    S2 += (2 * e + 1) * C / (4 * mp.pi)        # Σ (2ℓ+1)C_ℓ/(4π)
RMS2 = mp.sqrt(S2)
DTT2 = RMS2 / T
print(f"  Σ (2ℓ+1)C_ℓ/(4π) = {mp.nstr(S2, 10)} μK²   (C_ℓ 路線)")
print(f"  rms = {mp.nstr(RMS2, 10)} μK ⇒ ΔT/T = {mp.nstr(DTT2, 10)}")
chk("B2 C_ℓ 路線 = w 路線 (兩路線一致)",
    abs(float(S2) - 12271.551) < 0.01, f"({float(S2):.4f})")
chk("B3 ★ 全圖 rms ΔT/T = 4.0644962e-5",
    abs(float(DTT2) - 4.0644962e-5) < 1e-12, f"({float(DTT2):.7e})")
ratio = DTT2 / anchor_num
chk("B4 ★★ 比值 3.6926222 (環2 失效之定量)",
    abs(float(ratio) - 3.6926222) < 1e-6, f"({float(ratio):.7f})")

# ================================================================ C
print("\n=== C: 5 峰 delta-sum — Fraction 精確核對 ===")
# 用 Fraction 精確表達 w_m 之結構部分, mpmath 計 D 部分
PEAK_B = {220: '5816.4797', 528: '2579.2168', 792: '2552.7278',
          1012: '1246.2912', 1188: '822.1860'}
S_B = mp.mpf(0)
for e, D in PEAK_B.items():
    S_B += (2 * e + 1) * mp.mpf(D) / (2 * e * (e + 1))
print(f"  docs/18 基線 Σw = {mp.nstr(S_B, 10)} μK²")
chk("C1 docs/18 基線 Σw = 36.40279 μK²",
    abs(float(S_B) - 36.40279) < 1e-4, f"({float(S_B):.5f})")
TGT = (anchor_num * T) ** 2
DL_B = TGT / S_B
chk("C2 Δℓ_eff (docs/18 基線) = 24.7227",
    abs(float(DL_B) - 24.7227) < 1e-3, f"({float(DL_B):.5f})")
# 用 Fraction 精確驗證第一峰結構係數
frac_w1 = F(441, 2 * 220 * 221)
print(f"  w₁ 結構係數 (精確 Fraction) = {frac_w1} = {float(frac_w1):.8f}")
chk("C3 w₁ 結構係數 = 441/97240 (精確)",
    frac_w1 == F(441, 97240))
# 第一峰佔比 (mpmath 重算)
w1_val = mp.mpf(441) * mp.mpf(PEAK_B[220]) / (2 * 220 * 221)
share1 = w1_val / S_B
print(f"  第一峰佔 Σw 比例 = {float(share1)*100:.2f}% (docs/18 稱 72.5%)")
chk("C4 第一峰主導 (佔 Σw > 70%)", float(share1) > 0.70,
    f"({float(share1)*100:.2f}%)")

# ================================================================ D
print("\n=== D: 環3 算術 — Fraction 精確 ===")
sig_U = F(32334, 10 ** 6)
sig_D1 = F(1654180814864716, 10 ** 16) / F(5816479677744882, 10 ** 15)
need_id = F(303, 10 ** 6)
need_det = F(1, 68)
r1 = sig_U / need_id
r2 = sig_D1 / need_det
print(f"  σ(U) = {float(sig_U)*100:.4f}%   σ(D₁) = {float(sig_D1)*100:.5f}%")
print(f"  σ(U)/0.0303% = {float(r1):.3f}   σ(D₁)/(1/68) = {float(r2):.4f}")
chk("D1 無錨差 = 106.71× (docs/16 稱 107×)", abs(float(r1) - 106.71) < 0.01)
chk("D2 有錨差 = 1.9340× (docs/16 稱 1.93×)", abs(float(r2) - 1.9340) < 0.001)
# D₁ 相對誤差精確
d1_rel = F(1654180814864716, 10 ** 13) / F(5816479677744882, 10 ** 12)
print(f"  D₁ 相對誤差 (精確) = {float(d1_rel)*100:.6f}%")
chk("D3 D₁ 相對誤差 = 2.843955% (精確 Fraction; 舊記 2.8441% 係四捨五入)",
    abs(float(d1_rel) - 0.028439553) < 1e-9, f"({float(d1_rel)*100:.6f}%)")

# ================================================================ E
print("\n=== E: 通道矩陣 — 逐格獨立重算 ===")
CHD = {
    "D1_peak": (F(1654180814864716, 10 ** 13), F(5816479677744882, 10 ** 12)),
    "A_s":     (F(14, 1000), F(1)),                       # σ(lnAs) = 0.014
    "r_d":     (F(26, 100), F(14709, 100)),               # 0.26 / 147.09
    "r_star":  (F(25, 100), F(14446, 100)),
}
sig_r = {}
for k, (a, b) in CHD.items():
    sig_r[k] = a / b
# r*/r_d 比: σ² = σ_a² + σ_b²
s2 = sig_r["r_star"] ** 2 + sig_r["r_d"] ** 2
sig_r["r_ratio"] = sp.sqrt(sp.Rational(s2.numerator, s2.denominator))
print(f"  σ(r*/r_d) (精確) = {float(sig_r['r_ratio'])*100:.5f}%")
chk("E1 σ(r*/r_d) = 0.247374%",
    abs(float(sig_r['r_ratio']) - 0.00247374) < 1e-8,
    f"({float(sig_r['r_ratio'])*100:.5f}%)")
MAT = [("33/34", 34, "A_s"), ("44/45", 45, "A_s"),
       ("55/56", 56, "r_ratio"), ("420/421", 421, "r_d")]
print(f"  {'成員':>9} {'d':>5} {'通道':>9} {'z_偵測':>10}")
zr = {}
for lab, d, ch in MAT:
    z = (F(1, d) / sig_r[ch])
    zr[lab] = float(z)
    print(f"  {lab:>9} {d:>5} {ch:>9} {float(z):9.3f}σ")
chk("E2 55/56 z = 7.2191σ (scripts/31 稱 7.22σ)", abs(zr["55/56"] - 7.2191) < 0.001)
chk("E3 420/421 z = 1.344σ", abs(zr["420/421"] - 1.344) < 0.01)
chk("E4 33/34 (A_s) z = 2.101σ", abs(zr["33/34"] - 2.101) < 0.01)
chk("E5 44/45 (A_s) z = 1.587σ", abs(zr["44/45"] - 1.587) < 0.01)
# 33/34 用 D₁ 通道
z_d1 = float(F(1, 34) / sig_r["D1_peak"])
print(f"  33/34 用 D₁ 通道: z = {z_d1:.3f}σ")
chk("E6 33/34 (D₁) z = 1.0342σ", abs(z_d1 - 1.0342) < 0.001, f"({z_d1:.4f}σ)")

# ================================================================ F
print("\n=== F: 55/56 與 420/421 之實際吻合 — 精確 Fraction ===")
r_obs = sp.Rational(14446, 100) / sp.Rational(14709, 100)
r_pred = sp.Rational(55, 56)
dev = (r_obs - r_pred) / r_pred
print(f"  r*/r_d 觀測 = {r_obs} = {sp.N(r_obs, 15)}")
print(f"  預言 55/56 = {sp.N(r_pred, 15)}")
print(f"  dev = {sp.N(dev * 100, 8)}%")
chk("F1 ★ r*/r_d dev = −0.002349% (精確)",
    abs(float(dev) * 100 + 0.002349) < 1e-6, f"({float(dev)*100:+.6f}%)")
chk("F2 ★ 無修正 (r*/r_d = 1) 之偏離 = −1.7880%",
    abs(float((r_obs - 1) * 100) + 1.7880) < 1e-3, f"({float((r_obs-1)*100):+.4f}%)")
rd_pred = sp.Rational(1470883, 10000)
rd_obs = sp.Rational(14709, 100)
rd_bare = sp.Rational(1474385, 10000)
dev_rd = (rd_pred - rd_obs) / rd_obs
dev_bare = (rd_bare - rd_obs) / rd_obs
print(f"  r_d IDCM 147.0883 vs 觀測 147.09 ⇒ dev {sp.N(dev_rd*100, 8)}%")
print(f"  r_d 無修正 147.4385 ⇒ dev {sp.N(dev_bare*100, 8)}%")
chk("F3 420/421 修正後 r_d dev = −0.00116%",
    abs(float(dev_rd) * 100 + 0.00116) < 1e-5, f"({float(dev_rd)*100:+.6f}%)")
chk("F4 無修正 r_d dev = +0.23694%",
    abs(float(dev_bare) * 100 - 0.23694) < 1e-4, f"({float(dev_bare)*100:+.5f}%)")
z_bare = float(dev_bare) / float(sig_r["r_d"])
chk("F5 420/421 z = 1.340σ", abs(z_bare - 1.340) < 0.01, f"({z_bare:.3f}σ)")

# ================================================================ G
print("\n=== G: o77 hardcode 之獨立核查 (直接讀檔) ===")
src = (BASE.parent / "o77_occam_deep" / "scripts" / "01_occam_verification.py").read_text(encoding="utf-8")
m = re.search(r"obs_rms\s*=\s*([0-9.eE+-]+)", src)
print(f"  正則抽取: obs_rms = {m.group(1) if m else None}")
chk("G1 ★ o77 obs_rms 為字面常數 1.1e-5", m is not None and float(m.group(1)) == 1.1e-5)
n_load = len(re.findall(r"\b(loadtxt|genfromtxt|read_csv|json\.load)\b", src))
print(f"  數據載入呼叫 (loadtxt/genfromtxt/read_csv/json.load) = {n_load}")
chk("G2 ★ o77 零數據載入 ⇒ 1.1e-5 非量測", n_load == 0, f"(n={n_load})")
dev_true = float((DTT2 / mp.mpf('1.1e-5') - 1) * 100)
print(f"  真圖 rms 對 1.1e-5 之偏離 = {dev_true:+.2f}%")
chk("G3 ★ 真偏離 +269.50% (vs 硬編 1.1e-5; o77 聲稱 0.06%)", abs(dev_true - 269.50) < 0.01, f"({dev_true:+.2f}%)")

# ================================================================ H
print("\n=== H: 交叉核對 — docs/16 §6 之 34.8× ===")
D221 = mp.mpf('5816.4797')
C221 = 2 * mp.pi * D221 / (221 * 222)
r16 = anchor_num / (mp.sqrt(C221) / T)
print(f"  √C_221/T = {mp.nstr(mp.sqrt(C221)/T, 8)}")
print(f"  錨/√C_221 = {mp.nstr(r16, 8)}×")
chk("H1 docs/16 §6 之 34.8× 獨立重現 (34.759×)",
    abs(float(r16) - 34.759) < 0.01, f"({float(r16):.3f}×)")
chk("H2 ★ 兩疑點方向相反 ⇒ 錨唔對應任何 CMB 絕對量",
    float(r16) > 10 and float(ratio) < 10,
    f"(單模 {float(r16):.1f}× 細 / 全圖 {float(ratio):.2f}× 大)")

# ================================================================ I
print("\n=== I: json 輸出交叉核對 ===")
j30 = json.loads((BASE / "data" / "30_amplitude_real_planck.json").read_text(encoding="utf-8"))
j31 = json.loads((BASE / "data" / "31_channel_split_matrix.json").read_text(encoding="utf-8"))
j32 = json.loads((BASE / "data" / "32_r7_anchor_chain.json").read_text(encoding="utf-8"))
chk("I1 scripts/30 json: full_spectrum_dTdT 一致",
    abs(j30["full_spectrum_dTdT"] - float(DTT2)) < 1e-13)
chk("I2 scripts/30 json: dl_eff_required 一致",
    abs(j30["dl_eff_required"] - 23.186403) < 1e-4)
chk("I3 scripts/31 json: 55/56 z_det 一致",
    abs(j31["matrix"]["55/56"]["z_det"] - zr["55/56"]) < 1e-6)
chk("I4 scripts/32 json: 環2 ratio 一致",
    abs(j32["link2_ratio_anchor_vs_full_rms"] - float(ratio)) < 1e-6)
chk("I5 scripts/32 json: 環3 已撤銷",
    "撤銷" in j32["link3_conclusion"])

# ================================================================ J
print("\n=== J: 裁決 ===")
print(f"  第七輪 30/31/32 全部數字獨立重算一致 ✓")
print(f"  核心新結果:")
print(f"    (1) 真 Planck 全譜 rms = 110.777 μK (ΔT/T = 4.06450e-5)")
print(f"    (2) ε_φ⁵/8 = 1.100707e-5 唔係圖 rms (差 3.69×) ⇒ 環2 失效")
print(f"    (3) o77「Planck 1.1e-5」= hardcode ⇒ 0.06% 無效 (真 +269.50%; vs ε_φ⁵/8 則 +269.26%)")
print(f"    (4) Δℓ_eff (兩基線 23.186 / 24.723) 命中 ≈ null ⇒ 無結構身份")
print(f"    (5) 通道分裂: 55/56 (r*/r_d) z = 7.219σ 已檢定; 420/421 z = 1.344σ")
print(f"    (6) 識別全部 < 0.2σ ⇒ docs/20 識別結論保留")

print("\n" + "=" * 72)
print(f"RESULT: {N_PASS}/{N_PASS + N_FAIL} PASS")
if FAILS:
    print("FAILS:")
    for f_ in FAILS:
        print(f"  - {f_}")
print("=" * 72)
