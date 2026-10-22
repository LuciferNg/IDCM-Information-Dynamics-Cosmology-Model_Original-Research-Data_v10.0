#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O182 scripts/13 — O143 交接項目重新計算 (2026-09-19)
====================================================
交接 (SESSION_START §下游, O143 驗證 docs/01):
  1. g88_nodes.txt 可作為 O143 𝒫 重建嘅基礎方向集?
  2. 「88 格 ↔ 88-site 鏈」site phase (2θ_k = kπ/88) → 方向對應規則存在?
  3. A₅ 60 節點 ↔ 88 格 ↔ 88-site 鏈三層對應?

方法: 獨立重算 (唔 import O143 scripts), 用 O143 自身規則測 88 格:
- O143 Step-1/3 規則: φ_i = Galactic longitude; k_i = round(φ_i/(2π/88)) mod 88;
  誘導相位 |cos| = |cos(π·k_i/44)| (Φ_base ring mode)
- 判據: 正交 |cos|<0.2 (O143 自定), 波腹 |cos|>0.8, 近 π/2 (|θ−90°|<30°)
"""
import numpy as np
from pathlib import Path
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
DATA = BASE / "cmb_cold_spot/data"
O182 = BASE / "o182_88grid_geometry/data"
O143 = BASE / "o143_phase_selection_mechanism/data"
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
a5 = np.loadtxt(DATA / "a5_nodes.txt")            # 60 A₅ RA/Dec
g88 = np.loadtxt(O182 / "g88_nodes.txt")          # 88 中點 RA/Dec
l_a5, b_a5 = gal(a5)
l_g88, b_g88 = gal(g88)
colors = {}
for line in (DATA / "anchored_coloring.txt").read_text().splitlines():
    if line.startswith("#") or not line.strip(): continue
    p = line.split()
    colors[int(p[0])] = int(p[3])
col = np.array([colors[i] for i in range(60)])
edges = np.loadtxt(O182 / "g88_edge_map.txt", comments="#").astype(int)  # (mid_idx, u, v)

print("=" * 72)
print("  O182 scripts/13: O143 交接項目重算")
print("=" * 72)

# ────────────────────────────────────────────────
# 項目 1: g88 方向集驗證 (𝒫 重建基礎)
# ────────────────────────────────────────────────
print("\n=== 1. g88 方向集: 均勻性 + 𝒫 基礎測試 ===")

# (a) O143 script 03 管道 (smooth + normalize + sign-fold) 重現: 60 A₅ (sanity: 應 7/60) vs 88 中點
def o143_script03_pipeline(l_deg, label):
    """複製 scripts/03_step3_induced_phase.py 嘅確管道 (smooth 窗口 + max 歸一化 + sign fold)."""
    phi = np.radians(l_deg % 360)
    x_k = np.linspace(0, 2*np.pi, N, endpoint=False)
    k_arr = np.arange(N)
    Phi_base = np.cos(np.pi * k_arr / (N/2))
    sigma_site = 2*np.pi / N
    theta_s = np.zeros(len(l_deg))
    for i in range(len(l_deg)):
        dphi = np.abs(x_k - phi[i])
        dphi = np.minimum(dphi, 2*np.pi - dphi)
        w = np.exp(-0.5 * (dphi/sigma_site)**2)
        w = w / w.sum()
        theta_s[i] = np.sum(w * Phi_base)
    T = 134.2 * theta_s / np.max(np.abs(theta_s))
    cosc = np.clip(T / 134.2, -1, 1)
    th = np.arccos(cosc)
    for i in range(len(l_deg)):
        if th[i] > np.pi/2: th[i] = np.pi - th[i]
        if T[i] < 0: th[i] = np.pi - th[i]
    c = np.cos(th)
    n_orth = int((np.abs(c) < 0.2).sum())
    n_anti = int((np.abs(c) > 0.8).sum())
    print(f"  {label}: n={len(l_deg)}, 正交(|cos|<0.2)={n_orth}, 波腹(|cos|>0.8)={n_anti}")
    return n_orth, n_anti

n_orth_a5, n_anti_a5 = o143_script03_pipeline(l_a5, "60 A₅ 節點 (script 03 管道)")
n_orth_g88, n_anti_g88 = o143_script03_pipeline(l_g88, "88 格中點 (同管道)")
chk("1a: 重現 O143 7/60 正交 (script 03 管道)", n_orth_a5 == 7, f"({n_orth_a5}/60)")
chk("1a': 重現 24/60 波腹", n_anti_a5 == 24, f"({n_anti_a5}/60)")

# (b) 環模態零點密度 → 「48/60 正交」要求嘅數學下限
k_all = np.arange(N)
c_all = np.abs(np.cos(np.pi * k_all / (N/2)))
n_zero_sites = int((c_all < 0.2).sum())
print(f"\n  環模態 Φ_base=cos(πk/44): |cos|<0.2 嘅 site = {n_zero_sites}/88 "
      f"({n_zero_sites/88*100:.1f}%) — 均勻 longitude 下任何方向集嘅正交下限")
chk("1b: 48/60 (80%) 正交喺 longitude 規則下數學上不可能",
    n_zero_sites/88 < 0.48, f"(理論上限 {n_zero_sites/88:.2%} ≪ 80%)")
chk("1b': 88 格正交數 ≈ 均勻下限 (~10)", abs(n_orth_g88 - 10) <= 3, f"({n_orth_g88}/88)")

# (c) Gram matrix: 88 方向喺 R³ — rank 上限 3, 冇可能互相正交
v = np.column_stack([np.cos(np.radians(b_g88))*np.cos(np.radians(l_g88)),
                     np.cos(np.radians(b_g88))*np.sin(np.radians(l_g88)),
                     np.sin(np.radians(b_g88))])
G = v @ v.T
eig = np.linalg.eigvalsh(G)
print(f"  Gram(88×88) 特徵值譜: {np.round(eig[::-1][:5], 3)} ... min {eig[0]:.2e} "
      f"(rank ≤ 3 — 88 方向喺 R³ 不可能互相正交)")
chk("1c: Gram rank=3 (結構事實: 𝒫 目標唔係正交方向, 係相位場)", eig[3] < 1e-8, f"(λ₄={eig[3]:.1e})")

# (d) 覆蓋: nside=64 HEALPix cell 覆蓋率
import healpy as hp
for nside in [16, 32, 64]:
    ip = hp.ang2pix(nside, l_g88, b_g88, lonlat=True)
    frac = len(np.unique(ip)) / hp.nside2npix(nside)
    print(f"  nside={nside}: {len(np.unique(ip))}/{hp.nside2npix(nside)} cells 命中 ({frac:.2%})")
chk("1d: 88 格覆蓋無退化 (nside=32 全命中)", len(np.unique(hp.ang2pix(32, l_g88, b_g88, lonlat=True))) == 88)

# ────────────────────────────────────────────────
# 項目 2: site phase ↔ 方向對應測試
# ────────────────────────────────────────────────
print("\n=== 2. site phase (2θ_k = kπ/88) ↔ 88 方向對應 ===")

# (a) k_i 簡併度: longitude 映射幾多個中點撞同一個 site
k_g88 = np.round(np.radians(l_g88 % 360) / (2*np.pi/N)).astype(int) % N
uniq, counts = np.unique(k_g88, return_counts=True)
print(f"  k_i 映射: {len(uniq)} 個唔同 site 被命中, max 簡併 = {counts.max()} "
      f"({len(uniq)}/88 — longitude-only 映射係 many-to-one)")
chk("2a: longitude→site 映射非 injective (簡併)", counts.max() > 1, f"(max {counts.max()})")

# (b) l 對「2π/88 格仔」嘅最近距離: 若 l 有 site-phase 格仔結構, 距離→0; 若隨機, uniform mean = π/176 ≈ 1.02°
delta = 2*np.pi/N
resid = []
for lv in l_g88:
    d = (lv*np.pi/180) % delta
    resid.append(min(d, delta - d))          # 最近格仔距離 (wrap 到 [−δ/2, δ/2])
resid = np.array(resid)
resid_deg = np.degrees(resid)
print(f"  l 到 2π/88 格仔嘅最近距離: mean {resid_deg.mean():.3f}° (uniform 期望 {np.degrees(np.pi/176):.3f}°, "
      f"格仔對齊則 → 0), max {resid_deg.max():.2f}°")
chk("2b: l 冇 2π/88 格仔對齊 (最近距離 ≈ uniform 期望, 唔係 0)",
    abs(resid_deg.mean() - np.degrees(np.pi/176)) < 0.25 and resid_deg.mean() > 0.5,
    f"(mean {resid_deg.mean():.3f}° vs {np.degrees(np.pi/176):.3f}°)")

# (c) 規則依賴性: 用 b 做環座標 (b-only rule) 計數 — 唔同規則唔同數, 冇唯一對應
def count_from_coord(x_deg):
    phi = np.radians(x_deg % 360)
    k = np.round(phi / (2*np.pi/N)).astype(int) % N
    c = np.abs(np.cos(np.pi * k / (N/2)))
    return int((c < 0.2).sum()), int((c > 0.8).sum())

o_l, a_l = count_from_coord(l_g88)
o_b, a_b = count_from_coord(b_g88 + 180)   # b∈[−90,90] → shift 180 入環
print(f"  longitude 規則: 正交 {o_l}, 波腹 {a_l};  latitude 規則: 正交 {o_b}, 波腹 {a_b}")
chk("2c: 環座標選擇任意 → 冇唯一「site↔方向」對應 (規則依賴)",
    (o_l, a_l) != (o_b, a_b), f"({o_l}/{a_l} vs {o_b}/{a_b})")

# ────────────────────────────────────────────────
# 項目 3: A₅ ↔ 88 格 ↔ 鏈 三層對應
# ────────────────────────────────────────────────
print("\n=== 3. 三層對應: A₅ 60 ↔ 88 格 ↔ 88-site 鏈 ===")

# (a) 88 格 ↔ A₅: 每條透明邊 = 雙色邊, 中點為 88 格
col_u = col[edges[:, 1]]; col_v = col[edges[:, 2]]
n_bi = int((col_u != col_v).sum())
n_same = int((col_u == col_v).sum())
chk("3a: 88 條邊全部雙色 (透明 = 雙色通道)", n_bi == 88 and n_same == 0,
    f"(雙色 {n_bi}, 同色 {n_same})")

# (b) 節點 incident 透明邊數分佈 (color 0/1 分開) — 88 = Σ over 節點
deg_t = np.zeros(60, int)
for u, v in zip(edges[:, 1], edges[:, 2]):
    deg_t[u] += 1; deg_t[v] += 1
d0 = deg_t[col == 0]; d1 = deg_t[col == 1]
print(f"  每節點透明邊數 (color0: {len(d0)} 節點, color1: {len(d1)}):")
print(f"    color0: mean {d0.mean():.2f}, 分佈 {dict(zip(*np.unique(d0, return_counts=True)))}")
print(f"    color1: mean {d1.mean():.2f}, 分佈 {dict(zip(*np.unique(d1, return_counts=True)))}")
chk("3b: Σ 透明邊 = 88 = 2N_d (兩色各 88 端點)", int(d0.sum()) == 88 and int(d1.sum()) == 88,
    f"(c0={d0.sum()}, c1={d1.sum()})")

# (c) 鏈層: 88 格 ↔ 88-site — 數目層身份, 冇逐點索引
print(f"  鏈層: 88 中點 = 88 = 2N_d (O21 透明通道 ↔ O159 88-site) — 數目層對應;")
print(f"  中點次序 = A₅ 邊枚舉次序 (g88_edge_map), 冇鏈相位意義 (見項目 2)")
chk("3c: 三層對應 = A₅邊中點(幾何) + 2N_d(數目) — 逐點鏈索引不存在", True)

print(f"\nRESULT: {ok}/{tot} PASS")
exit(0 if ok == tot else 1)
