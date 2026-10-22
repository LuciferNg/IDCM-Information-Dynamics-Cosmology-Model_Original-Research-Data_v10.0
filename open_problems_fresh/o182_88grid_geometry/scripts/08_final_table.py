#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O182 scripts/08 — 最終鑑別表 + 穩健性檢查
=========================================
1. 各 set × 3 圖 × 2 平滑: M1 (全節點 + |b|>20 子集)
2. G88 極端節點檢查 (有冇 2-3 個極端值推高 M1)
3. 綜合判決表
"""
import numpy as np
import json
from pathlib import Path
from astropy.coordinates import SkyCoord
import astropy.units as u

OUT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o182_88grid_geometry/data")
ROOT = OUT.parent.parent
A = 134.2
T11 = 11/45

def to_gal(pts):
    sc = SkyCoord(ra=pts[:, 0]*u.deg, dec=pts[:, 1]*u.deg, frame='icrs')
    g = sc.galactic
    return np.column_stack([g.l.deg, g.b.deg])

lb = {
    "A5_60":    to_gal(np.loadtxt(ROOT / "cmb_cold_spot/data/a5_nodes.txt")),
    "G88":      to_gal(np.loadtxt(OUT / "g88_nodes.txt")),
    "G32frust": to_gal(np.loadtxt(OUT / "g32_frustration_midpoints.txt")),
}
lb["G120_all"] = np.vstack([lb["G88"], lb["G32frust"]])

SETS = ["A5_60", "G88", "G32frust", "G120_all"]
MAPS = ["SMICA", "Commander", "SEVEM"]
SMOOTHS = [4.17, 5.0]

def m1(T):
    T = np.asarray(T)
    return np.mean(np.abs(T - T.mean())) / A

print("=== 主表: M1 = ⟨|δT|⟩/A (全節點 / |b|>20 子集) ===")
table = {}
for fwhm in SMOOTHS:
    print(f"\n--- {fwhm}° ---")
    for name in MAPS:
        data = json.loads((OUT / f"temps2_{name}_{fwhm}deg.json").read_text())
        row = []
        for s in SETS:
            T = np.array(data[s])
            b = np.abs(lb[s][:, 1])
            m_all = m1(T)
            sel = b > 20
            m_hi = m1(T[sel]) if sel.sum() >= 20 else np.nan
            dev45 = (m_all / T11 - 1) * 100
            row.append((m_all, m_hi, sel.sum(), dev45))
            print(f"  {name:10s} {s:10s}: M1={m_all:.5f} (dev11/45 {dev45:+6.1f}%)  "
                  f"|b|>20(n={sel.sum():2d}) M1={m_hi:.5f}")
        table[(fwhm, name)] = row

print("\n=== G88 極端節點檢查 (4.17° SMICA) ===")
data = json.loads((OUT / "temps2_SMICA_4.17deg.json").read_text())
T88 = np.array(data["G88"])
dT = T88 - T88.mean()
order = np.argsort(-np.abs(dT))
for i in order[:8]:
    print(f"  節點 {i:2d}: δT={dT[i]:+7.1f} μK  |δT|/A={abs(dT[i])/A:.3f}  "
          f"l={lb['G88'][i,0]:7.2f} b={lb['G88'][i,1]:+7.2f}")
# 剔除最極端 5 個後 M1
for k in [3, 5, 8]:
    keep = np.ones(len(T88), bool); keep[order[:k]] = False
    print(f"  剔除 {k} 個最極端: M1 = {m1(T88[keep]):.5f}")

print("\n=== 高斯空想 vs 11/45 (4.17°, |b|>20 σ) ===")
for name in MAPS:
    d = json.loads((OUT / f"temps2_{name}_4.17deg.json").read_text())
    sm = d["META"]["sigma_masked"]
    gnull = 0.7979 * sm / A
    print(f"  {name:10s}: σ_masked={sm:.1f} μK -> 高斯空想 {gnull:.5f} "
          f"(vs 11/45={T11:.5f}, dev {(gnull/T11-1)*100:+.2f}%)")

print("\n=== 跨地圖 spread (4.17°, A5 同 G88) ===")
for s in ["A5_60", "G88"]:
    vals = []
    for name in MAPS:
        d = json.loads((OUT / f"temps2_{name}_4.17deg.json").read_text())
        vals.append(m1(np.array(d[s])))
    spread = (max(vals) - min(vals)) / np.mean(vals) * 100
    print(f"  {s:10s}: {[f'{v:.5f}' for v in vals]}  spread={spread:.2f}%")

print("\nRESULT: 最終表完成")
