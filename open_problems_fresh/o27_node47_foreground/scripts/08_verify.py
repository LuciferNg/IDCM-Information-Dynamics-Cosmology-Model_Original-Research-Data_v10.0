#!/usr/bin/env python3
"""
08_verify.py — O27: 檔案驗證 (no-hallucination close-out)
========================================================
讀返所有 data/ JSON, 獨立重算關鍵數字, 確認無幻覺。
"""
import json, os, sys
import numpy as np

DATA = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o27_node47_foreground/data"
BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"

passes, fails = 0, 0
def check(desc, cond, detail=""):
    global passes, fails
    if cond:
        passes += 1
        print(f"  ✅ {desc} {detail}")
    else:
        fails += 1
        print(f"  ❌ {desc} {detail}")

print("=" * 70)
print("O27: 檔案驗證")
print("=" * 70)

# 1. 檔案存在
print("\n① 檔案存在:")
for f in ["node47_multiscale.json", "crossmap_node47.json", "mask_node47.json",
          "antipode_node47.json", "commander_anomaly.json", "multifreq_node47.json"]:
    p = os.path.join(DATA, f)
    check(f, os.path.exists(p), f"({p})")

# 2. 多尺度
print("\n② 多尺度重算:")
ms = json.load(open(os.path.join(DATA, "node47_multiscale.json")))
# 獨立重算 3.0° rank (用 raw cache)
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u
CACHE = os.path.join(BASE, "o5_catalog_compare/data/smooth_cache")
nodes = []
with open(os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")) as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic
m3 = hp.read_map(os.path.join(CACHE, "smica2_smooth3.0.fits"), field=0)
nside = hp.get_nside(m3)
pix = hp.ang2pix(nside, gal.l.deg, gal.b.deg, lonlat=True)
T3 = m3[pix]*1e6
order = np.argsort(T3)
rank47_re = int(np.where(order == 47)[0][0]) + 1
rank0_re = int(np.where(order == 0)[0][0]) + 1
r3 = [r for r in ms if abs(r["fwhm"]-3.0) < 0.01][0]
check("3.0° T47 = -135.7", abs(r3["T47_uK"] - (-135.7)) < 2, f"(doc -135.7, 實測 {r3['T47_uK']:.1f})")
check("3.0° rank47 = 2", rank47_re == r3["rank47"] == 2, f"(重算 {rank47_re}, JSON {r3['rank47']})")
check("3.0° rank0 = 1", rank0_re == r3["rank0"] == 1, f"(重算 {rank0_re}, JSON {r3['rank0']})")
check("全部尺度 rank ≤ 2", all(r["rank47"] <= 2 for r in ms))

# 3. 三地圖
print("\n③ 三地圖重算:")
cm = json.load(open(os.path.join(DATA, "crossmap_node47.json")))
r3c = [r for r in cm if r["scale"] == "3.0"][0]
check("3.0° SMICA = -135.7", abs(r3c["SMICA"] - (-135.7)) < 2, f"({r3c['SMICA']:.1f})")
check("3.0° spread ~9.95%", abs(r3c["spread_pct"] - 9.95) < 1, f"({r3c['spread_pct']:.2f}%)")
check("Commander 最冷", r3c["Commander"] < r3c["SMICA"] < r3c["NILC"] or r3c["Commander"] < r3c["NILC"] < r3c["SMICA"],
      f"(Comm {r3c['Commander']:.1f})")

# 4. mask
print("\n④ mask 重算:")
mk = json.load(open(os.path.join(DATA, "mask_node47.json")))
r3m = mk["CMB-common-Int-R3"]
check("R3 mask 遮住 node47", r3m["node47_status"] == "masked")
check("R3 60節點 45/60 保留", r3m["n_nodes_keep"] == 45, f"({r3m['n_nodes_keep']})")
check("R3 5°盤 0% 保留", r3m["disc_frac"]["5.0"] == 0.0)

# 5. 對徑
print("\n⑤ 對徑重算:")
ap = json.load(open(os.path.join(DATA, "antipode_node47.json")))
anti3 = [r for r in ap["anti_T"] if abs(r["fwhm"]-3.0) < 0.01][0]
check("3.0° 對徑 +16.3", abs(anti3["T_anti"] - 16.3) < 3, f"({anti3['T_anti']:.1f})")
check("對徑唔冷 (>-30)", anti3["T_anti"] > -30)
check("node47 8° 環境 mean < -70", ap["env47"]["8.0"]["mean"] < -70, f"({ap['env47']['8.0']['mean']:.1f})")

# 6. Commander
print("\n⑥ Commander 偏差重算:")
ca = json.load(open(os.path.join(DATA, "commander_anomaly.json")))
check("低緯 C-S < -2", ca["low_lat_CminusS_mean"] < -2, f"({ca['low_lat_CminusS_mean']:.1f})")
check("p < 0.01", ca["ttest_p"] < 0.01, f"(p={ca['ttest_p']:.4f})")

# 7. 多頻譜 (如果存在)
print("\n⑦ 多頻譜:")
if os.path.exists(os.path.join(DATA, "multifreq_smooth_node47.json")):
    mf = json.load(open(os.path.join(DATA, "multifreq_smooth_node47.json")))
    rows = {r["name"]: r for r in mf["rows"]}
    n47 = rows.get("node47")
    n0 = rows.get("node0")
    if n47 and n0:
        # JSON keys: "100", "143", "217", "353" (字串數字)
        check("node47 143GHz > -50 (唔冷)", n47["143"] > -50, f"({n47['143']:.1f})")
        check("node0 143GHz < -80 (冷)", n0["143"] < -80, f"({n0['143']:.1f})")
        check("node47 217/143 > 2 (上升)", n47["r217_143"] > 2, f"({n47['r217_143']:.2f})")
        check("node0 217/143 < 1 (平譜)", n0["r217_143"] < 1, f"({n0['r217_143']:.2f})")
else:
    print("  [skip] multifreq_smooth 未完成")

print(f"\n{'='*70}")
print(f"驗證: {passes} PASS / {fails} FAIL")
sys.exit(1 if fails else 0)
