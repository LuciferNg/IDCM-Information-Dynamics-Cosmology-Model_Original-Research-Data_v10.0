# O149 — 群速度鎖定（v_g Locking）：由 K_Chain 色散結構推出混合角

> **日期**: 2026-09-05
> **狀態**: 🟡 部分閉合（受抑制扇區 2/2 先驗鎖定；中等扇區開放）
> **位置**: `open_problems_fresh/o149_vg_locking/`
> **問題**: CKM/PMNS 混合角能否由 K_Chain 色散結構**先驗鎖定**，取代後驗搜索？
> **結果**: 見 `docs/01_derivation_record.md` — 定理 1-4 + 盲測 P1-P3

---

## 1. 背景（O146 §10 審計結論，2026-09-05）

O146 §10 審計發現：

| 發現 | 結果 |
|:-----|:-----|
| 🔴 CKM/PMNS beat/beat 公式 | **後驗搜索產物**（83 萬候選密佈, 1e-7 匹配必然, δ_min 2.7x 無顯著） |
| 🟡 分子細/分母大傾向 | 10/11 公式分子 rank 17% vs 分母 76% |
| 🟡 d=1 相鄰對超額 | 4/22 vs 隨機 1.0, 超幾何 p=0.015 |
| 🟡 **d=1 = 群速度** | **beat(n,n+1) = 4sin(π/176)·cos((2n+1)π/176) = 4sin(π/176)·v_g(n+1/2)** (43/43) |

**核心機會**: 「細角度 = 低群速度模式比」嘅統計傾向 + d=1=群速度恆等式 → 混合角可能由 K_Chain 色散結構**先驗推出**，而唔係搜索。

---

## 2. 目標

**用群速度身份做先驗鎖定**: 由結構推出「θ₁₃ = 低群速度相鄰對 / 大模式對」，而唔係搜 83 萬個比。

具體子問題:
1. **v_g 色散結構**: v_g(n) = c·cos(πn/88) — 有咩特殊模式? (v_g=1, √2/2, 0, 極值)
2. **低群速度極限**: v_g→0 (n→44) 對應高模相鄰對 — 呢啲係咪 θ₁₃/V_ub 嘅分子?
3. **先驗鎖定規則**: 能否由 K_Chain 結構推出「θ₁₃ 用 (42,43)/(10,31)」而唔係其他 83 萬組合?
4. **盲測**: 鎖定規則後, 預言未用嘅混合角/CP 相位

---

## 3. 已知結構（O146/其他 O）

- ω_n = 2sin(nπ/88), γ_n = 4sin²(nπ/88) = Laplacian 本徵譜
- v_g(n) = c·cos(πn/88) (源碼 kchain_wave_params.py)
- d=1 拍頻 = 4sin(π/176)·v_g(n+1/2) (O146 §10 恆等式)
- beat/beat 比中分子傾向細拍頻 (rank 17%), 分母大拍頻 (rank 76%)
- O65 γ-ratio 混合角 (先驗, 4/4): sin²θ₁₂ = γ₂/(γ₂+γ₃) 等
- CKM/PMNS docs beat 公式 11 條 (後驗, 待先驗化)

---

## 4. 驗證方法（防後驗陷阱）

1. **先驗鎖定**: 由色散結構推出 (d,s), 唔准搜 83 萬個比
2. **多對一**: 多個混合角指向同一 v_g 家族
3. **精度 ≪ 間距**: 正規化後誤差遠細過 2.62e-6
4. **盲測**: 鎖定後預言未用觀測量

## 5. 判決標準

| 層 | 通過條件 |
|:--|:---------|
| 結構 | v_g 家族 = 混合角家族 有明確對應 |
| 統計 | 鎖定規則 p < 0.01 (唔係後驗) |
| 閉合 | 全部 CKM/PMNS 量 < 1% 誤差 |
| 證偽 | 若規則由搜索得出 → 🔴 |

---

## 6. 檔案

