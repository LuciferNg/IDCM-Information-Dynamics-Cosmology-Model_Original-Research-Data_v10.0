#!/usr/bin/env python3
"""
O10 32: Silk × Fibonacci 正交性 — D₂>1 佯謬解決
=================================================
關鍵洞察: F_m (幾何重數) 同 Silk (物理阻尼) 正交!

P_m(obs) = 3ε·F_m·φ^(-2(m-1))·D(ℓ_m)   ← 錯 (D 乘喺總 P_m)
P_m(obs) = 3ε·[F_m·φ^(-2(m-1))]·D(ℓ_m)  ← 啱 (D 乘喺單路徑, F_m 乘數喺阻尼前)

點解 D₂>1? 因為之前用 P_m_th 冇乘 Silk:
  P₂_unl/P₂_th = 1.037 應該係 D(ℓ₂) < 1!

除非... P₂_th 本身就包含 Silk?
  CAMB unlensed 譜 = 純聲波 + Silk (冇 lensing)
  峰高比 P₂ = (A₄+A₅)/2 已經包含 Silk damping!
  
所以: A_m(obs) = A_m(acoustic) × D(ℓ_m)
  P₂_th = 3εφ⁻² (純幾何, 冇 Silk)
  P₂_unl = 3εφ⁻² × D(ℓ₂) = 0.1836?
  → D(ℓ₂) = 1.037 > 1 矛盾!

除非: 峰 4,5 嘅「acoustic 振幅」本身 > 3εφ⁻²
  = Fibonacci 重數 F_m 嘅效應!

等我用 Silk 擬合倒推: 如果 A_m(acoustic) = F_m·3ε·φ^(-2(m-1)) 係「單路徑×F_m」
"""
import camb
import numpy as np, math
from scipy.optimize import curve_fit
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

phi = (1 + 5**0.5) / 2
eps = phi**-1/4
F = [1, 1, 2, 3, 5, 8]

pars = camb.CAMBparams()
pars.set_cosmology(H0=67.36, ombh2=0.02237, omch2=0.1200, tau=0.0544)
pars.InitPower.set_params(ns=0.9649, As=2.1e-9)
pars.set_for_lmax(3000)
res = camb.get_results(pars)
unl = res.get_cmb_power_spectra(raw_cl=True, spectra=['unlensed_scalar'])['unlensed_scalar']
ell = np.arange(len(unl))
Dl_unl = unl[:, 0] * ell * (ell + 1) / (2*np.pi) * 1e12
D1 = Dl_unl[np.argmin(np.abs(ell-221))]

# 峰讀數 (CAMB unlensed 峰位)
peaks = {1: 221, 2: 536, 3: 814, 4: 1129, 5: 1419, 6: 1624, 7: 1812}
A = {}
for m, lp in peaks.items():
    idx = np.argmin(np.abs(ell-lp))
    A[m] = Dl_unl[idx]/D1
    print(f"峰{m} @ {ell[idx]}: A_unl = {A[m]:.4f}")

print()
print("=" * 72)
print("假設: A_m(acoustic) = 3ε·F_m·φ^(-2(m-1))·g_m")
print("      g_m = 每對嘅幾何因子 (可能係 1)")
print("=" * 72)

# P_m (簡併對平均) vs 理論
pairs = {1: (2, 3), 2: (4, 5), 3: (6, 7)}
print(f"{'m':>2} | {'P_unl':>7} | {'P_th':>7} | {'D=P/P_th':>8} | {'F_m':>3}")
for m, (a, b) in pairs.items():
    P_unl = (A[a]+A[b])/2
    P_th = 3*eps*F[m-1]*phi**(-2*(m-1))
    D = P_unl/P_th
    print(f"{m:>2} | {P_unl:>7.4f} | {P_th:>7.4f} | {D:>8.4f} | {F[m-1]:>3}")

print()
print("觀察: D₁=0.975, D₂=1.037, D₃=? (需要峰 6,7)")
print("如果 D 應該 < 1 (Silk), D₂>1 矛盾!")
print()

# 關鍵測試: D 應該係 ℓ 嘅平滑函數 (Silk tail)
# 用峰 6,7 (如果存在) 或者用高 ℓ 讀數
# unlensed 峰 6,7: 試搵
s = gaussian_filter1d(Dl_unl, sigma=3)
pk, _ = find_peaks(s, distance=30)
print("unlensed 高 ℓ 峰:", [(int(ell[p]), Dl_unl[p]) for p in pk if ell[p] > 1450][:8])

print()
print("=" * 72)
print("正交性驗證: D(ℓ) 擬合")
print("=" * 72)
# 用所有峰 (1-7) 擬合 D(ℓ) = exp[-(ℓ/ℓ_D)^{3/2}]
# 但峰 1 唔應該有 Silk (低 ℓ)
# 用峰 2-7
ell_pts = [536, 814, 1129, 1419]
D_pts = [A[2], A[3], A[4], A[5]]
# P_th 對應 (每峰, 唔係對平均)
# 峰2,3: P₁_th/1 (每峰 = P₁_th)
# 峰4,5: P₂_th/1
th_pts = [3*eps, 3*eps, 3*eps*phi**-2, 3*eps*phi**-2]
D_obs = [D_pts[i]/th_pts[i] for i in range(4)]
print("每峰: D_obs = A_m/P_m_th:")
for i in range(4):
    print(f"  ℓ={ell_pts[i]}: D={D_obs[i]:.4f}")

# 擬合 ln(D) vs ℓ^{1.5}
lnD = [math.log(d) for d in D_obs]
l15 = [e**1.5 for e in ell_pts]
# 線性擬合 ln(D) = -ℓ^{1.5}/ℓ_D^{1.5}
slope = np.polyfit(l15, lnD, 1)[0]
lD_fit = (-1/slope)**(2/3)
print(f"\n擬合: ln(D) = {slope:.6f}·ℓ^1.5 + b")
print(f"ℓ_D = {lD_fit:.0f}")
print()
print("問題: D₂ (ℓ=1129) 應該 = exp[-(1129/1085)^1.5] =", math.exp(-(1129/1085)**1.5))
print(f"但 D₂_obs = {D_obs[2]:.4f} → 唔匹配!")
print()
print("→ 結論: D 唔係單調 Silk tail!")
print("→ 峰 4,5 有額外結構 (Fibonacci 重數效應) 超出純 damping")
