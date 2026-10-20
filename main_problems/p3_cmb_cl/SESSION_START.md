# p3_cmb_cl — Session 啟動文件（P3 CMB 角功率譜 C_ℓ）

> 開新 session 時: 載入下面 skills, 然後將「啟動 prompt」複製做第一條訊息。

## 所需 Skills（載入順序）

### 1. `idcm-cmb-analysis`（核心, 必須）
- CMB C_ℓ 峰分析 / CAMB / Planck 數據處理
- 聲學峰位置、峰幅度、高ℓ尾

### 2. `idcm-cl-to-pk-projection`（輔助/需要時）
- IDCM C_ℓ → 3D P(k) / σ8 映射（零參數 ℳ）

### 3. `userskills-idcm-v10.0-research-navigation`（輔助）
- main_problems vs open_problems_fresh 慣例；register pid 對照

### 4. `idcm-rag-search`（查公式前）
- 版本隔離 RAG; 跨版本數字必核歸一化

## 前置資料（session 內需知）

```
專案: /home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/main_problems/p3_cmb_cl/
docs/     # 03_first_results 首推 / 04_peak_sequence 峰序列閉合 / 05_external_verification 外部驗證
          # 06_complete_record 完整記錄 / 08_open_items 開放位
scripts/  # 02 首個結構推導 / 03 峰序列搜索 / 05 CAMB 驗證 / 06 高ℓ峰 / 07 峰幅度 / 08 audit 獨立審計
logs/     # 2026-10-20 全量重跑正典輸出（02/03/05/06/07/08）
data/     # （空 — 冇產物落碟）
```

## 狀態快照（2026-10-20 16:26 HKT 記錄）

- 🟢 **主體閉合**: ℓ_sync=44, ℓ_A=301, 峰 m=1-4 = 220/537/810/1014（0.00-0.05%）
- 🔀 **O9 接管** m=5-7 峰修正（1121/1340/1412）; **O10 接管** 峰幅度（4/9, 11/26…）; **O48** 峰高模型（RMS 0.30%）
- 🔴 **真正缺口**: IDCM C_ℓ 譜高ℓ尾（ℓ>1409）傳輸函數模型 — O48 docs/02 指明 cmb_cl 課題承接
- ⚠️ **m=2 obs 核歸一化**: 文獻 537 vs O9 binned 527（Δ=10）— 引用閉合須註明 obs 來源
- ⚠️ scripts/05 用 lensed `total` 譜（docs/05 宣稱 raw_cl=True 不實）— 附註已加

## 註冊狀態

- register pid: `P3`（舊名 `cmb_cl` 已 merged, 2026-10-20）
- 事件: registered (10-05) → alias → merged → P3; audit/閉合事件 2026-10-20 補註冊