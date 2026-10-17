# Record 24 — 矯正版 T1 終判: absorber 修正後 IDCM 對稱仍拒 (2026-10-17)

狀態: 🔴 **T1 終判: 即使 fit self-absorption, IDCM 對稱雙峰都唔支持**
      🟢 **Absorber 存在確認** (A Hα ΔAIC −97 / E 驗證 −65.8, 同 Nikopoulos+2026 一致)
Script: `scripts/30_absorber_corrected_t1.py` (data/30_absorber_t1.json)
        `scripts/31_absorber_t1_final.py`
觸發: record 20 T1 (1.68≠1) 被質疑受 absorber 污染 — 矯正: 先 fit absorber
      再判 IDCM 對稱; 官方 paper (Nikopoulos+2026 A&A 710 A136) 確認
      self-absorption 存在 (E: Hα +47/350, Hβ −79/520, 食走 10%/21%)

---

## 1. E 驗證 (script 30 Part A) — pipeline 可重現 paper 嘅 absorber

| 線 | 我哋 fit (G395M) | paper 值 | 判定 |
|:---|:--|:--|:--|
| Hα | depth=0.44, σ_a=185 km/s, dv=−90, ΔAIC **−65.8** | +47 km/s, FWHM 350 | 🟢 absorber 存在 (位置偏移因冇 fit narrow) |
| Hβ | depth=0.16, σ_a=82, dv=−500, ΔAIC +8.6 | −79 km/s, FWHM 520 | 🟡 冇檢出 (Hβ SNR 低 + 冇 narrow component) |

⟹ self-absorption 係真實 (paper 方法獨立確認), 我哋 pipeline 識 fit.

## 2. A (R~2700) — absorber 檢測

| 線 | ΔAIC M4−M0 | absorber | 裁定 |
|:---|:--:|:--|:--|
| Hα | **−97.0** | depth=0.98, σ=183 km/s, dv=**−283 km/s** (藍側!) | 🟢 顯著 absorber |
| Hβ | +4.3 | — | 🔴 冇 |

⟹ **A 兩線受唔同污染** — 舊 T1 ratio (1.68) 確實有 absorber 污染成份.

## 3. 終判 (script 31 Part B): M6 = IDCM 對稱雙峰 × absorber dip

完整模型比較 (A, R~2700):

| 模型 | Hβ ΔAIC | Hα ΔAIC |
|:--|:--:|:--:|
| M0 單峰 (基準) | 0 | 0 |
| M4 單broad+dip | +4.3 | **−97.0** |
| M6 IDCM對稱+dip | +5.0 | −96.4 |
| M1 自由雙峰 | **−15.6** | −97.0 |

- **M6−M4 = +0.7 (Hβ) / +0.6 (Hα)** — 完全無分別
- M6 峰距 d 退化去 **100 km/s** (≪ IDCM 階梯 167-836) — fit 唔出對稱模態對,
  直接退化去單峰+dip
- M1 喺 Hβ 最好 (−15.6, Δv=880) — 但係 record 23 已示 M2 對稱版本 9/10 拒

## 4. 裁定

| 陳述 | 判定 |
|:-----|:----:|
| Absorber (self-absorption) 真實存在 | 🟢 (A Hα −97, E Hα −65.8, paper 一致) |
| Old T1 1.68 受 absorber 污染 | 🟢 (A 兩線污染唔同) |
| **加 absorber 後 IDCM 對稱模態對復活?** | 🔴 **冇** (M6 ≡ M4, d 退化單峰) |
| IDCM 對稱雙峰終判 | 🔴 **拒證** (T3/T1 一致, 修正後依然) |
| broad centroid 紅移 + 藍側吸收 | 🟢 物理圖像: 藍側吸收 dip (−283) + broad 紅移 — 同 P-Cygni/自吸收一致 |

## 5. 綜合 (record 19-24 完整鏈)

```
T3 形態對稱      : 9/10 拒 (M2 ΔAIC)
T1 雙線相等      : A 首測 1.68 唔等; absorber 修正後依然冇對稱模態對
T2 峰距量子化    : 冇大階梯聚集 (mean=120±99)
吸收 channel     : 存在但唔救 IDCM; 藍弱側比假陽性 (窄線z陷阱) 已修正
散射 channel     : 保對稱理論確立
── IDCM 對稱雙峰預言: 五判別全部傾向唔支持 ──
```

- 唯一未測: 高 SNR 全樣本 T1 (A 係唯一 R~2700 雙線光源; n=1)
- 結論: 現有公開最高品質樣本上, IDCM 對稱雙峰解釋 LRD 巴爾末線唔成立;
  證據鏈完整 (pipeline 校準 → forward-model → absorber 修正)

## 6. 教訓

- M4/M6 自由 fit 會爆 (σ→億級, dip 深度爆) — 必須 bounded fit (σ>0,
  depth∈[0,1.5])
- M4 基準要同 M0 比 (單結構對單結構), 唔係同 M1 (形態唔同冇可比性)
- E Hβ 冇檢出 absorber = SNR 限制 + 缺 narrow component — 唔代表 Absorber
  唔存在 (paper 有 narrow 組件 fit)

*文檔: closeout 攻堅 · 矯正版 T1 終判 · 2026-10-17*