# IDCM 再電離研究 — 外部數據來源完整參考

## 總覽

本文件記錄所有可用於 IDCM 再電離問題驗證嘅外部天文觀測數據來源。
除咗已下載嘅 JADES DR4、CEERS DR1、DESI DR1/DR2、Planck 2018 之外，
以下五大數據來源可進一步納入分析框架。

---

## 1. Subaru HSC 窄頻巡天數據

### 基本資料
| 項目 | 內容 |
|:----|:-----|
| 望遠鏡 | Subaru 8.2m (Hawaii) |
| 儀器 | Hyper Suprime-Cam (HSC) |
| 天區 | ~300 deg² (HSC SSP Wide layer) |
| 濾鏡 | NB921 (Lyα @ z≈6.6), NB101 (Lyα @ z≈7.3) |
| 極限星等 | NB921 ≈ 25.5 mag, NB101 ≈ 25.0 mag |
| LAE 樣本量 | ~1000+ (SILVERRUSH 計劃) |

### 應用場景
- **大樣本統計：** HSC 窄頻巡天可提供 ~1000+ LAE 樣本，遠超 JWST 小視場深場
- **數目密度測試：** 檢驗 N(z) 嘅大尺度行為，彌補 CEERS/JADES 嘅統計偏差
- **空間分佈：** 大天區可檢測 LAE 嘅大尺度成團性（clustering），驗證 K_Chain 諧波結構

### 關鍵論文
| 參考 | 內容 |
|:----|:------|
| SILVERRUSH (Konno+2018) | z≈6.6 LAE 嘅 1,000+ 樣本，光度函數 |
| SILVERRUSH 2 (Inoue+2018) | z≈7.3 LAE 樣本 |
| SILVERRUSH 7 (Kikuta+2023) | LAE 大尺度成團性分析 |

### 下載方式
```
HSC SSP Public Data Release:
  https://hsc-release.mtk.nao.ac.jp/
  
SILVERRUSH LAE 目錄（透過 arXiv 補充材料）:
  https://arxiv.org/abs/1804.02453 (SILVERRUSH)
  https://arxiv.org/abs/2209.09035 (SILVERRUSH 2)
  
curl 下載（ADS）:
  curl -sL -A 'Mozilla/5.0' -o silverrush_lae_catalog.fits '<URL>'
```

### IDCM 測試
- **N(z) 斜率測試：** HSC 大樣本可將 ln N(z) vs ln(1+z) 擬合誤差降至 <0.1
- **成團性測試：** LAE 嘅角相關函數 w(θ) 應該顯示 K_Chain 諧波間距

---

## 2. ALMA 檔案館數據

### 基本資料
| 項目 | 內容 |
|:----|:-----|
| 望遠鏡 | ALMA 66 天線 (Chile) |
| 波段 | Band 3-10 (84-950 GHz) |
| 關鍵譜線 | [CII] 158μm, [OIII] 88μm, [OIII] 52μm, 塵埃連續譜 |
| 解析度 | 0.1"-1.0" |
| 紅移覆蓋 | z≈5-10 ([CII] 喺 Band 7) |

### 應用場景
- **ISM 物理驗證：** 直接測量高z 星系嘅氣體動力學、金屬豐度、塵埃含量
- **獨立於光學紅移：** [CII] 158μm 提供與 Lyα 獨立嘅紅移系統
- **星系形態：** 高解析度成像可揭示高z 星系嘅內部結構

### 關鍵數據集
| 程式 | PI | 內容 |
|:----|:---|:------|
| 2018.1.00055.S | R. Bouwens | z≈7-9 星系 [CII] 觀測 |
| 2019.1.01676.S | F. Walter | ALPINE 計劃 (z≈4-6 [CII]) |
| 2021.1.00495.S | S. Fujimoto | REBELS 計劃 (z≈7-9 [CII]) |

### 下載方式
```
ALMA Archive:
  https://almascience.eso.org/aq/
  
ALMA Science Archive Query:
  curl -sL 'https://almascience.eso.org/archive-tap/...' -o alma_data.xml
  
Via astroquery:
  from astroquery.alma import Alma
  tables = Alma.query_object('GOODS-S')
```

