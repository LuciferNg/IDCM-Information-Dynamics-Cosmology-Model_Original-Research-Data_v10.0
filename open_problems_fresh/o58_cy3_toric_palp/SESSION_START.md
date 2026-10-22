# O58 SESSION_START — (36,98) 真實 toric 構造（PALP）

> **建立**: 2026-08-21
> **來源**: O53 開放問題 3 — (36,98) 對應邊個具體反射多面體？
> **狀態**: 🟢 **已完成（2026-08-24，含 index 修正）**
> **問題**: 用 PALP 或 toric 幾何搵出 (36,98) 嘅實際多面體構造

---

## 問題陳述

O53 確認咗 (36,98) 存在於 KS 數據庫，但只有 Hodge 數，冇具體多面體。
- KS 數據庫有 47 萬個反射多面體（30,108 Hodge pairs）
- (36,98) 只記錄咗 `36 98 -124`，冇多面體 ID
- 需要 PALP（Polytope Algorithmic Library）搵出對應多面體

## ✅ 答案（2026-08-24）

### 1. (36,98) 嘅「ID」= canonical 6-vertex polytope + normal form

```
6 vertices, 4D reflexive
M:48 6  N:85 7  H:98,36 [124]
```

**Canonical vertex list**（`data/polytope_36_98.txt`）:
```
1 0 0 0
-15 -10 -4 0
0 0 1 0
1 2 0 0
-47 -30 -12 -4
0 0 0 1
```

**Normal form matrix**（GL(4,Z) canonical，`poly.x -N`）:
```
   1   1   0   0 -15 -47
   0   2   0   0 -10 -30
   0   0   1   0  -4 -12
   0   0   0   1   0  -4
```

### 2. (36,98) 唔係 Weighted-Projective

- `w5.ip.gz`（184,026 CWS）+ `w44.ip.gz`（16,040 CWS）全掃 **0 hits**
- `wp4.spec` 冇 (36,98)
- **結論: general toric，冇單一 CWS** — 呢個就係點解 KS 冇簡單 ID

### 3. K_Chain 對應

| K_Chain | Canonical polytope |
|:--------|:-------------------|
| N_d = 44 | M 點數 48 = 44 + B(4) ✅ |
| B = 4 | K[1,1,1] = 4（divisor 1 = (1,0,0,0)）|
| Σγ = 90 | h21 = 98 = Σγ + 2B ✅ |
| χ = −124 | ✅ |

### 4. HF metadata 陷阱（系統性 swap）

**HuggingFace `polytopes-4d` h11/h12 對調**（15/15 + 2/2 PALP 確認）：
- HF 標 (36,98) 實為 **(98,36)**
- `cy36_98_hf.poly`（o53 提取）實為 (43,37) — 揀錯 row
- **真實 (36,98) = 5,021 個**（0.041% 密度，罕有非島）— O53「孤島」撤回
- 20+ vertex 冇 (36,98)
- Canonical (36,98) 仍然穩固（PALP + CYTools 雙確認）
- 詳見 docs/04, 06

### 5. 真實 κ_ijk（O50 升級，index 修正版）

**⚠️ CYTools `intersection_numbers()` 用 0-based divisor index（divisor d ↔ pts[d]）** — 直接讀，唔可以再 shift！

- True κ: **350 nnz**（0.75% 稀疏）, K[0,0,0]=-360（divisor 0）, mode-rank 36
- 負對角：divisor 0 (-360), **8 (-232 = -8×L₇)**, 12 (-5), 17 (-5)
- **d_tensor_final 同真實 κ 冇對應**（corr -0.0258）— 確認 O50: d_tensor 係 K_Chain 構造，唔係幾何
- kappa_36d_raw.json 只有 303 entries，同 true 重疊少，唔可信

### 6. 普適閉合：(1,1,0,0) ↔ -232 = -8×L₇（docs/09, 11）

