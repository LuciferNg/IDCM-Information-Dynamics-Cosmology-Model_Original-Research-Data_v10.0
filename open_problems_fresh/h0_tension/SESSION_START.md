# h0_tension — SESSION START (O169 修正交回專用, 2026-09-15 建立)

> ⚠️ **本檔由 O169 修正交回程序建立** — 目的係承載「O169 上游修正 → 本 O 重新驗證/重新推導」任務。
> 本 O 原有狀態與結論 (01_problem_record.md / docs/ / final_result.md) **未經改動**。
> **本 O 定位**: 舊目錄 (無 O 編號) — H₀ 投影公式 (D_app) 嘅早期實作。
> **原狀態**: 見 01_problem_record.md / 06_complete_record.md (D_app 公式 60 已閉合 χ² = 11.3/7dof — 該 χ² 需重驗)。


---

## ⚠️ O169 修正交回 (2026-09-15) — 本 O 專屬 session 必須重新驗證 / 重新推導

> **上游 O**: `../o169_da_spectral_first_principles/` (commit 41b5485; docs/01–04 + final_result.md)
> **性質**: 上游結構修正 — 本 O 下列結論**依賴已證偽嘅伸長定律**, 需就地重驗或重推。
> **鐵律**: 唔准用自由參數 tune 返舊結論; 唔准引入新常數補齊; 若新結構出唔到 → **誠實標 🔴**。
> **本節只加註** — 本 O 原有結論 (01_problem_record.md / docs/ / final_result.md) 未經改動,
> 重驗後嘅新結論由本 O session 自行寫入, 並更新本節狀態。

### ① 上游修正內容

```
【已證偽】E(ℓ) = 1 + 2φ⁻¹ℓ              2φ⁻¹ = 1.2360679
          DESI DR2 D_M × 6 排除 4.88σ (自由擬合 a = 0.994278 ± 0.04951, b = 1.12157 ± 0.02458, ρ = −0.9575)

【新零參數】E(ℓ) = ⟨γ⟩_odd/2 · ℓ + 1/⟨v_g⟩_{1..22} = 1·ℓ + 1.11911398
          χ²(D_M × 6) = 2.4528/5,  6/6 |σ| ≤ 1.0     (舊 27.16 / 舊+δ 13.09)
          a = ⟨γ⟩_odd/2 = μ²/2 = Σγ_odd/N_d = 1      (Σγ_odd = 44 = N_d, EXACT)
          b: 窗口 K = 22 = N_d/2 = Z₂ 自對偶模 (掃 K = 1..43, 唯一 ≤1σ)

【δ 新身份】δ(ℓ) = −φ⁻³(ℓ − 1/2),   C = 1 − 2φ⁻¹ = −(√5−2) = −0.23606798  (EXACT)
          ⚠️ 舊 C = −0.1697 係 (ℓ−0.5)(1−4^{−ℓ}) 形狀嘅係數 — 定義唔同, 唔可直接比數值
             (C_old/C_new = 0.7189); 舊形嘅 (1−4^{−ℓ}) 因子係多餘

【φ 影子】E(ℓ) = ℓ + √5/2  (δ 零點精確喺 ℓ = 1/2, E(1/2) = φ) — 同譜讀法簡併 0.097%, 觀測不可分辨

【殘餘】LRG1 −3.05σ → −1.00σ ; Lyα +1.64σ → +0.05σ ; BGS(D_V) −2.15σ → +1.45σ
```

### ② 本 O 受影響檔案 (grep 定位)

- `scripts/02_h0_projection.py:62-124,156,201-202` — D_app + dD/dz 導出
- `scripts/07_calibration_methods.py:29,112`
- `01_problem_record.md:14,88`, `03_first_results.md:28`, `06_complete_record.md:62-69`, `08_calibration_mechanism.md:64`

### ③ 交回任務 (本 O 專屬 session 執行)

1. [ ] H₀ 投影公式 (D_app) 換新伸長; 重算 χ² = 11.3/7dof (公式 60 嘅閉合需重驗)
2. [ ] dD/dz 導出 (line 201-202) 重推 (斜率 2φ⁻¹ → 1)
3. [ ] 校準機制重驗

### ④ 唔受影響 (核對過, 免重做)

- 1.80% Maser 偏移現象本身
- 距離階梯 H₀ 簇聚 ±2%

### ⑤ 參考

- `../o169_da_spectral_first_principles/docs/01_elongation_falsification.md` — 證偽全表 (七 tracer)
- `../o169_da_spectral_first_principles/docs/02_delta_spectral_closure.md` — 譜閉合 + 恆等式 11/11 + C = −φ⁻³
- `../o169_da_spectral_first_principles/docs/03_window_selection.md` — K = 22 Z₂ 窗口唯一性
- `../o169_da_spectral_first_principles/docs/04_open_ledger.md` — 誠實帳簿 + 跨 O 影響 (§E6 = 檢查器修復)

### ⑥ 全 repo 完整性檢查器已改為報 🔴 (2026-09-15, 附加)

`open_problems_fresh/scripts/integrity_check.py` (O169 §E6 已修) 現時會對本 O 嘅
`06_complete_record.md` 報 **3 項 stale** 並以 **exit 2** 結束:

```
🔴 h0_tension/06_complete_record.md: '73.13' 仍存在 — H_eff(0.03) 舊伸長值 → 新結構值 66.33
🔴 h0_tension/06_complete_record.md: '0.12%' 仍存在 — vs SH0ES 匹配率 → 新式 6.5σ 偏離
```

**即係**: 只要 `06_complete_record.md` 未更新, 全 repo 檢查器就會一直非零退出。
檢查器**唔會代本 O 改數值** (交回原則) — 呢個 🔴 要由本 O session 喺執行 ③ 之後自行清除。

新舊對照 (供 ③ 重推用, 實跑數值):

| z | 文檔/舊式 H_eff | 新式 H_eff |
|--:|--:|--:|
| 0.01 | 72.75 | 65.39 |
| 0.03 | **73.13** | **66.33** |
| 0.05 | 73.55 | 67.29 |
| 0.10 | 74.81 | 69.77 |
| 0.20 | 77.96 | 75.00 |
| 0.50 | 90.37 | 92.21 |
| z→0 | 72.59 (= c/R_H) | 64.93 |

★ `H₀_idcm = c/R_H = 72.59` 係**結構定義, 唔經伸長, 保持不變** (檢查器仍 ✅)。
崩潰嘅只係 **H_eff = c/(dD/dz)** 呢條投影 Jacobian 鏈 — 新式 z=0.03 得 66.33,
vs SH0ES 73.04 → **6.5σ**; vs Planck 67.40 → 1.6%; vs TRGB 69.85 → 5.0%。
即「匹配 SH0ES 0.12%」呢個結論喺新形式下**反轉**。
