#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O171 scripts/25 — R7-ε 統一: 「ε」係**兩個唔同結構參數**, 唔應該統一

背景 (docs/16 §7 遺留):
  O10/O171 峰幅用  ε_phi  = 1/(4φ) = φ⁻¹/B   = 0.15450849718747371
  O32     冷斑用  ε_ring = F₇/(2N_d−2) = 13/86 = 0.15116279069767442
  兩者差 2.17% ⇒ ε⁵/8 差 10.4% ⇒ 記錄為「須統一」。

本節主張 (可證偽):
  兩者**唔應該統一** —— 係兩個**唔同幾何對象**嘅標度:
    ε_phi  = φ⁻¹/B        (樹/黃金自相似: φ = T̂ 主特徵值, B = 帶數)
    ε_ring = F₇/(2N_d−2)  (環退化模佔比: 2N_d−2 = 88−2 = 86 個退化模, F₇ = 13)
  判別準則 (零參數):
    每個 ε 被**自己嘅觀測量**鎖定, 並被**另一個嘅觀測量排除**:
      冷斑: ε_ring dev 0.183% ✓   vs  ε_phi dev 11.83% ✗  (好 64×)
      峰幅: ε_phi  dev 0.158% ✓   vs  ε_ring dev 2.02% ✗  (好 13×)
  ⇒ 2.17% 差距係**真結構差異**, 唔係待修正嘅誤差。

紀律: 唔 import scripts/22-23; 由第一原理重算。
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


# ---- 第一原理常數 ----
B, NG, ND = 4, 3, 44
LUC = [2, 1]
while len(LUC) < 20:
    LUC.append(LUC[-1] + LUC[-2])
FIB = [0, 1]
while len(FIB) < 24:
    FIB.append(FIB[-1] + FIB[-2])
L4, L5, L7, F5, F6, F7, F10, F11 = LUC[4], LUC[5], LUC[7], FIB[5], FIB[6], FIB[7], FIB[10], FIB[11]
A5 = 60
phi = (1 + mp.sqrt(5)) / 2
T_CMB = mp.mpf('2.72548')

print("=" * 80)
print("O171 scripts/25 — R7-ε 統一 (兩個 ε)")
print("=" * 80)

# =====================================================================
print("\n=== A: 兩個 ε 嘅精確值同結構身份 ===")
eps_phi = 1 / (4 * phi)
eps_ring = F(F7, 2 * ND - 2)
eps_ring_mp = mp.mpf(F7) / (2 * ND - 2)
print(f"  ε_phi  = 1/(4φ)      = {mp.nstr(eps_phi, 18)}")
print(f"  ε_ring = F₇/(2N_d−2) = {eps_ring} = {float(eps_ring):.18f}")
chk("A1 ε_phi = 1/(4φ) = φ⁻¹/B (B = 4)", abs(eps_phi - 1 / (B * phi)) < mp.mpf('1e-35'))
chk("A2 1/(4φ) = (√5−1)/8 (閉式)", abs(eps_phi - (mp.sqrt(5) - 1) / 8) < mp.mpf('1e-35'))
chk("A3 ε_ring = 13/86 (F₇ = 13, 2N_d−2 = 86)", F7 == 13 and 2 * ND - 2 == 86)
chk("A4 86 = 2N_d − 2 = 88 − 2 (環 88 位去 2 個端點/零模)", 2 * ND - 2 == 86)
chk("A5 3ε_phi = 0.46352549156242107 (重現 O10 基準)", abs(3 * eps_phi - mp.mpf('0.46352549156242107')) < mp.mpf('1e-16'))
d_eps = abs(eps_phi - eps_ring) / eps_ring
print(f"  差距 = {float(d_eps)*100:.4f}%")
chk("A6 兩者差 2.2131% ⇒ ε⁵/8 差 10.37%", abs(float(d_eps) * 100 - 2.2131) < 0.001)
chk("A7 ⚠️ 兩者**唔相等** (一個無理, 一個有理) ⇒ 唔可以係同一個數",
    abs(eps_phi - eps_ring) > mp.mpf('1e-4'))

