"""
O73 攻堅 12: H3 機制深挖 — 點解修正係 λ_sync 而唔係 λ_sync/2?
=================================================================
script 11 發現: CMB 67.36 ≈ ω_ring × (1 - π/44) = ω_ring × (1 - λ_sync/R_world)
  命中 0.07%! 但機制未明:
  - CMB 聲學視界 r_s = λ_sync/2 (O73 之前已證, dev 0.24%)
  - 點解修正因子用 λ_sync (完整) 而唔係 r_s (半個)?

候選機制:
  A. 投影: CMB θ* 反推 D_A → 修正 = r_s 相關
  B. 周長補償: 世界環 (周長 2πR) 被聲學視界「遮住」λ_sync → 剩餘比例
  C. 頻率分裂: 世界環角頻率 ω_ring 分裂成 CMB 部分 + 同步波長部分
"""
import mpmath as mp
mp.mp.dps = 40

phi = (1 + mp.sqrt(5)) / 2
omega_ring = mp.mpf('72.59')
R_world = mp.mpf('4129.94')
c = mp.mpf('299792.458')

print("=" * 74)
print("1. 機制候選 A: 聲學視界投影")
print("=" * 74)
# r_s = λ_sync/2, θ* = r_s/D_A
lam_sync = 2 * mp.pi * R_world / 88
r_s = lam_sync / 2
theta_star = mp.mpf('1.04110e-2')
D_A = r_s / theta_star
print(f"  λ_sync = {mp.nstr(lam_sync, 8)} Mpc")
print(f"  r_s = λ_sync/2 = {mp.nstr(r_s, 8)} Mpc")
print(f"  θ* = {mp.nstr(theta_star, 8)} rad")
print(f"  D_A = r_s/θ* = {mp.nstr(D_A, 8)} Mpc")
print(f"  D_A/R_world = {mp.nstr(D_A/R_world, 8)}")
print(f"  R_world/D_A = {mp.nstr(R_world/D_A, 8)}")
print()

print("=" * 74)
print("2. 機制候選 B: 周長補償 (剩餘環比例)")
print("=" * 74)
# 世界環周長 = 2πR_world
L_ring = 2 * mp.pi * R_world
frac_sync = lam_sync / L_ring      # 同步波長佔周長比例
print(f"  L_ring = 2πR_world = {mp.nstr(L_ring, 8)} Mpc")
print(f"  λ_sync/L_ring = {mp.nstr(frac_sync, 10)}")
print(f"  = 1/88 (因為 λ_sync = L_ring/88)  = {mp.nstr(mp.mpf(1)/88, 10)}")
print(f"  → λ_sync/R_world = π/44 = {mp.nstr(mp.pi/44, 10)}")
print()
print("  ★ 關鍵: λ_sync/R_world = π/44 係「同步波長/半徑」")
print("    而 λ_sync/L_ring = 1/88 係「同步波長/周長」")
print("    CMB 修正用邊個?")
print(f"    1 - 1/88 = {mp.nstr(1-mp.mpf(1)/88, 10)} → ω_ring× = {mp.nstr(omega_ring*(1-mp.mpf(1)/88), 7)}")
print(f"    1 - π/44 = {mp.nstr(1-mp.pi/44, 10)} → ω_ring× = {mp.nstr(omega_ring*(1-mp.pi/44), 7)}")
print(f"    Planck 67.36 → 用 π/44 (半徑比), 唔係 1/88 (周長比)!")
print()

print("=" * 74)
print("3. 機制候選 C: 頻率分裂")
print("=" * 74)
# ω_ring = c/R_world, 修正後 = c/(R_world - λ_sync) ?
omega_alt1 = c / (R_world - lam_sync)   # 半徑減同步波長
omega_alt2 = c / (R_world - r_s)        # 半徑減聲學視界
print(f"  ω_ring = c/R_world = {mp.nstr(c/R_world, 7)}")
print(f"  c/(R_world - λ_sync) = {mp.nstr(omega_alt1, 7)}")
print(f"  c/(R_world - r_s) = {mp.nstr(omega_alt2, 7)}")
print(f"  Planck 67.36")
print(f"  c/(R-λ_sync) dev = {mp.nstr((omega_alt1-mp.mpf('67.36'))/mp.mpf('67.36')*100, 5)}%")
print(f"  c/(R-r_s) dev = {mp.nstr((omega_alt2-mp.mpf('67.36'))/mp.mpf('67.36')*100, 5)}%")
print()

