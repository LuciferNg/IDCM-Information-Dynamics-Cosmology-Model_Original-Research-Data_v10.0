# O219 — pt↔mode 索引前提審計 (Index Premise Audit)

> **日期**: 2026-09-25
> **狀態**: 🟡 **已註冊 — 未開始**
> **來源**: O137 `docs/36_gap_attack_round19.md` §十二 審計項 A3
> **前置**: O137（φ=9 子配置 / 9 模式集 / κ 相交張量）、O53（CY₃ 真實性）

---

## 一、問題

O137 `docs/19_open_problems_attack.md` §發現 2 建立「區分機制」時，用了一個
**未經核實之前提**：CYTools prime divisor label (1–36, 1-based) = pt index = mode index。
Round 19 審計（A3）實測：**φ=9 點索引 ∩ 9 模式集 = ∅** ⟹ 該前提有疑，
docs/19 §發現 2 之結論基礎可能失效。

核心質疑：索引約定（0-based vs 1-based；44-鏈 vs 48-點 vs 88-環）跨檔有歧義，
任何靠索引對齊之論證都必須**用座標直算**核實，唔可以靠檔案聲稱。

## 二、已確立嘅結構

```
🟢 φ=9 子配置 = 3 世代 (x₂ = 0) + 6 夥伴 (x₂ = 1)
   0-based 點索引: {33,37,41} ∪ {44,45,47,48,50,51}
🟢 9 模式集 Sel = {1,2,3,4,5,7,9,11,13}（O137 docs/31 + O209 docs/09 雙路徑）
🟢 CYTools prime divisor label = 1–36 (1-based) = pt index（O137 R19 §0 約定）
🟢 κ 完整結構 = 37³；0-based/1-based 陷阱實錄: K[0,0,0] = −360 = apex
   ⟹ 索引約定錯一次就令整個相交張量錯位
🟢 polytope: 48 點, 6 個頂點（點索引 {1,2,3,4,5,7}）；md5 63536d17…（自 08-22 未改）
🔴 φ=9 點索引 ∩ 9 模式集 = ∅ ⟹ docs/19 §發現 2 之前提有疑（A3）
🔴 索引約定跨檔冇統一憲章
```

## 三、未確立（🔴 開放問題）

```
🔴 docs/19 §發現 2 之結論是否因此失效（需逐條重核）
🔴 索引約定憲章：跨檔一律寫明 0-based/1-based + 物件（44-鏈 / 48-點 / 88-環 / 176-環）
🔴 「pt index = mode index」之聲稱來源（邊個檔首先寫？有冇驗證？）
🔴 若前提錯，需要 append-only 降級/撤回註記（禁改舊文）
🔴 有冇其他 O 檔同樣依賴該前提（傳播掃描）
```

## 四、攻擊路線

```
1. 逐檔重核 → grep 全 corpus「pt index / prime divisor / mode index」，
   逐處核實用邊個約定，用座標直算驗證（唔靠檔案聲稱）
2. 傳播掃描 → 搵出所有依賴「pt index = mode index」之推導，逐條標記影響
3. 憲章建立 → 寫索引約定憲章（0-based/1-based + 物件），供全項目引用
4. 降級/撤回 → 若前提錯，依時序鐵律加 append-only 註記（原文保留）
5. 反面路線 → 若重核後前提成立（φ=9 點索引其實另有對應），則 A3 解除
```

## 五、驗證標準

```
✅ 索引約定憲章（可執行核對腳本）
✅ docs/19 §發現 2 逐條裁決（成立 / 失效 / 需修）
✅ 傳播掃描報告（全部依賴點列出）
✅ 舊文檔零改動（只加 dated 註記）
```

## 六、狀態

```
🟢 已閉合 (2026-09-28) — 見 §九 裁決 + §十 推導時序索引 + §十一 未閉合遺留
   依據: scripts/01（44/44 PASS）、scripts/02（5,297 檔傳播掃描）、scripts/03（cytools 7 PASS + K8 chamber FAIL）
⭐ 優先度: ★★（審計完整性；唔阻塞主鏈）
原註冊狀態（時序保留）: 🟡 已註冊 — 未開始
```

## 七、相關文件

```
- o137_cy3_topological_resonance/docs/36_gap_attack_round19.md §十二 A3 — 審計項原文
- o137_cy3_topological_resonance/docs/19_open_problems_attack.md §發現 2 — 被審計之前提
- o137_cy3_topological_resonance/docs/14_task_bc_decoupling.md — φ=9 子配置 3+6
- o53_cy3_reality/data/polytopes/cy36_98_sage_export.json — 48 點 polytope（md5 63536d17…）
- O218 — 索引/表示非唯一性判準（相關方法論）
```

## 八、鐵律

```
- 跨檔索引約定有歧義 → 用座標直算
- 舊文檔零改動（時序鐵律：append-only 註記）
- 出唔到就誠實標 🔴
- 只改本 O 檔案
```

---

# 九、裁決（2026-09-28 執行） — 本輪新增，禁改上文

## 9.1 A3 審計項

