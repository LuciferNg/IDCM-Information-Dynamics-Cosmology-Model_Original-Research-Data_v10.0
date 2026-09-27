# O128 — σ8 歸一化驗證

> **創建日期**: 2026-08-29
> **狀態**: 🔴 未開始
> **來源**: v9.0 項目審計 — `open_problems_fresh/sigma8_norm/`
> **前置**: O100 (C_ℓ→P(k)) 🟢, O99 (光本體論) 🟢, O92 (KiDS S8) 🟢
> **定位**: 從 v9.0 sigma8_norm/ 遷移 — σ8 歸一化在 v10.0 O100 閉合後的獨立驗證

> **★ 後續更新 (2026-09-27, 第一輪)**: 狀態 🔴 未開始 → **🟢 已閉合**（獨立驗證完成；
> 真缺口交回上游）。**檔名沿革**: 本檔原位於 `docs/01_problem_record.md`，本輪依目錄約定
> 移至 root（`01_problem_record.md`）；內文原文一字保留，只 append 新段（§六–§八）。
> **路徑更正**: SESSION_START / §四 所載之 v9.0 來源 `open_problems_fresh/sigma8_norm/`
> 實際位於 **v9.0 樹** `IDCM-v9.0--W-Field-Lattice/open_problems_fresh/sigma8_norm/`
> （唯一檔 `01_derive_sigma8.py`）；v10.0 樹內並無該目錄。

---

## 一、問題

從 v9.0 sigma8_norm/ 遷移 — σ8 歸一化在 v10.0 O100 閉合後的獨立驗證

## 二、假設

1. v9.0 推導在 v10.0 非膨脹框架中部分或全部有效
2. 需要驗證的關鍵假設：
   - 是否依賴膨脹宇宙假設？
   - 是否使用 v9.0 已 demote 的參數（如 ζ(z)）？
   - 是否與 v10.0 已閉合結果（O76, O100, O51 等）一致？

## 三、驗證步驟

### 步驟 1：讀取 v9.0 原始推導
- 路徑: `open_problems_fresh/sigma8_norm/`
- 目標: 提取所有公式和數值

### 步驟 2：識別 v9.0 特有假設
- 列出所有依賴膨脹宇宙的假設
- 列出所有使用 v9.0 demote 參數的公式

### 步驟 3：在 v10.0 框架中重新驗證
- 用 v10.0 的 idcm_core.py 常數重新計算
- 與 v10.0 已閉合結果交叉驗證

### 步驟 4：遷移或重建
- 如果 v9.0 推導有效 → 遷移到 v10.0
- 如果 v9.0 推導失效 → 建立新推導

## 四、已知 v9.0 參考文件

- `open_problems_fresh/sigma8_norm/`

## 五、開放問題

1. v9.0 推導是否在 v10.0 中有效？
2. 是否需要修正以適應非膨脹框架？
3. 與 O1-O121 中已閉合結果的關係？

---

## 六、推導時序索引

### 第 1 輪 (2026-09-27) — v9.0 遷移裁決 + v10.0 σ8 獨立重推 + A_φφ/缺口審計

| 序 | 產物 | 內容 | 結果 | commit |
|:-:|:---|:---|:---|:---|
| 1 | `scripts/01_v9_migration_ruling.py` + `docs/02` | v9.0 `sigma8_norm` 遷移裁決（V1–V5） | **7/7 PASS**；裁決 = **唔可遷移**（σ8 = √A_chain×0.1 手調；PASS 準則 post-hoc；硬編碼路徑失效） | 24d50fe |
| 2 | `scripts/02_sigma8_independent.py` + `docs/03` | v10.0 σ8 獨立重推（閉式代數路線，唔讀 O100 產物檔） | **12/12 PASS**；σ8 = **0.7481967814**（dev 2.8×10⁻¹⁴%）；零自由參數、1 觀測錨 | 24d50fe |
| 3 | `docs/03` §四 | 審計 O100：χ*=πR_world 敏感度行內部不一致（只改窗未同步 transfer） | 0.1305 → 正確 **0.2247**（結論不變） | 24d50fe |
| 4 | `docs/03` §四 | 審計 O100：ℓ_m 公式 m=5 手寫例外（通用式 1199 ≠ 觀測 1121） | 🟡 公式脆弱點（只記錄，需 O83 交代） | 24d50fe |
| 5 | `scripts/03_aphphi_and_gap.py` + `docs/04` | A_φφ 核比穩健性（P_n 形狀掃描）+ 缺口分析 + 覆蓋率復算 | **16/16 PASS**；核比形狀依賴 [0.9899, 1.1446]；所需 σ8 ∈ [0.7622, 0.8196]；覆蓋率 94.2% 復現 | 24d50fe |
| 6 | `docs/04` §八 | 回報上游（只記錄，唔改上游檔） | O100 更正 2 項；O213 聲稱降級 2 項 | 24d50fe |
| 7 | `scripts/04_verifier.py` + `docs/05` | 獨立核對器（第三數學路線 + docs 聲稱值 + 自檢） | **30/30 PASS**（見 `data/04_verifier.log`） | 24d50fe |
| 8 | `final_result.md` | 依 `RESULT_TEMPLATE.md` | 🟢 已閉合 | 24d50fe |

**本輪 PASS 總計**: `scripts/01` = 7/7、`02` = 12/12、`03` = 16/16、`04` = 30/30 = **65/65**。

## 七、遺留 / 交回上游（唔屬 O128 範圍）

| # | 內容 | 去向 |
|:-:|:---|:---|
| 1 | σ8 真缺口（O100 0.7482 vs 所需 0.784，+4.8%）= **缺物質傳遞函數 T(k) 通道** | **O100 #1 / O133 / O86** |
| 2 | A_φφ 幾何核比非零參數（形狀依賴）—— O213 `docs/05` §四 聲稱需降級 | **O213** |
| 3 | 缺口幅度 +5.14% → 改述為 +2%～+10%（形狀依賴）—— O213 `docs/11` §六 | **O213** |
| 4 | χ*=πR_world σ8 由 0.1305 更正為 0.2247 —— O100 `scripts/03` L100–103、`docs/01` §2 表 | **O100** |
| 5 | ℓ_m 公式 m=5 例外之結構來源 | **O83 / O9** |
| 6 | BOSS DR12 σ8 = 0.783 之外部可重取性（本輪未由 VizieR/官方檔重算） | 🟡 建議下輪 |

## 八、檔案清單（第一輪產出）

```
o128_sigma8_normalization/
├── SESSION_START.md              (原文保留, 未改)
├── 01_problem_record.md          (本檔; 由 docs/ 移至 root, 內文原文保留)
├── final_result.md               (依 RESULT_TEMPLATE.md)
├── docs/
│   ├── 02_v9_migration_ruling.md
│   ├── 03_sigma8_independent_verification.md
│   ├── 04_aphphi_and_gap_audit.md
│   └── 05_verification_record.md
├── scripts/
│   ├── 01_v9_migration_ruling.py
│   ├── 02_sigma8_independent.py
│   ├── 03_aphphi_and_gap.py
│   └── 04_verifier.py
└── data/
    ├── 01_v9_migration_ruling.log
    ├── 02_sigma8_independent.log
    ├── 03_aphphi_and_gap.log
    └── 04_verifier.log
```
