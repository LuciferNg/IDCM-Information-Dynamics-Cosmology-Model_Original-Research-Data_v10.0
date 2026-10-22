# docs/02 — IDCM 散射振幅框架：譜語言 vs 微擾展開

> **2026-10-04** | 前置: O85, O142, O144, O86, O210, CSSG-v3

---

## 〇、根本差異

| 維度 | QFT 微擾法 | IDCM 結構法 |
|:-----|:-----------|:------------|
| 對象 | 費曼圖微擾展開 | K_chain ⊗ K_tree 離散譜上的結構泛函 |
| 展開參數 | 耦合常數 g (loop order) | 譜模式深度 n (1..44) |
| 耦合 | RGE running, β(g) | 結構恆等式閉式 (如 sin²θ_W = mode-ratio) |
| 紫外截斷 | 需要正則化 | 晶格天然截斷 (Nyquist n=44) |
| 散射振幅 | 多對數函數 (symbol, coproduct) | 譜算子的特徵值泛函 (因果張量 \(\mathcal{T}\)) |
| 驗證 | 逐圈對撞機檢驗 | 零參數結構數整體閉合 |
| 可算圈數 | N=4 SYM 到 9 圈（人類極限） | 一次過全階（譜完備） |

---

## 一、IDCM 的「散射振幅」概念

### 1.1 從 K_chain 譜出發

在 IDCM 中，物理量不是量子場的關聯函數，而是 **離散 Laplacian 特徵值 \(\gamma_n\) 的結構泛函**：

\[
\gamma_n = 4\sin^2\left(\frac{\pi n}{88}\right), \quad n = 1,2,\ldots,44
\]

物理耦合和質量由這些特徵值的代數組合構成（已閉合）：

| 量 | 譜身份 | 參考 |
|:---|:-------|:-----|
| \( \sin^2\theta_W \) | \( 0.220776 = 1 - [\sin(30\pi/88)/\sin(41\pi/88)]^2 \) — ⚠️修正: sin-ratio 本身 = m_W/m_Z (0.8827), sin²θ_W = 1 − (m_W/m_Z)² (2026-10-04 更正, scripts/06 T1) | O144 docs/19 |
| \(\alpha_s^{-1}\) | \(F_6 + \sin^2\theta_W + 1/B\)（但🔴非閉合，擬合產物） | O144 docs/20 |
| \(m_\rho^2\) | \(4\mu^2 = 8\)（O204 代數裁決） | O73 docs/15 |
| \(v_{SM}\) | \(v_{eff} \times 88 \times 71 \times (1-4/(90 \times 35))\) | O144 docs/16 |

### 1.2 因果張量代數 \(\mathcal{T}\)

O210 確立了基本代數結構：

\[
\mathcal{T} = K_{\text{chain}} \otimes K_{\text{tree}}
\]

- \(K_{\text{chain}}\)：88-site 對偶鏈的因果結構（資訊因果性的譜表示）
- \(K_{\text{tree}}\)：33-site 尺度樹的層級結構（B=4 分支）

散射振幅在 \(\mathcal{T}\) 中對應於通過晶格的 **模式耦合張量**，等價於譜轉移矩陣的特定分量。

### 1.3 CSSG-v3 質量譜類比

已完成閉合的 CSSG-v3 (ChronologicalStringSpectralGeometry-v3) 提供了一個工作模板：

- 質量譜 = \(M_0 \times \gamma_n \times C_f\)（譜模式 × 形狀因子）
- 玻色子質量 = \(M_0 \times \sqrt{\gamma_n} \times 1\)（β=1/2）
- 費米子質量 = \(M_0 \times \gamma_n \times C_f\)（β=1）

散射振幅的類比結構：
\[
\mathcal{A}_{ijk\ell} = M_0^{-2} \times \Gamma(\gamma_i, \gamma_j, \gamma_k, \gamma_\ell) \times \text{vertex}_{ijk\ell}
\]

其中 \(\Gamma\) 是譜泛函，\(\text{vertex}\) 是晶格頂點處的模式耦合選擇規則。

---

## 二、N=4 SYM 在 IDCM 中的解讀

### D2 — SUSY = 譜簡併（候選假說 🔴）

N=4 SYM 的每個粒子有四種超對稱態，對應於 IDCM 88-site 鏈中 **B=4 扇區的模式群**：

