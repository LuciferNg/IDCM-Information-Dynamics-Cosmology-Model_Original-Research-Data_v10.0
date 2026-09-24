# O211 docs/01 — 生成算子 G：定義與譜不變量

> **日期**: 2026-09-24
> **性質**: 交付物 #1（R1）— 生成算子 G 嘅形式定義（O210 型別語言）
> **驗證**: `scripts/01_generating_operator.py` — **16/16 PASS**（`data/01_output.txt`）
> **前置**: O210 docs/01（型別系統）、O56（moduli 鎖定）、O57（beat 空間）

---

## 一、問題

現行 `src/projection_operator.py` 將 CY₃(36,98) 當成**輸入**：

```python
h11 = 36   # 硬編碼
h21 = 98   # 硬編碼
```

O211 要嘅係「**譜代數 → 生成算子 G → 幾何係像**」。所以第一步係定義 G，並且要
證明 G 嘅譜不變量**全部係精確代數身份**（唔係擬合、唔係硬編碼）。

## 二、G 嘅定義

### 2.1 載體

$$\mathcal{T} = K_{\text{chain}} \otimes K_{\text{tree}}$$

- $K_{\text{chain}}$：44-site 世界鏈（88-site 對偶鏈之半）
- $K_{\text{tree}}$：MERA 分支樹，分支算子 $\hat{B}$

### 2.2 生成鏈（唯一輸入 = 種子方程）

| 步 | 對象 | 型別 | 公式 | 值 |
|:-:|:-----|:----:|:-----|:--:|
| 0 | 種子 | — | $x^2 + x - 1 = 0$ | — |
| 1 | $\varphi$ | Sc | $(1+\sqrt5)/2$ | 1.618… |
| 2 | $\hat{B}$ 本徵值 $B$ | Sc | $\varphi^3 - \varphi^{-3}$ | **4** |
| 3 | $L_5$ | Sc | $\varphi^5 + (-\varphi)^{-5}$ | **11** |
| 4 | $N_d$ | Sc | $B \cdot L_5$ | **44** |
| 5 | $\hat{\gamma}$ | **Op** | $B \cdot \sin^2\!\left(\dfrac{\pi \hat{H}}{2N_d}\right)$ | $\gamma_n = 4\sin^2(\pi n/88)$ |
| 6 | $\hat{\Pi}_{2B}$ | **Op** | K_tree 邊界投影（$B$ 分支 × 2 邊界 site） | $\mathrm{rank} = 2B = 8$ |
| 7 | $\mathbf{G}$ | **Op** | $\mathbb{1}_{K_{\text{chain}}} + \hat{\gamma}$ | — |

其中 $\hat{H} = \mathrm{diag}(1, 2, \dots, N_d)$ 係 site 指標算子。

> **★ 統一寫法**：$\gamma_n = B \cdot \sin^2(\pi n / 2N_d)$ — **振幅 = $B$（K_tree 分支），
> 頻率 = $2N_d = 88$（對偶鏈長）**。呢個係 O36/O95 嘅 $\gamma_n = 4\sin^2(\pi n/88)$ 嘅
> 因子分解：兩個「4」係同一件事（$B = 4$）。

### 2.3 G 係乜

$$\boxed{\;\mathbf{G} := \mathbb{1}_{K_{\text{chain}}} + \hat{\gamma}\;}$$

$\mathbf{G}$ 係**梯度維數算子（graded dimension operator）**：佢嘅跡就係「site 維數 +
譜維數」。呢個係本 O 嘅核心對象 —— **moduli 總數 = $\mathbf{G}$ 嘅跡**。

## 三、譜不變量（全部精確，`scripts/01` 驗證）

