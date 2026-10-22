# DESI DR2 BAO 補充數據 — 來源與校驗 (provenance)

## 下載

- 論文: DESI Collaboration et al. 2025, "DESI DR2 Results II: Measurement of Baryon Acoustic
  Oscillations and Cosmological Constraints", Phys. Rev. D (in press), arXiv:2503.14738
- Zenodo record: **`10.5281/zenodo.16644577`**
- 檔案: `dr2-bao-zenodo.zip`
- URL: `https://zenodo.org/api/records/16644577/files/dr2-bao-zenodo.zip/content`
- 官方 size: **1,306,284,840 bytes**
- 官方 checksum (md5): **`425623648b4b12515fa1943a5857fd46`**
- 下載日期: 2026-09-28
- **校驗結果: size 完全一致 + md5 完全一致 ✅**（8 路並行 range 分塊下載 + 續傳 + 拼接）

⚠️ 下載過程記錄（供後人）: 第一次並行下載報「100% of remaining」但**4/8 個 part 短咗**
（server 提早斷流被誤判為完成）。教訓: 完成度只可由 `stat()` 得出 + 必須驗官方 checksum。
下載工具唔入 repo（放 `/tmp/desi_dr2/pardl2.py`）。

## 本目錄收錄（我哋要用嘅子集，唔收 1.3 GB 的 `cosmology_chains.zip`）

| 檔案 | 內容 |
|:--|:--|
| `multipoles_<tracer>_data.txt` | **圖 5 數據**: `s  xi_0  xi_0_err  xi_2  xi_2_err`，23 點，s = 62.04..150.02，Δs ≈ 3.998 h⁻¹Mpc，8 個 tracer |
| `multipoles_<tracer>_theory.txt` | 圖 5 嘅 DESI 最佳擬合 ΛCDM+BAO 模型曲線 `s  xi_0  xi_2`（同一 s 網格） |
| `DESI_DR2_alpha_{DM_over_rs,DH_over_rs,DV_over_rs,DM_over_DH}.txt` | 官方 **DR2 BAO α 量測**（6 個 z 有效 bin，`z alpha alpha_err`） |
| `DESIY1_bao_compilation.csv`, `DESIY3_bao_compilation.csv` | 官方 Y1 / Y3 BAO 編纂表 |
| `DESI_DR2_Readme.md` | Zenodo 原始 README（目錄結構 + 模型/數據集命名字典） |

**未收錄**: `cosmology_chains.zip`（1.3 GB，MCMC chains，共 186 個 entry 中嘅大頭）；
`figure1/2/3/4/6/12` 其餘檔案（星系 n(z)、圖 2 嘅星系座標 npz、圖 12 嘅 violin 數據）。
需要時由上面 URL 重新下載（md5 校驗）。

## ⚠️ 用呢批數據嘅已知限制（唔可以隱瞞）

1. **冇協方差矩陣**。圖 5 release 只提供**對角誤差**（`xi_0_err`）。DR1 側我哋有官方 RascalC
   協方差（135×135），所以 DR1 用**相關 χ²**、DR2 只可以用**對角 χ²**。兩者**唔可以直接比
   p 值**——本項目嘅處理: 用同一統計量（Δχ²）並**同窗比較**（見 script 08 §E），並明文標註差異。
   🟡 可行後續: 圖 2 嘅 `fig2_*_ntile.npz` 係**星系座標**（x,y,z，唔係分區 ξ），所以暫時冇得
   由 n-tile 建 jackknife 協方差。
2. **s 窗口由 62 h⁻¹Mpc 開始**（BAO 擬合區間），唔似 DR1 由 2.99 開始。所以 DR2 嘅
   bin-Nyquist 限制（n_max = 9.59 @ Δs=4）**唔係**主要障礙，主要障礙係**窗口起點**剔走咗
   s < 62 嘅低階節點。
3. s 網格中心同 DR1 **差 ~0.95 h⁻¹Mpc**（DR1: 62.99；DR2: 62.04）—— 分箱平均嘅 s 唔完全一樣，
   做 DR1↔DR2 對照時要同窗（用各自 s 網格評估模板）。
