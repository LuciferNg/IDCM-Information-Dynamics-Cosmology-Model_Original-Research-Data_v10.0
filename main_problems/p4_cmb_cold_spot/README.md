# P4 — cmb_cold_spot（CMB 大冷斑：拓撲干涉節點）

## 狀態: 已閉合（8 階段, 0 自由參數）— 殘餘 O2/O3 級開放項另註冊

**IDCM v10.0 對 CMB 大冷斑 (209°, −57°) 嘅解釋**：冷斑唔係 5σ 高斯統計 tail，而係
A₅ 60 節點網格（Rhombicosidodecahedron）嘅拓撲干涉節點 — 位置、振幅、尺度全部由
K_Chain/Lucas/Fibonacci 結構碼鎖定。**「5σ」= 5 = F₅ Fibonacci 結構因子**，
唔係機率巧合。

**閉合鏈（8 階段）**：
振幅 5ε⁵/8 (0.11%) → 位置 (180+L₇, −(44+F₇)) → 尺度 44=2N_d → 群論 A₅ 一般軌道 →
圖身份 Rhombicosidodecahedron (20Δ+30□+12⬠, χ=2) → 阻挫飽和 32=20Δ+12⬠ →
SMICA 真數據 (p=0.019, z=−3.25σ 隨機著色對照) → 錨點唯一性 (node 0 + 57 對徑 only)。
詳細: `docs/22_complete_summary.md`。

完整雙重驗證: `scripts/28_double_verification.py` — **26/26 PASS** (2026-10-20 全量重跑)。

⚠️ **2026-10-24 更正**: §1.1「RMS = ε⁵/8, Planck 0.06%」🔴 降級 —— 真 Planck 全天空
RMS = 4.0645×10⁻⁵（差 3.69×），ε⁵/8 只喺 14.5669° 平滑成立（無結構來源）。詳見 `docs/26_rms_smoothing_audit.md`（O83 handoff）。冷斑比率/位置/圖/阻挫/SMICA 統計不受影響。

## 殘餘開放項（已轉 O-series）

| 項 | 內容 | 狀態 |
|:--|:-----|:----:|
| O1→o184 | 15.11° 幾何夾角 | 🔴 座標系假象證偽 |
| O2 | 熱斑 F₆/F₇ 等級 | 🟡 F₆✅ F₇候選 F₈🔴 |
| O3 | 60 節點溫度統計 | 🟡 主體✅ ΔE=0 邊緣 |
| O4 | Fibonacci 動機 | 🟡 數學✅ 觀測衰減❌ |
| O5-O8 | catalogue/對徑/阻挫/尺度 | 🟢 已閉合 |

## 檔案

| 檔案 | 描述 | 狀態 |
|:----|:-----|:----:|
| `01_problem_record.md` | 問題陳述 + 狀態表 | 🟢 |
| `docs/03_first_results.md` | 振幅 + 位置首推 | 🟢 |
| `docs/15_complete_record.md` | 完整研究記錄 | 🟢 |
| `docs/16-18` | 符號機制 + 圖身份 + 拓撲閉合 | 🟢 |
| `docs/19-21` | SMICA 驗證 + 顯著性 + 錨點對照 | 🟢 |
| `docs/22_complete_summary.md` | 完整總結 | 🟢 |
| `docs/23_edge_closure_integration.md` | 邊長 26.09° 群論閉合 | 🟢 |
| `SESSION_START.md` | 起手式 + 交接 | 🟢 |
| `final_result.md` | 結論摘要（RESULT_TEMPLATE 格式） | 🟢 |
| `scripts/02-28` | 全鏈驗證腳本 | 🟢 |
| `data/` | 節點/著色/阻挫/SMICA 數據 | 🟢 |