#!/usr/bin/env python3
"""
14_full_session_verify.py — O30: 本 session 全面驗證器
=========================================================
獨立重算本 session 所有關鍵數字 + 文檔完整性核對:

PART A: O30 主測試 (01-07)
  A1. 60 節點 mean = −1.25, z = −0.21σ (4.17°)
  A2. 高緯 31 mean = −4.06, z = −0.47σ
  A3. mean|T| = 32.75 (幅度檢驗)
  A4. 堆疊中心 bin z = −0.16
  A5. 冷/熱 29:31, 冷熱 mean|T| 比 1.154
  A6. ΔE=0 12節點 mean|T| = 19.05 (O3 交叉)

PART B: 離散性 (08)
  B1. 跨尺度穩定異常 5 節點 [0,9,33,47,53]
  B2. node53 zbar = +2.14, max zbar = 2.78 (node47)

PART C: node53 多頻譜 (09-13)
  C1. 三地圖 3°盤: SMICA +96.8, NILC +96.2, Commander +95.1 (spread 1.8%)
  C2. 環背景 ΔT: SMICA +82.0, NILC +82.1, Commander +82.4 (spread 0.5%)
  C3. 多頻譜當地超出: 100 +82.7, 143 +80.9, 217 +51.0
  C4. R3 mask unmasked
  C5. 對徑 −46.05
  C6. 跨尺度 10/10 全正

PART D: 文檔完整性
  D1. 所有宣稱數值喺記錄文檔出現
  D2. 所有 data 檔被文檔引用
  D3. 文檔之間一致 (NN_results ↔ DISCRETENESS ↔ NODE53 ↔ 01_record)
"""
import healpy as hp
import numpy as np
import os, json, re
from astropy.coordinates import SkyCoord
import astropy.units as u
from scipy import stats

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
O30 = os.path.join(BASE, "o30_node_systematics")
CACHE = os.path.join(BASE, "o5_catalog_compare/data/smooth_cache")
DATA27 = os.path.join(BASE, "o27_node47_foreground/data")
NODES = os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")
COLOR = os.path.join(BASE, "cmb_cold_spot/data/anchored_coloring.txt")

RNG = np.random.default_rng(20260817)
N_CTRL = 1000
passes, fails = [], []

def check(name, cond, detail=""):
    (passes if cond else fails).append(name)
    print(f"  {'✅' if cond else '❌'} {name} {detail}")

print("=" * 70)
print("O30-14: 本 session 全面驗證器")
print("=" * 70)

# ============ 基礎載入 ============
m = hp.read_map(os.path.join(CACHE, "smica2_smooth4.17.fits"), field=0)
nside = hp.get_nside(m)
npix = hp.nside2npix(nside)
nodes = np.loadtxt(NODES)
sc = SkyCoord(ra=nodes[:,0]*u.deg, dec=nodes[:,1]*u.deg, frame='icrs')
gal = sc.galactic
l_deg, b_deg = gal.l.deg, gal.b.deg
pix = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)
T = m[pix] * 1e6
hi_mask = np.abs(b_deg) >= 30

print("\n--- PART A: O30 主測試 ---")

# A1: 60 節點 mean + z
mu = T.mean()
ctrl = np.empty(N_CTRL)
for k in range(N_CTRL):
    ctrl[k] = m[RNG.integers(0, npix, size=60)].mean() * 1e6
z_all = (mu - ctrl.mean()) / ctrl.std(ddof=1)
check("A1 60節點 mean=-1.25", abs(mu + 1.25) < 0.05, f"({mu:+.3f})")
check("A1 z≈-0.21", abs(z_all + 0.207) < 0.1, f"({z_all:+.3f})")

# A2: 高緯 31
Th = T[hi_mask]
ctrl_hi = np.empty(N_CTRL)
for k in range(N_CTRL):
    ctrl_hi[k] = m[RNG.integers(0, npix, size=31)].mean() * 1e6
z_hi = (Th.mean() - ctrl_hi.mean()) / ctrl_hi.std(ddof=1)
check("A2 高緯 mean=-4.06", abs(Th.mean() + 4.06) < 0.1, f"({Th.mean():+.3f})")
check("A2 z≈-0.47", abs(z_hi + 0.468) < 0.15, f"({z_hi:+.3f})")

