# O219 docs/04 — 傳播掃描報告 (Propagation / Blast Radius)

> **日期**: 2026-09-28
> **腳本**: `scripts/02_propagation_scan.py`（輸出 `data/02_scan.json`、`logs/02_output.txt`）
> **範圍**: `open_problems_fresh/` 全部 `.md` + `.py`，首輪 **5,297 檔**、複跑 **5,303 檔**
> （差異來自期間新增之檔案；排除本 O 自身）
> **問題**: 若「pt index = mode index」唔成立，幾多推導要跟？答：**1 處**（docs/19 §發現 2），其餘屬 point-set 用法，前提唔 load-bearing。

---

## 一、三段式掃描結果

```
Bucket A  （直接斷言該前提）              ： 首輪 5 hit；複跑 6 hit
       （第 6 個 = 本輪寫入 o137 SESSION_START 之回報註記 L345，即本審計自身之產物）
Bucket B' （同一行有 pt 數字 + mode 語言）： 5 hit（4 個為 numpy popt 偽命中）
Bucket B  （索引/標籤/除子/κ 管道用語）   ： 12,342 → 12,372 hit（過寬，非依賴證據；見 §五）

Stage 2（四族關鍵詞，逐族列檔 + 觸及項目數）
  S1 φ 判準（φ=9 / φ≤12 / sub_glsm_44）當作選擇用 : 77 檔 / 13 項目
  S2 2-adic / Lucas 判準                        : 927 檔 / 147 項目
  S3 κ / 除子索引空間                            : 289 檔 / 15 項目
  S4 Δ* 資料檔消費者（dual_polytope_points 等）  : 24 檔 / 3 項目
⟹ 廣度 ≠ 依賴。S1 之 77 檔中，只有 2 檔真正把 φ 分層當「模式選擇」用（見 §二）。
```

## 二、Bucket A：前提之全部出現處（4 檔）

```
1. README.md:161                      O219 註冊行本身（本審計之入口）
2. o137 docs/06_phase4_derivation.md:21
     「CYTools divisor label = 1-36 (1-based) = pt index = mode index (1-based)」
     ⟹ ★ 唯一之「寫法出處」；無推導。O137 R19 §0 之約定，被 docs/19 引用。
3. o137 docs/36_gap_attack_round19.md:728   A3 審計項（已判前提有疑）
4. o137 docs/18_verification_audit.md:1042  「兩者【無交集】⟹『point index = mode index』
                                              在此【唔成立】」— O137 自己已記錄此疑
5. o137 scripts/07_cycle_lengths.py:67      print 標籤「(pt = mode)」— 僅文字標註
⟹ 前提之「使用」僅一處：docs/19 §發現 2。其餘為登錄、審計、或文字標籤。
```

## 三、S1 之逐檔裁決（同一行同時出現 φ 判準 + mode 語言者，共 13 檔）

| 檔 | 用法定性 | 判 |
|:---|:---|:---|
| o137 `docs/19_open_problems_attack.md` L72 | φ=9 選擇律 **＋ pt↔mode 區分機制** | 🔴 **受影響**（見 docs/03） |
| o137 `scripts/20_phase7_2adic_resonance.py` L192/204 | 「Map 5: High modes φ=9 (a=33..41)」= 六個候選映射之一（探索） | 🟡 候選，未選定；非結論依賴 |
| o137 `docs/09_phase6_mirror_period_test.md` L105 | 反而係**提問**：「44 個 φ≤12 點是否對應 44 sites?」 | ✅ 開放問題之記錄 |
| o137 `final_result.md` L104 | 記錄 A3 遺留 | ✅ 記錄 |
| o137 `docs/36…` L728 / `docs/18…` L1042 | 審計記錄 | ✅ 記錄 |
| o137 `docs/22_open_problems_attack4.md` L64–65 | 把 x₃ **數值**當 mode 編號（"mass modes {1,7,20}"） | 🟡 同類滑移，待核（憲章 R5 適用） |
| o137 `docs/25_problem1_a5_synthesis.md` L196 | 提問「A₅ 9 模式是否對應 φ=9 之 9 頂點」 | ✅ 開放問題之記錄 |
| o137 `docs/20_open_problems_attack2.md` L69 | 「模式 n 由 γ 譜決定；C_f 來自 φ=9」— 兩者分開用 | ✅ 唔受影響（未用橋） |
| o59 `scripts/29_projection_mapping.py` L225 | 「44 φ≤12 點…12D 表示應為 12 之選擇」 | 🟡 用 44 點集（集合用法） |
| o145 `scripts/08_physical_labels.py` L8–9 / `docs/07…` L54 | φ=6/8/9/12 **扇區** = 模式側 v₂ 分層（φ 係模式側層名） | ✅ **唔受影響**（唔用 polytope 標籤），但撞名 → 見 docs/03 B3 |
| o145 `RESULT.md` L10 | 同上（層名） | ✅ 同上 |
| o206 `scripts/22_shape_factors.py`、o144 `scripts/02…`、o59 `scripts/25/28/31`、`README.md` | φ=9/φ≤12 作為**點集**引用（標籤只作辨識） | ✅ 唔受影響 |

## 四、結論：影響範圍

```
🔴 真受影響（需修／撤回）：1 處
   o137 docs/19 §發現 2 之「區分機制」（2e）— 6 行內。逐條裁決見 docs/03。
🟡 需加限定／改名（不影響結論）：
   B1 φ 分層補「(topcom chamber)」（O137 docs/08–14 各處）
   B2 座標律補「在 73 條 φ 索引點之內」（docs/19 §發現 3）
   B3 O145「φ=6/8/9/12 扇區」改名為 φ_layer / v₂-layer（避免與 GKZ φ 撞名）
   B5 docs/22 L64–65 x₃ 數值 vs mode 編號之滑移
✅ 完全唔受影響：其餘 ~77 檔（13 項目）之 φ 用法 —— 全部係 point-set／層名用法，
    判準來自座標律（順序無關）或模式側算術（v₂/mod-4），與 polytope 標籤無關。
⟹ ★ 前提「pt index = mode index」在整個 corpus 之承載 = 一個句子（docs/06 L21）
   加一個用途（docs/19 §發現 2）。刪／改該兩處，全框架無其他依賴。
```

## 五、方法學備註

```
- Bucket B（12,342 hit）故意保留而唔當證據：任何「index / label / 索引 / κ」字樣
  都中招，屬雜訊。真正之依賴判定用 Stage 2 + 同行共現（co-occurrence on one line），
  再由人（本輪）逐檔定性。呢個三段式設計就係為咗避免「廣度當依賴」。
- S2（2-adic/Lucas，927 檔 / 147 項目）覆蓋面極廣，係因為 O136/O145/O209/O51/O95
  等 O 以 mode 側算術為主線 —— 而 mode 側算術**唔需要**任何 polytope 標籤，
  所以佢哋全部免疫於本前提。呢點係本 O 最重要之「無需恐慌」結論。
```
