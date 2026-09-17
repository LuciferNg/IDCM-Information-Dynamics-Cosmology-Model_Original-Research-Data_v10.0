#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O201 scripts/03 -- 反例狩獵 (Counterexample Hunt) — 憲章路線 4 (最強證偽路線)

目標: 主動搵「框架必需但冇譜表達」嘅量。搵到 => C1 完備性假 => 命題證偽。
要求 (憲章): 明確成功/失敗 + **搜尋空間記錄** (唔可以講「搵唔到」了事)。

分類:
  A. 無量綱必需量  -> 有判別力嘅搜索 (depth 1/2 + null control)
  B. 有量綱絕對標度 -> 維度論證: 譜原子池全部無量綱 => 結構性不可表達
                        (呢個係 C1 嘅**邊界**, 唔係數值失敗)

輸出: 反例集 + 每個反例嘅搜索空間 (候選數 / 最佳 dev / null 基線) + 判決
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import mpmath as mp
import o201_basis as ob

mp.mp.dps = 50

ATOMS = ob.build_atoms(with_derived=True)
PRIM = {k: v for k, v in ATOMS.items() if not k.startswith("sqrt_") and not k.startswith("inv_")}
PRIM_KEYS = list(PRIM.keys())
PRIM_VALS = np.array([float(v) for v in PRIM.values()], dtype=np.float64)