# A3: mean|T|
A = np.abs(T)
ctrl_abs = np.empty(N_CTRL)
for k in range(N_CTRL):
    ctrl_abs[k] = np.abs(m[RNG.integers(0, npix, size=60)]).mean() * 1e6
z_abs = (A.mean() - ctrl_abs.mean()) / ctrl_abs.std(ddof=1)
check("A3 mean|T|=32.75", abs(A.mean() - 32.75) < 0.05, f"({A.mean():.3f})")
check("A3 z≈-0.65", abs(z_abs + 0.649) < 0.15, f"({z_abs:+.3f})")

# A4: 堆疊中心 bin (讀 data 檔)
d2 = np.loadtxt(os.path.join(O30, "data/02_stack_radial.txt"))
check("A4 中心bin z=-0.16", abs(d2[0,8] + 0.162) < 0.05, f"({d2[0,8]:+.3f})")

# A5: 冷/熱
n_cold = (T < 0).sum()
A_cold, A_hot = np.abs(T[T<0]), np.abs(T[T>0])
check("A5 冷=29 熱=31", n_cold == 29 and (60-n_cold) == 31, f"({n_cold}/{60-n_cold})")
check("A5 冷/熱 abs 比 1.154", abs(A_cold.mean()/A_hot.mean() - 1.154) < 0.01,
      f"({A_cold.mean()/A_hot.mean():.3f})")

# A6: ΔE=0 12節點
zeroE = [10,12,19,22,23,25,28,32,37,40,45,46]
check("A6 ΔE=0 mean|T|=19.05", abs(np.abs(T[zeroE]).mean() - 19.05) < 0.05,
      f"({np.abs(T[zeroE]).mean():.3f})")

# A7: 冷色 8/10 (O24)
color = {}
with open(COLOR) as f:
    for line in f:
        if line.startswith("#") or not line.strip(): continue
        parts = line.split()
        color[int(parts[0])] = int(parts[3])
color_arr = np.array([color[i] for i in range(60)])
order = np.argsort(T)
c_cold10 = (color_arr[order[:10]] == 1).sum()
check("A7 最冷10 8/10 冷色", c_cold10 == 8, f"({c_cold10}/10)")

print("\n--- PART B: 離散性 ---")
# B1: 跨尺度穩定異常
SCALES = [0.5,1.0,1.5,2.0,3.0,4.0,4.17,5.0,7.0,10.0]
MAPS = {0.5:"smica2_smooth0.5.fits",1.0:"smica2_smooth1.0.fits",1.5:"smica2_smooth1.5.fits",
        2.0:"smica2_smooth2.0.fits",3.0:"smica2_smooth3.0.fits",4.0:"smica2_smooth4.0.fits",
        4.17:"smica2_smooth4.17.fits",5.0:"smica2_smooth5.0.fits",7.0:"smica2_smooth7.0.fits",
        10.0:"smica2_smooth10.0.fits"}
NSD = 512
Z = np.zeros((len(SCALES), 60))
for si, s in enumerate(SCALES):
    ms = hp.read_map(os.path.join(CACHE, MAPS[s]), field=0)
    ms = hp.ud_grade(ms, NSD)
    pxs = hp.ang2pix(NSD, l_deg, b_deg, lonlat=True)
    Z[si] = (ms[pxs]*1e6 - ms.mean()*1e6) / (ms.std()*1e6)
zbar = Z.mean(axis=0)
stable = np.where(np.abs(zbar) > 2)[0]
check("B1 穩定異常=5", len(stable) == 5, f"({len(stable)}: {list(stable)})")
check("B1 idx=[0,9,33,47,53]", set(stable) == {0,9,33,47,53}, f"({sorted(stable)})")
check("B2 node53 zbar>2", abs(zbar[53]) > 2, f"({zbar[53]:+.3f})")
check("B2 max=node47 2.78", abs(abs(zbar[47]) - 2.779) < 0.1, f"({zbar[47]:+.3f})")

print("\n--- PART C: node53 ---")
# C1: 三地圖 3°盤
L53, B53 = 319.50, -34.20
vals3 = {}
for name, fname in [("SMICA","smica2_smooth4.17.fits"), ("NILC","nilc2_smooth4.17.fits"),
                     ("Commander","commander_smooth4.17.fits")]:
    mm = hp.read_map(os.path.join(CACHE, fname), field=0)
    ns = hp.get_nside(mm)
    vec = hp.ang2vec(L53, B53, lonlat=True)
    p3 = hp.query_disc(ns, vec, np.radians(3.0))
    vals3[name] = np.mean(mm[p3]) * 1e6
