# O43-C: 全球 β = 0.277° 嘅方向依賴 — 文獻監測報告

> **狀態**: 🟡 監測中 — 等 LiteBIRD (2029+)
> **日期**: 2026-08-31
> **來源**: O26 衍生 (全息框架未測試項目)

---

## 1. 當前狀態

### 全球 β 測量值

| 測量 | β (deg) | 顯著性 | 來源 |
|:----|:--------:|:------:|:-----|
| WMAP+Planck PR4 | 0.34±0.09 | 3.8σ | Eskilt & Komatsu 2022 |
| ACT DR6 | 0.20±0.08 | 2.5σ | Louis et al. 2025 |
| **ACT+Planck joint** | **0.277±0.057** | **4.8σ** | 2026-08 (IDCM O26 記錄) |

### 方向依賴 (anisotropic birefringence)

| 檢查 | 結果 | 上限 | 來源 |
|:----|:----|:----|:-----|
| Planck PR4 map-space dipole | 冇發現 | — | Eskilt 2022 |
| Planck PR4 tomographic | 冇發現 anisotropy | — | 文獻 |
| ACT DR6 tomographic | 冇發現 anisotropy | — | Louis 2025 |
| LiteBIRD forecast | 全天空 map | σ(β)~0.03° | de la Hoz 2025 |

---

## 2. LiteBIRD 進度 (2026-08 更新)

| 里程碑 | 日期 | 狀態 |
|:------|:----:|:----:|
| KEK 管理變更 | 2024-10 | ✅ 已處理 |
| 重新規劃方案 | 2025-09 | ✅ 評估通過 |
| 任務定義審查 (MDR) | 2026 夏季 | 🔄 進行中 |
| 發射 | ~2029+ | 📅 預計 |
| 運作 | ~2032+ | 📅 預計 |

**LiteBIRD 核心能力**:
- 全天空 CMB 偏振 map (100-400 GHz)
- 可將 isotropic birefringence 誤差降至 σ(β)~0.03° (5-13σ 檢測)
- 可產生全天空雙折射 anisotropy map → 測試方向依賴
- 可區分 dark matter 與 dark energy 嘅 EB 訊號 (reionization peak)

---

## 3. IDCM 預測 (全息框架)

### 全息 β 預測
- 全球 β = 0.277° (4.8σ) — 已確認
- 方向依賴: 如果 β 嚟自全息屏邊界效應，應該有偶極或四極 anisotropy
- 全息屏軸 (r₀ axis: RA 328.28°, Dec +18.00°) 可能係 β 方向性嘅自然軸

### 可證偽預測
1. **零方向依賴**: 如果 LiteBIRD 發現 β 完全 isotropic → 全息解釋困難 (邊界效應應有方向性)
2. **軸對齊**: 如果 β anisotropy 軸對齊 r₀ 軸 (RA 328°, Dec +18°) → 支持全息框架
3. **偶極幅度**: 全息模型預測 dipole amplitude ~β×sin(θ_axis) ≈ 0.28°×sin(θ)

### 與暴脹解釋嘅區分
- 暴脹模型: β 來自 axion-like field → 應有尺度依賴但唔一定方向性
- 全息模型: β 來自邊界條件 → 應有方向性 (軸對齊 A₅ 對徑結構)

---

## 4. 現有數據嘅限制

| 限制 | 說明 |
|:----|:------|
| Planck PR4 靈敏度不足 | 單一 experiment 誤差 ~0.09°，不足以檢測 dipole |
| ACT DR6 天空覆蓋 | 只有 40% 天區，無法做全天空 anisotropy map |
| 地面 experiment 系統誤差 | 大氣污染、望遠鏡系統效應混淆 intrinsic birefringence |
| 偏振角度校準 | detector angle miscalibration 同 true birefringence 簡併 |

---

## 5. 建議監測計劃

| 頻率 | 行動 | 條件 |
|:----|:-----|:-----|
| 每 6 個月 | arXiv 搜索 "cosmic birefringence anisotropy" | LiteBIRD 更新 |
| 每 12 個月 | 檢查 LiteBIRD 進度 (JAXA/ISAS) | MDR 後 |
| 觸發 | 任何 anisotropic birefringence 檢測 | 立即分析軸對齊 |

**下一步動作**: 儲存此監測為 cronjob (每 6 個月)，當 LiteBIRD 有 anisotropy map 時自動觸發軸對齊測試。

---

## 6. 結論

| 問題 | 答案 | 狀態 |
|:----|:-----|:----:|
| β 有冇方向依賴? | 未知 — Planck PR4 冇發現 dipole, tomographic 冇發現 | 🟡 等 LiteBIRD |
| 全息預測可證偽? | 可以 — 零方向依賴 → 否決全息; 軸對齊 r₀ → 支持 | 🟢 清晰 |
| LiteBIRD 時間表 | 2029+ 發射, 2032+ 科學數據 | 🟡 等 |
| 替代方案 | ACT DR6 疊加更多數據可能改善靈敏度 | 🟡 低優先 |