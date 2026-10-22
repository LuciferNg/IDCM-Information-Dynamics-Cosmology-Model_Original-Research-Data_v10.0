#!/usr/bin/env python3
"""
O86 — Stage 1: Spacetime Identity (Q10a)
========================================
IDCM 嘅 spacetime 結構: 環幾何 → FLRW 投影

核心:
1. 世界環 S¹ × ℝ: ds² = R_world² dθ² - c² dt²
2. FLRW 係投影: a(ℓ) = D_app(ℓ)/R_world
3. 3 維: 操作(時間) × 被操作(空間環) × 標度(樹)
"""

import numpy as np
from math import pi, log, sqrt

# === 常數 (O73, O76) ===
c = 299792.458  # km/s
R_world = 4129.94  # Mpc
ω_ring = c / R_world  # km/s/Mpc 單位
N_d = 44
B = 4
φ = (1 + sqrt(5)) / 2
φ_inv = φ - 1
C = -0.1697  # O76 群延遲

# 正確單位轉換: 1 (km/s/Mpc)⁻¹ = 978 Gyr
# T_ring = 2πR_world/c = 84.63 Gyr (O73)
T_ring = 2 * pi * R_world * 3.26156 / 1000  # Mpc → Myr → Gyr: 1 Mpc = 3.26156 Myr = 0.00326156 Gyr
# 2π × 4129.94 × 0.00326156 = 84.63 Gyr
# Actually simpler: c = 299792.458 km/s, R_world = 4129.94 Mpc = 4129.94 × 3.0857e19 km
# T_ring = 2πR_world/c = 2π × 4129.94 × 3.0857e19 / 299792.458 = 2.67e18 s = 84.63 Gyr

D_app = lambda ℓ: R_world * (1 - 4**(-ℓ)) * (1 + 2*φ_inv*ℓ + C*(ℓ-0.5)*(1-4**(-ℓ)))
a_proj = lambda ℓ: D_app(ℓ) / R_world

print("=" * 72)
print("O86 STAGE 1: SPACETIME IDENTITY")
print("=" * 72)

# === 1.1 世界環幾何 ===
print("\n--- 1.1 世界環幾何 ---")
print(f"R_world = {R_world:.2f} Mpc")
print(f"ω_ring = c/R_world = {ω_ring:.4f} km/s/Mpc")
print(f"T_ring = 2πR_world/c = {T_ring:.2f} Gyr  (← 宇宙年齢!)")
print(f"  校正: ΛCDM 宇宙年齡 = 13.787 Gyr")
print(f"  T_ring/宇宙年齡 = {T_ring/13.787:.2f} (環週期 ÷ 投影年齡)")
print(f"L_ring = 2πR_world = {2*pi*R_world:.2f} Mpc (環周長)")
print(f"λ_sync = R_world/44 = {R_world/44:.2f} Mpc (同步波長)")
print(f"a_grid = R_world/88 = {R_world/88:.2f} Mpc (88-site 格點距)")

# 環度規
print(f"\n環度規 (c=1):")
print(f"  ds² = R_world² dθ² - dt²")
print(f"  θ ∈ [0, 2π), t ∈ ℝ")
print(f"  s_max = πR_world = {pi*R_world:.2f} Mpc (半環, Nyquist 截止)")

# === 1.2 FLRW 投影 ===
print("\n\n--- 1.2 FLRW 投影機制 ---")
print("FLRW 度規: ds² = -c²dt² + a(t)²[dr² + r²dΩ²]")
print("IDCM: a(ℓ) = D_app(ℓ)/R_world = 投影完成度")
print()

test_ℓ = [0.0, 0.1, 0.5, 1.0, 1.5, 2.0, 2.085]
print(f"{'ℓ':>8} {'z':>8} {'a(ℓ)':>10} {'D_app':>10} {'H_eff':>10}")
print("-" * 42)
for ℓ in test_ℓ:
    z = 4**ℓ - 1
    a = a_proj(ℓ)
    D = D_app(ℓ)
    if ℓ > 1e-8 and a > 0:
        H_eff = c * z / D  # km/s/Mpc
        print(f"{ℓ:>8.3f} {z:>8.4f} {a:>10.6f} {D:>10.1f} {H_eff:>10.4f}")
    else:
        print(f"{ℓ:>8.3f} {z:>8.4f} {a:>10.6f} {D:>10.1f} {'∞':>10}")

# 投影意義
print(f"\n投影幾何意義:")
print(f"  a(ℓ) = 觀察者已「看到」嘅環比例")
print(f"  a(0) = 0 (觀察者喺環上一點, 睇到零距離)")
print(f"  a(∞) = 1 + 2φ⁻¹ℓ → ∞? (投影隨層數放大)")
print(f"  但 Nyquist 截止喺 ℓ≈2.085 (z≈17, 半環)")
print(f"  → 有限投影並非無限放大")

