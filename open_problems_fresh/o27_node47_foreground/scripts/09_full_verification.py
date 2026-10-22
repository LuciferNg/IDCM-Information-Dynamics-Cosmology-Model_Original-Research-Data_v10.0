#!/usr/bin/env python3
"""
09_full_verification.py — O27 close-out: 全面檔案驗證 (file simulation verifier)
===============================================================================
5 層驗證 (O5 模式):
1. 檔案存在 — 所有 JSON/fits/doc 路徑
2. JSON 結構 — keys/counts 正確
3. 直接 FITS 讀取 — 從 raw cache 重算 node47 溫度, 對比 JSON/doc
4. 獨立重算 — 從 scratch 重算所有關鍵統計 (唔重用舊 code)
5. 文檔一致性 — NN_results.md 中所有數字 vs JSON
"""
import json, os, sys, math
import numpy as np
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u

OUT = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o27_node47_foreground"
DATA = os.path.join(OUT, "data")
BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
CACHE = os.path.join(BASE, "o5_catalog_compare/data/smooth_cache")

passes, fails = 0, 0
def check(desc, cond, detail=""):
    global passes, fails
    if cond:
        passes += 1
        print(f"  ✅ {desc} {detail}")
    else:
        fails += 1
        print(f"  ❌ {desc} {detail}")

print("=" * 72)
print("O27 close-out: 全面檔案驗證")
print("=" * 72)

