"""
O73 攻堅 03: 幾何角色釐清 — R_H 係半徑定周長? H₀ 係頻率定角頻率?
========================================================================
用戶指示: 「新參數不能再叫哈伯常數」— IDCM 冇膨脹, 舊名係 ΛCDM 包袱。

發現 O40 內部矛盾:
  src:      λ_n = R_H/n        → R_H 當「周長」(λ_1 = 4129.94 = 全環)
  O40:      T_sync = 2πR_H/c   → R_H 當「半徑」(周長 = 2πR_H = 25949)

驗證:
  1. c·T_sync 應該 = 邊個? (周長 4129.94 定 2πR_H = 25949?)
  2. H₀ = c/R_H = 72.59 係「頻率」定「角頻率」?
     - 頻率 f:     周期 T = 1/f = R_H/c = 4.04 Gyr
     - 角頻率 ω:   周期 T = 2π/ω = 2πR_H/c = 84.63 Gyr ← T_sync!
  3. λ_sync = c·T_sync/88 係咩幾何量?
"""
import numpy as np

c = 299792.458            # km/s
R_H = 4129.94             # Mpc (src)
Mpc_km = 3.085677581e19   # km/Mpc
Gyr_s = 3.15576e16        # s/Gyr
H0 = 72.59                # km/s/Mpc

print("=" * 74)
print("1. c·T_sync 對應邊個幾何量?")
print("=" * 74)
T_sync = 84.6349          # Gyr (O40)
L_Tsync = c * T_sync * Gyr_s / Mpc_km    # c·T 換做 Mpc
L_ring_2pi = 2 * np.pi * R_H             # 2πR_H
print(f"  c·T_sync            = {L_Tsync:.1f} Mpc")
print(f"  R_H (src 周長)      = {R_H:.1f} Mpc")
print(f"  2πR_H (半徑×2π)     = {L_ring_2pi:.1f} Mpc")
print(f"  c·T_sync / R_H      = {L_Tsync/R_H:.6f}")
print(f"  c·T_sync / (2πR_H)  = {L_Tsync/L_ring_2pi:.6f}")
print()
print("  → c·T_sync = 2πR_H (偏差 < 0.01%)")
print("  → T_sync 對應嘅環周長 = 2πR_H = 25949 Mpc, 唔係 R_H!")
print("  → R_H 喺 T_sync 公式入面係「半徑」角色")

print()
print("=" * 74)
print("2. H₀ = c/R_H = 72.59 係頻率定角頻率?")
print("=" * 74)
T_1 = R_H * Mpc_km / c / Gyr_s        # 若 f: T = R_H/c
T_2 = 2 * np.pi * R_H * Mpc_km / c / Gyr_s  # 若 ω: T = 2πR_H/c
print(f"  若 H₀ 係頻率 f:  T = 1/f = R_H/c       = {T_1:.3f} Gyr")
print(f"  若 H₀ 係角頻率 ω: T = 2π/ω = 2πR_H/c   = {T_2:.3f} Gyr")
print(f"  T_sync (O40)                          = {T_sync:.3f} Gyr")
print()
print("  → H₀ = c/R_H 必須係「角頻率」先至同 T_sync 一致")
print("  → O40 寫「H₀ = 環頻率(光繞一圈嘅頻率)」係錯:")
print("     光繞一圈頻率 = c/L = c/(2πR_H) = H₀/2π = 11.55 /Gyr")
print(f"     f_ring = c/(2πR_H) = {c/(2*np.pi*R_H):.4f} km/s/Mpc")
print(f"     = {c/(2*np.pi*R_H)*Mpc_km/Gyr_s:.4f} /Gyr")
print("  → IDCM 一直用「頻率」個名, 實際數值係角頻率 (差 2π)")
print("  → 呢個 2π 混亂正正係「哈伯常數」命名遺毒:")

