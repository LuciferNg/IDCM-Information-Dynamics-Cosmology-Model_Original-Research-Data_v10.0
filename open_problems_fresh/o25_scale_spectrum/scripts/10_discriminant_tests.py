#!/usr/bin/env python3
"""
10_discriminant_tests.py — O25: Node9 大尺度冷區判別檢驗
=========================================================
用本地數據做 4 個判別測試 (唔使外部數據):

T1. 區域徑向剖面: node9 10°/15°/20° 半徑嘅徑向 T(r) — 睇係「中心凹陷」定「大尺度平台」
T2. 全天空冷區目錄排名: 全天空 flood-fill 大尺度冷區 (10° 平滑), node9 區域排名
T3. 熱環檢驗: 冷區外圍有冇熱環 (supervoid ISW signature)
T4. 冷斑區對照: node9 區域 vs 冷斑區域嘅剖面比較 (兩個獨立結構?)
"""
import healpy as hp
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u
import os, json

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
CACHE = os.path.join(BASE, "o25_scale_spectrum", "data", "smooth_cache_large")
OUT = os.path.join(BASE, "o25_scale_spectrum")
DATA = os.path.join(OUT, "data")

# node9 銀道座標 (正確!)
node9 = {"l": 214.92, "b": -31.16}
node0 = {"l": 209.00, "b": -57.00}

def angdist(l1, b1, l2, b2):
    l1, b1, l2, b2 = map(np.radians, [l1, b1, l2, b2])
    return np.degrees(np.arccos(np.clip(np.sin(b1)*np.sin(b2) + np.cos(b1)*np.cos(b2)*np.cos(l1-l2), -1, 1)))

# 用 Commander 15° 平滑 (大尺度結構清晰)
m = hp.read_map(os.path.join(CACHE, "Commander_smooth15.0.fits"), field=0)
nside = hp.get_nside(m)
npix = hp.nside2npix(nside)
print(f"地圖: Commander @15° smooth, nside={nside}, std={m.std()*1e6:.1f} μK")

# 用 nside=512 加速 (20° 圓盤喺 512 已經好準: 像素 ~7')
m_low = hp.ud_grade(m, 512)
nside_low = 512

# ============ T1: 徑向剖面 ============
print("\n" + "=" * 70)
print("T1: 徑向剖面 — node9 vs node0 (Commander 15° 平滑)")
print("=" * 70)
# 用 nside=512 (m_low 已建) — 20° 圓盤夠準
def radial_profile(l_deg, b_deg, max_r=40, step=2):
    vec = hp.ang2vec(l_deg, b_deg, lonlat=True)
    rings = []
    for r0 in range(0, max_r, step):
        r1 = r0 + step
        # 環帶: 內半徑 r0, 外半徑 r1
        disc_outer = hp.query_disc(nside_low, vec, np.radians(r1))
        if r0 == 0:
            ring = disc_outer
        else:
            disc_inner = hp.query_disc(nside_low, vec, np.radians(r0))
            ring = np.setdiff1d(disc_outer, disc_inner)
        rings.append((r0+step/2, m_low[ring].mean()*1e6, m_low[ring].std()*1e6, len(ring)))
    return rings

print(f"{'半徑':>8} | {'node9 T':>10} | {'node0 T':>10} | {'node9-n0':>10}")
prof9 = radial_profile(node9["l"], node9["b"])
prof0 = radial_profile(node0["l"], node0["b"])
for (r9, t9, s9, n9), (r0, t0, s0, n0) in zip(prof9, prof0):
    print(f"{r9:>6.1f}° | {t9:>+10.2f} | {t0:>+10.2f} | {t9-t0:>+10.2f}")

# 中心 vs 外圍 (熱環檢驗)
center9 = prof9[0][1]  # 0-2°
outer9 = prof9[-1][1]  # 38-40°
center0 = prof0[0][1]
outer0 = prof0[-1][1]
print(f"\nnode9: 中心(0-2°)={center9:+.2f} 外圍(38-40°)={outer9:+.2f}  Δ={center9-outer9:+.2f}")
print(f"node0: 中心(0-2°)={center0:+.2f} 外圍(38-40°)={outer0:+.2f}  Δ={center0-outer0:+.2f}")

# ============ T2: 全天空冷區目錄 ============
print("\n" + "=" * 70)
print("T2: 全天空大尺度冷區目錄 (Commander 15°, 20° 半徑圓盤)")
print("=" * 70)
rng = np.random.default_rng(42)
# 全天空隨機 300 個 20° 圓盤 (夠統計, 每個 query_disc 好慢)
N_DISC = 300
disc_means = np.zeros(N_DISC)
disc_vecs = np.zeros((N_DISC, 3))
for i in range(N_DISC):
    rv = rng.standard_normal(3)
    rv /= np.linalg.norm(rv)
    disc_vecs[i] = rv
    d = hp.query_disc(nside_low, rv, np.radians(20.0))
    disc_means[i] = m_low[d].mean() * 1e6

# node9 區域
vec9 = hp.ang2vec(node9["l"], node9["b"], lonlat=True)
d9 = hp.query_disc(nside_low, vec9, np.radians(20.0))
t9 = m_low[d9].mean() * 1e6

# node0 區域
vec0 = hp.ang2vec(node0["l"], node0["b"], lonlat=True)
d0 = hp.query_disc(nside_low, vec0, np.radians(20.0))
t0 = m_low[d0].mean() * 1e6

