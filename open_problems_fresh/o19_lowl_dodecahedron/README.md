# O19 — 低 ℓ 異常 (60° Dodecahedron 尺度)

## 問題陳述

Planck 低 ℓ CMB 有異常：
- **大尺度功率偏低**：ℓ=2 四極功率只有 ΛCDM 預測嘅 ~14%
- **四極/八極對齊**：ℓ=2 同 ℓ=3 喺同一方向 (Axis of Evil)
- **60° 尺度異常**：CMB 低 ℓ 功率谷嘅特徵尺度
- **冷斑**：ℓ≈44 尺度 (已閉合)

IDCM 嘅 A₅ 節點網絡 (60 節點, 邊長 26.09°) 可能解釋呢啲異常。

## 主要發現

### 🔬 發現 1: 60° 異常 = 三角形面角 (新發現!)
- 60° 異常 **唔係** dodecahedron 面距 (63.435°)
- 60° = Rhombicosidodecahedron **三角形面內角** (20 個三角形)
- 球面三角形內角: 61.76° (球面超額 5.28°)
- ⇨ 60° 異常係 A₅ 晶格三角形面嘅幾何印記

### 🔬 發現 2: A₅ 節點場 C_ℓ 交替奇偶模式 ✅
- A₅ 節點場自然抑制 ℓ=2,3,5,7,9 (奇數低 ℓ)
- 增強 ℓ=4,6,8,10 (偶數)
- **測地線羽化閉合**: δ=a/2π=4.15°, ℓ₀=4 → χ²/dof=0.5079, C₂/C₃=0.570

### 🔬 發現 3: 四極-八極對齊 = 結構性投影 ✅
- SO(3) 歐拉角 (γ,α,β) ≈ (144°, 108°, 120°)
  - γ = 144° = 5-fold 對稱軸 (2×72°)
  - α = 108° = 正五邊形內角
  - β = 120° = 3-fold 對稱軸 (360°/3)
- 偏差全部 < 3° → 四極-八極對齊係 A₅ 晶格結構性投影

### 🔬 發現 4: 冷斑同源 ✅
- 冷斑 (ℓ=44) = 單個 A₅ 節點尺度 (a/2π = 4.15°)
- 低 ℓ (ℓ=2-5) = 20 個三角形面集體效應
- ⇨ **同一 A₅ 晶格嘅唔同尺度表現** ✅

## 狀態 (最終閉合)

| 路徑 | 狀態 | 說明 |
|:----|:----:|:-----|
| 1. 60° vs 63.435° | ✅ 閉合 | 60° = 三角形面角, 5.4% 差已解釋 |
| 2. 低 ℓ C_ℓ 預測 | ✅ 閉合 | 測地線羽化 δ=a/2π, ℓ₀=4, χ²/dof=0.51 |
| 3. 四極/八極對齊 | ✅ 閉合 | SO(3)=(144°,108°,120°) 結構性投影 |
| 4. 冷斑連結 | ✅ 閉合 | 同源確立 |

## 檔案結構

```
o19_lowl_dodecahedron/
├── SESSION_START.md          # Session 啟動文件
├── 01_problem_record.md      # 問題記錄 (含推導時序索引)
├── README.md                 # 本檔案
├── 05_handover.md            # 交接文件
├── final_result.md           # 最終結論 (RESULT_TEMPLATE 格式)
├── scripts/
│   ├── 01_a5_node_analysis.py    # 基礎分析 (路徑 1-4 初步)
│   ├── 02_deep_analysis.py       # 深度分析 + Planck 對比
│   ├── 03_master_closure.py      # Master 閉合管線 (O19-A/B)
│   ├── 03_planck_comparison.py   # Planck 2018 低 ℓ 定量比較
│   ├── 04_voronoi_closure.py     # Voronoi 連續分塊
│   ├── 05_final_closure.py       # 最終定量閉合
│   ├── 06_feathering_closure.py  # 測地線羽化 (最終閉合)
│   ├── 99_verify.py              # 23/23 驗證
│   ├── 99_audit.py               # 85 項全面審計
│   └── 99_doc_audit.py           # 文檔內容獨立核對
└── data/
    ├── a5_nodes.txt              # 60 個 A₅ 節點 (RA, Dec)
    ├── cl_feathered.json         # 最終 C_ℓ 譜
    ├── map_feathered.npy         # 羽化溫度場地圖
    ├── alm_matrix.npy            # a_ℓm 矩陣
    ├── rotation_params.json      # SO(3) 旋轉參數
    └── ...                       # 其他中間結果
```

## 引用

- Planck 2018: 1807.06209 (低 ℓ 異常)
- Vielva 2004: astro-ph/0310273 (冷斑)
- Luminet 2003: Nature (Poincaré dodecahedron)
- IDCM 冷斑項目: `main_problems/p4_cmb_cold_spot/`