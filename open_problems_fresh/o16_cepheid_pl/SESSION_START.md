# O16 新 Session 啟動文件 — Cepheid PL 機制

## 所需 Skills

1. `idcm-structural-derivation-workflow` (核心)
2. `theoretical-physics-validation` (輔助)

## 前置資料

```
SH0ES = 73.04 = H₀_idcm × (1+φ⁻¹/100) ✅ (0.00%)
H₀_idcm = 72.59
φ⁻¹/100 = 1% SH0ES 偏移
Cepheid = 距離階梯第 1 rung
```

## 啟動 Prompt

```
開 O16 Cepheid PL 專案: /home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o16_cepheid_pl/

任務: 推導 Cepheid 週光關係 (PL) 嘅 K_Chain 耦合

背景: SH0ES 校準 = ×(1+φ⁻¹/100) 閉合 (0.00%)
但 Cepheid PL 關係本身嘅結構機制未明

步驟:
1. Cepheid 週期 P ↔ K_Chain 模式分析
2. PL 斜率 vs 結構預測
3. φ⁻¹/100 偏移來源 (點解 /100?)
4. 44-tone 振盪器類比 (Cepheid = 恆星振盪)
5. 可證偽預測

載入 skills: idcm-structural-derivation-workflow
鐵律: 0,1 → φ → K_Chain 推導, 唔借外部
誠實: 推唔到 → 🟡
最後: 雙重驗證 + 更新 01_problem_record + README
```

## 常見坑

1. Cepheid PL 係觀測關係 (Leavitt law) — 唔好重新推
2. φ⁻¹/100: 100 = 10²? 定 44×2.27? — 要有來源
3. Cepheid 振盪物理 (radial mode) vs K_Chain 44 模式
4. SH0ES 已閉合 — 新機制唔好破壞
