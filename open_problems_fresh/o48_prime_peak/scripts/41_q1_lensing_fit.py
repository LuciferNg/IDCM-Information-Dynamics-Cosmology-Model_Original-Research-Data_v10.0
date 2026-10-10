#!/usr/bin/env python3
"""
O48 Q1.24b: lensing 前向 — CAMB lensed/unlensed 直接 fit 有效高斯核
=============================================================
Q1.24 解析 σ_lens=59.32 但單位可能唔穩。正路: 用 CAMB 直接輸出
lensed 同 unlensed TT 譜, 掃 Gaussian 核寬度 σ, 睇邊個 σ 令
unlensed ⊗ G(σ) 最似 lensed — 冇解析近似, 純前向。

然後對比 IDCM 候選 {49.5=297/6, 50, 55=F₁₀, 60}。
"""
import math, sys
import numpy as np
import camb

pars = camb.CAMBparams()
pars.set_cosmology(H0=67.36, ombh2=0.02237, omch2=0.1200, mnu=0.06, omk=0, tau=0.0544)
pars.InitPower.set_params(As=2.1e-9, ns=0.9649)
pars.set_for_lmax(4000)
pars.set_accuracy(AccuracyBoost=2)
res = camb.get_results(pars)
specs = res.get_cmb_power_spectra(lmax=4000, raw_cl=True)
lensed = specs['total'][:, 0]       # TT lensed
unlensed = specs['unlensed_total'][:, 0]  # TT unlensed
l = np.arange(len(lensed))

print("="*72)
print("CAMB lensed vs unlensed TT — 有效高斯核 fit")
print("="*72)
print(f"lmax={len(l)-1}, lensed[2000]={lensed[2000]:.3e}, unlensed[2000]={unlensed[2000]:.3e}")

# 峰谷區間 fit (ℓ 200..2500, 用普朗克可接區段)
l_fit = np.arange(200, 2501)
D_l = l_fit*(l_fit+1)/(2*np.pi) * lensed[l_fit]
D_u = l_fit*(l_fit+1)/(2*np.pi) * unlensed[l_fit]

# fit: 搵 α, β 令 D_u 平滑後 ≈ α·D_l 喺峰谷起伏層面
# 用緩變包絡歸一化: 比較"峰谷相對起伏"最穩
# 方法: 對 D_l 同 D_u 各自 detrend (局部平滑), 比較殘差
def smooth(y, w=31):
    k = np.ones(w)/w
    return np.convolve(y, k, mode='same')

env_l = smooth(D_l, 151)
env_u = smooth(D_u, 151)
r_l = D_l/env_l - 1   # 峰谷起伏 (lensed)
r_u = D_u/env_u - 1   # 峰谷起伏 (unlensed)

print(f"起伏 RMS: lensed {r_l.std():.4f}, unlensed {r_u.std():.4f} (lensing 壓制起伏)")

# 掃 σ: unlensed 起伏 ⊗ 高斯 → 對 lensed 起伏 corr
l_grid = np.arange(2000)  # 網格用
sigmas = np.arange(10, 101, 2)
best = (0, -9)
print("\n掃描有效高斯核 σ (corr: unlensed⊗G(σ) vs lensed):")
for s in sigmas:
    # 對每個 fit ℓ, 將 r_u 用高斯核 (寬度 s 喺 ℓ-space) 平滑
    # 高斯卷積喺 ℓ-space: kernel = exp(-(Δℓ)²/(2s²))
    kern = np.exp(-0.5*(np.arange(len(l_fit))[:,None] - np.arange(len(l_fit))[None,:])**2/s**2)
    kern /= kern.sum(axis=1, keepdims=True)
    r_sm = kern @ r_u
    c = float(np.corrcoef(r_sm, r_l)[0, 1])
    if c > best[0]:
        best = (c, s)
    if s in [40, 45, 50, 55, 60, 70, 80]:
        print(f"  σ={s:3d}: corr={c:+.3f}")
print(f"最佳 σ = {best[1]} (corr {best[0]:+.3f})")

print("\n" + "="*72)
print("IDCM 候選對比")
print("="*72)
cands = {"49.5 (297/6)": 49.5, "50": 50, "55 (F₁₀)": 55, "60": 60}
for lab, c in cands.items():
    diff = abs(c - best[1])
    print(f"  {lab}: 差={diff:.1f} ({'PASS' if diff < 5 else 'FAIL'})")

print("\n" + "="*72)
print(f"SUMMARY: 有效 lensing 高斯寬度 = {best[1]}")
print("="*72)
sys.exit(0)