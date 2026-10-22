# O236 docs/07 — R5: 補填原理統一（d/t filler）—— ⚰️ 負結果閉合

> **Script**: `scripts/05_filler_unification.py`（11/11 PASS）
> **Log**: `logs/05_filler_unification.out` · **Data**: `data/05_filler_unification.json`
> **日期**: 2026-10-07 · **verdict**: ⚰️ 統一補填機制否證 —— d 與 t 係兩個唔同機制嘅「第 4 成員」；R5 自己嘅可證偽預言已被現有數據否證（C1）；close（docs/01 明確註明「明顯負結果就 close」）
> **範圍**: docs/01 R5（最後一輪推導）+ O136 incoming ×3 整合

---

## 一、R5 可證偽預言：已被現有 filler d 否證

```
docs/01 R5 可證偽: 「新費米子若『補填』角色, C_f 應屬塊極端值 (min/max)」
現有 filler d:     C_f_d = 3.662 —— gen1 中位 (e 3.594 < d 3.662 < u 3.803)  ❌
s3 側檢查 (C1b):   τ 159.6 < c 186.1 < b 255.8 —— c/b 亦非塊極端            ❌
```
預言對現有「補填者」d（甚至 c/b）都唔成立 ⟹ R5 統一機制喺自身可證偽下即遭否證。

## 二、兩個 filler 嘅機制對比（否定統一）

| | d（odd-flow 補填 rank3） | t（s1 補填 mode 13） |
|:--|:--|:--|
| 決定層 | L2 γ 階梯（m_d/m_u = γ₃C_d/γ₂C_u = 2.162 **EXACT**, O233 P2） | SSB/VEV（y_t = 0.994 ≈ 1, m_t = v/√2） |
| 槽位閘 | 輕子 rank {1,5,7} 全奇 ⟹ odd rank 剩餘 3 = d（質量次序固有） | B−L = +1/3 ∉ ℤ ⟹ T3 荷定義域外 ⟹ VEV 移除 |
| C_f 角色 | 正常商殘餘（中位 3.662） | N/A（唔入 C_f 表） |
| 充填目標 | flow-sieve 第 4 成員 | phase-sieve 第 4 成員 |

**冇共同算子**：d 由 L2 譜（γ₁₃…鏈本徵值）定，t 由 v（SSB 尺度）定。唯一共享 = **3+1
sieve 算術**（兩個篩都係「3 輕子 + 1 邊界成員」）—— 描述性平行，唔係機制同一（C6）。

## 三、O136 incoming ×3 整合（register 答覆依據）

| handoff | O136 結論 | 本 O 整合 |
|:--|:--|:--|
| mass-shape | rank-parity 兩值修正 P=0.2165 否證；冪律家族窮盡 | 與 R1 T-G（格填充唔係 label 機制）一致；冪律路線終止，R6 已負閉合 |
| cs-outlier | s/c 獨立單點（ΔRMS −0.1455/−0.068）；家族 P=0.7065 | C_f 內結構冇家族共同性；s 按單點處理 |
| dquark-sector | H_sector FAIL（|Σ| P=0.0856） | d 嘅 odd-flow 補填唔係扇區共同效應；d 按單點處理（本 O 就此收窄） |

O136 三條與本 O 結論一致構成**相互鎖定**：C_f 層冇扇區/家族/統一機制 —— 值層剩餘
只能係單點身份（原 O233/O209 負閉合立場維持）。

## 四、四道硬測試

| 硬測試 | 結果 | 證據 |
|:--|:--|:--|
| ① 自由度成本 | ✅ 零參數 | 機制對比只用已閉合量（γ、C_f、y_t、B−L） |
| ② MC null | ✅ 負結果閉合（無新正聲稱） | R5 預言被現有數據否證（C1/C1b）—— 唔需要新 null |
| ③ 可證偽 | ✅ | 「補填 → C_f 極端」預言已被 d 否證 = 即時可證偽 |
| ④ 結構剛性 | ✅ | 兩個 filler 喺框架層（L2 譜 vs SSB）分離；3+1 只係計數 |

## 五、誠實邊界

1. R5 = **負結果閉合**（docs/01 註明「明顯負結果就 close, 唔好硬推」）—— 統一補填
   機制唔存在；3+1 sieve 平行只係描述。
2. O136 三條為**引用**（docs/38/39 已閉合）；本 O 只做整合答覆。
3. 開放殘餘 = R7（數據等待：P2 第三尺 / P3/P4 相位守恆）—— 唔喺本 O 推。

## 六、產物

- `scripts/05_filler_unification.py`（11/11 PASS）+ `logs/05_filler_unification.out` + `data/05_filler_unification.json`
- 引用：O233 docs/15（d/t 槽）、O136 docs/38/39（incoming ×3）、O235 T5（C_f 表）