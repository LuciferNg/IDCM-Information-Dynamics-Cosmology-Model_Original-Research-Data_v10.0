#!/usr/bin/env python3
"""
24_bmode_mc.py — O26-G3: EB→β Monte Carlo noise floor
========================================================
naive EB estimator 喺 den=Σ(EE−BB)≈0 時爆炸。
用 MC 模擬建立 β 嘅 noise floor:
1. 用 SMICA Cℓ (EE, BB) 生成 200 個 Gaussian 偏振模擬
2. 每個模擬計 β (用相同 estimator)
3. β 分佈 = noise floor → 觀察 β 嘅顯著性
"""
import healpy as hp
import numpy as np
import math
from astropy.io import fits

MAP = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o26_node57_region/data/smica_iqu_2048.fits"

results = []
def log(*args):
    line = " ".join(str(a) for a in args)
    print(line, flush=True)
    results.append(line)

log("=" * 72)
log("O26-G3: EB→β MC noise floor")
log("=" * 72)

# 讀 map
h = fits.open(MAP)
data = h[1].data
I_full = np.array(data['I_STOKES'], dtype=float)
Q_full = np.array(data['Q_STOKES'], dtype=float)
U_full = np.array(data['U_STOKES'], dtype=float)
pmask_full = np.array(data['PMASK'], dtype=float)
h.close()

# 降採樣
nside = 256
I_low = hp.ud_grade(I_full, nside)
Q_low = hp.ud_grade(Q_full, nside)
U_low = hp.ud_grade(U_full, nside)
pmask_low = (hp.ud_grade(pmask_full, nside) > 0.5).astype(float)
log(f"nside={nside}, mask 覆蓋 {pmask_low.mean()*100:.1f}%")

# 真 map 嘅 Cℓ (做 MC 輸入)
from healpy.sphtfunc import anafast
cl_obs = anafast([I_low*pmask_low, Q_low*pmask_low, U_low*pmask_low], lmax=128, iter=3)
ee_obs, bb_obs = cl_obs[1], cl_obs[2]

# MC: 200 個模擬
betas = []
for i in range(200):
    # synfast: 由 Cℓ 生成 Q/U map (帶 mask 效果由後處理)
    # 用 TT=0, EE, BB 光譜; TE=TB=EB=0 (null 假設)
    cl_in = np.zeros((6, 129))
    cl_in[1] = ee_obs  # EE
    cl_in[2] = bb_obs  # BB
    # 用 numpy global seed 令每次唔同 (healpy 1.19 冇 rng 參數)
    np.random.seed(i * 37 + 13)
    maps = hp.synfast(cl_in, nside, lmax=128, pol=True, new=True, verbose=False)
    Q_sim, U_sim = maps[1], maps[2]
    # 應用 mask
    Q_sim_m = Q_sim * pmask_low
    U_sim_m = U_sim * pmask_low
    cl_sim = anafast([Q_sim_m*0, Q_sim_m, U_sim_m], lmax=128, iter=3)
    ee_s, bb_s, eb_s = cl_sim[1], cl_sim[2], cl_sim[3]
    l = np.arange(2, 129)
    num = np.sum((2*l+1) * 2 * eb_s[l])
    den = np.sum((2*l+1) * (ee_s[l] - bb_s[l]))
    if abs(den) > 1e-30:
        beta = 0.5 * np.arctan2(num, den)
        betas.append(np.degrees(beta))
    if (i+1) % 50 == 0:
        log(f"  MC {i+1}/200 done")

betas = np.array(betas)
log(f"\nMC β 分佈 (n={len(betas)}):")
log(f"  mean = {np.mean(betas):.2f}°, std = {np.std(betas):.2f}°")
log(f"  95% CI = [{np.percentile(betas, 2.5):.2f}, {np.percentile(betas, 97.5):.2f}]°")
log(f"  文獻 β = 0.277°±0.057° (4.8σ) — 呢個係 MC 可以分辨嘅嗎?")

# 觀察 β
l = np.arange(2, 129)
cl_obs2 = anafast([I_low*pmask_low, Q_low*pmask_low, U_low*pmask_low], lmax=128, iter=3)
num_o = np.sum((2*l+1) * 2 * cl_obs2[3][l])
den_o = np.sum((2*l+1) * (cl_obs2[1][l] - cl_obs2[2][l]))
beta_obs = 0.5 * np.arctan2(num_o, den_o)
beta_obs_deg = np.degrees(beta_obs)
log(f"\n觀察 β = {beta_obs_deg:.2f}°")
log(f"  相對 MC noise floor: {(beta_obs_deg - np.mean(betas))/np.std(betas):.2f}σ")
log(f"  {'✅ 喺 noise 內 (無法分辨)' if abs(beta_obs_deg) < 2*np.std(betas) else '⚠️ 超出 noise'}")

with open("/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o26_node57_region/data/node57_bmode_mc.txt", "w") as f:
    f.write("\n".join(results) + "\n")
print(f"\n✅ 結果寫入 data/node57_bmode_mc.txt")