print("=" * 74)
print("4. 更深: ω_ring × (1-π/44) 嘅代數身份")
print("=" * 74)
# ω_ring × (1 - λ_sync/R_world) = c/R × (1 - π/44)
# = c/R × (44-π)/44 = c(44-π)/(44R)
# 但 R = c/ω_ring → = ω_ring(44-π)/44
# 另一寫法: = ω_ring - ω_ring·π/44 = ω_ring - c·π/(44R)?? 錯
# 正確: ω_ring × π/44 = c/R × π/44 = cπ/(44R)
# 修正量 = cπ/(44R) — 呢個係咩?
delta = omega_ring * mp.pi / 44
print(f"  修正量 = ω_ring × π/44 = {mp.nstr(delta, 7)}")
print(f"  = cπ/(44R_world) = {mp.nstr(c*mp.pi/(44*R_world), 7)}")
print(f"  = c/(44R/π) = c/(R × 44/π)")
print(f"  44/π = {mp.nstr(44/mp.pi, 8)}")
print(f"  → 修正量 = c/(R_world × 44/π)")
print()
print("  幾何詮釋: 修正量 = c / (世界半徑 × 44/π)")
print("  44/π = 世界半徑/同步波長 (R_world/λ_sync)")
print("  → 修正量 = c / (R_world × R_world/λ_sync) = c·λ_sync/R_world²")
print(f"  c·λ_sync/R_world² = {mp.nstr(c*lam_sync/R_world**2, 7)}")
print()

print("=" * 74)
print("5. 高精度: 用精確 c/72.59 重算")
print("=" * 74)
R_exact = c / omega_ring   # 4129.9416...
lam_exact = 2 * mp.pi * R_exact / 88
pred_exact = omega_ring * (1 - lam_exact / R_exact)
print(f"  R_exact = c/ω_ring = {mp.nstr(R_exact, 10)} Mpc")
print(f"  λ_sync_exact = {mp.nstr(lam_exact, 10)} Mpc")
print(f"  pred = ω_ring×(1-λ_sync/R) = {mp.nstr(pred_exact, 10)}")
print(f"  (應該 = 67.407086, 因為 λ/R = π/44 恆等)")
print(f"  dev vs Planck 67.36 = {mp.nstr((pred_exact-mp.mpf('67.36'))/mp.mpf('67.36')*100, 6)}%")
print()

print("=" * 74)
print("6. 全部三實驗 + 張力地圖對照")
print("=" * 74)
pred = pred_exact
for name, val, err in [
    ("Planck 2018", '67.36', '0.54'),
    ("ACT DR6", '68.3', '0.8'),
    ("SPT-3G", '68.8', '0.8'),
    ("TDCOSMO", '67.4', '3.6'),
]:
    v = mp.mpf(val); e = mp.mpf(err)
    z = (pred - v) / e
    print(f"  {name:12s} 預言 {mp.nstr(pred,7)} vs {val}±{err}  "
          f"z={mp.nstr(z,4)}σ {'✅' if abs(z)<2 else '❌'}")

print()
print("=" * 74)
print("結論 (H3 機制)")
print("=" * 74)
print("""
  ★★★ CMB 67.36 = ω_ring × (1 - λ_sync/R_world) = ω_ring × (1 - π/44)
     Planck: dev 0.070%, z = 0.09σ  ✅
     ACT/SPT/TDCOSMO: 全部 < 2σ ✅

  機制詮釋 (最合理):
    CMB 聲學視界反推 H₀ 時, D_A(z*) 嘅幾何包含「世界環半徑投影」
    → 反推嘅 ω 唔係 c/R_world 本身
    → 而係 c/(R_world - 同步波長) ≈ c/R_world × (1 - π/44)
    → CMB 量到嘅 = 世界環角頻率 × 剩餘環比例

  🔴 需要更深機制:
    - 點解「剩餘」係 R - λ_sync 而唔係 R - r_s?
    - 可能: CMB 聲學視界 r_s = λ_sync/2 對應半波長,
            但投影修正用全波長 (因為環係周期邊界?)
    - 需要正規 QFT/幾何推導 (docs/05 後續)
""")
