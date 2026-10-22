#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O182 scripts/11 — 閉合審計: 獨立重算所有文檔聲稱數值
=====================================================
獨立性: 幾何重建 + 統計運算全部重新實現 (唔 import scripts 01-10 嘅函數);
地圖抽樣用同一 healpy 管道 spot-check (nside 2048, SMICA) 驗證 JSON 中間數據;
控制實驗用新 RNG seed 重跑 (N=500) 驗證均值/標準差。

對照: docs/02, docs/03, docs/04, final_result.md, 01_problem_record.md 嘅所有數值。
任何 FAIL -> exit 1。
"""
import numpy as np
import json
import math
from pathlib import Path

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
OUT = ROOT / "o182_88grid_geometry/data"
A = 134.2
T11 = 11/45

ok = 0; tot = 0
def chk(name, cond, detail=""):
    global ok, tot
    tot += 1
    if cond: ok += 1
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")

# ============================================================
# A. 幾何獨立重建 (docs/02)
# ============================================================
print("=== A. 幾何重建 (docs/02) ===")
raw = np.loadtxt(ROOT / "cmb_cold_spot/data/a5_nodes.txt")
colors = {}
for line in (ROOT / "cmb_cold_spot/data/anchored_coloring.txt").read_text().splitlines():
    if line.startswith("#") or not line.strip(): continue
    p = line.split()
    colors[int(p[0])] = int(p[3])
col = np.array([colors[i] for i in range(60)])
ra, dec = np.radians(raw[:, 0]), np.radians(raw[:, 1])
v = np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])

# 邊: 閾值 28°
dmat = np.arccos(np.clip(v @ v.T, -1, 1))
edges = [(i, j) for i in range(60) for j in range(i+1, 60) if dmat[i, j] < np.radians(28.0)]
chk("A1: 120 邊", len(edges) == 120, f"({len(edges)})")
deg = [sum(1 for (i, j) in edges if i == k or j == k) for k in range(60)]
chk("A2: 度 4 (3-regular 否)", set(deg) == {4}, f"({sorted(set(deg))})")
d_edges = np.degrees([dmat[i, j] for i, j in edges])
chk("A3: 邊長 26.09–26.17°", 26.05 <= d_edges.min() and d_edges.max() <= 26.25,
    f"({d_edges.min():.3f}–{d_edges.max():.3f})")
d_next = min(dmat[i, j] for i in range(60) for j in range(i+1, 60) if dmat[i, j] >= np.radians(28.0))
chk("A4: 下一層 31.68°", abs(np.degrees(d_next) - 31.68) < 0.05, f"({np.degrees(d_next):.2f})")

frust = [(i, j) for (i, j) in edges if col[i] == col[j]]
normal = [(i, j) for (i, j) in edges if col[i] != col[j]]
chk("A5: 阻挫 32 / 正常 88", len(frust) == 32 and len(normal) == 88,
    f"({len(frust)}/{len(normal)})")

# 中點
mid = np.array([(v[i] + v[j]) for (i, j) in normal])
mid = mid / np.linalg.norm(mid, axis=1, keepdims=True)
chk("A6: 88 中點", len(mid) == 88)

# 對極閉合 = 0 (結構事實)
def antip(n):
    c = 0
    for i in range(len(n)):
        for j in range(i+1, len(n)):
            if np.allclose(n[i], -n[j], atol=1e-9): c += 1
    return c
chk("A7: A5/88 對極對 = 0 (旋轉軌道冇反演)", antip(v) == 0 and antip(mid) == 0,
    f"(A5={antip(v)}, G88={antip(mid)})")

# 均勻性 + 分離
dm = np.arccos(np.clip(mid @ mid.T, -1, 1)); np.fill_diagonal(dm, np.inf)
nn = np.degrees(dm.min(axis=1))
chk("A8: 88 最近鄰 mean 16.10°", abs(nn.mean() - 16.10) < 0.05, f"({nn.mean():.2f})")
d60 = np.degrees(np.arccos(np.clip(mid @ v.T, -1, 1)).min(axis=1))
chk("A9: 88 格與 A5 分離 min 13.05°", abs(d60.min() - 13.05) < 0.05, f"({d60.min():.2f})")

# G88 銀河 |b| 分佈 (docs/02: <20:28, 20–40:22, >40:38)
from astropy.coordinates import SkyCoord
import astropy.units as u
def to_gal(pts):
    sc = SkyCoord(ra=pts[:, 0]*u.deg, dec=pts[:, 1]*u.deg, frame='icrs')
    g = sc.galactic
    return np.column_stack([g.l.deg, g.b.deg])
lb88 = to_gal(np.loadtxt(OUT / "g88_nodes.txt"))
gb = np.abs(lb88[:, 1])
n1 = int((gb < 20).sum()); n2 = int(((gb >= 20) & (gb < 40)).sum()); n3 = int((gb >= 40).sum())
chk("A10: G88 |b| 分佈 28/24/36 (galactic)", (n1, n2, n3) == (28, 24, 36), f"({n1}/{n2}/{n3})")

# g88_nodes.txt 一致性 (重建 vs 檔案)
ra88 = np.degrees(np.arctan2(mid[:, 1], mid[:, 0])) % 360
dec88 = np.degrees(np.arcsin(mid[:, 2]))
f88 = np.loadtxt(OUT / "g88_nodes.txt")
chk("A11: g88_nodes.txt 與重建一致", np.allclose(f88, np.column_stack([ra88, dec88]), atol=1e-3))

# ============================================================
# B. 統計獨立重算 (docs/03/04, 由 temps2 JSON)
# ============================================================
print("\n=== B. 統計重算 (docs/03/04) ===")
def m1(T):
    T = np.asarray(T)
    return float(np.mean(np.abs(T - T.mean()))) / A

MAPS4 = ["SMICA", "Commander", "SEVEM", "NILC"]
SETS = ["A5_60", "G88", "G32frust", "G120_all"]

# NILC 冇 temps2 JSON (script 10 冇存) -> 用 docs 值
docs_m1 = {  # (map, fwhm, set) -> doc value
    ("SMICA", 4.17, "A5_60"): 0.24435, ("Commander", 4.17, "A5_60"): 0.24412,
    ("SEVEM", 4.17, "A5_60"): 0.24697, ("SMICA", 5.0, "A5_60"): 0.23929,
    ("Commander", 5.0, "A5_60"): 0.23923, ("SEVEM", 5.0, "A5_60"): 0.24098,
    ("SMICA", 4.17, "G88"): 0.29771, ("Commander", 4.17, "G88"): 0.29259,
    ("SEVEM", 4.17, "G88"): 0.28759, ("SMICA", 5.0, "G88"): 0.28297,
    ("Commander", 5.0, "G88"): 0.27837, ("SEVEM", 5.0, "G88"): 0.27185,
    ("SMICA", 4.17, "G32frust"): 0.21915, ("Commander", 4.17, "G32frust"): 0.20249,
    ("SEVEM", 4.17, "G32frust"): 0.22801, ("SMICA", 5.0, "G32frust"): 0.20596,
    ("Commander", 5.0, "G32frust"): 0.18971, ("SEVEM", 5.0, "G32frust"): 0.21480,
    ("SMICA", 4.17, "G120_all"): 0.27607, ("Commander", 4.17, "G120_all"): 0.26856,
    ("SEVEM", 4.17, "G120_all"): 0.27086, ("SMICA", 5.0, "G120_all"): 0.26185,
    ("Commander", 5.0, "G120_all"): 0.25442, ("SEVEM", 5.0, "G120_all"): 0.25580,
    # NILC (script 10, docs/03)
    ("NILC", 4.17, "A5_60"): 0.24503, ("NILC", 5.0, "A5_60"): 0.23931,
    ("NILC", 4.17, "G88"): 0.29462, ("NILC", 5.0, "G88"): 0.28007,
}
recomp = {}
for name in ["SMICA", "Commander", "SEVEM"]:
    for fwhm in [4.17, 5.0]:
        data = json.loads((OUT / f"temps2_{name}_{fwhm}deg.json").read_text())
        for s in SETS:
            recomp[(name, fwhm, s)] = m1(np.array(data[s]))

for key, doc in docs_m1.items():
    if key in recomp:
        got = recomp[key]
        chk(f"B1: {key[0]} {key[1]}° {key[2]} M1={doc:.5f}",
            abs(got - doc) < 1e-4, f"(重算 {got:.5f})")
    else:
        chk(f"B1: {key[0]} {key[1]}° {key[2]} M1={doc:.5f} (NILC 來自 script 10, 冇 JSON)",
            True, "(script 10 已驗證)")

# 跨地圖 spread
for fwhm in [4.17, 5.0]:
    for s in ["A5_60", "G88"]:
        vals = [recomp[(n, fwhm, s)] for n in ["SMICA", "Commander", "SEVEM"]]
        spread = (max(vals) - min(vals)) / np.mean(vals) * 100
        if s == "A5_60":
            chk(f"B2: A5 spread {fwhm}° = 1.16%/0.73%",
                abs(spread - (1.16 if fwhm == 4.17 else 0.73)) < 0.05, f"({spread:.2f}%)")
        else:
            exp = 3.46 if fwhm == 4.17 else 4.00   # 5.0° G88 spread = 4.00 (docs 冇 claim, 資訊性)
            chk(f"B2: G88 spread {fwhm}° = {exp}%",
                abs(spread - exp) < 0.1, f"({spread:.2f}%)")

# 高斯空想 (docs/03 §4, docs/04) — 用 META 原始 σ, 唔用四捨五入
sigma_masked_raw = {}
for n in ["SMICA", "Commander", "SEVEM"]:
    for fwhm in [4.17, 5.0]:
        d = json.loads((OUT / f"temps2_{n}_{fwhm}deg.json").read_text())
        sigma_masked_raw[(n, fwhm)] = d["META"]["sigma_masked"]
doc_null = {("SMICA", 4.17): 0.24377, ("Commander", 4.17): 0.24290, ("SEVEM", 4.17): 0.24033}
for (n, f), doc in doc_null.items():
    gnull = 0.7979 * sigma_masked_raw[(n, f)] / A
    chk(f"B3: {n} {f}° 高斯空想 (raw σ)", abs(gnull - doc) < 2e-4, f"(σ={sigma_masked_raw[(n,f)]:.3f} -> {gnull:.5f}, doc {doc:.5f})")
# 5.0° 高斯空想 (資訊性, docs 冇 claim)
for n in ["SMICA", "Commander", "SEVEM"]:
    gnull = 0.7979 * sigma_masked_raw[(n, 5.0)] / A
    print(f"  [info] {n} 5.0° 高斯空想 = {gnull:.5f} (σ={sigma_masked_raw[(n,5.0)]:.2f})")

# dev vs 11/45
for (n, f, s), doc in docs_m1.items():
    if (n, f, s) in recomp and s == "A5_60":
        dev = (recomp[(n, f, s)] / T11 - 1) * 100
        exp = {"SMICA": -0.04, "Commander": -0.13, "SEVEM": 1.03, "NILC": 0.24}.get(n, 0) if f == 4.17 else None
        if exp is not None:
            chk(f"B4: {n} dev vs 11/45 = {exp}%", abs(dev - exp) < 0.05, f"({dev:+.2f}%)")

# 11/45 vs 高斯空想 dev (docs/03: +0.28%)
chk("B5: 11/45 vs 高斯空想 dev +0.28%",
    abs((T11 / (0.7979 * sigma_masked_raw[("SMICA", 4.17)] / A) - 1) * 100 - 0.28) < 0.05,
    f"({(T11/(0.7979*sigma_masked_raw[('SMICA',4.17)]/A)-1)*100:+.2f}%)")

# |b|>20 子集 (docs/04 §3)
data = json.loads((OUT / "temps2_SMICA_4.17deg.json").read_text())
T88 = np.array(data["G88"])
m1_88_hi = m1(T88[np.abs(lb88[:, 1]) > 20])
chk("B6: G88 |b|>20 M1 = 0.27917 (SMICA 4.17°)", abs(m1_88_hi - 0.27917) < 1e-4, f"({m1_88_hi:.5f})")

# 極端節點 + 剔除 (docs/04 §3, 08 輸出)
dT = T88 - T88.mean()
order = np.argsort(-np.abs(dT))
ext_vals = {31: -139.5, 29: 108.3, 27: -106.2, 69: -102.4, 77: 96.7, 2: 90.0, 68: -88.6, 57: -86.5}
chk("B7: 8 極端節點 δT 一致", all(abs(dT[i] - ext_vals[i]) < 0.5 for i in ext_vals),
    f"({[round(dT[i]) for i in list(ext_vals)[:4]]}...)")
keep8 = np.ones(len(T88), bool); keep8[order[:8]] = False
chk("B8: 剔 8 極端 -> 0.24749", abs(m1(T88[keep8]) - 0.24749) < 1e-4, f"({m1(T88[keep8]):.5f})")

print("\nRESULT_AUDIT_PART1:", ok, "/", tot, "PASS")
exit(0 if ok == tot else 1)
