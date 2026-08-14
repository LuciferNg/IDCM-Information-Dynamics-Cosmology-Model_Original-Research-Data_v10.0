# IDCM v10.0 — 共震點宇宙學

**Information Dynamics Cosmology Model — 10th Generation**

K_Chain 44 個模式之間的共震點 (beat frequency) 經 CY₃(36,98) 幾何投影激化為物質與 CMB。

## 核心假設

> 物質 = K_Chain 44 個頻率之間嘅共震點，經 CY₃ 幾何投影激化

## 研究路線

1. **K_Chain 44 個模式** — 離散 Laplacian 本徵值 γₙ=4sin²(πn/88)
2. **946 個 beat frequency** — 44×43/2 對組合，物質 = 共振態
3. **CY₃(36,98) 投影** — 134×946 選擇律投影算子
4. **Z₃ Orbifold** — 36→12 維不變子空間
5. **WDVV 方程求解** — 三重相交張量，11 正 + 1 零個本徵值
6. **SM 質量盲測** — 5/8 粒子的質量預測 < 1% 誤差
7. **CKM 矩陣** — 從投影矩陣推導（待改進）

## 目錄結構

```
IDCM-v10.0/
├── README.md                    # 項目說明
├── src/
│   ├── kchain_wave_params.py    # 44 模式波參數
│   ├── beat_frequencies.py      # Beat 分析 (已凍結)
│   ├── projection_operator.py   # 134×946 投影算子
│   ├── orbifold_projection.py   # Z₃ orbifold 概念
│   ├── derive_dijk.py           # 三重約束推導
│   ├── derive_dijk_wdvv_solver.py  # 36D WDVV 求解
│   ├── hybrid_wdvv_solver.py    # 混合優化 (AdamW+L-BFGS)
│   ├── final_fine_tune.py       # 最後微雕
│   ├── final_blind_prediction.py # 盲測驗證
│   ├── self_consistent_projection.py  # 自洽投影矩陣
│   └── ckm_computation.py       # CKM 計算
├── data/
│   ├── eigenvalues_final.npy    # 最終本徵值
│   ├── final_spectrum.txt       # 本徵值譜文字
│   ├── final_blind_prediction.txt   # 盲測結果
│   ├── ckm_self_consistent.txt  # CKM 結果
│   └── d_tensor_final.npy       # 最終 d_{ijk}
└── docs/
    ├── research_record.md       # 完整研究記錄
    └── research_direction.md    # 方向調整記錄
```

## 基礎常數

| 常數 | 值 | 來源 |
|:----|:--|:-----|
| K_Chain 環周長 R_H | 4129.94 Mpc | D_app(∞) |
| Site 數 N_d | 44 | K_Chain 結構 |
| K_Tree 層數 M | 33 | MERA 結構 |
| CY₃(36,98) | h¹¹=36, h²¹=98 | Calabi-Yau 拓撲 |
| φ | (1+√5)/2 | 代數結構 |
| λ_sync | 294.88 Mpc | SYNC 模式 |
| BAO | 147.44 Mpc | λ_sync/2 |
| H₀ | 72.59 km/s/Mpc | D_app 校準 |

## 盲測結果摘要

| 粒子 | 預測值 | PDG | 誤差 |
|:----|:------|:----|:----:|
| Top | 172.760 GeV | 172.760 GeV | 0.00% ✅ |
| Bottom | 4.188 GeV | 4.180 GeV | 0.20% ✅ |
| Tau | 1.784 GeV | 1.777 GeV | 0.39% ✅ |
| Charm | 1.270 GeV | 1.270 GeV | 0.00% ✅ |
| Strange | 93.297 MeV | 93.400 MeV | 0.11% ✅ |
| Muon | 105.939 MeV | 105.658 MeV | 0.27% ✅ |
| Down | 4.659 MeV | 4.670 MeV | 0.25% ✅ |
| Up | 1.706 MeV | 2.160 MeV | 21.01% ⚠️ |
| ν_τ | 1.9e-10 eV | ~1.8e4 eV | 100% ❌ |

## 未解決問題

- CKM 角：投影方法未重現 PDG（Cabibbo 角: 0° vs 13.04°）
- 中微子質量：Seesaw 機制需要 M_R 推導
- Up 夸克質量：21% 誤差，偏離盲測 <1% 精度
- CY₃(36,98) 真實相交數未知