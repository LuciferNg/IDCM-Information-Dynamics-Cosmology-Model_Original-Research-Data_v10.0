# G2 出路① 存量獨立性時序裁決 — 85 號 (2026-10-17)

> **背景**: 61/63 號留低 G2 三出路；85 號裁決出路①「存量獨立性＝
> O-series 閉合時序保證 G2 降 🟡」
> **Script**: `85_g2_exit1_timeline.py` → `data/85_g2_exit1_timeline.json`

---

## 結果: **2/2 PASS — 時序鎖定，出路①成立**

## ★★ 時序證據（檔案 mtime）

```
O-series 閉合（final_result.md）:
  O35  beats/mass link-up      10-15 23:34  🟢 閉合
  O55  c_f/SM center/Z₃        10-15 23:34  🟢 核心閉合
  O158 N_d±k·N_gen 聚類       10-15 23:34  🟡 部分閉合
  O171 A₅ ↔ 88-site 配分      10-15 23:34  🟢 閉合

magic 識別（P9 docs）:
  16_magic_rows_rule / 17_layer_magic_data  10-17 11:03
  35_r5_full_procedure                       10-17 13:44

Δ = magic最早 − O最遲 = 1 日 11 時 29 分
```

## ★ 裁決

```
G2 出路①「存量獨立性」成立:
  12 個 label 嘅身份係「存量」— O-series 閉合先行 1.5 日,
  唔係 P9 睇咗 magic 5/5 之後反推貼 label（後驗污染風險排除）

分層裁決（59 號已分層, 85 號補時序證據）:
  「G2 label 存在性」🟡 — O-series 閉合時序獨立保證（77 A 層一致）
  「G2 規則可預測性」🔴 — mirror 盲測 FAIL 維持（59: p=0.69）
  整體 G2 維持 🔴（部分）— 但「後驗污染」指控已排除
```

## 對七閘全景嘅影響

```
G2 由「🔴 盲測 FAIL」精確化為:
  🟡 label 存在性（唔係後驗 — O-series 先行）
  🔴 規則可預測性（mirror 冇預測力）
⟹ G2 唔會 close，但「後驗污染」呢個最重指控已拆
```

## 誠實標記

- mtime 係檔案系統時間戳——假設冇人為改動；git commit 時序（十月 register
  記錄）同 mtime 一致（O35 final 已閉合 2026-09-12 全量審計 110/110,
  內容本身都證明閉合早於 magic 攻堅）
- 85 號唔推翻 59 號——唔會將 G2 改 PASS；只係將「存在性」同
  「可預測性」兩層連埋時序證據釐清

## 檔案
```
85_g2_exit1_timeline.py
data/85_g2_exit1_timeline.json
```