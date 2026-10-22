#!/usr/bin/env python3
"""
07_tau_refine.py — O25 一次過: τ 精確化 + 全尺度譜整合
=======================================================
用 17 個尺度 (SMICA 10 + NILC/Commander 7) 重擬合:
1. 冷熱差雙指數 (確認 τ₁=2/3, τ₂=2×4.17)
2. 固定 τ₁=2/3 vs 自由 (BIC)
3. node9 衰減模型 (平台+慢衰減)
4. ΔE0 比例全譜 (V形確認 + 大尺度回升)
5. 冷斑 τ 矛盾解釋
"""
import numpy as np
from scipy.optimize import curve_fit
import json, os

OUT = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o25_scale_spectrum"
DATA = os.path.join(OUT, "data")

with open(os.path.join(DATA, "scale_spectrum.json")) as f:
    R10 = json.load(f)
with open(os.path.join(DATA, "scale_spectrum_large.json")) as f:
    RL = json.load(f)

SCALES10 = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 4.17, 5.0, 7.0, 10.0]
EXTRA = [0.3, 0.75, 6.0, 8.0, 12.0, 15.0, 20.0]

def bic(n, rss, k):
    return n*np.log(rss/n) + k*np.log(n)

# ============ 1. SMICA 冷熱差雙指數 (10 尺度) ============
print("=" * 70)
print("1. 冷熱差雙指數 (SMICA 10 尺度)")
print("=" * 70)
x10 = np.array(SCALES10)
d10 = np.array([abs(R10['SMICA'][str(s)]['cold_hot_diff_uK']) for s in SCALES10])

def exp5(x, a1, t1, a2, t2, c):
    return a1*np.exp(-x/t1) + a2*np.exp(-x/t2) + c
popt, pcov = curve_fit(exp5, x10, d10, p0=(25, 1.5, 15, 8, 10), maxfev=40000)
perr = np.sqrt(np.diag(pcov))
a1, t1, a2, t2, c = popt
print(f"  自由: a1={a1:.2f} t1={t1:.4f}±{perr[1]:.4f} a2={a2:.2f} t2={t2:.4f}±{perr[3]:.4f} c={c:.2f}")

# 固定 t1=2/3
def exp5_fixed(x, a1, a2, t2, c):
    return a1*np.exp(-x/(2/3)) + a2*np.exp(-x/t2) + c
popt_f, _ = curve_fit(exp5_fixed, x10, d10, p0=(25, 15, 8, 10), maxfev=40000)
rss_f = np.sum((d10 - exp5_fixed(x10, *popt_f))**2)
rss_5 = np.sum((d10 - exp5(x10, *popt))**2)
print(f"  固定 t1=2/3: a1={popt_f[0]:.2f} a2={popt_f[1]:.2f} t2={popt_f[2]:.4f} c={popt_f[3]:.2f}")
print(f"  BIC: free(5par)={bic(10, rss_5, 5):.1f} fixed(4par)={bic(10, rss_f, 4):.1f}")

# ============ 2. 全 17 尺度 (NILC+Commander 合併) ============
print("\n" + "=" * 70)
print("2. 全 17 尺度冷熱差 (NILC + Commander)")
print("=" * 70)
# 用 NILC 延伸 + SMICA 原有 (因為 SMICA 冇延伸)
# 合併: SMICA 0.5-10 + NILC 12-20
x17 = np.array(SCALES10 + [12.0, 15.0, 20.0])
d17 = np.array([abs(R10['SMICA'][str(s)]['cold_hot_diff_uK']) for s in SCALES10] +
               [abs(RL['NILC'][str(s)]['cold_hot_diff']) for s in [12.0, 15.0, 20.0]])
popt17, _ = curve_fit(exp5, x17, d17, p0=(25, 1.5, 15, 8, 10), maxfev=40000)
pred17 = exp5(x17, *popt17)
r2_17 = 1 - np.sum((d17-pred17)**2)/np.sum((d17-d17.mean())**2)
print(f"  17 尺度: a1={popt17[0]:.2f} t1={popt17[1]:.4f} a2={popt17[2]:.2f} t2={popt17[3]:.4f} c={popt17[4]:.2f} R²={r2_17:.5f}")
# 固定 t1=2/3 喺 17 尺度
popt_f17, _ = curve_fit(exp5_fixed, x17, d17, p0=(25, 15, 8, 10), maxfev=40000)
rss_f17 = np.sum((d17 - exp5_fixed(x17, *popt_f17))**2)
rss_517 = np.sum((d17 - exp5(x17, *popt17))**2)
print(f"  固定 t1=2/3 17尺度: a1={popt_f17[0]:.2f} a2={popt_f17[1]:.2f} t2={popt_f17[2]:.4f} c={popt_f17[3]:.2f}")
print(f"  BIC: free={bic(len(x17), rss_517, 5):.1f} fixed={bic(len(x17), rss_f17, 4):.1f}")
print(f"  t2 vs 2×4.17=8.34: dev={abs(popt17[3]-8.34)/8.34*100:.2f}%")