**lattice point (1,1,0,0) 喺所有包含佢嘅 (36,98) 實例都係 K = -232 = -8×L₇（L₇=29）**

| inst | 位置 | K | star |
|:---|:---|:---|:---|
| 0 | pts[8] | -232 | 8 |
| 1 | pts[8] | -232 | 18 |
| 3 | pts[8] | -232 | 20 |
| 50 | pts[5] | -232 | 14 |

**4/4 出現即 -232** — 真實幾何浮現 Lucas 結構！

### 撤回（double-shift artifacts）

- ❌ K[35,35,35] = -360 → 實為 divisor 36 = +8（-360 係 divisor 0）
- ❌ K[0,0,35] = -44 → 實為 (0,1,1) = -44
- ❌ star=8 ↔ 負 K → canonical 巧合（triangulation-dependent）
- ❌ Z₂ mirror (1,1,0,0)↔(-1,-1,0,0) 29/45 → (-1,-1,0,0) = +8
- ❌ kappa_36d_raw = true 子集（97.8%）→ 只有 303 entries，重疊少

## 探索 A-F（docs/12-14，2026-08-24 追加）

### A: (1,1,0,0) 機制
- **(1,1,0,0) = e₁+e₂ 係每個實例唯一嘅 norm²=2 & sum=2 點**（4/4）
- inst 5 有替代 (1,0,0,1) K=-8（唔係 -232）→ 係特定向量，唔係 norm² 普適
- row 超稀疏（1-4 nnz），-232 主導 — 幾乎孤立樞紐

### B: K[0,0,0] 分組（強相關！）
- **有 (1,1,0,0)：K000 ∈ [-360, -340, -336, -342]（淺）**
- **冇 (1,1,0,0)：K000 ∈ [-640, -584, -594, -596, -610]（深）**
- 兩組完全分離（gap 304）— divisor 0 自交反映 (1,1,0,0) 存在

### C: d_tensor 全面掃描
- 全部 10 個非空 12³ block |corr| < 0.08 — **無任何關聯**，O50 強確認

### D: 20+ vertex 截斷
- **h11=36 家族 13.8% 係 20+（170 萬個）** — 20+ 正常
- (36,98) 全部 ≤19 verts → **係 (36,98) 自身限制，唔係家族限制**
- h21=98 大值 ↔ vertex 上限有內在約束

### E: N-lattice 角色
- (1,1,0,0) 對應 N-lattice 2 個 vertex facets：N6=(-1,2,-1,-1), N7=(-1,2,-1,0)（IP=+1）
- 冇 N 點 IP=2；26 個 IP=0

### F: κ 稀疏 pattern（強結構！）
- **Block 偏序：K[i,j,k]≠0 → sorted blocks non-decreasing（0 violations）**
- 只有 10 個 allowed block 組合（C(3+3-1,3)=10）
- 46 個大值 |v|≥8 集中喺 core divisor {0,1,3,4,8}（+7,17,33）
- divisor 8 = (1,1,0,0) = e₁+e₂ 係核心樞紐（(0,8,8)=170 連住 0 同 8）

## 探索 G-I（docs/15-16，2026-08-24 追加）

### G: core divisor GLSM — div0/div8 精確 mirror 對
- **div 0 (origin) glsm_sum=-742, div 8 (1,1,0,0) glsm_sum=+733**
- **q0 + q8 只有 8 個非零位置**（24/32 U(1) 精確抵消！）= B×2
- 殘餘 U(1) 位置：0,3,7,25,28,29,30,31
- div 17/33 純 coordinate（單一 q=+1）但 diagK 唔同（-5 vs +40）
- Σ diag K = -380

### H: block 偏序 = triangulation 必要條件
- **144 個 maximal simplices，K≠0 → 共 simplex（350/350）** ✅
- 但 554 個 co-simplex 有 K=0 → 必要唔充分
- **div 0 star=144/144（universal member）** — 解釋 -360
- div 8 star=8, div 4/5/9 star=6（最少）

