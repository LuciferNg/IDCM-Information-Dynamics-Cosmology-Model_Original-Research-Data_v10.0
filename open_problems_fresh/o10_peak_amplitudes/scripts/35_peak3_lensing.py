#!/usr/bin/env python3
"""
O10 35: 峰 3 異常 — lensing 效應檢查
=====================================
峰 3 @ 814 對 Silk 曲線異常高 (+42%)
檢查: unlensed vs lensed 峰 3 高度差異
"""
import camb
import numpy as np, math

phi = (1 + 5**0.5) / 2
eps = phi**-1/4

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

# 峰讀數 (CAMB 峰位)
peaks = {1: 221, 2: 536, 3: 814, 4: 1129, 5: 1419, 6: 1624, 7: 1812}
print("unlensed vs lensed 峰高:")
print(f"{'峰':>2} | {'ℓ':>5} | {'unlensed':>9} | {'lensed':>9} | {'比率':>6}")
for m, lp in peaks.items():
    iu = np.argmin(np.abs(ell-lp))
    il = np.argmin(np.abs(ell-lp))
    U = Dl_unl[iu]/Dl_unl[np.argmin(np.abs(ell-221))]
    L = Dl_lens[il]/Dl_lens[np.argmin(np.abs(ell-221))]
    print(f"{m:>2} | {lp:>5} | {U:>9.4f} | {L:>9.4f} | {U/L:>6.3f}")

print()
print("峰 3 (814): unlensed/lensed 比率應該 ≈1 (lensing 平滑)")
print("如果比率高 → unlensed 峰 3 特別高 (異常)")
print()

# 峰 3 對比峰 2 (同對)
i2 = np.argmin(np.abs(ell-536))
i3 = np.argmin(np.abs(ell-814))
print("峰 2 vs 峰 3 (簡併對):")
print(f"  unlensed: 峰2={Dl_unl[i2]:.0f}, 峰3={Dl_unl[i3]:.0f}, 比={Dl_unl[i3]/Dl_unl[i2]:.4f}")
print(f"  lensed:   峰2={Dl_lens[i2]:.0f}, 峰3={Dl_lens[i3]:.0f}, 比={Dl_lens[i3]/Dl_lens[i2]:.4f}")

# 峰 4 vs 5
i4 = np.argmin(np.abs(ell-1129))
i5 = np.argmin(np.abs(ell-1419))
print(f"\n峰 4 vs 峰 5:")
print(f"  unlensed: 峰4={Dl_unl[i4]:.0f}, 峰5={Dl_unl[i5]:.0f}, 比={Dl_unl[i5]/Dl_unl[i4]:.4f}")
print(f"  lensed:   峰4={Dl_lens[i4]:.0f}, 峰5={Dl_lens[i5]:.0f}, 比={Dl_lens[i5]/Dl_lens[i4]:.4f}")
