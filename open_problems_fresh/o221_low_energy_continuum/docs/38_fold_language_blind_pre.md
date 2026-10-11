# O221 / docs/38 — R32-FOLD blind test：O246→O221 handoff「fold 語言適用性」盲測預註冊（B）

**狀態**：🔒 預註冊（frozen 2026-10-11 08:3x HKT）——**未讀取 `logs/42_linear.out` 任何內容**（scripts/42 已完成、log 存在但未開過；mtime/size 已見，內容未見）。
**觸發**：調律者指令「B 完全後按情況是否A」——先跑 B（fold 盲測）再按結果決定 A（接納與否）。

## 0. 測試對象
O246 → O221 handoff：*「O221 殘餘⑤雙 description 可能適合 fold 語言 (tan=二元結構→連續量自然橋)」*。

四判準審計（事前已交）：非秘數 ✓（fold 身份教科書）、可反推 ✓（身份本身）／✗（適用性冇推導鏈）、**盲測 ✗、預測性 ✗**——本 B 測試就係補盲測/預測腿。

## 1. 數據（unseen）
scripts/42 (R32) 嘅 **FD（線性化）deficit ladder** + 同一運行嘅 raw deficit：
- 家族：naive / vert / cube（scripts/42 冇 cell）
- deficit 定義：conf-slope − TT-slope，2 點斜率 M=4→16（scripts/42 `deficits()` 慣例）
- 輸出喺 `logs/42_linear.out`（L2 段 + 逐 M 行）

## 2. 預測（frozen，未睇 log）

| # | 預測 | 門檻 | 結果流向 |
|:--|:--|:--|:--|
| **B1（主）** | **fold-shape 線性化不變性失效**：若 fold 語言 describe 殘餘⑤，階梯形狀比 r = Δ₂/Δ₁（Δ₁=d_naive−d_vert、Δ₂=d_vert−d_cube）必須 raw 同 FD 一致。**預測：r_fd 與 r_raw 偏離 > 50%（相對）**——因為 raw 階梯已顯示冇 fold-ramp（docs/20：[0.8827, 0.4786, 0.3109, 5.16e-4]，增量比 0.415 vs 1.85 非恆定），線性化唔可能無中生有造出 fold 結構。 | \|r_fd − r_raw\|/max(\|r_raw\|, 0.1) > 0.5 ⟹ REFUTED | REFUTED → A=未接納 |
| **B2（次）** | **FD 階梯本身冇 fold-ramp**：若 fold 結構成立，FD deficit 增量 Δ₂/Δ₁ 應該係剛性（與 raw 同向同比例）；**預測：唔係**。 | fold-ramp 一致性 ‖ 唔成立（比率唔恆定、或投向反轉） | 記錄 |
| **B3（次）** | **FD deficit 值唔喺 fold 定點格**：fold 語言 implies deficit 值量化（個值落喺三角波 turning lattice）。**預測：ratio 唔聚集**（d_cube/d_vert、d_vert/d_naive 唔係簡單有理如 ½、⅓） | 記錄（唔做 PASS/FAIL 門檻） | 記錄 |

## 3. 決策規則（pre-declared）
- **B1 REFUTED**（主預測）→ handoff 適用性宣稱**未能通過盲測** → **A：register note**（O246→O221 handoff 標 acceptance = **未接納**，B1 證偽，附實數）。
- **B1 PASS**（意外：FD 與 raw 形狀一致）→ 部分接納／待深測 → **A：register note（部分接納 + 剩餘盲測缺口）**。

## 4. 誠實
- 本測試只處理「fold 語言」嘅可證偽核心；fold 身份存在性（非秘數/可反推）唔重測（已核）。
- 只要 scripts/42 嘅 raw/FD deficit 冇喺註冊前被讀過，B 保持 blind。——註冊時間 2026-10-11 08:31 前後；log mtime 2026-10-10 18:26。

## 5. 結果（2026-10-11 讀 log 後，append-only；預註冊原文唔改）
**scripts/42 log（logs/42_linear.out）FD/raw deficit（2-pt M=4→16）**：
| 家族 | raw deficit | FD deficit |
|:--|:--|:--|
| naive | +1.0737 | +0.8828 |
| vert | −0.0000 | −0.0511 |
| cube | **nan**（扇區響應 M≥4 精確為零） | **nan** |
- **B1：VOID（非 REFUTED、非 PASS）**——cube deficit 未定義（cube 響應精確零）⟹ 預註冊三點 fold 比 r = Δ₂/Δ₁ 無法定義。主預測（r_fd 偏離 r_raw >50%）**無法實測**。
- B1p（post-hoc 兩點比，冇預註冊權重，只記錄）：raw 1.000 vs fd 1.058，偏 5.8%——接近，但 pre-reg void 令佢冇證據力；若要作證據需重新預註冊一條獨立測試。
- **B2：無 fold-ramp**——vert_fd/naive_fd = −0.0579，唔係簡單有理（½/⅓/¼...）。
- **B3：無 fold lattice**——ratio 0.0579 唔聚喺 {½,⅓,⅔...}。
- **B 總判：無正面盲測證據支持「fold 語言適用於殘餘⑤」** ⟹ 按預註冊決策規則同 4 判準：applicability 宣稱 盲測 ✗、預測性 ✗ ⟹ **A 執行：O246→O221 handoff = 未接納（作為結果）；fold 身份僅作可用數學工具；建議保持 OPEN**（register note ×2，2026-10-11）。
- 意外結構事實（R32，docs/39 詳述）：cube 家族 sector 響應喺 axial k 精確為零（M≥4）——呢個先係 R28「cube deficit → 0」嘅真正機制；vert FD deficit −0.0511（距 0.05 門檻 2%）＋ A_TT_fd 1.1651 OK。