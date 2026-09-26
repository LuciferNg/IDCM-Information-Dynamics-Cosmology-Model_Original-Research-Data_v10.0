# O118 docs/03 — 閉合審計輪（2026-09-26）

> **觸發**: 調律者「開工查 O118 嘅 χ²/dof = 2.58 殘差係咪同樣係假象」→ 閉合後「補全缺口」
> **審計層**: `scripts/02_audit_independent.py`（**36/36 PASS**），`data/02_audit_independent.json`
> **前置層**: `scripts/01_premise_reevaluation.py`（14/14 PASS）— 本輪原地重跑，輸出 **byte-identical**（無 drift）

## 〇. 一句話

閉合成立，且經**兩層獨立驗證**：① 前提值精確複現（18.092/7，dev < 0.01%）；② 獨立第三方重算（36/36）
確認同一數據換現行定律後 `1.7154/7`，並把 **DESI DR2 論文原始表逐值溯源**（數據側無誤 ⟹ 污染在定律側）。

## 一. 本輪做咗乜（四項）

1. **原地重跑** `scripts/01` → 14/14 PASS；`data/01_*.json` 重生成後與原檔 `diff` 為空。
2. **新增獨立第三方審計** `scripts/02_audit_independent.py` — 唔 import 本資料夾任何腳本，自建數據表 + 自建常數管線。
3. **數據側溯源** — 拉 DESI DR2 原文（arXiv:2503.14738）Table 6 逐格核對。
4. **缺口補全** — 根目錄權威 `01_problem_record.md`（含時序索引）、`final_result.md`、本檔；README O118 行回退修復。

## 二. 獨立審計（36/36 PASS）之獨立性措施

| 措施 | 內容 |
|:--|:--|
| 不 import | 完全不引用 `scripts/01` 或其輸出 |
| 自建數據表 | 6 個宇宙學 bin + 2 個 D_V 行**逐字鍵入自論文**（非抄腳本） |
| 雙形式常數 | `B_NEW` 同時用**求和式** `22/Σcos(πn/88)` 與**閉式** `22 sin(π/176)/(sin(π/8)cos(23π/176))`（O213 R3 恆等式），dev < 1e-6% |
| 自寫協方差 | 2×2 協方差矩陣**顯式求逆**（非原腳本之 `(r_m²−2ρr_mr_h+r_h²)/(1−ρ²)` 簡寫） |
| 三種掃描 | SYNC bump：z-空間窄網格（複現原值）+ z-空間寬網格 + **ℓ-空間獨立參數化** |

## 三. 審計結果

| 檢查 | 值 | 判定 |
|:--|--:|:--:|
| 前提複現（7 點，D_lin + D_H=dD_app/dz） | **18.0920 / 7** (2.585) | ✅ dev < 0.01% |
| 前提：LRG1 係最大離群 | worst = LRG1 (−3.05σ) | ✅ |
| 現行框架（同 7 點） | **1.7154 / 7** (0.245) | ✅ 改善 10.5× |
| D_M/rd（6 bin, O169 律） | **2.4528 / 6** | ✅ 6/6 pull ≤ 1σ |
| D_H/rd（6 bin, O170 arch 核） | **3.4712 / 6** | ✅ 與 O170 docs/06 獨立一致 |
| 12 點聯合（含 ρ） | **6.8591 / 12** (0.572/pt) | ✅ |
| LRG1 解剖 | −4.563% (−3.713σ) → **−1.148% (−0.934σ)** | ✅ |
| Lyα | D_H −0.301σ / D_M +0.087σ | ✅ |
| SYNC bump（窄網格，複現） | Δχ² = **0.6387**（amp +0.12, w 0.06） | ✅ 複現閉合值 |
| SYNC bump（寬網格） | Δχ² = **0.335**（amp +0.01, w 0.38） | ✅ < 4 ⟹ 唔被要求 |
| SYNC bump（ℓ-空間） | Δχ² = **0.297**（ℓ_c = 0.3390） | ✅ < 4 ⟹ 唔被要求 |
| 零參數審計 | 兩條定律 0 個擬合常數 | ✅ |

⚠️ **寬網格反而 Δχ² 更細**（0.335 < 0.639）：原腳本掃描 w ≤ 0.80，本輪放寬至 2.00 容許寬 bump。
**兩者皆 ≪ 4（2 dof）** ⟹ 結論不變，且方向上**更強**。此差異係網格範圍，非分歧。

