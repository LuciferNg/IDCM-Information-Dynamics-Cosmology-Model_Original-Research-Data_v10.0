# O219 — pt↔mode 索引前提審計 (Index Premise Audit)

## 狀態: 🟢 **已閉合** (2026-09-28)
一段話：A3 審計項成立；「pt index = mode index」🔴 判為**未證且約定依賴之橋**，
docs/19 §發現 2 之區分機制（2e）失效，其餘 2a–2d 數值全部 ✅；
φ 幾何側結構（44 = 2+5+9+28 = N_d、φ=9 九點座標律）全部 ✅ 且順序無關。
傳播範圍 = 1 處（docs/19 §發現 2），另 4 項 🟡 標註建議（chamber／限定詞／撞名／x₃ 滑移）。

## 一、問題與方法

```
輸入：O137 docs/36 §十二 審計項 A3 —
      「docs/19 §發現 2 之 pt↔mode 前提有疑；φ=9 點索引 ∩ 9 模式集 = ∅」
方法（次序不可倒，依 SESSION_START §三）：
  1. 座標直算：唔信任何檔案之索引聲稱，由 polytope 座標 + 存檔 simplices 重建全部索引集
  2. 傳播掃描：5,297 檔三段式（斷言 / 同行共現 / 管道）+ 四族關鍵詞
  3. 獨立複核：用 cytools 自己嘅 label API 對照座標直算結果
  4. 逐條裁決：docs/19 §發現 2 拆成 2a–2e 五條；原文零改動
```

## 二、結論（✅ / 🟡 / 🔴）

```
✅ 成立（順序無關、可精確重算）
  - Δ* φ 向量：73 條，Σφ = 1800 = 5·V(Δ*)，V(Δ*) = 360，φ[0] = 360，φ[1] = 176
    ★ 由存檔 simplices × 精確有理體積 73/73 逐位重算成功（scripts/01 C1/C2）
  - GKZ φ 分層：44 = 2+5+9+28 = N_d（φ=6:2, φ=8:5, φ=9:9, φ=12:28）
  - φ=9 九點座標律：(x₂=0 ∧ x₃≡1 mod 4) ∨ (x₂=1 ∧ x₃∈{0,1,3,4,6,7})，3+6 分裂
  - 低 φ（≤12）= 44 = N_d；高 φ = 29 = L₇
  - docs/14 九行座標表逐行吻合；γ₃₃ = 2+√2、γ₁₁ = 2−√2、和 = 4（精確代數）
  - 索引結構：Δ 非 facet = 0..36（origin + 36 除子）；Δ* 非 facet = 0..72；
    φ 索引 = Δ* 標籤（一對一、非壓縮）；κ key 0..36（0 = origin）

🔴 失效（作為推導／判準）
  - 「pt index = mode index」：無推導；O137 自己列 6 個候選映射未選定；
    標籤係枚舉偽影（33/19/6/51）；排名映射下令判準恆真；全局應用會排除 2-adic 候選 1、7；
    統計中性（0.2837 / 0.4855）
  ⟹ docs/19 §發現 2 **2e（區分機制）** 失效；2a–2d 數值不受影響

🟡 待標註（回報 O137／O145，本輪唔動他 O 檔案）
  B1 φ 分層係 chamber 依賴（topcom vs qhull：φ=9 有 9 點 vs 0 點；低 φ 44 vs 22–26）
  B2 座標律需加「在 73 條 φ 索引點之內」（全 85 點會多中 {74,78,79}）
  B3 O145「φ=6/8/9/12 扇區」係模式側 v₂ 分層，與 GKZ φ 撞名 → 建議 φ_layer
  B4 O137 docs/12 之 φ=9 候選映射屬探索（scripts/20 內有「Let's try」痕跡）
  B5 O137 docs/22 L64–65 把 x₃ 數值當 mode 編號（同類滑移）
```

## 三、密度基準（O208 要求）

