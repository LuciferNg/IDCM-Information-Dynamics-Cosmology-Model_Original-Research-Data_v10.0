#!/usr/bin/env python3
"""檢查 HFI frequency map 結構 + fill values"""
import healpy as hp
import numpy as np

m = hp.read_map('HFI_SkyMap_100_2048_R3.01_full.fits', field=0, nest=True)
bad = (~np.isfinite(m)) | (np.abs(m) > 1e-3)
print('bad pixels:', int(bad.sum()), '/', len(m), f'({bad.mean()*100:.4f}%)')
good = m[np.isfinite(m) & (np.abs(m) < 1e-3)]
print('good std(uK):', round(float(good.std())*1e6, 1))
hdr = hp.read_map('HFI_SkyMap_100_2048_R3.01_full.fits', h=True)[1]
for k in hdr.keys():
    if any(s in k for s in ['TUNIT', 'TTYPE', 'EXTNAME', 'BAND', 'FREQ', 'POLAR', 'NSIDE', 'ORDER']):
        print(' ', k, '=', hdr[k])