```
✅ A3 成立：docs/19 §發現 2 之「pt index = mode index」前提不可作區分判準。
   ⚠️ A3 所引論據（φ=9 標籤 ∩ 9 模式集 = ∅）屬弱證據（虛無 P = 0.2837），
      應升級為：範圍檢查（5/9 標籤 > 44）+ 枚舉不變性 + 排名映射退化 +
      與 2-adic 判準衝突 + provenance（docs/12 六候選未選定）。
```

## 9.2 docs/19 §發現 2 逐條

```
2a pt[33] = (−1,0,0,1) φ=9            ✅ 成立（Δ* 標籤 33）
2b pt[11] = (−1,0,−1,3) φ=18          ✅ 成立
2c γ₃₃ = 2+√2、γ₁₁ = 2−√2、和 = 4    ✅ 成立（精確代數，dev < 1e-12）
2d φ≤12 判準：33 入選 / 11 落選        ✅ 成立（數值層）
2e 由 2d 建立「區分機制」= pt↔mode     🔴 失效（前提未證 + 約定依賴 + 退化 + 自相矛盾 + 統計中性）
```

## 9.3 生存之結構（全部順序無關）

```
Δ* φ 向量：73 條，Σ = 1800 = 5·V(Δ*)，V(Δ*) = 360，φ[0] = 360，φ[1] = 176
           ★ 由存檔 simplices × 精確有理體積 73/73 逐位重算成功
φ 分層    ：44 = 2+5+9+28 = N_d；φ=9 九點 = {33,37,41,44,45,47,48,50,51}
座標律    ：(x₂=0 ∧ x₃≡1 mod 4) ∨ (x₂=1 ∧ x₃∈{0,1,3,4,6,7}) ⟹ 9 點（3+6），限 73 條 φ 索引點內
低/高 φ   ：44 = N_d / 29 = L₇
索引結構  ：Δ non-facet 0..36（origin + 36 除子）；Δ* non-facet 0..72；
           φ 索引 = Δ* 標籤（一對一、非壓縮）；κ 0..36（0 = origin）
```

# 十、推導時序索引（禁回溯污染）

```
2026-08-22  O53: Δ = cy36_98_sage_export.json 定稿（md5 63536d17…；48 點 / 6 頂點 / h11 36 / h21 98）
2026-08-2x  O137 docs/06 §1: 寫下「divisor label = 1-36 = pt index = mode index」（唯一出處，無推導）
2026-08-2x  O137 docs/12: 列 Map 1–6 六個候選映射（φ 分層 ↔ 44 鏈），冇選定
2026-08-2x  O137 docs/14: φ=9 九行座標表（3+6 分裂）
2026-08-2x  O137 docs/19 §發現 2: 用標籤同一（pt 33 / pt 11）建「鏡像區分機制」
2026-09-2x  O137 docs/18 L1042: 首次記錄「point index = mode index 唔成立」→ 列新遺留
2026-09-25  O137 docs/36 §十二 A3 + README O219 註冊
2026-09-28  O219（本輪）: scripts/01 座標直算 44/44 → scripts/02 傳播掃描 5,297 檔 →
            scripts/03 cytools 複核 7 PASS + K8 chamber FAIL → docs/02 憲章 / docs/03 裁決 /
            docs/04 傳播報告 → 回報 o137 SESSION_START（append-only）
⟹ 上文（§一–§八）為 09-25 註冊時之原文，零改動（唯 §六 狀態加一行）。
```

# 十一、未閉合遺留（交回 O137 主線；依鐵律唔開新 O）

```
1. pt↔mode 之正確映射仍未導出 → 唯一合法路線：由結構導出（候選：子 GLSM 電荷 LCS；
   O137 docs/24 L494 / R19 B29），導出後須報全部 44 模式結果。
2. φ 分層之 chamber 選擇原理（為何 topcom？）→ 若無原理，φ 分層只可作 chamber 性質引用。
3. 9 模式集（A₅ 軌道）vs φ=9 層（9 點）之真正結構關係 —— 唯一連結（標籤同一）已否證。
4. 🟡 標註建議 4 項：chamber 標註（O137 docs/08–14, docs/24 L162）／座標律限定詞（docs/19 §發現 3）／
   O145 φ 層改名 φ_layer（避免與 GKZ φ 撞名）／O137 docs/22 L64–65 x₃ 數值 ↔ mode 編號滑移。
```

# 十二、本輪新增檔案

```
scripts/01_index_charter_verify.py   座標直算核對（44/44 PASS）
scripts/02_propagation_scan.py       傳播掃描（5,297 檔；A=5、Stage2 四族）
scripts/03_cytools_repro.py          cytools 獨立複核（7 PASS + K8 發現性 FAIL）
data/01_checks.json                  44 條 check 逐條結果
data/01_index_charter.json           索引空間機讀註冊表
data/02_scan.json                    傳播掃描原始命中
data/03_cytools_checks.json          cytools 複核結果
docs/02_index_charter.md             ★ 索引約定憲章（權威表 + R1–R6 + T1–T7）
docs/03_adjudication.md              ★ 逐條裁決（2a–2e + A3 + B1–B5）
docs/04_propagation_scan.md          ★ 傳播報告（真受影響 1 處）
logs/01_output.txt, 02_output.txt, 03_output.txt
final_result.md                      閉合報告
```