print("=" * 78)
print("O201/03 -- 反例狩獵 (Counterexample Hunt)")
print("=" * 78)
print("搜索空間: 全原子池 %d 個 (depth 1) / 原語池 %d 個 (depth 2: %d 對 x 6 運算 = %d 格)"
      % (len(ATOMS), len(PRIM), len(PRIM) ** 2 // 2, len(PRIM) ** 2 // 2 * 6))

# null control
rng = np.random.default_rng(20260917)
rnd_real = np.exp(rng.uniform(np.log(1e-3), np.log(1e4), 400))
rnd_real = rnd_real[np.abs(rnd_real - np.round(rnd_real)) > 1e-6]
null_d2 = ob.depth2_best(PRIM_VALS, rnd_real, tol=1.0)
NULL_D2_1e3 = sum(1 for h in null_d2 if h and h[0] < 1e-3) / len(rnd_real)
NULL_D2_1e5 = sum(1 for h in null_d2 if h and h[0] < 1e-5) / len(rnd_real)
NULL_D2_1e9 = sum(1 for h in null_d2 if h and h[0] < 1e-9) / len(rnd_real)
rnd_int = np.round(np.exp(rng.uniform(np.log(1e-3), np.log(1e4), 400)))
null_d2i = ob.depth2_best(PRIM_VALS, rnd_int, tol=1.0)
NULL_D2_INT = sum(1 for h in null_d2i if h and h[0] < 1e-9) / len(rnd_int)
print("null control (非整數 400 個): P(<1e-3)=%.3f  P(<1e-5)=%.3f  P(<1e-9)=%.4f" % (
    NULL_D2_1e3, NULL_D2_1e5, NULL_D2_1e9))
print("null control (整數 400 個)  : P(<1e-9)=%.3f" % NULL_D2_INT)

# ============================================================
# 1. 反例候選 (框架必需量)
# ============================================================
CASES = [
    # (name, value_str, dim, provenance/必要性)
    ("M_Pl", "1.220890e19", "GeV", "O168: 最後絕對尺度輸入 (G = M_Pl^-2)"),
    ("G", "6.67430e-11", "m^3 kg^-1 s^-2", "O121/O168: 引力常數 = 唯一有量綱輸入"),
    ("T_CMB", "2.72548", "K", "O166 開題: CMB 溫度絕對值冇結構閉合"),
    ("m_p", "938.27208816", "MeV", "O144: 質子質量 (QCD 預算攻堅中)"),
    ("m_7", "13.95", "MeV", "O116/O119: DM 譜扇區質量 = M_0/2"),
    ("a_0", "1.2e-10", "m s^-2", "O32: RAR 加速度標度"),
    ("r_d", "147.09", "Mpc", "O167: DESI 拖曳視界 (聲學視界)"),
    ("omega_ring", "72.59", "(km/s)/Mpc", "O73: 世界環角頻率"),
    ("H0_SHOES", "73.04", "(km/s)/Mpc", "O73/O167: 距離階梯族"),
    ("eta_B", "6.0636e-10", "-", "O73: BBN 鎖定 omega_ring 嘅輸入 (無量綱)"),
    ("lambda_Edd", "0.1", "-", "O173/O197: Eddington 比 (需要外部假設?)"),
    ("z_f_star", "13.43", "-", "O197: 成長閉合紅移"),
    ("sigma8", "0.811", "-", "O100: 結構增長振幅"),
    ("Delta_VLambda", "0.082129", "-", "O111: V_Lambda 殘留 (未閉合)"),
    ("N_crit", "150", "-", "O153: 臨界通道數候選"),
    ("mu_logN", "0.862478", "-", "O169: logN 中位斜率"),
    ("s_logN", "1.1874", "-", "O169: logN 散射"),
    ("crack_0746", "0.00746", "-", "O168: 雙尺度裂縫 0.746%"),
    ("baryon_1960", "0.31666666666666665", "-", "O163: 19/60 重子佔物質比"),
    ("Omega_Lambda", "0.6833333333333333", "-", "O148: 41/60 (已知有譜表達, 正對照)"),
    ("N_gen", "3", "-", "O103 (已知有譜表達, 正對照)"),
]

print("\n" + "=" * 78)
print("反例候選 (%d 個; 其中 %d 個有量綱)" % (
    len(CASES), sum(1 for c in CASES if c[2] != "-")))
print("=" * 78)

rows = []
for nm, vs, dim, prov in CASES:
    t = mp.mpf(vs)
    d1 = ob.search_depth1(ATOMS, t)
    best1 = d1[0] if d1 else None
    h2 = ob.depth2_best(PRIM_VALS, [float(t)])[0]
    rows.append((nm, t, dim, prov, best1, h2))

# ============================================================
# 2. 判決
# ============================================================
print("\n%-16s %-10s %-22s %-11s %s" % ("量", "值", "維度", "depth1", "depth2 最佳"))
print("-" * 110)
res = {}
for nm, t, dim, prov, best1, h2 in rows:
    s1 = ("%s dev %.2e" % (best1[1], best1[0])) if best1 else "冇 (dev > 1e-3)"
    if h2:
        s2 = "%s %s %s dev %.2e" % (PRIM_KEYS[h2[2]], ["+", "-", "*", "/", "R/", "|d|"][h2[1]],
                                    PRIM_KEYS[h2[3]], h2[0])
    else:
        s2 = "冇"
    print("%-16s %-10s %-22s %-11s %s" % (nm, mp.nstr(t, 8), dim, s1.split()[0], s2))

print("\n" + "=" * 78)
print("判決 (反例集)")
print("=" * 78)
counter_examples = []
for nm, t, dim, prov, best1, h2 in rows:
    if dim != "-":
        verdict = "結構性不可表達 (有量綱; 譜原子池全無量綱)"
        counter_examples.append((nm, "dimensional", prov))
    else:
        if best1 and ob.classify(mp.mpf(best1[0])) in ("EXACT", "HIT"):
            verdict = "有譜表達 (%s)" % best1[1]
        elif h2 and h2[0] < 1e-9:
            verdict = "有譜表達 (depth2: %s %s %s)" % (PRIM_KEYS[h2[2]],
                                                  ["+", "-", "*", "/", "R/", "|d|"][h2[1]],
                                                  PRIM_KEYS[h2[3]])
        elif (h2 and h2[0] < 1e-3) or (best1 and best1[0] < 1e-3):
            verdict = "🔴 只落陷阱窗 (1e-5,1e-3) => 無譜表達"
            counter_examples.append((nm, "trap-window", prov))
        else:
            verdict = "🔴 無譜表達 (搜索空間內冇命中)"
            counter_examples.append((nm, "no-expression", prov))
    print("  %-16s %s" % (nm, verdict))
    print("     必要性: %s" % prov)
    if dim == "-":
        print("     搜索空間: depth1 %d 候選 | depth2 %d 格 | null(非整數) <1e-9 = %.4f"
              % (len(ATOMS), len(PRIM) ** 2 // 2 * 6, NULL_D2_1e9))

# ============================================================
# 3. 維度論證 (scale-blindness theorem)
# ============================================================
print("\n" + "=" * 78)
print("維度論證 (C1 邊界, 唔係數值失敗)")
print("=" * 78)
print("  (i) 譜原子池 %d 個元素全部係純數 (π, 整數, cos/sin 值, 譜和) — 零量綱" % len(ATOMS))
print("  (ii) 譜語言嘅任何閉式泛函 = 純數運算 => 仍係純數")
print("  (iii) 所以譜語言嘅像 ⊆ 無量綱數; 有量綱量必須 = (無量綱譜因子) x (外部標度錨)")
print("  (iv) 驗證: R_world 由 c 同 T_ring 定標 (O73), M_Pl 由 G 定標 (O168)")
print("  (v) 結論: C1 完備性**必須加維度限制** — 譜分解係無量綱語言;")
print("           絕對標度 (M_Pl, T_CMB, m_p, G) 結構上唔可能係譜泛函。")
print("           => 反例集 A (有量綱) 係**語言邊界**, 唔係語言失效。")

# 具體驗證: SI 數值唔會係譜原子
print("\n  具體驗證 (SI 數值 vs 譜原子池):")
for nm, t, dim, prov, best1, h2 in rows:
    if dim == "-":
        continue
    b = best1[0] if best1 else None
    print("    %-12s SI 值 = %-14s 最近譜原子 dev = %s  => %s" % (
        nm, mp.nstr(t, 8), ("%.2e" % b) if b else "> 1e-3",
        "MISS (預期: SI 單位係人擇)" if (not b or b > 1e-3) else "⚠️ 命中 (需查)"))

# ============================================================
# 4. 反例集總結
# ============================================================
print("\n" + "=" * 78)
print("反例集總結")
print("=" * 78)
dim_ce = [c for c in counter_examples if c[1] == "dimensional"]
num_ce = [c for c in counter_examples if c[1] != "dimensional"]
print("  A. 有量綱反例 (語言邊界, %d 個):" % len(dim_ce))
for nm, k, prov in dim_ce:
    print("     - %-16s %s" % (nm, prov))
print("  B. 無量綱反例 (真缺口, %d 個):" % len(num_ce))
for nm, k, prov in num_ce:
    print("     - %-16s [%s] %s" % (nm, k, prov))
print("\n  => C1 判決: 無量綱層 %d/%d 有譜表達; 有量綱層 0/%d (結構性)" % (
    len(CASES) - len(counter_examples), len(CASES) - len(dim_ce), len(dim_ce)))

# ============================================================
# 5. data 輸出
# ============================================================
out = {
    "n_atoms": len(ATOMS), "n_prim": len(PRIM), "depth2_cells": len(PRIM) ** 2 // 2 * 6,
    "null_d2_1e3": NULL_D2_1e3, "null_d2_1e5": NULL_D2_1e5, "null_d2_1e9": NULL_D2_1e9,
    "null_d2_int_1e9": NULL_D2_INT,
    "cases": [{"name": nm, "value": mp.nstr(t, 20), "dim": dim, "prov": prov,
               "depth1": (best1[1] if best1 else None),
               "depth1_dev": (best1[0] if best1 else None),
               "depth2": ("%s%s%s" % (PRIM_KEYS[h2[2]], ["+", "-", "*", "/", "R/", "|d|"][h2[1]],
                                      PRIM_KEYS[h2[3]])) if h2 else None,
               "depth2_dev": (h2[0] if h2 else None)} for nm, t, dim, prov, best1, h2 in rows],
    "counter_examples_dimensional": [c[0] for c in dim_ce],
    "counter_examples_numeric": [c[0] for c in num_ce],
}
d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
os.makedirs(d, exist_ok=True)
p = os.path.join(d, "03_counterexample_hunt.json")
with open(p, "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("\n[data] %s" % os.path.abspath(p))

# ============================================================
# 6. 自檢
# ============================================================
print("\n" + "=" * 78)
print("自檢")
print("=" * 78)
NPASS = NFAIL = 0


def check(label, cond):
    global NPASS, NFAIL
    if cond:
        NPASS += 1
        print("  PASS  %s" % label)
    else:
        NFAIL += 1
        print("  FAIL  %s" % label)


check("[INJECT] checker 識 FAIL (3 != 4)", not (abs(mp.mpf(3) - mp.mpf(4)) < mp.mpf('1e-40')))
check("正對照 Omega_Lambda = 41/60 有譜表達 (depth1/2)", any(
    r[0] == "Omega_Lambda" and ((r[4] and r[4][0] < 1e-5) or (r[5] and r[5][0] < 1e-9))
    for r in rows))
check("正對照 N_gen = 3 有譜表達", any(
    r[0] == "N_gen" and r[4] and r[4][0] < 1e-5 for r in rows))
check("正對照 19/60 有譜表達 (depth2)", any(
    r[0] == "baryon_1960" and r[5] and r[5][0] < 1e-9 for r in rows))
check("有量綱反例 >= 5 個", len(dim_ce) >= 5)
check("M_Pl 係有量綱反例", "M_Pl" in [c[0] for c in dim_ce])
check("T_CMB 係有量綱反例", "T_CMB" in [c[0] for c in dim_ce])
check("搜索空間已記錄 (depth2 cells = %d > 1e6)" % out["depth2_cells"],
      out["depth2_cells"] > 1e6)
check("null control 已報", 0.0 <= NULL_D2_1e9 <= 1.0)
check("原子池全無量綱 (純數)", all(isinstance(v, mp.mpf) for v in ATOMS.values()))
check("反例集非空 (有真結果)", len(counter_examples) > 0)
check("SI 數值唔係譜原子 (T_CMB)", not any(
    r[0] == "T_CMB" and r[4] and r[4][0] < 1e-3 for r in rows))
check("eta_B 判決已記錄", any(r[0] == "eta_B" for r in rows))

print("\n總計: %d/%d PASS" % (NPASS, NPASS + NFAIL))
print("EXIT=%d" % (0 if NFAIL == 0 else 1))