# ============ 3. node9 衰減 ============
print("\n" + "=" * 70)
print("3. node9 衰減模型")
print("=" * 70)
# node9 SMICA + NILC 延伸
x9 = np.array(SCALES10 + [12.0, 15.0, 20.0])
n9 = np.array([R10['SMICA'][str(s)]['node9'] for s in SCALES10] +
              [RL['NILC'][str(s)]['node9'] for s in [12.0, 15.0, 20.0]])
print(f"  node9 全譜: {n9}")
# 兩指數: 快衰減 + 極慢衰減
def exp4(x, a1, t1, a2, t2):
    return a1*np.exp(-x/t1) + a2*np.exp(-x/t2)
try:
    popt9, _ = curve_fit(exp4, x9, n9, p0=(-80, 0.5, -90, 30), maxfev=40000)
    pred9 = exp4(x9, *popt9)
    r2_9 = 1 - np.sum((n9-pred9)**2)/np.sum((n9-n9.mean())**2)
    print(f"  雙指數: a1={popt9[0]:.1f} t1={popt9[1]:.3f} a2={popt9[2]:.1f} t2={popt9[3]:.2f} R²={r2_9:.4f}")
except Exception as e:
    print(f"  雙指數 FAIL: {e}")

# 冪律衰減
def pow2(x, a, b):
    return a*x**b
try:
    popt9p, _ = curve_fit(pow2, x9, n9, p0=(-120, -0.2), maxfev=40000)
    pred9p = pow2(x9, *popt9p)
    r2_9p = 1 - np.sum((n9-pred9p)**2)/np.sum((n9-n9.mean())**2)
    print(f"  冪律: a={popt9p[0]:.1f} b={popt9p[1]:.3f} R²={r2_9p:.4f}")
except Exception as e:
    print(f"  冪律 FAIL: {e}")

# 對數擬合
def log2(x, a, b):
    return a + b*np.log(x)
popt9l, _ = curve_fit(log2, x9, n9, p0=(-60, -15), maxfev=40000)
pred9l = log2(x9, *popt9l)
r2_9l = 1 - np.sum((n9-pred9l)**2)/np.sum((n9-n9.mean())**2)
print(f"  對數: a={popt9l[0]:.1f} b={popt9l[1]:.2f} R²={r2_9l:.4f}")

# ============ 4. ΔE0 比例全譜 ============
print("\n" + "=" * 70)
print("4. ΔE0 比例全譜 (SMICA 10 + NILC 延伸)")
print("=" * 70)
z10 = np.array([R10['SMICA'][str(s)]['zeroE_ratio'] for s in SCALES10])
z_ext = np.array([RL['NILC'][str(s)]['zeroE_ratio'] for s in [12.0, 15.0, 20.0]])
print(f"  SMICA: {z10}")
print(f"  NILC 延伸: {z_ext}")
print(f"  全譜最小值: SMICA @ {SCALES10[int(np.argmin(z10))]}° ({z10.min():.3f})")
print(f"  大尺度回升: 12°={z_ext[0]:.3f} 15°={z_ext[1]:.3f} 20°={z_ext[2]:.3f}")

# 高緯 ΔE0 延伸
h10 = np.array([json.load(open(os.path.join(DATA, 'decay_analysis.json')))['hi_zero_ratios'][str(s)] for s in SCALES10])
print(f"\n  高緯 SMICA: {h10}")
# 高緯 NILC 延伸
h_ext = [RL['NILC'][str(s)]['hi_zeroE_ratio'] for s in [12.0, 15.0, 20.0]]
print(f"  高緯 NILC 延伸: {h_ext}")

# ============ 5. 儲存 ============
out = {
    "smica_10": {"free": {"params": popt.tolist(), "bic": bic(10, rss_5, 5)},
                  "fixed_t1_2_3": {"params": popt_f.tolist(), "bic": bic(10, rss_f, 4)}},
    "all_17": {"free": {"params": popt17.tolist(), "bic": bic(len(x17), rss_517, 5)},
                "fixed_t1_2_3": {"params": popt_f17.tolist(), "bic": bic(len(x17), rss_f17, 4)},
                "r2": r2_17},
    "node9_model": {"exp4": {"params": popt9.tolist(), "r2": r2_9},
                     "log": {"params": popt9l.tolist(), "r2": r2_9l}},
    "zeroE_full": {"smica": z10.tolist(), "nilc_ext": z_ext.tolist()},
}
with open(os.path.join(DATA, "tau_refine.json"), "w") as f:
    json.dump(out, f, indent=2)
print("\n✅ saved data/tau_refine.json")
