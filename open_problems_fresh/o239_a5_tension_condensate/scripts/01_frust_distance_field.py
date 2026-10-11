#!/usr/bin/python3
"""O239 — Script 01: 挫阻距離場 MC null（幾何層 signature 盲測）
========================================================================
問題 5（O239/01_problem_record）: 「挫阻扣減」(88 = 120 − 32) 喺譜層有冇 signature?
本 script = P1 第一支 probe —— 幾何層:
  88 節點（A₅ 網 88 條透明邊中點, g88_nodes.txt）每個有「到最近 32 挫阻中點」嘅角距 d_i。
  O238 scripts/29 只報 median = 16.107° 冇 MC 對照。本 script 補完整分佈 + MC null。

預註冊判據（跑前凍結，threshold 零放寬）:
  C1 挫阻距離場空模型 null: obs median(d_i) 落入 MC(10⁴ 隨機 88 點 → 同一 32 挫阻中點) 嘅
     [0.5%, 99.5%] 兩尾區間內 ⟹ 挫阻距離冇空間 signature（PASS = 唔顯著）
  C2 排斥側: obs median > MC 97.5th ⟹ 挫阻系統性遠離 88 節點（缺陷-透明排斥, 有意義）
  C3 聚集側: obs median < MC 2.5th ⟹ 挫阻系統性接近 88 節點（缺陷-透明聚集, 有意義）
  C4 對照: 88 節點自身最近鄰 median vs MC 隨機 88 點最近鄰（O182 docs/02 已知 88 格比隨機更均勻,
    呢度重現作為 sanity, 同時係「挫阻距離尺度同節點密度尺度比較」嘅參考）
  C5 尺度對照: node→frust median vs 88 節點自身最近鄰 median（若相等, 挫阻融入節點密度;
    若 node→frust 明顯更大 = 挫阻「避開」節點）

盲測紀律: 判據/閾值喺 docstring 預註冊; 唔 fit target; MC seed 固定可重現;
只報機制預言, 唔報「湊到嘅數字」。
"""
import json, math
import numpy as np
from pathlib import Path

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
DATA = ROOT / "o182_88grid_geometry/data"

rng = np.random.default_rng(20261012)
N_MC = 10000
ALPHA = 0.005  # 兩尾 0.5%/99.5%

checks = []
def chk(name, cond, detail=""):
    checks.append((name, bool(cond), detail))
    print(f"  [{'PASS' if cond else 'XX '}] {name} {detail}")

def sph(ra, dec):
    ra, dec = np.radians(ra), np.radians(dec)
    return np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])

def angmat(v):
    d = np.arccos(np.clip(v @ v.T, -1, 1))
    return np.degrees(d)

# ── 讀數據 ──
nodes = np.loadtxt(DATA / "g88_nodes.txt")            # 88 x (RA, Dec)
frust = np.loadtxt(DATA / "g32_frustration_midpoints.txt")  # 32 x (RA, Dec)
assert nodes.shape == (88, 2) and frust.shape == (32, 2), (nodes.shape, frust.shape)

Vn = sph(nodes[:, 0], nodes[:, 1])
Vf = sph(frust[:, 0], frust[:, 1])

# 88 節點 → 最近挫阻角距（實測）—— 直接叉乘, 唔經 angmat（angmat 會再乘 Vᵀ）
D_nf = np.degrees(np.arccos(np.clip(Vn @ Vf.T, -1, 1)))   # 88 x 32
d_i = D_nf.min(axis=1)            # 每個節點到最近挫阻
d_med_obs = float(np.median(d_i))

# 88 節點自身最近鄰（實測, 密度尺度對照）—— 直接叉乘（angmat 唔可以食已乘矩陣）
D_nn = np.degrees(np.arccos(np.clip(Vn @ Vn.T, -1, 1)))
np.fill_diagonal(D_nn, np.inf)
nn_obs = float(np.median(D_nn.min(axis=1)))

# ── MC null: 隨機 88 點（均勻球面）→ 同一 32 挫阻中點 ──
def uniform_sphere(k, rng):
    z = rng.uniform(-1, 1, k)
    phi = rng.uniform(0, 2*np.pi, k)
    r = np.sqrt(1 - z*z)
    return np.column_stack([r*np.cos(phi), r*np.sin(phi), z])

