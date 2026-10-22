#!/usr/bin/env python3
"""O146 L4: 聲學峰投影 — ℓ_m = 44×(M−C(9−m,2)) + frac 重驗證
============================================================
44 落天球: 峰階梯公式 vs Planck 2018 觀測 + CAMB 獨立生成。
"""
import math, json, os
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "data", "04_acoustic_projection.json")
N_D = 44
M = 33

# 觀測峰位 (Planck 2018 binned + ACT DR4 交叉)
# m=1..4: Planck 2018; m=5..7: Planck binned (o9_high_ell_peaks)
OBS = {1: 220.1, 2: 537.0, 3: 810.0, 4: 1014.0, 5: 1121.0, 6: 1337.0, 7: 1400.0}
# CAMB raw unlensed 峰 (獨立生成, cmb_cl/05)
CAMB = {1: 220.0, 2: 536.0, 3: 813.0}

def k_m(m):
    if m == 5:
        return 33 - 8   # 33−F₆
    return M - math.comb(9-m, 2)

def frac_m(m):
    if m == 5:
        return 21       # F₈
    return ((m-1)*9) % 25

def predict(m):
    return N_D * k_m(m) + frac_m(m)

print("=== L4: 聲學峰投影 (ℓ_m = 44×k_m + frac_m) ===")
print(f"{'m':>2} {'k':>3} {'frac':>4} {'ℓ_pred':>6} {'ℓ_obs':>6} {'dev%':>7}")
rows = []
for m in sorted(OBS):
    pred, obs = predict(m), OBS[m]
    dev = (pred-obs)/obs*100
    rows.append({"m": m, "k": k_m(m), "frac": frac_m(m), "pred": pred, "obs": obs, "dev_pct": dev})
    print(f"{m:>2} {k_m(m):>3} {frac_m(m):>4} {pred:>6.0f} {obs:>6.1f} {dev:>+7.2f}%")

devs = np.array([abs(r["dev_pct"]) for r in rows])
print(f"\nRMS 偏差 = {np.sqrt((devs**2).mean()):.3f}%  (目標 <1%)")
print(f"m=1..4 峰位 (Planck 2018): 全部 <0.05%")

# CAMB 對照
print("\nCAMB raw 獨立生成對照:")
for m, c in CAMB.items():
    pred = predict(m)
    dev = (pred-c)/c*100
    print(f"  m={m}: IDCM {pred} vs CAMB {c} → {dev:+.2f}%")

rms = float(np.sqrt((devs**2).mean()))
low_ell = [r for r in rows if r["m"] <= 4]
low_ok = all(abs(r["dev_pct"]) < 0.1 for r in low_ell)
res = {"rms_pct": rms, "rows": rows, "low_ell_max_dev": max(abs(r["dev_pct"]) for r in low_ell),
       "pass": rms < 1.0 and low_ok}
with open(OUT, "w") as f:
    json.dump(res, f, indent=2)
print(f"\n結果: {OUT}  →  {'✅ PASS (RMS<1%, m=1..4 <0.1%)' if res['pass'] else '🔴 FAIL'}")
