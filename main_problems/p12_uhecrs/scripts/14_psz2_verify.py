#!/usr/bin/env python3
"""
PSZ2 獨立驗證 — 節點核心真空 (1653 星系團)
============================================
PSZ1 發現: 節點核心 <4.5° 星系團不足 p=0.0048 (2.8σ)
獨立驗證: PSZ2 (1653 個, 更完整) 應該重現同一效應

如果 PSZ2 都顯示 p<0.05 → 真空效應係真嘅, 唔係 PSZ1 特異
"""
import math, os, json
import numpy as np
from astropy.io import votable

# ============ PSZ2 ============
v = votable.parse('/tmp/psz2_all.xml')
t = v.get_first_table().to_table()
cl_ra = np.array(t['ra'], dtype=float)
cl_dec = np.array(t['dec'], dtype=float)
print(f"PSZ2 星系團: {len(cl_ra)} 個 (獨立樣本)")

# ============ 節點 ============
CMB_DATA = '/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data'
nodes = []
with open(os.path.join(CMB_DATA, 'a5_nodes.txt')) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'): continue
        p = line.split()
        nodes.append((float(p[0]), float(p[1])))
nodes = np.array(nodes)

def ang_dist_mat(ra1, dec1, ra2, dec2):
    ra1, dec1 = np.radians(ra1), np.radians(dec1)
    ra2, dec2 = np.radians(ra2), np.radians(dec2)
    cosd = np.sin(dec1)[:, None]*np.sin(dec2)[None, :] + \
           np.cos(dec1)[:, None]*np.cos(dec2)[None, :]*np.cos(ra1[:, None]-ra2[None, :])
    return np.degrees(np.arccos(np.clip(cosd, -1, 1)))

D = ang_dist_mat(cl_ra, cl_dec, nodes[:, 0], nodes[:, 1])
d_min = D.min(axis=1)
print(f"最近節點距離: 中位數 {np.median(d_min):.2f}°")

# ============ 真空掃描 ============
rng = np.random.default_rng(42)
N_MC = 5000
print(f"\n{'='*70}")
print("PSZ2 節點核心真空掃描")
print(f"{'='*70}")
results = {}
for r in np.arange(3, 9, 0.5):
    obs = int((d_min < r).sum())
    mc = np.zeros(N_MC, dtype=int)
    for i in range(N_MC):
        ra_r = rng.uniform(0, 360, len(cl_ra))
        dec_r = np.degrees(np.arcsin(rng.uniform(-1, 1, len(cl_ra))))
        D_r = ang_dist_mat(ra_r, dec_r, nodes[:, 0], nodes[:, 1])
        mc[i] = (D_r.min(axis=1) < r).sum()
    p_lo = float((mc <= obs).mean())
    results[f"{r}deg"] = {"obs": int(obs), "obs_pct": float(obs/len(cl_ra)*100),
                          "mc_mean": float(mc.mean()), "mc_pct": float(mc.mean()/len(cl_ra)*100),
                          "p_deficit": p_lo}
    sig = "🟢" if p_lo < 0.05 else ("🟡" if p_lo < 0.15 else "  ")
    print(f"  <{r:.1f}°: 觀測 {obs:>4} ({obs/len(cl_ra)*100:5.1f}%)  MC={mc.mean():.1f} ({mc.mean()/len(cl_ra)*100:5.1f}%)  P(≤)={p_lo:.4f} {sig}")

best = min(results, key=lambda k: results[k]["p_deficit"])
print(f"\n最顯著不足: {best} (p={results[best]['p_deficit']:.4f})")

# ============ 對比 PSZ1 ============
print(f"\n{'='*70}")
print("PSZ1 vs PSZ2 對比")
print(f"{'='*70}")
print(f"  PSZ1 (1227): 最顯著 4.5° p=0.0048")
print(f"  PSZ2 (1653): 最顯著 {best} p={results[best]['p_deficit']:.4f}")
print(f"  → {'🟢 一致! 真空效應獨立重現' if results[best]['p_deficit'] < 0.05 else '🟡 未重現'}")
print(f"  → {'🟢 更強' if results[best]['p_deficit'] < 0.0048 else ('🟡 弱過 PSZ1' if results[best]['p_deficit'] < 0.05 else '')}")

# ============ 合併樣本 ============
print(f"\n{'='*70}")
print("合併 PSZ1 + PSZ2 (2880 星系團)")
print(f"{'='*70}")
# PSZ1 重新載入
v1 = votable.parse('/tmp/psz_all.xml')
t1 = v1.get_first_table().to_table()
ra1 = np.array(t1['ra'], dtype=float)
dec1 = np.array(t1['dec'], dtype=float)
# 合併 (去重: PSZ2 包含 PSZ1, 但做近似)
ra_all = np.concatenate([ra1, cl_ra])
dec_all = np.concatenate([dec1, cl_dec])
print(f"合併 (含重複): {len(ra_all)}")

D_all = ang_dist_mat(ra_all, dec_all, nodes[:, 0], nodes[:, 1])
d_all = D_all.min(axis=1)
for r in [3.0, 4.0, 4.5, 5.0]:
    obs = int((d_all < r).sum())
    mc = np.zeros(3000, dtype=int)
    for i in range(3000):
        ra_r = rng.uniform(0, 360, len(ra_all))
        dec_r = np.degrees(np.arcsin(rng.uniform(-1, 1, len(ra_all))))
        D_r = ang_dist_mat(ra_r, dec_r, nodes[:, 0], nodes[:, 1])
        mc[i] = (D_r.min(axis=1) < r).sum()
    p_lo = float((mc <= obs).mean())
    sig = "🟢" if p_lo < 0.05 else "  "
    print(f"  <{r:.1f}°: 觀測 {obs:>4} ({obs/len(ra_all)*100:5.1f}%)  MC={mc.mean():.1f}  P(≤)={p_lo:.4f} {sig}")

# ============ 保存 ============
os.makedirs('data', exist_ok=True)
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/psz2_vacuum_scan.json'), 'w') as f:
    json.dump({"psz2": results, "best": best, "p_best": results[best]["p_deficit"]}, f, indent=2)
print(f"\n已保存 data/psz2_vacuum_scan.json")
