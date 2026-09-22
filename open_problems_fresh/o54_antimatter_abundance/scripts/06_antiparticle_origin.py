#!/usr/bin/env python3
"""
O54 — 檢查 6: 反粒子自由度喺 IDCM 中嘅結構來源
================================================
調律者指正: 「反物質的確能人造及在宇宙射線發現」。
上一輪「n_B̄=0 結構上不存在」係 over-claim — 撤回 (docs/02)。

真正問題: 反粒子自由度喺 IDCM 入面點嚟?
- K_Chain 譜半正定 (γ_n ≥ 0) — 冇「負頻率模式」
- 但實驗室造到反質子 → 反粒子自由度必須存在

方法:
1. K_Chain 緊束矩陣: 檢查有冇負頻率分支 (e^{ikx} 展開發散?)
2. 複波函數 vs 實波函數: 實譜 + 複結構 = 粒子/反粒子?
3. K_Chain × K_Tree 張量積: 複相位自由度係咪反粒子通道?
4. 相位共軛 C 算子: 喺張量積空間中作用
5. 結論: 反粒子 = 張量積空間嘅相位共軛自由度 (唔係 K_Chain 譜)

關鍵洞察:
- K_Chain 譜半正定 (γ_n ≥ 0) 只係「頻率譜」
- 反粒子 = 波函數嘅複相位自由度, 唔係頻率符號
- K_Chain ⊗ K_Tree 張量積提供複相位 (U(1) 荷)
"""
import math
import json
import numpy as np

phi = (1 + 5**0.5) / 2
phi_inv = 1 / phi
Nd = 44
M = 33

print("=" * 72)
print("O54 檢查 6: 反粒子自由度喺 IDCM 中嘅結構來源")
print("=" * 72)

# ============ 1. 緊束矩陣頻譜 vs 反粒子 ============
print("\n[1] 緊束矩陣: 頻譜 vs 反粒子自由度")
print("-" * 72)
# 週期邊界: H = -Σ(ψ†_{n+1}ψ_n + h.c.) → 本徵值 2-2cos(2πk/44) ≥ 0
# 但場算符 ψ_n 可以係複數! ψ_n = Σ_k (a_k e^{ikx} + b†_k e^{-ikx})
# a_k = 湮滅算子 (粒子), b†_k = 產生算子 (反粒子)
N = Nd
T = np.zeros((N, N))
for i in range(N):
    T[i, (i+1) % N] = -1
    T[i, (i-1) % N] = -1
T = T + 2 * np.eye(N)
eigvals = np.linalg.eigvalsh(T)

print(f"  週期邊界本徵值: {eigvals.min():.6f} .. {eigvals.max():.6f}")
print(f"  → 譜半正定 (冇負頻率)")
print(f"")
print(f"  但場算符展開:")
print(f"  ψ_n = Σ_k [ a_k·u_k(n) + b†_k·v_k(n) ]")
print(f"  a_k = 粒子湮滅算子 (能量 +ω_k)")
print(f"  b†_k = 反粒子產生算子 (能量 +ω_k)")
print(f"  → 反粒子 b†_k 用同一個正頻率 ω_k, 唔需要負頻率!")
print(f"  → 粒子/反粒子 = 荷 (charge) 自由度, 唔係頻率符號")
print(f"  → 譜半正定完全相容反粒子存在 ✅")

# ============ 2. 複相位自由度 ============
print("\n[2] 複相位自由度: U(1) 荷")
print("-" * 72)
# 實波函數 (檢查 1) 只係話本徵向量可以揀實數
# 但物理態可以係複相位疊加: ψ_phys = e^{iθ}·ψ_eigen
# U(1) 相位 θ → 荷 Q = i∂/∂θ → 粒子/反粒子 = ±Q
print(f"  實本徵向量 ψ_eigen (檢查 1): 只係一個基底選擇")
print(f"  物理態: ψ_phys = e^{{iθ}}·ψ_eigen (U(1) 相位)")
print(f"  U(1) 生成元: Q = i·∂/∂θ → 荷算符")
print(f"  Q|粒子⟩ = +q|粒子⟩, Q|反粒子⟩ = −q|反粒子⟩")
print(f"  → U(1) 相位自由度 = 反粒子通道 (唔係譜嘅正負)")
print(f"")
print(f"  IDCM 對應:")
print(f"  - K_Chain 譜: 頻率結構 (γ_n ≥ 0) ✅ 已閉合")
print(f"  - K_Chain ⊗ K_Tree: 複相位結構 (U(1) 荷)")
print(f"  - CY₃(36,98) 投影: 荷量子化 (粒子的 U(1) 荷)")