mc_med = np.empty(N_MC)
mc_nn = np.empty(N_MC)
for i in range(N_MC):
    R = uniform_sphere(88, rng)
    # 最近挫阻
    dR = np.degrees(np.arccos(np.clip(R @ Vf.T, -1, 1)))
    mc_med[i] = np.median(dR.min(axis=1))
    # 自身最近鄰
    dRR = np.degrees(np.arccos(np.clip(R @ R.T, -1, 1)))
    np.fill_diagonal(dRR, np.inf)
    mc_nn[i] = np.median(dRR.min(axis=1))

lo, hi = np.percentile(mc_med, [ALPHA*100, (1-ALPHA)*100])
pct = (mc_med < d_med_obs).mean()
z = (d_med_obs - mc_med.mean()) / mc_med.std()
nn_lo, nn_hi = np.percentile(mc_nn, [ALPHA*100, (1-ALPHA)*100])

print("="*78)
print("O239 scripts/01 — 挫阻距離場 MC null（幾何層 signature）")
print("="*78)
print(f"\n88 節點 → 最近挫阻中點角距 d_i:")
print(f"  min={d_i.min():.3f}°  median={d_med_obs:.3f}°  max={d_i.max():.3f}°")
print(f"  <20°: {(d_i<20).sum()}/88,  <26°: {(d_i<26).sum()}/88")
print(f"\n88 節點自身最近鄰 median = {nn_obs:.3f}°")
print(f"\nMC null (10⁴ 隨機 88 點 → 同一 32 挫阻中點):")
print(f"  median(d_i) MC: mean={mc_med.mean():.3f}°  std={mc_med.std():.3f}°  "
      f"[{lo:.3f}, {hi:.3f}]")
print(f"  觀察 median = {d_med_obs:.3f}°  →  percentile={pct*100:.2f}%  z={z:+.2f}")
print(f"\nMC null 自身最近鄰: mean={mc_nn.mean():.3f}°  [{nn_lo:.3f}, {nn_hi:.3f}]")
print(f"  觀察 88 格最近鄰 = {nn_obs:.3f}°")

print("\n── 預註冊判據 ──")
chk("C1 挫阻距離 null（obs ∈ [0.5%,99.5%] → 冇 signature）",
    lo <= d_med_obs <= hi,
    f"obs={d_med_obs:.3f} MC=[{lo:.3f},{hi:.3f}]")
chk("C2 排斥側（obs > MC 97.5th → 挫阻遠離，結構性）",
    d_med_obs > np.percentile(mc_med, 97.5),
    f"obs={d_med_obs:.3f} vs 97.5th={np.percentile(mc_med,97.5):.3f}")
chk("C3 聚集側（obs < MC 2.5th → 挫阻接近，結構性）",
    d_med_obs < np.percentile(mc_med, 2.5),
    f"obs={d_med_obs:.3f} vs 2.5th={np.percentile(mc_med,2.5):.3f}")
chk("C4 對照: 88 格自身最近鄰比 MC 更均勻（重現 O182 docs/02, sanity）",
    nn_obs > np.percentile(mc_nn, 99.5),
    f"obs_nn={nn_obs:.3f} vs MC 99.5th={np.percentile(mc_nn,99.5):.3f}")
chk("C5 尺度對照: 挫阻距離 scale vs 節點密度 scale",
    abs(d_med_obs - nn_obs) < 2.0,
    f"d_med={d_med_obs:.3f} vs nn={nn_obs:.3f}")

out = {
    "d_i": d_i.tolist(),
    "d_med_obs": d_med_obs, "d_min": float(d_i.min()), "d_max": float(d_i.max()),
    "nn_obs": nn_obs,
    "mc_median_mean": float(mc_med.mean()), "mc_median_std": float(mc_med.std()),
    "mc_lo": float(lo), "mc_hi": float(hi),
    "obs_percentile": float(pct), "z": float(z),
    "mc_nn_mean": float(mc_nn.mean()), "mc_nn_lo": float(nn_lo), "mc_nn_hi": float(nn_hi),
    "N_MC": N_MC,
}
outfile = Path(__file__).parent.parent / "data" / "01_frust_distance_field.json"
outfile.parent.mkdir(parents=True, exist_ok=True)
with open(outfile, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

n_pass = sum(1 for _, c_, _ in checks if c_)
print(f"\nRESULT: {n_pass}/{len(checks)} checks passed")