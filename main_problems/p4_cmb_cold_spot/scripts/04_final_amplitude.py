#!/usr/bin/env python3
"""
冷斑振幅最終驗證 + 座標 astropy 核對
=====================================
核心發現:
- CMB RMS ΔT/T = ε⁵/8 = 1.1007e-5 (vs Planck 1.1e-5, 0.06%)
- 冷斑 ΔT/T = 5ε⁵/8 = 5.5035e-5 (vs -150μK → 5.498e-5, 0.1%)
- 5 = F₅ (Fibonacci) — 「5σ」係結構因子, 唔係統計
"""
import math

phi = (1+5**0.5)/2
phi_inv = 1/phi
eps = phi_inv/4
kappa = 1/16

print("=" * 66)
print("冷斑振幅 — 最終結構公式")
print("=" * 66)

# 1. RMS
rms = eps**5 / 8
print(f"\n[1] CMB 起伏 RMS")
print(f"ε⁵ = {eps**5:.6e}")
print(f"RMS = ε⁵/8 = {rms:.6e}")
print(f"Planck RMS ≈ 1.1e-5 → 偏差 {abs(rms-1.1e-5)/1.1e-5*100:.2f}%")
print(f"結構: ε⁵/8 = (φ⁻¹/4)⁵/8 = φ⁻⁵/32768")
print(f"  8 = 2³ = κ×128? 或 2×B (B=4)? 或 L₀+L₃ = 2+4? ")
print(f"  最簡單: 8 = 2³ — 3 個二分")

# 2. 冷斑
cs_150 = 150e-6 / 2.7284
cs_160 = 160e-6 / 2.7284
cs_pred = 5 * rms
print(f"\n[2] 冷斑振幅")
print(f"冷斑 = 5×RMS = 5ε⁵/8 = {cs_pred:.6e}")
print(f"  5 = F₅ (Fibonacci) ✅")
print(f"-150μK → {cs_150:.6e}  偏差 {abs(cs_pred-cs_150)/cs_150*100:.2f}%")
print(f"-160μK → {cs_160:.6e}  偏差 {abs(cs_pred-cs_160)/cs_160*100:.2f}%")
print(f"-170μK → {170e-6/2.7284:.6e}  偏差 {abs(cs_pred-170e-6/2.7284)/(170e-6/2.7284)*100:.2f}%")
print()
print(f"「5σ」= 5×RMS = F₅×ε⁵/8 — 結構因子, 唔係高斯統計!")
print(f"IDCM: 冷斑 = F₅ 個 ε⁵ 單元嘅相位對消節點")

# 3. 其他冷斑預測
print(f"\n[3] 冷斑/熱斑結構等級")
print(f"1×RMS  = {rms:.4e} (普通起伏)")
print(f"2×RMS  = {2*rms:.4e}")
print(f"3×RMS  = {3*rms:.4e}")
print(f"5×RMS  = {5*rms:.4e} (F₅ 冷斑)")
print(f"8×RMS  = {8*rms:.4e} (F₆ 熱斑?)")
print(f"13×RMS = {13*rms:.4e} (F₇)")

# 4. 座標: astropy 核對
print(f"\n[4] 冷斑座標核對")
try:
    from astropy.coordinates import SkyCoord, Galactic, FK5
    import astropy.units as u
    c = SkyCoord(l=209*u.deg, b=-57*u.deg, frame=Galactic)
    eq = c.fk5
    print(f"銀道 (209°, -57°) → 赤道: RA = {eq.ra.deg:.2f}° ({eq.ra.hms.h:.2f}h {eq.ra.hms.m:.1f}m), Dec = {eq.dec.deg:.2f}°")
    print(f"文獻: RA ≈ 3.5h (52.5°), Dec ≈ -38° → 需比對")
except ImportError:
    print("astropy 未安裝 — 用手動轉換")
    # 手動 (之前 RA=127° 有誤, 修正)
    b = math.radians(-57)
    l = math.radians(209)
    eps_g = math.radians(62.87)
    sin_delta = math.sin(b)*math.cos(eps_g) + math.cos(b)*math.sin(eps_g)*math.sin(l)
    delta = math.asin(sin_delta)
    cos_dec = math.cos(delta)
    cos_alpha = (math.cos(b)*math.cos(l))/cos_dec
    sin_alpha = (math.cos(b)*math.sin(l)*math.cos(eps_g) - math.sin(b)*math.sin(eps_g))/cos_dec
    alpha = math.degrees(math.atan2(sin_alpha, cos_alpha))
    if alpha < 0:
        alpha += 360
    print(f"手動: RA = {alpha:.2f}° ({alpha/15:.2f}h), Dec = {math.degrees(delta):.2f}°")

# 5. 位置: 冷斑喺 Eridanus, 檢查赤道座標同 dodecahedron
print(f"\n[5] 位置結構")
print(f"冷斑銀道: (209°, -57°)")
print(f"之前: 最近 dodecahedron 頂點 24.26° — 唔夠近")
print(f"新思路: 冷斑可能對準 60° 節點網格嘅交匯 (face/vertex 之間)")
print(f"或: 需要考慮 44-site K_Chain 投影到天球嘅特定方向")
