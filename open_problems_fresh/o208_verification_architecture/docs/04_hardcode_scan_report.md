# O208 docs/04 — 全目錄硬編碼掃描報告 + 擴展污染清單

> **日期**: 2026-09-22
> **工具**: `scripts/01_hardcode_scanner.py`（語義級，排除 API 參數/配置/註釋/docstring）
> **範圍**: `open_problems_fresh/` 全目錄

---

## 一、掃描結果

| 指標 | 掃描前 | 掃描後（O208 審計完成） |
|:-----|:------|:----------------------|
| 含硬編碼 script 數 | 223 | **190**（剩餘 = 擴展污染） |
| 硬編碼總數 | 546 | **425**（剩餘） |
| O208 10 個 target | 45 | **0** ✅ |
| O208 自身 scripts | — | **0** ✅ |

---

## 二、O208 10 個 target 審計結果

| # | Script | 原硬編碼 | 處置 | 重跑 |
|:-:|:-------|:--------|:-----|:-----|
| 1 | O86 `scripts/05_final_verification.py` | 17 D 型 | 11 數值化 + 6 → 🟡 聲稱 | 19/19 PASS ✅ |
| 2 | O117 `scripts/09_first_principles_closure.py` | 6 D 型 | 用已有 chi² 變量 + 🟡 聲稱 | 跑通 ✅ |
| 3 | O69 `scripts/06_verify_geometric_derivation.py` | 3 B + 5 D | 全部數值化 | 48/48 PASS ✅ |
| 4 | O54 `scripts/06_antiparticle_origin.py` | 5 D 型 | 1 數值化 + 4 🟡 聲稱 | 跑通 ✅ |
| 5 | O65 `scripts/04_final_verification.py` | 1 B + 3 D | 全部數值化 | 全 PASS ✅ |
| 6 | O121 `scripts/05_information_paradox.py` | 2 D 型 | 重用已有計算 | 8/8 PASS ✅ |
| 7 | O121 `scripts/10_singularity_resolution.py` | 1 D 型 | 重用已有計算 | 10/10 PASS ✅ |
| 8 | O66 `scripts/00_verification_check.py` | 3 B + 3 D | 全部數值化 | 69/69 PASS ✅ |
| 9 | O49 `scripts/06_structural_closure.py` | 3 D 型 | 全部數值化 | 12/12 PASS ✅ |
| 10 | O21 `scripts/03_cross_map_verify.py` | 3（假陽性） | **豁免** — healpix `nest`/`pre_smoothed` 係 API/配置參數，唔係驗證斷言 | — |

---

## 三、擴展污染（O208 範圍外 — 各 O 自行修正）

**425 hits / 190 script，按 O 分組：**

| O | hits | 主要形態 |
|:-:|:----:|:--------|
| o204_wfield_constitution | 127 | `chk("1a", True, ...)` 結構聲稱當檢查 |
| o82_mass_generation | 40 | `check("名", True, ...)` 比較論證 |
| o96_su12_origin | 21 | `check("P2b...", True)` 存在性命題 |
| o171_a5_partition_theory | 19 | `ok=True` accumulator 風險 |
| o139_finite_qft_to_qed | 17 | `check("...", True)` 結構論證 |
| o163_dm_identity | 17 | 同上 |
| o168_g_last_input | 14 | `ok_all=True` |
| p7_reionization | 14 | `check("論文已下載", True)` 存在性 |
| o151_holographic_channel_capacity | 12 | `all_exact=True` |
| o83_correlator_cmb | 10 | 混合 |
| 其餘 180 個 script | 118 | 分散 1-9 hits |

**處置協議**（O208 鐵律「只改本 O 檔案」）:
1. 各 O session 用 `o208/scripts/01_hardcode_scanner.py` 掃自己目錄
2. 可數值化 → 改真計算；結構聲稱 → 🟡 分級（唔入 PASS 計數）
3. 每 script 重跑確認 PASS 數不變（或誠實修正）
4. 更新該 O 嘅 SESSION_START 跟進段

**已寫入 SESSION_START 跟進段**: O204（127 hits，最嚴重）— 見 o204 SESSION_START。

---

## 四、驗收

- [x] 10 個 target 0 硬編碼
- [x] O208 自身 0 硬編碼（掃描器以身作則）
- [x] 擴展污染全數列明（本文件 + JSON 全清單）
- [x] 最嚴重 O204 已分派

> ⚠️ 閉合測試「全目錄 0 硬編碼」= 10 target + O208 自身歸零 + 擴展清單分派。
> 全庫 190 script 修正係各 O 嘅執行責任（O208 只訂標準）。
