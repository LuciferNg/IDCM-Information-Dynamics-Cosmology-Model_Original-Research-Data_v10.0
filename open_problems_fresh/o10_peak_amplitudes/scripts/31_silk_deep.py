#!/usr/bin/env python3
"""
O10 31: Silk 解耦深度分析 — unlensed D₂>1 殘留
=================================================
unlensed P₂ 需要 D=1.037 (>1) — Silk 單獨解釋唔到

假設: 讀數方法有偏差 (CAMB unlensed 峰位 1129/1419 vs Planck 1121/1409)
      + CAMB unlensed 峰 4,5 之間 dip 唔夠深 (lensing 平滑殘留)

方法: 
  A. 用 CAMB 自己嘅峰位 (1129/1419) 讀 (避免峰位錯配)
  B. 檢查 unlensed vs lensed 峰-谷深度差異
  C. 檢查 Silk damping 尾嘅理論形狀
"""
import camb
import numpy as np, math
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

phi = (1 + 5**0.5) / 2
eps = phi**-1/4

# CAMB
pars = camb.CAMBparams()
pars.set_cosmology(H0=67.36, ombh2=0.02237, omch2=0.1200, tau=0.0544)
pars.InitPower.set_params(ns=0.9649, As=2.1e-9)
pars.set_for_lmax(3000)
res = camb.get_results(pars)
unl = res.get_cmb_power_spectra(raw_cl=True, spectra=['unlensed_scalar'])['unlensed_scalar']
ell = np.arange(len(unl))
Dl_unl = unl[:, 0] * ell * (ell + 1) / (2*np.pi) * 1e12
lens = res.get_cmb_power_spectra(spectra=['total'], CMB_unit='muK')['total']
Dl_lens = lens[:, 0]

# 自動峰 (unlensed + lensed)
for label, Dl in [("unlensed", Dl_unl), ("lensed", Dl_lens)]:
    s = gaussian_filter1d(Dl, sigma=3)
    pk, _ = find_peaks(s, distance=30)
    print(f"{label} 自動峰: {[int(ell[p]) for p in pk[:6]]}")
    print(f"  heights: {[f'{Dl[p]:.0f}' for p in pk[:6]]}")

print()
print("=" * 72)
print("A. CAMB 自己峰位讀數")
print("=" * 72)
# unlensed 峰: 221, 536, 814, 1129, 1419
# lensed 峰: 220, 536, 813, 989, 1174, 1365, 1422 (lensing 移位)
# 用 unlensed 峰位配對: (536,814) → P₁, (1129,1419) → P₂
A_unl = {}
D1_unl = Dl_unl[np.argmin(np.abs(ell-221))]
for m, lp in {1: 221, 2: 536, 3: 814, 4: 1129, 5: 1419}.items():
    idx = np.argmin(np.abs(ell-lp))
    A_unl[m] = Dl_unl[idx]/D1_unl
    print(f"  峰{m} @ {ell[idx]}: A_unl = {A_unl[m]:.4f}")

P1_u = (A_unl[2]+A_unl[3])/2
P2_u = (A_unl[4]+A_unl[5])/2
P1_th, P2_th = 3*eps, 3*eps*phi**-2
print(f"\n  P₁ unlensed = {P1_u:.4f} vs {P1_th:.4f} → D={P1_u/P1_th:.4f}")
print(f"  P₂ unlensed = {P2_u:.4f} vs {P2_th:.4f} → D={P2_u/P2_th:.4f}")

print()
print("=" * 72)
print("B. unlensed vs lensed 峰-谷深度")
print("=" * 72)
# unlensed 谷: 搵峰之間嘅局部極小
for label, Dl in [("unlensed", Dl_unl), ("lensed", Dl_lens)]:
    s = gaussian_filter1d(Dl, sigma=3)
    tr, _ = find_peaks(-s, distance=30)
    troughs = [(ell[p], Dl[p]) for p in tr if 300 < ell[p] < 1600]
    print(f"\n{label} 谷 (300-1600):")
    for le, D in troughs:
        print(f"  ℓ={le}: D={D:.0f}")

# 峰-谷深度比
print()
print("峰-谷深度 (峰4/5 區域):")
# unlensed: 峰4 @1129, 峰5 @1419
# 搵中間谷
idx4 = np.argmin(np.abs(ell-1129))
idx5 = np.argmin(np.abs(ell-1419))
mid = (idx4+idx5)//2
valley_idx = np.argmin(Dl_unl[idx4:idx5]) + idx4
print(f"  unlensed: 峰4={Dl_unl[idx4]:.0f} @ {ell[idx4]}, 谷={Dl_unl[valley_idx]:.0f} @ {ell[valley_idx]}, 峰5={Dl_unl[idx5]:.0f} @ {ell[idx5]}")
print(f"  峰4-谷 = {Dl_unl[idx4]-Dl_unl[valley_idx]:.0f}, 峰5-谷 = {Dl_unl[idx5]-Dl_unl[valley_idx]:.0f}")
idx4l = np.argmin(np.abs(ell-1129))
idx5l = np.argmin(np.abs(ell-1419))
midl = (idx4l+idx5l)//2
valley_idx_l = np.argmin(Dl_lens[idx4l:idx5l]) + idx4l
print(f"  lensed:  峰4={Dl_lens[idx4l]:.0f} @ {ell[idx4l]}, 谷={Dl_lens[valley_idx_l]:.0f} @ {ell[valley_idx_l]}, 峰5={Dl_lens[idx5l]:.0f} @ {ell[idx5l]}")
print(f"  峰4-谷 = {Dl_lens[idx4l]-Dl_lens[valley_idx_l]:.0f}, 峰5-谷 = {Dl_lens[idx5l]-Dl_lens[valley_idx_l]:.0f}")

print()
print("=" * 72)
print("C. Silk damping tail 理論形狀")
print("=" * 72)
# Silk: D(ℓ) = exp[-(ℓ/ℓ_D)^{3/2}], 用高 ℓ tail 擬合 ℓ_D
# 用 unlensed ℓ>1600 嘅平滑下降 (冇峰, 純 damping)
tail_idx = np.where(ell > 1600)[0]
tail_l = ell[tail_idx]
tail_D = Dl_unl[tail_idx]
# 擬合 ln(D) vs ℓ^{3/2}
from scipy.optimize import curve_fit
def silk_model(l, lD, A):
    return A*np.exp(-(l/lD)**1.5)
try:
    popt, _ = curve_fit(silk_model, tail_l, tail_D, p0=[1400, 100])
    lD_fit, A_fit = popt
    print(f"  ℓ_D = {lD_fit:.0f}, A = {A_fit:.1f}")
    # 驗證峰 4,5 位置嘅預期阻尼
    for lp in [1129, 1419]:
        D_pred = A_fit*np.exp(-(lp/lD_fit)**1.5)
        D_obs = Dl_unl[np.argmin(np.abs(ell-lp))]
        print(f"  ℓ={lp}: 預期 {D_pred:.0f} vs 實際 {D_obs:.0f}")
except Exception as e:
    print(f"  fit fail: {e}")
