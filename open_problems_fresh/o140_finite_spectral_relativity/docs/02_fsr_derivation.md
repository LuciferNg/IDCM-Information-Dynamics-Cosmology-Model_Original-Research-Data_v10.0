# 有限譜化相對論 (Finite-Spectral Relativity, FSR)
## O140 — 完整結構推導

> **日期**: 2026-08-30
> **狀態**: 🟡 核心推導完成 (38/38 PASS)，🔴 4 項開放
> **來源**: 從 IDCM K_Chain ⊗ K_Tree 結構重新設計相對論，兼容 IDCM 及 QM

---

## 摘要

標準相對論 (SR) 建立在連續 Minkowski 空間 + 無界譜。IDCM 的 K_Chain 是 44-site 有限離散譜，K_Tree 是 33-site 尺度維 (B=4)。FSR 從有限譜推導所有運動學結構：速度階梯、洛倫茲階梯、快度格子、離散質量殼、Doppler 因子。SR 是 K_Tree 尺度精化 ℓ→∞ 的連續極限。QM 兼容性來自有限維 Hilbert 空間 + 緊緻動量空間 + 無紫外發散。

---

## 1. K_Chain 譜基礎

從 `src/kchain_wave_params.py`:

**44-site 世界鏈** (n=1..44):
$$\gamma_n^{44} = 4\sin^2\left(\frac{\pi n}{88}\right), \quad \sum_{n=1}^{44} \gamma_n^{44} = 90$$

**88-site 對偶鏈** (k=1..88):
$$\gamma_k^{88} = 4\sin^2\left(\frac{\pi k}{176}\right), \quad \sum_{\text{even}} \gamma_k^{88} = 90\;(\text{世界}), \sum_{\text{odd}} \gamma_k^{88} = 88\;(\text{觀察者}), \;\text{總和}=178=2F_{11}$$

**色散關係** (晶格場論標準型):
$$\omega_n = \frac{2c}{a}\sin\left(\frac{\pi n}{88}\right), \quad a = \frac{R_{\text{world}}}{44} = 93.86\;\text{Mpc}$$

**驗證**: 38/38 PASS (scripts/01_verify_fsr_identities.py)

---

## 2. 運動學重設計: 速度階梯

### 2.1 群速度
從晶格色散, 群速度:
$$v_g(n) = \frac{d\omega_n}{dk_n} = c\,\cos\left(\frac{\pi n}{88}\right), \quad n=1..44$$

| n | v_g/c | 物理意義 |
|:-:|:-----:|:---------|
| 0 → ε | → 1 | 連續極限 (光速 c) |
| 1 | 0.99936 | 最快速模式 (v < c) |
| 22 | 1/√2 = 0.7071 | 中階梯 |
| 44 | 0 | Nyquist = 靜止 |

**Z₂ 鏡像對偶**: $v_{88-n} = -v_n$ — 模式反射 = 速度反轉。

### 2.2 Lorentz 階梯

從 SR 恆等式 $\gamma = 1/\sqrt{1-v^2/c^2}$:
$$\gamma_n = \frac{1}{\sqrt{1-\cos^2(\pi n/88)}} = \csc\left(\frac{\pi n}{88}\right)$$

**關鍵**: SR 的 $\gamma$-$v$ 關係在階梯上**精確保持**。FSR 不修改 $\gamma$ 的定義 — 它將速度量子化離散值。

| n | γ_n | 意義 |
|:-:|:---:|:-----|
| 1 | 28.017 | 最快速模式 |
| 22 | √2 = 1.414 | 中階梯 |
| 44 | 1 | 靜止 |

### 2.3 速度階梯間距 (速度量子)

$$\Delta v_n = v_n - v_{n+1} = 2c\sin\left(\frac{\pi(n+1/2)}{88}\right)\sin\left(\frac{\pi}{176}\right)$$

最大間距: $\Delta v_{22} \approx 0.025c$ (中階梯)。最小間距: $\Delta v_1 \approx 0.00064c$ (高速端)。階梯在高速端最密。

---

## 3. 本徵值恆等式

### 3.1 對偶鏈鏡像乘積
$$\gamma_n^{88} \cdot \gamma_{88-n}^{88} = 16\sin^2\left(\frac{\pi n}{176}\right)\cos^2\left(\frac{\pi n}{176}\right) = 4\sin^2\left(\frac{\pi n}{88}\right) = \gamma_n^{44}$$

**物理**: 世界鏈 (44-site) 的每個本徵值是對偶鏈 (88-site) 一對鏡像模式的乘積 — 世界/觀察者對偶內嵌在 Lorentz 結構中。

### 3.2 Lorentz 因子從本徵值
$$\gamma_n = \frac{2}{\sqrt{\gamma_n^{44}}} = \frac{c}{\pi a f_n}$$

