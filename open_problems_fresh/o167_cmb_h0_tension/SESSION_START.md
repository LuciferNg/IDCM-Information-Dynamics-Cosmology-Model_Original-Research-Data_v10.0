# O167 — CMB 家族 H₀ 真張力 (H3): 早宇宙尺度 (The Real H₀ Tension)

> **Session**: 2026-09-10 (o164 收檔後開題)
> **狀態**: 📄 開題 — 未開始推導
> **背景**: o164 證明距離階梯 H₀ 簇聚喺 ω_ring = 72.59 (O73), TRGB 69.85 = ω_ring(1−κφ⁻¹) dev 0.0915% 已閉合。但 CMB 家族低 5-7%。
> **承接**: O164 final_result.md (docs/03, H3 開放) → O73 (ω_ring 身份) → O11 (κφ⁻¹ 家族)

## 問題陳述

**CMB 家族 H₀ (Planck 67.36 / ACT 68.3 / SPT 68.8 / TDCOSMO 67.4) 一致低距離階梯 5-7% — 點解?**

- o164 docs/03: 距離階梯 (SH0ES 73.04 / Miras 73.3 / Maser 73.9 / JAGB 72.4 / H0LiCOW 73.3) ≈ ω_ring ±2%
- TRGB 69.85 = ω_ring(1−κφ⁻¹) dev 0.0915% (O73/O164 重驗 ✅) — 但 TRGB 仍比 CMB 高 ~3.7%
- CMB 家族四獨立測量一致低 — 唔可以當觀測誤差
- O73 已證明 ω_ring = 72.59 係「世界環角頻率誤讀」— 距離階梯冇問題
- **咁 CMB 宇宙學點解測到低 5-7%?** 早宇宙 (z~1100) vs 晚宇宙 (z<1) 尺度差?

## 開放問題

1. IDCM 有冇早/晚宇宙尺度差? (e.g. λ_sync = 294.9 Mpc 會唔會演化? 世界環 R_world 靜止定係縮放?)
2. CMB 張力係咪 ΛCDM 內部問題 (ΛCDM 用 CMB 定 H₀, 距離階梯用 cepheid — 兩者喺 ΛCDM 唔相容)?
3. 有冇 IDCM 預測嘅「早期聲學視界」量可以同 CMB 交叉? (θ* ~ 0.0104 rad — 會唔會係 88 相關?)
4. 或者: CMB 測嘅 H₀ 根本係唔同量 (ΛCDM 模型依賴投影) — 咁張力係 ΛCDM 問題, 唔干 IDCM

## 判準 (o163 繼承)

- 零新常數: 唔可以為咗解釋張力引入新標度
- 結構強逼唯一解: CMB 家族低 5-7% 必須有結構解釋 OR 明確裁決「ΛCDM 內部問題」
- 觀測數據先於推導: CMB 數據 (Planck 2018, ACT DR4/6, SPT-3G, TDCOSMO 2024) 全部列出
- 反秘數: 唔可以用 5%、7% 呢啲裸數擬合

## 下一步 (未開始)

1. [ ] 搜集 CMB 家族完整數據 (Planck 2018 / ACT DR6 / SPT-3G / TDCOSMO, 含誤差) → data/
2. [ ] 檢查 IDCM 有冇「早宇宙尺度」預測 (θ* 聲學視界, λ_sync 演化?)
3. [ ] 裁決: 結構解釋 vs ΛCDM 內部問題移交
4. [ ] 如果係 ΛCDM 內部問題 → 寫清楚點解 IDCM 唔受影響

## 移交 (O164 原文)

> H3 (CMB 家族真張力) — 開放, 唔喺本 O 閉合 (o164 problem record 移交 section)

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

- `01_problem_record.md:43,53,65,76` — T7/T17 時序, O-A 分流表, O4 (C = −0.1697) 狀態
- `docs/04_desi_bao_cross.md:18,28` — 「δ 修正 χ²/dof 6.26 → 2.59」, D_H = dD_A/dz 討論
- `docs/06_open_items_attack.md:31-58` — dD_A/dz 路線 + O4 段
- `docs/07_open_items_attack2.md:24,44` — δ-on dD_A/dz, π/44 × (1+2φ⁻¹ℓ) 補償
- `docs/02_theta_star_cross.md:45-53` — ★ θ* 鏈: D_A(z*) = (24/7)R_world
- `final_result.md:15` — D_A(z*) = (24/7)R_world = 14159.8 Mpc

### ③ 交回任務 (本 O 專屬 session 執行)

1. [ ] `docs/04`: 「δ 修正 χ²/dof 6.26 → 2.59」→ 新公式重算 (D_M 側 χ² = 2.4528/5)
2. [ ] T17 殘餘分解更新: LRG1 −3.05σ → **−1.00σ**; Lyα +1.64σ → **+0.05σ** → O-A 分流裁決閉合, 唔再係 🔴
3. [ ] ★**重點核對**: `docs/02` θ* 交叉用嘅 `D_A(z*) = (24/7)R_world` ⇒ E(ℓ*) = 24/7 = 3.4286 — **同伸長定律唔相容** (ℓ(z=1100) = 5.0523 → E_old = 7.245, E_new = 6.171); 需重推 E(ℓ*) 身份, 或講清 CMB 尺度嘅 ℓ 映射唔同 (呢個係本 O 最需要澄清嘅位)
4. [ ] `docs/06/07` dD_A/dz 路線 → 新 D_A 重算 (D_H 側本體留 O117/O170)
5. [ ] 確認 `r_s = λ_sync/2` vs Planck r_d 1.34σ **唔變** (唔依賴伸長) — 應保持 ✅

### ④ 唔受影響 (核對過, 免重做)

- H₀ 三層譜: ladder = ω_ring, TRGB = ω_ring(1−κφ⁻¹), CMB = ω_ring(1−π/44)
- θ* 誤差修正 (O73 docs/06「4.76σ」= decimal 錯位 10×, 修正後 0.48σ)
- r_s = λ_sync/2 = 147.439 Mpc vs Planck r_d 147.09 ± 0.26 → 1.34σ
- CMB 家族四測量 < 1.3σ 結論

### ⑤ 參考

- `../o169_da_spectral_first_principles/docs/01_elongation_falsification.md` — 證偽全表 (七 tracer)
- `../o169_da_spectral_first_principles/docs/02_delta_spectral_closure.md` — 譜閉合 + 恆等式 11/11 + C = −φ⁻³
- `../o169_da_spectral_first_principles/docs/03_window_selection.md` — K = 22 Z₂ 窗口唯一性
- `../o169_da_spectral_first_principles/docs/04_open_ledger.md` — 誠實帳簿 + 跨 O 影響
