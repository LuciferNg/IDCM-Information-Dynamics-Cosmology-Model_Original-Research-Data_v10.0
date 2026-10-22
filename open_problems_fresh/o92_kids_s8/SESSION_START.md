# O92 — SESSION START (O169 修正交回專用, 2026-09-15 建立)

---

## ⚠️ O169 修正點 (2026-09-15) — 待本 O 重驗

**修正點** (上游 O169):

- 伸長定律 `E = 1 + 2φ⁻¹ℓ` **已證偽** (DESI DR2 D_M×6 排除 4.88σ) → `E(ℓ) = ℓ + 1.11911398` (= ⟨γ⟩_odd/2·ℓ + 1/⟨v_g⟩_{1..22}); `δ(ℓ) = −φ⁻³(ℓ−1/2)`, `C = 1−2φ⁻¹ = −(√5−2)`

**問題** (本 O 受影響點):

- `scripts/01_kids_lensing_kernel.py:29`, `scripts/02_s8_geometry_comparison.py:26`, `scripts/99_verifier.py:40,57`
- `docs/99_session_complete.md:34-37` — ★「C = −0.1697 (**理論推導, 非擬合**)」
- ★ `docs/99:37` 「C = −0.1697 (理論推導, 非擬合)」 — **呢句係錯嘅** (O51/82 FAIL, 係經驗式) → 必須改寫; 新: C = −φ⁻³ (結構, EXACT)

**狀態**: [ ] 未重驗
> 只加註, 未改本 O 結論檔 (01_problem_record.md / docs/ / final_result.md); 重驗後由本 O 自行寫入。


---

## ★ 全樹路徑衛生審計註記（2026-10-02，append-only）

> 由 skill `script-chain-reproducibility` 全鏈核對器（`path_hygiene_scan.py`）全樹掃描建立——
> **2026-10-02 首次**。**本節唔改動上方任何內容。**
>
> ⚠️ 本節係**工具層審計**（產物路徑衛生），**唔屬本 O 推導**；亦冇對本 O 任何結論作出判定。
> 完整報告：`path_hygiene_audit_20261002/REPORT.md`

### 〇. 一句話

本目錄命中 **2 個 ghost-tree call site**。

### 一. 命中清單

#### ⚠️ ghost tree 依赖

| # | 檔案:行 | 讀取目標（ghost tree 內）|
|:--|:--|:--|
| 1 | `o92_kids_s8/scripts/02_s8_geometry_comparison.py:294` | `open_problems_fresh/o92_kids_s8/docs/01_first_results.md` |
| 2 | `o92_kids_s8/scripts/03_legacy_des_update.py:177` | `open_problems_fresh/o92_kids_s8/docs/02_legacy_des_update.md` |

### 二. 處置（別 O 執行；本節只記移交）

```
⚠️ ghost tree 依赖：2 個 call site 讀 `/home/wsl/Projects/IDCM/IDCM-v10.0/`。
   ① 把所需檔搬入本 O `data/`（或記明「唯讀外部輸入」）
   ② `BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` ＋ 相對路徑
   ③ 風險（已量化）：ghost tree 係 2026-09-08 副本（全樹 288K）。全樹 301 個 call site 分類：
      ① 69 個目標仍存在（讀嘅係**陳舊副本**）；② 231 個目標已失踪但同相對路徑在 repo 存在
      （⟹ **改一行即可，零資料損失**）；③ 1 個 repo 內完全冇。逐 O 對照表 → 同報告目錄 `ghost_dispatch.md`
```

> ⚠️ 依據 `idcm-closeout` §8.1：跨 O 問題**只登記移交，唔准就地修**。本節由**外部審計**寫入，
> 本 O 之 session **有權刪去或改寫本節**（上方內容不受影響）——但如果決定保留，
> 請在 GATE / 下輪 round doc 裏明文記下「已接納 / 已處理」。