**結構**: 模式的 Lorentz 因子 = 2 / √(本徵值)。質量 (∝ γ_n^{44}) 和最大速度 (cos(πn/88)) 來自同一本徵值 — 同一階梯兩個讀數。

### 3.3 Σγ²=1291
$$\sum_{n=1}^{44} \gamma_n^2 = \sum_{n=1}^{44} \csc^2\left(\frac{\pi n}{88}\right) = 1291 \;(\text{質數})$$

**釐清 O100 P3**: 1291 不是 artifact — 它是 FSR Lorentz 因子平方的世界和。出自數學恆等 $\sum_{k=1}^{N-1} \csc^2(\pi k/N) = (N^2-1)/3$ 對 N=88。

---

## 4. 快度格子與 Doppler

### 4.1 快度

SR 快度: $\eta = \operatorname{atanh}(v/c) = \frac{1}{2}\ln\frac{1+v/c}{1-v/c}$。

代入 $v/c = \cos(\pi n/88)$:
$$\eta_n = \operatorname{atanh}(\cos\theta_n) = \ln\cot\frac{\theta_n}{2} = \ln\cot\left(\frac{\pi n}{176}\right)$$

| n | η_n | 物理 |
|:-:|:---:|:-----|
| 1 | 4.0256 | 高速 |
| 22 | 0.8814 | 中速 |
| 44 | 0 | 靜止 |

### 4.2 Doppler 因子

相對論性 Doppler: $D = \sqrt{\frac{1+\beta}{1-\beta}} = e^\eta$:
$$D_n = e^{\eta_n} = \cot\left(\frac{\pi n}{176}\right)$$

| n | D_n | 物理 |
|:-:|:---:|:-----|
| 1 | 56.017 | 最大 Doppler (移近/遠離) |
| 22 | 1 | 橫向 Doppler (無位移) |
| 44 | 1 | 靜止 |

**精確閉合形式**: Doppler 因子 = 快度指數 = 三角餘切 — 無近似。

---

## 5. 離散質量殼

能量-動量關係在質量殼上:
$$E_n = mc^2\gamma_n = mc^2\csc\left(\frac{\pi n}{88}\right)$$
$$p_n = mv_n\gamma_n = mc\cos\left(\frac{\pi n}{88}\right)\csc\left(\frac{\pi n}{88}\right) = mc\cot\left(\frac{\pi n}{88}\right)$$

**驗證**: $E_n^2 - p_n^2c^2 = m^2c^4(\csc^2\theta - \cot^2\theta) = m^2c^4$ ✓ 精確。

**離散雙曲線**: 能量-動量空間的點集 $\{(E_n, p_n)\}$ 位於質量殼雙曲線上，但取值離散 — 44 個點對應 44 個模式。

---

## 6. 尺度精化與 SR 極限

### 6.1 K_Tree B=4 精化

K_Tree (33-site, B=4) 提供尺度精化機制。在層 ℓ:
$$N_\ell = 44 \cdot 4^\ell, \quad a_\ell = \frac{R_{\text{world}}}{N_\ell} = \frac{a_0}{4^\ell}$$
$$v_g(n; \ell) = c\cos\left(\frac{\pi n}{88 \cdot 4^\ell}\right), \quad n=1..N_\ell$$
$$\gamma_n(\ell) = \csc\left(\frac{\pi n}{88 \cdot 4^\ell}\right), \quad \gamma_{\max}(\ell) = \csc\left(\frac{\pi}{88 \cdot 4^\ell}\right) \approx \frac{88}{\pi} \cdot 4^\ell$$

| ℓ | N_ℓ | γ_max(ℓ) | 物理 |
|:-:|:---:|:--------:|:-----|
| 0 | 44 | 28.0 | 基礎鏈 |
| 1 | 176 | 112.0 | |
| 2 | 704 | 448.2 | |
| 6 | 180,224 | 1.15×10⁵ | LEP 電子 (γ∼10⁵) |
| 10 | 4.61×10⁷ | 2.87×10⁷ | LHC 質子 |
| ℓ→∞ | ∞ | ∞ | **SR 極限** |

### 6.2 紅移連接 (O76)

從 O76: $1+z = 4^\ell$。則:
$$\gamma_{\max}(\ell) = \csc\left(\frac{\pi}{88 \cdot 4^\ell}\right) = \csc\left(\frac{\pi}{88}(1+z)\right) \approx \frac{88}{\pi} \cdot (1+z)$$

**關鍵**: γ_max / (1+z) = 88/π = 28.01 常數 — 紅移標度了可達 Lorentz 因子的上限。

### 6.3 SR 偏差

在層 ℓ, 色散偏離線性的相對量:
$$\frac{\omega_n - ck_n}{ck_n} \approx -\frac{1}{6}\left(\frac{\pi n}{88 \cdot 4^\ell}\right)^2$$

