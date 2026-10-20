#!/usr/bin/env python3
"""
O2 F7 診斷 T3+T6 (manual dot) — annulus 背景 + 徑向 profile
===========================================================
修: hp.rotator.angdist (3,)x(N,3) 返回 garbage (max 120° 而非 2°);
   手動 dot product 精確 (min 0.0157°, max 2.0499° 正確)。
T3 v3 用咗 broken angdist -> 重做。
判据:
  T3 annulus 1-3°: peak-bg > 3x map std (0.5° 平滑)
  T6 徑向 FWHM vs 0.5° beam: 點源 => FWHM ≈ beam; 延展 => FWHM > beam
"""
import numpy as np
import healpy as hp
import math

SMICA = "/home/wsl/.hermes/cache/scratch/planck_smica/smica.fits"
F7 = (0.2, -37.9)

def degdist(v1, v2):
    """手動球面角距 (度) — 避免 angdist garbage"""
    d = np.arccos(np.clip(v1 @ v2.T, -1, 1))
    return np.degrees(d)

print("O2 F7 診斷 T3+T6 (manual dot)")
m = hp.read_map(SMICA, field=0)
nside = hp.get_nside(m)
sig = np.radians(0.5) / (2 * np.sqrt(2 * np.log(2)))
mm = hp.remove_dipole(hp.smoothing(m, sigma=sig))
vec = hp.ang2vec(F7[0], F7[1], lonlat=True)
peak = mm[hp.ang2pix(nside, *F7, lonlat=True)] * 1e6
print(f"  peak={peak:+.1f} μK, map std={mm.std()*1e6:.1f} μK")

# ---- T3: annulus 1-3° (manual) ----
print("\n[T3] annulus 1-3° 背景 (SMICA 0.5°, manual dot):")
pix_disc = hp.query_disc(nside, vec, np.radians(5.0))
pv = np.stack(hp.pix2vec(nside, pix_disc), axis=1)
ang_deg = degdist(vec.reshape(1, 3), pv)[0]
bg_mask = (ang_deg > 1.0) & (ang_deg < 3.0)
bg_mean = mm[pix_disc[bg_mask]].mean() * 1e6
print(f"  peak={peak:+.1f}, annulus={bg_mean:+.1f}, peak-bg={peak-bg_mean:+.1f}, n_bg={bg_mask.sum()}")
ok3 = (peak - bg_mean) > 3 * mm.std() * 1e6
print(("  ✅ T3 peak 明顯 (peak-bg > 3x std)" if ok3 else "  ❌ T3 fail"), f"(3xstd={3*mm.std()*1e6:.1f})")

# ---- T6: radial profile (manual) ----
print("\n[T6] 徑向 profile @0.5° 平滑 (manual dot):")
rads = [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0]
prof = []
for rad in rads:
    if rad == 0:
        prof.append(peak)
        continue
    pix_r = hp.query_disc(nside, vec, np.radians(rad + 0.05))
    pv_r = np.stack(hp.pix2vec(nside, pix_r), axis=1)
    a_r = degdist(vec.reshape(1, 3), pv_r)[0]
    sel = (a_r >= rad - 0.05) & (a_r < rad + 0.05)
    v = mm[pix_r[sel]].mean() * 1e6 if sel.sum() > 0 else np.nan
    prof.append(v)
    print(f"  r={rad:>4.2f}°: {v:+7.1f} μK (n={sel.sum()})")

half = peak / 2
fwhm_est = math.nan
for rad, v in zip(rads[1:], prof[1:]):
    if not math.isnan(v) and v < half:
        fwhm_est = 2 * rad
        break
if math.isnan(fwhm_est):
    print(f"  FWHM_est > {rads[-1]*2}° (peak {peak:.1f}, half {half:.1f})")
    ok6 = False
else:
    print(f"  FWHM_est ≈ {fwhm_est:.2f}°  (beam=0.5° 平滑)")
    ok6 = fwhm_est > 0.5
print(("  ✅ T6 結構延展 (FWHM > beam)" if ok6 else "  ❌ T6 fail — 疑似點源或超範圍"))

print("\n" + "=" * 50)
print("T3:", "✅" if ok3 else "❌", "| T6:", "✅" if ok6 else "❌")