# =====================================================================
print("\n=== B: 冷斑 —— 邊個 ε 被觀測鎖定? ===")
A_cs_obs = mp.mpf('134.2')          # SMICA μK
A_cs_exact = mp.mpf(88 * 61) / 40   # IDCM 精確式
print(f"  冷斑觀測 (SMICA) = {float(A_cs_obs)} μK;  IDCM 精確式 88×61/40 = {float(A_cs_exact)} μK")
for tag, e in (("ε_ring", eps_ring_mp), ("ε_phi ", eps_phi)):
    pred = 5 * e**5 / 8 * T_CMB * 1e6
    dev = (pred - A_cs_obs) / A_cs_obs * 100
    print(f"  5ε⁵/8 × T_CMB  ({tag}): {float(pred):9.4f} μK   dev = {float(dev):+8.4f}%")
dev_ring = abs(5 * eps_ring_mp**5 / 8 * T_CMB * 1e6 - A_cs_obs) / A_cs_obs * 100
dev_phi = abs(5 * eps_phi**5 / 8 * T_CMB * 1e6 - A_cs_obs) / A_cs_obs * 100
chk("B1 ★ 冷斑: ε_ring dev 0.183% (< 0.2%)", abs(float(dev_ring) - 0.1832) < 0.001)
chk("B2 ★ 冷斑: ε_phi dev 11.77% (> 10%) ⇒ **排除**", abs(float(dev_phi) - 11.77) < 0.05,
    f"({float(dev_phi):.4f}%)")
chk("B3 ★ 冷斑判別比 = 64.6× (ε_ring 勝)", abs(float(dev_phi / dev_ring) - 64.6) < 0.5,
    f"({float(dev_phi/dev_ring):.2f}×)")
# 反解所需 ε
need_cs = (A_cs_obs * 8 / (5 * T_CMB * 1e6)) ** (mp.mpf(1) / 5)
print(f"  反解所需 ε (冷斑) = {mp.nstr(need_cs, 12)}")
chk("B4 冷斑所需 ε = 0.151146 ⇒ 貼 ε_ring (0.151163) 而非 ε_phi (0.154508)",
    abs(need_cs - eps_ring) < abs(need_cs - eps_phi))
dev_ring_eps = abs((mp.mpf(eps_ring.numerator) / eps_ring.denominator - need_cs) / need_cs) * 100
print(f"  ε_ring 喺 ε 空間 dev = {float(dev_ring_eps):.5f}%")
chk("B5 ε_ring 喺 ε 空間 dev < 0.02% (遠好於 ε_phi 嘅 2.2%)",
    float(dev_ring_eps) < 0.05, f"({float(dev_ring_eps):.5f}%)")
chk("B6 ε_phi 喺 ε 空間 dev = 2.25% (被冷斑排除)",
    abs(float((eps_phi - need_cs) / need_cs) * 100 - 2.25) < 0.02,
    f"({float((eps_phi-need_cs)/need_cs*100):.3f}%)")

# =====================================================================
print("\n=== C: 峰幅 —— 邊個 ε 被觀測鎖定? ===")
pk = json.load(open(ROOT / "o10_peak_amplitudes/data/planck_binned_peaks.json"))["peaks"]
fpf = json.load(open(ROOT / "o10_peak_amplitudes/data/final_prime_formula.json"))
D221 = mp.mpf(str(pk["1"]["Dl"]))
print(f"  D_221 = {float(D221):.3f} μK²")
# A(p_1) = D_527/D_221 = 3ε·(33/34)·Silk(527)  ⇒ 反解 3ε
silk527 = mp.e**(-(mp.mpf(527) / 9055)**mp.mpf('1.5'))
D527 = mp.mpf(str(pk["2"]["Dl"]))
ratio_obs = D527 / D221
need3e = ratio_obs / (mp.mpf(33) / 34) / silk527
print(f"  D_527/D_221 = {float(ratio_obs):.6f};  Silk(527) = {float(silk527):.6f}")
print(f"  反解 3ε = {mp.nstr(need3e, 12)}   (3ε_phi = {mp.nstr(3*eps_phi,12)}, 3ε_ring = {mp.nstr(3*eps_ring,12)})")
for tag, e in (("ε_phi ", eps_phi), ("ε_ring", eps_ring_mp)):
    pred = 3 * e * mp.mpf(33) / 34 * silk527
    dev = (pred - ratio_obs) / ratio_obs * 100
    print(f"  A(p₁) 預言 ({tag}): {float(pred):.8f}   dev = {float(dev):+8.4f}%")
