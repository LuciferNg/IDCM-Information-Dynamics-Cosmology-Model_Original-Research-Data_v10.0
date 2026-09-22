# O208 SESSION_START — 驗證架構標準 (Verification Architecture)

> **Session**: 2026-09-19（新建立）
> **狀態**: 🔴 已註冊 — 未開始
> **來源**: O115 `docs/02_architecture_gap_analysis.md` §三 缺陷 3 + `docs/03_migration_plan.md` §三 VERIFICATION
> **前置**: 無（最上游 — Phase 0，其他新 O 全部依賴本 O 標準）
> **位置**: `IDCM-v10.0--It-From-Beat/open_problems_fresh/o208_verification_architecture/`

---

## 一、問題陳述

v10 閉合帳本不可信 — 實測證據：

| 證據 | 數值 | 來源 |
|:-----|:-----|:-----|
| 硬編碼 `True` 冒充驗證嘅 script（≥3 個字面 True） | **10 個** | 全目錄掃描 |
| O86 `scripts/05_final_verification.py` | 「34/34 PASS」含 **17 個字面 True** | O86 docs/03 |
| 記錄「虛假驗證」嘅審計文檔 | 9 份 | grep |
| README 狀態過時 | O116/117/121/122 標 🔴 實際 🟢 | O115 docs/01 |
| 前置引用漂移 | O134 寫「O56 🟢」但 O56 實際 🔴 | 檔案核對 |
| **密度效應** | 質量匹配 觀測 0.146% ≈ **隨機中位 0.176%** → 統計唔顯著 | O136 docs/13 |
| 組合空間可匹配任意目標 | 隨機可達 **0.0003%** | O136 docs/13 §2.4 |

**後果**: 任何新建構繼承不可信帳本 → 必須最先修復。

---

## 二、交付物

| # | 交付物 | 內容 | 驗收 |
|:-:|:-------|:-----|:-----|
| 1 | **密度基準規則** | 任何數值匹配必須同時報告：隨機搜尋空間大小、隨機中位偏差、觀測偏差分位數。唔報 = 未閉合 | 寫入 `docs/01_density_baseline_spec.md` |
| 2 | **反硬編碼規則** | 驗證 script 禁止字面 `True` / `assert True`；改為數值檢查或明確分級 🟢/🟡/🔴 | 寫入 `docs/02_anti_hardcode_spec.md` |
| 3 | **三源一致機制** | README / SESSION_START / 前置引用 自動對齊工具 | `scripts/` + 一致率報告 |
| 4 | **10 script 審計** | 逐個重寫為真檢查或降級標記 | 每 script 一份審計記錄 |

### 10 個高風險 script（待審計）

```
o86_sm_gr_coupling/scripts/05_final_verification.py     17 個 True
o117_dh_line_of_sight/scripts/09_first_principles_closure.py  6
o69_gamma_spectrum/scripts/06_verify_geometric_derivation.py  5
o54_antimatter_abundance/scripts/06_antiparticle_origin.py    5
o65_mixing_first_principles/scripts/04_final_verification.py  4
o121_black_hole_entropy/scripts/05_information_paradox.py     3
o121_black_hole_entropy/scripts/10_singularity_resolution.py  3
o66_mcomp_first_principles/scripts/00_verification_check.py   3
o49_neutrino_mass/scripts/06_structural_closure.py            3
o21_node9_anomaly/scripts/03_cross_map_verify.py              3
```

---

## 三、閉合測試

- [ ] 0 個 script 含硬編碼斷言（全目錄掃描通過）
- [ ] 三源狀態一致率 = 100%
- [ ] 密度基準納入標準報告格式（新 O 強制）
- [ ] 10 個 script 全部重寫或降級標記完成

---

## 四、與現有 O 嘅邊界

| 範圍 | 歸屬 |
|:-----|:-----|
| 驗證**標準**（規則制定） | **本 O** |
| 驗證**執行**（各 O 自己嘅 script 修正） | 各 O 自己 |
| Runtime ISA 驗證（計算架構） | O126（唔重疊） |
| 結構強制完整驗證 | O135（唔重疊 — 本 O 只訂標準） |

**唔准**: 用本 O 標準改寫其他 O 嘅結論（只降級標記，唔改推導）。

---

## 五、鐵律

- 唔准 tune 返舊結論、唔准引入新常數；出唔到就誠實標 🔴。
- 密度基準係**入場券**：冇分位數 = 唔准入帳。
- 只改本 O 檔案（其他 O 由各自 session 自行修正）。
