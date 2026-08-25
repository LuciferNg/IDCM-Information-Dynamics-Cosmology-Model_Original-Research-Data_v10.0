"""
O73 攻堅 16: θ* 機制深推 — D_A = 48×λ_sync? θ* = 1/96?
=================================================================
script 12 發現 D_A/R_world = 3.42906
script 13 發現 D_A = (24/7)R_world → θ* = 7π/2112 (0.014%)

新發現: D_A/λ_sync = 14159.8/294.88 = 48.02 ≈ 48!
  → D_A = 48 × λ_sync
  → θ* = r_s/D_A = (λ_sync/2)/(48λ_sync) = 1/96

96 有 44 系身份?
  96 = 88 + 8 = 2N_d + 2B (B=4)
  96 = 2×48 = 2×(44+4)
  96 = 44 + 44 + 4 + 4

θ* = 1/96 = 0.0104167 rad
Planck θ* = 0.0104110 → dev 0.055%

對比 θ* = 7π/2112 = 0.0104125 → dev 0.014% (更準)

兩個候選邊個啱?
"""
import mpmath as mp
mp.mp.dps = 40

R_world = mp.mpf('4129.94')
lam_sync = 2 * mp.pi * R_world / 88
r_s = lam_sync / 2
D_A_247 = mp.mpf(24)/7 * R_world
theta_planck = mp.mpf('1.04110e-2')
err_planck = mp.mpf('3.1e-7')

print("=" * 74)
print("1. D_A = 48×λ_sync 驗證")
print("=" * 74)
D_A_48 = 48 * lam_sync
D_A_obs = r_s / theta_planck
print(f"  λ_sync = {mp.nstr(lam_sync, 8)} Mpc")
print(f"  D_A_obs = r_s/θ* = {mp.nstr(D_A_obs, 8)} Mpc")
print(f"  D_A_48 = 48×λ_sync = {mp.nstr(D_A_48, 8)} Mpc")
print(f"  dev = {mp.nstr((D_A_48-D_A_obs)/D_A_obs*100, 6)}%")
print(f"  D_A/(48λ_sync) = {mp.nstr(D_A_obs/(48*lam_sync), 8)}")
print(f"  48 = ? 44+4 = N_d+B = 88/2+8/2? 4×12? 2×24?")
print()

print("=" * 74)
print("2. θ* = 1/96 vs θ* = 7π/2112 對決")
print("=" * 74)
theta_96 = mp.mpf(1)/96
theta_7pi = 7 * mp.pi / 2112
for name, val in [("θ* = 1/96", theta_96), ("θ* = 7π/2112", theta_7pi)]:
    dev = (val - theta_planck) / theta_planck * 100
    z = (val - theta_planck) / err_planck
    print(f"  {name:14s} = {mp.nstr(val, 10)}  dev {mp.nstr(dev, 6)}%  z={mp.nstr(z, 4)}σ")
print()

print("=" * 74)
print("3. 96 嘅結構身份 (44 系)")
print("=" * 74)
candidates = {
    "88+8 (2N_d+2B)": 88 + 8,
    "2×48 (2×(44+4))": 2 * 48,
    "4×24 (4×2BN_gen)": 4 * 24,
    "8×12 (8×su12)": 8 * 12,
    "32×3 (2B²×3)": 32 * 3,
    "44+52": 44 + 52,
    "90+6 (Σγ_even+6)": 90 + 6,
    "178-82": 178 - 82,
    "33×3-3": 33 * 3 - 3,
}
for name, val in candidates.items():
    print(f"  {name:24s} = {val}")
print()
print(f"  ★ 最自然: 96 = 2N_d + 2B = 88 + 8 (B=4)")
print(f"    → 2N_d = 對偶鏈維度, 2B = 雙分支數")
print(f"  ★ 或者: 96 = 8×12 = 2B × su(12) fundamental")
print(f"    12 = L₅+1 = B×N_gen (O59), 8 = 2B")
print(f"    → 96 = 2B × (B×N_gen) = 2B²N_gen = 32×3 = 2×16×3")
print(f"    2B² = 32 (GLSM 32 U(1), O62), ×3 = 世代數")
print(f"    → 96 = 32×3 = 2B²×N_gen ★★★ 呢個好靚!")
print()

print("=" * 74)
print("4. 96 = 2B²×N_gen 結構身份 (O62 連結)")
print("=" * 74)
B = mp.mpf(4)
N_gen = mp.mpf(3)
print(f"  96 = 2B²×N_gen = 2×16×3 = {mp.nstr(2*B**2*N_gen, 4)}")
print(f"  2B² = 32 = GLSM 32 U(1) (O62 三大目標②)")
print(f"  N_gen = 3 = 世代數 (O13, 27=3³)")
print()
print(f"  → θ* = 1/(2B²N_gen) = 1/96")
print(f"  → D_A = 2B²N_gen × λ_sync = 96λ_sync/2... 等等")
print(f"  D_A = 48λ_sync = (2B²N_gen/2)λ_sync = 16×3×λ_sync")
print(f"  48 = B²N_gen = 16×3 = 48! ★★★")
print(f"  → D_A = B²×N_gen × λ_sync = 16×3×294.88 = 14154.2 Mpc")
print(f"  → θ* = r_s/D_A = (λ_sync/2)/(B²N_gen λ_sync) = 1/(2B²N_gen) = 1/96")
print()

print("=" * 74)
print("5. 最終對決: 兩個候選嘅結構說服力")
print("=" * 74)
print("""
  候選 A: θ* = 7π/2112 = (π/88)(L₄/24)
    - 7 = L₄ (d→n=7), 24 = 2BN_gen
    - dev 0.014% (更準)
    - 但 π/88 係「半 site 角」— 點解聲學視界角 = 半 site 角 × 7/24?

  候選 B: θ* = 1/96 = 1/(2B²N_gen)
    - 96 = 2B²N_gen (2B² = GLSM 32 U(1), N_gen = 3)
    - dev 0.055% (稍差)
    - 但 96 身份更「結構」: GLSM 32 × 世代 3
    - 冇 π — 純整數! 更乾淨!

  ★ 關鍵判別: θ* = 1/96 係「純整數倒數」— 冇 π, 冇 fit
    同 r_s = λ_sync/2 結合: θ* = r_s/D_A → D_A = 96r_s = 48λ_sync
    D_A = 48λ_sync = B²N_gen × λ_sync ← 超乾淨!
""")