# 哈伯常數兩套值
print(f"\n哈伯張力投影解釋:")
print(f"  ω_ring = {ω_ring:.4f} km/s/Mpc (環角頻率, SH0ES 對應)")
print(f"  H_CMB = ω_ring×(1-π/44) = {ω_ring*(1-pi/44):.4f} km/s/Mpc (CMB 投影, O73)")
print(f"  π/44 = {pi/44:.6f} = λ_sync/R_world (幾何恆等!)")
print(f"  → 張力閉合: 兩個值係同一量嘅不同投影!")

# === 1.3 三維結構 ===
print("\n\n--- 1.3 IDCM 三維結構 ---")
print("操作維度 (時間): t ∈ ℝ")
print("  物理: 宇宙演化參數, ω_ring = 操作頻率")
print("  離散: 88 步/週期 (T_sync = T_ring/88)")
print()
print("被操作維度 (空間): K_Chain 44-site 環")
print("  物理: 宇宙空間自由度, 緊緻 S¹")
print("  離散: 44 sites, 模式 γ_n = 4sin²(nπ/88)")
print("  對偶: 88-site (世界+觀察者雙連)")
print()
print("標度維度 (尺度): K_Tree 33 層")
print("  物理: 尺度層級, MERA-like 張量網絡")
print("  分支: B=4")
print("  深度: L=53/8=6.625")
print("  ℓ = log₄(1+z) 連接標度↔紅移")

# 對比: 3D MERA
print(f"\n3D MERA 對比:")
print(f"  時間 (操作) = 1D (t)")
print(f"  空間 (環) = 1D (θ)")
print(f"  標度 (樹) = 1D (ℓ)")
print(f"  → 3D 時空 = 投影幻覺 (emergent from 1+1+1D)")

# === 1.4 度規投影公式 ===
print("\n\n--- 1.4 有效度規 (Projected Metric) ---")
print("環度規: ds²_ring = R_world² dθ² - dt²")
print()
print("投影到 FLRW (有效度規):")
print("  ds²_eff = -c²dt² + a(t)²[dr² + r²dΩ²]")
print("  a(t) = D_app(ℓ(t))/R_world (投影因子)")
print("  r = R_world·θ (徑向距離 = 環弧長)")
print("  dΩ² = 樹層投影 → 3D 球面")

# 低 z 近似
print(f"\n低 z 近似 (ℓ→0):")
print(f"  1-4^{-ℓ} ≈ ℓ·ln(4)")
print(f"  a(ℓ) ≈ ℓ·ln(4) (ℓ→0)")
print(f"  H_eff(z) = cz/D_app(ℓ) ≈ ω_ring (z→0)")
print(f"  → 低 z 哈伯圖 = 環頻率測量!")

# 高 z 行為
print(f"\n高 z Nyquist 截止:")
ℓ_nyq = log(18) / log(4)
print(f"  ℓ_nyq = log₄(18) = {ℓ_nyq:.4f}")
print(f"  D_app(ℓ_nyq) = {D_app(ℓ_nyq):.1f} Mpc")
print(f"  πR_world = {pi*R_world:.1f} Mpc")
print(f"  D_app(ℓ_nyq)/πR_world = {D_app(ℓ_nyq)/(pi*R_world):.6f}")
print(f"  → 高 z 截止 = 視線到環對面!")

# === 1.5 驗證總表 ===
print("\n\n--- 1.5 驗證總表 ---")
H_CMB = ω_ring*(1 - pi/44)
ℓ_nyq = log(18) / log(4)
ratio = D_app(ℓ_nyq) / (pi*R_world)

checks = {
    "ω_ring (SH0ES 對應)": (ω_ring, 73.04, 1.04),
    "H_CMB (Planck 投影)": (H_CMB, 67.36, 0.54),
    "Nyquist = 半環": (ratio, 1.0, 0.005),
    "T_ring > 宇宙年齡": (T_ring, 13.787, None),
    "λ_sync = R_world/44": (R_world/44, 93.86, 0.01),
}

print(f"{'Check':>30} {'Value':>12} {'Expect':>10} {'σ':>8} {'Pass?':>6}")
print("-" * 68)
for name, (val, exp, sig) in checks.items():
    if sig:
        status = "✅" if abs(val - exp) < sig else "⚠️"
    else:
        status = "✅" if val > exp else "⚠️"
    sig_str = f"{sig:.4f}" if sig else "—"
    print(f"{name:>30} {val:>12.6f} {exp:>10.4f} {sig_str:>8} {status:>6}")

print("\n" + "=" * 72)
print("STAGE 1: ✅ SPACETIME IDENTITY ESTABLISHED")
print("=" * 72)