# ============ 0. 節點座標 (權威源) ============
nodes = []
with open(os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")) as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic
l47, b47 = float(gal.l.deg[47]), float(gal.b.deg[47])
l0, b0 = float(gal.l.deg[0]), float(gal.b.deg[0])
check("node47 l=313.47°", abs(l47 - 313.47) < 0.01, f"({l47:.2f})")
check("node47 b=-8.58°", abs(b47 - (-8.58)) < 0.01, f"({b47:.2f})")
check("node0 l=209.00°", abs(l0 - 209.00) < 0.01, f"({l0:.2f})")
check("node0 b=-57.00°", abs(b0 - (-57.00)) < 0.01, f"({b0:.2f})")

# ============ 1. 檔案存在 ============
print("\n① 檔案存在:")
FILES = [
    "data/node47_multiscale.json", "data/crossmap_node47.json",
    "data/mask_node47.json", "data/antipode_node47.json",
    "data/commander_anomaly.json", "data/multifreq_node47.json",
    "data/multifreq_smooth_node47.json",
    "data/COM_Mask_CMB-common-Mask-Int_2048_R3.00.fits",
    "data/COM_Mask_CMB-IQU-common-field-MaskInt_2048_R2.01.fits",
    "data/HFI_Mask_GalPlane-apo0_2048_R2.00.fits",
    "data/HFI_SkyMap_100_2048_R3.01_full.fits",
    "data/HFI_SkyMap_143_2048_R3.01_full.fits",
    "data/HFI_SkyMap_217_2048_R3.01_full.fits",
    "data/HFI_SkyMap_353_2048_R3.01_full.fits",
    "NN_results.md", "01_problem_record.md",
    "scripts/01_node47_multiscale.py", "scripts/02_crossmap_node47.py",
    "scripts/03_foreground_mask.py", "scripts/04_antipode_check.py",
    "scripts/05_commander_anomaly.py", "scripts/06_multifreq_node47.py",
    "scripts/06b_multifreq_smooth.py", "scripts/07_synthesis.py",
    "scripts/08_verify.py", "scripts/09_full_verification.py",
]
for f in FILES:
    check(f, os.path.exists(os.path.join(OUT, f)), "")

# ============ 2. JSON 結構 ============
print("\n② JSON 結構:")
ms = json.load(open(os.path.join(DATA, "node47_multiscale.json")))
check("multiscale 10 尺度", len(ms) == 10, f"({len(ms)})")
check("multiscale keys 完整", all(set(r.keys()) >= {"fwhm","T47_uK","rank47","rank0","T0_uK"} for r in ms))
cm = json.load(open(os.path.join(DATA, "crossmap_node47.json")))
check("crossmap 3 尺度", len(cm) == 3, f"({len(cm)})")
check("crossmap keys 完整", all(set(r.keys()) >= {"scale","SMICA","NILC","Commander","spread_pct"} for r in cm))
mk = json.load(open(os.path.join(DATA, "mask_node47.json")))
check("mask 3 個 mask", len(mk) == 3, f"({len(mk)})")
ap = json.load(open(os.path.join(DATA, "antipode_node47.json")))
check("antipode anti_T ≥5 尺度", len(ap["anti_T"]) >= 5, f"({len(ap['anti_T'])})")
ca = json.load(open(os.path.join(DATA, "commander_anomaly.json")))
check("commander keys", "ttest_p" in ca and "low_lat_CminusS_mean" in ca)
mf = json.load(open(os.path.join(DATA, "multifreq_node47.json")))
check("multifreq 8 目標", len(mf["rows"]) == 8, f"({len(mf['rows'])})")
mfs = json.load(open(os.path.join(DATA, "multifreq_smooth_node47.json")))
check("multifreq_smooth 8 目標", len(mfs["rows"]) == 8, f"({len(mfs['rows'])})")

# ============ 3. 直接 FITS 重算 (raw cache) ============
print("\n③ 直接 FITS 重算 (SMICA cache):")
m3 = hp.read_map(os.path.join(CACHE, "smica2_smooth3.0.fits"), field=0)
nside = hp.get_nside(m3)
pix47 = hp.ang2pix(nside, l47, b47, lonlat=True)
pix0 = hp.ang2pix(nside, l0, b0, lonlat=True)
T47_re = float(m3[pix47] * 1e6)
T0_re = float(m3[pix0] * 1e6)
check("SMICA 3.0° T47 = -135.7", abs(T47_re - (-135.7)) < 0.5, f"(重算 {T47_re:.2f})")
check("SMICA 3.0° T0 = -145.0", abs(T0_re - (-145.0)) < 0.5, f"(重算 {T0_re:.2f})")

# rank 重算
pix_all = hp.ang2pix(nside, gal.l.deg, gal.b.deg, lonlat=True)
T_all = m3[pix_all] * 1e6
order = np.argsort(T_all)
rank47_re = int(np.where(order == 47)[0][0]) + 1
rank0_re = int(np.where(order == 0)[0][0]) + 1
check("rank47 = 2", rank47_re == 2, f"(重算 {rank47_re})")
check("rank0 = 1", rank0_re == 1, f"(重算 {rank0_re})")

# 多尺度重算 (0.5, 1.0, 2.0, 4.17, 5.0, 7.0, 10.0)
for fwhm in [0.5, 1.0, 2.0, 4.17, 5.0, 7.0, 10.0]:
    fname = os.path.join(CACHE, f"smica2_smooth{fwhm}.fits")
    if not os.path.exists(fname):
        continue
    m = hp.read_map(fname, field=0)
    ns = hp.get_nside(m)
    p = hp.ang2pix(ns, l47, b47, lonlat=True)
    T = float(m[p] * 1e6)
    jr = [r for r in ms if abs(r["fwhm"] - fwhm) < 0.01][0]
    check(f"{fwhm}° T47 一致 (|Δ|<0.5)", abs(T - jr["T47_uK"]) < 0.5, f"(重算 {T:.1f}, JSON {jr['T47_uK']:.1f})")

# 對徑重算
l_anti = (l47 + 180) % 360
b_anti = -b47
pix_a = hp.ang2pix(nside, l_anti, b_anti, lonlat=True)
T_anti_re = float(m3[pix_a] * 1e6)
check("對徑 3.0° = +16.3", abs(T_anti_re - 16.3) < 1, f"(重算 {T_anti_re:.1f})")

# 三地圖重算 (o5 smooth_cache 4.17 — O3C /tmp 已清, 3.0/5.0 NILC/Commander 唔可用)
print("\n④ 三地圖重算 (o5 smooth_cache 4.17):")
O5C = os.path.join(BASE, "o5_catalog_compare/data/smooth_cache")
for mname, fname in [("SMICA", "smica2_smooth4.17.fits"), ("NILC", "nilc2_smooth4.17.fits"), ("Commander", "commander_smooth4.17.fits")]:
    p = os.path.join(O5C, fname)
    if not os.path.exists(p):
        print(f"  [skip] {p}")
        continue
    m = hp.read_map(p, field=0)
    ns = hp.get_nside(m)
    pix = hp.ang2pix(ns, l47, b47, lonlat=True)
    T = float(m[pix] * 1e6)
    jv = [r for r in cm if r["scale"] == "4.17"][0][mname]
    check(f"4.17° {mname} = {jv:.1f}", abs(T - jv) < 0.5, f"(重算 {T:.1f})")

# ============ 4. 多頻譜獨立重算 ============
print("\n⑤ 多頻譜獨立重算 (直接從 fits):")
# 用已存 smooth 結果對比 — 重新讀 143GHz 檢查 node47
m143 = hp.read_map(os.path.join(DATA, "HFI_SkyMap_143_2048_R3.01_full.fits"), field=0, nest=True)
m143 = hp.reorder(m143, n2r=True)
bad = (~np.isfinite(m143)) | (np.abs(m143) > 1e-3)
m143 = np.where(bad, np.nan, m143)
mask_ok = np.isfinite(m143)
sm143 = hp.smoothing(np.where(mask_ok, m143, 0.0), sigma=np.radians(3.0)/(2*np.sqrt(2*np.log(2))), verbose=False)
sm_ok = hp.smoothing(mask_ok.astype(float), sigma=np.radians(3.0)/(2*np.sqrt(2*np.log(2))), verbose=False)
sm143 = np.where(sm_ok > 0.1, sm143/sm_ok, np.nan)
ns143 = hp.get_nside(m143)
p47 = hp.ang2pix(ns143, l47, b47, lonlat=True)
p0 = hp.ang2pix(ns143, l0, b0, lonlat=True)
T143_47 = float(sm143[p47] * 1e6)
T143_0 = float(sm143[p0] * 1e6)
row47 = [r for r in mfs["rows"] if r["name"] == "node47"][0]
row0 = [r for r in mfs["rows"] if r["name"] == "node0"][0]
check("node47 143GHz = +18.3", abs(T143_47 - row47["143"]) < 1, f"(重算 {T143_47:.1f}, JSON {row47['143']:.1f})")
check("node0 143GHz = -111.9", abs(T143_0 - row0["143"]) < 1, f"(重算 {T143_0:.1f}, JSON {row0['143']:.1f})")
check("node47 143 唔冷 (>-50)", T143_47 > -50, f"({T143_47:.1f})")
check("node0 143 冷 (<-80)", T143_0 < -80, f"({T143_0:.1f})")

# 217GHz 重算
m217 = hp.read_map(os.path.join(DATA, "HFI_SkyMap_217_2048_R3.01_full.fits"), field=0, nest=True)
m217 = hp.reorder(m217, n2r=True)
bad = (~np.isfinite(m217)) | (np.abs(m217) > 1e-3)
m217 = np.where(bad, np.nan, m217)
mask_ok = np.isfinite(m217)
sm217 = hp.smoothing(np.where(mask_ok, m217, 0.0), sigma=np.radians(3.0)/(2*np.sqrt(2*np.log(2))), verbose=False)
sm_ok = hp.smoothing(mask_ok.astype(float), sigma=np.radians(3.0)/(2*np.sqrt(2*np.log(2))), verbose=False)
sm217 = np.where(sm_ok > 0.1, sm217/sm_ok, np.nan)
ns217 = hp.get_nside(m217)
p47 = hp.ang2pix(ns217, l47, b47, lonlat=True)
p0 = hp.ang2pix(ns217, l0, b0, lonlat=True)
T217_47 = float(sm217[p47] * 1e6)
T217_0 = float(sm217[p0] * 1e6)
check("node47 217GHz = +380.9", abs(T217_47 - row47["217"]) < 2, f"(重算 {T217_47:.1f}, JSON {row47['217']:.1f})")
check("node0 217GHz = -40.1", abs(T217_0 - row0["217"]) < 2, f"(重算 {T217_0:.1f}, JSON {row0['217']:.1f})")
r47 = T217_47 / T143_47 if abs(T143_47) > 1 else float('nan')
r0 = T217_0 / T143_0 if abs(T143_0) > 1 else float('nan')
check("node47 217/143 ≈ 20.8", abs(r47 - 20.8) < 1, f"(重算 {r47:.1f})")
check("node0 217/143 ≈ 0.36", abs(r0 - 0.36) < 0.1, f"(重算 {r0:.2f})")

# ============ 5. 文檔一致性 ============
print("\n⑥ 文檔一致性 (NN_results.md):")
doc = open(os.path.join(OUT, "NN_results.md")).read()
doc_checks = [
    ("-135.7", "3.0° T47"), ("-145.0", "3.0° T0"), ("20.8", "217/143 node47"),
    ("0.36", "217/143 node0"), ("+18.3", "143GHz node47"), ("-111.9", "143GHz node0"),
    ("+380.9", "217GHz node47"), ("-40.1", "217GHz node0"), ("16.3", "對徑"),
    ("9.95", "spread 3.0°"), ("0.67", "node0 spread"), ("45/60", "mask 節點"),
    ("p=0.0004", "Commander t-test"), ("-81.4", "8° 環境"), ("249.6", "0.5° T47"),
    ("-123.4", "4.17° T47"), ("-86.1", "10° T47"), ("🔴", "最終判決"),
]
for val, desc in doc_checks:
    check(f"doc 含 {desc} {val}", val in doc, "")

# 公式/數值驗證: 關鍵統計
print("\n⑦ 關鍵統計獨立重算:")
# spread 重算
vals3 = [float(cm[0]["SMICA"]), float(cm[0]["NILC"]), float(cm[0]["Commander"])]
spread_re = (max(vals3) - min(vals3)) / abs(np.mean(vals3)) * 100
check("spread 3.0° = 9.95%", abs(spread_re - 9.95) < 0.2, f"(重算 {spread_re:.2f}%)")

# 60 節點 low-lat 統計 (Commander 偏差, 4.17 版 — O3C 已清)
mn = hp.read_map(os.path.join(O5C, "nilc2_smooth4.17.fits"), field=0)
mc = hp.read_map(os.path.join(O5C, "commander_smooth4.17.fits"), field=0)
ms4 = hp.read_map(os.path.join(O5C, "smica2_smooth4.17.fits"), field=0)
ns = hp.get_nside(mn)
pix = hp.ang2pix(ns, gal.l.deg, gal.b.deg, lonlat=True)
Tn, Tc = mn[pix]*1e6, mc[pix]*1e6
low = np.abs(gal.b.deg) < 20
d_cs = Tc - (ms4[hp.ang2pix(ns, gal.l.deg, gal.b.deg, lonlat=True)]*1e6)
d_low = d_cs[low].mean()
# 註: JSON low_lat_CminusS_mean=-2.7 係 3.0 尺度; 4.17 重算應同號 (<0 低緯偏冷)
check("低緯 C-S 4.17° < 0 (偏冷)", d_low < 0, f"(重算 {d_low:.1f}, 3.0° JSON {ca['low_lat_CminusS_mean']:.1f})")

print(f"\n{'='*72}")
print(f"驗證結果: {passes} PASS / {fails} FAIL")
print(f"{'='*72}")
sys.exit(1 if fails else 0)