| 檔案 | 內容 |
|:----|:-----|
| `docs/01_derivation_record.md` | 推導記錄（§一–十二 撰寫 2026-09-05；§十三 獨立驗證補充） |
| `final_result.md` | 最終結果（RESULT_TEMPLATE.md 範本） |
| `scripts/01_vg_spectrum.py` | v_g 色散結構分析 |
| `scripts/02_prior_locking.py` | 先驗鎖定規則統計（R0–R5） |
| `scripts/03_locking_discovery.py` | 鎖定發現 + 局部密度 null |
| `scripts/04_ladder_lock.py` | k-ladder 驗證 + 統計 + 敏感度 |
| `scripts/05_family_structure.py` | 家族結構（Fib/Lucas 聚類） |
| `scripts/06_final_structure.py` | 最終結構驗證 |
| `scripts/07_blind_test.py` | 盲測（P1–P4） |
| `scripts/99_independent_verifier.py` | 獨立驗證（mpmath 高精度，25/25 ✅） |
| `data/*.json` | 結果 |

## 7. 依賴

O146 (§10 審計) → O149 (本項目) ; 交叉: O65 (γ-ratio), docs/ckm_derivation, docs/pmns_derivation

---

## 8. 推導時序索引（2026-09-05）

按實際發生順序，每一步只記錄當時知道嘅嘢（無回溯加料）：

| 步驟 | 時間序 | 動作 | 發現 / 產出 |
|:----:|:-------|:-----|:-----------|
| T0 | 前置 | 讀 O146 §10 審計 | 🔴 docs beat 公式 = 後驗（831,713 候選）；🟡 d=1 相鄰對 = 群速度恆等式 |
| T1 | 1 | `scripts/01_vg_spectrum.py` | **定理 1**: beat(a,b) = 4·sin(dπ/176)·v_g((a+b)/2)（946/946）；**定理 2**: Z₂ 字典 ω_n = 2v_g(44−n), γ_n = 4v_g(44−n)²（44/44）→ O65 γ-ratio = v_g²-ratio |
| T2 | 2 | `scripts/02_prior_locking.py` | R0–R5 規則統計；R2 相鄰對 ratio 初現 8/11 <1%；R4/R5 密度飽和 |
| T3 | 3 | `scripts/03_locking_discovery.py` | 局部密度 null：R2 8/11 低於密度期望（~11/11）→ 唔顯著；受抑制角低於 v_g-ratio 下限 |
| T4 | 4 | `scripts/04_ladder_lock.py` | **定理 3**: floor = sin(π/176)（loose）；**定理 4**: k-ladder g_k = beat(44−k,44−k+1)/beat(44−(k+1),F_{k+6}) — k=2 → sinθ₁₃、k=3 → V_ub、k=4 自然終止；p_joint = 9.64e-10；敏感度：放寬後 98 候選只有嚴格規則嗰 2 個命中 |
| T5 | 5–6 | `scripts/05_family_structure.py` + `06_final_structure.py` | 分母 mean 11/11 特殊位置 ±2（F₈×4、L₆×3、SYNC 22、階梯 33、F₇、L₅）；分子 5/11 Fib；單調性成立 |
| T6 | 7 | `scripts/07_blind_test.py` | 盲測 P1–P4 → 3/4 PASS；🟡 V_td = beat(40,42)/beat(3,42) = 0.0085684（搜索產物，非鎖定） |
| T7 | 8 | 撰寫 `docs/01_derivation_record.md`（§一–十二） | 完整推導記錄；狀態 🔴→🟡 |
| T8 | 9 | `scripts/99_independent_verifier.py`（獨立 code path + mpmath） | **25/25 PASS**；發現 tight floor = sin(π/176)/cos(3π/176) = 0.017875（§五 補充）；docs 全部數值重算一致 |
| T9 | 10 | 本 session：docs §十三 + 本索引 + `final_result.md` | 文檔層面收尾 |

**時序誠實聲明**: T1–T8 係同一 session（2026-09-05）內順序發生；每步產出只依賴先前步驟，無以最終結果回溯反推（k-ladder 規則本身係「動機化選擇」— 🟡，見 docs §六 同 §十#1）。
