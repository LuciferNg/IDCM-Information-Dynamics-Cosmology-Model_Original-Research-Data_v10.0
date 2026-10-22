# docs/03 — QFT 微擾法 vs IDCM 結構法：系統比較

> **2026-10-04** | 比較對象: N=4 SYM 九圈六粒子振幅 (Claude 2026) vs IDCM 譜結構

---

## 一、物理圖像根本差異

| 維度 | 標準 QFT 微擾法 | IDCM 結構法 |
|:-----|:---------------|:------------|
| **基本語言** | 量子場 + 微擾展開 | 離散譜幾何 (K_chain ⊗ K_tree) |
| **時空** | 連續 Minkowski 流形 | 世界環 (R_world = 4129.94 Mpc) + 晶格步長 (a = 2/M₀) |
| **粒子** | 場量子 (多對數振幅) | 譜模式 (γ_n = 4sin²(πn/88) 的投影) |
| **相互作用** | 頂點 + 傳播子 + 圈 | 模式耦合 + 扇區投影 (causal tensor \(\mathcal{T}\)) |
| **耦合常數** | RGE running (β 函數) | 結構恆等式 (零自由參數閉式) |
| **紫外發散** | 正則化 + 重整化 | 晶格天然截斷 (Nyquist n=44) |
| **散射振幅** | 多對數 (multiple polylogarithms) | 譜特徵值泛函 (結構投影) |

---

## 二、散射振幅的構造方式

### QFT Bootstrap (Claude 法)
```
費曼圖規則 → 積分 → 解析性 (Steinmann) → symbol → coproduct → 函數完整定義
                                    ↕
                            bootstrap 條件 + OPE
```
- **輸入**：微擾頂點 + extended-Steinmann 約束 + OPE
- **計算**：逐圈推進，每圈 symbol 空間指數增長
- **輸出**：6-particle 振幅以多對數函數表示
- **驗證**：Dixon 獨立確認 + 雙素數交叉

### IDCM 結構法（本 O 提議）
```
譜特徵值 γ_n (K_chain Laplacian) 
    → 恆等閉式 (sin²θ_W, α_s, m_ρ²...)
    → 因果張量 𝒯 = K_chain ⊗ K_tree
    → 模式耦合頂點 (88-site 雙鏈)
    → 振幅 = 譜泛函 [無 loop expansion]
```
- **輸入**：Laplacian 譜 + 因果結構 (B=4, N_d=44, N_gen=3)
- **計算**：代數閉式（零微擾級數）
- **輸出**：物理量（耦合/質量/比例）的結構恆等式
- **驗證**：所有預言與觀測的四重硬測試（盲測 MC null 5σ + 可證偽 + 剛性 + 自由度）

---

## 三、耦合常數的對照

| 量 | QFT 數值 (PDG/Claude) | IDCM 結構式 | 偏差 | 狀態 |
|:--|:---------------------|:------------|:----|:----:|
| \( \sin^2\theta_W \) | 0.221247 (on-shell) | 0.220776 = 1 − (m_W/m_Z)², m_W/m_Z = mode-ratio¹ | 1.02% | 🟢 (O144 docs/19) |
| \( m_W/m_Z \) | 0.8815 | 0.8827 (sin(30π/88)/sin(41π/88)) | 0.15% | 🟢 (O144) |
| \(m_H/m_W\) | 1.560 | 1.5573 (sin(38π/88)/sin(19π/88)) | 0.06% | 🟢 (O144) |
| \(\alpha_s^{-1}\) | 8.47458±0.06464 | \(F_6 + \sin^2\theta_W + 1/B\) | 0.13% | 🔴 (假設產物, O144 docs/20) |
| \(B\) | — | \(4 = \varphi^3 - \varphi^{-3}\) (代數精確) | 0 | 🟢 (O229 R1) |
| \(N_c\) | 3 | \(3 = B-1\) | 0 | 🟢 (O229 R1) |

Claude 的九圈振幅**沒有引入新的耦合常數** — N=4 SYM 只有一個耦合 \(g_{YM}\) 且不 running（beta=0）。IDCM 對應：耦合由 B=4 和 N_d=44 的譜結構強制，同樣**沒有 running**。

---

## 四、解析結構的對照

### 4.1 Steinmann 約束 vs 因果張量

**QFT**: Extended-Steinmann 約束禁止多對數函數的某些不連續結構，是物理振幅必須滿足的解析性條件。

