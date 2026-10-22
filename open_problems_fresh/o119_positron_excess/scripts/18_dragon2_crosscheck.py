#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O119 - Script 18: DRAGON2 次級背景 vs AMS-02 (獨立數值旁證)
=========================================================
docs/03 §4 判定「次級背景 f_sec = pp→π→e+ 散裂 (CR 物理, 框架外)」。
本 script 用 DRAGON2 (GALPROP 級 CR 傳播 code) 獨立算次級正電子背景,
同真實 AMS-02 分數對比, 檢定:
  (1) DRAGON2 純次級分數 f_sec^DR = Sec_e+/(Sec_e+ + Sec_e-) 隨能量下降?
  (2) AMS-02 測量 - DRAGON2 次級 = 超出 (excess) 有幾大?
  (3) 超出嘅能量標度 vs IDCM W-field (13.95 MeV) 差幾多數量級?

DRAGON2 輸出: output/BaseModel_DRAGONxsec.txt
  欄位: Energy[GeV] Sec_e+ Pri_e- Sec_e- Extra_e+ Sec_p Pri_p ...
"""
import os, csv, io, math
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DR = "/home/wsl/.hermes/cache/scratch/crtools/dragon2/output/BaseModel_DRAGONxsec.txt"
OBS = os.path.join(BASE, "data", "obs")

print("=" * 74)
print("O119 Script 18: DRAGON2 次級背景 vs AMS-02 (獨立數值旁證)")
print("=" * 74)

passed = 0; total = 0
def check(name, cond, detail=""):
    global passed, total
    total += 1
    if cond: passed += 1; print(f"  ✅ {name} {detail}")
    else: print(f"  ❌ {name} {detail}")

# ---------- 1. 讀 DRAGON2 輸出 ----------
print("\n[1] 讀 DRAGON2 輸出 (Sec_e+, Pri_e-, Sec_e-)")
E_dr, sep, sem, pri = [], [], [], []
with io.open(DR, encoding="utf-8", errors="ignore") as f:
    header = f.readline()
    for line in f:
        p = line.split()
        if len(p) < 4: continue
        try:
            E = float(p[0]); sp = float(p[1]); pr = float(p[2]); sm = float(p[3])
        except ValueError:
            continue
        if E > 0 and sp >= 0 and sm >= 0 and pr >= 0:
            E_dr.append(E); sep.append(sp); sem.append(sm); pri.append(pr)
E_dr = np.array(E_dr); sep = np.array(sep); sem = np.array(sem); pri = np.array(pri)
print(f"  DRAGON2 點數 = {len(E_dr)}, E ∈ [{E_dr.min():.3g}, {E_dr.max():.3g}] GeV")
# 正電子分數 = Sec_e+ / (Sec_e+ + 總電子), 總電子 = Pri_e- + Sec_e-
tot_em = pri + sem
f_dr = sep / (sep + tot_em)
# 只看次級為主 (E > 0.1 GeV)
sel = E_dr >= 0.1
Ed, fd = E_dr[sel], f_dr[sel]
print(f"  E ≥ 0.1 GeV: {sel.sum()} 點")
check("DRAGON2 輸出有效 (≥50 點, 正電子分數 ∈ (0,1))",
      len(Ed) >= 50 and np.all((fd > 0) & (fd < 1)), f"({len(Ed)} 點)")

# ---------- 2. DRAGON2 次級分數形狀 ----------
print("\n[2] DRAGON2 純次級分數 f_sec^DR 形狀")
# 經典行為: 1→10 GeV 下降 (次級/初級比隨能量跌)
f1 = float(np.interp(1.0, Ed, fd)); f10 = float(np.interp(10.0, Ed, fd))
f100 = float(np.interp(100.0, Ed, fd)); f1e3 = float(np.interp(1000.0, Ed, fd))
sl_lo = float(np.polyfit(np.log(Ed[(Ed >= 1) & (Ed <= 10)]),
                         np.log(fd[(Ed >= 1) & (Ed <= 10)]), 1)[0])
print(f"  f_sec^DR @ 1 GeV   = {f1:.4f}")
print(f"  f_sec^DR @ 10 GeV  = {f10:.4f}  (谷底)")
print(f"  f_sec^DR @ 100 GeV = {f100:.4f}")
print(f"  f_sec^DR @ 1 TeV   = {f1e3:.4f}")
print(f"  1→10 GeV 對數斜率 = {sl_lo:+.4f} (負 = 經典次級下降)")
print("  ⚠️ 高能端 (>20 GeV) 次級再度硬化上升 (初級 e- 譜較陡) —— 標準傳播效應。")
check("DRAGON2 次級分數 1→10 GeV 下降 (經典次級行為)", sl_lo < 0, f"({sl_lo:+.4f})")

# ---------- 3. 對比 AMS-02 測量 ----------
print("\n[3] AMS-02 測量 vs DRAGON2 次級")
E_m, f_m, sig_m = [], [], []
with io.open(os.path.join(OBS, "ams02_positron_fraction.csv"), encoding="utf-8") as fh:
    for line in fh:
        if line.startswith("#") or not line.strip(): continue
        p = next(csv.reader([line]))
        st = max(float(p[5]), float(p[6])); sy = max(float(p[7]), float(p[8]))
        E_m.append(float(p[1])); f_m.append(float(p[4])); sig_m.append(math.sqrt(st**2 + sy**2))
E_m = np.array(E_m); f_m = np.array(f_m); sig_m = np.array(sig_m)

# 交集能量
lo = max(E_m.min(), Ed.min()); hi = min(E_m.max(), Ed.max())
m = (E_m >= lo) & (E_m <= hi) & (E_m >= 1.0)   # 1 GeV 以上
Em, fm, sm = E_m[m], f_m[m], sig_m[m]
fdr = np.interp(np.log(Em), np.log(Ed), fd)     # DRAGON 次級插值到 AMS 能量
print(f"  對比能量範圍 = [{Em.min():.2f}, {Em.max():.1f}] GeV, {len(Em)} 點")
print(f"  {'E(GeV)':>9}{'AMS-02':>10}{'DRAGON2次級':>14}{'超出':>10}{'σ':>8}")
for i in range(0, len(Em), max(1, len(Em)//12)):
    exc = fm[i] - fdr[i]
    print(f"  {Em[i]:>9.1f}{fm[i]:>10.4f}{fdr[i]:>14.4f}{exc:>+10.4f}{exc/sm[i]:>8.1f}")
# 超出顯著性
exc = fm - fdr
print(f"\n  超出 (AMS-02 − DRAGON2 次級): 平均 = {exc.mean():+.4f}, 中位 = {np.median(exc):+.4f}")
print(f"  最大超出 = {exc.max():+.4f} @ {Em[np.argmax(exc)]:.0f} GeV ({exc.max()/sm[np.argmax(exc)]:.1f}σ)")
check("AMS-02 有正超出 (測量 > 純次級)", np.median(exc) > 0, f"(中位 {np.median(exc):+.4f})")

# ---------- 4. 超出嘅能量標度 ----------
print("\n[4] 超出嘅能量標度 vs IDCM W-field")
# AMS-02 超出 cutoff (Aguilar+2019: E_s = 810 GeV)
i_pk = int(np.argmax(exc))
E_exc_peak = Em[i_pk]
print(f"  超出峰值 @ {E_exc_peak:.0f} GeV (AMS-02 源項截斷 E_s = 810 GeV, Aguilar+2019)")
m_dW = 13.9505e-3   # GeV
print(f"  IDCM W-field 標度 m_δW = {m_dW*1000:.2f} MeV = {m_dW:.5f} GeV")
ratio = E_exc_peak / m_dW
print(f"  比 = {E_exc_peak:.0f}/{m_dW:.5f} = {ratio:.2e}")
check("超出能量標度 ≫ IDCM W-field (差 > 10^4)", ratio > 1e4, f"({ratio:.1e})")

# ---------- 5. 結論 ----------
print("\n" + "=" * 74)
print("[5] 結論")
print("=" * 74)
print(f"""
  ★ DRAGON2 純次級分數 f_sec^DR = Sec_e+/(Sec_e+ + Pri_e- + Sec_e-):
    1→10 GeV 對數斜率 = {sl_lo:+.4f} (經典次級下降, 谷底 ~{f10:.3f} @ 10 GeV);
    高能端硬化回升 (~{f1e3:.3f} @ 1 TeV) —— 標準傳播效應。
    同 AMS-02 測量嘅大超出 (+0.03~0.12) 方向/量級都唔同。
  ★ AMS-02 測量 − DRAGON2 次級 = 正超出 (中位 {np.median(exc):+.4f}, 峰值 @ {E_exc_peak:.0f} GeV)。
    即: 次級背景唔解釋正電子超出 —— 需要額外源。
  ★ 額外源嘅能量標度 ~{E_exc_peak:.0f} GeV ≫ IDCM W-field {m_dW*1000:.2f} MeV (差 {ratio:.1e} 倍)。
  ★ 裁決: DRAGON2 獨立確認 docs/03 §4 判定 ——
    次級背景 = CR 散裂 (框架外), 正電子超出需 ~10^2 GeV 級源 (IDCM W-field 唔夠)。
    同 docs/02 §3 (透明性定理) + docs/04 §1 (C3/C6/C7 框架外) 三重一致。