在 ℓ=6 (γ∼10⁵): 偏差 ∼ 3.8×10⁻¹¹ — 不可觀測。FSR 在所有當前實驗能量下與 SR 不可分辨。

---

## 7. QM 兼容性

### 7.1 有限維 Hilbert 空間

基礎層 ℓ=0: $\dim\mathcal{H} = 44$ (44-site 世界鏈)。在層 ℓ: $\dim\mathcal{H}_\ell = 44\cdot 4^\ell$。

**全部算子有界** — 無 QM 發散問題。

### 7.2 動量化

晶格動量: $k_n = \frac{\pi n}{44a}$ (等間距)
$$p_n = \hbar k_n = \frac{\hbar\pi n}{44a}, \quad n=1..44, \quad p_{\max} = \frac{\hbar\pi}{a}$$

Brillouin 區間: $p \in [0, \hbar\pi/a]$ — 緊緻動量空間。

### 7.3 推廣不確定性原理 (GUP)

從緊緻動量空間:
$$\Delta p \leq p_{\max} = \frac{\hbar\pi}{a}, \quad \Delta x \geq \frac{\hbar}{2\Delta p_{\max}} = \frac{a}{2\pi}$$

**GUP**: $\Delta x \geq a/(2\pi)$ — 最小位置不確定性 = 晶格間距 / (2π)。這不是「最小長度」在通常意義上（位置本徵態存在於站點），而是由動量截斷引起的擴展不確定性。

### 7.4 晶格 Klein-Gordon (紫外有限)

$$E_n^2 = m^2c^4 + \hbar^2c^2k_n^2 = m^2c^4 + \left(\frac{\hbar c\pi n}{44a}\right)^2$$

譜有界: $E_{\max} = \sqrt{m^2c^4 + (\hbar c\pi/a)^2}$ — 無紫外發散。這正是 O80/O94 的「88-site 晶格 = 物理截斷 → 有限 QFT」。

### 7.5 費米子結構

88-site 對偶鏈的奇偶分解提供旋量結構:
- 世界: Σγ_even = 90 (玻色子/時空)
- 觀察者: Σγ_odd = 88 (費米子/自旋)
- 反週期量子化: n·L ≡ 44 mod 88 (O137, 費米子邊界條件)

---

## 8. 跨域閉合

### 8.1 BBN n/p (O13)
$$\frac{n}{p} = \frac{\gamma_7}{\gamma_{20}} = \frac{\gamma_7^{44}}{\gamma_{20}^{44}} = \left(\frac{\gamma_{\text{FSR}}(20)}{\gamma_{\text{FSR}}(7)}\right)^2 = 0.142618$$

**解釋**: BBN 中子-質子比 = 兩個 FSR Lorentz 因子平方的比值 — 不是熱凍結，是結構。

### 8.2 Etherington 指數 (O76)
$$1-\frac{n}{p} = 1-\frac{\gamma_7}{\gamma_{20}} = 0.857382$$
$$\frac{D_L}{D_A} = (1+z)^{1-n/p} = (1+z)^{0.857} \neq (1+z)^2$$

**FSR 預言**: Etherington 關係在 IDCM 中失效，偏差來自同一個結構比值 γ₇/γ₂₀。

### 8.3 質量-速度階梯共享

O54 輕子質量: $m_g = M_0\gamma_{n_g} \cdot S_g$ (n_g=1,7,20)
FSR: $\gamma_{\text{FSR}}(n_g) = 2/\sqrt{\gamma_{n_g}^{44}}$

$$\Rightarrow m_g \cdot \gamma_{\text{FSR}}(n_g)^2 = 4M_0 \cdot S_g$$

**結構陳述**: 同一 K_Chain 模式 n_g 決定三個量:
1. 靜止質量 (∝ γ_{n_g})
2. 速度上限 (v_g = c·cos(πn_g/88))
3. 最大 Lorentz 因子 (γ_FSR(n_g) = csc(πn_g/88))

| 粒子 | 模式 n | m ∝ γ_n | v_ceiling/c | γ_FSR | 物理 |
|:----:|:------:|:--------:|:-----------:|:-----:|:-----|
| e | 1 | 0.0051 | 0.9994 | 28.0 | 最輕、最快 |
| μ | 7 | 0.2446 | 0.9689 | 4.04 | 中等 |
| τ | 20 | 1.7154 | 0.7557 | 1.53 | 最重、最慢 |

**質量-速度反相關**: 越重的粒子，其模式速度上限越低 — 代價是更大的靜止能量。

---

## 9. 加速合成: 開放問題 (🔴)

SR 快度可加: $\eta_{a\oplus b} = \eta_a + \eta_b$。在 FSR 階梯上:
$$\eta_{a\oplus b} = \ln\cot\frac{\pi a}{176} + \ln\cot\frac{\pi b}{176} = \ln\left(\cot\frac{\pi a}{176}\cot\frac{\pi b}{176}\right)$$