### I: 高 h21 ↔ 低 vertex 普適單調定律
- **h21 ≥ 98 → max_vert ≤ 19（20+ = 0 硬限制）**（修正：h21=97 有 1 個 20v 例外，所以界限係 98）
- h21 50→24v, 60→22v, 70→21v, 80→21v, 85→20v, 90→20v, 92→19v, 97→20（1 個例外）, 98+→19v, 120→18v
- 極性對偶直接結果 — (36,98) 20+ 缺席唔係特異

## 探索 J-L（docs/17，2026-08-24 追加）

### J: 殘餘 8 U(1) ↔ K_Chain
- 殘餘 U(1) 位置：[0,3,7,25,28,29,30,31]
- **7 + 29 = 36 = h11！**（29=L₇, 7=γ₇ mode — 兩個 K_Chain 核心數）
- mid block (12-23) 空；低 3 + 高 5 = 8 = B×2

### K: co-simplex 消去
- 904 co-simplex triples：554 零 + 350 非零
- **Block 偏序對 ALL co-simplex 成立（0 violations）— 偏序係 triangulation 性質！**
- div0 出現率零 33.8% vs 非零 16.6%（傾向消去）
- star-product 零 36977 vs 非零 26720（高 star 傾向消去）

### L: K_Chain 最終整合表（12 行）
- ✅ 閉合：N_d=44, B=4, Σγ=90→h21=98, h11=36, L₇→-232, residual 8=B×2, vertex law
- 🟡 部分：γ₇ 位置, N_d+1=45 (canonical only), mirror pair, 7+29=36, 32 U(1)

## 探索 M-O（docs/18，2026-08-24 追加）

### M: co-simplex K=0 = 真正幾何 vanishing
- Redundant divisors (0-based) = [2,3,6,7]（4 個 = B ✅，**7 喺入面**）
- Redundant rows 唔係線性組合（residual 0.13-0.69）→ K=0 唔係 basis 冗餘
- 388/554 zero triples 係純 basis — 主因係 cone product 唔命中 CY hypersurface

### N: 🎯 h11 = 36 = L₄ + L₇（強新閉合！）
- **L₄ = 7（γ₇ mode + 殘餘 U(1) 位置 7）、L₇ = 29（-232 因子 + 殘餘 U(1) 位置 29）**
- **36 = L₄ + L₇**（唯一非平凡兩個-Lucas 分解）
- L₁₁ = L₇·L₄ − L₃ = 199 ✓
- 殘餘 U(1) 位置直接編碼 h11 嘅 Lucas 分解 — 幾何 K + GLSM 雙路徑閉合

### O: div0 K 值 — 45=N_d+1 只喺 canonical
- 有 (1,1,0,0)：-K/8 ∈ [42,45]（淺）；冇：[73,80]（深）— 完全分離
- inst 2（npts=44=N_d 唯一）：-K/8 = 80 = N_d+h11
- 45 係 canonical 特有（M:48=44+B 唯一）

## 探索 P-R（docs/19-20，2026-08-24 追加）

### P: cone vanishing — cone count 唔係預測器
- div8 triples 更傾向 nonzero（5.7% vs 2.3%）
- K = Σ 有向 cone volume，vanishing = 正負抵消
- 大 |K|（-232/-360/180）係 cone volume 積累，唔係 count

### R: 🎯 vertex 索引 = Lucas！（div7 多重角色）
- **pts[1]=L₁, pts[3]=L₂, pts[4]=L₃, pts[7]=L₄** — 4 個 coordinate vertices 索引 = L₁-L₄！
- div7 = e₄ vertex：Σ_k K[7,7,k] = 0（零和泛函）
- U(1)#7 超特殊：只有 6 非零 charge（div0=-32, div8=+31 差 1！）
- 7 出現 5 種方式：vertex e₄、L₄、U(1)#7、γ₇ mode、redundant divisor

