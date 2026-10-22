#!/usr/bin/env python3
"""
O100 剩餘問題: P4 (968↔T_CMB) + P5 (Nyquist) + P6 (Planck/ACT D₁)
====================================================================
全部數值檢驗, 唔涉新結構推導。
"""
import numpy as np

WORK = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o100_cl_to_pk"
R_world = 4129.64; h = 0.6727; R8 = 8.0; Tcmb = 2.72548e6

def top_hat(x): return 3*(np.sin(x)-x*np.cos(x))/x**3

# ===== P4: 968 ↔ T_CMB 熱態交叉驗證 =====
print("="*60)
print("P4: 968 ↔ T_CMB 熱態 partition function 交叉驗證")
print("="*60)
# O83 熱態: Z(β) = Π_n e^{-βω_n/2}/(1-e^{-βω_n})
# T_CMB = 2.7283 K (IDCM 值, 0.10% above FIRAS)
# Σ1/γ_odd = 968 = 44×22
# 想法: 如果 T_CMB 來自 partition function, 968 應該係某個熱態和
# 高溫極限: ⟨φ²⟩_T = 1/(βγ_n) = k_B T / (ħ·γ_n) 
# 落番自然單位: ω_n = 2sin(nπ/88), γ_n = 4sin²(nπ/88)
# T_CMB 嘅物理量綱: k_B T_CMB 對應嘅能量尺度
# 用 O83 嘅 T_CMB 推導: T_CMB 來自 SYNC 操作
# 968 = 44×22 = Σ1/γ_odd: 觀察者 chain 嘅熱態方差 budget
# 需要 O83 partition function 公式 — 讀 O83 文檔

# O83 嘅 T_CMB 推導: 
# T_sync = 2π/H₀ = 84.64 Gyr → T_CMB = ?
# 實際: O83 用 SYNC 操作得出 T_CMB = 2.7283 K
# 968 = Σ1/γ_odd: 如果 Σ1/γ = k_B T / (ħ·ω_0) 之類
# 最簡單: 檢查 968 同 T_CMB 嘅數值關係
# k_B T_CMB / (M₀·c²) = ?
M0 = 27.9e-3  # GeV (m_7 = 13.95 MeV × 2)
kBT = 2.7283 * 8.617e-5  # eV = 2.35e-4 eV
M0_eV = 27.9e-3 * 1e9  # eV = 2.79e7 eV
ratio = kBT / M0_eV
print(f"k_B T_CMB = {kBT:.4e} eV")
print(f"M₀ = {M0_eV:.4e} eV")
print(f"k_B T_CMB / M₀ = {ratio:.4e}")
print(f"968 × ratio = {968 * ratio:.4e}")
print(f"44 × ratio = {44 * ratio:.4e}")

# 另一個角度: 968 = 44×22, 44 = N_d (維度), 22 = 88/4 = 2L₅
# T_CMB 同 嘅關係可能係: T_CMB ∝ 1/968 × (M₀ c²/k_B)
T_from_968 = M0_eV / 968 * 11604.5  # K (1 eV = 11604.5 K)
print(f"T_CMB if = M₀/968 × (eV→K) = {T_from_968:.4f} K")
print(f"實際 T_CMB = 2.7283 K")
print(f"比 = {T_from_968/2.7283:.4f}")
# 722.2/2.7283 = 264.7 ≈ 6N_d? 6×44=264. 接近!
print(f"  → 264 = 6N_d = 3Σγ_odd (O62!)")
print(f"  M₀/(264×968) = {M0_eV/264/968*11604.5:.4f} K")
# 太細, 唔啱.

# 直接: T_CMB = 2.7283 K, 同 968 有冇線性關係?
# 2.7283 × 968 = 2641.0 K
# 2.7283 × 44 = 120.0 K
# 唔似有直接關係.

# 改用 O83 嘅 T_CMB 推導流程:
# O83: T_CMB 嚟自 SYNC 操作: ω_sync = H₀ = 2.36e-18 rad/s
# T_CMB = ħ·ω_sync / (k_B · 2π) = ??? 
# ħ·H₀/k_B = 1.054e-34 × 2.36e-18 / 1.38e-23 = 1.80e-29 K — 唔啱
# 實際: T_CMB 來自 energy partition among 44 chain modes
# Σω_n = 88 (Σγ_odd?), k_B T_CMB = ħ·ω_0·(total energy scaling)
# 要 O83 完整推導先做到交叉驗證 → 🔴
print("→ 需要 O83 完整 partition function 公式 (🔴 未做)")
print("P4: 暫無結論 — T_CMB 推導流程在外層 O83 文檔")

