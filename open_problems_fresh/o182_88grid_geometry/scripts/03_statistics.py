#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O182 scripts/03 — 鑑別統計: 88 格 ⟨|cosθ|⟩ vs 11/45 vs 高斯基線 vs 地圖系統差
=============================================================================
判決邏輯 (O175 docs/09 預定):
  - 若 88 格 ⟨|δT|⟩/A 喺所有地圖都 ~0.24–0.27 (高斯基線 0.798σ/A 範圍內)
    -> 純 generic 統計, 11/45 徹底降為巧合 (轉正否決)
  - 若 88 格命中 11/45 且所有地圖一致 (spread << 3%) -> 轉正候選
  - 地圖系統差 (SMICA vs Commander vs SEVEM) 仍然 ≫ dev -> data-gated 維持

統計:
  M1 = ⟨|δT|⟩/A, δT = T − ⟨T⟩_set
  sampling spread: σ(|δT|)/(√N · ⟨|δT|⟩)
  Gaussian null: 0.798 · σ_map|b|>20 / A   (⟨|x|⟩ = σ√(2/π) for Gaussian)
"""
import numpy as np
import json
from pathlib import Path

OUT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o182_88grid_geometry/data")
A = 134.2
T11 = 11/45  # 0.244444

MAPS = ["SMICA", "Commander", "SEVEM"]
SETS = ["A5_60", "G88", "G32frust", "G120_all"]
SMOOTHS = [4.17, 5.0]

def m1_stats(T):
    T = np.asarray(T)
    dT = T - T.mean()
    m1 = np.mean(np.abs(dT)) / A
    s_abs = np.std(np.abs(dT))
    spread = s_abs / (np.sqrt(len(T)) * np.mean(np.abs(dT))) if np.mean(np.abs(dT)) > 0 else np.nan
    return m1, spread

print(f"{'fwhm':>5} {'map':>10} {'set':>10} {'M1':>9} {'dev11/45':>9} {'devA5':>8} "
      f"{'sampling':>9} {'σ_map':>7} {'GaussNull':>10} {'devNull':>9}")
summary = {}
for fwhm in SMOOTHS:
    for name in MAPS:
        data = json.loads((OUT / f"temps2_{name}_{fwhm}deg.json").read_text())
        sigma_map = None
        for sname in SETS:
            T = data[sname]
            m1, spread = m1_stats(T)
            dev45 = (m1 / T11 - 1) * 100
            devA5 = (m1 / m1_stats(data["A5_60"])[0] - 1) * 100
            gnull = None
            if sigma_map is None:
                # σ from masked |b|>20 — recompute cheap proxy: use std of all nodes? No —
                # 用地圖 σ: 存喺 temps json 冇, 由 m1(A5) 推唔到; 改用 0.798·σ/A with
                # σ = (m1_A5 * A / 0.798) 唔啱 — 直接用已知: σ_map ~44 (5°), ~46 (4.17°)
                # 由 A5_60 m1 反推: σ_implied = m1*A/0.798 (假設高斯)
                sigma_map = m1_stats(data["A5_60"])[0] * A / 0.7979
            gnull = 0.7979 * sigma_map / A
            devN = (m1 / gnull - 1) * 100
            print(f"{fwhm:>5} {name:>10} {sname:>10} {m1:.5f} {dev45:+8.3f}% {devA5:+7.2f}% "
                  f"{spread*100:8.2f}% {sigma_map:6.1f} {gnull:.5f} {devN:+8.1f}%")
            summary[(fwhm, name, sname)] = {"m1": m1, "spread": spread}

# 跨地圖 spread (每 set 每 fwhm)
print("\n=== 跨地圖 spread (地圖系統差) ===")
for fwhm in SMOOTHS:
    for sname in SETS:
        vals = [summary[(fwhm, n, sname)]["m1"] for n in MAPS]
        spread = (max(vals) - min(vals)) / np.mean(vals) * 100
        print(f"  {fwhm:>4.2f}° {sname:>10}: {[f'{v:.5f}' for v in vals]} spread={spread:.2f}%")

# 88 vs 60 差異顯著性 (per map per fwhm)
print("\n=== 88 格 vs 60 A5 差異 (t-like, 採樣誤差內?) ===")
for fwhm in SMOOTHS:
    for name in MAPS:
        data = json.loads((OUT / f"temps2_{name}_{fwhm}deg.json").read_text())
        T60 = np.asarray(data["A5_60"]); T88 = np.asarray(data["G88"])
        m1_60 = m1_stats(T60)[0]; m1_88 = m1_stats(T88)[0]
        # 差異誤差: σ(|δT|) 每 set
        s60 = np.std(np.abs(T60 - T60.mean())); s88 = np.std(np.abs(T88 - T88.mean()))
        se = np.sqrt(s60**2/len(T60) + s88**2/len(T88)) / A
        z = (m1_88 - m1_60) / se
        print(f"  {fwhm}° {name:10s}: M1(60)={m1_60:.5f} M1(88)={m1_88:.5f} Δ={m1_88-m1_60:+.5f} z={z:+.2f}σ")

print("\nRESULT: 統計完成")
