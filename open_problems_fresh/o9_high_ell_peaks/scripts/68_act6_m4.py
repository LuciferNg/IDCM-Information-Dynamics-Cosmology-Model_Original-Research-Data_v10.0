#!/usr/bin/env python3
"""
O9-D9: ACT DR6 m=4 檢查 — sacc 格式
======================================
ACT DR6 (act_dr6_cmb_sacc.fits) 有 45 bins
之前記錄: cl_00 = TT, bin 中心 1098 (m=5)

檢查 ACT DR6 喺 m=4 (1013) 附近有冇訊號
"""
import numpy as np
import os

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
print("="*78)
print("O9-D9: ACT DR6 m=4 檢查")
print("="*78)

try:
    from astropy.io import fits
    hdul = fits.open(os.path.join(DATADIR, 'act_dr6_cmb_sacc.fits'))
    print("\n1. sacc 文件結構:")
    for h in hdul:
        print(f"   {h.name}: {h.shape}")
    
    # 睇 sacc 內容
    hdr = hdul[0].header
    print(f"\n2. Header keys:")
    for k in list(hdr.keys())[:20]:
        print(f"   {k}: {hdr[k]}")
    
    # sacc 通常有: sacc 字典型 (data_01, meta_01...)
    # 或者單一 table
    for h in hdul:
        if h.data is not None and len(h.data) > 0:
            print(f"\n   {h.name} data columns: {h.data.dtype.names}")
            if hasattr(h.data, 'field'):
                for name in h.data.dtype.names[:10]:
                    print(f"     {name}: {h.data[name][:3]}")
except Exception as e:
    print(f"   ⚠️ astropy 讀取失敗: {e}")
    print("   改用 sacc library?")
    try:
        import sacc
        s = sacc.Sacc.load_fits(os.path.join(DATADIR, 'act_dr6_cmb_sacc.fits'))
        print(f"\n   sacc loaded: {len(s.bins)} bins, {len(s.mean)} mean")
        print(f"   bin types: {s.bins}")
    except ImportError:
        print("   sacc 未安裝")