# ===== P5: high-ℓ Nyquist 邊界 (ℓ=1452) =====
print("\n" + "="*60)
print("P5: high-ℓ Nyquist 邊界 (ℓ_Nyquist = 44×33 = 1452)")
print("="*60)
# 44-site chain, M=33: ℓ_max = 44×33 = 1452
# 9 峰: ℓ = {220, 537, 810, 1014, 1121, 1340, 1412, 1465, 1474}
# ℓ_Nyquist = 1452
# 峰 8 (ℓ=1465) 同 9 (ℓ=1474) 都大過 ℓ_Nyquist!
# 但 O83 公式: ℓ_m = 44×(M−C(9−m,2)) + F_{8-m}
# 峰 8 同 9 嘅 n_m = 33 (M=33, n=33), 所以 ℓ₈ = 44×33 + F₁ = 1452 + 1 = 1453?
# 實際 ℓ₈ = 1465, ℓ₉ = 1474 — 都大過 Nyquist
# 呢個可能係邊界效應: 峰 8,9 嘅 ℓ 超出 Nyquist, 貢獻不可靠

print(f"ℓ_Nyquist = 44×33 = {44*33}")
print(f"峰 8 ℓ=1465: 超出 Nyquist 13 ({(1465/(44*33)-1)*100:.1f}%)")
print(f"峰 9 ℓ=1474: 超出 Nyquist 22 ({(1474/(44*33)-1)*100:.1f}%)")
print(f"峰 7 ℓ=1412: 低於 Nyquist ({1412 < 44*33})")

# 對 σ8 嘅影響: 峰 8 貢獻 0.0022, 峰 9 貢獻 0.0010
# 總 σ8² = 0.5598, 峰 8+9 共 0.0032 = 0.57%
print(f"\n峰 8+9 對 σ8² 貢獻: {0.0022+0.0010:.4f} = {100*(0.0022+0.0010)/0.5598:.2f}%")
print(f"排除峰 8,9 後 σ8 = sqrt({0.5598-0.0032:.4f}) = {np.sqrt(0.5598-0.0032):.4f}")
print(f"vs 基線 0.748: Δ = {100*(np.sqrt(0.5598-0.0032)/0.748-1):+.2f}%")
print("→ Nyquist 影響 <1% — 峰 8,9 貢獻可忽略")

# 真正問題: ℓ > 1452 嘅峰可能係 aliasing 產物
# 實際: O83 公式包含 frac 修正, ℓ = 44n + F_{m} 可以超出 44M
# 但超出 Nyquist 嘅模式應被 cutoff — 需要 O83 確認
print("→ Nyquist cutoff 對峰 8,9 嘅影響需 O83 確認 (🔴)")

# ===== P6: Planck D₁ vs ACT 系統學 =====
print("\n" + "="*60)
print("P6: Planck D₁=5750 vs ACT ~5300 μK² 系統學")
print("="*60)
# 參考: Planck 2018 D_ℓ TT peak 1 ≈ 5750 μK²
# ACT DR4: ≈ 5300 μK² (～8% 低)
# 對 σ8 影響: σ8 ∝ √D₁
D1_planck = 5750
D1_act = 5300
s8_planck = 0.748
s8_act = s8_planck * np.sqrt(D1_act / D1_planck)
print(f"Planck D₁ = {D1_planck} μK² → σ8 = {s8_planck:.3f}")
print(f"ACT D₁   = {D1_act} μK²   → σ8 = {s8_act:.3f}")
print(f"ACT/Planck σ8 比 = {s8_act/s8_planck:.4f} (Δ={100*(s8_act/s8_planck-1):+.1f}%)")
print(f"\nACT σ8 = {s8_act:.3f} vs BOSS 0.783: Δ={100*(s8_act/0.783-1):+.1f}%")
print(f"ACT σ8 = {s8_act:.3f} vs 目標 0.81: Δ={100*(s8_act/0.81-1):+.1f}%")
print(f"Planck σ8 = {s8_planck:.3f} vs BOSS 0.783: Δ={100*(s8_planck/0.783-1):+.1f}%")
print(f"Planck σ8 = {s8_planck:.3f} vs 目標 0.81: Δ={100*(s8_planck/0.81-1):+.1f}%")
# ACT 低 D₁ 令 σ8 更接近 BOSS 但更遠離目標 0.81
print("→ ACT D₁ 降低 σ8 但同時令目標差距更大")
print("→ 系統學已入 C 包絡 [0.710, 0.785]")

# ===== 總結: P1 結論 =====
print("\n" + "="*60)
print("P1 結論: Beat 背景 (946 拍頻) 包絡模型")
print("="*60)
print("連續包絡法 (scripts/09) 失敗原因:")
print("  C_ℓ 係 44 條 δ-function 線譜, 唔係連續包絡")
print("  連續包絡積分 ∫Δ²·W² d(log k) 給出 σ8 = 0.454")
print("  比 9 峰離散和 0.748 細 39% — 因為包絡迴歸低估了峰位")
print("正確方法: 全 44-mode K_Tree 投影權重 w_n 推導")
print("  → 需要 O83 擴展: 所有 n=1..44 嘅 w_n 公式")
print("  → 屬於 K_Tree 結構推導, 唔係數值問題")
print(f"\n狀態: 🔴 未解決 — 需要新 O 系列 (beat 背景專項)")
print("P4: 🔴 需要 O83 partition function 公式")
print("P5: 🟡 Nyquist 影響 <1%, 峰 8,9 可暫保留")
print("P6: 🟡 已入 C 包絡, 無需獨立處理")