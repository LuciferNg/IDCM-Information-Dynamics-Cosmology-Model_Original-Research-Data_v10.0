# O219 docs/02 — 索引約定憲章 (Index Convention Charter)

> **日期**: 2026-09-28
> **狀態**: 🟢 建立完成（附可執行核對腳本 `scripts/01`、`scripts/03`）
> **用途**: 全 `open_problems_fresh` 引用索引時之單一權威來源。任何文檔寫
> 「pt n / index n / label n / mode n / κ[n,n,n]」前，先對本檔。
> **依據**: 座標直算（`scripts/01`，44/44 PASS）+ cytools 獨立複核（`scripts/03`，7/8 PASS，K8 為發現性 FAIL）

---

## 一、為何需要憲章

O219 起因：O137 `docs/19_open_problems_attack.md` §發現 2 用「pt index = mode index」
建立 n=33 vs n=11 之鏡像區分機制。本輪證明：**同一個整數 33 在 repo 入面至少有
四個唔同嘅物件身份**，而該「區分機制」正正踩在其中兩個之間。

```
Δ[33]  = (−11, −7, −3, −1)   ← CY36_98 polytope Δ 之第 33 個點（o53 sage export）
Δ*[33] = (−1, 0, 0, 1)        ← 極對偶 Δ* 之第 33 個點（o137 dual_polytope_points.json）
mode 33 = K_Chain 第 33 站      ← 鏈側頻譜，與上兩者無任何已證映射
κ[33,·,·] = Δ 第 33 個除子之相交數（= prime divisor label 33，1-based 33 → 內部 32/33 陷阱，見 T5）
```

## 二、五個索引空間（權威表）

| 代號 | 物件 | 範圍 | base | 產生檔 | 主要消費者 |
|:---|:---|:---|:---|:---|:---|
| `L(Δ)` | CY36_98 polytope Δ 之點標籤 | `0..47`（48 點） | 0-based，origin = 0 | `o53_cy3_reality/data/polytopes/cy36_98_sage_export.json` | κ 相交張量、除子基 |
| `L(Δ*)` | 極對偶（鏡像）Δ* 之點標籤 | `0..84`（85 點） | 0-based，origin = 0 | `o137_cy3_topological_resonance/data/dual_polytope_points.json` | φ 向量、sub-GLSM 44 |
| `φ` | GKZ 週期向量 | 73 條，索引 = `L(Δ*)` 之 `0..72` | 0-based，**非壓縮**（標籤保留） | `o137.../data/gkz_period_data.json` | φ 分層、44 點集、docs/13/14/19 |
| `q` | 反規範電荷 | 72 條，`q[i] = φ[0] − φ[i+1]` | 索引 = 標籤 − 1 | — | sub-GLSM 判別式 |
| `κ` | 三重相交張量 | 存檔 `36³`；完整 key 集 `0..36` | 0-based，**0 = origin** | `o53.../cy36_98_intersection_full.json` | O58/O137 P_f 重疊算子 |
| `mode n` | 鏈站點 | 44（`n=1..44`）/ 88 / 176 | **1-based** | K_Chain（O51/O88/O95） | 全部質量譜、選擇律、φ 分層之名 |

### 已驗證之標籤結構（座標直算，`scripts/01`）

```
Δ      : 6 頂點 {1,2,3,4,5,7}；7 個 facet
         non-facet 標籤 = 0..36  （37 = origin + 36 條 ray = h11 ✔）
         facet-interior 標籤 = 37..47（11 點；origin 係唯一內部點 label 0）
Δ*     : 7 個極點 {1..7}；6 個 facet（大小 5,8,13,34,58,77）
         non-facet 標籤 = 0..72  （73 = origin + 72 條 ray）
         facet-interior 標籤 = 73..84（12 點）
★ 推論 : φ 之 73 條 = Δ* 之 non-facet 標籤，一對一，標籤值直接沿用（冇 compact）
         ⟹ 「φ 索引 33」= Δ* 標籤 33；但「prime divisor label 33」= Δ 標籤 33（另一個物件）
φ      : 73 條，Σφ = 1800 = 5×V(Δ*)，V(Δ*) = 360，φ[0] = 360，φ[1] = 176
         ★ 由存檔三角化 simplices × 精確有理體積，73/73 逐位重算成功
φ 分層 : φ=6 → 2 點 {2,31}；φ=8 → 5 點 {5,17,25,29,72}；
         φ=9 → 9 點 {33,37,41,44,45,47,48,50,51}；φ=12 → 28 點
         ⟹ 44 = 2+5+9+28 = N_d（O137 docs/24 L162 之「GKZ φ 分層」恆等式 ✔）
座標律 : (x₂=0 ∧ x₃≡1 mod 4) ∨ (x₂=1 ∧ x₃∈{0,1,3,4,6,7}) ⟹ 恰好 9 點 = φ=9 層
         ⚠ 必須加限定詞「在 73 條 φ 索引點之內」：在全部 85 點上同一律會多中
           {74,78,79}（3 個 facet-interior 點，φ 未定義）
κ      : key 集 0..36（0 = origin）；κ[(0,0,0)] = −360（最大 |κ| 亦然）
         prime_toric_divisors() = 1..36（1-based）；divisor_basis() 缺 {0,3,4,7,8}
mode 側 : A₅ 9 模式集 = {1,2,3,4,5,7,9,11,13} = 前 13 個整數剔除 4 個偶數 {6,8,10,12}
         （純模式側算術，與任何 polytope 標籤無關）
```