spread3 = (max(vals3.values()) - min(vals3.values())) / abs(np.mean(list(vals3.values()))) * 100
check("C1 SMICA +96.8", abs(vals3["SMICA"] - 96.83) < 1.0, f"({vals3['SMICA']:+.2f})")
check("C1 NILC +96.2", abs(vals3["NILC"] - 96.21) < 1.0, f"({vals3['NILC']:+.2f})")
check("C1 Commander +95.1", abs(vals3["Commander"] - 95.14) < 1.0, f"({vals3['Commander']:+.2f})")
check("C1 spread=1.8%", abs(spread3 - 1.8) < 0.5, f"({spread3:.1f}%)")

# C2: 環背景 ΔT
dT_ring = {}
for name, fname in [("SMICA","smica2_smooth4.17.fits"), ("NILC","nilc2_smooth4.17.fits"),
                     ("Commander","commander_smooth4.17.fits")]:
    mm = hp.read_map(os.path.join(CACHE, fname), field=0)
    ns = hp.get_nside(mm)
    vec = hp.ang2vec(L53, B53, lonlat=True)
    pc = hp.query_disc(ns, vec, np.radians(2.0))
    pr = hp.query_disc(ns, vec, np.radians(8.0))
    pi = hp.query_disc(ns, vec, np.radians(4.0))
    pr = np.setdiff1d(pr, pi)
    dT_ring[name] = (np.mean(mm[pc]) - np.mean(mm[pr])) * 1e6
check("C2 SMICA ΔT=+82", abs(dT_ring["SMICA"] - 82.0) < 2.0, f"({dT_ring['SMICA']:+.2f})")
check("C2 NILC ΔT=+82.1", abs(dT_ring["NILC"] - 82.14) < 2.0, f"({dT_ring['NILC']:+.2f})")
check("C2 Commander ΔT=+82.4", abs(dT_ring["Commander"] - 82.40) < 2.0, f"({dT_ring['Commander']:+.2f})")

# C3: 多頻譜當地超出 (讀 10 JSON)
with open(os.path.join(O30, "data/10_node53_ring_background.json")) as f:
    j10 = json.load(f)
dT100 = j10["results"]["node53"]["100"]["dT"]
dT143 = j10["results"]["node53"]["143"]["dT"]
dT217 = j10["results"]["node53"]["217"]["dT"]
check("C3 100GHz +82.7", abs(dT100 - 82.7) < 1.0, f"({dT100:+.1f})")
check("C3 143GHz +80.9", abs(dT143 - 80.9) < 1.0, f"({dT143:+.1f})")
check("C3 217GHz +51.0", abs(dT217 - 51.0) < 2.0, f"({dT217:+.1f})")

# C4: R3 mask
mk = hp.read_map(os.path.join(DATA27, "COM_Mask_CMB-common-Mask-Int_2048_R3.00.fits"), field=0)
ns = hp.get_nside(mk)
check("C4 R3 unmasked", mk[hp.ang2pix(ns, L53, B53, lonlat=True)] > 0.5)

# C5: 對徑
vec_a = hp.ang2vec((L53+180)%360, +34.2, lonlat=True)
T_a = np.mean(m[hp.query_disc(nside, vec_a, np.radians(3.0))]) * 1e6
check("C5 對徑 -46.05", abs(T_a + 46.05) < 1.0, f"({T_a:+.2f})")

# C6: 跨尺度 10/10 全正
signs = []
for s in SCALES:
    ms = hp.read_map(os.path.join(CACHE, MAPS[s]), field=0)
    ns = hp.get_nside(ms)
    p = hp.ang2pix(ns, L53, B53, lonlat=True)
    signs.append(np.sign(ms[p]))
check("C6 跨尺度10/10全正", all(sg > 0 for sg in signs), f"({sum(1 for sg in signs if sg>0)}/10)")

print("\n--- PART C2: node33 (2026-08-22) ---")
L33, B33 = 191.4, -16.1
# C2a: 三地圖
vals33 = {}
for name, fname in [("SMICA","smica2_smooth4.17.fits"), ("NILC","nilc2_smooth4.17.fits"),
                     ("Commander","commander_smooth4.17.fits")]:
    mm = hp.read_map(os.path.join(CACHE, fname), field=0)
    ns = hp.get_nside(mm)
    vec = hp.ang2vec(L33, B33, lonlat=True)
    p3 = hp.query_disc(ns, vec, np.radians(3.0))
    vals33[name] = np.mean(mm[p3]) * 1e6