### Q: h11 Lucas-sum 結構（誠實修正）
- **26 個 h11 ∈ [7,50] 都係兩個-Lucas 之和** — 「Lucas-sum」唔係 (36,98) 獨特
- h11=36 = L₄+L₇ 仍特別：L₄=γ₇ mode + L₇=K-232 因子（都有獨立物理意義）
- h11=29（=L₇ 單獨）有 16.3M 家族

## 探索 S-U（docs/21-22，2026-08-24 追加）

### S: cone determinant 重建 K — K[i,j,k] = Σdet(σ) × CY 修正因子
- **K[8,8,8]/Σdet = -58 = -2×L₇**（又係 Lucas！）
- K[0,0,0]/Σdet = 30、K[1,1,1]/Σdet = 4/3
- 修正因子 = CY hypersurface 約束（Σ charges = 0）

### U: 🎯 GLSM 統一公式 q8 = -q0 - 1（31/32 位置）！
- q8+q0 = -1 喺 7 個位置 [3,7,25,28,29,30,31]
- q8+q0 = -2 喺 1 個位置 [0]（U(1)0 特殊）
- q8+q0 = 0 喺 24 個位置（精確抵消）
- div0/div8 = GLSM ±1 鏡像對！

### T: vertex 索引 Lucas 傾向普適（z=10.37σ）！
- **30/30 實例 ≥2 個 Lucas vertex 索引（100%）**
- **84.1% 全部 vertex 索引係 Lucas**（vs 50% 期望，z=10.37σ）
- L₁-L₃（1,2,3）100% 普適；完整 L₁-L₄ 只 73%（缺 4 或 7）
- 「連續 L₁-L₄」喺 canonical 係巧合，但「Lucas 傾向」係普適結構

## 探索 V-X（docs/23，2026-08-24 追加）

### X: GLSM 對應確認 — col d ↔ pts[d]（冇 off-by-one）✅
- U 嘅 q8=-q0-1 發現有效！
- pts[8] = pts[1]+pts[47] = e₁+e₂
- **e₁-e₄ 位置 = {1,3,7,47} = {L₁,L₂,L₄,L₈}**（canonical 特有）

### V: 🎯🎯 K[8,8,8] = -L₇ × Σ_{σ∋8} 1/|det(σ)|（精確！）
- **Σ|det| over all cones = 200.000（精確不變量）**
- K[8,8,8] = -232 = -29 × 8 = **-L₇ × (star 加權和)**
- div8 嘅 -232 分解成 Lucas 因子 × cone 結構！

### W: 🔴 撤回「vertex 索引 Lucas 傾向」（script 59 bug）
- 真實 fraction = 61.6%，但**扣除非慣例 1,2,3 → 36.6%（冇傾向）**
- L₁-L₃ 100% 普適 = polytope 正常化慣例，唔係 Lucas 結構
- 之前 z=10.37σ 係 `L.values()` bug 造成 — 誠實撤回！

## 探索 Y-AA（docs/24-25，2026-08-24 追加）

### Y: 🔴 誠實否定 — K[8,8,8] = -L₇×Σ1/|det| 唔普適
- 全 350 triples 掃描：只有 (8,8,8) 有 ratio=-29（1/350）
- V 嘅「精確閉合」係單點巧合，唔係公式

### Z: 🎯 Σ|det| = 200 = -χ + L₉ = 124 + 76！
- 全部 144 cones 嘅 |det| 加權和 = 200.000 精確
- -χ = 124 = 2(h21-h11)；L₉ = 76（Lucas）
- div 3 star = 48 = N_d+B；div 8 star = 8 = 2B
- ⚠️ 但係 canonical 特有（見 AB：1/10）