## 三、命名規約（寫文檔時照抄）

```
R1  索引必須帶物件：寫 "Δ* 標籤 33" / "Δ 標籤 33" / "鏈模式 n=33"。
    禁止裸寫 "pt 33"、"index 33"、"label 33"。
R2  標明 base。1-based 者寫成 "1-based（內部索引 = 值 − 1）"。
R3  φ 之任何引用須寫 chamber：「φ(topcom chamber)」。見 T3。
R4  「φ」在本 repo 有三義，必須寫明：φ_GKZ（GKZ 週期值）/ φ_layer（2-adic 模式層名）
    / φ = (1+√5)/2（黃金比）。三者互不相干，只係撞名。
R5  禁止隱含 pt↔mode 對應。若真要用，必須寫出映射名（O137 docs/12 之 Map 1–6）
    並標明「未證」；且要報告該映射下嘅全部判別結果（唔可以只取對自己有利嘅一對）。
R6  κ 引用須寫「0 = origin」；除子編號須寫「prime divisor label（1-based）」。
```

## 四、陷阱實錄（T1–T7，全部有腳本可複現）

```
T1 同名不同物：Δ[33] = (−11,−7,−3,−1) ↔ Δ*[33] = (−1,0,0,1)。
    「prime divisor label 33」屬 Δ；「φ 索引 33」屬 Δ*。兩者不能互換。
T2 標籤係枚舉偽影：同一個點 (−1,0,0,1) 嘅索引隨排序改變 —
      file order → 33 ／ 字典序 → 19 ／ (ℓ²,字典序) → 6 ／ 逆向 → 51
    (−1,0,−1,3) → 11 ／ 4 ／ 39 ／ 73
    ⟹ 「pt 33」「pt 11」係 data 檔排序嘅產物，唔係幾何不變量。
T3 chamber 依賴：φ 係某一個三角化 chamber 之性質，唔係 polytope 不變量。
      backend='topcom' → φ=9 有 9 點，44 = 2+5+9+28（= 存檔值，可複現）
      backend='qhull'  → φ=9 有 0 點，低 φ 只 22–26 點（且兩次跑出唔同結果）
    ⟹ O137 docs/08–14 之 φ 分層係 topcom chamber 之產物；文檔未記錄此事。
T4 φ 三義同形（見 R4）。O145 `scripts/08` 之「φ=6/8/9/12 扇區」係模式側 v₂ 分層，
    唔係 GKZ φ；兩者只共享名稱與計數（2,5,9,28）。
T5 κ 之 base：cytools `prime_toric_divisors()` 回 1..36（1-based），
    而 `intersection_numbers()` 之 key 集係 0..36（0 = origin）。同一支 lib 兩種 base。
T6 φ 0-based（0..72）vs mode 1-based（1..44）：同一個整數 33 在兩個空間都合法
    ⟹ 最易發生「靜默錯位」（O219 直接成因）。
T7 電荷索引 = 標籤 − 1：q[i] = φ[0] − φ[i+1]，i = 0..71。
```

## 五、可執行核對

```
/usr/bin/python3 scripts/01_index_charter_verify.py            # 44/44 PASS（座標直算，無外部 lib）
LD_LIBRARY_PATH=$HOME/tools/lib:/usr/local/lib \
  /usr/bin/python3 scripts/03_cytools_repro.py                 # 7 PASS + K8 發現性 FAIL（chamber）
輸出: data/01_checks.json, data/01_index_charter.json, data/03_cytools_checks.json
      logs/01_output.txt, logs/03_output.txt
```

`scripts/01` 之方法論備註：體積必須用 `Fraction` 精確行列式。曾用「Bareiss 唔除前
pivot」之變體，零/非零判斷正確但數值被縮放，令 φ 重算 71/73 不符 —— 呢個 bug
係本輪實際踩過並修正嘅（見 docstring NOTE）。
