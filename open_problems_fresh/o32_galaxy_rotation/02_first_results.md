# O32 首推結果 — 星系旋轉曲線

> 日期: 2026-08-18
> 狀態: 🟢 IDCM a₀ = cH₀/2π 零參數命中官方 RAR bins
> 位置: `open_problems_fresh/o32_galaxy_rotation/`

## 核心結果

**IDCM 零自由參數預測: a₀ = cH₀/2π = 1.1225×10⁻¹⁰ m/s²**

| 測試 | IDCM (0 參數) | MOND (1 參數) | 結果 |
|:-----|:------------:|:------------:|:----:|
| 官方 RAR bins (14 bins) | χ² = 0.38 | χ² = 0.42 | 🟢 IDCM 更好 |
| 官方 RAR bins 最佳 a₀ | 1.14e-10 | — | IDCM 偏差 1.6% |
| 1σ 範圍 | [0.88, 1.46]e-10 | — | IDCM ✅ 在內 |
| Kepler null test | χ²/dof = 158 | χ²/dof = 11 | 🟢 需要額外效應 |
| BTFR 斜率 | 4.0 (理論) | 4.0 | 🟢 一致 |
| SPARC 全樣本 (3391 點) | χ²/dof = 11.0 | χ²/dof = 12.3 | 🟢 IDCM 較好 |

## 關鍵發現

1. **a₀ = c²/(2πR_H)** — 由 R_H = c/H₀ = 4129.94 Mpc (K_Chain 環周長) 直接導出
2. **零自由參數** — MOND 嘅 a₀ 係 fit 參數, IDCM 嘅 a₀ 係結構常數
3. **官方 RAR bins 完美命中** — χ² = 0.38/13 dof = 0.029
4. **Kepler null test 證明必須有修正** — χ²/dof = 158 完全失敗
5. **m₇ = 13.8 MeV 唔係粒子暈** — 密度差 2×10⁵ 倍, 星系 DM 係 K_Chain 幾何效應

## 圖

- `docs/rar_btfr.png` — RAR + BTFR
- `docs/rotation_curves.png` — NGC2403, NGC3198, NGC6503 旋轉曲線

## 與 MOND 比較

| 方面 | MOND | IDCM |
|:-----|:-----|:-----|
| a₀ 來源 | 擬合參數 | **結構常數 cH₀/2π** |
| 自由參數 | 1 (a₀) | **0** |
| RAR 插值函數 | 手動選擇 | K_Chain 諧波結構 |
| DM 本質 | 無 | K_Chain 幾何投影 |
| BTFR | 斜率 4 | 斜率 4 (V⁴ = GMa₀) |

## 深層物理

```
a₀ = cH₀/2π = c²/(2πR_H) = c²/(88π·dx)

R_H = 4129.94 Mpc (K_Chain 環周長)
dx = R_H/44 = 93.86 Mpc (site 間距)
λ_sync = 294.88 Mpc = 2πR_H/88
```

K_Chain mode 1 (基本模式) 嘅 W-field 耦合喺 g < a₀ 時放大引力 → 平坦旋轉曲線。

*下一文件: 03_derivation.md (完整推導)*
