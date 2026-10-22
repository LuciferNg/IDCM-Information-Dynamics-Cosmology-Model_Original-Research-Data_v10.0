# O26-G3 測試計劃 — B-mode 偏振對齊 (完整嚴謹版)

> **日期**: 2026-08-21
> **狀態**: 🔄 進行中 (等待 2GB map 下載 ~60 min)
> **原則**: 不取巧不加速，時間不是問題，嚴謹性比速度重要 (user.md 已記錄)

---

## 數據

**完整 Planck SMICA IQU 2048 full map**:
- URL: `https://irsa.ipac.caltech.edu/data/Planck/release_3/all-sky-maps/maps/component-maps/cmb/COM_CMB_IQU-smica_2048_R3.00_full.fits`
- 大小: 2,013,312,960 bytes (2.0 GB)
- nside: 2048 (50M pixels × 3 fields I/Q/U)
- 來源: Planck 2018 Release 3 (PR3), SMICA component-separated CMB

**唔用**:
- ❌ 1024 降採樣版本 (冇官方)
- ❌ WMAP 代替 (唔同儀器, 唔係 CMB-only)
- ❌ partial download (唔完整)
- ✅ 完整 2048 full map

## 測試方法 (5 步)

### 1. 節點 Q/U 提取
- 60 個 A₅ 節點 (a5_nodes.txt) → `hp.ang2pix(2048, ...)` → 讀 Q/U
- 偏振角 ψ = 0.5·atan2(U, Q) mod 180°
- 偏振強度 P = √(Q²+U²)

### 2. 偏振角 vs 對徑軸幾何
- 對徑軸: RA=328.2825°, Dec=+18.0° (r₀ 軸)
- 每節點: 軸喺切平面投影角 vs 偏振角差 (0-90°)
- 期望: random 45°; 全息預測: 接近 0° (對齊)

### 3. 對徑對偏振角差
- 30 對徑對: Δψ = |ψ_i − ψ_j| mod 90°
- 期望: random 45°; 全息: 對徑對偏振相關
- Permutation test vs 隨機對

### 4. 偏振角 vs k 值
- k=0/1/2 組嘅 ψ 分佈同 P 強度
- 全息預測: k=0 (無阻挫) 偏振最乾淨 (P 最大/ψ 最一致)

### 5. 全 map EB 交叉譜 (cosmic birefringence)
- nside=256 降採樣 (ℓ<170 足夠) — 注意: 呢個係「分析降採樣」唔係「數據替代」
- EB cross-spectrum → β 估計
- 對照文獻: β = 0.277°±0.057° (ACT+Planck joint 2026)

### 6. Monte Carlo null
- 1000 次隨機 shuffle ψ → mean Δψ_axis 分佈
- p = 觀察值嘅百分位

## 判決標準

| 測試 | 全息預測 | Null 期望 | 判決 |
|:---|:---|:---|:---|
| 2. 軸投影角差 | mean ≈ 0° | 45° | <35° = 有對齊 |
| 3. 對徑對 Δψ | mean ≈ 0° | 45° | <35° + p<0.05 |
| 4. k=0 P 最大 | P_k0 >> P_k2 | 相等 | p<0.05 |
| 5. EB → β | β≈0.3° | 0° | 對照文獻 |

## 誠實限制

1. PR3 SMICA 偏振有系統誤差 (polarimeter calibration)
2. ψ 係 180° 模 (偏振無方向) — 對齊測試只測 0-90°
3. 60 節點小樣本 — 統計力有限
4. EB 譜嘅 β 同「軸對齊」係兩個獨立測試
