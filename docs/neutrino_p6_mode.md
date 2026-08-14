# IDCM v10.0 — 中微子質量：W-field p6 模式

## 概述

中微子質量唔係來自 Seesaw 機制，而係直接來自 K_Chain 嘅 W-field 高階 harmonic 模式。
**中微子 = W-field 嘅 p6 模式**（n=6 諧波）。

---

## 一、K_Chain 諧波結構

### 44 個模式

K_Chain 有 44 個離散模式，每個模式有頻率：
$$\gamma_n = 4\sin^2\left(\frac{\pi n}{88}\right), \quad n = 1, 2, \ldots, 44$$

### 粒子-模式對應

| 粒子 | n | γ_n | 說明 |
|:----|:-:|:---:|:-----|
| Top | 1 | 0.0051 | 最重夸克 |
| Bottom | 2 | 0.0203 | 第二代 |
| ... | ... | ... | ... |
| Electron | 9 | 0.3989 | 最輕帶電粒子 |
| **ν** | **6** | **0.1807** | **中微子** |
| DM | 4-7 | 0.0805-0.2476 | 暗物質模式 |

---

## 二、中微子質量機制

### 唔係 Seesaw！

標準模型嘅 Seesaw 機制需要：
- 右旋中微子 N_R（未發現）
- 大質量 M_R ~ 10^11 GeV（未觀測）
- Type-I seesaw: m_ν ≈ m_D² / M_R

**IDCM 唔需要 Seesaw！** 中微子質量直接來自 W-field 嘅 harmonic 結構。

### IDCM 質量公式

所有粒子質量遵循同一公式：
$$m_i = \lambda_i \times M_{Pl} \times \exp(-V_{cycle}) \times f_{sector}$$

其中：
- λ_i = eigenvalue（從 WDVV 方程求解）
- M_Pl = 1.22 × 10^22 MeV（Planck 質量）
- V_cycle = 循環體積（exp(-V) 係體積壓抑因子）
- f_sector = sector-specific factor（波函數重整化）

### 中微子嘅 λ 值

從 12 個 WDVV eigenvalue 中，中微子對應嘅 eigenvalue：
- ν_τ: λ_9 ≈ 0.0014（index 9）
- ν_μ: λ_10 ≈ 0.0010（index 10）

### V_cycle 同 f_sector

中微子嘅 V_cycle 同 lepton sector 一致：
- V_cycle ≈ 46.5（Gen1，同 electron 相同）
- f_sector ≈ 1（無需額外修正）

但中微子嘅 p6 模式意味住佢嘅 W-field 結構同 charged lepton 唔同：
- Electron: n=9, γ_9 = 0.3989
- 中微子: n=6, γ_6 = 0.1807

---

## 三、質量估算

### 簡單估算

$$m_\nu \approx \lambda_\nu \times M_{Pl} \times \exp(-V_{cycle})$$

用 ν_τ 嘅 eigenvalue:
$$m_{\nu_\tau} \approx 0.0014 \times 1.22 \times 10^{22} \times \exp(-46.5) \approx 1.9 \times 10^{-10} \text{ eV}$$

### PDG 對比

| 中微子 | IDCM 估算 | PDG 上限 | 狀態 |
|:------|:---------:|:--------:|:----:|
| ν_τ | 1.9e-10 eV | ~1.8e4 eV | 🔴 太輕 |
| ν_μ | 1.0e-10 eV | ~9.0e3 eV | 🔴 太輕 |
| ν_e | — | < 0.8 eV | 🔴 |

### 問題

IDCM 嘅中微子質量估算（~10^-10 eV）遠低於 PDG 上限（~10^4 eV）同宇宙學上限（Σm_ν < 0.12 eV）。
可能原因：
1. eigenvalue 分配唔啱——中微子可能對應更大嘅 eigenvalue
2. V_cycle 唔同——中微子可能有更細嘅 V_cycle（更細體積 = 更大質量）
3. p6 模式嘅 harmonic 結構同 charged lepton 唔同
4. 需要引入 W-field 嘅非對角混合

---

## 四、同 Seesaw 機制嘅區別

| 特性 | Seesaw 機制 | IDCM p6 模式 |
|:----|:-----------|:-------------|
| 右旋中微子 N_R | 需要 | 唔需要 |
| M_R 質量 | 10^10-10^15 GeV | 無 |
| 質量起源 | 高能尺度 seesaw | K_Chain harmonic |
| 中微子類型 | Majorana | Dirac（或 Majorana） |
| 自由參數 | M_R, Yukawa | 0（純粹幾何） |

---

## 五、待解決問題

1. **中微子 eigenvalue 確認** — 需要正確分配 12 個 eigenvalue 到中微子
2. **V_cycle 精確值** — 中微子嘅 V_cycle 可能同 charged lepton 唔同
3. **p6 模式嘅 harmonic 結構** — 需要完整推導 n=6 嘅 W-field 結構
4. **中微子混合（PMNS）** — 未開始推導
5. **Majorana vs Dirac** — IDCM 中微子嘅性質未確定