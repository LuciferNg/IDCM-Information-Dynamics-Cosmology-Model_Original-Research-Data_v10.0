# O173 — 觀測約束 (Observational Constraints)

> 數據先行 (O163 紀律): 開題第一件事 = 觀測約束表, 先至開始推導。
> 全部錨點來自 crystal_stress 已驗證記錄 (45/45 PASS, 2026-09-09)。

## C1-C10 約束表

| # | 量 | 值 | 來源 |
|:-:|:---|:---|:-----|
| C1 | COSMOS-Web LRD 數 | 434 (0.54 deg², 單節點 8) | Akins+2024; crystal_stress record 05 |
| C2 | LRD 中位質量 M_obs (λ=10% 假設) | 6.97e6 M☉ | record 11/12 (ratio 0.9994) |
| C3 | LRD z 範圍 | z ≈ 2–9 (峰值 z≈6–6.5) | record 05 (N(z) 峰值) |
| C4 | 本地 LRD | DESI 27 @ z=0.2–0.9; Lin+2025 3 @ z=0.1–0.2 | record 07 ((LRDs)² Paper II, arXiv:2605.21574; arXiv:2507.10659) |
| C5 | LRD 數密度律 | N(z) ∝ 1/(1+z) (EIGER 校準 @ z=2.2) | record 05/07 |
| C6 | 凝聚效率 | η = φ⁻²¹ = 4.09e-5 | record 04/07 (F₈ 階梯) |
| C7 | E_strain 池 | 1.565e12 M☉ = (π²/75)·M_Pl·(R_H/L_P)·44⁻⁶ (dev 0.0045%) | record 07/13 (75 = L₄L₅−μ²) |
| C8 | LRD 輻射率 | 1.54 M☉/yr/核 (= Lbol/(0.1c²), Lbol = 9.91·L_Edd) | 09-11 LRD 本體論討論; script 01 C3 重現 |
| C9 | UHECR 天花板 | E_GZK = hc/(L_P·φ⁴⁴) = 4.891e19 eV; 冇事件 > 316.6 EeV | crystal_stress 04 (2.18%) |
| C10 | 守恆量 | 離散 Noether Q = 44 = N_d; μ² = E−O = γ₄₄ = 2 | O161 (94/94), O159 (92/92) |

## 結構錨點 (已閉合, 唔重推)

| 量 | 值 | 閉合 O |
|:---|:---|:-------|
| T_ring (SYNC) | 84.6349 Gyr | O39/O51 |
| τ (渲染深度) | 13.4701 Gyr | O51 |
| t_true | 11,100.64 Gyr = 131·T_ring + τ | O51 |
| T_beat (拓撲拍頻) | 45,963 Gyr = 3330× 宇宙年齡 | crystal_stress record 04 |
| 凝聚穩定 | V''(⟨W⟩) = 8 > 0 → 冇熱寂 | O39 (110/110) |
| RG 不變量 | 21 × 176/42 = 88 = 2N_d | O159 系 (record 11) |
| 合併時鐘 | K_Chain 模式共振 n=7/8/15, p≈2.8e-4 | O60 |
| 節點 8 參數 | S(8) = 0.0470485, f(4) = 0.6364, M_base = 1.914e6 M☉ | record 07 |

## 誠實標記

- C8 嘅「1.54 M☉/yr」嚟自 09-11 討論 (λ_Edd = 9.91 × L_Edd/(0.1c²)) — script 01 C3 用
  L_Edd = 1.26e38·M erg/s 重現 = 1.5366 M☉/yr (dev 0.2%).
- ⚠️ 交接文檔「凝聚時標 3.2e7 yr = 6.97e6/1.54」算術錯誤: 6.97e6/1.54 = 4.54 Myr.
  32 Myr 對應率 0.218 M☉/yr (觀測平均形成率). 本 O 統一用觀測平均率 0.218 M☉/yr/節點
  做消耗率 (觀測直接, 無時標假設), 4.54 Myr 做單核凝聚時標 (輻射率定義).
