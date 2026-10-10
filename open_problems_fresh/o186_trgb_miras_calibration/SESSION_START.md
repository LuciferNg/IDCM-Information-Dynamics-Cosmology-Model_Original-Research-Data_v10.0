# O186 新 Session 啟動文件 — TRGB/Miras 差異（原 O17 duplicate, 2026-10-04 搬移）

## 所需 Skills

1. `idcm-structural-derivation-workflow` (核心)
2. `theoretical-physics-validation` (輔助)

## 前置資料

```
TRGB = 69.78 = H₀_idcm × (1−κφ⁻¹) ✅ (0.03%)
Miras = 73.29 = H₀_idcm × (1+κφ⁻¹/4) ✅ (0.01%)
κ = 1/16, φ⁻¹ = 0.618
κφ⁻¹ = 3.86%, κφ⁻¹/4 = 0.97%
符號相反 + 幅度比 4:1
```

## 啟動 Prompt

```
開 O186 TRGB/Miras 專案: open_problems_fresh/o186_trgb_miras_calibration/ (原 o17_trgb_miras, 2026-10-04 搬移)

任務: 解釋 TRGB/Miras 校準差異機制

背景: TRGB ×(1−κφ⁻¹) 減, Miras ×(1+κφ⁻¹/4) 加
幅度比 4:1。點解?

步驟:
1. 物理差異: TRGB (He flash, 舊星) vs Miras (脈動, 長週期)
2. 符號: 投影方向 (內/外層)?
3. 4:1 幅度: 4 = F₅−1? κ⁻¹/4? 2²?
4. 結構類比: 44-tone 振盪器模式
5. 可證偽: RR Lyrae 預測?

載入 skills: idcm-structural-derivation-workflow
鐵律: 0,1 → φ → K_Chain, 唔借外部
誠實: 推唔到 → 🟡
最後: 雙重驗證 + 更新 01_problem_record + README
```

## 常見坑

1. 兩個都已經閉合 (0.03%, 0.01%) — 機制要保住精度
2. 符號相反唔一定係「對稱」— 可能係唔同物理
3. 4:1 = 2²:1 可能係 2-fold 結構 — 但要證明
4. TRGB 係「尖端」光度 — 可能同投影層厚度有關

---

## Session 記錄 (2026-10-10) — 結構整理 + 全面重審計

- **任務**: 修正資料夾結構 + 對所有 docs/scripts 做 audit
- **結構**: 02-06 md → `docs/`；`logs/` 建立；8/8 內部鏈接驗證有效；編號自我指涉 O17 → O186（歷史語境「原 O17」保留）
- **scripts**: 01 → 5/5、02 → 6/6、03 → 8/8 全部重跑 PASS（logs/01-03_verify.txt），19/19 零回歸
- **獨立重算**: mpmath 60-dps 13/13 PASS（Binet/Lucas 恆等式精確；H₀ 預測一致；審計自身兩次假 FAIL 已記錄）
- **未動**: register（O186 已 registered + closed，ref 仍有效）；o17_snia_phillips（現正主 O17，本 session 禁止讀寫）

## Session 記錄 (2026-10-10) — 攻堅 session（docs/07）

- **先同步 O73 最新公式**: ω_cmb = ω_ring(1−π/44) = 67.4071 → Q5 由 O73 閉合 (RAG v10.0 確認)，O186 內 Q5 🟡→✅(經 O73)
- **R1 Maser**: MCP XIII 六星系聯合 73.9±3.0 (Pesce+2020)，非單點——候選 φ⁻¹/34 = 73.9095 命中 0.013%、幾何 72.59 = 0.44σ；誤差 ±3.0 無法二分 → 🟡 等 prec<1
- **R2 κ≈6/100**: MC null (10⁷) 命中率 0.269%，未排除 → 🟡 對偶未證實
- **R3 Cepheid 相消**: 「→0」實為統計相位干涉，殘差 ~κφ⁻¹/√44 = 0.58% → 🟡 措辭定量修正
- **R4 家族封閉**: n∈{1,4,6} 對應 3 種標準燭光類型 (天文側封閉 = N_gen) → 🟢
- **R5 10 減 1**: 10 = L5−L1 (L1=1 EXACT)，同 n=6 = L4−1 統一，解除 TRGB circular → 🟢
- **R6 RR Lyrae**: 2025-2026 冇新獨立 H₀ (calibration <1% 就緒未接 Hubble flow) → 🟡 維持
- **R8 Planck 67.36**: ✅ 經 O73 閉合（0.07%/0.09σ）

## Session 記錄 (2026-10-10) — 攻堅第二輪（docs/07 第二輪）

- **R1 Maser 硬化**: Pesce+2020 Table 1 六星系原始數據 (D_A, v) 重建 weighted-likelihood → best-fit 75.2 [72.2, 78.3]，與文獻 73.9±3.0 一致；候選 73.9095 vs 幾何 72.59 ΔlnL=+0.29 (2ΔlnL=0.58≪3.84) 完全無法分辨；**需 ~124 星系先 2σ 分辨**（pec 誤差地板 250 km/s 主導）→ R1 係結構性數據閘
- **R2 結構統一 🏆**: κφ⁻¹/n ≡ φ⁻¹/(16n) **EXACT** (60-dps 驗證) — L1 家族本質係 φ⁻¹/M (16, 64, 96)，κ ≡ 1/16 只係 M=16 命名；全部 H₀ 修正統一 M-家族；SH0ES-RR「近對偶」實為家族內相鄰成員 (96 vs 100, 差 4=B)；R2 🟡→🟢(重構)；MC null 結構池 0.43% > 隨機池 0.269%（巧合嫌疑↑，但已被恆等取代）
- **R3 定量**: Cepheid 群體殘差 κφ⁻¹/√44 = 0.5823% 與 SH0ES 0.6180% 同量級 — 弱觀察，不作結構對偶
- **R5 交叉**: L5−L1=10, L4−L1=6 EXACT；O137 Σ9模式=55=F₁₀ → 10 同時係 F₁₀ 序
