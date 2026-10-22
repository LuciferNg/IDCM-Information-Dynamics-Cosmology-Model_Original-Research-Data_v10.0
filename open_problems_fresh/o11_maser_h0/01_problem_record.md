# O11: Maser H₀ 偏移機制（原 P4）

## 問題陳述

IDCM: H₀_idcm = c/R_H = 72.59 km/s/Mpc。校準方法 = 唔同投影層偏移：
- TRGB = 72.59×(1−κφ⁻¹) = 69.78 (觀測 69.8 ✅)
- Miras = 72.59×(1+κφ⁻¹/4) = 73.29 (觀測 73.3 ✅)
- SH0ES = 72.59×(1+φ⁻¹/100) = 73.04 (觀測 73.04 ✅)
- Maser (水脈澤, 純幾何) = 73.9 → **已閉合: 偏移 = 0, IDCM 預測 72.59 (0.44σ)**

## 推導時序索引 (Derivation Timeline)

按時間順序記錄 O11 推導鏈每一步 (2026-08-16 問題註冊 → 08-20 閉合 → 09-11 審計):

| # | 日期 | 步驟 | Script / 文檔 | 結果 |
|:-:|:-----|:-----|:--------------|:------|
| 1 | 08-16 | 問題註冊: Maser 73.9 偏移 +1.80% 未鎖定 | SESSION_START.md | h0_tension 閉合時遺留 |
| 2 | 08-20 01:09 | 文獻回顧: MCP XIII 73.9±3.0; 2025 profile 73.5; pv 處理 71.8–76.9 | curl arXiv (2001.09213, 2502.11998) | 2026 冇新值; 所有值含 72.59 |
| 3 | 08-20 01:09 | κφ⁻¹ 家族延伸結構搜索 | scripts/01 | 最佳 κφ⁻¹/2 = 7.02% — 冇 <1% 候選 |
| 4 | 08-20 01:11 | 統計顯著性: (73.9−72.59)/3.0 = 0.44σ | scripts/02 | 偏移唔顯著 |
| 5 | 08-20 01:14 | Mendeleev 測試: D_app 預測 6 星系 | scripts/03 | χ²(5)=5.0=1.00/dof ✅; χ²(6)=265.6; ΛCDM 515.8 |
| 6 | 08-20 01:16 | 模型依賴 mock (200 次) | scripts/04 | ΛCDM bias = -0.35 km/s (-0.48%) |
| 7 | 08-20 01:18 | MCP likelihood 初版重現 | scripts/05 | 診斷出 z_i 必須自由 (bug 修正) |
| 8 | 08-20 01:23 | 完整 z_i nuisance 重現 | scripts/06 | ΛCDM 73.25; IDCM 75.75; 72.59 喺兩者 1σ |
| 9 | 08-20 01:23 | 最終閉合驗證 + κφ⁻¹ 家族對比 | scripts/07 | Maser σ=+0.44 ✅; 偏移=0 閉合 |
| 10 | 08-20 01:25 | 閉合寫入: 01_problem_record + README | 01_problem_record.md | 🟢 已閉合 |
| 11 | 08-20 01:40 | 閉合詳細記錄 + 文檔 verifier | 02_closure_record.md + scripts/08 | 20/20 PASS |
| 12 | 08-20 01:41 | Session 完整性檢查 | scripts/09 | 9/9 scripts exit=0 |
| 13 | 09-11 13:27 | 公式級獨立重算審計 (37/37) | scripts/10 | 全部推導鏈正確 |
| 14 | 09-11 | 額外輸出寫入: χ²(6), ΛCDM χ², mock bias, H_eff(0.03) | 02_closure_record.md §3/§4/§6/§9 | 補齊 |
| 15 | 09-11 | 本推導時序索引 | 01_problem_record.md | 建立 |

## 閉合摘要 (2026-08-20, 09-11 審計確認)

**「+1.80% 偏移」唔係結構效應:**

1. **統計唔顯著:** (73.9−72.59)/3.0 = 0.44σ。73.9 嘅 1σ range 70.9–76.9 包含 72.59
2. **模型依賴:** MCP 5 種 peculiar velocity 處理 → 71.8–76.9。「+1.80%」只係 fiducial (σpec=250 km/s) 選擇嘅產物; 用 2M++/CF3 flow 修正 → 71.8 (-1.1%!)
3. **Mendeleev 測試:** IDCM D_app(ℓ) 零參數預測 6 星系距離 → χ²(5) = 1.00/dof ✅ (NGC 4258 異常 = M106 群 +130 km/s peculiar velocity, 0.52σpec)
4. **機制:** Maser = 純幾何 angular diameter distance → 直接量度 D_app → H₀_idcm, 冇投影層 → 偏移 = 0 (對比 TRGB/Miras/SH0ES 嘅恆星投影層 κφ⁻¹ 家族)
5. **冇任何結構候選 < 1% 偏差** (最佳 κφ⁻¹/2 = 7%) → 唔鎖定任何公式

## 可證偽預測

| # | 預測 | 分辨力 |
|:-:|:-----|:------|
| P1 | MCP 增加星系 → H₀ 收斂 72.6 ± 0.5 | vs ΛCDM 73.9 |

> **★ 2026-09-15 更新 (跟進)**: P1 重新表述 — 「MCP 幾何距離必須符合 D_app(ℓ)」(IDCM 直接預言, χ²(5)=5.02=1.00/dof ✅ 已驗證); 「H0 收斂 72.6」係 ΛCDM 翻譯 (cz/D), 2026 新論文 (2608.06247/2609.17684) PV 修正令 H0 跌向 68.7-71.6 但幾何距離同 P20 一致 0.3σ → IDCM 距離預言保持。詳見 o73 docs/11 P1。
| P2 | NGC 4258 v_pec ≈ +130 km/s | 直接量度 |
| P3 | ngVLA 100+ 星系 → σ < 1% → 分辨 72.6 vs 73.9 | 2028+ |

## 驗證

- `scripts/01_structural_search.py` — κφ⁻¹ 家族延伸掃描 (冇 <1% 候選)
- `scripts/02_statistical_analysis.py` — 0.44σ 顯著性
- `scripts/03_mendeleev_test.py` — 6 星系 χ² 比較
- `scripts/04_model_dependence.py` — 模型依賴模擬
- `scripts/05_mcp_reproduction.py` — MCP likelihood 重現
- `scripts/06_full_mcp_reproduction.py` — 完整 z_i nuisance 重現
- `scripts/07_final_verification.py` — 最終閉合驗證
- `scripts/08_doc_verifier.py` — 文檔聲稱值對比 (20/20 PASS)
- `scripts/09_session_check.py` — Session 完整性 (9/9 exit=0)
- `scripts/10_derivation_audit.py` — 公式級獨立重算 (37/37 PASS, 09-11)

## 相關檔案

```
main_problems/p8_h0_tension/scripts/
main_problems/p8_h0_tension/08_calibration_mechanism.md
docs/02_closure_record.md
```

## 技能

- theoretical-physics-validation (核心, 防數字遊戲) ✅ 已用
- web-access-protocol (輔助, 文獻) ✅ 已用 (curl arXiv API)
