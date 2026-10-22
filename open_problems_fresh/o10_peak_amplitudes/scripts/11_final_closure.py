#!/usr/bin/env python3
"""
O10 11: 最終閉合驗證 — Planck binned + CAMB 交叉 + 修正項
=========================================================
完整公式: P_m = 3ε × F_m × φ^(-2(m-1)) × (1 + δ_m)
δ_m 候選: δ_m = ε·(-1)^m·C?

觀察 (unlensed @ IDCM 峰位):
  δ₁ = -2.508% = -0.02508
  δ₂ = +2.174% = +0.02174
  δ₃ = +0.477% = +0.00477

δ_m/ε: -16.23%, +14.07%, +3.09%
→ δ₁ ≈ -16ε? δ₂ ≈ +14ε? 唔係整數.
→ 試 δ_m = ε²·(-1)^m·k?
→ 試 δ_m ∝ (Lucas 組合)?
"""
import numpy as np, math, json, os

phi = (1 + 5**0.5) / 2
phi_inv = 1/phi
eps = phi_inv/4
F = [1, 1, 2, 3, 5, 8]

def S_fib(m):
    return F[m-1] * phi_inv**(2*(m-1))

# ============ Planck binned ground truth ============
DATA = os.path.join(os.path.dirname(__file__), "..", "..", "o9_high_ell_peaks", "data", "planck_tt.txt")
data = np.loadtxt(DATA)
l, val, err = data[:,0], data[:,1], data[:,2]
Dl = val * l*(l+1)/(2*np.pi)
Dl_err = err * l*(l+1)/(2*np.pi)

from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
s = gaussian_filter1d(Dl, sigma=1.5)
pk, _ = find_peaks(s, distance=25)

# 自動峰: 221(5816), 527(2579), 815(2553), 1121(1246), 1409(822)
peaks_ell = [int(l[p]) for p in pk]
peaks_D = [Dl[p] for p in pk]
peaks_err = [Dl_err[p] for p in pk]
print("Planck binned 自動峰:", list(zip(peaks_ell, [int(d) for d in peaks_D])))

# 簡併對 (2,3), (4,5): 用自動峰
# 峰 1 = 221, 峰 2 = 527, 峰 3 = 815, 峰 4 = 1121, 峰 5 = 1409
D1 = peaks_D[0]
pairs = {1: (peaks_D[1], peaks_D[2]), 2: (peaks_D[3], peaks_D[4])}

print()
print("=" * 72)
print("Planck binned: P_m = 3ε × F_m × φ^(-2(m-1))")
print("=" * 72)
results = {}
for m, (Da, Db) in pairs.items():
    P_obs = (Da + Db)/(2*D1)
    e_obs = 0.5*np.sqrt((peaks_err[2*m-1]/D1)**2 + (peaks_err[2*m]/D1)**2)
    P_th = 3*eps*S_fib(m)
    dev = (P_obs - P_th)/P_th*100
    sigma = abs(P_obs-P_th)/e_obs
    results[m] = {"P_obs": P_obs, "P_th": P_th, "dev": dev, "sigma": sigma}
    print(f"  P_{m} = {P_obs:.4f} ± {e_obs:.4f} | 理論 {P_th:.4f} | 偏差 {dev:+.3f}% | σ={sigma:.2f}")

# ============ 修正項分析 ============
print()
print("=" * 72)
print("修正項 δ_m 結構")
print("=" * 72)
# 用 Planck binned 嘅 δ
for m in results:
    d = results[m]["dev"]/100
    print(f"  δ_{m} = {d*100:+.3f}%  | δ/ε = {d/eps*100:+.2f}%  | δ/ε² = {d/eps**2:+.2f}")

print()
print("候選修正: δ_m = ±ε²·k?")
print(f"  ε² = {eps**2:.5f}")
print(f"  δ₁/ε² = {results[1]['dev']/100/eps**2:+.2f}")
print(f"  δ₂/ε² = {results[2]['dev']/100/eps**2:+.2f}")
print()
print("候選: δ_m = (-1)^m × ε² × L_m?  (Lucas)")
L = [2, 1, 3, 4, 7, 11]
print(f"  δ₁/ε² = {results[1]['dev']/100/eps**2:+.2f} vs L₁=1, -L₁=-1")
print(f"  δ₂/ε² = {results[2]['dev']/100/eps**2:+.2f} vs L₂=3, -L₂=-3")
print()
print("候選: δ_m = (-1)^m × ε × φ^{-m}?")
for m in [1, 2]:
    v = (-1)**m * eps * phi_inv**m
    print(f"  m={m}: {v*100:+.3f}% vs δ={results[m]['dev']:+.3f}%")

# 儲存
out = {"planck_peaks": list(zip(peaks_ell, [float(d) for d in peaks_D])),
       "pairs": {str(k): v for k, v in results.items()}}
with open(os.path.join(os.path.dirname(__file__), "..", "data", "fibonacci_ladder_results.json"), "w") as f:
    json.dump(out, f, indent=2)
print("\n已儲存 -> data/fibonacci_ladder_results.json")
