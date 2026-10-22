# O232 docs/05 — R4 裁決：無 t=0 vs 論文 t=0 翻譯層

> 第三輪產物 2026-10-05。附 `scripts/05`（6/6 PASS）。
> 目的：將「IDCM 冇 t=0」同「ΛCDM 有 t=0」之間嘅陳述翻譯規則成文，消除類別混淆。

---

## 0. 結論先行（🟢 R4 已裁決）

**翻譯層成文——任何跨框架時間陳述必須先標 category，只允許「觀測 ↔ 觀測」直接比較；
AGE 與 DISTANCE 相減 = category error（R1 已實際示範並撤銷）。**

## 1. 本源（v10 權威，只引用）

O51 §撤回聲明（2026-08-22）：
> 「IDCM 無膨脹、無大爆炸 → 冇『宇宙年齡』。R_H/c = 13.470 Gyr 係光行時間（哈勃時間量級），唔係年齡。
> 真實年齡 = N·T_sync + τ，其中 N（完整週期數）同 τ（相位位置）都冇法由無理拍頻特徵決定。」
> 「渲染深度 ≠ 年齡：渲染深度 = 光行時間（距離量度，環周長固定 → 永遠 13.47 Gyr）」

## 2. 翻譯表（每行 = 一條翻譯規則 + category 標記）

| ΛCDM 陳述 | IDCM 對應 | Category |
|:---|:---|:---|
| 宇宙年齡 A_U = 13.8 Gyr | 無對應量（冇 t=0）；最近者 τ=13.4701 = 光行距離 | AGE→DISTANCE（**禁相減**） |
| Big Bang at t=0 | 冇 t=0；recursion C_{n+1}=1/(1+C_n) 冇首步；觀察者係幀原點 | NO-MAP |
| 星齡 A_★（觀測） | 同一觀測量，兩框架直接共用 | OBS↔OBS ✅ |
| z → cosmic time | z = 距離／紅移投影（O76），冇時間語義 | NO-MAP（O76） |
| ETS 宇宙年齡 12.91 | ΛCDM 內部比較（早期新物理 vs CMB） | INTERNAL-LCDM |
| t_true = 11100.64 Gyr（IDCM 真實年齡） | N·T_sync+τ（O213）；ΛCDM 冇此量 | IDCM-ONLY |

## 3. 執行規則

```
R1′  每句跨框架時間陳述先標 category (AGE/DISTANCE/OBS/INTERNAL/NO-MAP/IDCM-ONLY)
R2′  只有 OBS↔OBS 可直接比較 (星齡、紅移、光度、H0 觀測)
R3′  AGE↔DISTANCE 相減 = category error (O232 首輪『1.6σ 缺口』案例)
R4′  NO-MAP 陳述不可宣稱「一致」或「分歧」——只可標「無對應」
R5′  文章/新聞引用 IDCM 數字時, 先查 version (v9 遺留敘述可能繼承撤回 — R3 案例)
```

## 4. D1 之正式化（docs/01 六條分歧之首）

「論文 Big Bang t=0 客觀齡 vs IDCM 無 t=0 observer-relative」——依翻譯層，此「分歧」標 **NO-MAP**：
**唔係兩套數值打架，而係 IDCM 冇 AGE category 量**。論文嘅「恆星比宇宙還老」爭議 = ΛCDM 內部
（ETS 12.91 vs CMB 13.8），與 IDCM **正交**（同 R1 裁決）。

## 5. 判決

```
R4 🟢 翻譯層成文: 6 類 category + 5 條執行規則; D1 正式化為 NO-MAP
   實際效果: O232 全 O 嘅比較陳述往後必須帶 category 標記
   (R3 之 τ+t_f「讀法」= DISTANCE+?. 標記為 🟡 待 R5/O213 裁定 t_f 狀態)
```