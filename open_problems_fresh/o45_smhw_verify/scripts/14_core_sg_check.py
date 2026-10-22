#!/usr/bin/env python3
"""O45 — 控制: 核心區 SG fit 係咪穩健 (2026-09-12)
只用 θ<8° 核心區 fit SG (σ,n), 對比全域 fit — n=12 係咪真頂帽定全域假象"""
import json
import numpy as np
from scipy.optimize import curve_fit

prof_data = json.load(open('data/07_ring_nature.json'))
th = np.array(prof_data['radial_profiles']['SMICA']['theta'])
T = np.array(prof_data['radial_profiles']['SMICA']['T'])
A = 134.2

def sg(th, sigma, n):
    return -A * np.exp(-(th/sigma)**n / 2)

print("核心區 SG fit (smooth 後 profile, A 固定 134.2):")
print(f"  {'範圍':>10} {'σ(°)':>8} {'n':>6} {'RMS(μK)':>8}")
results = {}
for lo, hi in [(0, 6), (0, 8), (0, 10), (0, 12), (0, 20)]:
    m = (th >= lo) & (th < hi)
    try:
        popt, pcov = curve_fit(sg, th[m], T[m], p0=[5.5, 10],
                               bounds=([2, 2], [15, 20]), maxfev=5000)
        s, n = popt
        resid = T[m] - sg(th[m], s, n)
        rms = float(np.sqrt(np.mean(resid**2)))
        print(f"  [{lo:>2},{hi:>2}]°   {s:>8.3f} {n:>6.2f} {rms:>8.2f}")
        results[f"{lo}-{hi}"] = {'sigma': float(s), 'n': float(n), 'RMS': rms}
    except Exception as e:
        print(f"  [{lo},{hi}]: {e}")

# 對比: 全域
m = th < 25
popt, _ = curve_fit(sg, th[m], T[m], p0=[5.5, 10], bounds=([2, 2], [15, 20]), maxfev=5000)
print(f"  [0,25]°    {popt[0]:>8.3f} {popt[1]:>6.2f}")

# 正環剔除後 (θ<8° 核心 fit 應該無正環污染)
r = results.get('0-8')
if r:
    print(f"\n核心區 (0-8°) n={r['n']:.2f} — {'≈12 真頂帽' if abs(r['n']-12)<3 else '≠12 全域假象'}")

json.dump(results, open('data/14_core_sg_check.json', 'w'), indent=2)
print("\n儲存: data/14_core_sg_check.json")