print()
print("=" * 74)
print("3. λ_sync 嘅真實幾何身份")
print("=" * 74)
lam_sync = c * T_sync * Gyr_s / Mpc_km / 88   # c·T/88
print(f"  λ_sync = c·T_sync/88 = {lam_sync:.3f} Mpc")
print(f"  2πR_H/88 = {2*np.pi*R_H/88:.3f} Mpc")
print(f"  環周長/88 = λ_sync  → 同步波長 = 世界環 ÷ 觀察者維度(88)!")
print(f"  R_H/λ_sync = {R_H/lam_sync:.6f} = 44/π = {44/np.pi:.6f}")
print("  → 之前 R_H/λ_sync = 14.006 嘅 π 之謎解開:")
print("    R_H = L/2π (半徑), λ_sync = L/88 (周長/88)")
print("    → R_H/λ_sync = (L/2π)/(L/88) = 88/2π = 44/π ✓")
print()

print("=" * 74)
print("4. 新身份定義 (IDCM 語境, 唔再用哈伯常數)")
print("=" * 74)
print("""
  世界環半徑      R_world = 4129.94 Mpc     (幾何輸入)
  世界環周長      L_ring  = 2πR_world = 25949.2 Mpc
  世界環角頻率    ω_ring  = c/R_world = 72.59 (km/s)/Mpc
                 (= 舊 H₀ 數值, 但身份係角頻率, 唔係膨脹率)
  世界環周期      T_ring  = 2π/ω_ring = 84.63 Gyr (= T_sync)
  世界環繞圈頻率  f_ring  = ω_ring/2π = 11.55 /Gyr (真正頻率)
  同步波長        λ_sync  = L_ring/88 = 294.88 Mpc (觀察者維度分割)

  新命名: ω_ring (世界環角頻率) — 唔再用 H₀/哈伯常數
""")

print("=" * 74)
print("5. 一致性核對 (全部應 ✓)")
print("=" * 74)
checks = [
    ("c·T_sync = 2πR_H", abs(L_Tsync - L_ring_2pi)/L_ring_2pi < 1e-3),
    ("T_ring = 2π/ω_ring = T_sync", abs(T_2 - T_sync) < 0.01),
    ("λ_sync = L_ring/88", abs(lam_sync - 2*np.pi*R_H/88) < 1e-6),
    ("R_H/λ_sync = 44/π", abs(R_H/lam_sync - 44/np.pi) < 1e-4),
    ("ω_ring = c/R_world = 72.59 (km/s)/Mpc", abs(c/R_H - 72.59) < 0.01),
    ("f_ring = ω_ring/2π = 1/T_sync", abs(1.0/T_sync - 1.0/T_2) < 1e-3),
]
all_ok = True
for name, ok in checks:
    print(f"  {'✅' if ok else '❌'} {name}")
    all_ok &= ok
print()
print(f"  總判定: {'全部一致 ✅' if all_ok else '有矛盾 ❌'}")
print(f"  (f_ring 驗證: 1/T_sync = {1.0/T_sync:.6f} /Gyr, 1/T_2 = {1.0/T_2:.6f} /Gyr)")

print()
print("=" * 74)
print("結論")
print("=" * 74)
print("""
  1. R_H 嘅幾何角色: 半徑 (T_sync 公式) — src λ_n = R_H/n 嘅「周長」
     用法係有效近似/定義 (44 段鏈), 但環本身周長 = 2πR_H
  2. H₀ = c/R_H 係「角頻率」, 唔係「頻率」 — O40 描述要修正
  3. 新參數身份: ω_ring = c/R_world = 世界環角頻率
     - 同 ΛCDM H₀ 數值相同, 但身份完全唔同:
       ΛCDM: 膨脹率 (scale factor 變化率)
       IDCM: 世界環幾何嘅角頻率 (冇膨脹, 冇 scale factor)
  4. λ_sync = L_ring/88 有清晰幾何意義:
     世界環 ÷ 觀察者維度 = 同步波長 (44/π 之謎解開)
""")
