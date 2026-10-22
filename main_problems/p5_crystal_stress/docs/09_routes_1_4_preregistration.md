# 路線 1 + 4 預註冊 (2026-10-17)

> 本文件記錄剩餘兩條路線嘅**預註冊**：測試規格已凍結、等外部數據。
> 全部由既有結構推導 (零新常數)；冇執行所需數據之前唔會動手。

---

## 路線 1 — CMB 偏振宇稱違反: edge-band 預註冊 ✅

**預言** (p12 data/polarization_parity.json): 偏振旋轉 ~**1e-5 rad**,
局限喺 32 條阻挫邊 ±2.0° 帶 (Ising 位元 / 相位滑移邊界, O7)。

**證偽條件**: edge bands 冇偏振異常 (旋轉統計 = control) ⟹ 證偽。

### 預註冊產物 (scripts/19_edge_band_prereg.py)

| 項 | 值 |
|:---|:---|
| 邊源 | `p4_cmb_cold_spot/data/frustration_edges.txt` (32 邊, 端點 RA/Dec 已知) |
| 網格 | Nside=128 (~0.46°/px), **凍結** |
| band 半徑 | **r_band = 2.0°** (凍結; 對應節點核心真空最佳尺度 ~2.5°) |
| control | 離所有邊/節點 > 5°, area-matched (seed 20261017, 抽至同 band 面積) |
| band 覆蓋 | **8.73% 天空** = 17,162 px; 每邊 ~112.5 deg² |
| ML 發現 | ★ **32 條阻挫邊全部等長 26.09°** (規則 A5 結構) |
| 檔 | `data/edge_band_mask_20261017.json` (規格+端點) + `.npz` (band/control mask) |

### 敏感度 / 狀態
- CMB-S4 0.01° ≈ 1.7e-4 rad — 預言 1e-5 rad 需 32 邊 stacking (p12 json).
- 現有 Planck 偏振數據 noise 遠超預言 ⇒ 而家執行只會得 noise 主導 null (道德上唔算測試).
- 🔴 **等 CMB-S4 (2029+) / SO (2027+) — mask 已凍結, 數據到埗即測**.

---

## 路線 4 — Euclid 寬場 60 節點位置檢驗 🔴

> 原「待裁決」歸屬問題 (P5 vs cold-spot O-series): 60 節點 = A5 crystal nodes,
> 係 **P5 核心物件** → 本路線歸屬 P5；cold-spot O-series lineage 以 cross-ref 註記。
> 最終確認留用戶。

### 目標
60 A₅ 節點位置嘅星系團核心真空 (同 DESI 5th 一樣嘅檢驗) — **目標 5σ** (Euclid 星系團目錄)。

### 數據時間線 (2026-10-17 調查)
- **Euclid Q1 (2025-03)**: ~98 deg² — 太細, 覆蓋唔到 60 節點統計
- **Euclid DR1 Foundation: 2026-11-12** (還有 ~4 週)
- Euclid DR1 Complete: mid-2027; DR4: 2029-03

### 測試規格 (預註冊, script 17 machinery 直接重用)
1. 輸入: Euclid DR1 cluster catalog (RA/Dec; Q1 已示範 cluster workflow)
2. null: **scramble RA, keep dec** (footprint-safe — Euclid 亦係部分天區)
3. radii 掃描 2.5-8.5° (同 DESI), best z / clamp p
4. Fisher 合併: 5 目錄 + Euclid → **Fisher6** (target >5σ)
5. 對照: DESI CluMPR (2026-10-17 已做) + 4 舊目錄

### 狀態
🔴 **等 Euclid DR1 (2026-11-12)** — 規格就緒, 數據到埗即跑 (script 17 同款)。

---

## 總結 (2026-10-17 全部路線狀態)

| 路線 | 狀態 | 下一步 |
|:---|:---|:---|
| 1 CMB 偏振宇稱 | ✅ 預註冊 (mask 凍結) | 🔴 CMB-S4/SO 數據 |
| 2 DESI 第 5 重 | ✅ 已執行 (Fisher5=4.69σ) | — |
| 3 盲測 | ✅ 第一輪 (P0-P2 全中, N<20) | 🔴 AugerPrime N≥20 |
| 4 Euclid 60 節點 | ✅ 預註冊 (規格凍結) | 🔴 Euclid DR1 (2026-11-12) |
| P9′ 節點源模型 | 🔴 | 🔴 AugerPrime >5σ (2035) |