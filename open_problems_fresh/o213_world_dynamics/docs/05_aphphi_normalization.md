# docs/05 — R4: A_φφ 歸一化（ℓ-空間殼測度）

> **狀態**: 🟡 結構部分 ✅ 閉合 / 振幅 gated on σ_8
> **腳本**: `scripts/06_aphphi_normalization.py` (18/18 PASS) → `data/06_aphphi_normalization.txt`
> **上游**: O99 `docs/09_o99v2_layer_in_layer.md`, `docs/10_amplitude_sigma8_gap.md`, `scripts/09_layer_lensing.py`
> **本檔新增**: 由 L7 細化流導出 ℓ-空間測度（O99 命名之缺口），並據此做振幅檢查

---

## 一、問題之原文（O99 docs/09 §「未閉合」）

O99 明確命名缺口：

> **「A_φφ=1.01 強度對齊未閉合: 「ℓ層物質正規化」(P_matter 喺 ℓ-空間) 需指定 —— 形狀已 match, 強度未。」**

O99 `scripts/09_layer_lensing.py` 用咗 `∫dχ`（**有量綱**）做層疊積分，故振幅需要一個**外部標度**輸入 ⟹ 唔係零參數。本檔由 L7 細化流補上該測度。

---

## 二、測度之推導（零參數，EXACT）

### 2.1 由 L7 殼身份

docs/01 C6 已證（整數 ℓ）：

$$1 - 4^{-\ell} = 3\sum_{j=1}^{\ell} 4^{-j} \qquad \text{(EXACT, 差 = 0)}$$

其右側係**殼權之和**。定義離散殼權：

$$w_j \equiv 3\cdot 4^{-j}, \qquad \sum_{j\ge 1} w_j = 3\cdot\frac{1/4}{1-1/4} = 1 \quad \text{(EXACT)}$$

### 2.2 連續測度

