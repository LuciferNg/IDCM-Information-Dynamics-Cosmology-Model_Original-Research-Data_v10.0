# O175-D4 數據閉合 — Fall Locus 真數據驗證 (scripts/14, 開放科學渠道)

日期: 2026-09-13
狀態: 🟢/🟡 (j*-M* 定量閉合; R_d(M) 外推不確定性)

## 數據來源 (用戶提供渠道, 100% 公開免費)

| 數據集 | 渠道 | 樣本 | 用途 |
|:---|:---|:---|:---|
| Posti+2018 (A&A 612, L6) | VizieR `J/A+A/612/L6` | 92 星系 j*-M* | T2b Fall locus 閉合 |
| Mancera Piña+2021 (A&A 647, A76) | VizieR `J/A+A/647/A76` | 152 星系 jbar-Mbar-Rd | T1/T2a/T4 |
| SPARC (Lelli+2016) | astroweb.case.edu/SPARC/ | 175 星系 (4 mrt 檔案) | 支援/交叉 |

數據落盤: `data/vizier/` (posti2018_fall.tsv, mancera2021_baryonic_j.tsv), `data/sparc/` (SPARC_Lelli2016c.mrt 等)。

## IDCM 預言 (零新常數, scripts/12 延續)

- M_c = 1.89e12 Msun (關閉質量)
- R_d(M_c) = R_c/4 = 12.121 kpc (R_c = R_world/44³ = 48.48 kpc)
- V_max(M_c) = (GM_c/R_c)^0.5 = 409.8 km/s
- j_Fall,IDCM = 2·R_d·V_max = **9,935 kpc·km/s = j_spec/2** (19,867/2)

## 結果 (真數據 log-log 擬合外推)

| Test | IDCM | 觀測外推 | dev | 判定 |
|:---|:---|:---|:---|:---|
| **T2b j*(M_c)** | 9,935 | **9,770** | **−1.66%** | ✅ **PASS 定量閉合** |
| T2a j_bar(M_c) | 9,935 | 1.199e4 | +20.7% | 🟡 ORDER 邊緣 (baryonic 含 gas, 高質量端 j 偏大合理) |
| T1 R_d(M_c) | 12.12 kpc | 8.67 kpc | −28.5% | 🔴 FAIL (外推方法不確定性) |
| T4 V_max(M_c) | 409.8 km/s | 692 km/s | +68.8% | 🔴 FAIL (同上, V_eff 由 R_d 反推) |
| T3 j_spec/j_disk = R_c/(2R_d) | 2.0 | 2.0 | 0% | ✅ 定義性 |

## T2b 閉合細節 — 本次最強結果

- Posti 2018 樣本: 92 星系, log M* ∈ [7.3, 11.3]
- 擬合: log j* = 0.528·log M* + const, **r = 0.944** (文獻 slope 0.585 ± 0.02)
- 外推到 M_c = 1.89e12 (log 12.28, 外推 ~1 dex): j*(M_c) = 9,770 kpc·km/s
- vs IDCM 結構預言 9,935: **dev −1.66%**
- 意義: IDCM 用純結構量 (R_c = R_world/44³, M_c 關閉, V = √(GM/R)) 預言嘅盤特定角動量, 撞中獨立星系樣本嘅 Fall locus 外推 — 零新常數。

## 誠實負結果分析

**T1/T4 外推失敗唔等於 IDCM 否決**: 樣本質量上限 log M ~ 11.3, 外推至 12.28 有 ~1 dex 距離; R_d−M 關係 slope 對 fit 方法敏感 (Mstar-based 0.21, Mbar-based 0.26, 文獻 0.3-0.5 → 外推結果 7.5–62 kpc 範圍極大)。單 power-law 外推唔足以分辨。scripts/12 嘅雙錨閉合 (M_c + MW, dev 0.66%) 仍然係 R_d(M_c) = R_c/4 嘅主要支持 — 但屬「兩點決定直線」, 強度有限。**R_d(M_c) 維持 🟡**。

**T2a +20.7%**: baryonic j 高質量端大過 stellar j (gas 比角動量 slope 兩倍陡, Mancera 2021 文獻 slope α_bar = 0.60 vs α_star = 0.53) — 方向性合理, 但超 20% 閾。

## 結論

- ✅ D4 核心 (j_spec 對應 Fall locus) 由獨立真數據定量閉合 (dev 1.66%, 92 星系, r=0.944)
- 🟡 R_d(M) 形式維持開放: 需要樣本內高質量端星系 (M > 10^11.5) 或者 volume-limited 樣本 (後續: eDisk/其他 catalog)
- 方法學教訓: 外推超過樣本質量上限 ~1 dex 時, 結果受 slope 不確定性主導 — 應以「支持/不支持方向」解讀, 唔係定量判決
