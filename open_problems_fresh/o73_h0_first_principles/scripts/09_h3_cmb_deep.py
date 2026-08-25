"""
O73 攻堅 09: H3 深攻 — CMB 67.36 嘅 IDCM 身份
=================================================================
問題: CMB (Planck) 量到 67.36, 距離階梯 73.04, IDCM ω_ring = 72.59
      O11 解釋咗距離階梯偏移 (κφ⁻¹ 家族), CMB 唔係!

洞察: CMB H₀ 唔係直接量度! 係 θ* (聲學視界角) + 模型反推:
  ΛCDM: θ* = r_s/D_A(z*), fit H₀
  → CMB 量到嘅「67.36」係 ΛCDM 模型嘅投影!

IDCM 冇膨脹 → CMB 嘅 θ* 喺 IDCM 有咩身份?

關鍵候選: r_s = λ_sync/2 (已證 dev 0.24%)
  r_s = λ_sync/2 = R_world·π/44 = 294.88/2 = 147.44 Mpc
  θ* = r_s/D_A(z*)

如果 D_A(z*) 喺 IDCM 有結構值 → θ* 可以預言!
"""
import mpmath as mp
mp.mp.dps = 40

phi = (1 + mp.sqrt(5)) / 2
c = mp.mpf('299792.458')
omega_ring = mp.mpf('72.59')
R_world = c / omega_ring

# 世界環幾何
L_ring = 2 * mp.pi * R_world
lam_sync = L_ring / 88
r_s = lam_sync / 2

print("=" * 74)
print("1. IDCM 聲學視界")
print("=" * 74)
print(f"  R_world = {mp.nstr(R_world, 10)} Mpc")
print(f"  L_ring = 2πR_world = {mp.nstr(L_ring, 10)} Mpc")
print(f"  λ_sync = L_ring/88 = {mp.nstr(lam_sync, 10)} Mpc")
print(f"  r_s = λ_sync/2 = {mp.nstr(r_s, 10)} Mpc (IDCM 聲學視界)")
print(f"  Planck r_s = 147.09 ± 0.26 Mpc → dev {mp.nstr((r_s-147.09)/147.09*100, 6)}%")

print()
print("=" * 74)
print("2. θ* 預言: θ* = r_s/D_A(z*)")
print("=" * 74)
theta_obs = mp.mpf('1.04110e-2')
print(f"  Planck θ* = {mp.nstr(theta_obs, 12)} rad")
print(f"  IDCM 需要 D_A(z*) = r_s/θ* = {mp.nstr(r_s/theta_obs, 10)} Mpc")
D_A_needed = r_s / theta_obs
print(f"  R_world = {mp.nstr(R_world, 10)} Mpc")
print(f"  D_A/R_world = {mp.nstr(D_A_needed/R_world, 8)}")
print()

# D_A/R_world = 3.4210 有冇結構?
ratio_DA = D_A_needed / R_world
print(f"  3.4210 嘅結構候選:")
candidates = {
    "φ²+φ+1": phi**2 + phi + 1,
    "2φ+1": 2*phi + 1,
    "φ³": phi**3,
    "1+2φ": 1 + 2*phi,
    "√(2π)+1": mp.sqrt(2*mp.pi) + 1,
    "π+0.28": mp.pi + mp.mpf('0.28'),
    "√(4φ+4)": mp.sqrt(4*phi + 4),
    "2√(φ+2)": 2*mp.sqrt(phi + 2),
    "3+φ⁻¹": 3 + phi**-1,
    "√(5φ)": mp.sqrt(5*phi),
    "4-2/3": mp.mpf(4) - mp.mpf(2)/3,
    "10/3+0.0877": mp.mpf(10)/3,
    "3.4210 直接": mp.mpf('3.4210'),
    "1+2.4210": mp.mpf('2.4210'),
}
for name, val in candidates.items():
    dev = (val - ratio_DA) / ratio_DA * 100
    print(f"    {name:16s} = {mp.nstr(val, 10)}  dev {mp.nstr(dev, 5)}%")

print()
print("=" * 74)
print("3. 反推: 如果 D_A(z*) 有結構值 → CMB 量到嘅 ω_ring")
print("=" * 74)
# ΛCDM 反推: H₀ 由 θ* 定 (假設 Ω 固定)
# 但 IDCM: θ* = r_s/D_A, r_s = λ_sync/2 = R_world·π/44
#         D_A(z*) = ? — 如果係 R_world×k (k 結構)
# 則: θ*_IDCM = (R_world·π/44)/(R_world·k) = π/(44k)
# CMB 反推: 67.36 = ω_ring × f
# 如果 f = θ*_IDCM/θ*_obs?

# 實際: CMB H₀ 係由 θ* 反推, θ*_obs 固定
# IDCM 聲稱 θ*_IDCM = π/(44k) — 要 match θ*_obs
# θ*_obs = 1.04110e-2
# π/(44k) = 1.04110e-2 → k = π/(44×1.04110e-2)
k_implied = mp.pi / (44 * theta_obs)
print(f"  如果 θ*_IDCM = π/(44k) 要 = θ*_obs:")
print(f"  k = π/(44×θ*) = {mp.nstr(k_implied, 10)}")
print(f"  k ≈ 3.43? 3.4291 = 2π/θ*·?")
print(f"  2π/θ* = {mp.nstr(2*mp.pi/theta_obs, 8)} (= 圓周/θ* = 603.5)")
print(f"  603.5/176 = {mp.nstr(2*mp.pi/theta_obs/176, 8)}")
print(f"  603.5/88 = {mp.nstr(2*mp.pi/theta_obs/88, 8)}")
print(f"  603.5/178 = {mp.nstr(2*mp.pi/theta_obs/178, 8)}")
print()