### IDCM 測試
- **[CII]-Lyα 偏移驗證：** 如果 GP trough 係結構閾值而非 IGM 中性化，[CII]-Lyα 速度偏移嘅 z 演化應該呈現離散跳躍
- **金屬豐度獨立測量：** 與 JWST 嘅 O3N2 金屬豐度交叉驗證

---

## 3. HST CANDELS 與經典深場數據

### 基本資料
| 項目 | 內容 |
|:----|:-----|
| 計劃 | CANDELS (Cosmic Assembly Near-IR Deep Extragalactic Legacy Survey) |
| 天區 | GOODS-S, GOODS-N, UDS, EGS, COSMOS (~800 arcmin²) |
| 波段 | F435W, F606W, F775W, F850LP, F105W, F125W, F160W |
| 深度 | H~27-28 mag (5σ) |
| 星系數 | ~200,000+ |

### 應用場景
- **多波段光度補充：** HST 光學-近紅外覆蓋與 JWST 中紅外重疊，可建構完整 SED
- **低z 污染排除：** HST 嘅 5 個光學波段可以有效識別 z<3 嘅低z 污染源
- **光度函數基線：** HST 嘅 z≈4-8 光度函數（Bouwens+2015, Finkelstein+2015）可與 JWST 結果交叉比對

### 關鍵論文
| 參考 | 內容 |
|:----|:------|
| Bouwens+2015 | HST z≈4-10 光度函數 |
| Finkelstein+2015 | CANDELS z≈4-8 光度函數 |
| Oesch+2016 | HST z≈11 星系候選體 |

### 下載方式
```
CANDELS 官方目錄:
  https://candels.ucolick.org/data_access/CANDELS_catalogs.html
  
3D-HST (HST grism) 目錄:
  https://3dhst.research.yale.edu/Data.php
  
curl 下載:
  curl -sL -A 'Mozilla/5.0' \
    -o candels_goodss_catalog.fits \
    'https://candels.ucolick.org/data/.../candels_catalog.fits'
```

### IDCM 測試
- **光度函數 LF 斜率演化：** IDCM 預測 LF 嘅 characteristic magnitude M* 隨 ℓ 線性演化（非 ΛCDM 嘅時間演化）
- **UV 光度函數驗證：** 比較 HST vs JWST 嘅 LF，檢驗 photometric redshift 系統誤差

---

## 4. 低頻射電干涉陣列數據（LOFAR, MWA, HERA）

### 基本資料
| 望遠鏡 | 頻率範圍 | 紅移範圍 | 當前靈敏度 | 目標靈敏度 |
|:------|:--------:|:--------:|:----------:|:----------:|
| **LOFAR** | 110-190 MHz | z≈6.5-12 | Δ²< (10 mK)² | Δ²< (1 mK)² |
| **MWA** | 80-300 MHz | z≈4-16 | Δ²< (100 mK)² | Δ²< (10 mK)² |
| **HERA** | 50-250 MHz | z≈5-27 | Δ²< (30 mK)² | Δ²< (1 mK)² |
| **SKA-Low** (未來) | 50-350 MHz | z≈3-27 | — | Δ²< (0.1 mK)² |

### 應用場景
- **k-space 功率譜上限：** 目前所有陣列都只提供上限約束，但係 IDCM 嘅等距諧波預測可以直接同呢啲上限比較
- **P(k) 形狀測試：** 即使未檢測到諧波尖峰，P(k) 嘅整體形狀（斜率、特徵尺度）都可分辨 ΛCDM vs IDCM
- **紅移演化：** 唔同陣列覆蓋唔同紅移範圍，可測試諧波間距嘅紅移獨立性

### 關鍵論文
| 參考 | 內容 |
|:----|:------|
| HERA Collaboration 2023 | HERA Phase I 上限 @ z=7.9 |
| LOFAR 2021 | LOFAR 上限 @ z≈8.5 |
| MWA 2020 | MWA 上限 @ z≈6.5-8.7 |

