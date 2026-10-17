# G2 出路②③ 裁決 — 87 號 (2026-10-17)

> **背景**: 85 號已裁出路① (存量獨立性 🟡)；87 號裁出路②③
> **Script**: `87_g2_exit23_ruling.py` → `data/87_g2_exit23_ruling.json`

---

## 結果: **2/3 PASS（B1 誠實 FAIL = 程式後驗發現）**

## ★★ 時序鎖定 — 出路③ 程序預註冊閘 唔成立 🔴

```
magic 識別:  16_magic_rows_rule / 17_layer_magic_data  10-17 11:03
R5 程序:     35_r5_full_procedure                       10-17 13:44
            37_r5_necessity_and_extension               10-17 13:56
Δ 程序−識別 = +2 時 40 分

★ R5 程序係 magic 識別之後先 formalize — 程序本身係後驗構建!
⟹ 出路③「程序 lock 早於一切」❌ 唔成立
   (程序係為 magic 後驗寫嘅, 唔係獨立預註冊)
```

## 出路② 未來真預註冊 ✅ 採納

```
作為未來 protocol 採納: 新 label 先 lock 後測
唔影響當前 G2 裁決 — 當前 12 label 仍然係: 存量身份 (O-series 先閉合)
+ 程序後驗 (R5 後寫)
```

## G2 完整性裁決（85+87 合併）

```
① 存量獨立性 (O-series 閉合時序)  → 🟡 成立 (85: O 先閉合 1日11時)
② 未來真預註冊                    → ✅ 採納為未來 protocol (87)
③ 程序預註冊閘                    → 🔴 唔成立 — 程序後驗 (87)

G2 最終 = 🔴(規則可預測性, 59 盲測 p=0.69) + 🟡(label 存在性, 85)
         — 兩層分開, 唔會升 PASS
```

## 誠實標記

- B1_exit3 FAIL 係誠實負面——冇 bug：程序 timestamp 真係後於識別
  2:40:40。呢個係「無效才是正確」示範：出路③ 聽落吸引（「程序就係
  預註冊」）但時序拆穿佢——程序係為 magic 寫嘅
- 85+87 合併：唯一企穩嘅 G2 出口 = 出路①（O-series 閉合先行）——
  呢個先係 label 存在性嘅真正獨立保證

## 檔案
```
87_g2_exit23_ruling.py
data/87_g2_exit23_ruling.json
```