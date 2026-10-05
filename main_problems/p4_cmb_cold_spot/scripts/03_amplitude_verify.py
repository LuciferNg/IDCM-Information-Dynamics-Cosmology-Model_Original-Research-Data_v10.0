#!/usr/bin/env python3
"""驗證冷斑振幅公式 + 座標轉換"""
import math
phi = (1+5**0.5)/2
phi_inv = 1/phi
eps = phi_inv/4
kappa = 1/16

print("=== 驗證 1: RMS = ε⁵·κ/2 ===")
rms_pred = eps**5 * kappa / 2
print(f"ε⁵·κ/2 = {rms_pred:.6e}")
print(f"Planck RMS ≈ 1.1e-5, 偏差 = {abs(rms_pred-1.1e-5)/1.1e-5*100:.2f}%")
print()

print("=== 驗證 2: 冷斑 = 5×RMS ===")
cs_pred = 5 * rms_pred
cs_obs = 160e-6 / 2.7284
print(f"5×RMS = {cs_pred:.6e}")
print(f"冷斑(-160μK) = {cs_obs:.6e}, 偏差 = {abs(cs_pred-cs_obs)/cs_obs*100:.1f}%")
print()

print("=== 驗證 3: 冷斑直接結構公式 ===")
cands = {
    "ε⁴φ⁻²/4": eps**4*phi_inv**2/4,
    "κ²ε⁴": kappa**2*eps**4,
    "ε⁵×5×κ/2": eps**5*kappa/2*5,
    "κ⁴×2ε": kappa**4*2*eps,
    "ε⁴/φ²×κ": eps**4/phi**2*kappa,
    "2ε⁵/κ": 2*eps**5/kappa,
}
for name, val in cands.items():
    dev = abs(val-cs_obs)/cs_obs*100
    print(f"  {name:14s} = {val:.4e}  偏差 {dev:.2f}%")
print()

print("=== 驗證 4: 冷斑座標轉換 ===")
b = math.radians(-57)
l = math.radians(209)
eps_g = math.radians(62.87)
sin_delta = math.sin(b)*math.cos(eps_g) + math.cos(b)*math.sin(eps_g)*math.sin(l)
delta = math.degrees(math.asin(sin_delta))
cos_dec = math.cos(math.asin(sin_delta))
cos_alpha = (math.cos(b)*math.cos(l)) / cos_dec
sin_alpha = (math.cos(b)*math.sin(l)*math.cos(eps_g) - math.sin(b)*math.sin(eps_g)) / cos_dec
alpha = math.degrees(math.atan2(sin_alpha, cos_alpha))
if alpha < 0:
    alpha += 360
print(f"冷斑銀道 (209°, -57°) → 赤道: RA = {alpha:.2f}° ({alpha/15:.2f}h), Dec = {delta:.2f}°")
print(f"文獻: RA ≈ 3.53h = 52.9°, Dec ≈ -38.5° (需核對)")
print()
print("=== 驗證 5: 冷斑位置 60° 節點 ===")
# 冷斑應該靠近 dodecahedron 投影節點
# 如果節點網格 = 60° 間距, 冷斑同最近節點角度應該 < 5°
# 之前算: 最近頂點 24.26°, 最近面中心 31.54°
# 呢啲太大 — 需要諗下係咪用錯參考系
print("之前: 最近 dodecahedron 頂點 24.26°, 面中心 31.54°")
print("❌ 太大 — 冷斑唔係直接對準 dodecahedron 頂點/面中心")
print("可能: 冷斑 = 節點網格嘅邊界交匯 (edge crossing)")
print("或: 需要考慮銀道座標 → 某種投影")