spread33 = (max(vals33.values()) - min(vals33.values())) / abs(np.mean(list(vals33.values()))) * 100
check("C2a node33 SMICA -74.1", abs(vals33["SMICA"] + 74.12) < 1.0, f"({vals33['SMICA']:+.2f})")
check("C2a node33 spread=3.8%", abs(spread33 - 3.8) < 0.5, f"({spread33:.1f}%)")
# C2b: 353 dust (raw, 只 finite)
m353 = hp.read_map(os.path.join(DATA27, "HFI_SkyMap_353_2048_R3.01_full.fits"), field=0, nest=True)
m353 = hp.reorder(m353, n2r=True)
m353 = np.where(np.isfinite(m353), m353, np.nan)
ns353 = hp.get_nside(m353)
v33 = hp.ang2vec(L33, B33, lonlat=True)
p33c = hp.query_disc(ns353, v33, np.radians(2.0))
v0 = hp.ang2vec(209.0, -57.0, lonlat=True)
p0c = hp.query_disc(ns353, v0, np.radians(2.0))
dust33 = np.nanmean(m353[p33c]) * 1e6
dust0 = np.nanmean(m353[p0c]) * 1e6
check("C2b node33 353 dust +4844", abs(dust33 - 4844) < 300, f"({dust33:+.0f})")
check("C2b node33 dust 8.9x node0", abs(dust33/dust0 - 8.9) < 1.2, f"({dust33/dust0:.1f}x)")
# C2c: R3 mask node33
check("C2c node33 R3 unmasked", mk[hp.ang2pix(ns, L33, B33, lonlat=True)] > 0.5)

print("\n--- PART D: 文檔完整性 ---")
docs = {}
for fn in ["NN_results.md", "DISCRETENESS_COMPLETE.md", "NODE53_REPORT.md", "01_problem_record.md", "SESSION_START.md"]:
    with open(os.path.join(O30, fn)) as f:
        docs[fn] = f.read()

# D1: 關鍵數值喺文檔 (容忍 Unicode minus U+2212 同 ASCII hyphen)
def norm_minus(s):
    return s.replace("−", "-").replace("−", "-")  # U+2212 → ASCII

docs_norm = {fn: norm_minus(d) for fn, d in docs.items()}

key_claims = [
    ("-1.25", "60節點 mean"), ("-0.21σ", "z all"), ("32.75", "mean|T|"),
    ("1.154", "冷熱比"), ("29:31", "冷熱 count"), ("19.05", "ΔE=0"),
    ("5 個跨尺度", "離散 5"), ("node53", "node53 出現"), ("+112", "node53 T"),
    ("96.8", "SMICA 3°盤"), ("1.8%", "spread"), ("0.5%", "環 spread"),
    ("+82", "環 ΔT"), ("unmasked", "mask"), ("-46.05", "對徑"),
]
for val, label in key_claims:
    found = any(val in d for d in docs_norm.values())
    check(f"D1 '{val}' ({label})", found)

# D2: data 檔被引用
data_files = ["01_mean_vs_random.txt", "02_stack_radial.txt", "03_multiscale.txt",
              "04_sign_asymmetry.txt", "06_amplitude_test.txt", "08_discreteness.txt",
              "09_node53_multifreq.json", "10_node53_ring_background.json",
              "11_node53_crossmap.json", "12_node53_antipode_mask.json"]
for df in data_files:
    found = any(df in d for d in docs.values())
    check(f"D2 data/{df} 被引用", found)

# D3: 文檔互相引用
check("D3 NN→DISCRETENESS", "DISCRETENESS_COMPLETE" in docs["NN_results.md"])
check("D3 NN→NODE53", "NODE53_REPORT" in docs["NN_results.md"])
check("D3 01→NODE53", "NODE53_REPORT" in docs["01_problem_record.md"])
check("D3 01→NN", "NN_results" in docs["01_problem_record.md"])

print(f"\n{'='*70}")
print(f"結果: {len(passes)}/{len(passes)+len(fails)} PASS")
if fails:
    print(f"❌ FAILED: {fails}")
    exit(1)
print("✅ 全部通過 — 本 session 所有推導、計算、結果、文檔一致可信")
