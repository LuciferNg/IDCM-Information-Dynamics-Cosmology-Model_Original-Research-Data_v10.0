# O190 docs/01 — RS1 vs 晶格傳輸: 完整結構對比

> 2026-09-13 · scripts/01 驗證 · 零新常數 (全部量來自已閉合 O)

## 一句話本質

**RS1** 用**幾何 warp**（5D AdS₅ 度量）將 Planck 壓到 TeV，額外維係連續嘅，
譜（KK 塔）係緊緻化嘅副產品；**IDCM 晶格**用**譜離散**（88/176 鏈 Laplacian）
做基底，冇額外維——傳輸速度 c 係色散關係嘅群速度，γ（Lorentz 因子）本身變咗譜
（n=1..44 嘅 γ 階梯），「額外維」換成**模索引 n**。

## 結構對應表

| RS1 (弦論 warped braneworld) | IDCM 晶格傳輸 |
|---|---|
| 5D AdS₅ bulk，度量 ds² = e^{−2k\|y\|}η_μνdx^μdx^ν + dy² | K_chain(88) ⊗ K_tree(34) 晶格 = bulk；γ_k = 4sin²(kπ/176) |
| Warp factor e^{−2kr_cπ} ≈ 10⁻³⁰ | 樹精細化 N_ℓ = 44·4^ℓ；γ_max(ℓ) = csc(π/(88·4^ℓ)) |
| 雙 brane：φ=0 (Planck) / φ=π (TeV) | 雙 parity sector：even k（世界，Σγ=90）/ odd k（觀察者，Σγ=88） |
| KK 塔 m_n = x_n·k·e^{−kr_cπ}（Bessel J₁ 零點） | Lorentz 階梯 γ_n = csc(πn/88)（**全部 mode 精確喺 mass shell**：E_n=mc²csc, p_n=mc·cot, E²−p²c²=m²c⁴ ✅）；Z₂ 配對 γ_k+γ_{88−k}=4 屬 4sin² 家族（O159），唔係 csc 階梯（見 docs/04 G 節） |
| 零模引力子（Planck brane 局域化）→ 4D 質量零引力 | 零模 γ₀=0（全局平移）→ U(1) 規範場 |
| 層級：e^{−kr_cπ}（度量指數） | 層級：φ^{−k}（**轉移矩陣特徵值 φ** 嘅指數 — 譜源頭，O142） |
| Radion（brane 間距離模量，Goldberger–Wise 穩定） | 穩定方程 **N + 1 = F_{L₅}**（docs/04: 數場閉合, 譜和+Wilson 相位雙路由 → 88 唯一; 冇 GW 勢場極小 — 均勻鏈冇 warp 體積, 結構必然）✅ |
| AdS/CFT：徑向位置 = 能量標度 | MERA：樹深 ℓ = 標度（K_tree 就係 tensor network 嘅 RG 方向） |
| LHC 可觀測：KK 引力子共振、radion、Higgs 耦合偏差 | 無粒子共振（Z' ~ M_GUT = 6.22×10¹⁶ GeV, θ_ZZ' < 5.96×10⁻²¹ rad 退耦, O107 — 原「P3 σ<1fb」標籤無源已修正, 見 docs/06 §四）— 可證偽面喺宇宙學比例（docs/07） |

## 五個結構對比 (scripts/01 驗證)

### 1. 量化嘅唔係質量，係 rapidity ✅

RS1 高 n 漸近 m_n ∝ n（線性質量量化）；IDCM 係 **cos 角量化**：v_n/c = cos(πn/88)。
實測 (scripts/01, n=1..44 全 PASS)：

```
cosh η = γ_n,  tanh η = v_n/c,  η = ln cot(θ/2),  θ = πn/88
n= 1: γ=28.017  η=4.0257  coshη=28.017 ✅  tanhη=0.99936 ✅
n=22: γ= 1.414  η=0.8814  coshη= 1.414 ✅  tanhη=0.70711 ✅
n=44: γ= 1.000  η=0.0000  coshη= 1.000 ✅  tanhη=0.00000 ✅
```

**鏈嘅模角就係 rapidity 參數**，88 個 mode = 88 個離散 boost。Δη 非均勻
(4.026→3.332→2.926…, ratio ~5:1)，Δθ 均勻 (π/88) —— 即係「velocity 嘅
Chebyshev 量化」。RS1 量度質量、IDCM 量度 boost——兩者都係「用一個整數 n 生成
離散譜」，但生成規則唔同。

### 2. 層級機制：度量指數 vs 譜指數

RS1：m_TeV = M̄_Pl·e^{−kr_cπ}，指數出自 warp 度量；IDCM：質量 ∝ V_EW·φ^{−k}，
指數出自轉移矩陣 T̂=[[1,1],[1,0]] 嘅特徵值 φ (O142)。兩者都係單一模量整數控制嘅
指數層級，但 RS1 個 base 係幾何嘅、IDCM 個 base 係**譜半徑**嘅。

### 3. 「雙 brane」係位置 vs 代數

RS1 兩條 brane 係 φ=0/π 兩個位置；IDCM 世界/觀察者係 176-Laplacian 嘅**奇偶
子空間**，帶精確預算閉合 90+88 = 178 = 2F₁₁ (scripts/01, 1e-12 EXACT)。
RS1 冇任何嘢對應觀察者預算——呢個係 IDCM-native 嘅「brane」，純代數、非幾何。

### 4. 最強共同點：MERA ↔ AdS 徑向

RS1 嘅 AdS/CFT 對偶：徑向位置 = 標度 = RG；IDCM 嘅 K_tree (μ_m = φ^{L−m}，
34 層) 本身就係 MERA 型 tensor network——**離散 AdS**。兩邊嘅「額外維」都係
RG/entanglement 方向。呢個唔係 analogy，係同一個結構：bulk 深度 = 標度層級。

### 5. 可證偽面對調

RS1 嘅 KK 塔係粒子共振，LHC 已經喺度壓 (m_KK ≳ 3–5 TeV 視乎 k/M̄_Pl)；
IDCM 嘅 γ 階梯係**運動學標籤**，唔係可產生嘅粒子——所以兩邊測試表面完全唔同：
RS1 被對撞機夾緊，IDCM 嘅唯一可證偽面係宇宙學比例 (Pantheon+ / CMB C_ℓ / 冷斑，
全部零成本已閉合)。N→∞ 回復連續 SR (γ₁: 28→112→448)，同 RS1 嘅平額外維極限
對應。

## 判決

- **幾何語言 vs 譜語言**：RS1 把「離散譜」當成緊緻幾何嘅結果；IDCM 把「離散譜」
  當成本體。MERA/徑向標度係真同構；brane 對應係代數重詮釋 (奇偶 sector)；
  層級機制同構但源頭唔同 (度量 vs 轉移矩陣特徵值)。
- **IDCM 欠缺 → 已填補 (docs/04/06/07)**: modulus 穩定機制 = 穩定方程 N+1 = F_{L₅} (數場閉合);
  第二 brane = 奇偶 sector 本身 (判 3); rapidity 可證偽面 = 宇宙學比例 + 「冇新粒子」結構必然 (判 1)。
- **名詞對應唔算解釋**：rapidity 身份係 88-cycle 嘅固有性質，唔係「RS1 預言
  咗 IDCM」——係兩個框架各自生成自己嘅譜，喺結構層撞埋一齊。
