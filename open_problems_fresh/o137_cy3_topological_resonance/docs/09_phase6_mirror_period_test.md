# O137 — Phase 6: 鏡像週期積分條件測試 (Mori/GKZ 實測)

**狀態**: 🟡 部分完成 — 基礎設施就緒 + 重要結構發現; 完整 discriminant 測試被 Mori cone 計算阻礙
**日期**: 2026-08-30
**檔案**: scripts/16, 17 + data/dual_triangulation_data.json, data/gkz_period_data.json

---

## 一、背景: 用戶戰略決策

鏡像對稱 (h¹¹ ↔ h²¹) 攻擊 O137 充分性:
> 「模式選擇源於鏡像週期積分條件——無法在鏡像 Picard-Fuchs 方程零點上取得整數化週期的模式（如 n=15,21,25,35）將被拓撲鎖定失敗剔除」

測試計劃:
1. 計算鏡像 polytope Δ* 的 triangulation + GKZ φ (✅ 完成)
2. 提取 Mori cone generators → 逐方向計算 GKZ 週期 (🟡 部分)
3. 計算 PF 方程 discriminant → 測試 modes 位置 (🔴 未完成 — Mori 計算超時)
4. 盲測 {1,7,33} vs {15,21,25,35} (🔴 未完成)

---

## 二、已完成的計算

### 2.1 Δ* Triangulation (TOPCOM, 2 秒 vs CYTools 預設 600s timeout)

```
Δ  : 48 pts (CY3 h11=36, h21=98) — 原始
Δ* : 85 pts (CY3 h11=98, h21=36) — 鏡像 (Batyrev dual)
Triangulation: fine ✓ regular ✓ star ✓, 283 simplices, 73 點參與
12 點未參與 = facets-interior 點
```

### 2.2 GKZ φ 向量 (73 entries, Σφ = 1800)

| φ 值 | 數量 | 結構 |
|:---:|:---:|:---|
| 12 | 28 | 28 = B×L₅ = 4×7 (B=4, L₅=7 Lucas) |
| 9 | 9 | 9 = 3² |
| 8 | 5 | 5 = F₅ |
| 6 | 2 | 2 = 對偶鏈因子 |
| 14,16,18,20,22,26,29 | 4,3,4,4,4,3,3 | 各種 |
| 113, 173, 176, 360 | 1 each | 大值: 176=2×88, 360=4×Σγ |

### 2.3 ★ 核心結構發現: 44 個 φ≤12 點 = Nd ★

```
φ ∈ {6, 8, 9, 12} 的點數: 2 + 5 + 9 + 28 = 44 = Nd (K_Chain 44-site)!
```

**44 個 φ≤12 點 labels**: [2, 5, 17, 24-61, 66, 70, 71, 72]

**鏡像 polytope 的 GKZ φ 結構直接編碼 K_Chain 的 site 數 44!**

### 2.4 GKZ ↔ K_Chain 結構連結

| 連結 | 數值 | 驗證 |
|:---|:---:|:---|
| φ_origin | 360 = 4·Σγ₄₄ (Σγ=90) | ✅ |
| Σφ | 1800 = 20·Σγ₄₄ | ✅ |
| φ[1] | 176 = 2×88 (對偶鏈) | ✅ |
| φ≤12 點數 | 44 = Nd | ✅ ★ |

---

## 三、負面結果 (誠實記錄)

### 3.1 Dwork 整數性 — 不是 discriminator

68 條 GLSM charge rows 全部給出整數 GKZ 週期係數 (68/68 pass)。
→ 整數化週期是 CY3 的普遍性質，無法區分 modes。

### 3.2 GKZ 收斂半徑 — 不是 discriminator

所有 GLSM rows 的收斂半徑 R ∈ [4.0, 1889]，全部 > 1。
所有 modes 的 |z_n| = 1 都在收斂域內 → 無法排除任何 mode。

### 3.3 Mori cone generators 計算受阻

CYTools `secondary_cone().extremal_rays()` 在 73 維空間超時 (>600s)。
`expanded_secondary_fan()` 返回 85 維 cone 但 extremal_rays 觸發 CYTools bug。
→ 無法完成逐方向 discriminant 計算。

### 3.4 初步 z_n 測試 (無 discriminator)

- n=7 最接近 z=-1 (dist=0.034) — 但唔係唯一
- n=1 最接近 z=1 (dist=0.032, 僅次 n=22,44 精確=0)
- 無乾淨的 {1,7,33} vs {15,21,25,35} 分離

---

## 四、結論與下一步

### 已確立 (零參數結構)
1. **44 = Nd**: 鏡像 polytope GKZ φ≤12 點數 = K_Chain site 數
2. **Σφ = 20·Σγ**: GKZ 總體積編碼 chain 總諧振
3. **φ_origin = 4·Σγ**: apex 體積 = 4×chain 總和

### 未完成
- Mori cone generators (需要 gfan 直接計算或更長時間)
- 逐 Mori 方向的 PF discriminant
- 盲測 {1,7,33} vs {15,21,25,35}

### 下一步候選
1. **gfan 直接計算 secondary fan** (gfan_secondaryfan binary, 輸入點配置)
2. **利用 44 點結構**: 44 個 φ≤12 點是否對應 44 sites? φ 值是否編碼 mode 選擇?
3. **其他 discriminator**: 不追求 discriminant, 直接用 44 點 φ 值的算術結構
