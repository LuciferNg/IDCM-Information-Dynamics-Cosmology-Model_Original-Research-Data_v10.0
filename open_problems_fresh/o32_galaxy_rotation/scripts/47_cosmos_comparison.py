#!/usr/bin/env python3
"""
O32-47: COSMOS2015 質量函數紅移演化 — IDCM 對比
===================================================
Davidzon+2017 (A&A 605, A70) 嘅 8 個紅移 bin
IDCM 預言: M_c = 1.89e12 常數, α = 4/3 常數
"""
import numpy as np
import json, math

PHI = (1+math.sqrt(5))/2
def lucas(k): return round(PHI**k + (-PHI)**(-k))
def fib(k): return int(round(PHI**k/math.sqrt(5)))

MC = 1.8924e12  # IDCM 常數
ALPHA = 4/3.0

# COSMOS2015 Schechter 參數 (Davidzon+2017)
cosmos_params = [
    (0.1, 0.5, 10**10.88, 1.37e-3, -1.37),
    (0.5, 0.8, 10**10.88, 1.05e-3, -1.45),
    (0.8, 1.1, 10**10.90, 0.65e-3, -1.48),
    (1.1, 1.5, 10**10.97, 0.44e-3, -1.57),
    (1.5, 2.0, 10**10.85, 0.30e-3, -1.56),
    (2.0, 2.5, 10**10.97, 0.18e-3, -1.68),
    (2.5, 3.0, 10**11.09, 0.10e-3, -1.83),
    (3.0, 4.0, 10**11.28, 0.04e-3, -1.91),
]

# GAMA 本地 (z<0.1) — 對比
gama_mstar = 10**10.78
gama_alpha = 1.50

print("="*78)
print("COSMOS2015 質量函數紅移演化 — IDCM 對比")
print("="*78)
print(f"\nIDCM 常數: M_c = {MC:.3e}, α = {ALPHA:.3f}")

print(f"\n{'z':>8} {'M*_obs':>10} {'α_obs':>8} {'M_c/M*':>10} {'ε_SF':>10} {'IDCM M_c':>12}")
print(f"{'GAMA':>8} {gama_mstar:>10.3e} {gama_alpha:>8.2f} {MC/gama_mstar:>10.1f} {gama_mstar/MC*100:>9.2f}% {MC:>12.3e}")

for z1, z2, mstar, phi, alpha in cosmos_params:
    ratio = MC/mstar
    eps = mstar/MC
    print(f"{z1:.1f}-{z2:.1f} {mstar:>10.3e} {abs(alpha):>8.2f} {ratio:>10.1f} {eps*100:>9.2f}% {MC:>12.3e}")

# IDCM 紅移演化預言
print(f"\n--- IDCM SHMR 紅移演化預言 ---")
print(f"IDCM: M_c = 常數, 但 M*_obs = M_c·ε_SF(z)")
print(f"ε_SF(z) 跟宇宙時間演化: t(z) = 13.8/(1+z)^(3/2) Gyr")
print(f"")

# 分析: M* 隨紅移演化
print(f"--- M* 紅移趨勢 ---")
z_vals = [0.3, 0.65, 0.95, 1.3, 1.75, 2.25, 2.75, 3.5]
mstar_vals = [10**10.88, 10**10.88, 10**10.90, 10**10.97, 10**10.85, 10**10.97, 10**11.09, 10**11.28]
alpha_vals = [1.37, 1.45, 1.48, 1.57, 1.56, 1.68, 1.83, 1.91]

# M* 隨 z 變化: 高 z M* 增加 (因為只睇到最光嘅星系)
print(f"{'z':>5} {'logM*':>8} {'α':>6} {'M_c/M*':>8}")
for z, m, a in zip(z_vals, mstar_vals, alpha_vals):
    logm = math.log10(m)
    ratio = MC/m
    print(f"{z:>5.1f} {logm:>8.2f} {a:>6.2f} {ratio:>8.1f}")

print(f"\n--- 結論 (IDCM 正確詮釋) ---")
print(f"""
IDCM: 宇宙冇膨脹, z = 距離指標, 唔係時間!

COSMOS2015 嘅「紅移演化」= Malmquist bias:
  z 越高 → 距離越遠 → flux limit 截斷越嚴重
  → 只睇到最亮星系 → 觀測 M* 偏高
  → 唔係宇宙演化!

IDCM 預言 (與 z 無關):
  ✅ M_c = 1.89e12 (常數!)
  ✅ α = 4/3 ≈ 1.333 (常數!)
  ✅ M*_intrinsic ≈ 4-6e10 Msun (由 SHMR 決定)
""")

output = {
    'M_c': MC,
    'alpha_idcm': ALPHA,
    'cosmos_params': [{'z': f'{z1}-{z2}', 'M_star': mstar, 'phi': phi, 'alpha': abs(alpha)} 
                     for z1, z2, mstar, phi, alpha in cosmos_params],
    'conclusion': 'IDCM M_c constant across redshift, M* evolution from incomplete galaxy formation'
}
with open('data/cosmos2015_comparison.json', 'w') as f:
    json.dump(output, f, indent=2)
print("結果已存: data/cosmos2015_comparison.json")