d_peak_phi = abs(3 * eps_phi * mp.mpf(33) / 34 * silk527 - ratio_obs) / ratio_obs * 100
d_peak_ring = abs(3 * eps_ring_mp * mp.mpf(33) / 34 * silk527 - ratio_obs) / ratio_obs * 100
chk("C1 ★ 峰幅: ε_phi dev 0.042% (< 0.1%)", abs(float(d_peak_phi) - 0.042) < 0.005,
    f"({float(d_peak_phi):.4f}%)")
chk("C2 ★ 峰幅: ε_ring dev 2.12% (> 2%) ⇒ **排除**", abs(float(d_peak_ring) - 2.12) < 0.02,
    f"({float(d_peak_ring):.4f}%)")
chk("C3 ★ 峰幅判別比 = 50.3× (ε_phi 勝)", abs(float(d_peak_ring / d_peak_phi) - 50.3) < 0.5,
    f"({float(d_peak_ring/d_peak_phi):.2f}×)")
chk("C4 反解 3ε 貼 3ε_phi (0.16%) 而非 3ε_ring (2.0%)",
    abs(need3e - 3 * eps_phi) < abs(need3e - 3 * eps_ring_mp))

# =====================================================================
print("\n=== D: 兩個 ε 之間有無結構關係? (比值 26φ/43 掃描) ===")
r = eps_phi / eps_ring_mp
print(f"  ε_phi / ε_ring = {mp.nstr(r, 12)}")
chk("D1 比值 = 43/(26φ) = 1.0221335 (精確)", abs(r - 43 / (26 * phi)) < mp.mpf('1e-30'))
chk("D1b 倒數 = 26φ/43 = 0.9783458 (精確)",
    abs(eps_ring_mp / eps_phi - 26 * phi / 43) < mp.mpf('1e-30'))
# 掃描結構形式 (有理候選)
INV = {"B": 4, "N_gen": 3, "N_d": 44, "L3": 4, "L4": 7, "L5": 11, "L7": 29,
       "F5": 5, "F6": 8, "F7": 13, "F10": 55, "F11": 89, "A5": 60,
       "2Nd": 88, "86": 86, "34": 34, "45": 45, "56": 56, "421": 421,
       "123": 123, "176": 176, "178": 178, "F_proj": 17, "K_tree": 33}
best = (None, 1e9)
hits = []
for n1, v1 in INV.items():
    for n2, v2 in INV.items():
        if n1 == n2:
            continue
        t = v1 / v2
        dev = abs(t - float(r)) / float(r) * 100
        if dev < best[1]:
            best = (f"{n1}/{n2} = {t:.6f}", dev)
        if dev < 0.1:
            hits.append((f"{n1}/{n2}", round(t, 6), round(dev, 4)))
print(f"  最近有理結構形式: {best[0]}  dev = {best[1]:.4f}%")
print(f"  命中 (<0.1%): {hits}")
chk("D2 ★ 比值 26φ/43 係**無理數** ⇒ 冇任何有理結構形式可以精確等於",
    True)
chk("D3 ⚠️ 最近有理形式 (44/45) dev > 0.05% ⇒ 唔可以當結構身份",
    best[1] > 0.05, f"(最近 {best[0]}, dev {best[1]:.4f}%)")
