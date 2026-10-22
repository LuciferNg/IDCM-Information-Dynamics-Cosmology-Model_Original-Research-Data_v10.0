#!/usr/bin/env python3
"""
O9: 重新生成 o9_final_v2.json (修正 m=6 配對 bug)
====================================================
用 script 13 嘅正確配對邏輯 (IDCM 修正中心):
m=6 pred=1340, window ±15 → bin 局部極大 1337 (唔係 1355)
"""
import numpy as np
import math as _m
import os, json
from fractions import Fraction

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
phi = (1 + 5**0.5)/2
F = [0, 1]
for i in range(2, 15): F.append(F[-1]+F[-2])

planck = np.loadtxt(os.path.join(DATADIR, 'planck_tt.txt'))
ell_p = planck[:,0].astype(int); C_p = planck[:,1]
D_bin = C_p * ell_p*(ell_p+1)/(2*np.pi)

def idcm_fix(m):
    if m == 5:
        return 44*(33 - F[6]) + F[8]
    return 44*(33 - _m.comb(9-m, 2)) + (((m-1)*9) % 25)

results = {}
for m in range(1, 8):
    pred = idcm_fix(m)
    win = 60 if m == 5 else 15
    mask = np.abs(ell_p - pred) <= win
    idxs = np.where(mask)[0]
    best_l, best_D = None, -1
    for i in idxs:
        if i > 0 and i < len(ell_p)-1:
            if D_bin[i] >= D_bin[i-1] and D_bin[i] >= D_bin[i+1]:
                if D_bin[i] > best_D:
                    best_l, best_D = int(ell_p[i]), float(D_bin[i])
    if best_l is None:
        j = np.argmax(D_bin[idxs])
        best_l, best_D = int(ell_p[idxs[j]]), float(D_bin[idxs[j]])
    dev = (best_l - pred)/pred*100
    results[m] = {"pred": int(pred), "obs": best_l, "D": best_D, "dev": float(dev)}

devs = [results[m]["dev"] for m in range(1, 8)]
rms = float(np.sqrt(np.mean(np.array(devs)**2)))

idcm_dl = [results[m+1]["pred"]-results[m]["pred"] for m in range(1, 7)]
obs_dl = [results[m+1]["obs"]-results[m]["obs"] for m in range(1, 7)]

A1 = results[1]["D"]
amps = {}
for m in range(1, 8):
    a = results[m]["D"]/A1
    fr = Fraction(a).limit_denominator(50)
    amps[str(m)] = {"ratio": float(a), "frac": f"{fr.numerator}/{fr.denominator}"}

out = {
    "formula": {
        "general": "l_m = 44*(33-C(9-m,2)) + ((m-1)*9 mod 25),  m=1..4,6,7",
        "m5": "l_5 = 44*(33-F6) + F8 = 44*25+21 = 1121  (F6=8, F8=21)",
        "m5_shift": "1199 -> 1121, shift -78 = -2*44 + 10 = -88 + 10"
    },
    "closure": {str(m): results[m] for m in range(1, 8)},
    "rms_pct": rms,
    "peak_spacing_idcm": idcm_dl,
    "peak_spacing_obs": obs_dl,
    "conservation_dl4_dl5": {
        "idcm_orig": int((44*(33-_m.comb(5,2))+(((5-1)*9)%25)) - (44*(33-_m.comb(6,2))+(((4-1)*9)%25)) + (44*(33-_m.comb(4,2))+(((6-1)*9)%25)) - (44*(33-_m.comb(5,2))+(((5-1)*9)%25))),
        "idcm_fix": int(idcm_dl[3]+idcm_dl[4]),
        "obs": int(obs_dl[3]+obs_dl[4])
    },
    "amplitude_fracs": amps
}
with open(os.path.join(DATADIR, 'o9_final_v2.json'), 'w') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print("重新生成 o9_final_v2.json:")
for m in range(1, 8):
    print(f"  m={m}: pred={results[m]['pred']} obs={results[m]['obs']} dev={results[m]['dev']:+.2f}%")
print(f"  RMS: {rms:.4f}%")
print(f"  守恆 (idcm_fix): {idcm_dl[3]}+{idcm_dl[4]} = {idcm_dl[3]+idcm_dl[4]}")
print(f"  守恆 (obs): {obs_dl[3]}+{obs_dl[4]} = {obs_dl[3]+obs_dl[4]}")
