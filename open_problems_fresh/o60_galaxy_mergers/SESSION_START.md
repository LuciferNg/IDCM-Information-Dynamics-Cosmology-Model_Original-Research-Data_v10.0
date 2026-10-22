# O60 記錄 01 — 星系合併歷史與 IDCM 中小尺度自洽性

> 日期: 2026-08-24
> 論文: Massari+2026 (arXiv:2601.18896, Nature Astronomy)
> 主題: HST 發現銀河系早期合併 LKH (12.3 Gyr ago, z>4)

## 觀測事件 (框架無關)

| 量 | 值 | 註 |
|:---|:---:|:---|
| LKH 合併時間 | ~12.3 Gyr ago (z>4) | 比 GSE 早 1.8 Gyr |
| LKH 恆星質量 | ~5×10⁸ M☉ | 與 GSE 相當 |
| LKH 空間 | 內 6 kpc | 12 個 GCs |
| GSE | ~10.5 Gyr ago | Helmi+2018 |
| Sgr | ~6 Gyr ago | 進行中 |
| 最老 GC | 14.48 Gyr (isochrone) | CARMA 相對尺度 |

## IDCM 詮釋

- z = 結構座標 ℓ = log₄(1+z)，LKH z>4 → ℓ>1.16 (K_Tree level 1-2)
- τ = 13.470 Gyr (渲染深度), T_sync = 2πτ = 84.635 Gyr, t_true = 11,100.64 Gyr (N=131)
- 恆星年齡 12-14.5 Gyr ≈ τ 觀察窗 (7.5% 偏差待解釋)
- **質量階梯合併規則 (新發現)**: LKH/GSE/Sgr 全部 d≈4.4 級, MW 當時 d=4.08, 質量比 0.24 吻合論文 0.2-0.3

## 誠實標記 (Inventory)

| 項目 | 狀態 | 說明 |
|:-----|:----:|:-----|
| 質量階梯合併規則 | ✅ 新發現 | d=4 只吸收 d≈4.5-5 級; 可證偽 |
| M31 RAR 內圈 | 🟢 | χ²/dof ≈ 1.0 (零參數) |
| M31 外圈形狀 | 🟡 | 「23% 下跌」可能係 Zhang+2024 Jeans 方法特有; Sofue 只跌 10% |
| 合併時鐘 | 🟢 候選閉合 | LKH→n=7, GSE→n=8, Sgr→n=15, M31盤→n=15; p≈2.8e-4 |
| 衛星系平面 | 🔴 | 垂直 M31 假說否證 (64.3°); 需 O57 |
| M31-MW 軌道 | 🟢 有趣 | 43.5 Gyr ≈ 0.51 T_sync |

## 延伸 (O60a-e)

O60a: M31 外圈形狀判別 (HII region 獨立測量) 🟡 部分推進 (docs/04 方案 A)
O60b: 衛星系平面 VPOS (K_Chain 投影?) 🔴 假說否證, 需 O57
O60c: 本星系群 timing argument 🟡 初步 (43.5 Gyr 軌道週期)
O60d: 合併時鐘機制 🟢 候選閉合 (n 模式共振, 需精密星流年齡)
O60e: 恆星年齡上限 7.5% 偏差 🟡 分析中

## 關鍵文件

- 01_problem_record.md (主記錄)
- docs/02_m31_rar_verification.md (M31 RAR)
- docs/03_merger_mass_ladder.md (質量階梯合併規則)
- docs/04_three_directions.md (三方案推進結果)
- scripts/01-18 (分析 + verifier, 全 PASS)
- data/massari2026_lkh.pdf (原始論文)
- data/m31_rotation_2024.pdf (Zhang+2024)