print("=" * 74)
print("4. 張力本質: CMB 67.36 vs ω_ring 72.59")
print("=" * 74)
ratio = mp.mpf('67.36') / omega_ring
print(f"  67.36/72.59 = {mp.nstr(ratio, 10)}")
print(f"  1 - ratio = {mp.nstr(1-ratio, 10)} = {mp.nstr((1-ratio)*100, 6)}%")
# 結構掃描: 1-ratio 有冇結構?
delta = 1 - ratio
print(f"  δ = {mp.nstr(delta, 10)}")
struct_candidates = {
    "1/14": mp.mpf(1)/14,
    "1/13.88": mp.mpf(1)/mp.mpf('13.88'),
    "1/√(194)": 1/mp.sqrt(194),
    "φ⁻⁴": phi**-4,
    "2/π²": 2/mp.pi**2,
    "1/2π²": 1/(2*mp.pi**2),
    "1/(44-2)": mp.mpf(1)/42,
    "1/88×6.34": mp.mpf(1)/88*mp.mpf('6.34'),
    "sin(π/44)/1.001": mp.sin(mp.pi/44)/mp.mpf('1.001'),
    "γ_20/6": mp.mpf('0.4288')/6,
    "γ_7": mp.mpf('0.06116'),
    "γ_7/0.849": mp.mpf('0.06116')/mp.mpf('0.849'),
}
for name, val in struct_candidates.items():
    dev = (val - delta) / delta * 100
    marker = " ★" if abs(dev) < 1 else ""
    print(f"    {name:20s} = {mp.nstr(val, 10)}  dev {mp.nstr(dev, 5)}%{marker}")

print()
print("=" * 74)
print("5. 更深: CMB 量嘅係「另一種頻率」?")
print("=" * 74)
print(f"  ω_ring = {mp.nstr(omega_ring, 8)} (km/s)/Mpc")
print(f"  ω_ring × cos(π/44)? = {mp.nstr(omega_ring*mp.cos(mp.pi/44), 8)}")
print(f"  ω_ring × cos(π/88)? = {mp.nstr(omega_ring*mp.cos(mp.pi/88), 8)}")
print(f"  ω_ring × sin(π/2-π/88)? = {mp.nstr(omega_ring*mp.sin(mp.pi/2-mp.pi/88), 8)}")
print(f"  ω_ring × (1-γ_20/2)? = {mp.nstr(omega_ring*(1-mp.mpf('0.4288')/2), 8)}")
print(f"  ω_ring × (1-γ_7/2)? = {mp.nstr(omega_ring*(1-mp.mpf('0.06116')/2), 8)}")
print(f"  ω_ring × (1-γ_22/2)? = {mp.nstr(omega_ring*(1-mp.mpf('0.5')/2), 8)} = 54.44")
print(f"  ω_ring × (1-γ_6/2)? = {mp.nstr(omega_ring*(1-mp.mpf('0.1819')/2), 8)} = 65.99")
print(f"  ω_ring × (1-γ_5/2)? = {mp.nstr(omega_ring*(1-mp.mpf('0.1259')/2), 8)} = 68.02")
print(f"  ω_ring × (1-γ_4/2)? = {mp.nstr(omega_ring*(1-mp.mpf('0.0817')/2), 8)} = 69.62")
print(f"  ω_ring × (1-γ_3/2)? = {mp.nstr(omega_ring*(1-mp.mpf('0.0458')/2), 8)} = 70.93")
print(f"  ω_ring × (1-γ_2/2)? = {mp.nstr(omega_ring*(1-mp.mpf('0.0203')/2), 8)} = 71.85")
print()
print("  CMB 67.36 落喺邊?")
print(f"  (1-γ_6/2)×ω_ring = {mp.nstr(omega_ring*(1-mp.mpf('0.1819')/2), 8)} (γ_6 = sin²(6π/88)×4)")
print(f"  67.36 目標: 偏差 {(mp.nstr(omega_ring*(1-mp.mpf('0.1819')/2)/mp.mpf('67.36')-1, 5))}")

print()
print("=" * 74)
print("H3 初步判決")
print("=" * 74)
print("""
  1. IDCM r_s = λ_sync/2 = 147.44 Mpc (dev 0.24% vs Planck)
  2. θ* 預言需要 D_A(z*) = 3.4210×R_world — 冇明顯結構
  3. CMB 67.36 候選機制: ω_ring × (1-γ_n/2)
     - γ_6: 65.99 (dev -2.0%)
     - γ_5: 68.02 (dev +1.0%)
     - γ_4: 69.62 (dev +3.4%)
     - 冇一個啱 67.36 到 <1%
  4. 張力可能係「CMB 聲學視界反推嘅模型依賴」:
     - ΛCDM fit θ* → H₀, 但 θ* 本身有 Ω 依賴
     - IDCM: θ* 冇直接 44 系結構
  5. 🔴 H3 未有閉合 — CMB 67.36 未有 IDCM 結構解釋
     → 保留為開放問題
""")
