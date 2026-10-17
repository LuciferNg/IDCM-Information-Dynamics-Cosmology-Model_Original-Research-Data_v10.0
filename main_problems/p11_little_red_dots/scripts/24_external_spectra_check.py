#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P11 closeout 攻堅 — 數據下載 + T1-T4 外部光譜判別 (2026-10-17)
================================================================
來源 (全部公開):
  1. Naidu+2025 MoM-BH*-1 (BH*): Zenodo 15059215 mom-uds01-v3 prism  z=7.76
  2. Rusakov+2026 Object A (JADES-GN-68797): DJA v4.4 G395H R~2700 + G395M
  3. Rusakov+2026 Object G (RUBIES-EGS-58237): DJA v4.4 G395M R~1000 + PRISM

判別目標 (record 14 T1-T4):
  T1: 對稱雙峰 + Δv(Hβ)=Δv(Hα) (最 sharp, 殺共振散射)
  T2: 峰距量子化 Δv = n·cπ/(88·4^ℓ)
  T3: 線心精確對稱
  T4: 跨尺度 a₀

輸出: data/24_external_spectra_check.json
"""
import json, numpy as np, os
from astropy.io import fits

# 光譜檔案目錄 (scratch, 公開數據留碟)
FITS_DIR = os.environ.get('P11_FITS_DIR', '/home/wsl/.hermes/cache/scratch/p11_data')

C_KM = 2.99792458e5
RESULT = {"date": "2026-10-17", "sources": {}}

def process(fn, z, lines, label, res_info):
    """峰搜尋 + 峰距 + 對稱性"""
    fn = os.path.join(FITS_DIR, fn)
    h = fits.open(fn)
    d = h[1].data
    w, f = d['wave'], d['flux']
    ok = ~np.isnan(f)
    out = {"file": fn, "z": z, "resolution": res_info}
    for lname, lrest in lines.items():
        cobs = lrest*(1+z)
        # continuum
        mcont = ok & (((w>=cobs-0.10)&(w<=cobs-0.06)) | ((w>=cobs+0.06)&(w<=cobs+0.10)))
        if mcont.sum() < 5:
            out[lname] = {"status": "cont-fail"}
            continue
        A = np.polyfit(w[mcont], f[mcont], 1)
        m = ok & (w>=cobs-0.03) & (w<=cobs+0.03)
        wl, fl = w[m], f[m]-np.polyval(A, w[m])
        # 峰搜尋 (弱 smooth: 3pt, 要 f>max*0.1 減少 noise peak)
        fs = np.convolve(fl, np.ones(3)/3, mode='same')
        peaks = []
        for i in range(1, len(fs)-1):
            if fs[i] > fs[i-1] and fs[i] > fs[i+1] and fs[i] > 0.1*fs.max():
                peaks.append((float(wl[i]), float(fs[i])))
        # 合併 <150 km/s
        merged = []
        for p, v in peaks:
            if merged and C_KM*abs(p-merged[-1][0])/cobs < 150:
                if v > merged[-1][1]:
                    merged[-1] = (p, v)
            else:
                merged.append((p, v))
        peaks = merged
        if len(peaks) >= 2:
            p1, p2 = peaks[0][0], peaks[-1][0]
            dv = C_KM*abs(p2-p1)/cobs
            mid = (p1+p2)/2
            off = C_KM*(mid-cobs)/cobs
        else:
            dv, off = None, None
        out[lname] = {
            "peaks": [{"lam": p, "dv_kms": C_KM*(p-cobs)/cobs} for p, _ in peaks],
            "outer_dv_kms": dv, "mid_offset_kms": off,
            "symmetric": abs(off) < 200 if off is not None else None,
        }
    return out

# ---------- 1. Naidu BH* ----------
RESULT["sources"]["naidu_bhstar"] = process(
    'mom_uds01_prism.fits', 7.76, {"Hbeta": 0.48614}, 'Naidu',
    "PRISM ~R100 (z=7.76, BH* MoM-uds01)")

# ---------- 2. Rusakov Object A ----------
RESULT["sources"]["rusakov_A_JADES_GN_68797"] = process(
    'objA_g395h.fits', 5.0385, {"Halpha": 0.65628}, 'Rusakov A',
    "G395H R~2700 (z~5.04, JADES-GN-68797)")

# ---------- 3. Rusakov Object G ----------
RESULT["sources"]["rusakov_G_RUBIES_EGS_58237"] = process(
    'objG_g395m.fits', 3.6493, {"Halpha": 0.65628}, 'Rusakov G',
    "G395M R~1000 (z=3.6493, RUBIES-EGS-58237)")

# ---------- IDCM 階梯匹配 (對每個外峰距) ----------
def ladder(ell, n):
    return n*np.pi*C_KM/(88*4**ell)

IDCM_NOTES = []
for src, s in RESULT["sources"].items():
    for lname, info in s.items():
        if not isinstance(info, dict) or "outer_dv_kms" not in info:
            continue
        dv = info["outer_dv_kms"]
        if dv is None:
            continue
        for ell in range(4):
            for n in range(1, 10):
                dv0 = ladder(ell, n)
                r = dv/dv0
                if r < 0.5:
                    continue   # 峰距細過階梯 → 唔構成匹配
                if abs(r-round(r)) < 0.015:
                    IDCM_NOTES.append(
                        f"{src}/{lname}: Δv={dv:.0f} ≈ {round(r)}×ℓ={ell} n={n} ({dv0:.0f}) EXACT (dev {(r-round(r))*100:+.1f}%)")
                elif abs(r-round(r)) < 0.10:
                    IDCM_NOTES.append(
                        f"{src}/{lname}: Δv={dv:.0f} ≈ {r:.2f}×ℓ={ell} n={n} ({dv0:.0f}) 近")

RESULT["idcm_ladder_matches"] = IDCM_NOTES

# T1: 有齊 Hα+Hβ 對比嗎?
t1_notes = []
if "Halpha" in RESULT["sources"]["rusakov_G_RUBIES_EGS_58237"] and \
   "Hbeta" in RESULT["sources"]["rusakov_G_RUBIES_EGS_58237"]:
    pass  # PRISM 版先有 Hβ 但 R~100 太粗 — 記低
t1_notes.append("T1 (Δv_Hβ=Δv_Hα) 判別: 未有光源同時有 R≥1000 嘅 Hα+Hβ — G 嘅 Hβ 只有 PRISM R~100 (不可辨 3000 km/s 內)")
RESULT["t1_notes"] = t1_notes

with open('/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/main_problems/p11_little_red_dots/data/24_external_spectra_check.json', 'w') as fh:
    json.dump(RESULT, fh, indent=2, ensure_ascii=False, default=str)
print(json.dumps({k: v for k, v in RESULT.items() if k != 'sources'}, indent=1, ensure_ascii=False))
for sname, s in RESULT["sources"].items():
    print(f"\n=== {sname} ===")
    for lname, info in s.items():
        if isinstance(info, dict) and "outer_dv_kms" in info:
            print(f"  {lname}: 外峰距={info['outer_dv_kms']} km/s, 中點偏移={info['mid_offset_kms']} km/s, 對稱={info['symmetric']}")