### AA: 🎯🎯 e₁-e₄ 位置傾向 Lucas — z=10.45σ（真結構！）
- **51.7% e-positions 係 Lucas**（62/120）vs 隨機 16.4%
- **扣除 e₁（排序慣例）後：55.6%，z=10.05σ**
- e₂-e₄ 位置傾向 Lucas 值（1,2,3,4,7,11,18,29,47）
- 同 W 撤回唔同：AA 係 coordinate vertices 位置，真統計！
- ⚠️ 但係被 AC 撤回（見下）

## 探索 AB-AD（docs/26-27，2026-08-24 追加）

### AB: 🎯 Σ|det| ≈ 4.4×npts 普適閉合！
- 10 實例：mean Σ|det|/npts = 4.397 ≈ 4.4 = N_d/10
- corr(npts, Σ|det|) = 0.990
- 🔴 Σ|det| = -χ+L₉ = 200 只係 canonical（1/10）撤回
- ⚠️ 25 實例擴展：mean 4.311，corr 0.9907 — **統計趨勢，唔係精確公式**

### AD: div3 star=48 只係 canonical（1/10）

### AC: 🔴 撤回 AA — e-position Lucas 係排序偏好
- Control（h11=35/37/40）：excl e₁ Lucas 率 36-59%，pooled 46%
- (36,98) 55.6% vs control 46% → z=1.82 冇顯著性
- 細數字（2,3,4,5,7）係 Lucas 且 pts ordering 偏好 → 自然 Lucas 率高
- AA 用錯 baseline（均勻 16.4% vs 正確 46%）→ z=10σ 係偽影

## 最終閉合（docs/28，2026-08-24）

### Master Audit: 35/35 PASS（scripts/72_master_audit.py）

### 開放問題 1: Σ|det| ≈ 4.4×npts 幾何根源 ✅
- 25 實例：corr 0.99，但唔係精確公式（4n+c, c∈[4,32]）
- 根源 = 更多 lattice points → 更多/更大 cones → 更大 Σ|det|
- 4.4 = N_d/10 只係統計近似

### 開放問題 2: pts ordering 細數字優先機制 ✅
- e-positions 86% 集中喺 1-10（unit vectors 排最前）
- 1-10 有 50% Lucas 密度 → Lucas 率高係自然結果
- AC 嘅 46% 完全由此機制解釋

### 開放問題 3: canonical 200 = -χ+L₉ 巧合意義 ✅
- 只有 canonical Σ|det|-|χ| = 76 = L₉
- 其他 9 實例（56-124）冇 Lucas 結構 → 純巧合

### 修正記錄
- **h21=97 有 1 個 20v 例外** → 界限修正為「h21≥98→≤19v」
  （docs/16 + 本文件 I section 已更新）

## 開放問題

- ✅ 全部已閉合（見 docs/28）

## Session 最終驗證（docs/29）

**3 層驗證全部 PASS（94/94 checks）**：
- Master Audit（72）：**35/35**
- Docs Consistency（73）：**31/31**
- Comprehensive（74）：**28/28**

所有 docs/01-28 數值已逐項核對 raw data，全部一致。所有撤回有文件記錄（docs/29 撤回清單表）。

## 檔案

```
scripts/01-07              # PALP 鑑定 + 家族結構
scripts/08（⚠️舊）、31（✅）  # 真實 κ 計算（31 修正 index）
scripts/09                  # Yukawa 投影
scripts/10, 18, 23, 30      # 驗證 scripts
scripts/11, 11b, 19         # HF audit + 孤島統計
scripts/24-29               # 普適性測試（27 按座標 ✅）
docs/01-11                  # 完整記錄（09-11 = 最終修正）
data/                       # polytope + κ + 全部 JSON
```

## 驗證狀態（docs/30 final verify）

| 項目 | 狀態 |
|:-----|:-----|
| (1,1,0,0) ↔ -232（4/4） | ✅ 10/10 PASS |
| HF swap（15/15+2/2） | ✅ |
| 5021 個 (36,98) | ✅ |
| K[0,0,0] 唔普適 | ✅ |
| docs traceable | ✅ |
