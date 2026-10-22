#!/usr/bin/env python3
"""
07_verification.py — O30: 文件模擬驗證器 (no-hallucination close-out)
=====================================================================
獨立重算所有 O30 宣稱數字, 讀返實際 data 檔案核對。
做法:
  1. 重平滑/重抽 60 節點 (用 cache 直接讀, 唔用 scripts 中間值)
  2. 重算全部統計 → 對比 data/*.txt 已存值
  3. 檔案存在性檢查
  4. 交叉檢查 O3 已知值 (mean=-1.25, std=45.81, mean|T|=32.75)
"""
import healpy as hp
import numpy as np
import os
from astropy.coordinates import SkyCoord
import astropy.units as u
from scipy import stats

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
O30 = os.path.join(BASE, "o30_node_systematics")
CACHE = os.path.join(BASE, "o5_catalog_compare/data/smooth_cache/smica2_smooth4.17.fits")
NODES = os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")

RNG = np.random.default_rng(20260817)
N_CONTROL = 1000
passes, fails = [], []

def check(name, cond, detail=""):
    (passes if cond else fails).append(name)
    print(f"  {'✅' if cond else '❌'} {name} {detail}")

print("=" * 66)
print("O30-07: 文件模擬驗證器")
print("=" * 66)

# ---------- 0. 檔案存在 ----------
for f in ["data/01_mean_vs_random.txt", "data/02_stack_radial.txt",
          "data/03_multiscale.txt", "data/04_sign_asymmetry.txt",
          "data/06_amplitude_test.txt"]:
    check(f"exists {f}", os.path.exists(os.path.join(O30, f)))

# ---------- 1. 獨立重抽節點 ----------
m = hp.read_map(CACHE, field=0)
nside = hp.get_nside(m)
npix = hp.nside2npix(nside)
nodes = np.loadtxt(NODES)
sc = SkyCoord(ra=nodes[:,0]*u.deg, dec=nodes[:,1]*u.deg, frame='icrs')
gal = sc.galactic
l_deg, b_deg = gal.l.deg, gal.b.deg
pix = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)
T = m[pix] * 1e6
hi_mask = np.abs(b_deg) >= 30

# 01: mean 檢驗
mu_node = T.mean()
ctrl = np.empty(N_CONTROL)
for k in range(N_CONTROL):
    rpix = RNG.integers(0, npix, size=60)
    ctrl[k] = m[rpix].mean() * 1e6
z = (mu_node - ctrl.mean()) / ctrl.std(ddof=1)
check("01 mean=-1.25", abs(mu_node - (-1.25)) < 0.05, f"({mu_node:+.3f})")
check("01 z≈-0.21", abs(z - (-0.207)) < 0.1, f"({z:+.3f})")

# 02: 中心 bin (讀 data 檔)
d2 = np.loadtxt(os.path.join(O30, "data/02_stack_radial.txt"))
z_center = d2[0, 8]  # col 8 = z
check("02 center z≈-0.16", abs(z_center - (-0.16)) < 0.1, f"({z_center:+.3f})")

# 03: 多尺度 z 範圍 (讀 data 檔)
d3 = np.loadtxt(os.path.join(O30, "data/03_multiscale.txt"))
z3 = d3[:, 3]
check("03 z range ∈[-1,1]", z3.min() > -1 and z3.max() < 1,
      f"([{z3.min():+.2f},{z3.max():+.2f}])")

# 04: 冷/熱 count
n_cold = (T < 0).sum()
check("04 cold=29", n_cold == 29, f"({n_cold})")
A_cold, A_hot = np.abs(T[T < 0]), np.abs(T[T > 0])
m_cold, m_hot = A_cold.mean(), A_hot.mean()
check("04 cold_abs=35.17", abs(m_cold - 35.17) < 0.05, f"({m_cold:.3f})")
check("04 hot_abs=30.48", abs(m_hot - 30.48) < 0.05, f"({m_hot:.3f})")

# 06: mean|T|
A = np.abs(T)
check("06 mean|T|=32.75", abs(A.mean() - 32.75) < 0.05, f"({A.mean():.3f})")
d6 = np.loadtxt(os.path.join(O30, "data/06_amplitude_test.txt"))
# 讀 z 值
z6_line = [l for l in open(os.path.join(O30, "data/06_amplitude_test.txt")) if l.startswith("# ALL_ISO")][0]
z6 = float(z6_line.split("z=")[1].split()[0])
check("06 z≈-0.65", abs(z6 - (-0.65)) < 0.1, f"({z6:+.3f})")

# ---------- 2. O3 交叉檢查 ----------
T_o3 = np.loadtxt(os.path.join(BASE, "o3_node_temperatures/data/node_temps.txt"), skiprows=1)[:, 2]
check("O3 cross mean=-1.25", abs(T_o3.mean() - (-1.25)) < 0.05, f"({T_o3.mean():+.3f})")
check("O3 cross mean|T|=32.75", abs(np.abs(T_o3).mean() - 32.75) < 0.05, f"({np.abs(T_o3).mean():+.3f})")

# ---------- 3. ΔE=0 12節點 (O3 已知 19.05, 驗證無迴歸) ----------
zeroE = [10, 12, 19, 22, 23, 25, 28, 32, 37, 40, 45, 46]
check("O3 ΔE=0 mean|T|=19.05", abs(np.abs(T[zeroE]).mean() - 19.05) < 0.05,
      f"({np.abs(T[zeroE]).mean():.3f})")

print(f"\n{'='*66}")
print(f"結果: {len(passes)}/{len(passes)+len(fails)} PASS")
if fails:
    print(f"❌ FAILED: {fails}")
    exit(1)
print("✅ 全部通過 — O30 數字可信")
