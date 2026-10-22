# O232 docs/03 — R6 裁決：高 z 星系恆星齡 vs ΛCDM 天花板（實測）

> 第三輪產物 2026-10-05。附 `scripts/04`（JADES 真數據）、`data/04_jades_age_ceiling.json`。
> 方法 = scripts/03 之判據：ΛCDM 硬天花板 t_age(z) = A_U − lookback(z)，age > t_age(z) ⟹ ΛCDM 違反。

---

## 0. 結論先行（🟡 R6 數據側，偏 ΛCDM）

**高 z 恆星齡未違反 ΛCDM 天花板；而且上包絡隨 z 單調下降 ⟹ 「與 z 無關嘅年齡包絡」（IDCM『無天花板』之可測形式）被數據拒絕。**

1. `de la Vega+2025`（JADES 2,282 星系，Bagpipes 質量加權齡）：**0/2,282** 中位值超過 t_age(z)；z 分箱上包絡 4.55 → 0.52 Gyr 單調下降，形狀**跟住** t_age(z)。
2. 極端案例 JADES-GS-z14-0（z=14.32，v9 自己嘅例子）：文獻質量加權齡 = **15 Myr（Helton+2024）/ 36 Myr（Carniani+2024）**，只有天花板 287 Myr 嘅 5–12%——**遠低於天花板**。

⚠️ 限制：SED 擬合多數有「星形成須喺 Big Bang 之後」prior（違反會被 prior 壓制）；樣本 z<6（+1 個 z=14），選樣效應（亮選星）影響包絡。⇒ R6 不能定案為 🟢「證實 ΛCDM」，但**否定 IDCM 之 z-無關包絡形式**。

---

## 1. 數據（scripts/04；真數據）

**來源**：`bagpipes_umap_jades_2025.txt`（github alex-delavega/umap_jades_2025；de la Vega et al. 2025，JADES 3<z<6 quiescent 搜尋之母樣本）；N = 2,282，z ∈ [0, 11.31]，無 NaN。質量加權齡 mwa_50/16/84。檢驗用 Planck H0=67.4, Ω_m=0.315（mpmath 積分）。

```
違反: mwa_50 > t_age:   0/2,282 (0%)
      mwa_16 > t_age:   0
      mwa_84 > t_age:   5  (84% 上限越線; prior 壓制區)
z-分箱上包絡 (max mwa_50 / t_age(mid)):
  z∈[0,1):  max 4.55 Gyr   (t=8.59)   z∈[1,2): max 4.15 (t=4.26)
  z∈[2,3):  max 1.86       (t=2.61)   z∈[3,4): max 1.50 (t=1.80)
  z∈[4,5):  max 0.78       (t=1.33)   z∈[5,6): max 0.52 (t=1.04)
  ⟹ 單調下降 = True  (4.55→0.52, 跨 5 箱)
最迫近天花板: z=3.45 星系 mwa_50/t = 0.818;  整體 A50/t: 中位 0.091, p95 0.434, max 0.818
```

**判讀**：ΛCDM 形式（包絡隨 z 下降）與數據一致；「IDCM 無天花板 → 包絡與 z 無關（~常數 ≈ 4.5 Gyr at all z）」形式被拒（高 z 箱最大齡 0.52–1.50 ≪ 4.5）。

## 2. 極端案例 GS-z14-0（文獻，只引用）

| 量 | 值 | 出處 |
|:---|:---|:-----|
| z | 14.32 (+0.08/−0.20) | Carniani+2024 (Nature, arXiv 2405.18485) |
| ΛCDM 天花板 t_age(14.32) | **287 Myr** | scripts/04 積分 |
| mass-weighted age | **~15 Myr** (3–43; BAGPIPES) | Helton+2024 (arXiv 2405.18462) |
| mass-weighted age | ~36 Myr (模型) | Carniani+2024 (A&A 2024, aa50944) |
| ⟹ 年齡 = 天花板 5–12%，餘量 88–95% | — | — |

**判讀**：GS-z14-0 證明「300 Myr 後已有亮星系」，但佢嘅**星齡極年輕**，離天花板一大截——**唔構成 ΛCDM 違反**。

## 3. ⚠️ v9 數據完整性 finding #2 🔴

v9 `verify_young_galaxies.py`（line 103）用 `("JADES-GS-z14-0", 14.32, 0.30, …)`：星齡 0.30 Gyr。
文獻質量加權齡 = 0.015–0.036 Gyr ⇒ **v9 個 0.30 高咗 ~10–20 倍**。
v9 據此示範「0.30 vs t_age=0.287 微超天花板」——該示範**基於錯誤數值**，實質上 GS-z14-0 遠低於天花板。
（本 O 只記錄，不修 v9。連同 scripts/03 之 540 vs 466 Myr，共 2 個 v9 數據完整性 finding。）

## 4. 判決

```
R6 🟡 數據側(偏 ΛCDM):
   ① 0/2,282 中位違反 + GS-z14-0 遠低天花板 ⟹ ΛCDM 天花板在高 z 未被違反
   ② 包絡單調下降 ⟹ IDCM『z-無關包絡/無年齡上限』之可測形式被拒
   ③ 限制: SED prior 壓制違反; z<6 選樣; 數量密度 (number density) 張力另案
```

**對 IDCM 嘅實質意義**：IDCM 並無「星齡」預言（τ 係周長，見 docs/02）——故 ① 唔係 IDCM 之敗績；
但 ② 令 IDCM 若想靠「無天花板」解釋 JWST 高 z 觀測（Labbé 等）失去一個簡單形式——高 z 星系嘅星齡**確實**比低 z 年輕，呢個係 ΛCDM 天花板嘅指紋。
IDCM 若要存活，須以**渲染深度早端截斷（216 Myr, z=17）**自洽解釋「高 z 星系存在但星齡年輕且隨 z 下降」——即 R5 語義問題變成**必須**解決，唔係可選。

## 5. 來源
- 外部：de la Vega+2025（github 目錄）；Helton+2024 (arXiv 2405.18462)；Carniani+2024 (arXiv 2405.18485; A&A 2024 aa50944)。
- IDCM（只引用）：v9 `verify_young_galaxies.py`（GS-z14-0 0.30 Gyr 之錯誤示範）。
- 計算：`scripts/04`（exit 0；全部檢查 PASS 見 logs/04）。