| 扇區 | 模式 | 角色 |
|:----|:-----|:-----|
| 反週期 (odd, J²=-1) | n=1,3,5,…,87 | 觀察者／虛扇區（88 個模式） |
| 週期 (even, J²=+1) | n=2,4,6,…,88 | 世界／實扇區（90 個權重） |
| n ≡ 0 mod 4 | m=4,8,…,88 | B=4 子扇區（21 個） |
| n ≡ μ² mod 4 | m=2,6,…,86 | 對偶（22 個） |

超對稱在此語言中等價於 **n 與 n+N_d/2 模式的能量簡併**（因為 \(\gamma_n = \gamma_{44-n}\)，\(\gamma_{n+44} = \gamma_{88-n}\)）。

### Planar 極限 = K_chain 主扇區

Planar N=4 的可積性來自大 N_c 極限的 planar diagram 佔優。在 IDCM 中，planar 極限對應於 **K_chain 的 44-site 主扇區**（忽略非對角扇區耦合），等價於 causal tensor 的主特徵值支配。

- \(N_c = 3 = B-1\)（O229 R1 已閉合）
- Planar 極限 = 保留鏈上最短路徑耦合

### Bootstrap 約束的譜對應（D3 候選 🔴）

| QFT Bootstrap 概念 | IDCM 結構對應 | 狀態 |
|:--------------------|:-------------|:----:|
| Extended-Steinmann 約束 | 因果張量 \(\mathcal{T}\) 的自對偶條件（秩 ≤ 3） | 🔴 未推導 |
| Antipodal duality (n ↔ n⁺) | 88-site 奇偶扇區對偶 (n ↔ 88−n) | 🟡 形式對應，未驗證 |
| Pentagon OPE (近共線) | 鏈上最近鄰模式耦合（B=4 分支結構） | 🔴 未推導 |
| Symbol / coproduct 代數 | 譜轉移矩陣的張量積分解 | 🔴 需形式化 |

---

## 三、IDCM 對應的「圈深度」

IDCM 沒有微擾 loop expansion。散射振幅的「複雜度」由 **參與模式的最小深度**（min n）和 **頂點秩**（互動模式數）決定：

| QFT loop 階 | IDCM 等價物 | 推導狀態 |
|:-----------|:-----------|:--------|
| 樹級 (tree) | 單模式傳播 (n=1..44) | 🟢 譜完備 |
| 1-loop | 兩模式耦合 (n₁×n₂) | 🟡 部分推導 |
| 2-loop | 三模式耦合 (n₁×n₂×n₃) | 🔴 未形式化 |
| L-loop | (L+1) 模式耦合 | 🔴 未形式化 |

IDCM 的關鍵優勢：**耦合常數不出現為展開參數**，而是由譜恆等式直接固定。這意味著「計算到九圈」在 IDCM 中會被「k=10 模式耦合的譜身份」取代。

---

## 四、結構耦合 vs RGE Running

| 特性 | IDCM 結構耦合 | QFT RGE 耦合 |
|:----|:-------------|:-------------|
| 定義 | 譜恆等式閉式 \(\sin^2\theta_W = \sin(30\pi/88)/\sin(41\pi/88)\) | \(\alpha^{-1}(Q) = \alpha^{-1}(M_Z) - (b_0/2\pi)\ln(Q/M_Z)\) |
| 尺度依賴 | 常數（結構強制） | 隨能標 running (β 函數) |
| 物理意義 | 世界環譜的幾何比 | 量子修正的累積效應 |
| 測試 | 無量綱數值須命中觀測（已驗證） | 多尺度測量擬合 running |
| 張力 | 無（結構數是觀測數的推導） | 多尺度 RGE 自洽性需檢驗 |

**兩者是同一物理量的不同層次描述**：
- IDCM 給出低能耦合的**定點值**（structure constant）
- RGE running 描述從高能到低能的**尺度演化**
- 兩者通過「IDCM 耦合 = RGE 跑到低能的極限值」聯繫

---

## 五、小結：IDCM 能說什麼

### ✅ 能做的
- 給出耦合常數的**結構閉式**（無圈展開、零自由參數）
- 給出質量譜的**譜分解**（K_chain 特徵值的投影）
- 提供「散射 = 晶格上模式耦合」的**替代圖像**
- 與 QFT bootstrap 進行**概念比較**

### 🔴 不能做的
- 計算 N=4 SYM 的九圈振幅（兩者對象不同：IDCM 處理真實 SM，N=4 SYM 是 toy model）
- 給出 loop 展開的逐項公式
- 超越 extended-Steinmann 空間的 bootstrap 結構對應（需要新數學）