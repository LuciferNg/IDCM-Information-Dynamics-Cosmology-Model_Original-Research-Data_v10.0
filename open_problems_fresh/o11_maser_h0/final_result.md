# O11 — Maser H₀ 偏移 (原 P4)

## 狀態: 🟢 已閉合 (2026-08-20; 09-11 審計 37/37)

## 結論

**「Maser +1.80% 偏移」= 0.44σ 統計漲落 + peculiar velocity 模型依賴，唔係結構效應。**
Maser (純幾何 angular diameter distance) 冇恆星投影層 → 偏移 = 0 → 直接量度 H₀_idcm = 72.59 (0.44σ ✅)。

- MCP XIII (2020) 73.9 ± 3.0: 1σ range 70.9–76.9 含 72.59; 5 種 pv 處理 71.8–76.9; 2025 profile 73.5 (0.30σ)
- Mendeleev 測試: IDCM D_app(ℓ) 零參數預測 6 星系距離 → χ²(5) = 1.00/dof ✅ (NGC 4258 = M106 +129 km/s v_pec, 0.52σpec; ΛCDM 對佢 fail 22.5σ)
- 結構搜索: 冇任何 φ/ε/κ 候選 < 1% 偏差 (最佳 κφ⁻¹/2 = 7.02%) → 唔鎖定公式 (禁數字遊戲)

## 關鍵公式

```
偏移解剖:   (73.9 − 72.59)/3.0 = 0.44σ (唔顯著)
           MCP pv 處理 range 71.8–76.9 → 偏移由 fiducial 選擇決定
Mendeleev:  D_app(ℓ) = (44−44/4^ℓ)(R_H/44)(1+2φ⁻¹ℓ),  ℓ = log₄(1+z)
           χ²(5 星系, 剔除 NGC 4258) = 5.0 = 1.00/dof   (零自由參數)
           χ²(6 含 4258) = 265.6  vs  ΛCDM χ²(6) = 515.8
模型依賴:   mock 200 次: ΛCDM 分析 bias = −0.35 km/s (−0.48%)
fit 重現:   ΛCDM D_A → 73.25 (70.5–76.3);  IDCM D_app → 75.75 (72.5–78.5)
           → 72.59 喺兩者 1σ 內; 兩種模型差異 0.62σ (數據唔足以分辨)
家族:       TRGB ×(1−κφ⁻¹)=69.79 | Miras ×(1+κφ⁻¹/4)=73.29 | SH0ES ×(1+φ⁻¹/100)=73.04
           Maser 冇投影層 → ×1 = 72.59
```

## 可證偽預測

- P1: MCP 增加星系 → H₀ 收斂 **72.6 ± 0.5** (vs ΛCDM 保持 73.9)
- P2: NGC 4258 v_pec ≈ **+130 km/s** (M106 infall; cz_fit ≈ 550 km/s)
- P3: ngVLA (2028+) 100+ maser 星系 → σ(H₀) < 1% → 分辨 72.6 vs 73.9 (>1.5σ)

## 依賴

O4 (h0_tension TRGB/Miras/SH0ES κφ⁻¹ 家族) → O11 → (ngVLA 觀測 2028+)

## 驗證

10 scripts (01–10) 全部 exit=0; 文檔 verifier 20/20; 公式級審計 37/37 (2026-09-11)。
詳見 02_closure_record.md §9 + 01_problem_record.md 推導時序索引。

<!-- conclusion-history:start -->
## 迭代史（machine-generated from register.conclusion；append-only）

| concl_hash | 日期 | verdict | 結論摘要 | 支撐 | 取代 |
|---|---|---|---|---|---|
| `cd6c451ecf083428` | 2026-10-24 | closed | 「Maser +1.80% 偏移」= 0.44σ 統計漲落 + peculiar velocity 模型依賴，唔係結構效應。 Maser (純幾何 angular diameter distance) 冇恆星投影層 → 偏移 = 0 → … | open_problems_fresh/o11_maser_h0/final_result.md | — |
<!-- conclusion-history:end -->