```
F8 隨機 9 點子集（宇宙 = 0..72，共 73）與 9 模式集不相交之機率
   = C(64,9)/C(73,9) = 27540584512/97082021465 = 0.2837
   N_search = 1；d_obs = |交集| = 0；虛無中位數 = 1 ⟹ 觀察不顯著（A3 原論據偏弱）
F9 隨機 φ 分層把一對指定模式判成「一入一落」之機率
   = 2·44·29/(73·72) = 319/657 = 0.4855 ⟹ 該「區分」近半數屬偶然
範圍檢查（更強）：φ=9 之 9 個標籤中 5 個（45,47,48,50,51）超出 1..44 ⟹ 44-鏈下不可能
```

## 四、驗證與可重跑

```
/usr/bin/python3 scripts/01_index_charter_verify.py            44/44 PASS
/usr/bin/python3 scripts/02_propagation_scan.py                5,297 檔；A=5
LD_LIBRARY_PATH=$HOME/tools/lib:/usr/local/lib \
  /usr/bin/python3 scripts/03_cytools_repro.py                 7 PASS + K8（chamber）FAIL

產物：data/01_checks.json、data/01_index_charter.json、data/02_scan.json、
      data/03_cytools_checks.json；logs/01..03_output.txt
踩坑修正（已入 docstring）：體積必須用 Fraction 精確行列式；
      「Bareiss 唔除前 pivot」變體令 φ 重算 71/73 不符（零/非零正確、數值被縮放）。
```

## 五、交付文件

```
docs/01_problem_record.md   問題登錄（+ 本輪 §九 裁決、§十 推導時序索引）
docs/02_index_charter.md    ★ 索引約定憲章（五空間權威表 + R1–R6 規約 + T1–T7 陷阱）
docs/03_adjudication.md     ★ docs/19 §發現 2 逐條裁決（2a–2e）+ A3 裁決 + B1–B5
docs/04_propagation_scan.md ★ 傳播掃描（真受影響 1 處；🟡 5 項；其餘免疫）
RESULT.md / final_result.md 結論摘要
scripts/01,02,03           座標直算 / 傳播掃描 / cytools 複核
```

## 六、未閉合遺留（交回 O137 主線，依鐵律不開新 O）

```
1. pt↔mode 之**正確映射**仍未導出。唯一合法下一步：由結構導出映射
   （候選：子 GLSM 電荷 LCS 匹配；O137 docs/24 L494 已列 B29），
   導出後須報告全部 44 模式之結果（非單對）。
2. φ 分層之 chamber 選擇原理（為何 topcom chamber？）—— 若無原理，
   則 φ 分層只能作為「一個 chamber 之性質」引用，唔可以當 polytope 不變量。
3. 9 模式集（A₅ 軌道）與 φ=9 層（9 點）之真正關係 —— 兩者皆為 9 元結構，
   但目前唯一之連結（標籤同一）已否證；是否另有結構連結（如 3+6 對 3+6）待查。
```

## 七、依賴

```
O137 → O219（docs/06 前提句、docs/12 六候選、docs/14/19 使用點、data/*）
O53  → O219（cy36_98_sage_export、intersection_full κ）
O219 → O137（回報註記已寫入 o137 SESSION_START 2026-09-28 段）
O219 → 全 corpus（docs/02 憲章為索引引用之權威來源）
```

<!-- conclusion-history:start -->
## 迭代史（machine-generated from register.conclusion；append-only）

| concl_hash | 日期 | verdict | 結論摘要 | 支撐 | 取代 |
|---|---|---|---|---|---|
| `a1275ffa298ba1d0` | 2026-10-24 | — | 輸入：O137 docs/36 §十二 審計項 A3 — 「docs/19 §發現 2 之 pt↔mode 前提有疑；φ=9 點索引 ∩ 9 模式集 = ∅」 方法（次序不可倒，依 SESSIONSTART §三）： 1. 座標直算：唔信… | open_problems_fresh/o219_pt_mode_index_premise/final_result.md | — |
<!-- conclusion-history:end -->
