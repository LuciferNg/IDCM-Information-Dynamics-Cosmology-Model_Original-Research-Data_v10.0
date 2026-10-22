#!/usr/bin/env python3
"""
03_cross_map_verify.py — O21: SMICA × NILC × Commander node 9 cross-map
====================================================================
Download raw NILC/Commander maps → smooth to 4.17° → compare node 9
"""

import numpy as np
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u
import os, sys, math, json, time

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
O21 = os.path.join(BASE, "o21_node9_anomaly")
DATA = os.path.join(O21, "data")
SMOOTH_CACHE = os.path.join(BASE, "o5_catalog_compare/data/smooth_cache")

FWHM = 4.17
sigma = np.radians(FWHM) / (2 * np.sqrt(2 * np.log(2)))

# Nodes
nodes = np.loadtxt(os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt"))
sc = SkyCoord(ra=nodes[:,0]*u.deg, dec=nodes[:,1]*u.deg, frame='icrs')
gal = sc.galactic
l_deg = np.array(gal.l.deg)
b_deg = np.array(gal.b.deg)

# BFS + coloring
from collections import defaultdict, deque
vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])
adj = defaultdict(set)
for i in range(60):
    for j in range(i+1, 60):
        ang = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if ang < 28.0:
            adj[i].add(j); adj[j].add(i)
hop = {0: 0}; q = deque([0])
while q:
    u = q.popleft()
    for w in adj[u]:
        if w not in hop: hop[w] = hop[u] + 1; q.append(w)
hop_arr = np.array([hop[i] for i in range(60)])
color = {}
with open(os.path.join(BASE, "cmb_cold_spot/data/anchored_coloring.txt")) as f:
    for line in f:
        if line.startswith("#") or not line.strip(): continue
        parts = line.split()
        color[int(parts[0])] = int(parts[3])
color_arr = np.array([color[i] for i in range(60)])

print("=" * 66)
print("O21: Cross-map verification — SMICA × NILC × Commander")
print("=" * 66)

# ─── Load / smooth each map ───
maps = {}
map_configs = {
    "SMICA": {
        "path": os.path.join(SMOOTH_CACHE, "smica2_smooth4.17.fits"),
        "nest": False,
        "pre_smoothed": True,
    },
    "NILC": {
        "path": "/tmp/nilc.fits",
        "nest": True,
        "pre_smoothed": False,
    },
    "Commander": {
        "path": "/tmp/commander.fits",
        "nest": True,
        "pre_smoothed": False,
    },
}

for name, cfg in map_configs.items():
    if not os.path.exists(cfg["path"]):
        print(f"  {name}: 🔴 NOT FOUND at {cfg['path']}")
        continue

    if cfg["pre_smoothed"]:
        m = hp.read_map(cfg["path"], field=0)
        m = hp.remove_dipole(m)
        nside = hp.get_nside(m)
        print(f"  {name}: ✅ pre-smoothed @ {FWHM}°, nside={nside}, std={m.std()*1e6:.1f} μK")
    else:
        m_raw = hp.read_map(cfg["path"], field=0, nest=cfg["nest"])
        if cfg["nest"]:
            m_raw = hp.reorder(m_raw, n2r=True)
        nside = hp.get_nside(m_raw)
        print(f"  {name}: ✅ raw loaded, nside={nside}, raw std={m_raw.std()*1e6:.1f} μK")

        # Smooth to 4.17°
        m_s = hp.smoothing(m_raw, sigma=sigma)
        m = hp.remove_dipole(m_s)
        print(f"  {name}: smoothed @ {FWHM}°, std={m.std()*1e6:.1f} μK")

        # Cache smoothed
        cache_path = os.path.join(SMOOTH_CACHE, f"{name.lower()}_smooth{FWHM}.fits".replace("smica", "smica2"))
        # Actually use the right naming
        if name == "NILC":
            cache_path = os.path.join(SMOOTH_CACHE, f"nilc2_smooth{FWHM}.fits")
        elif name == "Commander":
            cache_path = os.path.join(SMOOTH_CACHE, f"commander_smooth{FWHM}.fits")
        hp.write_map(cache_path, m.astype(np.float32), overwrite=True)
        print(f"  {name}: cached to {cache_path}")

    maps[name] = {"map": m, "nside": nside}