**Claim**: 累積 $\int_0^{\ell} w(\ell')\,d\ell' = 1 - 4^{-\ell}$ 唯一決定

$$\boxed{\,w(\ell) = \ln 4 \cdot 4^{-\ell}\,}$$

**驗證**（script C3–C4，dps = 40）：
- $\int_0^\infty w\,d\ell = \ln4\cdot\frac{1}{\ln4} = 1$ **EXACT**
- $\int_0^{3.7} w\,d\ell = 0.994079232162069 = 1-4^{-3.7}$ **EXACT**
- $\ell\to$ 整數時 $w_j = 3\cdot4^{-j}$ 對應離散版（$w_1 = 3/4$ ✓）

> **★ 測度係唯一**：歸一化（$\Sigma = 1$）+ 累積 = 殼身份 ⟹ **零自由參數**。呢個就係 O99 命名嘅「ℓ層物質正規化」。

### 2.3 ★ 測度 = 指數分布

$w(\ell) = \ln4\,e^{-\ell\ln4}$ ⟹ **級聯深度 ℓ 服從指數分布，rate = ln4**：

| 動差 | 值 | 驗證 |
|---|---|---|
| $\langle\ell\rangle_w$ | $1/\ln4 = 0.7213475$ | C8 ✔ |
| $\langle\ell^2\rangle_w$ | $2/(\ln4)^2 = 1.0406845$ | C9 ✔ |
| $\mathrm{Var}(\ell)$ | $1/(\ln4)^2$ ⟹ $\mathrm{std} = \langle\ell\rangle$ | C9 ✔ |
| $\langle 4^{-\ell}\rangle_w$ | $1/2$ EXACT | C11 ✔ |

- **平均 = 標準差 = 1/ln4**（指數分布之簽名）
- **中位深度** $\ell_{1/2} = \log_4 2 = 1/2$：一半殼重喺 ℓ < 1/2 之內

> **★ 結構讀法**：級聯冇特徵標度（scale-free）—— 指數測度 = 唯一無記憶（memoryless）之連續分布，與「自相似 4:1 細化」完全相容。若測度有特徵 ℓ*，就會破壞自相似 ⟹ **指數測度係自相似之唯一選擇**。

---

## 三、層疊積分之正規化

O99 版本：$C_L^{\phi\phi} \propto \int d\chi\, \frac{W(\chi)^2}{\chi^2} P_\delta\!\left(\frac{L}{\chi}\right)$ —— $\int d\chi$ **有量綱**（長度）⟹ 振幅需要外部標度。

**本檔版本**（用測度）：

$$C_L^{\phi\phi} \propto \Big\langle \frac{W^2}{D_{\rm app}^2}\,P_\delta\!\Big(\frac{L}{D_{\rm app}}\Big) \Big\rangle_w \equiv \int_0^\infty w(\ell)\, \frac{W(\ell)^2}{D_{\rm app}(\ell)^2}P_\delta\!\Big(\frac{L}{D_{\rm app}(\ell)}\Big)\,d\ell$$

**後果**：測度歸一化（$\int w = 1$）⟹ 積分係**加權平均**（無量綱）⟹ **振幅冇自由標度**。呢個就係「強度」部分之結構修復。

---

## 四、幾何核比（新結構量）

用 IDCM 橫向距離（O76）$D_{\rm app}(\ell) = R_{\rm world}(1-4^{-\ell})E(\ell)$，$E(\ell) = \ell + 1.11911398$（docs/04 §四），$R_{\rm world} = 4129.94$ Mpc；對照 ΛCDM（$H_0 = 67.4$, $\Omega_m = 0.3153$）：

| 量 | IDCM | ΛCDM | 備註 |
|---|---|---|---|
| $\chi$ 範圍 (Mpc) | 315.6 → 8872.3 | 306.1 → 8378.3 | $D_{\rm app}/\chi_{\Lambda}$: 0.983–1.059 |
| 峰 $L$ | **143** | 136 | O99 報 149 vs 136 ✓ |
| $\mathrm{std}(\ln Q)$ | 0.196 | 0.187 | 形狀吻合 |
| $\int Q\,dL$ | — | — | **比 = 1.0745** |

$$\boxed{\;Q_{\rm IDCM}/Q_{\Lambda\rm CDM} = 1.0745\;}$$

> **★ 呢個就係 O99 命名缺口之「強度」部分**：由測度 + IDCM 幾何唯一決定，零參數。

---

## 五、振幅檢查（σ_8 為唯一外部輸入）

$$A_{\phi\phi}^{\rm IDCM} = \Big(\frac{\sigma_{8,\rm IDCM}}{\sigma_{8,\Lambda\rm CDM}}\Big)^{2} \times \frac{Q_{\rm IDCM}}{Q_{\Lambda\rm CDM}}$$

觀測錨：**$A_{\phi\phi} = 1.011 \pm 0.028$**（Planck VIII 2019，MV $L=8$–400，CMB marginalized）

| $\sigma_{8,\rm IDCM}$ | 來源 | $A_{\phi\phi}^{\rm IDCM}$ | pull vs $1.011 \pm 0.028$ |
|---|---|---|---|
| 0.748 | O100 現行 🟡 | 0.9141 | **−3.46σ** ✘ |
| 0.783 | BOSS DR12 實測 | 1.0016 | **−0.34σ** ✅ |
| 0.785 | IDCM 包絡頂 | 1.0067 | **−0.15σ** ✅ |

**精確命中所需**：$\sigma_{8,\rm IDCM} = 0.7867$

- vs BOSS DR12 實測 0.783：**+0.5%**
- vs IDCM 包絡頂 0.785：**+0.2%**
- vs O100 現行 0.748：**+5.2%**

---

## 六、裁決

| 部件 | 狀態 | 依據 |
|---|---|---|
| ℓ-空間測度 $w(\ell) = \ln4\cdot4^{-\ell}$ | ✅ **閉合** | C1–C11，EXACT，零參數 |
| 積分正規化（無自由標度） | ✅ **閉合** | C6，C14 |
| 形狀（峰位、寬度） | ✅ **閉合** | C12（O99 已證，本檔復現） |
| 幾何核比 1.0745 | ✅ **閉合** | C13，零參數 |
| **振幅** | 🟡 **gated on σ_8** | C15–C18 |

### ★ 結構含義

1. **A_φφ 提供 σ_8 之獨立約束**：$\sigma_{8,\rm IDCM} \approx 0.787$。此值**唔係擬合** —— 0.783 係 BOSS DR12 之獨立實測，0.785 係 IDCM 包絡之獨立上界，兩者皆獨立於 A_φφ。
2. **閉合被 O100 #1 閘住**：O100 之 $\sigma_8 = 0.748$ 係 🟡 半閉合（缺口 = beat 背景 946 拍頻之 44-mode 投影權重 $w_n$）。**若該包絡閉合到 $\sigma_8 < 0.77$ ⟹ A_φφ 失敗（>2σ）**。
3. **O99 缺口已補**：由「需指定」→「已指定」（測度由 L7 強逼，非選擇）。

### ★ 可證偽

| 情境 | 預言 | 判準 |
|---|---|---|
| 完整 44-mode 包絡閉合 | $\sigma_8 \in [0.783, 0.787]$ | A_φφ ✅ |
| 完整 44-mode 包絡閉合 | $\sigma_8 < 0.77$ | A_φφ **FAIL >2σ** 🔴 |
| 幾何核比獨立重算 | $1.0745 \pm$ 形狀不確定度 | 若 ≠ 1 ⟹ 「強度」缺口確實存在 |

---

## 七、殘餘

- 🔴 **O100 #1**（44-mode beat 包絡權重）未閉合 ⟹ $\sigma_8 = 0.748$ 係暫值，A_φφ 之終值未定。
- 🟡 **A_L = 1.180 ± 0.065**（Planck VI 2018，2.7σ 異常）未處理：本檔之核比 1.0745 < 1.18。若 IDCM 之核比係真值，則 A_L 異常**唔**由 IDCM 幾何解釋 ⟹ 支持 A_L 係 Planck 內部系統（dust masking，見 Rosenberg+ 2023）。
- 🔴 源距離 $\chi_s$：IDCM 級聯之 Nyquist 上限係 $z = 17$，而 CMB 最後散射面 $z \approx 1100$ 唔喺級聯內 ⟹ 本檔沿用 O99 之「偏折體範圍」約定（$z \in [0.07, 5.9]$）做**相對**比較。絕對歸一化仍需源距離之結構指定。

---

*本檔為 O213 交付物 ② 之完成件。原文（O99 docs/09-10）保留不改。*