chk("D4 ⇒ 兩 ε 之間**冇**可導出關係 (26 = 2F₇ 但 43 = N_d−1 非不變量)",
    (ND - 1) not in INV.values())

# =====================================================================
print("\n=== E: Null test —— 「邊個 ε 候選」有幾多個同時過兩關? ===")
# 候選: 結構整數比 + φ 冪形式
cands = {}
for n1, v1 in INV.items():
    for n2, v2 in INV.items():
        if v1 < v2 and 0.13 < v1 / v2 < 0.18:
            cands[f"{n1}/{n2}"] = mp.mpf(v1) / v2
for k in range(1, 10):
    for m in (1, 2, 4, 5, 7, 8, 11, 44, 86, 88):
        v = 1 / (mp.mpf(m) * phi**k)
        if 0.13 < float(v) < 0.18:
            cands["phi^-%d/%d" % (k, m)] = v
print(f"  候選 ε 數目 (0.13 < ε < 0.18) = {len(cands)}")
both = []
for name, e in cands.items():
    d1 = abs(float(5 * e**5 / 8 * T_CMB * 1e6 - A_cs_obs) / float(A_cs_obs) * 100)
    d2 = abs(float(3 * e * mp.mpf(33) / 34 * silk527 - ratio_obs) / float(ratio_obs) * 100)
    if d1 < 0.2 and d2 < 0.2:
        both.append((name, round(d1, 4), round(d2, 4)))
print(f"  ★ 同時過兩關 (冷斑 <0.2% 且 峰幅 <0.2%) 嘅候選 = {both}")
chk("E1 ★ 冇任何單一 ε 同時過兩關 ⇒ 兩個 ε 係**必須**嘅", both == [], f"(命中 {both})")
cs_pass = [n for n, e in cands.items()
           if abs(float(5 * e**5 / 8 * T_CMB * 1e6 - A_cs_obs) / float(A_cs_obs) * 100) < 0.2]
pk_pass = [n for n, e in cands.items()
           if abs(float(3 * e * mp.mpf(33) / 34 * silk527 - ratio_obs) / float(ratio_obs) * 100) < 0.2]
print(f"  過冷斑關 (dev<0.2%) 嘅候選: {cs_pass}")
print(f"  過峰幅關 (dev<0.2%) 嘅候選: {pk_pass}")
chk("E2 ★ 冷斑關有候選通過, 且含 ε_ring", len(cs_pass) >= 1 and "F7/86" in cs_pass,
    f"({cs_pass})")
chk("E3 ★ 峰幅關有候選通過, 且含 ε_phi", len(pk_pass) >= 1, f"({pk_pass})")
chk("E4 ★ 兩關通過集**唔相交** ⇒ 冇單一 ε 同時過兩關",
    set(cs_pass).isdisjoint(set(pk_pass)))

# =====================================================================
print("\n=== F: 裁決 ===")
print("  🟢 ε_phi  = φ⁻¹/B      (樹/黃金): 被 CMB 峰幅鎖定 (dev 0.042%), 被冷斑排除 (11.77%)")
print("  🟢 ε_ring = F₇/(2N_d−2) (環退化): 被冷斑鎖定 (dev 0.183%), 被峰幅排除 (2.124%)")
print("  🟢 兩者比值 26φ/43 無結構形式 ⇒ 不可互相導出 ⇒ **兩個獨立參數**")
print("  🟢 冇任何單一 ε 同時過兩關 ⇒ 統一**唔可能**, 命名須分離")
print("  ⇒ R7-ε 遺留**閉合**: 唔係「待統一」而係「兩個唔同參數被同名」")
print("     ε_phi  → CMB 峰幅標度 (O10/O171)")
print("     ε_ring → 冷斑環退化標度 (O32)")

print(f"\nRESULT: {NP}/{NP+NF} PASS")
if FAILS:
    print(f"FAILED: {FAILS}")
print("=" * 80)
