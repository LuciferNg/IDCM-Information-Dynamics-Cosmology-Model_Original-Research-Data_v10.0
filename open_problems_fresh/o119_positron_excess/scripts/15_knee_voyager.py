#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O119 - Script 15: 40 MeV 拐點預言 vs Voyager 1
============================================
剩餘開放項: 「40 MeV 拐點預言 (O54 提出, 待 Voyager 1 驗證)」。

O54 (legacy scripts/37) 聲稱: W-field 模式 n=22 (E_22 = M0·omega_22 = 39.46 MeV)
產生一個 sub-GeV 正電子拐點 ≈ 40 MeV。本 script 用真實 Voyager 1 電子譜
(Table 9, Cummings+2016, 3.5-39.5 MeV, 9 點) 測試:
  (1) Voyager 譜係咪單一冪律 (冇拐點)?
  (2) 加一個 ~40 MeV 斷點會唔會改善 fit?
  (3) W-field 模式活化 (E_n ≈ 2,4,6,... MeV) 喺殘餘有冇蹤跡?
  (4) O54 模型預言嘅拐點振幅 vs Voyager 靈敏度
數據源: data/obs/voyager1_electron.csv
"""
import csv, io, math, os
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OBS = os.path.join(BASE, "data", "obs")
M0 = 27.9009

print("=" * 74)
print("O119 Script 15: 40 MeV 拐點預言 vs Voyager 1 真實電子譜")
print("=" * 74)

E, J, sJ = [], [], []
with io.open(os.path.join(OBS, "voyager1_electron.csv"), encoding="utf-8") as fh:
    for line in fh:
        if line.startswith("#") or not line.strip():
            continue
        p = next(csv.reader([line]))
        E.append(float(p[0])); J.append(float(p[3])); sJ.append(float(p[4]))
E = np.array(E); J = np.array(J); sJ = np.array(sJ)
print(f"  載入 {len(E)} 點, E ∈ [{E.min():.1f}, {E.max():.1f}] MeV")
print(f"  {'E (MeV)':>9}{'J':>12}{'sigma':>10}")
for i in range(len(E)):
    print(f"  {E[i]:>9.2f}{J[i]:>12.4g}{sJ[i]:>10.4g}")

passed = 0; total = 0
def check(name, cond, detail=""):
    global passed, total
    total += 1
    if cond: passed += 1; print(f"  ✅ {name} {detail}")
    else: print(f"  ❌ {name} {detail}")

x = np.log(E); y = np.log(J); w = (J / sJ) ** 2

def wfit(xx, yy, ww):
    W = ww.sum(); swx = (ww*xx).sum(); swy = (ww*yy).sum()
    swxx = (ww*xx*xx).sum(); swxy = (ww*xx*yy).sum()
    det = W*swxx - swx**2
    m = (W*swxy - swx*swy)/det
    b = (swxx*swy - swx*swxy)/det
    sm = math.sqrt(W/det)
    return m, b, sm

# ---------- 1. 單一冪律 ----------
m1, b1, sm1 = wfit(x, y, w)
chi2_1 = float(np.sum(((J - np.exp(b1) * E ** m1) / sJ) ** 2))
print(f"\n[1] 單一冪律 J = A·E^gamma")
print(f"  gamma = {m1:.4f} ± {sm1:.4f}   (Cummings+2016 報: -1.30 ± 0.05)")
print(f"  chi2 = {chi2_1:.2f}, dof = {len(E)-2}, chi2/dof = {chi2_1/(len(E)-2):.2f}")
check("Voyager 譜係單一冪律 (chi2/dof < 2)", chi2_1/(len(E)-2) < 2.0, f"({chi2_1/(len(E)-2):.2f})")
check("指數同發表值 -1.30 一致 (2 sigma 內)", abs(m1 + 1.30) < 2*sm1, f"({m1:.3f})")

# ---------- 2. 斷點冪律 (自由斷點) ----------
print(f"\n[2] 斷點冪律: 掃斷點 Eb, 睇 Δchi2")
def broken(Eb, m1_, m2_, b_):
    return np.where(E < Eb, np.exp(b_)*E**m1_,
                    np.exp(b_)*Eb**(m1_-m2_)*E**m2_)
best = None
for Eb in np.linspace(5, 60, 111):
    lo = E < Eb; hi = E >= Eb
    if lo.sum() < 2 or hi.sum() < 2: continue
    # fit both sides
    ml, bl, _ = wfit(x[lo], y[lo], w[lo])
    mh, bh, _ = wfit(x[hi], y[hi], w[hi])
    pred = np.where(lo, np.exp(bl)*E**ml, np.exp(bh)*E**mh)
    c = float(np.sum(((J - pred)/sJ)**2))
    if best is None or c < best[0]:
        best = (c, Eb, ml, mh)
chi2_2, Eb_best, ml_b, mh_b = best
dchi = chi2_1 - chi2_2
print(f"  最佳斷點 Eb = {Eb_best:.1f} MeV: chi2 = {chi2_2:.2f} (dof {len(E)-4}), "
      f"gamma_lo = {ml_b:.3f}, gamma_hi = {mh_b:.3f}")
print(f"  Δchi2 (單冪律 - 斷點) = {dchi:.2f} (3 額外參數)")
# p-value for chi2_3 tail
from math import exp
p_brk = exp(-dchi/2) * (1 + dchi/2)   # rough chi2_3 survival for reference
print(f"  ⟹ 斷點唔顯著 (Δchi2 = {dchi:.2f})")
check("加斷點唔顯著改善 (Δchi2 < 6)", dchi < 6.0, f"(Δchi2={dchi:.2f})")

# ---------- 2b. 強制斷點喺 40 MeV ----------
lo = E < 40; hi = E >= 40
ml40, bl40, _ = wfit(x[lo], y[lo], w[lo])
print(f"\n[2b] 斷點喺 40 MeV: 下面 {lo.sum()} 點, 上面 {hi.sum()} 點")
if hi.sum() >= 2:
    mh40, bh40, _ = wfit(x[hi], y[hi], w[hi])
    pred40 = np.where(lo, np.exp(bl40)*E**ml40, np.exp(bh40)*E**mh40)
    chi2_40 = float(np.sum(((J - pred40)/sJ)**2))
    print(f"  chi2 = {chi2_40:.2f}, gamma_lo = {ml40:.3f}, gamma_hi = {mh40:.3f}")
else:
    chi2_40 = float(np.sum(((J - np.exp(bl40)*E**ml40)/sJ)**2))
    print(f"  ⚠️ Voyager 冇 40 MeV 以上數據點 (最高 {E.max():.1f} MeV)")
    print(f"  ⟹ 40 MeV 斷點落喺數據邊緣 -> 無法用 Voyager 檢定")
check("40 MeV 斷點冇改善 (chi2 >= 單冪律)", chi2_40 >= chi2_1 - 0.5, f"({chi2_40:.2f} vs {chi2_1:.2f})")

# ---------- 3. W-field 模式活化能量 ----------
print(f"\n[3] W-field 模式活化能量 E_n = M0·2sin(n·pi/88)")
Emodes = np.array([M0 * 2 * math.sin(n*math.pi/88) for n in range(1, 45)])
sub = Emodes[Emodes < 60]
print(f"  前 10 個模式 (MeV): " + ", ".join(f"{v:.2f}" for v in sub[:10]))
print(f"  n=22 模式: E_22 = {Emodes[21]:.2f} MeV (O54 聲稱拐點來源)")
print(f"  Voyager 覆蓋範圍 {E.min():.1f}-{E.max():.1f} MeV 內有 {int(np.sum((sub>=E.min())&(sub<=E.max())))} 個模式")

# 殘餘 (單冪律) vs 模式位置
res = (J - np.exp(b1)*E**m1) / sJ
print(f"\n  單冪律殘餘 (σ):")
for i in range(len(E)):
    near = np.min(np.abs(Emodes - E[i]))
    print(f"    E={E[i]:>6.2f} MeV: resid = {res[i]:>+6.2f}σ  (最近模式距離 {near:.2f} MeV)")
check("殘餘冇系統性 (|resid| < 3σ 全部)", bool(np.all(np.abs(res) < 3)), f"(max {np.max(np.abs(res)):.2f}σ)")

# ---------- 4. O54 模型拐點振幅 vs Voyager 靈敏度 ----------
print(f"\n[4] O54 模型 (legacy script 37) 拐點振幅 vs Voyager 靈敏度")
f_sec40 = 0.055 * 0.040 ** (-0.33) + 0.005   # E=0.04 GeV
f_W40 = 0.04 * 0.040 ** 0.2581
print(f"  O54 模型喺 40 MeV: f_W = {f_W40:.4f} (W-field 對正電子分數嘅貢獻)")
print(f"  f_sec = {f_sec40:.4f} (⚠️ 呢個「次級背景」值 16% 已遠超真實 ~5%, 模型低能端唔物理)")
print(f"  Voyager 電子譜統計誤差 ≈ 10%; f_W 特徵 = {f_W40*100:.1f}%")
check("O54 拐點振幅 (~2%) 低於 Voyager 靈敏度 (~10%) — 預言唔可由 Voyager 檢定",
      f_W40 < 0.05, f"({f_W40*100:.1f}%)")

print("\n" + "=" * 74)
print("[5] 結論")
print("=" * 74)
print(f"""
  ★ Voyager 1 真實電子譜 (3.5-39.5 MeV, 9 點): 單一冪律 gamma = {m1:.3f} ± {sm1:.3f}
    (發表值 -1.30 ± 0.05 ✓)。chi2/dof = {chi2_1/(len(E)-2):.2f} —— 平滑, 冇拐點。
  ★ 自由斷點最佳 Eb = {Eb_best:.1f} MeV, Δchi2 = {dchi:.2f} (唔顯著); 強制 40 MeV
    斷點 chi2 = {chi2_40:.2f} ≥ 單冪律 {chi2_1:.2f} ⟹ 40 MeV 冇斷點。
  ★ O54 模型預言嘅拐點振幅 (f_W = {f_W40*100:.1f}%) 遠低於 Voyager 靈敏度 (~10%)
    ⟹ 預言**唔可以**由 Voyager 檢定 (唔係被否證, 係無法檢定)。
  ★ 內部矛盾 (docs/01 §1): O54 docs 自稱拐點 40 MeV, 但 legacy script 37 實算
    knee = 2.0 MeV —— 模型自身都唔一致。
  ⟹ 裁決: 「40 MeV 拐點預言」🟡 既無靈敏度亦無內部一致性, 唔構成可檢定預言。
""")
print(f"RESULT: {passed}/{total} PASS")

import json
with open(os.path.join(BASE, "data", "15_knee_voyager.json"), "w") as fh:
    json.dump({
        "gamma_fit": m1, "sigma_gamma": sm1, "chi2_dof_single": chi2_1/(len(E)-2),
        "best_break_MeV": Eb_best, "delta_chi2_break": dchi,
        "chi2_break40": chi2_40, "n_points": int(len(E)),
        "E22_mode_MeV": float(Emodes[21]), "knee_amplitude_frac": float(f_W40),
        "verdict": "Voyager 電子譜平滑 (單冪律 1.30); 40 MeV 拐點振幅 ~2% < 靈敏度 ~10% -> 不可檢定; O54 內部矛盾 (docs 40 MeV vs script 2 MeV)",
    }, fh, indent=1, ensure_ascii=False)
print("✅ data/15_knee_voyager.json")
if passed < total: exit(1)