### 數據獲取方式
```
LOFAR EoR 數據:
  https://lofar-surveys.org/eorss.html
  
HERA 數據:
  https://reionization.org/data/
  
MWA 數據:
  https://www.mwatelescope.org/data
```

### IDCM 測試
- **Δk = 0.0213 h/Mpc 檢測：** 目前 LOFAR/HERA 嘅 k 範圍 (0.05-1.0 h/Mpc) 可以覆蓋 n≥3 嘅諧波
- **預期檢測時間：** HERA Phase II 同 SKA-Low 將喺 k=0.02-0.2 h/Mpc 範圍內達到 mK 靈敏度

---

## 5. Spitzer Space Telescope 檔案數據 (SHA)

### 基本資料
| 項目 | 內容 |
|:----|:-----|
| 儀器 | IRAC (Infrared Array Camera) |
| 波段 | 3.6μm (Channel 1), 4.5μm (Channel 2) |
| 計劃 | S-CANDELS, GREATS, ICDERS |
| 深度 | [3.6]~26-27 mag, [4.5]~26-27 mag |
| 天區 | 與 HST/JWST 深場重疊 |

### 應用場景
- **恆星質量測定：** 3.6/4.5μm 係高z 星系嘅 rest-frame 光學/近紅外，可直接測量恆星質量
- **低z 污染排除：** 低z 橢圓星系喺 3.6/4.5μm 有強烈嘅 Balmer break 特徵，可與高z 星系區分
- **活躍星系核 (AGN) 識別：** 4.5μm 超出可用於識別 AGN

### 關鍵論文
| 參考 | 內容 |
|:----|:------|
| Ashby+2015 | S-CANDELS 目錄 |
| Stefanon+2017 | GREATS (Spitzer Great Observatories) |
| Roberts-Borsani+2024 | ICDERS (JWST + Spitzer 交叉比對) |

### 下載方式
```
Spitzer Heritage Archive (SHA):
  https://sha.ipac.caltech.edu/
  
IRSA (Infrared Science Archive):
  https://irsa.ipac.caltech.edu/
  
curl 下載:
  curl -sL -A 'Mozilla/5.0' \
    -o spitzer_catalog.fits \
    'https://irsa.ipac.caltech.edu/.../spitzer_catalog.fits'
```

### IDCM 測試
- **恆星質量函數：** IDCM 預測恆星質量函數嘅演化由 K_Tree projection 主導，非時間演化
- **UV-光學顏色：** 高z 星系嘅 rest-frame UV 顏色（β slope）應由結構參數決定，非星族年齡

---

## 數據來源優先級

| 優先級 | 數據源 | 用途 | 可立即下載？ |
|:------:|:------|:-----|:-----------:|
| **1** | Subaru HSC SILVERRUSH | LAE 大樣本 N(z) 斜率 | 🟡 需從 arXiv 下載 |
| **2** | HST CANDELS | 光度函數基線交叉比對 | ✅ 公開目錄 |
| **3** | Spitzer SHA | 質量測定 + 低z 污染排除 | ✅ 公開目錄 |
| **4** | HERA/LOFAR 21cm | P(k) 上限比較 | ✅ 公開數據 |
| **5** | ALMA [CII] | ISM 物理獨立驗證 | 🟡 需查詢程式 |

---

## 已下載數據

| 數據 | 大小 | 用途 |
|:----|:---:|:-----|
| `jades_dr4_combined.fits` | 90 MB | 5,190 源光譜目錄 |
| `ceers_dr1_catalog.fits.gz` | 195 MB | 87,345 源光度目錄 |
| `desi_dr1_bao.pdf` | 3.8 MB | BAO 參考 |
| `desi_dr2_lya_bao.pdf` | 2.1 MB | Lyα BAO 參考 |
| `planck_2018_parameters.pdf` | 8.9 MB | τ 參考 |

---

*文檔：IDCM 再電離研究 — 外部數據來源參考*
*框架：IDCM v10.0 (共震點宇宙學)*
*日期：2026-08-15*