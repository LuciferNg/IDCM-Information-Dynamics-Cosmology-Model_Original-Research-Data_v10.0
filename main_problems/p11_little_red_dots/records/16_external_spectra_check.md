# Record 16 — 外部公開光譜 T1-T4 判別: 數據下載 + 盲測 (2026-10-17)

狀態: 🟡 數據獲取成功 (3 光源公開光譜); 判別形態 0/2 對稱雙峰拒證未成;
      G Δv=837 ≈ ℓ=3 n=5 階梯 EXACT (0.2%) 單點信號 — 樣本 n=1 唔足以定論
Script: `scripts/24_external_spectra_check.py` (data/24_external_spectra_check.json)
觸發: 用戶「數據能下載就下載」— T1-T4 判別屬數據閘, 公開光譜可下載

---

## 1. 數據獲取 (全部公開渠道)

| 光源 | 文獻 | 渠道 | 檔案 | 解像度 |
|:-----|:-----|:-----|:-----|:------:|
| MoM-uds01 (BH*) | Naidu+2025 (2503.16596) | Zenodo 15059215 | mom-uds01-v3 prism (md5 核對 3f09ede7) | PRISM R~100 |
| JADES-GN-68797 (Obj A) | Rusakov+2026 (Nature) | DJA v4.4 | jades-gdn198-v4 G395H (R~2700) | R~2700 |
| RUBIES-EGS-58237 (Obj G) | Rusakov+2026 | DJA v4.4 | rubies-egs62-v4 G395M (R~1000) | R~1000 |

- Nagative: 三光源都係「Three apparent peaks」候選 (Rusakov B/G) + 最高 SNR (A) + 多峰 Hβ (BH*)
- 檔案留碟: `~/.hermes/cache/scratch/p11_data/` (公開數據政策)
- z 核定: A z=5.0385 (由 [OIII]5007 3.0235 定, 唔用假設); G z=3.6493 (DJA zfit)

## 2. 判別結果 (盲測 — 未看目標配峰)

### 2.1 Naidu BH* (PRISM R~100)
- Hβ 窗 4.11-4.40 μm: 峰 4.2587 / 4.3479 → 外峰距 6279 km/s
- **峰距中點偏移 +3149 km/s — 嚴重不對稱** (P-Cygni 形態, 支持 Naidu 自己 BH*/atmosphere 模型)
- PRISM R~100 (≈3000 km/s/像元) 只可辨 >3000 km/s — 細結構不可辨

### 2.2 Rusakov Object A (JADES-GN-68797, R~2700 最高解像)
- Hα: 單主峰 3.9654 (+181 km/s), 藍翼一堆微抖動 (noise, 非物理)
- 外峰距 3599 km/s (含 noise 峰), 中點偏移 +159 km/s
- **單峰 — 冇對稱雙峰** (Rusakov 自己: A 加 P Cygni absorption)

### 2.3 Rusakov Object G (RUBIES-EGS-58237, R~1000)
- Hα 三峰: 3.0346 (-1713) / 3.0516 (-39, 主) / 3.0602 (+799)
- **主峰→紅峰距 837 km/s ≈ IDCM ℓ=3 n=5 = 836.1 km/s (dev +0.2%) EXACT**
- 藍→主 1674 vs 2×838 (dev 0.12%)
- ⚠️ **峰距中點偏移 -458 km/s — 不對稱** (IDCM 預言對稱雙峰)
- ⚠️ R~1000 ≈ 300 km/s 解像度, 峰位誤差 ~100-200 km/s; 837 喺 836.1±0.2% 係巧合級別內

## 3. 判定 (誠實)

- **T1 判別未完**: 冇光源有 R≥1000 嘅 Hα+Hβ 同時數據 (G 嘅 Hβ 只有 PRISM R~100) — 最銳判別仍等 NIRSpec R≳2700 雙線
- **形態判別: 0/2 對稱雙峰** (A 單峰, G 不對稱) — IDCM 對稱雙峰預言喺呢兩個最靚公開光源上未獲支持
- **單點階梯信號**: G Δv(Hα)=837 ≈ ℓ=3 n=5 (0.2%) — 唯一 EXACT 命中, 但 n=1 + 不對稱中點, 唔可以宣稱
- 需要: (a) R≥2700 全樣本峰距直方圖 vs IDCM 階梯 (b) B/G 更高 SNR 確認三峰真實性
- Rusakov 樣本 (12 objects + 18 stack) 嘅剩餘 10 個中解像光源 — DJA 可下載, 可做系統峰距統計 (待辦)

## 4. 驗證

- `scripts/24_external_spectra_check.py` exit 0; z/A 峰/階梯匹配一致
- md5 核對 Zenodo (3f09ede7...) ✅
- 檔案: `data/24_external_spectra_check.json` (2578 bytes)

*文檔: closeout 攻堅 · 數據閘 · 2026-10-17*