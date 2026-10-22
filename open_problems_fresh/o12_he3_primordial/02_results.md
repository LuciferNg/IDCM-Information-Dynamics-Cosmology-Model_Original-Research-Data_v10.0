# O12: ³He/H primordial — 分辨力分析結果

## 摘要

**2026 年 8 月止, ³He/H primordial 觀測分辨唔到 IDCM (9.76×10⁻⁶) vs ΛCDM (1.04×10⁻⁵)。** 兩模型都完全 consistent with 所有觀測約束。[1] 🟡

## 文獻現狀 (2022-2025)

| 文獻 | 方法 | 結果 | 註 |
|:-----|:-----|:-----|:---|
| Cooke et al. 2022 [1] | VLT/CRIRES Orion ³Heⁱ* 吸收 | ³He/⁴He = (1.77±0.13)×10⁻⁴ | 太陽系外首次直接量度 |
| Cooke et al. 2022 [1] | SM 預測 | (³He/⁴He)_p = (1.257±0.017)×10⁻⁴ | 標準 BBN |
| Cooke et al. 2022 [1] | GCE model fit | (³He/⁴He)_p = (1.043±0.089)×10⁻⁴ | 誤差唔包 model/yield |
| **Cooke et al. 2022 [1]** | **Empirical limit** | **(³He/H)_p ≤ (1.09±0.18)×10⁻⁵** | **最強約束** |
| Balser & Bania 2018 [3] | GBT ³He⁺ 8.7GHz HII | S209 ³He/H = (1.10±0.28)×10⁻⁵ | 外銀河系, 最接近 primordial |
| Bania & Balser 2020 [4] | GBT ³He⁺ PNe | NGC 3242/6543/6826/7009 | 銀河系內, 非 primordial |
| Balser et al. 2006 [5] | VLA ³He⁺ PN | NGC 6572, J320 探測 | 首次 PN ³He⁺ 探測 |
| Johnson et al. 2025 [2] | GCE 分析 | 需 ~4 個新量度先達 30% 精度 | 現有數據唔夠 |

## 分辨力數學

```
模型差距:  IDCM 9.76e-6 vs ΛCDM 1.04e-5 = 6.16%
觀測誤差:  Cooke limit 1σ = 16.5%
          S209 1σ = 25.5%
需要:      <3.1% 誤差先可以 2σ 分辨
結論:      🟡 分辨唔到 (誤差 >> 差距)
```

## 各基準對比

### (³He/H) 直接對比

| 基準 | 值 | IDCM 9.76e-6 | ΛCDM 1.04e-5 |
|:-----|:---|:---:|:---:|
| Cooke limit | 1.09±0.18e-5 | ✅ 1σ 內 (0.63σ) | ✅ 1σ 內 (0.28σ) |
| S209 | 1.10±0.28e-5 | ✅ 0.44σ | ✅ 0.21σ |

### (³He/⁴He) 推導對比

| 基準 | 值 | IDCM 1.174e-4 | ΛCDM 1.280e-4 |
|:-----|:---|:---:|:---:|
| SM (³He/⁴He)_p | 1.257±0.017e-4 | 6.6% / 4.9σ 名義 | 1.8% / 1.3σ |
| GCE fit | 1.043±0.089e-4 | 12.5% / 1.5σ | 22.7% / 2.7σ |

**重要:** SM 對比嘅 4.9σ 係「名義」張力 — 冇計 ⁴He/H 誤差 (Y_p ~1.4%) + D/H 誤差 (~1.1%)。IDCM ³He/⁴He 系統誤差 ~2.5%, 真實張力 ~2.5σ (組合誤差 quadrature: 6.6%/√(1.35²+2.5²)=2.5σ)。而對比 GCE fit 反而 ΛCDM 有更大偏差 (2.7σ) — 方向性結論取決於用邊個基準。

## 結論

1. **IDCM 9.76e-6 完全 consistent with 所有觀測** ✅ (Cooke limit 0.63σ, S209 0.44σ)
2. **ΛCDM 1.04e-5 都 consistent** ✅
3. **分辨力不足** 🟡 — 模型差距 6.2% vs 觀測誤差 16.5-25.5%
4. Johnson 2025 確認: 現有 ³He/⁴He 量度唔夠精確/唔夠多 → 需要 ~4 個新量度先達 30% 精度
5. **誠實標記:** ³He 係 IDCM 最弱嘅 BBN 測試 — 觀測極難 (³He 得 8.7GHz 自旋翻轉線), 樣本極少 (得 S209 一個乾淨外銀河系量度), post-BBN production 污染嚴重

## 建議未來量度

| 儀器 | 時間線 | 能力 |
|:-----|:------:|:-----|
| ngVLA | 2030s | ³He⁺ 8.7GHz 高靈敏度, 可量度更多 HII 區 |
| JWST | 現役 | HII 區高分辨紅外光譜 (³He 同位素位移) |
| ELT/CRIRES+ | 現役 | 更遠恆星視線 ³Heⁱ* 吸收 |
| DLA ³He | 長期目標 | 需要極高 S/N, 未有成功案例 |

**分辨所需:** ³He/H 直接量度誤差 <3% (目前 16-26%)。若 ngVLA 將 S209 類量度精度提升至 ~5%, 仍差 2σ 分辨所需 (~3%)。需要量度誤差 <3% 先可以分辨 6% 差距 — 2030s 末有望。

## 狀態

- [x] 文獻搜索 (Cooke 2022, Johnson 2025, Balser & Bania 2018, Bania & Balser 2020)
- [x] 最新上限/測量 + 誤差
- [x] 分辨力分析
- [x] 結論 + 建議未來量度
- [x] 🟡 觀測分辨唔到 — 已誠實記錄

*分析: scripts/01_resolution_analysis.py*
*日期: 2026-08-20*

## Sources

[1] https://arxiv.org/abs/2203.11256 — Cooke et al. 2022, Primordial helium-3 redux (ApJ)
[2] https://arxiv.org/abs/2510.08689 — Johnson, Weller & Cooke 2025, Metals vs Non-metals (AAS)
[3] https://arxiv.org/abs/1810.09422 — Balser & Bania 2018, GBT 3He+: HII Regions (AJ)
[4] https://arxiv.org/abs/2012.11707 — Bania & Balser 2020, GBT 3He+: Planetary Nebulae (ApJ)
[5] https://arxiv.org/abs/astro-ph/0511504 — Balser et al. 2006, Detection of 3He+ in PN (ApJ)
