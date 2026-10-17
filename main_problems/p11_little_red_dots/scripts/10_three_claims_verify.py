#!/usr/bin/env python3
"""
三個開放點第一性原理驗證
=========================
1. η = P_frust × φ⁻¹² 閉合檢查
2. Δω = 0.00368 拍頻 → τ₀ 映射 → 宇宙學可觀測性
3. Euclid hop=4 波節預測: C = 0.363 對比度 + 質量比
"""
import math

phi = (1 + 5**0.5)/2          # 1.618
phi_inv = 1/phi               # 0.618
M_sun = 1.989e30

print("="*72)
print("三個開放點驗證")
print("="*72)

# ============ 1. η 效率因子 ============
print("\n1. η 效率因子")
P_frust = 32/120
print(f"  P_frust = 32/120 = {P_frust:.6f}")

# 用戶提議: η = P_frust × φ⁻¹²
eta_prop = P_frust * phi_inv**12
print(f"  η = P_frust × φ⁻¹² = {P_frust:.4f} × {phi_inv**12:.6f} = {eta_prop:.4e}")
print(f"  12 階衰減: φ⁻¹² = {phi_inv**12:.6f}")

# 觀測 η (相對每節點配額)
M_0_total = 1.565e12  # M☉ (32 條阻挫邊總應變能)
M_per_node = M_0_total / 60
M_LRD = 1e6  # 典型 LRD
eta_obs = M_LRD / M_per_node
print(f"\n  觀測 η = M_LRD / (M_0/60) = {M_LRD:.0e} / {M_per_node:.2e} = {eta_obs:.3e}")
print(f"  用戶提議 η = {eta_prop:.3e} → ratio vs 觀測 = {eta_prop/eta_obs:.1f}×")

# 其他候選
print(f"\n  其他候選:")
cands = [
    ("φ⁻²¹ (F₈=21)", phi_inv**21),
    ("P_frust × φ⁻¹⁸", P_frust * phi_inv**18),
    ("P_frust × φ⁻¹⁵", P_frust * phi_inv**15),
    ("P_frust² × φ⁻¹²", P_frust**2 * phi_inv**12),
]
for name, val in cands:
    dev = abs(val/eta_obs - 1)*100
    print(f"    {name:<18} = {val:.4e}  (偏差 {dev:6.1f}%)")

# log_φ 分析
print(f"\n  log_φ 分析:")
print(f"    log_φ(1/η_obs) = {math.log(1/eta_obs)/math.log(phi):.3f}")
print(f"    log_φ(1/η_obs) - 21 = {math.log(1/eta_obs)/math.log(phi) - 21:.3f}")

# ============ 2. Δω 拍頻 ============
print("\n" + "="*72)
print("2. Δω = 0.00368 拍頻")
d_omega = 0.300169 - 0.296486
print(f"  Δω = {d_omega:.6f}")
T_beat = 2*math.pi/d_omega
print(f"  T_beat = 2π/Δω = {T_beat:.1f} 時間單位")

# τ₀ = T_sync/π?
T_sync = 84.64  # Gyr
tau_0 = T_sync/math.pi
print(f"  τ₀ = T_sync/π = {tau_0:.2f} Gyr")

T_beat_phys = T_beat * tau_0
print(f"  T_beat(物理) = {T_beat:.0f} × {tau_0:.2f} = {T_beat_phys:.0f} Gyr")
print(f"  宇宙年齡 13.8 Gyr → T_beat/宇宙年齡 = {T_beat_phys/13.8:.1f}×")

# 可觀測性: 喺 z=4-8 視窗 (宇宙年齡 1.2-1.6 Gyr) 內調製相位變化
t_z6 = 1.0  # Gyr (z~6 宇宙年齡)
phase_change = d_omega * (t_z6/tau_0) / 2
print(f"\n  可觀測性檢查 (z~6, t=1 Gyr):")
print(f"    調製相位 Δφ = Δω·t/2 = {d_omega:.6f} × {t_z6/tau_0:.4f}/2 = {phase_change:.2e} rad")
print(f"    cos 變化 = {1 - math.cos(phase_change):.2e} (完全不可觀測)")

# Δz ≈ 0.2 起伏需要幾大 Δω?
print(f"\n  要 Δz≈0.2 週期性起伏, 需要:")
# LRD 形成視窗 Δt ~ 0.4 Gyr (z 4-8), 一個完整週期要 2π 相位
d_omega_needed = 2*math.pi*2 / (0.4/tau_0)  # 兩個半週期喺視窗內
print(f"    Δω_needed = 4π/(Δt/τ₀) = {d_omega_needed:.4f}")
print(f"    實際 Δω = {d_omega:.4f} → 差 {d_omega_needed/d_omega:.0f}×")

# ============ 3. Euclid hop=4 預測 ============
print("\n" + "="*72)
print("3. Euclid hop=4 波節預測")
E = {0: 0.014819, 4: 0.006916, 8: 0.014819}
C_obs = (E[0] - E[4])/(E[0] + E[4])
print(f"  對比度 C = (E₀-E₄)/(E₀+E₄) = ({E[0]}-{E[4]})/({E[0]}+{E[4]}) = {C_obs:.4f}")
print(f"  用戶提議 C ≈ 0.363 → 偏差 {abs(C_obs-0.363)/0.363*100:.1f}%")

# 正確公式: E(hop) = E₀[1 + C·cos(π·hop/4)]
print(f"\n  公式驗證: E(hop) = E₀[1 + C·cos(π·hop/4)], C={C_obs:.4f}")
for h in [0, 1, 2, 3, 4, 5, 6, 7, 8]:
    E_pred = E[0]/(1+C_obs) * (1 + C_obs*math.cos(math.pi*h/4))
    print(f"    hop={h}: cos={math.cos(math.pi*h/4):+.3f} E_pred={E_pred:.6f}")

# 質量比
M_ratio = (1 - C_obs)/(1 + C_obs)
print(f"\n  質量比 M(hop=4)/M(hop=0) = (1-C)/(1+C) = {M_ratio:.4f}")
print(f"  → hop=4 比 hop=0/8 低 {(1-M_ratio)*100:.1f}%")
print(f"  用戶 claim: 低 53.3% → 偏差 {abs((1-M_ratio)*100-53.3)/53.3*100:.1f}%")
