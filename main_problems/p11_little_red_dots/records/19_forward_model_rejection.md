# Record 19 — Forward-model AIC 判別: IDCM 對稱雙峰首次拒證 (2026-10-17)

狀態: 🔴 **T3 對稱性第一次 forward-model 拒證 (3/3 光源)** — 非 pipeline artifact
S scripts: `scripts/26_injection_calibration.py` (data/27_injection_calibration.json)
          + scratch `27_g_forward_model.py` / `27b_ac_forward_model.py`
觸發: 用戶「繼續」→ 落判生死三條件: ① injection-calibrated pipeline
      (都已做) ② R≥2700 全樣本 (A/C 有) ③ T1 雙線 (仍等數據)

---

## 1. 先決: Injection calibration — 舊 pipeline 零辨別力

| 檢查 | 結果 | 意義 |
|:-----|:-----|:-----|
| 假陽性率 (A/C/G, 500 trials) | **1.000** | 對任何輸入都報 ≥2 峰 |
| 注入 Δv=836 量到 bias | +3000..+3700 km/s | 量嘅係寬線跨度, 唔係雙峰 |
| 注入 3345 校正 recover | 0.10-0.48 | 大峰距先有弱信號 |

⟹ **record 17 嘅「峰距 567-837 連續」係 pipeline artifact** (寬線 FWHM 類跨度) —
嗰個「負結果」唔成立。真正判別要 forward-model。

## 2. Forward-model AIC (scipy curve_fit, 同一批數據三模型比較)

模型:
- M0: 單 Gaussian + cont (寬線核心)
- M1: 雙 Gaussian + cont (峰距/振幅/σ 全自由)
- M2: **IDCM 嚴格對稱雙峰** + cont (同振幅/同σ, ±d 繞線心) ← record 14 T3 預言

| 光源 | R | N | ΔAIC M1−M0 | ΔAIC M2−M0 | M1 峰距/中點 |
|:-----|:--:|:--:|:--:|:--:|:--|
| A JADES-GN-68797 | 2700 | 95 | **−66.8** | **+87.8** | 222 km/s / −132 |
| C JADES-GN-73488 | 2700 | 95 | −190.1 | **+41.3** | 8 km/s / +92 |
| G RUBIES-EGS-58237 | 1000 | 35 | −24.1 | **+34.6** | 1067 km/s / +521 |

### 判定

- **M2 (IDCM 對稱) 3/3 光源被拒**: ΔAIC = +87.8/+41.3/+34.6 全部 > +10
  (強證據對抗對稱雙峰形態) — 喺最高 SNR (A)、最高解像 (A/C)、
  有三峰候選 (G) 嘅光源上一致
- **M1 (自由雙峰) 3/3 較好**: ΔAIC = −66.8/−190.1/−24.1 — 但唔應過度解讀:
  自由雙峰提供形狀自由度, fit 好可能係吸收 electron-scattering 嘅指數翼
  (Rusakov model 嘅 exp tail ≈ unequal 雙 Gaussian), 唔一定係「物理雙峰」
- **G 嘅 837 km/s 命中** (record 16): forward-model 顯示峰距 1067 km/s
  中點偏 +521 — 對稱雙峰 fit 唔到 (ΔAIC +34.6) — 單點數字命中唔係形態命中

## 3. 誠實層次

| 層級 | 判定 |
|:-----|:-----|
| T3 對稱雙峰形態 (3/3 光源, forward-model AIC) | 🔴 **拒證** |
| T1 雙線同測 (Δv_Hβ=Δv_Hα) | 🔴 未測 (冇 R≥1000 Hβ+Hα 同窗樣本) |
| T2 峰距量子化 | 🔴 未可判 (舊 pipeline 無效; 需要 injection-calibrated 先掃) |
| IDCM 定理本身 (共軛模態對 → 對稱) | 🟡 數學唔變; LRD 應用喺呢 3 光源唔似成立 |
| 樣本覆蓋 | 3/12 Rusakov 光源 (A/C/G), 非全 LRD 族 |

## 4. 結論

- 巴爾末雙峰定理嘅 **T3 可證偽預言已受第一次真數據拒證** (3/3 高品質光源)
- 未到最終證偽: A/C 係 Rusakov 樣本 (broad-line Hα 選擇), G 有複雜三峰;
  T1 最銳判別仍未測; 樣本 3/12
- 巴爾末雙峰作為 LRD 普遍解釋: **現有數據傾向不支持對稱形態** —
  留低 T1 做最後一槍 (R≥2700 雙線樣本)
- Rusakov electron-scattering 模型 vs IDCM: 本分析唔判兩者優劣,
  只判 IDCM 對稱預言 vs 數據; 雙方都需要 T1 數據

*文檔: closeout 攻堅 · 拒證判別 · 2026-10-17*