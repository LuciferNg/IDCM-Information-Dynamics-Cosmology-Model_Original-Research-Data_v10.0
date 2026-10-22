# O51 — SESSION START (O169 修正交回專用, 2026-09-15 建立)
> **本 O 原狀態**: 🟢 已閉合 (2026-09-15, 全部數學層問題零剩餘) — 惟 §9.13 群延遲修正 (scripts/82) 已 FAIL。

---

## ⚠️ O169 修正點 (2026-09-15) — 待本 O 重驗

**修正點** (上游 O169):

- 伸長定律 `E = 1 + 2φ⁻¹ℓ` **已證偽** (DESI DR2 D_M×6 排除 4.88σ) → `E(ℓ) = ℓ + 1.11911398` (= ⟨γ⟩_odd/2·ℓ + 1/⟨v_g⟩_{1..22}); `δ(ℓ) = −φ⁻³(ℓ−1/2)`, `C = 1−2φ⁻¹ = −(√5−2)`

**問題** (本 O 受影響點):

- `01_problem_record.md:425,563-580,590-653,860,888` — D_app 預言, §9.13 C 推導, 腳本狀態表
- `final_result.md:17-18` — D_app + C = −0.1697
- `scripts/63_bao_advanced.py:143-164` — IDCM D_app 預言 (2φ⁻¹ℓ)
- `scripts/82_group_delay.py` — 群延遲推導 (❌ FAIL, C_final = 0.0759 ≠ 0.1697)
- `scripts/63` D_app 預言 → 新形重跑, 更新 BAO 比較
- **裁決 `C_delay = 0.061410` 係咪結構量** — O169 完全冇用到佢; 若冇獨立身份 → 降級巧合 (避免佢日後再被當結構常數用)

**狀態**: [ ] 未重驗
> 只加註, 未改本 O 結論檔 (01_problem_record.md / docs/ / final_result.md); 重驗後由本 O 自行寫入。

---

## 📌 2026-09-20 — O81 session 移交: Σγ_even/Σγ_odd 兩慣例需明確區分 (需本 O 處理)

> **性質**: 修正指引 + 要求。**本節只加註, 未改本 O 任何原文/結論檔。**
> **來源**: `o81_eom_unification/docs/03_doc_crosscheck_20260919.md` ⚠️1

### 問題

本 O `scripts/reconstruct_o51.py` L63 / L70 **同時**記載兩套定義, 但冇明確區分兩者係**唔同索引集**:

```
L63: | Σγ_even（44-site 偶數子集 n=2,4,…,44） | 46 |
L70: > Σγ_even = 90（偶數 k=2n 完整重現 44-site 全譜 = 世界）、Σγ_odd = 88（奇數 k=2n−1 = 觀察者）
```

讀者容易把 46 同 90 當成同一符號嘅兩個值。

### 要求

1. 喺 `scripts/reconstruct_o51.py` L63 / L70 附近加**明確標籤**:
   - `46` = 44-site 鏈 (γ_n = 4sin²(πn/88), n = 1..44) 之 **n-奇偶和**
   - `90` = 88-site 對偶鏈 (γ_k = 4sin²(πk/176), k = 1..88) 之 **k-偶和** = **世界能量** (O34 定義)
2. 若 O34 完成命名裁定 (見 O34 SESSION_START 移交項), 本 O 跟隨該命名
3. 確認 `Σγ_even − Σγ_odd = μ² = 2` 在**兩套慣例下皆成立** (O81 已獨立核對: 兩者皆 = 2.0000000000)


---

## ★ 全樹路徑衛生審計註記（2026-10-02，append-only）

> 由 skill `script-chain-reproducibility` 全鏈核對器（`path_hygiene_scan.py`）全樹掃描建立——
> **2026-10-02 首次**。**本節唔改動上方任何內容。**
>
> ⚠️ 本節係**工具層審計**（產物路徑衛生），**唔屬本 O 推導**；亦冇對本 O 任何結論作出判定。
> 完整報告：`path_hygiene_audit_20261002/REPORT.md`

### 〇. 一句話

本目錄命中 **5 個 ghost-tree call site**。

### 一. 命中清單

#### ⚠️ ghost tree 依赖

| # | 檔案:行 | 讀取目標（ghost tree 內）|
|:--|:--|:--|
| 1 | `o51_kchain_origin/scripts/07_inverse_problem.py:19` | `open_problems_fresh/cmb_cold_spot/data/smica_smoothed.txt` |
| 2 | `o51_kchain_origin/scripts/60_lowl_verification.py:186` | `open_problems_fresh/o19_lowl_dodecahedron/data/cl_feathered.json` |
| 3 | `o51_kchain_origin/scripts/61_full_verification.py:62` | `open_problems_fresh/cmb_cold_spot/data/a5_nodes.txt` |
| 4 | `o51_kchain_origin/scripts/reconstruct_o51.py:11` | `open_problems_fresh/o51_kchain_origin/01_problem_record.md` |
| 5 | `o51_kchain_origin/scripts/reconstruct_o51.py:693` | `open_problems_fresh/o51_kchain_origin/01_problem_record.md` |

### 二. 處置（別 O 執行；本節只記移交）

```
⚠️ ghost tree 依赖：5 個 call site 讀 `/home/wsl/Projects/IDCM/IDCM-v10.0/`。
   ① 把所需檔搬入本 O `data/`（或記明「唯讀外部輸入」）
   ② `BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` ＋ 相對路徑
   ③ 風險（已量化）：ghost tree 係 2026-09-08 副本（全樹 288K）。全樹 301 個 call site 分類：
      ① 69 個目標仍存在（讀嘅係**陳舊副本**）；② 231 個目標已失踪但同相對路徑在 repo 存在
      （⟹ **改一行即可，零資料損失**）；③ 1 個 repo 內完全冇。逐 O 對照表 → 同報告目錄 `ghost_dispatch.md`
```

> ⚠️ 依據 `idcm-closeout` §8.1：跨 O 問題**只登記移交，唔准就地修**。本節由**外部審計**寫入，
> 本 O 之 session **有權刪去或改寫本節**（上方內容不受影響）——但如果決定保留，
> 請在 GATE / 下輪 round doc 裏明文記下「已接納 / 已處理」。
