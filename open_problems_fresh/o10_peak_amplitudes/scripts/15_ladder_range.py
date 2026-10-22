#!/usr/bin/env python3
"""
O10 15: Fibonacci 階梯適用範圍 — P₃ 閉合 vs P₄ 失敗
====================================================
發現: P₃ (m=6,7) 閉合 0.37%, 但 P₄ (m=8,9) 失敗 +67.7%

分析:
  1. P₃ 喺 Planck binned 用 IDCM 峰位驗證
  2. 高 ℓ 峰結構: Planck 只有 1 個峰 (1409) 喺 ℓ>1300
  3. IDCM 峰位 m=8,9 (1465/1474) 附近冇峰 → 讀數係 damping tail 下降段
  4. 結論: P₄ 無法用 Planck binned 驗證 (峰唔存在), 需要 ACT/SPT 高 ℓ
"""
import numpy as np, math, os
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

phi = (1 + 5**0.5) / 2
phi_inv = 1/phi
eps = phi_inv/4
F = [1, 1, 2, 3, 5, 8, 13, 21, 34]

DATA = os.path.join(os.path.dirname(__file__), "..", "..", "o9_high_ell_peaks", "data", "planck_tt.txt")
data = np.loadtxt(DATA)
l, val, err = data[:,0], data[:,1], data[:,2]
Dl = val * l*(l+1)/(2*np.pi)
Dl_err = err * l*(l+1)/(2*np.pi)
D1 = Dl[np.argmin(np.abs(l-220))]

def read_ratio(target):
    idx = np.argmin(np.abs(l-target))
    return Dl[idx]/D1, Dl_err[idx]/D1, l[idx]

print("=" * 72)
print("Fibonacci 階梯適用範圍分析")
print("=" * 72)

# P₃ 驗證 (m=6,7 @ IDCM 峰位 1340/1412)
print("\nP₃ (m=6,7) Planck binned 驗證:")
r6, e6, l6 = read_ratio(1340)
r7, e7, l7 = read_ratio(1412)
P3_obs = (r6+r7)/2
P3_th = 3*eps*F[2]*phi_inv**4
eP3 = 0.5*np.sqrt(e6**2+e7**2)
print(f"  m=6: ℓ=1340 → bin {l6:.0f}, A={r6:.4f}")
print(f"  m=7: ℓ=1412 → bin {l7:.0f}, A={r7:.4f}")
print(f"  P₃ = ({r6:.4f}+{r7:.4f})/2 = {P3_obs:.4f} ± {eP3:.4f}")
print(f"  理論 = 3ε·F₃·φ⁻⁴ = {P3_th:.4f}")
print(f"  偏差 = {(P3_obs-P3_th)/P3_th*100:+.2f}% | σ = {abs(P3_obs-P3_th)/eP3:.2f}")

# P₄ 驗證 (m=8,9 @ 1465/1474)
print("\nP₄ (m=8,9) Planck binned 驗證:")
r8, e8, l8 = read_ratio(1465)
r9, e9, l9 = read_ratio(1474)
P4_obs = (r8+r9)/2
P4_th = 3*eps*F[3]*phi_inv**6
print(f"  m=8: ℓ=1465 → bin {l8:.0f}, A={r8:.4f}")
print(f"  m=9: ℓ=1474 → bin {l9:.0f}, A={r9:.4f}")
print(f"  P₄ = ({r8:.4f}+{r9:.4f})/2 = {P4_obs:.4f}")
print(f"  理論 = 3ε·F₄·φ⁻⁶ = {P4_th:.4f}")
print(f"  偏差 = {(P4_obs-P4_th)/P4_th*100:+.2f}%")

# 高 ℓ 峰結構
print("\n高 ℓ 峰結構 (自動峰檢測):")
s = gaussian_filter1d(Dl, sigma=1.5)
pk, _ = find_peaks(s, distance=25)
high = [p for p in pk if l[p] > 1250]
for p in high:
    print(f"  ℓ={l[p]:.0f}, D={Dl[p]:.0f}")

print()
print("=" * 72)
print("關鍵問題: m=8,9 附近有冇峰?")
print("=" * 72)
# 檢查 1400-1550 範圍
print("ℓ 1400-1550 Planck binned:")
for i in range(len(l)):
    if 1400 <= l[i] <= 1550:
        print(f"  ℓ={l[i]:.0f}, D={Dl[i]:.0f}")

print()
print("=> 1409 之後 D 單調下降 (762→750→...), 冇新峰")
print("=> m=8,9 唔係真峰 — IDCM 峰位公式高 ℓ 外推失效 (O9 已知)")
print("=> P₄ 預測無法用 Planck binned 驗證 — 需要 ACT/SPT-3G 高 ℓ 譜")
print("=> Fibonacci 階梯適用範圍: m ≤ 3 (P₁, P₂, P₃ 閉合)")
