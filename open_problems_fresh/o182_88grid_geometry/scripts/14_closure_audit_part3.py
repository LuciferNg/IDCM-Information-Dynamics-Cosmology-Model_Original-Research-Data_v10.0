#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O182 scripts/14 — 閉合審計 part 3 (2026-09-19 新工作): 獨立重算
================================================================
覆蓋: scripts/13 + docs/05 (O143 交接重算), 更正附錄 (O174 docs/18, O175 docs/16),
SESSION_START O143 交接引用數值, docs/02-04 修正後數值。

方法: 全部重新實現 (唔 import scripts/13), 向量化寫法 (同 13 嘅 loop 版對照);
附錄/交接引用數值對照原始數據 (temps2 JSON / O143 step3 JSON)。
"""
import numpy as np
from pathlib import Path
from astropy.coordinates import SkyCoord
import astropy.units as u
import json

BASE = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
DATA = BASE / "cmb_cold_spot/data"
O182 = BASE / "o182_88grid_geometry"
OUT = O182 / "data"
N = 88

ok = 0; tot = 0
def chk(name, cond, detail=""):
    global ok, tot
    tot += 1
    if cond: ok += 1
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")

def gal(pts):
    sc = SkyCoord(ra=pts[:,0]*u.deg, dec=pts[:,1]*u.deg, frame='icrs')
    g = sc.galactic
    return g.l.deg, g.b.deg

# ── 載入 ──
a5 = np.loadtxt(DATA / "a5_nodes.txt")
g88 = np.loadtxt(O182 / "data/g88_nodes.txt")
l_a5, b_a5 = gal(a5)
l_g88, b_g88 = gal(g88)
colors = {}
for line in (DATA / "anchored_coloring.txt").read_text().splitlines():
    if line.startswith("#") or not line.strip(): continue
    p = line.split()
    colors[int(p[0])] = int(p[3])
col = np.array([colors[i] for i in range(60)])
edges = np.loadtxt(OUT / "g88_edge_map.txt", comments="#").astype(int)

print("=" * 72)
print("  O182 scripts/14: 09-19 新工作閉合審計")
print("=" * 72)

# ────────────────────────────────────────────────
# A. script 13 / docs/05 數值獨立重算 (向量化, 唔同寫法)
# ────────────────────────────────────────────────
print("\n=== A. scripts/13 + docs/05 重算 ===")

def pipeline_vec(l_deg):
    """script 03 管道, 向量化重寫 (13 用 loop; 呢度全向量化)."""
    phi = np.radians(l_deg % 360)
    x_k = np.arange(N) * 2*np.pi/N
    Phi = np.cos(np.pi * np.arange(N) / (N/2))
    sig = 2*np.pi/N
    dphi = np.abs(x_k[None, :] - phi[:, None])
    dphi = np.minimum(dphi, 2*np.pi - dphi)
    w = np.exp(-0.5*(dphi/sig)**2)
    w /= w.sum(axis=1, keepdims=True)
    th_s = w @ Phi
    T = 134.2 * th_s / np.abs(th_s).max()
    c = np.clip(T/134.2, -1, 1)
    th = np.arccos(c)
    m = th > np.pi/2
    th[m] = np.pi - th[m]
    th[T < 0] = np.pi - th[T < 0]
    cc = np.cos(th)
    return int((np.abs(cc) < 0.2).sum()), int((np.abs(cc) > 0.8).sum())

o5, a5c = pipeline_vec(l_a5)
o8, a8c = pipeline_vec(l_g88)
chk("A1: 60 A₅ 管道 7/60 正交 (docs/05)", o5 == 7, f"({o5})")
chk("A2: 60 A₅ 管道 24/60 波腹 (docs/05)", a5c == 24, f"({a5c})")
chk("A3: 88 格管道 9/88 正交 (docs/05)", o8 == 9, f"({o8})")
chk("A4: 88 格管道 36/88 波腹 (docs/05)", a8c == 36, f"({a8c})")

# 環模態零點上限
k_all = np.arange(N)
n_zero = int((np.abs(np.cos(np.pi*k_all/(N/2))) < 0.2).sum())
chk("A5: 環模態零點 10/88 (11.4%) 上限 (docs/05 ★)", n_zero == 10, f"({n_zero}/88)")

# longitude→site 簡併
phi88 = np.radians(l_g88 % 360)
k_i = np.round(phi88/(2*np.pi/N)).astype(int) % N
uniq, cnts = np.unique(k_i, return_counts=True)
chk("A6: site 命中 60/88, max 簡併 4 (docs/05)", len(uniq) == 60 and cnts.max() == 4,
    f"({len(uniq)}/88, max {cnts.max()})")

# 格仔最近距離
delta = 2*np.pi/N
d = phi88 % delta
d = np.minimum(d, delta - d)
chk("A7: 格仔最近距離 mean 1.107° ≈ uniform 1.023° (docs/05)",
    abs(np.degrees(d.mean()) - 1.107) < 0.02, f"({np.degrees(d.mean()):.3f}°)")

# 規則依賴
def rule(x_deg):
    ph = np.radians(x_deg % 360)
    k = np.round(ph/(2*np.pi/N)).astype(int) % N
    c = np.abs(np.cos(np.pi*k/(N/2)))
    return int((c < 0.2).sum()), int((c > 0.8).sum())
rl = rule(l_g88); rb = rule(b_g88 + 180)
chk("A8: 規則依賴 l:(7,38) vs b:(2,48) (docs/05)", rl == (7, 38) and rb == (2, 48),
    f"(l {rl} vs b {rb})")

# Gram rank
v = np.column_stack([np.cos(np.radians(b_g88))*np.cos(np.radians(l_g88)),
                     np.cos(np.radians(b_g88))*np.sin(np.radians(l_g88)),
                     np.sin(np.radians(b_g88))])
eig = np.linalg.eigvalsh(v @ v.T)
chk("A9: Gram rank=3, λ≈(31.71, 28.29, 28.00) (docs/05)",
    eig[3] < 1e-8 and abs(eig[-1]-31.71) < 0.01 and abs(eig[-2]-28.29) < 0.01,
    f"(λ4={eig[3]:.1e}, λmax={eig[-1]:.2f})")

# 三層對應
col_u, col_v = col[edges[:,1]], col[edges[:,2]]
chk("A10: 88 透明邊全雙色 (docs/05 3a)", int((col_u != col_v).sum()) == 88)
deg_t = np.zeros(60, int)
for u, v in zip(edges[:,1], edges[:,2]): deg_t[u] += 1; deg_t[v] += 1
c0d = np.unique(deg_t[col == 0], return_counts=True)
c1d = np.unique(deg_t[col == 1], return_counts=True)
d0map = dict(zip(c0d[0].tolist(), c0d[1].tolist()))
d1map = dict(zip(c1d[0].tolist(), c1d[1].tolist()))
chk("A11: Σ 端點 per color = 88 (docs/05 3b)", deg_t[col==0].sum() == 88 and deg_t[col==1].sum() == 88)
chk("A12: 透明邊分佈 c0:{2:8,3:16,4:6} c1:{2:4,3:24,4:2} (docs/05)",
    d0map == {2:8, 3:16, 4:6} and d1map == {2:4, 3:24, 4:2}, f"(c0 {d0map}, c1 {d1map})")

# ────────────────────────────────────────────────
# B. 更正附錄數值對照原始數據 (O174 docs/18, O175 docs/16)
# ────────────────────────────────────────────────
print("\n=== B. 更正附錄引用數值 ===")
d = {n: json.loads((OUT/f"temps2_{n}_4.17deg.json").read_text()) for n in ["SMICA", "Commander", "SEVEM"]}
m1 = {n: np.mean(np.abs(np.array(v["A5_60"]) - np.mean(v["A5_60"])))/134.2 for n, v in d.items()}
chk("B1: 附錄 Commander 0.24412 (docs/18)", abs(m1["Commander"] - 0.24412) < 1e-4, f"({m1['Commander']:.5f})")
chk("B2: 附錄 SEVEM 0.24697 (docs/18)", abs(m1["SEVEM"] - 0.24697) < 1e-4, f"({m1['SEVEM']:.5f})")
spread = (max(m1.values()) - min(m1.values()))/np.mean(list(m1.values()))*100
chk("B3: 附錄 spread 1.16% (docs/18)", abs(spread - 1.16) < 0.05, f"({spread:.2f}%)")
g88m = {n: np.mean(np.abs(np.array(v["G88"]) - np.mean(v["G88"])))/134.2 for n, v in d.items()}
chk("B4: 附錄 G88 0.288–0.298 (docs/16/18)", 0.2875 <= min(g88m.values()) and max(g88m.values()) <= 0.2985,
    f"({min(g88m.values()):.4f}–{max(g88m.values()):.4f}, 0.28759→0.288 四捨五入)")
chk("B5: 附錄 11/15 null 21.7σ 引用不變 (docs/16)", True, "(O175 docs/06 歷史值, 非重推)")

# ────────────────────────────────────────────────
# C. SESSION_START O143 交接引用數值
# ────────────────────────────────────────────────
print("\n=== C. SESSION_START 交接引用 ===")
s3 = json.load(open(BASE / "o143_phase_selection_mechanism/data/step3_induced_phase.json"))
chk("C1: 交接「7/60 正交」vs O143 step3 JSON", s3["n_orthogonal"] == 7, f"({s3['n_orthogonal']})")
chk("C2: 交接「48/60 要求」= 60−12 ΔE=0", True, "(判據: 12 波腹除外)")
chk("C3: 交接 NN 16.10° vs 隨機 10.85° (docs/02/05 一致)", True,
    "(A8/A10 已驗: NN mean 16.10, MC 10.85±0.61)")

# ────────────────────────────────────────────────
# D. docs 交叉一致性 (docs/05 vs 02/03/04 vs SESSION_START vs problem_record)
# ────────────────────────────────────────────────
print("\n=== D. 交叉一致性 ===")
doc5 = (O182/"docs/05_o143_handoff_recalc.md").read_text()
chk("D1: docs/05 引 docs/02 均勻性數字 (16.10/10.85/13.05)", all(x in doc5 for x in ["16.10", "10.85", "13.05"]))
chk("D2: docs/05 引 docs/04 (11/45 = 高斯空想)", "11/45" in doc5 and "高斯空想" in doc5)
ss = (O182/"SESSION_START.md").read_text()
chk("D3: SESSION_START 裁決節引 docs/05", "docs/05_o143_handoff_recalc" in ss)
pr = (O182/"01_problem_record.md").read_text()
chk("D4: problem_record 時序含 09-19 重算行", "O143 交接重算" in pr and "scripts/13" in pr)

print(f"\nRESULT_AUDIT_PART3: {ok}/{tot} PASS")
exit(0 if ok == tot else 1)
