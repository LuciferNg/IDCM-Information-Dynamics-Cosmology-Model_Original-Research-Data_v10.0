#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O171 scripts/32 — R7 絕對錨定鏈條逐環驗證 + 最終裁決

背景:
  docs/12 §8 (R7 第一版): 33/34 同 0.97 相距 0.0606% ⇒ 需 σ < 0.0303%
                          ⇒ 觀測 CV 下限 0.672% 粗 22× ⇒ 「原理上不可檢定」🔴
  docs/16 §9 (R7 第二版): IDCM 有零參數絕對振幅 ε⁵/8 ⇒ A_s 非自由
                          ⇒ 判別力 107× → 1.93× ⇒ 改判「有條件可檢定」🟡
  docs/18 §3 (R7 第三版): 三分解 Q1/Q2/Q3; Q3 (歸一化) 判「結構不相容」🔴
  scripts/30 (本輪):      ★ 真實 Planck 全譜 ⇒ ε⁵/8 唔係 CMB 圖 rms (差 3.69×)
                          ★ o77「Planck 1.1e-5」係 hardcode 常數

本節: 將 docs/16 §9 之論證拆成**逐環**, 每環獨立驗證, 找出失效環並傳播後果。

鏈條:
  環1  ε⁵/8 = 1.100707e-5 由 φ 導出 (唔依賴 CMB)           → 結構 ✅
  環2  ε⁵/8 = CMB 圖 rms ΔT/T (絕對錨)                      → ★ 失效
  環3  錨定 ⇒ 判別力 107× → 1.93× ⇒ 「有條件可檢定」        → 撤銷 (因環2)