這一般不等於 $\ln\cot(\pi c/176)$ 對任何整數 c — 加速合成在階梯上不封閉。

**FSR 的回答**: 合成提升到更精細的尺度層 ℓ 實現。在層 ℓ，快度加法:
$$\eta_{a,b}(\ell) = \ln\cot\frac{\pi a}{176\cdot 4^\ell} + \ln\cot\frac{\pi b}{176\cdot 4^\ell}$$

結果落在層 ℓ' 的階梯上，其中 ℓ' 由所需精度決定。物理上，這對應於 K_Tree 的尺度上升 — 加速合成是尺度層的轉換。

**🔴 開放**: 此解釋需形式化為離散群結構。可能需要推導階梯的離散子群 (Z_(44·4^ℓ)，或某種量子群形變)。

---

## 10. 文獻定位

FSR 的數學結構對應於文獻中三個獨立發展的框架:

| 框架 | 共同點 | 差異 |
|:-----|:-------|:-----|
| **Polymer 量子化** (LQG) | 正弦色散 ω∝sin(ka/2), 速度 v_g=c·cos(ka/2) | LQG 需要人工選擇聚合物表示; IDCM 的 K_Chain 是結構強制 |
| **DSR** (Amelino-Camelia, Magueijo-Smolin) | 變形色散, 非封閉合成 | DSR 有自由參數 (Planck 尺度); FSR 零參數, 尺度由 K_Tree 給出 |
| **Connes 譜三元組** | 有限 Dirac 算子 → 有限維 Hilbert 空間 | IDCM 的 44-site 鏈是具體譜三元組, 非交換幾何的離散特例 |
| **'t Hooft 胞自動機 QM** | 離散晶格 + 量子疊加 | IDCM 的 44 模式提供自然基底; 自動機法則 = K_Chain 動力學 |

**關鍵區別**: FSR 不是引入新的相對論 — 它從 K_Chain 的有限譜推導出相對論。SR 的運動學公式 (γ=1/√(1-v²/c²), E²-p²c²=m²c⁴, Doppler=e^η) 全部精確保持; 新內容是速度離散化 + 尺度精化結構。

---

## 11. 可證偽預言

| # | 預言 | 現狀 |
|:-:|:-----|:----:|
| P1 | γ-v 關係與 SR 完全相同 (在階梯上) | ✅ 所有 SR 測試通過 |
| P2 | SR 偏差在 ℓ≥6 時 < 4×10⁻¹¹ | 🟡 不可觀測 (當前實驗) |
| P3 | D_L/D_A = (1+z)^{0.857} (Etherington 失效) | 🟢 O76 已驗證 (Pantheon+) |
| P4 | 時間膨脹 Δt ∝ (1+z) (與 ΛCDM 同) | 🟢 O76 已驗證 |
| P5 | 最大紅移 z_max ≈ 17 (Nyquist 截止) | 🟡 JWST 等待 |
| P6 | 速度離散化 (純模式) | 🔴 需要純模式製備 (開放) |
| P7 | γ_max = 28·(1+z) (紅移標度) | 🔴 需高 z 高能數據 |

---

## 12. 總結

FSR 從 IDCM 的 K_Chain ⊗ K_Tree 結構推導出相對論，結果:

1. **速度階梯**: v_n = c·cos(πn/88) — 離散速度空間
2. **Lorentz 階梯**: γ_n = csc(πn/88) = 2/√γ_n^{44} — SR 關係精確保持
3. **快度/Doppler 格子**: η_n = ln cot(πn/176), D_n = cot(πn/176)
4. **離散質量殼**: E_n = mc²csc, p_n = mc·cot, E²-p²c²=m²c⁴ 精確
5. **尺度精化**: N_ℓ = 44·4^ℓ, SR = ℓ→∞ 極限
6. **QM 兼容**: 有限維 Hilbert 空間, 緊緻動量, GUP, 紫外有限
7. **跨域閉合**: n/p, Etherington, 質量-速度共享

**零自由參數** — 所有量從 K_Chain 的 44/88 結構導出。

---

## 參考

- `~/Projects/IDCM-v10.0--It-From-Beat/src/kchain_wave_params.py` — K_Chain 波參數
- O76: z紅移翻譯 — 1+z = 4^ℓ, D_L/D_A = (1+z)^{0.857}
- O54: 輕子質量閉合 — m_g ∝ γ_{n_g}
- O34: 觀察者/內觀 — 88-site 奇偶分解
- O80/O94: 有限 QFT — 88-site 晶格 = 物理截斷
- O99: 光實質不存在 — v_g ≤ c, 零色散
- O100: C_ℓ→P_3D — 1291 質數 artifact
- scripts/01_verify_fsr_identities.py — 38/38 PASS 驗證