if len(maps) < 2:
    print(f"\n🔴 Only {len(maps)} maps available — need at least 2 for cross-map verification")
    sys.exit(1)

# ─── Extract node 9 temperatures ───
print(f"\n─── Node 9 temperature at 4.17° ───")
results = {}
for name, cfg in maps.items():
    m = cfg["map"]
    nside_m = cfg["nside"]
    pix = hp.ang2pix(nside_m, l_deg, b_deg, lonlat=True)
    T = m[pix] * 1e6

    results[name] = {
        "node9_T_uK": float(T[9]),
        "node0_T_uK": float(T[0]),
        "node9_rank": int(np.sum(T < T[9]) + 1),
        "node0_rank": int(np.sum(T < T[0]) + 1),
        "all_mean_uK": float(T.mean()),
        "all_std_uK": float(T.std()),
        "node9_hop": int(hop_arr[9]),
        "node9_color": int(color_arr[9]),
    }
    # Store full 60-node array for correlation
    if name == "SMICA": T_smica = T.copy()
    elif name == "NILC": T_nilc = T.copy()
    elif name == "Commander": T_cmd = T.copy()

    print(f"  {name:>10s}: node9={T[9]:+8.2f} μK (rank {np.sum(T<T[9])+1}/60), "
          f"node0={T[0]:+8.2f} μK (rank {np.sum(T<T[0])+1}/60), "
          f"68-node σ={T.std():.1f} μK")

# ─── Cross-map consistency ───
print(f"\n─── Cross-map consistency ───")
names = list(results.keys())
T9 = np.array([results[n]["node9_T_uK"] for n in names])
T0 = np.array([results[n]["node0_T_uK"] for n in names])

spread9 = T9.max() - T9.min()
spread0 = T0.max() - T0.min()
mean9 = T9.mean()
mean0 = T0.mean()
pct9 = spread9 / abs(mean9) * 100 if abs(mean9) > 0.1 else 0
pct0 = spread0 / abs(mean0) * 100 if abs(mean0) > 0.1 else 0

print(f"  Node 9: mean={mean9:+.1f} μK, spread={spread9:.1f} μK ({pct9:.1f}%)")
print(f"  Node 0: mean={mean0:+.1f} μK, spread={spread0:.1f} μK ({pct0:.1f}%)")

# Consistency criteria (from skill §12):
# <5% = 🟢🟢 confirmed, 5-20% = 🟡 marginal, >20% = 🔴 invalid
for label, pct, spread in [("Node 9", pct9, spread9), ("Node 0", pct0, spread0)]:
    if pct < 5:
        verdict = "🟢🟢 confirmed"
    elif pct < 20:
        verdict = "🟡 marginal"
    else:
        verdict = "🔴 invalid"
    print(f"  {label}: {verdict} (spread={spread:.1f} μK, {pct:.1f}%)")

# ─── 60-node correlation ───
print(f"\n─── 60-node correlation ───")
T_all = {"SMICA": T_smica, "NILC": T_nilc, "Commander": T_cmd}
for i, n1 in enumerate(names):
    for n2 in names[i+1:]:
        r = np.corrcoef(T_all[n1], T_all[n2])[0, 1]
        print(f"  corr({n1}, {n2}) = {r:.4f}")

# ─── Save ───
with open(os.path.join(DATA, "cross_map_verified.json"), "w") as f:
    json.dump({
        "fwhm_deg": FWHM,
        "maps": results,
        "consistency": {
            "node9_mean_uK": float(mean9),
            "node9_spread_uK": float(spread9),
            "node9_spread_pct": float(pct9),
            "node9_verdict": "🟢🟢 confirmed" if pct9 < 5 else ("🟡 marginal" if pct9 < 20 else "🔴 invalid"),
            "node0_mean_uK": float(mean0),
            "node0_spread_uK": float(spread0),
            "node0_spread_pct": float(pct0),
            "node0_verdict": "🟢🟢 confirmed" if pct0 < 5 else ("🟡 marginal" if pct0 < 20 else "🔴 invalid"),
        }
    }, f, indent=2)

print(f"\n✅ Saved: cross_map_verified.json")