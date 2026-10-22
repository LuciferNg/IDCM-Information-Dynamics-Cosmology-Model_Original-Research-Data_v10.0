# O218 docs/07 — 規則溯源 + 邊界 + 下游用法

> **日期**: 2026-09-28
> **狀態**: 🟢 本 O 交付物（SESSION_START §四「邊界（唔重疊聲明）」之落實）

---

## 一、規則溯源表（每條 gate → 來源 O）

| gate / 元件 | 來源 | 具體依據 |
|:--|:--|:--|
| class 三分派 (`identity` / `prediction_residual` / `pool_match`) | **O200** | `o200_dimensional_collapse/docs/01` 三分類 |
| G1/G2 葉合法性、G3 零自由參數 | **O201** | `docs/03_identity_criterion.md` §①③; 11 條常數掃描陷阱 |
| G4 陷阱窗 (1e-5, 1e-3) + 前置條件 | **O148 / O151** | `o151/docs/05 §4`、`docs/12`; O201 §2 前置條件 |
| T1 重言式判別（共有量） | **O151** | `o151/docs/12_b1_123_coincidence_verdict.md` §3 |
| T2 跨框架巧合 + T3 自由乘數 | **O204** | `references/structural-null-test-protocol.md` 步驟 4/8 |
| T5 兩級測試 | **O204** | 同協議步驟 2（observable 級 + correction 級） |
| U 非唯一表示 | **O137 R19 A2** | `docs/36 §8.5`「47」6 種表示 |
| G5 密度三件套 (`N_search/N_mc/d_obs/d_med/q_obs`) | **O208** | `docs/01_density_baseline_spec.md` |
| G5 Farey 解析路徑 | **本 O** | 新結果（`farey_density`）— O136 符號庫爆炸之定量形式化 |
| G6 數域分離 | **O201** | §11 數域相容; `b_spec ∈ Q(ζ₁₇₆)⁺` vs `√5/2 ∈ Q(√5)` |
| 池自動閉包（禁手選） | **O204** | 實錄: 手選池漏 `15 = N_d − L₇` |
| 閉包退化定理 | **本 O** | 新結果（`3,4 ∈ base ⟹ 1 ∈ P`）— O201 §4/§19 之代數根源 |
| 表示數 R 隨目錄變 | **本 O** | 新結果（3 → 6 → 23） |

---

## 二、O137 交接項之處理

| O137 項 | O137 原文 | 本 O 處理 |
|:--|:--|:--|
| **遺留 6** | Δn_color 色荷纏繞「無單一結構規則；密度基準 46%/96% ⟹ 目錄論證本身無效」 | **唔屬本 O** — O137 `docs/37` 派工表明寫「開 **O216**」。本 O 提供 O216 所需之 G5 密度判準（候選丟入 `criterion()` ⟹ 密度 > 1% 即 🔴） |
| **審計項 A2** | 「47」有 6 種 a+b 表示 ⟹ 目錄表示非唯一（原文在 docs/26, 未動） | ✅ **已裁決** `NONUNIQUE`（R = 6 ≥ 2）; 並證明 R 係目錄狀態量（3 → 6 → 23), docs/03 §3 |
| 方法論鐵律 ① 密度基準先報 | 任何「和/差屬 IDCM 目錄」論證必須先報密度基準 | ✅ 已**自動化**為 G5（唔再靠人記得報） |
| 方法論鐵律 ② 相對量度 | 模式判別用相對量度 | ✅ dev 一律相對值; trap 窗用相對偏差 |
| 方法論鐵律 ③ 跨檔索引約定有歧義 | 用座標直算 | ✅ **升級**: 本 O 發現 γ 亦有**兩鏈歸一化**歧義（docs/06 §F）⟹ 鐵律③ 推廣為「譜符號必須帶鏈標籤」 |
| 方法論鐵律 ④ 精確無容差判準 | — | ✅ 精確證書機制（sympy 化簡 / mpmath 60 位 < 1e-45） |

---

## 三、邊界（唔重疊聲明）

```
✅ 本 O 擁有: 統一可執行判準 + 非唯一表示裁決 + 池閉包退化 + Farey 密度 + γ 鏈標籤
🚫 本 O 唔做:
   · 唔重新推導 O200/O201/O204/O208 之規則（只合成 + 自動化）
   · 唔裁決 Δn_color（O216）
   · 唔生成候選表達式（判準只判, 唔搜）
   · 唔為結構結果貼物理標籤（Higgs/W-field 屬另一翻譯步驟）
   · 唔改動任何其他 O 之檔案（零外部寫入, docs/06 §B 已證）
```

---

## 四、對 O136「符號庫爆炸」之療效（量化）

```
前: 「數字 X 屬 IDCM 目錄」= 逐案判斷, 無統一標準 ⟹ 1..1000 任何數都能湊到 0.2%
後: 三條可執行防線
    ① class 分派   — 恆等式要有精確證書 (N_search = 1), 唔可以靠數值接近
    ② U + G5 密度  — pool_match 類必須過表示數 + 密度 (Farey: N_search ≫ 1 ⟹ 零判別力)
    ③ 閉包退化定理 — 「n ∈ 池」由代數上恆真 ⟹ 任何以「∈ 池」為據之論證自動作廢
    驗證: 13 類注入全判死 (docs/05) + 10 個真實案例全數復現原判 (docs/04)
```

---

## 五、下游用法（其他 O 點用）

```python
import sys; sys.path.insert(0, "<...>/o218_catalog_identity_criteria/scripts")
import o218_lib as L
P = L.closure_pool()

# (a) 我有一個候選式, 想知道係咪目錄身份
print(L.fmt_result(L.criterion("我嘅候選", "X_expr", "目標", "pool_match", P,
                               nonunique_target=L.depth1_reps(目標值, L.registered_values()).__len__())))
# (b) 我得觀測值 + σ
L.criterion("預言檢定", "pred", "obs", "prediction_residual", P,
            d_obs=偏差, target_precision=σ)
# (c) 我做代數恆等式
L.criterion("恆等式", lhs, rhs, "identity", P,
            exact_cert=("symbolic", L.certify_exact_symbolic(lhs, rhs)[1]))
# (d) 我要判譜身份 (記得帶鏈標籤!)
L.chain_pairing_check("88"); L.chain_pairing_check("176")
```

**必讀提醒**:
```
1. 一定要聲明 class — 混淆三分類 = 方法論錯誤 (O200)
2. 譜符號一定要帶鏈標籤 γ⁽⁸⁸⁾ / γ⁽¹⁷⁶⁾ — 否則同一字串可真可假 (docs/06 §F)
3. 冇密度基準 / 冇證書 ⟹ 判準只會給 🟡 FORMAL_OK — 唔可以當 🟢 用
```