| # | 不變量 | 值 | 性質 |
|:-:|:-------|:--:|:-----|
| C1 | $\varphi^2 = \varphi + 1$ | — | 種子方程 |
| C2 | $B = \varphi^3 - \varphi^{-3}$ | 4 | sympy 精確 |
| C3 | $L_5 = \varphi^5 + (-\varphi)^{-5}$ | 11 | sympy 精確 |
| C4 | $N_d = B \cdot L_5$ | 44 | sympy 精確 |
| C5 | $\gamma_{22} = 2$ | 2 | 精確（mid-point） |
| C6 | $\gamma_{44} = B$ | 4 | 精確（Nyquist） |
| C7 | $\mathrm{Tr}\,\hat\gamma = \sum\gamma = \dfrac{B(N_d+1)}{2}$ | **90** | ★ **精確閉式** |
| C8 | $\gamma_n + \gamma_{N_d-n} = B$ | 4 | ★ Z₂ 對偶（全部 $n$，精確） |
| C9 | $\mathrm{Tr}\,\mathbf{G} = N_d + \sum\gamma$ | **134** | 精確 |
| C10 | $\mathrm{rank}(\hat\Pi_{2B}) = 2B$ | 8 | 定義 |
| C11 | $h^{11} = \mathrm{Tr}(\mathbb{1} - \hat\Pi_{2B}) = N_d - 2B$ | **36** | 零輸入 |
| C12 | $h^{21} = \mathrm{Tr}(\hat\gamma + \hat\Pi_{2B}) = \sum\gamma + 2B$ | **98** | 零輸入 |
| C13 | $h^{11} + h^{21} = \mathrm{Tr}\,\mathbf{G}$ | 134 | $2B$ 相消 |
| C14 | $h^{21} - h^{11} = \sum\gamma - N_d + 4B$ | 62 | 耦合判別者 |
| C15 | $\chi = 2(h^{11} - h^{21})$ | −124 | — |

### ★ C7 嘅精確閉式（本 O 新增）

$$\sum_{n=1}^{N_d} \sin^2\!\left(\frac{\pi n}{2N_d}\right) = \frac{N_d + 1}{2}$$

證明：$\sum_{n=1}^{2N_d-1} \sin^2(\pi n/2N_d) = N_d$；由對稱 $\sin^2(\pi n/2N_d) =
\sin^2(\pi(2N_d-n)/2N_d)$ 得 $\sum_{n=1}^{N_d-1} = (N_d-1)/2$，加 $n=N_d$ 項
（$\sin^2(\pi/2)=1$）得 $(N_d+1)/2$。$\square$

⟹ $\sum\gamma = B \cdot (N_d+1)/2 = 4 \times 45/2 = 90$ **精確**，唔係數值巧合。

## 四、型別檢查（O210 四型系統）

| 對象 | 型別 | 說明 |
|:-----|:----:|:-----|
| $\mathbf{G} = \mathbb{1} + \hat\gamma$ | `Op` | 生成算子 |
| $\hat\gamma$ | `Op` | K_chain 譜算子 |
| $\hat B$ | `Op` | K_tree 分支算子（rank $B$） |
| $\hat\Pi_{2B}$ | `Op` | K_tree 邊界投影 |
| $\mathrm{Tr}$ | `Fn` | 跡泛函 |
| $\gamma_n$ | `Sc` | $\hat\gamma$ 嘅第 $n$ 個成員 |
| $N_d$, $\sum\gamma$ | `Sc` | $\mathrm{Tr}\,\mathbb{1}$, $\mathrm{Tr}\,\hat\gamma$ |
| $I_{44}$, $I_{88}$ | `Ix` | 指標集 |

10 條目、**0 型別錯誤**（C16）。符合 O210 T0 判準：$h^{11}, h^{21}$ 都有產生對
$(\mathrm{Tr} \circ \text{Proj}, \hat\Pi_{2B})$，**唔係 ad hoc 常數**。

## 五、同舊架構嘅差別

| | 舊（`src/projection_operator.py`） | 新（O211） |
|:--|:--|:--|
| 方向 | 幾何 → 投影 | **譜 → 生成算子 → 幾何係像** |
| $h^{11}$ | 硬編碼 `36` | $\mathrm{Tr}(\mathbb{1}-\hat\Pi_{2B})$ |
| $h^{21}$ | 硬編碼 `98` | $\mathrm{Tr}(\hat\gamma+\hat\Pi_{2B})$ |
| $P$ | 人手設定（5 條律 + ad hoc 權重） | 由 $\mathbf{G}$ 導出（見 docs/04） |

## 六、誠實標記

| 項目 | 狀態 |
|:-----|:----:|
| $\varphi, B, L_5, N_d, \gamma_n$ 由種子導出 | 🟢 精確（sympy） |
| $\sum\gamma = B(N_d+1)/2$ 閉式 | 🟢 精確（本 O 證明） |
| $h^{11}, h^{21}$ 由 $\mathbf{G}$ + $\hat\Pi_{2B}$ 導出 | 🟢 零輸入 |
| $\hat\Pi_{2B}$ 嘅「2 邊界 site / 分支」具體實現 | 🟡 引用 O56 §3.1 嘅耦合機制；**具體 lift 哪 8 個 mode 係約定（見 docs/05 §2）** |
| $\mathbf{G}$ 嘅譜是否唯一決定 $\hat\Pi_{2B}$ | 🔴 未證（見 docs/05） |
