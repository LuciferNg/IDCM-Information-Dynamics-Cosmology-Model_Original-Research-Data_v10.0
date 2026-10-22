#!/usr/bin/env python3
"""
O10 33: Silk 曲線擬合 + F_m 幾何因子倒推 (最終)
=================================================
數據 (unlensed, CAMB 峰位):
  P₁: D=0.9754 @ <ℓ>=675
  P₂: D=1.0367 @ <ℓ>=1274
  P₃: D=0.4634 @ <ℓ>=1718

如果 Silk D(ℓ) = exp[-(ℓ/ℓ_D)^{3/2}]:
  D₁ = 0.975 → ℓ_D = 675/(-ln 0.975)^{2/3} = ?
  D₃ = 0.463 → ℓ_D = 1718/(-ln 0.463)^{2/3} = ?
  如果兩個 ℓ_D 一致 → Silk 成立, P₂ 嘅 D>1 係異常
  如果唔一致 → Silk 唔係唯一機制
"""
import numpy as np, math, camb
from scipy.optimize import curve_fit

phi = (1 + 5**0.5) / 2
eps = phi**-1/4

# 重載 CAMB unlensed
pars = camb.CAMBparams()
pars.set_cosmology(H0=67.36, ombh2=0.02237, omch2=0.1200, tau=0.0544)
pars.InitPower.set_params(ns=0.9649, As=2.1e-9)
pars.set_for_lmax(3000)
res = camb.get_results(pars)
unl = res.get_cmb_power_spectra(raw_cl=True, spectra=['unlensed_scalar'])['unlensed_scalar']
ell = np.arange(len(unl))
Dl_unl = unl[:, 0] * ell * (ell + 1) / (2*np.pi) * 1e12
D1_ref = Dl_unl[np.argmin(np.abs(ell-221))]

# 峰讀數
peaks = {1: 221, 2: 536, 3: 814, 4: 1129, 5: 1419, 6: 1624, 7: 1812}
A = {}
for m, lp in peaks.items():
    idx = np.argmin(np.abs(ell-lp))
    A[m] = Dl_unl[idx]/D1_ref

# 數據
data = [
    (1, 675, 0.9754),
    (2, 1274, 1.0367),
    (3, 1718, 0.4634),
]

print("用 D(ℓ) = exp[-(ℓ/ℓ_D)^{3/2}] 倒推 ℓ_D:")
for m, l, D in data:
    if D > 0:
        lD = l / (-math.log(D))**(2/3)
        print(f"  P_{m} @ <ℓ>={l}: D={D:.4f} → ℓ_D = {lD:.0f}")
    else:
        print(f"  P_{m}: D={D} (無效)")

print()
print("P₁ 同 P₃ 嘅 ℓ_D 唔一致 → Silk 唔係唯一!")
print("P₂ 嘅 D>1 表示峰 4,5 有額外抬升")
print()

# 假設: 真正機制係「每對一個幾何因子 g_m」
# A_m = 3ε·F_m·φ^(-2(m-1))·g_m·D(ℓ_m)
# 用 D₁ (峰2,3) 同 D₃ (峰6,7) 定義 Silk 曲線, 倒推 g₂
# 但 P₂ 嘅 D>1... 用另一方法:
# 用高 ℓ tail (peak 6,7 + 更高) 擬合 Silk 曲線

# CAMB 高 ℓ 峰: 1739(54.4), 2038(31.6), 2348(14.6), 2639(7.9)
# 用呢啲 + 峰 6,7 擬合純 Silk (佢哋冇 Fibonacci 重數?)
high = [(1739, 54.4), (2038, 31.6), (2348, 14.6), (2639, 7.9)]
D1_ref = 773  # unlensed D₁

print("高 ℓ tail 峰 (相對 D₁):")
A_tail = {}
for le, D in high:
    A_tail[le] = D/D1_ref
    print(f"  ℓ={le}: A={D/D1_ref:.5f}")

# 擬合 A(ℓ) = A₀·exp[-(ℓ/ℓ_D)^{1.5}]
from scipy.optimize import curve_fit
import numpy as np

def model(l, A0, lD):
    return A0*np.exp(-(l/lD)**1.5)

l_arr = np.array([1739, 2038, 2348, 2639])
A_arr = np.array([A_tail[1739], A_tail[2038], A_tail[2348], A_tail[2639]])
popt, _ = curve_fit(model, l_arr, A_arr, p0=[0.5, 1200], maxfev=5000)
A0, lD = popt
print(f"\n高 ℓ tail 擬合: A₀ = {A0:.4f}, ℓ_D = {lD:.0f}")

# 預測峰 4,5 位置
print("\n用呢條 Silk 曲線預測:")
for lp, m in [(1129, 4), (1419, 5)]:
    pred = A0*math.exp(-(lp/lD)**1.5)
    obs = A[4] if m == 4 else A[5]
    print(f"  峰{m} @ ℓ={lp}: Silk 預測 {pred:.4f} vs 實際 {obs:.4f} → 比值 {obs/pred:.3f}")

# 峰 2,3
for lp, m in [(536, 2), (814, 3)]:
    pred = A0*math.exp(-(lp/lD)**1.5)
    obs = A[2] if m == 2 else A[3]
    print(f"  峰{m} @ ℓ={lp}: Silk 預測 {pred:.4f} vs 實際 {obs:.4f} → 比值 {obs/pred:.3f}")

# 峰 6,7
for lp, m in [(1624, 6), (1812, 7)]:
    pred = A0*math.exp(-(lp/lD)**1.5)
    obs = A[6] if m == 6 else A[7]
    print(f"  峰{m} @ ℓ={lp}: Silk 預測 {pred:.4f} vs 實際 {obs:.4f} → 比值 {obs/pred:.3f}")

print()
print("如果峰 2-7 全部 ratio ≈ 1 → Silk 曲線完美 (冇 Fibonacci 重數)")
print("如果 ratio 有結構 (0.44, 1.4, 0.46...) → 每峰獨立幾何因子")
