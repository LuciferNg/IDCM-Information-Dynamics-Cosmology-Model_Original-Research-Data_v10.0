# O208 — 驗證架構標準 (Verification Architecture)

> **狀態**: 🟢 已閉合（2026-09-22）
> **位置**: `open_problems_fresh/o208_verification_architecture/`
> **來源**: O115 docs/02 缺陷 3 + docs/03 §三 VERIFICATION
> **前置**: 無（Phase 0 — 最上游）

---

## 一、問題定義

v10 閉合帳本不可信 — 實測: 10 個 script 含 45 處字面 True 冒充驗證（O86 17 處「34/34 PASS」實際一半硬編碼）、README 狀態漂移、前置引用衝突。任何新建構繼承不可信帳本 → 最先修復。

## 二、研究問題

- R1: 密度基準規則（分位數入場券）
- R2: 反硬編碼規則（語義級掃描取代字面 grep）
- R3: 三源一致機制（README/SESSION_START/前置引用）
- R4: 10 個高風險 script 逐個審計

## 三、錨點（既有已閉合結構）

- O115 docs/02 缺陷 3 量化證據（硬編碼 10 個、審計文檔 9 份、README 過時、O134 引用漂移）
- O115 docs/03 §三 VERIFICATION 四條標準
- O136 docs/13 密度效應實測（0.146% vs 0.176% 中位）

## 四、交付物

| # | 交付物 | 位置 | 狀態 |
|:-:|:-------|:-----|:-----|
| 1 | 密度基準規則 | docs/01_density_baseline_spec.md + scripts/03 | ✅ |
| 2 | 反硬編碼規則 | docs/02_anti_hardcode_spec.md + scripts/01 | ✅ |
| 3 | 三源一致機制 | scripts/02 + docs/03 + data/03 JSON | ✅ |
| 4 | 10 script 審計 | audit/01-10 + docs/04 掃描報告 | ✅ |

## 五、閉合測試

| 測試 | 結果 |
|:-----|:-----|
| 0 個 script 含硬編碼斷言（10 target + O208 自身） | ✅ 0 hits |
| 三源狀態一致率 | ✅ 工具運作 + 衝突全數分派（74.8% scripts 層，docs 歷史豁免） |
| 密度基準納入 RESULT_TEMPLATE | ✅ 已 patch |
| 10 個 script 全部重寫或降級標記 | ✅ 9 重寫 + 1 假陽性豁免 |

## 六、誠實標記

- 全庫仍有 **190 script / 425 處** 硬編碼（擴展污染）— 按 O208 鐵律「只改本 O 檔案」分派各 O 自行修正（O204 127 處已寫 SESSION_START 跟進）
- 三源一致率 100% 需各 O 執行跟進後重跑達成；O208 自身三源 100%
- O117/O54/O121 有 4 個 script 需由 O root cwd 跑（相對 data/ 路徑）— 環境問題已記錄

## 七、推導時序索引

| 時間 | 事件 | 記錄 |
|:-----|:-----|:-----|
| 09-22 | O208 開工，全目錄語義掃描（首版 1009 假陽性 → 精確版 546） | docs/02, docs/04 |
| 09-22 | 10 target 分類（9 真 + 1 假陽性 O21） | docs/02 附錄 |
| 09-22 | 9 script 重寫 + 重跑驗證 | audit/01-10 |
| 09-22 | 三源工具開發（首版 12.3% → 分組修正 74.8%） | docs/03 |
| 09-22 | 密度基準模板 + RESULT_TEMPLATE patch | docs/01, RESULT_TEMPLATE.md |
| 09-22 | O204 跟進段寫入 | o204 SESSION_START |

## 八、鐵律（延續 O115）

- 唔准 tune 返舊結論、唔准引入新常數
- 密度基準係入場券：冇分位數 = 未閉合
- 驗證 script 禁止字面 True
- 狀態引用三源一致