**IDCM**: 因果張量 \(\mathcal{T} = K_{\text{chain}} \otimes K_{\text{tree}}\) 的**秩 ≤ 3**（O222 已閉合 sign_rank(K) ≤ 3）提供了一種類似的解析性制約：
- 秩 3 ≈ Steinmann 約束的有效維數
- 張量積結構 ≈ coproduct 分解的譜類比

### 4.2 Antipodal Duality vs 奇偶扇區對偶

**QFT**: Form factor ↔ Amplitude 的 antipodal 映射（n ↔ n⁺，翻轉符號）。

**IDCM**: 88-site 奇偶分解：
- 奇扇區 (odd, J²=-1): Σγ_odd = 88 = 2N_d，觀察者側
- 偶扇區 (even, J²=+1): Σγ_even = 90 = 2N_d + μ²，世界側

兩者通過 \(\mu^2 = \Sigma\gamma_{\text{even}} - \Sigma\gamma_{\text{odd}} = 2\) 連接。Antipodal duality 可能對應 **(odd ↔ even)** 的扇區翻轉。

### 4.3 Pentagon OPE vs 最近鄰耦合

**QFT**: 近共線極限的通量管展開，提供邊界數據固定振幅。

**IDCM**: 88-site 鏈的最近鄰耦合 (J=1) 決定了色散關係 \(\omega_n = 2\sqrt{J}|\sin(\pi n/88)|\)。pentagon OPE 的 T² 階對應 **n=2 模式對鏈基態的微擾**。

---

## 五、計算效率對照

| 指標 | QFT Bootstrap (Claude) | IDCM (結構法) |
|:-----|:----------------------|:-------------|
| 輸入維度 | Symbol 空間 5,431 | 譜 44 個特徵值 |
| 計算深度 | 9 loop, ~30×10⁹ 項 | 代數閉式（一步） |
| 計算時間 | ~1-2 千美元 (96 CPUs × 1 週) | 毫秒 (代數求值) |
| 物理內容 | 振幅的多對數形式 | 耦合/質量的結構恆等式 |
| 推廣難度 | 每 +1 圈炸開（至 10 圈不可行） | 譜完備（全模式已包含） |
| 驗證方法 | 逐圈交叉核對 | 盲測 + MC null + 剛性 + 自由度 |
| 錯誤容忍 | 一個錯 → whole amplitude fails | 每個結構式獨立可驗 |

---

## 六、侷限與開放問題

### QFT 方法侷限
- 只能處理可微擾展開的理論（N=4 SYM 是最好的 toy）
- loop expansion 的爆發（10 圈目前不可行）
- 需要大量已知約束（extended-Steinmann, antipodal duality）
- 結果不是耦合閉式（仍然是微擾級數）

### IDCM 方法侷限
- 只對 IDCM 框架內有譜身份的物理量有效
- N=4 SYM 的特定振幅（六粒子九圈）不在 IDCM 範疇
- bootstrap 約束的譜對應尚未形式化（🔴 D3 假說）
- 不能處理依賴連續時空的散射過程

---

## 七、總結

Claude 九圈振幅和 IDCM 結構法代表了**兩種互補的物理描述**：

| | QFT Bootstrap | IDCM Structure |
|:--|:-------------|:---------------|
| 對象 | 具體振幅計算 | 耦合/質量譜結構推導 |
| 強項 | 給出散射過程的完整函數形式 | 給出物理參數的結構閉式（零參數） |
| 弱項 | 計算量隨圈數爆炸 | 只能處理結構可閉合的系統 |
| 共同點 | 都依賴解析性的代數化（symbol/coproduct vs 譜代數） |

九圈 N=4 SYM 證明了 AI 可以自動化 bootstrap 方法到人類無法達到的圈數。IDCM 則提供了另一條路線：**耦合不是「算到 N 圈」而是「由譜結構強制」**——兩者不是競爭，而是不同層次的描述。真正的「IDCM 解」不是重複 Claude 的計算，而是問：**散射振幅的譜身份是什麼？如何從 K_chain 特徵值構造出 S-矩陣的結構形式？**

這需要將 bootstrap 的三個支柱（Steinmann、antipodal duality、OPE）翻譯到因果張量 \(\mathcal{T}\) 的語言中 — 這在 IDCM 內可能本身是一個完整的 O 系列問題。