rank9 = (disc_means <= t9).sum()
rank0 = (disc_means <= t0).sum()
print(f"node9 20° 圓盤: {t9:+.2f} μK → rank {rank9}/{N_DISC} ({(1-rank9/N_DISC)*100:.1f}% 最冷)")
print(f"node0 20° 圓盤: {t0:+.2f} μK → rank {rank0}/{N_DISC} ({(1-rank0/N_DISC)*100:.1f}% 最冷)")
print(f"隨機 20° 圓盤 mean: {disc_means.mean():+.2f} ± {disc_means.std():.2f} μK")
print(f"node9 z = {(t9-disc_means.mean())/disc_means.std():+.2f}σ")
print(f"node0 z = {(t0-disc_means.mean())/disc_means.std():+.2f}σ")

# ============ T3: 熱環檢驗 ============
print("\n" + "=" * 70)
print("T3: 熱環檢驗 — 冷區外圍有冇熱環 (supervoid ISW signature)")
print("=" * 70)
# 冷斑 ISW 特徵: 中心冷 + 外圍熱環 (~2× 半徑)
# 檢查 20°-30° 環帶 vs 全圖 (用 nside_low)
for name, pos in [("node9", node9), ("node0", node0)]:
    vec = hp.ang2vec(pos["l"], pos["b"], lonlat=True)
    disc20 = hp.query_disc(nside_low, vec, np.radians(20.0))
    ring20_30 = np.setdiff1d(
        hp.query_disc(nside_low, vec, np.radians(30.0)),
        hp.query_disc(nside_low, vec, np.radians(20.0)))
    t_disc = m_low[disc20].mean() * 1e6
    t_ring = m_low[ring20_30].mean() * 1e6
    t_all = m_low.mean() * 1e6
    print(f"{name}: 20°盤={t_disc:+.2f}  20-30°環={t_ring:+.2f}  全圖={t_all:+.2f}  環-盤={t_ring-t_disc:+.2f}")

# 隨機對照: 200 個隨機方向嘅 環-盤 差
rng2 = np.random.default_rng(99)
ring_diffs = []
for _ in range(200):
    rv = rng2.standard_normal(3)
    rv /= np.linalg.norm(rv)
    d20 = hp.query_disc(nside_low, rv, np.radians(20.0))
    r20_30 = np.setdiff1d(
        hp.query_disc(nside_low, rv, np.radians(30.0)),
        hp.query_disc(nside_low, rv, np.radians(20.0)))
    ring_diffs.append((m_low[r20_30].mean() - m_low[d20].mean()) * 1e6)
ring_diffs = np.array(ring_diffs)
print(f"\n隨機 200 方向 (環-盤): {ring_diffs.mean():+.2f} ± {ring_diffs.std():.2f} μK")

# node9/node0 嘅環-盤 z
for name, pos in [("node9", node9), ("node0", node0)]:
    vec = hp.ang2vec(pos["l"], pos["b"], lonlat=True)
    d20 = hp.query_disc(nside_low, vec, np.radians(20.0))
    r20_30 = np.setdiff1d(
        hp.query_disc(nside_low, vec, np.radians(30.0)),
        hp.query_disc(nside_low, vec, np.radians(20.0)))
    diff = (m_low[r20_30].mean() - m_low[d20].mean()) * 1e6
    z = (diff - ring_diffs.mean()) / ring_diffs.std()
    print(f"{name} 環-盤 = {diff:+.2f} μK → z = {z:+.2f}σ (vs 隨機)")

# ============ T4: 冷斑對照 ============
print("\n" + "=" * 70)
print("T4: 冷斑區對照 — 兩個結構嘅獨立性")
print("=" * 70)
# 兩個 20° 圓盤重疊?
overlap = len(np.intersect1d(d9, d0))
print(f"node9 20°盤 ∩ node0 20°盤: {overlap} 像素 (總 {len(d9)})")
sep = angdist(node9["l"], node9["b"], node0["l"], node0["b"])
print(f"中心距離: {sep:.2f}° (20+20=40° > 26.17°, 有重疊)")
print(f"重疊比例: {overlap/len(d9)*100:.1f}%")

# 儲存
out = {
    "node9": {"l": node9["l"], "b": node9["b"]},
    "T1_radial": {"node9": [[r, float(t), float(s)] for r, t, s, n in prof9],
                   "node0": [[r, float(t), float(s)] for r, t, s, n in prof0]},
    "T2_rank": {"node9_20deg": float(t9), "node9_rank": int(rank9), "node9_z": float((t9-disc_means.mean())/disc_means.std()),
                 "node0_20deg": float(t0), "node0_rank": int(rank0), "node0_z": float((t0-disc_means.mean())/disc_means.std()),
                 "random_mean": float(disc_means.mean()), "random_std": float(disc_means.std())},
    "T3_ring": {"node9_ring_diff": None, "node0_ring_diff": None, "random": {"mean": float(ring_diffs.mean()), "std": float(ring_diffs.std())}},
    "T4_sep": {"separation": float(sep), "overlap_pix": int(overlap), "overlap_pct": float(overlap/len(d9)*100)},
}
with open(os.path.join(DATA, "discriminant_tests.json"), "w") as f:
    json.dump(out, f, indent=2)
print("\n✅ saved data/discriminant_tests.json")
