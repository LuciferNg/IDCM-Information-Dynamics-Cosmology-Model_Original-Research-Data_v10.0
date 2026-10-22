# O91 — S8 張力: 策略更新 (v2)

> **日期**: 2026-08-26
> **狀態**: 🟡 **策略更新 — 剔除 DESI，用獨立數據驗證**

## 原策略問題

原論證「S8 張力 = ΛCDM 外推 artifact」太草率，原因：
1. DESI 2024 數據本身就同 ΛCDM 存在顯著不協調 (w₀wₐCDM, phantom divide)
2. 將問題歸咎於「外推」忽略咗 DESI 自身嘅系統性討論
3. 需要更穩健嘅獨立驗證，避免同單一數據集綁定

## 新策略 (剔除 DESI)

### 獨立數據源

| 數據 | 物理原理 | 角色 | 紅移範圍 |
|:-----|:---------|:----|:---------|
| **Pantheon+** (SNIa) | 光度距離 D_L(z) → D_A(z) | 純幾何驗證 | 0 < z < 2.3 |
| **KiDS-1000** | 弱透鏡剪切譜 | S8 驗證 | z < 1.0 |
| **DES Y3** | 3×2pt (shear+clustering+galaxy-galaxy) | 交叉驗證 | z < 1.2 |
| **Cosmic Chronometers** | H(z) 被動星系年齡差 | 模型獨立 H(z) | 0 < z < 2.0 |
| **TDCOSMO/H0LiCOW** | 強透鏡時間延遲 | 幾何交叉驗證 | z~0.5-1.0 |

### 新論證鏈

```
Step 1: Pantheon+ 驗證 IDCM D_A(z) 幾何
  → 用 1500+ SNe 檢驗 IDCM 距離曲線
  → 如果 IDCM 被 Pantheon+ 排除 → 模型無效
  → 如果 IDCM 通過 → 幾何成立

Step 2: KiDS-1000 驗證 S8 一致性
  → 代入 IDCM D_A(z) 到弱透鏡 lensing kernel
  → 檢驗 inferred S8 是否同 Planck 自洽
  
Step 3: 結論
  → 如果 Steps 1&2 都通過:
    ΛCDM 喺解釋多個獨立數據時存在內在矛盾
    IDCM 嘅幾何自然消除呢啲矛盾
```

### 優勢

1. **避免 DESI 爭議** — 唔綁定單一數據集
2. **多重獨立驗證** — SNIa (幾何) + WL (結構) + CC (H(z)) + SL (距離)
3. **更嚴格嘅檢驗** — Pantheon+ 1500+ SNe 係最嚴苛嘅純幾何關卡
4. **學術避險** — 唔將 IDCM 命運同 DESI 系統誤差討論綁定

## 檔案更新

```
o91_s8_tension/
├── 01_problem_record.md       ← 更新策略
├── docs/
│   ├── 05_strategy_v2.md      ← 本文件
│   └── ...
├── scripts/
│   ├── 10_pantheon_verify.py  ← 新: Pantheon+ 驗證 IDCM D_A(z)
│   └── ...
```