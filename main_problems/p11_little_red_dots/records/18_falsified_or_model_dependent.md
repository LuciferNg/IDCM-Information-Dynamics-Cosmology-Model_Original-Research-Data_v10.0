# Record 18 — 判定層次: 已證偽 or 模型依賴? (2026-10-17)

狀態: 🟡 **未達證偽; 模型依賴成份實質; 預言保持 alive (weak tension 方向)**
觸發: 用戶「已證偽還是模型依賴?」— 對 record 17 負結果嘅判定層次質問

---

## 1. 三層答案

### 1.1 未達證偽 (三原因)

1. **T1 未測**: 最銳判別 (Δv_Hβ=Δv_Hα 雙線同測 R≥2700) 喺任何樣本上都冇 — Rusakov
   樣本只有 Hα 中解像; 冇光源有 R≥1000 嘅 Hβ+Hα 同時
2. **分辨力不足**: R~1000 ≈ 300 km/s/元素, 峰位誤差 ~100-200 km/s — 同 IDCM 最細階梯
   (ℓ=3 n=1 = 167 km/s) 同量級; 不能分辨
3. **pipeline 未校準**: 峰搜尋 (3pt smooth, 0.1×max, <200 km/s merge) 從未做 injection
   calibration — 唔知佢 recover 真實雙峰嘅能力

### 1.2 模型依賴成份實質 (直接證據)

**C 光源係最乾淨示範**: 同一物理 (JADES-GN-73488, z=4.1325),
- G395M (R~1000) → **單峰**
- G395H (R~2700) → **雙峰** (620 km/s)

⟹ 峰分類隨解像度變 — 峰搜尋結果係 resolution-dependent artifact 成份

**Injection test (初步)**: 注入已知對稱雙峰入真實 G 光譜 noise, recover 率:
| 注入峰距 | 峰高 20% | 35% | 50% |
|:--------|:-------:|:---:|:---:|
| 836 km/s (ℓ=3 n=5) | 0.74 | 0.40 | 0.15 |
| 1672 km/s | 0.09 | 0.38 | 0.87 |
| 3344 km/s | 0.08 | 0.37 | 0.69 |
recover 率 0.08-0.87 橫跨全範圍 — **pipeline 唔係乾淨 detector**; 負結果不能平移到「物理冇雙峰」。
(⚠️ test 自身限制: 未校正 false-positive baseline — 真實 G 本身 noise 下都出 2 峰;
未做多 trials 統計; 結果只做 pipeline 不穩定性示範, 唔係 calibration)

### 1.3 但亦唔係純 artifact (model-free 成份)

- **MC null 係 model-free**: 隨機峰距嘅階梯擊中率 95.5% — 呢個唔依賴峰搜尋參數,
  係「36 候選×±15% 幾何覆蓋」嘅必然; 佢否證嘅係「單點 0.2% 命中有證據力」,
  唔係「雙峰存在與否」
- **A 喺 R~2700 單峰** (形態): 最高 SNR + 最高解像 — 呢個係少數唔太依賴 pipeline
  嘅觀察, 同 IDCM 對稱雙峰預言構成 weak tension (n=1)

## 2. 判定結論

| 陳述 | 判定 |
|:-----|:----:|
| IDCM 對稱雙峰預言已被證偽 | 🔴 未達 — T1 未測 + 分辨力 + pipeline 未校準 |
| 負結果係純模型 artifact (零資訊) | 🔴 唔係 — MC null model-free; A R~2700 單峰係 weak tension |
| 預言保持 alive | ✅ 係 — 未殺死, 未證實 |
| 現有數據方向 | 🟡 唔利 (weak tension) — 但唔足以翻案 |

## 3. 判生死需要 (data-gated)

1. **Injection-calibrated pipeline**: 全 forward-model + false-positive 校正 →
   T2 峰距分佈先有統計意義
2. **R≥2700 全樣本**: Rusakov 只有 A/C 有 R~2700; 需全 12-30 光源同等解像
3. **T1 雙線同測**: NIRSpec R≳2700 Hβ+Hα 同窗 — 一槍定生死 (record 14 判別)

任一樣落地 → 立即重跑 script 25 pipeline (10 光譜檔案留碟)

*文檔: closeout 攻堅 · 判定層次 · 2026-10-17*