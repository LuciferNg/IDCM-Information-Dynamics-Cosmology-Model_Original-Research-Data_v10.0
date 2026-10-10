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