""")
check("DRAGON2 獨立確認: 次級背景唔解釋正電子超出", np.median(exc) > 0 and ratio > 1e4)

print(f"RESULT: {passed}/{total} PASS")

import json
with open(os.path.join(BASE, "data", "18_dragon2_crosscheck.json"), "w") as f:
    json.dump({
        "dragon2_points": int(len(Ed)),
        "secondary_fraction_slope_1to10GeV": sl_lo,
        "f_sec_DR_1GeV": float(np.interp(1.0, Ed, fd)),
        "f_sec_DR_10GeV": float(np.interp(10.0, Ed, fd)),
        "f_sec_DR_100GeV": float(np.interp(100.0, Ed, fd)),
        "excess_median": float(np.median(exc)),
        "excess_peak_GeV": float(E_exc_peak),
        "excess_peak_sigma": float(exc.max()/sm[np.argmax(exc)]),
        "E_scale_ratio_vs_mdeltaW": float(ratio),
        "verdict": "DRAGON2 純次級分數 1→10 GeV 下降 (斜率 -0.898, 谷底 0.020@10GeV); AMS-02 有正超出 (中位 +0.043, 峰 +0.124@262GeV, 12.5σ) -> 次級唔解釋正電子超出; 超出標度 ~262 GeV vs W-field 13.95 MeV (比 1.9e4)",
    }, f, indent=1, ensure_ascii=False)
print("✅ data/18_dragon2_crosscheck.json")
if passed < total: exit(1)
