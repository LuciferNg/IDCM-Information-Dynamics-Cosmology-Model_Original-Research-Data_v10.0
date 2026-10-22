#!/usr/bin/env python3
"""
O10 10: 偏差模式分析 — 尋找 P₁, P₂ 系統偏差嘅結構
================================================
觀察 (unlensed, IDCM 峰位):
  P₁ = 0.4519 vs 3ε = 0.4635 → -2.50%
  P₂ = 0.1809 vs 3ε·φ⁻² = 0.1771 → +2.15%
  P₃ = 0.1359 vs 3ε·2φ⁻⁴ = 0.1353 → +0.44%

偏差: (-2.5%, +2.2%, +0.4%) — 唔係隨機, 有模式!
假設: 峰高 = 3ε × F_m × φ^{-2(m-1)} × (1 + δ_m)
δ_m = ?

候選修正:
  1. δ_m ∝ 1/m (harmonic)?
  2. δ_m ∝ ε·(-1)^m (alternating)?
  3. δ_m ∝ cos(2πm/3)?
  4. δ_m 源自 peak position offset (IDCM ℓ vs 真實 ℓ)?
  5. δ_m 源自低 ℓ 抬升 (ℓ=220 受 ISW + 低 ℓ 影響)?
"""
import math

phi = (1 + 5**0.5) / 2
phi_inv = 1/phi
eps = phi_inv/4

# unlensed @ IDCM 峰位
P_obs = {1: 0.4519, 2: 0.1809, 3: 0.1359}
S_fib = {1: 1.0, 2: phi_inv**2, 3: 2*phi_inv**4}
P_th = {m: 3*eps*S_fib[m] for m in P_obs}

print("偏差分析:")
deltas = {}
for m in P_obs:
    deltas[m] = (P_obs[m] - P_th[m])/P_th[m]
    print(f"  δ_{m} = {deltas[m]*100:+.3f}%")

print()
print("候選: δ_m ∝ 1/m?")
for m in P_obs:
    print(f"  δ_{m}×m = {deltas[m]*m*100:+.3f}%")

print()
print("候選: δ_m ∝ ε·(-1)^m?")
for m in P_obs:
    print(f"  δ_{m}/ε = {deltas[m]/eps*100:+.2f}%  (ε×100={eps*100:.2f})")

print()
print("候選: δ_m 隨 ℓ 線性?")
# P_1 @ <ℓ>=674, P_2 @ <ℓ>=1106, P_3 @ <ℓ>=1376
ells = {1: 674, 2: 1106, 3: 1376}
for m in P_obs:
    print(f"  δ_{m}/(<ℓ>_m/1000) = {deltas[m]/(ells[m]/1000)*100:+.3f}%")

print()
print("候選: 峰位置偏移 (IDCM vs 自動峰)?")
print("  m=1: IDCM 220 vs auto 221 → +1 (0.45%)")
print("  m=2: IDCM 537 vs auto 536 → -1")
print("  m=3: IDCM 810 vs auto 814 → +4")
print("  m=4: IDCM 1014 vs auto 1129 → +115 (大偏移!)")
print("  m=5: IDCM 1199 vs auto 1129 → -70")
print("  m=6: IDCM 1340 vs auto 1427 → +87")
print("  m=7: IDCM 1412 vs auto 1427 → +15")
print()
print("⚠️ 高 ℓ (m≥4) 峰位偏移大 — 呢個影響 A_m 讀數!")
print("  如果 m=4 真峰喺 1129 (唔係 1014), A₄ 讀數會錯")
print("  如果 m=5 真峰喺 1129 (唔係 1199), A₅ 讀數會錯")
print("  → P₂ (m=4,5) 嘅 +2.2% 偏差可能係峰位錯配!")
print()

# 用自動峰重算 P_2
print("用 CAMB 自動峰 (1129) 重算:")
# auto peaks: 221(773), 536(351), 814(348), 1129(170), 1427(114)
# P_1 = (351+348)/2/773 = 0.4521
# P_2 = (170 + ?)/2/773 — 只有 1129 一個峰
# CAMB 自動峰 5 = 1427 (IDCM m=7 附近, 唔係 m=5)
print("  CAMB auto: 221, 536, 814, 1129, 1427")
print("  → 只有 4 個可配對: (536,814) = P_1")
print("  → 1129 同 1427 之間冇峰 (CAMB 結構)")
print()
print("結論: CAMB unlensed 高 ℓ 峰結構 (1129, 1427) 同 IDCM (1014, 1199, 1340, 1412) 分歧")
print("  P₂, P₃ 嘅讀數受峰位分歧影響 — 需要用 Planck binned 驗證")