## 四. 數據側溯源（DESI DR2, arXiv:2503.14738）

逐值核對論文 Table 6（6 個宇宙學 bin，8 行含 LRG3/ELG1 子樣本）及 DR2 D_V 行：

| tracer | z | D_M/r_d | D_H/r_d | ρ | 判定 |
|:--|--:|--:|--:|--:|:--:|
| BGS | 0.295 | — (D_V 7.942±0.075) | — | — | ✅ |
| LRG1 | 0.510 | 13.588 ± 0.167 | 21.863 ± 0.425 | −0.459 | ✅ |
| LRG2 | 0.706 | 17.351 ± 0.177 | 19.455 ± 0.330 | −0.404 | ✅ |
| LRG3+ELG1 | 0.934 | 21.576 ± 0.152 | 17.641 ± 0.193 | −0.416 | ✅ |
| ELG2 | 1.321 | 27.601 ± 0.318 | 14.176 ± 0.221 | −0.434 | ✅ |
| QSO | 1.484 | 30.512 ± 0.760 | 12.817 ± 0.516 | −0.500 | ✅ (D_V 26.055±0.398) |
| Lyα | 2.330 | 38.988 ± 0.531 | 8.632 ± **0.101** | −0.431 | ✅ |

**Lyα σ 陷阱已守**：D_H 側用 **0.101**（O117 修正之誤用 0.531 = D_M 值）。

⟹ **數據無誤**（10/10 raw 值命中論文）。前提失效係**定律側**污染，非數據問題。

## 五. 缺口補全清單

| 缺口 | 處置 | 檔案 |
|:--|:--|:--|
| 無 `final_result.md` | ✅ 依 `RESULT_TEMPLATE.md` 建立 | `final_result.md` |
| 問題記錄僅在 `docs/` | ✅ 根目錄新增**權威**記錄（含時序索引）；`docs/01` 原檔保留未動 | `01_problem_record.md` |
| 無推導時序索引 | ✅ 9 行時序表 + 時序完整性確認 | 同上 §推導時序索引 |
| 無第三方獨立審計腳本 | ✅ 建立（36/36 PASS） | `scripts/02_audit_independent.py` |
| README O118 行滯後 | ✅ 修復（見 §六） | `open_problems_fresh/README.md:55` |

## 六. ⚠️ README 回退事件（越權污染還原）

`open_problems_fresh/README.md` 之 O118 行在**已提交狀態**（commit `fcbbab7`「O118: premise VOID」）為
🟢 **已閉合 — 前提作廢**，但工作區被**改返** 🔴 **未開始**（舊前提摘要）。本輪以 `git show HEAD:` 之
commit 版本為權威，**還原該行**（其餘同批新增行 O137/O216–O222 屬其他 session 之工作，未觸碰）。

- 備份：`~/.hermes/backups/open_problems_fresh__README.md.v22pre.20260926_165728`
- 還原後 `git diff README.md` 只剩其他 session 之新增行（+8 行 O137/O216–O222），O118 行 **無 diff**（= 與 HEAD 一致）。

## 七. 檔案變更總表（全部在本 O 資料夾內 + README 一行）

| 檔案 | 動作 |
|:--|:--|
| `01_problem_record.md` | 🆕 新增（根目錄權威記錄 + 時序索引） |
| `final_result.md` | 🆕 新增 |
| `docs/03_closeout_audit.md` | 🆕 新增（本檔） |
| `scripts/02_audit_independent.py` | 🆕 新增 |
| `data/02_audit_independent.json` | 🆕 新增（腳本輸出） |
| `docs/01_problem_record.md` | ✏️ 只加 dated 指針（正文一字不刪） |
| `SESSION_START.md` | ✏️ 附錄閉合審計輪（原文不刪） |
| `README.md:55` | ✏️ 還原至 HEAD（🟢） |

## 八. 相關文件

- `scripts/01_premise_reevaluation.py`, `data/01_premise_reevaluation.json`
- `scripts/02_audit_independent.py`, `data/02_audit_independent.json`
- `docs/01_problem_record.md`（原前提，歷史）, `docs/02_premise_void.md`（裁決）
- `01_problem_record.md`（權威 + 時序索引）, `final_result.md`
- `../o169_da_spectral_first_principles/`（伸長定律證偽）, `../o170_phase_depth_distance/docs/06`（arch 核）
- `../o117_dh_line_of_sight/docs/04`（徑向核取代）, `../o51_kchain_origin/scripts/86_cubic_correction.py`（前提來源）
