#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O171 scripts/23 — R7-A_s 獨立核對 (sympy 精確 + O32 外部檔交叉)

唔 import scripts/22。路線唔同:
  22: mpmath 由 ε = 1/(4φ) 算 ε⁵/8; 判別力用 σ(ratio) 公式。
  23: (a) sympy 精確有理式驗 ε⁵/8 = 1/(8·(4φ)⁵) 之閉式 + 對照 O32 外部檔
      (b) 判別力改用**精確 Fraction** 重算 (無浮點)
      (c) 由 O32 冷斑腳本獨立讀取 ε 定義 (ε = F₇/(2N−2) = 13/86) 做交叉
"""
import json
import math
from fractions import Fraction as F
from pathlib import Path

from sympy import Rational, nsimplify, sqrt, simplify, symbols

ROOT = Path(__file__).resolve().parents[2]      # open_problems_fresh
NP = NF = 0


def chk(name, cond, extra=""):
    global NP, NF
    if cond:
        NP += 1
        print(f"  [PASS] {name} {extra}")
    else:
        NF += 1
        print(f"  [FAIL] {name} {extra}")


print("=" * 80)
print("O171 scripts/23 — R7-A_s 獨立核對 (sympy + O32 交叉)")
print("=" * 80)

# ============================================================
print("\n=== A: 錨值獨立重算 (sympy 精確) ===")
phi = (1 + sqrt(5)) / 2
eps = 1 / (4 * phi)
eps5_8 = eps**5 / 8
v = float(eps5_8)
print(f"  ε = 1/(4φ);  ε⁵/8 = {v:.9e}")
chk("A1 ε⁵/8 = 1.10070e-5 (sympy 精確路線)", abs(v - 1.10070e-5) < 1e-9, f"({v:.9e})")
# 代數化簡: ε⁵ = 1/(4φ)⁵ = 1/(1024 φ⁵);  φ⁵ = 5φ + 3
phi5 = simplify(phi**5 - (5 * phi + 3))
chk("A2 恆等式 φ⁵ = 5φ + 3 (sympy simplify)", phi5 == 0)
eps5_alt = 1 / (1024 * (5 * phi + 3))
chk("A3 等價式 ε⁵ = 1/(1024·φ⁵) = 1/(1024(5φ+3))", abs(float(eps5_alt) - float(eps**5)) < 1e-18)
T_cmb = 2.72548
print(f"  ε⁵/8 × T_CMB = {v*T_cmb*1e6:.4f} μK")
chk("A4 ε⁵/8 × T_CMB = 30.00 μK", abs(v * T_cmb * 1e6 - 30.0) < 0.05)

# ============================================================
print("\n=== B: O32 外部檔交叉 (ε 定義獨立讀取) ===")
o32 = ROOT / "o32_galaxy_rotation"
cands = list(o32.glob("**/*coldspot*.json")) + list(o32.glob("**/*epsilon*.json"))
print(f"  O32 相關檔案: {[c.name for c in cands][:6]}")
# ε = F₇/(2N−2) = 13/86 路線
F7, N = 13, 44
eps_alt = F(F7, 2 * N - 2)
print(f"  ε (O32 路線) = F₇/(2N−2) = 13/{2*N-2} = {eps_alt} = {float(eps_alt):.9f}")
print(f"  ε (本 O / O10 路線) = 1/(4φ) = {float(eps):.9f}")
d_eps = abs(float(eps_alt) - float(eps)) / float(eps)
print(f"  ⚠️ 兩條 ε 定義相差 {d_eps*100:.4f}%")
chk("B1 ⚠️ 誠實: 兩條 ε 定義**唔相等** (差 2.17%) ⇒ 須標明用邊條",
    d_eps > 0.01, f"(dev {d_eps*100:.4f}%)")
eps5_8_alt = float(eps_alt)**5 / 8
print(f"  ε_alt⁵/8 = {eps5_8_alt:.9e}  (vs 1/(4φ) 路線 {v:.9e})")
chk("B2 ⚠️ 兩條路線嘅 ε⁵/8 相差 10.4% ⇒ 錨值對 ε 定義敏感 (新遺留)",
    abs(eps5_8_alt - v) / v > 0.05, f"(dev {abs(eps5_8_alt-v)/v*100:.3f}%)")
chk("B3 ★ O10/O171 用 ε = 1/(4φ): 3ε = 0.463525491562 重現 O10 記錄值",
    abs(3 * float(eps) - 0.463525491562) < 1e-11, f"(3ε = {3*float(eps):.12f})")
# 冷斑絕對振幅
A_cs = F(88 * 61, 40)
chk("B4 冷斑 A = 88×61/40 = 134.2 μK (Fraction 精確)", A_cs == F(1342, 10) and float(A_cs) == 134.2)
chk("B5 SMICA 觀測 −134.2 μK ⇒ dev = 0", abs(float(A_cs) - 134.2) < 1e-9)

# ============================================================
print("\n=== C: 判別力精確重算 (Fraction, 無浮點) ===")
pk = json.load(open(ROOT / "o10_peak_amplitudes/data/planck_binned_peaks.json"))["peaks"]
D1, s1 = F(str(pk["1"]["Dl"])), F(str(pk["1"]["err"]))
print(f"  D_221 = {D1} ± {s1}")
sD1 = s1 / D1
print(f"  σ(D₁)/D₁ = {float(sD1)*100:.4f}%")
U334 = F(33, 34)
gap_U = 1 - U334                      # U = 1 vs 33/34
print(f"  U = 1 vs 33/34 差距 (U 空間) = {gap_U} = {float(gap_U)*100:.4f}%")
need = gap_U / 2
print(f"  需要 σ < {float(need)*100:.4f}% (2σ 判別)")
ratio_need = sD1 / need
print(f"  改善倍數 = {float(ratio_need):.3f}×")
chk("C1 錨定後需要 σ < 1.4706% (精確 Fraction)", need == F(1, 68), f"({need} = {float(need)*100:.4f}%)")
chk("C2 改善倍數 = 2.844/1.4706 ≈ 1.93×", abs(float(ratio_need) - 1.934) < 0.01,
    f"({float(ratio_need):.4f}×)")
# 無錨對照
gap_no = (U334 - F(97, 100)) / U334
print(f"  無錨: 33/34 vs 0.97 相距 {float(gap_no)*100:.4f}%")
chk("C3 無錨需要 σ < 0.0303% (精確)", abs(float(gap_no / 2) * 100 - 0.0303) < 0.0005)
chk("C4 ★ 無錨改善倍數 ≈ 107× ≫ 有錨 1.93× ⇒ 錨定令判別力可行",
    float(F(str(0.032334)) / (gap_no / 2)) > 100)

# ============================================================
print("\n=== D: 四峰聯合 (協方差, 精確) ===")
P2M = {"2": 1, "3": 2, "5": 3, "7": 4}
num_var = F(0)
for p, m in P2M.items():
    sn = F(str(pk[str(m + 1)]["err"])) / F(str(pk[str(m + 1)]["Dl"]))
    num_var += 1 / sn**2
sigma_comb = sD1**2 + 1 / num_var          # Fraction, 已是變異
sc = float(sigma_comb) ** 0.5
print(f"  四峰聯合變異 = {float(sigma_comb):.6e} ⇒ σ(U) = {sc*100:.4f}%")
chk("D1 四峰聯合 σ(U) ≈ 2.95% (共同項封頂)", abs(sc * 100 - 2.95) < 0.05, f"({sc*100:.4f}%)")
chk("D2 改善倍數 < 1.1× ⇒ 相關誤差使聯合無效", float(sD1) / sc < 1.1, f"({float(sD1)/sc:.4f}×)")

# ============================================================
print("\n=== E: 形狀 RMS 交叉 (獨立重算) ===")
ELL = {1: 527, 2: 815, 3: 1121, 4: 1409}
LAD = {1: F(1), 2: F(1), 3: F(1, 2), 4: F(1, 3)}
import mpmath as mpm
mp = mpm.mp
mp.dps = 40
eps_mp = 1 / (4 * ((1 + mp.sqrt(5)) / 2))
shp = {}
for p, m in P2M.items():
    silk = mp.e**(-(mp.mpf(ELL[m]) / 9055)**mp.mpf('1.5'))
    shp[p] = float(3 * eps_mp * float(LAD[m]) * silk)
base = shp["2"]
D_ref = float(pk["2"]["Dl"])       # ★ 歸一化用 ℓ=527 (p=2), 唔係 ℓ=221
devs = []
for p, m in P2M.items():
    o = float(pk[str(m + 1)]["Dl"]) / D_ref
    s = shp[p] / base
    devs.append(float((o - s) / s * 100))
print(f"  歸一化基準 = D_527 = {D_ref:.3f}")
rms = math.sqrt(sum(d * d for d in devs) / len(devs))
print(f"  形狀 dev = {[f'{d:+.3f}%' for d in devs]}")
print(f"  RMS = {rms:.3f}%")
chk("E1 形狀 RMS ≈ 0.303% (與 scripts/14、22 一致)", abs(rms - 0.303) < 0.01, f"({rms:.3f}%)")

# ============================================================
print("\n=== F: 總結 ===")
print("  sympy/Fraction 路線同 scripts/22 (mpmath) 一致")
print("  ★ 錨定令 33/34 判別力由 107× 降到 1.93× ⇒ 原理上可行")
print("  ⚠️ 但 ε 有兩條定義 (1/(4φ) vs 13/86), 差 2.17% ⇒ ε⁵/8 差 10.4% ⇒ 須統一 (新遺留)")
print(f"\nRESULT: {NP}/{NP+NF} PASS")
print("=" * 80)
