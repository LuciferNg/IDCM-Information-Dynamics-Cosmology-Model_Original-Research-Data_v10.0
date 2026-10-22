#!/usr/bin/env python3
"""
11_verify_discriminant.py — O25: 判別檢驗獨立驗證
=================================================
獨立重算 T2/T3 核心數字 (nside=512, 唔同 seed), 對比 05_discriminant_tests.md。
"""
import healpy as hp
import numpy as np
import os, json, sys

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
CACHE = os.path.join(BASE, "o25_scale_spectrum", "data", "smooth_cache_large")
DATA = os.path.join(BASE, "o25_scale_spectrum", "data")

node9 = {"l": 214.92, "b": -31.16}
node0 = {"l": 209.00, "b": -57.00}

m = hp.read_map(os.path.join(CACHE, "Commander_smooth15.0.fits"), field=0)
m_low = hp.ud_grade(m, 512)
nside_low = 512

passes, fails = 0, 0
fail_msgs = []

def check(name, claimed, recomputed, tol):
    global passes, fails
    if abs(claimed - recomputed) <= tol:
        passes += 1
    else:
        fails += 1
        fail_msgs.append(f"{name}: claimed={claimed} recomputed={recomputed:.4f} tol={tol}")

# ============ T2 重算 (唔同 seed 123) ============
print("T2 重算 (seed=123, 300 圓盤)")
rng = np.random.default_rng(123)
N = 300
means = np.zeros(N)
for i in range(N):
    rv = rng.standard_normal(3)
    rv /= np.linalg.norm(rv)
    d = hp.query_disc(nside_low, rv, np.radians(20.0))
    means[i] = m_low[d].mean() * 1e6

vec9 = hp.ang2vec(node9["l"], node9["b"], lonlat=True)
d9 = hp.query_disc(nside_low, vec9, np.radians(20.0))
t9 = m_low[d9].mean() * 1e6
vec0 = hp.ang2vec(node0["l"], node0["b"], lonlat=True)
d0 = hp.query_disc(nside_low, vec0, np.radians(20.0))
t0 = m_low[d0].mean() * 1e6

z9 = (t9 - means.mean()) / means.std()
z0 = (t0 - means.mean()) / means.std()
print(f"  node9: T={t9:+.2f} z={z9:+.2f}σ")
print(f"  node0: T={t0:+.2f} z={z0:+.2f}σ")

# 對比 05 文檔: node9 T=-39.30 z=-2.00, node0 T=+7.99 z=+0.45
check("node9 T", -39.30, t9, 1.0)
check("node9 z", -2.00, z9, 0.3)
check("node0 T", 7.99, t0, 1.0)
check("node0 z", 0.45, z0, 0.3)

# ============ T3 重算 (唔同 seed 456) ============
print("T3 重算 (seed=456, 200 方向)")
rng2 = np.random.default_rng(456)
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
print(f"  隨機環-盤: {ring_diffs.mean():+.2f} ± {ring_diffs.std():.2f}")

for name, pos, claimed in [("node9", node9, 2.43), ("node0", node0, 0.09)]:
    vec = hp.ang2vec(pos["l"], pos["b"], lonlat=True)
    d20 = hp.query_disc(nside_low, vec, np.radians(20.0))
    r20_30 = np.setdiff1d(
        hp.query_disc(nside_low, vec, np.radians(30.0)),
        hp.query_disc(nside_low, vec, np.radians(20.0)))
    diff = (m_low[r20_30].mean() - m_low[d20].mean()) * 1e6
    z = (diff - ring_diffs.mean()) / ring_diffs.std()
    print(f"  {name}: 環-盤={diff:+.2f} z={z:+.2f}σ")
    check(f"{name} ring z", claimed, z, 0.4)

# ============ T1 中心值重算 ============
print("T1 中心 (0-2°) 重算")
for name, pos, claimed in [("node9", node9, -73.44), ("node0", node0, -31.61)]:
    vec = hp.ang2vec(pos["l"], pos["b"], lonlat=True)
    d = hp.query_disc(nside_low, vec, np.radians(2.0))
    t = m_low[d].mean() * 1e6
    print(f"  {name}: 中心 T={t:+.2f}")
    check(f"{name} center", claimed, t, 1.0)

# ============ T4 距離重算 ============
def angdist(l1, b1, l2, b2):
    l1, b1, l2, b2 = map(np.radians, [l1, b1, l2, b2])
    return np.degrees(np.arccos(np.clip(np.sin(b1)*np.sin(b2) + np.cos(b1)*np.cos(b2)*np.cos(l1-l2), -1, 1)))
sep = angdist(node9["l"], node9["b"], node0["l"], node0["b"])
check("separation", 26.16, sep, 0.1)
print(f"  separation: {sep:.2f}°")

print(f"\n{'='*60}")
print(f"驗證結果: {passes} PASS, {fails} FAIL")
if fails:
    for msg in fail_msgs:
        print(f"  ❌ {msg}")
    sys.exit(1)
else:
    print("🎉 判別檢驗全部驗證通過 — 無幻覺")