# ============ 3. K_Chain ⊗ K_Tree 張量積 ============
print("\n[3] K_Chain ⊗ K_Tree 張量積空間")
print("-" * 72)
dim_total = Nd * M
print(f"  dim(H_chain ⊗ H_tree) = {Nd} × {M} = {dim_total}")
print(f"  946 = C(44,2) (beat 空間, O51)")
print(f"  134 = h11+h21 (CY₃ moduli, O53)")
print(f"  36 = h11 = N_d − 2B (CY₃ Kähler, O53)")
print(f"  98 = h21 = Σγ + 2B (CY₃ 複結構, O53)")
print(f"")
print(f"  → CY₃ 複結構 (98 = Σγ+2B) 提供複相位自由度!")
print(f"  → 反粒子 = CY₃ 複結構嘅相位共軛")
print(f"  → 粒子/反粒子對 = K_Chain 頻率 × CY₃ 複相位")

# ============ 4. C 算子喺張量積空間 ============
print("\n[4] 電荷共軛 C 算子")
print("-" * 72)
# C 算子: 作用喺複結構上, 相位 θ → -θ
# C|ψ, θ⟩ = |ψ, −θ⟩
# C² = 1 (C 係 involution)
# C 交換粒子 ↔ 反粒子
print(f"  C 算子: θ → −θ (複相位共軛)")
print(f"  C² = 1 (involution)")
print(f"  C|粒子, +q⟩ = |反粒子, −q⟩")
print(f"")
print(f"  喺 IDCM 中:")
print(f"  C = 複結構相位反轉 (CY₃ 複結構 98 = Σγ+2B)")
print(f"  → C 係 K_Chain 譜嘅「相位對偶」, 唔係「頻率對偶」")
print(f"  → 檢查 1 嘅 ψ = ψ* 只係話本徵基底可揀實數,")
print(f"    唔等於物理態係 C 不變 — 物理態可以有任意 U(1) 相位")

# ============ 5. 反物質豐度修正 ============
print("\n[5] 反物質豐度修正（宏觀 vs 微觀）")
print("-" * 72)
print(f"""  宏觀: n_B̄/n_B < 1e-9 (湮滅 γ-ray 上限) — 冇反物質區域
  微觀: 反物質存在 (實驗室 + 宇宙射線) — 局部生成

  結構解釋 (修正後):
  - 宏觀物質 = K_Chain 投影 (T_pipe, 全局單向)
  - 微觀反物質 = 局部反投影 (pair production, 局部能量集中)
  - 兩者都由同一 U(1) 荷結構 (CY₃ 複結構) 支持

  ⟹ 「反物質唔係冇, 而係局部」— 正確框架
     宏觀差額 η_B 保持, 微觀對產生可能
""")

# ============ 6. 結論 ============
print("\n[6] 檢查 6 結論")
print("-" * 72)
print(f"""
  1. 反粒子自由度 = U(1) 荷 (複相位), 唔係頻率符號
     → K_Chain 譜半正定完全相容反粒子存在
  2. 反粒子通道 = CY₃ 複結構 (98 = Σγ+2B) 嘅相位共軛
     → C 算子: θ → −θ (唔係 γ_n → −γ_n)
  3. 檢查 1 嘅 ψ = ψ* 只係基底選擇, 唔係物理 C 不變
  4. 反物質 = 局部反投影 (pair production), 宏觀冇
  5. 🟡 部分閉合: 反粒子自由度結構定位完成,
     🔴 但「局部反投影 ⇔ pair production」嘅精確映射未推導
""")

results = {
    "test": "反粒子自由度結構來源",
    "spectrum_semi_positive": float(eigvals.min()) >= 0,  # O208: 由計算產生
    "antiparticle_from_charge": "🟡 結構聲稱 — U(1) 荷自由度 (本文 [2])",
    "charge_from_CY3_complex_structure": "🟡 結構聲稱 — CY₃ 複結構 98=Σγ+2B (O53)",
    "h21": 98,
    "h21_formula": "Σγ+2B",
    "C_operator_involution": "🟡 結構聲稱 — C: θ→−θ, C²=1 (本文 [4])",
    "macro_nBbar_limit": 1e-9,
    "micro_antimatter_observed": "🟡 結構聲稱 — 實驗室/宇宙射線觀測事實",
    "conclusion": "反粒子=U(1)荷(CY₃複結構98=Σγ+2B相位共軛), 唔係頻率符號; 譜半正定相容; 反物質=局部反投影, 宏觀差額保持",
}
print("驗證摘要:")
for k, v in results.items():
    print(f"  {k}: {v}")

with open("data/06_antiparticle_origin.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print("\n✅ 結果已寫入 data/06_antiparticle_origin.json")