"""

import json
import math
import random
from pathlib import Path

import mpmath as mpm
mp = mpm.mp
mp.dps = 40

BASE = Path(__file__).resolve().parent.parent
PLK = BASE / "data" / "planck"
T_CMB = mp.mpf('2.72548') * 1e6

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


def load_spec(fn):
    out = []
    for ln in open(fn, encoding="utf-8"):
        if ln.startswith("#"):
            continue
        p = ln.split()
        if len(p) >= 2:
            out.append((int(float(p[0])), float(p[1])))
    return out


FULL = load_spec(PLK / "COM_PowerSpect_CMB-TT-full_R3.01.txt")
PHI = (1 + mp.sqrt(5)) / 2
EPS = 1 / (4 * PHI)
ANCHOR = EPS ** 5 / 8

print("=" * 72)
print("O171 scripts/32 — R7 絕對錨定鏈條逐環驗證 + 最終裁決")
print("=" * 72)

# ================================================================ A
print("\n=== A: 鏈條逐環拆解 ===")
print("  環1: ε⁵/8 由 φ 導出 (結構, 唔依賴 CMB)")
print("  環2: ε⁵/8 = CMB 圖 rms ΔT/T (絕對錨)  ← docs/16 §6 已見 34.8× 疑點")
print("  環3: 錨定 ⇒ 判別力 107× → 1.93× (docs/16 §9)")
chk("A1 ε = 1/(4φ) 精確 (docs/17 樹/黃金路線)",
    abs(float(EPS) - 0.1545084971874737) < 1e-15, f"({float(EPS):.17f})")
chk("A2 環1 之 ε⁵/8 = 1.1007073e-5 (結構, 可獨立重算)",
    abs(float(ANCHOR) - 1.1007073e-5) < 1e-12, f"({float(ANCHOR):.7e})")

# ================================================================ B
print("\n=== B: 環2 獨立重算 (真實 Planck 全譜, 唔 import scripts/30) ===")
S = sum((2 * e + 1) * mp.mpf(D) / (2 * e * (e + 1)) for e, D in FULL)
RMS = mp.sqrt(S)
DTT = RMS / T_CMB
print(f"  Σ_ℓ (2ℓ+1)C_ℓ/4π = {mp.nstr(S, 8)} μK²")
print(f"  CMB 圖 rms = {mp.nstr(RMS, 8)} μK ⇒ ΔT/T = {mp.nstr(DTT, 8)}")
ratio = DTT / ANCHOR
print(f"  ratio = {mp.nstr(ratio, 8)}  (dev {float(ratio-1)*100:+.2f}%)")
chk("B1 環2: 真圖 rms ΔT/T = 4.06450e-5 (獨立重算)",
    abs(float(DTT) - 4.0644962e-5) < 1e-12, f"({float(DTT):.7e})")
chk("B2 ★★ 環2 失效: ε⁵/8 比真圖 rms 細 3.69× (唔係 rms)",
    abs(float(ratio) - 3.6926222) < 1e-6, f"({float(ratio):.7f})")
# docs/16 §6 之 34.8× 疑點: √C_221 (用 O10 分箱 D_221 = 5816.48, ℓ=221)
D1_221 = 5816.4797
C1 = 2 * mp.pi * mp.mpf(D1_221) / (221 * 222)
r_16 = ANCHOR / (mp.sqrt(C1) / T_CMB)
# 同一量用原始全譜 ℓ=220 值 (D = 6373.42)
C1f = 2 * mp.pi * mp.mpf(dict(FULL)[220]) / (220 * 221)
r_16f = ANCHOR / (mp.sqrt(C1f) / T_CMB)
print(f"  docs/16 §6 疑點重算 (O10 分箱 D_221 = 5816.48):")
print(f"    √C_221/T = {mp.nstr(mp.sqrt(C1)/T_CMB, 6)} ⇒ ratio = {mp.nstr(r_16, 6)}×")
print(f"  同量用原始全譜 ℓ=220 (D = {dict(FULL)[220]:.2f}):")
print(f"    √C_220/T = {mp.nstr(mp.sqrt(C1f)/T_CMB, 6)} ⇒ ratio = {mp.nstr(r_16f, 6)}×")
chk("B3 docs/16 §6 之 34.8× 疑點確認存在 (單模 vs 錨)",
    abs(float(r_16) - 34.77) < 0.05, f"({float(r_16):.2f}×)")
print("  ⇒ 兩個疑點方向一致: 錨 (1.1007e-5) 對唔上任何 CMB 絕對量:")
print("      單模 √C_221 = 3.167e-7  (細 34.8×)")
print("      全圖 rms    = 4.0645e-5  (大 3.69×)")
print("      ⇒ 錨唔係「圖 rms」, 亦唔係「單模振幅」—— 觀測對應物未定義 🔴")

# ================================================================ C
print("\n=== C: 環3 算術核對 (107× / 1.93× 之定義一致性) ===")
sig_U = 0.032334          # docs/16: σ(U) 無錨估計量
sig_D1 = 165.4180814864716 / 5816.479677744882   # Planck D₁ 峰高 (精確)
need_id = 0.000303        # docs/12 §8: 分辨 33/34 vs 0.97
need_det = 1.0 / 68       # docs/20 §3: 偵測門檻 σ < 1/(2d), d = 34
print(f"  σ(U) 無錨 = {sig_U*100:.4f}%  |  σ(D₁) = {sig_D1*100:.4f}%")
print(f"  識別門檻 (docs/12) = {need_id*100:.4f}%  |  偵測門檻 (docs/20) = {need_det*100:.4f}%")
r1 = sig_U / need_id
r2 = sig_D1 / need_det
print(f"  無錨 差 = σ(U)/門檻_識別 = {r1:.2f}×   (docs/16 稱 107×)")
print(f"  有錨 差 = σ(D₁)/門檻_偵測 = {r2:.3f}×  (docs/16 稱 1.93×)")
chk("C1 環3 算術: 107× 源自 σ(U)/0.0303% (定義一致)",
    abs(r1 - 107) < 1.0, f"({r1:.2f}×)")
chk("C2 環3 算術: 1.93× 源自 σ(D₁)/(1/68) (定義一致)",
    abs(r2 - 1.934) < 0.01, f"({r2:.4f}×)")
print("  ⇒ ★ 環3 之**算術本身無誤**; 但兩者用**唔同 σ** (σ(U) vs σ(D₁))")
print("     且 σ(U) 亦由 CMB 峰高導出 ⇒ 兩者其實同源 (峰高通道)")

# ================================================================ D
print("\n=== D: 撤銷連鎖 (環2 失效 ⇒ 環3 結論撤銷) ===")
print("  環2 失效 (B2/B3): ε⁵/8 ≠ 任何 CMB 絕對量")
print("  ⇒ 錨唔存在 ⇒ 無錨 ⇒ 判別力仍為 107× (或 93.9× 用 σ(D₁))")
print("  ⇒ docs/16 §9「107× → 1.93×」**撤銷**")
print("  ⇒ docs/16 §9「A_s 非自由 ⇒ 有條件可檢定」**前提失效**")
print("  ⇒ R7 (33/34) 狀態: 🟡 → **🔴 回到 docs/12 §8 之結論**")
chk("D1 ★ 撤銷: 環2 失效 ⇒ 環3 結論不成立",
    abs(float(ratio) - 1) > 0.5, f"(環2 dev {float(ratio-1)*100:+.1f}% ⇒ 錨無效)")
chk("D2 ★ R7 (33/34) 振幅通道: 最終 z = 1.03σ (用 D₁) / 2.10σ (用 A_s)",
    abs(0.0294118 / sig_D1 - 1.0342) < 0.001 and abs(0.0294118 / 0.014 - 2.101) < 0.01)

# ================================================================ E
print("\n=== E: 冷斑絕對錨能否補位? ===")
A_CS = mp.mpf('134.2')          # SMICA 冷斑 (直接量測, 真絕對錨)
D1_bin = mp.mpf('5816.4797')    # O10 分箱首峰 (標準量測峰高)
D1_raw = mp.mpf(dict(FULL)[220])  # 原始全譜 ℓ=220
D1p = mp.sqrt(D1_bin)
print(f"  冷斑 A = {float(A_CS):.1f} μK (SMICA, 直接量測 ⇒ 真絕對錨)")
print(f"  首峰振幅 √D₁ = {float(D1p):.4f} μK (O10 分箱 D₁ = 5816.48)")
print(f"     (原始全譜 ℓ=220 ⇒ √D = {float(mp.sqrt(D1_raw)):.4f} μK)")
r_cs = A_CS / D1p
r_cs_raw = A_CS / mp.sqrt(D1_raw)
print(f"  A_cs/√D₁ = {float(r_cs):.6f}  (原始全譜: {float(r_cs_raw):.6f})")
print(f"  5ε_ring⁵/8·T = {float(5*(mp.mpf(13)/86)**5/8*T_CMB):.3f} μK (dev "
      f"{float(5*(mp.mpf(13)/86)**5/8*T_CMB/A_CS-1)*100:+.3f}%)")
print(f"  5ε_φ⁵/8·T    = {float(5*ANCHOR*T_CMB):.3f} μK (dev "
      f"{float(5*ANCHOR*T_CMB/A_CS-1)*100:+.3f}%)")
chk("E1 冷斑 5ε_ring⁵/8·T = 134.45 μK (dev 0.18%) — 冷斑自身閉合",
    abs(float(5 * (mp.mpf(13) / 86) ** 5 / 8 * T_CMB) - 134.446) < 0.01)
chk("E2 冷斑 5ε_φ⁵/8·T = 150.0 μK (dev +11.8%) — ε_φ 被冷斑排除",
    abs(float(5 * ANCHOR * T_CMB) - 149.998) < 0.01)
# 冷斑 ↔ 峰高 之結構掃描
LIB = [4, 3, 44, 7, 11, 29, 5, 8, 13, 21, 55, 89, 33, 17, 60, 2, 9, 16,
       88, 90, 178, 176, 420, 421, 123, 99, 198, 528, 22, 45, 46, 34, 56,
       360, 137, 128, 48, 12, 6, 10, 27, 28, 36, 66, 78, 264, 180, 9055]


def scan(target, tol=1e-3, n3=False):
    t = float(target)
    hits = []
    for a in LIB:
        for b in LIB:
            for nm, v in ((f"{a}/{b}", a / b), (f"{a}*{b}", a * b)):
                if abs(v - t) / t <= tol:
                    hits.append((nm, v))
    if n3:
        for a in LIB:
            for b in LIB:
                for c in LIB:
                    v = a * b / c
                    if abs(v - t) / t <= tol:
                        hits.append((f"{a}*{b}/{c}", v))
    return hits


h_cs = scan(r_cs)
h_cs_raw = scan(r_cs_raw)
print(f"  A_cs/√D₁ (分箱) = {float(r_cs):.6f}: 0.1% 內命中 {len(h_cs)} 條")
print(f"  A_cs/√D₁ (原始全譜 ℓ=220) = {float(r_cs_raw):.6f}: 命中 {len(h_cs_raw)} 條")
random.seed(20260917)
null = [len(scan(random.uniform(1.2, 2.2))) for _ in range(60)]
mn = sum(null) / len(null)
print(f"  null control (60 隨機 U(1.2,2.2)): 平均 {mn:.1f} 條")
chk("E3 ★ 冷斑/峰高比 (兩版本 {:.4f} / {:.4f}) 之命中 ≈ null ⇒ 無結構身份".format(
        float(r_cs), float(r_cs_raw)),
    len(h_cs) < 1.5 * max(mn, 1) and len(h_cs_raw) < 1.5 * max(mn, 1),
    f"(實測 {len(h_cs)}/{len(h_cs_raw)} vs null {mn:.1f})")

# ================================================================ F
print("\n=== F: 振幅比 √D₁/(ε⁵/8·T) 之結構掃描 ===")
r_amp = D1p / (ANCHOR * T_CMB)                       # 分箱 D₁
r_amp_raw = mp.sqrt(D1_raw) / (ANCHOR * T_CMB)       # 原始全譜 ℓ=220
print(f"  √D₁ / (ε_φ⁵/8·T) = {float(r_amp):.6f} (分箱)")
print(f"                   = {float(r_amp_raw):.6f} (原始全譜 ℓ=220)")
h_amp = scan(r_amp)
h_amp_raw = scan(r_amp_raw)
null2 = [len(scan(random.uniform(2.0, 3.5))) for _ in range(60)]
mn2 = sum(null2) / len(null2)
print(f"  null control (60 隨機 U(2,3.5)): 平均 {mn2:.1f} 條")
chk("F1 ★ 命中 ({}/{} 條) ≈ null ({:.1f}) ⇒ 無結構身份 ⇒ 歸一化鏈仍缺".format(
        len(h_amp), len(h_amp_raw), mn2),
    len(h_amp) < 1.5 * max(mn2, 1) and len(h_amp_raw) < 1.5 * max(mn2, 1),
    f"(實測 {len(h_amp)}/{len(h_amp_raw)} vs null {mn2:.1f})")

# ================================================================ G
print("\n=== G: 最終裁決 ===")
verdict = {
    "link1_eps_derivation": "OK (結構, 由 φ 導出)",
    "link2_anchor_is_map_rms": False,
    "link2_ratio_anchor_vs_full_rms": float(ratio),
    "link2_ratio_anchor_vs_single_mode": float(ANCHOR / (mp.sqrt(C1) / T_CMB)),
    "link3_arithmetic": "OK (107× / 1.93× 定義一致)",
    "link3_conclusion": "撤銷 (環2 失效)",
    "r7_final_z_D1": 1.034,
    "r7_final_z_As": 2.101,
    "coldspot_selfclosed_eps_ring": True,
    "coldspot_eps_phi_excluded_pct": float(5 * ANCHOR * T_CMB / A_CS - 1) * 100,
    "coldspot_peak_ratio_binned": float(r_cs),
    "coldspot_peak_ratio_raw": float(r_cs_raw),
    "coldspot_peak_ratio_has_structure": len(h_cs) >= 1.5 * max(mn, 1),
    "amplitude_ratio_binned": float(r_amp),
    "amplitude_ratio_raw": float(r_amp_raw),
    "amplitude_ratio_has_structure": len(h_amp) >= 1.5 * max(mn2, 1),
    "verdict": "R7 絕對錨定鏈條環2 失效 ⇒ 環3 (107×→1.93×) 撤銷; "
               "R7 振幅通道回到 🔴 (z = 1.03σ D₁ / 2.10σ A_s); "
               "冷斑自身閉合 (ε_ring 路線 0.18%) 但唔能提供峰高尺度 (無結構比)",
}
(BASE / "data" / "32_r7_anchor_chain.json").write_text(
    json.dumps(verdict, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"  環1 結構導出      : ✅ OK")
print(f"  環2 絕對錨 (圖 rms): 🔴 失效 (差 {float(ratio):.2f}×)")
print(f"  環3 判別力改善    : 🔴 撤銷 (算術無誤, 但前提失效)")
print(f"  R7 最終           : 🔴 z = 1.03σ (D₁) / 2.10σ (A_s) < 3σ")
print(f"  冷斑              : 🟢 自身閉合 (ε_ring 0.18%), 🔴 唔能鎖峰高")
print(f"  歸一化鏈          : 🔴 仍缺 (兩個比都無結構身份)")

print("\n" + "=" * 72)
print(f"RESULT: {N_PASS}/{N_PASS + N_FAIL} PASS")
if FAILS:
    print("FAILS:")
    for f_ in FAILS:
        print(f"  - {f_}")
print("=" * 72)
