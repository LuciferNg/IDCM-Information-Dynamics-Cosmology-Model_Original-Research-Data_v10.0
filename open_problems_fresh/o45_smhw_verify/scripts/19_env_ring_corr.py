#!/usr/bin/env python3
"""O45 — 環境環 vs 節點溫度: 補償環機制檢查 (2026-09-12)
問題: 冷斑環境 +38 (正), node 47 環境 −57 (負) — 有冇系統結構?
假設: 如果環境環 ∝ −T_node (冷→正環, 熱→負環) = 補償機制 (能量守恆)
      如果冇相關 = 純大尺度背景
"""
import os, json
import numpy as np
import healpy as hp

PROJECT = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
CACHE = os.path.join(PROJECT, 'open_problems_fresh/o5_catalog_compare/data/smooth_cache')
NSIDE = 256

data = json.load(open('data/02_smhw_full_data.json'))
gal = np.array([data['nodes'][f'node{i}']['gal'] for i in range(60)])
l, b = gal.T

m = hp.ud_grade(hp.read_map(os.path.join(CACHE, 'smica2_smooth4.17.fits')), NSIDE)
npix = hp.nside2npix(NSIDE)
v = hp.pix2vec(NSIDE, np.arange(npix))

# 60 節點: T_pix + 環境環 (10-20°, 12-18°)
T_pix = np.array([m[hp.ang2pix(NSIDE, l[i], b[i], lonlat=True)] for i in range(60)]) * 1e6
env_1020 = np.empty(60)
env_1218 = np.empty(60)
for i in range(60):
    v0 = hp.ang2vec(l[i], b[i], lonlat=True)
    cosang = np.clip(v[0]*v0[0] + v[1]*v0[1] + v[2]*v0[2], -1, 1)
    ang = np.degrees(np.arccos(cosang))
    env_1020[i] = np.mean(m[(ang >= 10) & (ang < 20)]) * 1e6
    env_1218[i] = np.mean(m[(ang >= 12) & (ang < 18)]) * 1e6

print("=== 60 節點: 環境環 (10-20°) vs 節點溫度 ===")
print(f"  T_pix: mean={T_pix.mean():+.1f}, std={T_pix.std():.1f}")
print(f"  環境環: mean={env_1020.mean():+.2f}, std={env_1020.std():.2f}")
print(f"  環境環 12-18°: mean={env_1218.mean():+.2f}, std={env_1218.std():.2f}")

# 相關性
corr_1020 = np.corrcoef(T_pix, env_1020)[0, 1]
corr_1218 = np.corrcoef(T_pix, env_1218)[0, 1]
print(f"\n  corr(T_pix, env_10-20) = {corr_1020:+.3f}")
print(f"  corr(T_pix, env_12-18) = {corr_1218:+.3f}")
print(f"  (補償機制 → 負相關; 純背景 → ~0)")

# 冷/熱節點環境對比
cold = T_pix < 0
hot = ~cold
print(f"\n  冷節點環境: {env_1020[cold].mean():+.2f} ± {env_1020[cold].std():.2f} (n={cold.sum()})")
print(f"  熱節點環境: {env_1020[hot].mean():+.2f} ± {env_1020[hot].std():.2f} (n={hot.sum()})")

# 關鍵節點
for i in [0, 47, 9, 33, 56, 53]:
    print(f"  node {i:>2}: T={T_pix[i]:>+8.2f}, env(10-20)={env_1020[i]:>+7.2f}, env(12-18)={env_1218[i]:>+7.2f}")

# 線性 fit: env = a·T + c
a, c = np.polyfit(T_pix, env_1020, 1)
print(f"\n  線性 fit: env = {a:.4f}·T + {c:+.2f}")
print(f"  若補償: a 應負且 |a|≈環/中心比例")

# 隨機控制: 60 隨機點同量級
rng = np.random.default_rng(42)
u = rng.uniform(-1, 1, 500)
phi_r = rng.uniform(0, 2*np.pi, 500)
v_rand = np.array([np.sqrt(1-u**2)*np.cos(phi_r), np.sqrt(1-u**2)*np.sin(phi_r), u]).T
env_rand = np.array([np.mean(m[(np.degrees(np.arccos(np.clip(v_rand[k]@v, -1, 1))) >= 10) & (np.degrees(np.arccos(np.clip(v_rand[k]@v, -1, 1))) < 20)])*1e6 for k in range(500)])
print(f"\n  隨機 500 點環境: {env_rand.mean():+.2f} ± {env_rand.std():.2f}")
print(f"  60 節點環境 std {env_1020.std():.2f} vs 隨機 std {env_rand.std():.2f} → 節點環境係咪特別?")

json.dump({'T_pix': T_pix.tolist(), 'env_1020': env_1020.tolist(), 'env_1218': env_1218.tolist(),
           'corr_1020': float(corr_1020), 'corr_1218': float(corr_1218),
           'cold_env_mean': float(env_1020[cold].mean()), 'hot_env_mean': float(env_1020[hot].mean()),
           'random_env_mean': float(env_rand.mean()), 'random_env_std': float(env_rand.std())},
          open('data/18_env_ring_corr.json', 'w'), indent=2)
print("\n儲存: data/18_env_ring_corr.json")
