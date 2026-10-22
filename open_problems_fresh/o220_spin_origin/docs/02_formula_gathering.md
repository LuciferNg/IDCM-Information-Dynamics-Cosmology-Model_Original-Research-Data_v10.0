# O220 docs/02 — 公式盤點（RAG + skills 檢索結果）

> **日期**: 2026-09-28（O220 第一輪）
> **方法**: `idcm_rag_search`（version = `v10.0`，5 條 query）＋ skills
> （`o-series-research-workflow`、`idcm-rag-search`、`idcm-quantization-workflow`）
> **規則**: 本盤點為**引用**（引用唔重驗）——下游只喺本 O 驗後果；每條附出處路徑。

---

## 一、RAG query 與命中（idcm-v10-0 collection）

| # | Query | 主要命中 |
|:-:|:------|:---------|
| Q1 | 自旋 spin spinor spin-1/2 來源 holonomy 720 度 Wilson line 半整數 | `o160/scripts/23_spin_720.py`、`o160/docs/22_spin_720.md`、`o161/scripts/02_link_variables.py`、`o158/scripts/18_hw_spin_pure_world.py`、`o168/scripts/07_half_source.py` |
| Q2 | Dirac 方程 spinor 費米子 量子化 K_chain Clifford γ 矩陣 | `o137/scripts/05_fermion_quantization.py`、`o139/docs/02`、`o140/docs/02`、`bbn/01_problem_record.md` |
| Q3 | 手性 chirality 時間箭頭 time arrow 方向性 rotation CMB | `o213/scripts/07_arrow_directionality.py`、`o213/docs/09_chirality_absolute_orientation.md`、`o213/docs/06_arrow_directionality.md`、`o137/SESSION_START.md`（手性雙重角色） |
| Q4 | spin-statistics Pauli 交換反對稱 2π 相位 | `o137/docs/03_derivation_audit.md`（弱）、`o125/docs/02`、`o10/01_problem_record.md`（**無直接命中** ⟹ 自旋統計在 IDCM 未系統推導 = 本 O 缺口） |
| Q5 | 角動量 angular momentum 自旋 宇宙旋轉 ring 繞數 | `o175/scripts/04_angular_momentum.py`、`o175/docs/04_angular_momentum.md`、`o124/docs/09_irreducible_inputs.md §2.2`（繞數係整數） |

★ **檢索結論（缺口定位）**：IDCM 已有 (a) Wilson line = i、(b) 720° = 352、(c) 費米子反週期量子化、
(d) 手性 = 絕對定向、(e) helicity 算子 ĥ = −I 五塊**碎片**，但**冇**任何一處把它們統一成
「自旋是什麼」。Q4 尤其空 —— **自旋統計定理在 IDCM 從未被推導**（呢個係 O220 之核心缺口）。

---

## 二、公式清單（逐條附出處）

### 2.1 鏈譜與扇區（176-鏈慣例）

| 公式 | 值 | 出處 |
|:-----|:---|:-----|
| γ_k = 4sin²(kπ/176) | — | O211 / O161 |
| ω_k = 2sin(kπ/176) | — | O137 / O125 |
| μ² = γ₄₄ = 2 | 2 | O160 T7（中心模定理） |
| γ_{44+j} + γ_{44−j} = 2μ² = B = 4 | 4 | O211（鏡像和） |
| Σγ_odd = 88 = 2N_d | 88 | O211 |
| Σγ_even = 90 = B(N_d+1)/2 | 90 | O211 |
| 扇區: e^{i·88·2θ_k} = (−1)^k | ±1 | O159 A3 / O161 C5 |
| Σ√γ = 1 + cot(π/176) EXACT | 42.0055 | O215 |

### 2.2 ★ 自旋／輸送（本 O 之核心輸入）

| # | 公式 | 值／性質 | 出處 |
|:-:|:-----|:---------|:-----|
| S3 | U_k = e^{i2θ_k} = e^{ikπ/88}（site-link phase；= D-D 行波每 site 相位） | — | O161 C1 |
| S3b | γ_k = \|1 − U_k\|² | dev 6e-61 | O161 C1 |
| S4 | Π_{k=1..88} U_k = e^{i·44.5π} = **i** | 精確 | O161 C4 |
| S4b | 總相位 44.5π = (F₁₁/2)π = 89π/2；winding 22.25 = F₁₁/4 = 2L₅ + ¼ | — | O161 C4 / O175 docs/04 |
| S4c | 世界側（even k）= e^{i22.5π} = i；觀察者側（odd k）= e^{i22π} = 1 | — | O161 C4 |
| S4d | i² = −1 = J²（反週期）；i⁴ = +1 ⟹ 352 閉合 | — | O161 C4 |
| S5 | 步數 ↔ 角度: 44 步 = 90°、88 = 180°、176 = 360°、352 = 720°（步數 = 角度 × 44/90） | 表 | O160 T23 |
| S6 | 費米子: nL ≡ N_d (mod 2N_d) ⟺ nL/88 ∈ ℤ+½；玻色子: nL ≡ 0 (mod 88) | — | O137 Phase 1 |
| S6b | 六費米子候選 (e,μ,τ,s,c,b) 之 (n,L) 配對；L ∈ {B, 2B, L₅, N_d/2, N_d} | — | O137 Phase 1 §2.2 |
| S6c | 純玻色子模式 = {n ≡ 0 mod 8} = {8,16,24,32,40} | — | O137 Phase 1 §2.3 |
| S7 | helicity 算子 ĥ = A₅ 反演（88-grid），ĥ² = 1，譜 {+1×44, −1×44}，無固定點 | — | O125 §5 |
| S7b | 16 helicity 組態 → 6 存活 (MHV) = 2N_gen | 6 | O125 §4 |
| S8 | Spin 域規則: Spin-0 ⟹ 88 域；Spin-1 ⟹ 176 域 (21,24)；Spin-1/2 ⟹ 176 域 (13,32) | — | O158 scripts/18 |
| S9 | 有序旋轉 = 鏈相位繞數（非引力裝配）；Noether Q = 44 守恆 | — | O175 docs/04 / O161 |
| S10 | 繞數係整數：總反常相位 = 繞數 × 2π；F₁₁ = k + B·Δα⁻¹ = 53 + 36 = 89 | — | O124 docs/09 §2.2 |

### 2.3 手性與時間箭頭

| # | 公式 | 值 | 出處 |
|:-:|:-----|:---|:-----|
| H1 | A₅ 60-軌道 = 精確 I-軌道（proper 偏差 9.7e-5°）；improper 偏差 5.3402° | — | O213 docs/09 |
| H2 | \|Sym(A₅)\| = 60（全 det = +1）⟹ **嚴格手性**；RH（I·(1,1,φ³)）= 120 ⟹ 非手性 | — | O213 docs/09 |
| H3 | 手性偽標量 χ = sign(x₀·â)·δ_m = ±2.670063°（反射下 χ → −χ） | 2.670063° | O213 docs/09 |
| H4 | 對極接近 5.340200° = 2δ_m（dev 1.3e-3%） | — | O213 docs/09 |
| H5 | 四型 I-軌道: 12/20/30 必為中心對稱（非手性）；**只有 60-軌道可手性** | — | O213 docs/09 §3 |
| H6 | 手性承重: 手性 ⟹ 9 模式 {1,2,3,4,5,7,9,11,13} = N_gen²；非手性 ⟹ 24 模式 | — | O137 docs/29 §3, O213 docs/09 §5 |
| H7 | δ := ∏_{a∈A2}(a·x) = 第 15 次不變調和（deg 15 = #H₃ 鏡面）；m₁₅ = κδ² | — | O137 docs/29 §2 |
| H8 | 模式數 = 群之函數: C/D→1, T→2, O→5, **I→9**（唯一） | — | O137 docs/29 §5 |
| H9 | 時間箭頭: 不可逆（decimation many-to-one ΔS = 91.5/366 nats）× 方向性（前向函數 vs 後向關係）；IDCM 冇起始 ⟹ 箭頭係結構 | — | O213 docs/06 |
| H10 | 絕對定向 = A₅ 手性；ULCDM 需 Past Hypothesis，IDCM 零外部輸入 | — | O213 docs/09 §7 |
| H11 | κ 閘極 = γ_max⁻² = B⁻² = 1/16；冪等 + 非可逆 ⟹ 定向算子 | 1/16 | O164 / O213 docs/06 |
| H12 | 環: ω_ring = c/R_world；τ = 1/ω_ring = 13.470063 Gyr；T_ring = 84.6349 Gyr | — | O73 裁定 / O213 docs/06 |

### 2.4 88-grid 對稱（手性視實現）

| # | 事實 | 出處 |
|:-:|:-----|:-----|
| G1 | canonical 88-grid \|Sym\| = 4 = {+1: 2, −1: 2} ⟹ **非手性**（含 −I） | O182 |
| G2 | 冷斑 A₅ 軌道 88-grid \|Sym\| = 2 = {+1: 2} ⟹ 手性 | O182 |
| G3 | 88-grid 唔係 data-gated 而係 **anchor-依賴**（Gs 下最大偏差 16.1070°） | O223 docs/07 |
| G4 | 手性角 2δ_m = 180° − d(0,57) = 5.340114°（30/30） | O223 docs/06 |
| G5 | δ_m = 2.670063° 係定向 null 第 57.8 百分位 ⟹ 典型值，非結構強迫 | O223 §9.2 |

---

## 三、skills 檢索結果

| Skill | 用於本 O 之內容 |
|:------|:---------------|
| `o-series-research-workflow` | O-series 骨架、驗證紀律、`references/o160-spin-720-holonomy-20260908.md`（自旋 720° = 家族四下界）、密碼基線入場券、剛性測試、假說被證偽 = PASS |
| `idcm-quantization-workflow` | Dirac 結構由 K_chain: γ^0 = σ₁⊗I₂、γ^i = iσ₂⊗σ_i、γ^5 = −σ₃⊗I₂（**legacy v9/v10 前工作流，本 O 標 🟡 引用**）；陷阱表（D² 唔對角、P_L 與 γ⁵ 對易） |
| `idcm-rag-search` | RAG 版本隔離查詢；v10.0 collection = `idcm-v10-0` |

> ⚠️ `idcm-quantization-workflow` 之 γ^μ 構造係 legacy（v9 連續 QFT 期）。v10.0 之紀律係
> **離散有限譜**（`sm-quantization-from-kmatrix`：冇 continuum limit、冇 RGE）。本 O 嘅自旋
> 推導**唔用** γ^μ 連續構造，只引用其「Dirac 結構由 K_chain 派生」之原則。若日後要寫
> Dirac 方程，須先裁定用邊個版本之約定。

---

## 四、本輪由盤點得出之三項判斷

1. **缺口確認**：自旋統計定理（Q4）在 IDCM **零命中** ⟹ 唔係「已答但散落」，而係**真未推導**
   ⟹ O220 有實質新內容，唔係重複勞動。
2. **五塊碎片指向同一算子**：Wilson line（S4）、費米子反週期（S6）、helicity 對合（S7）、
   扇區 Z₂（S3b）、Spin 域規則（S8）—— 全部係「一個 Z₂ / Z₄ 分級」之不同呈現
   ⟹ 統一語言 = **鏈 transport 之 holonomy 類**。
3. **手性 → 定向 → 時間** 三塊（H1–H12）已閉合，**缺嘅係中間環節「定向 + Z₄ ⟹ 自旋」**
   ⟹ 正好係本 O 之核心命題（見 `docs/01` §一）。

---

## 五、誠實標記（引用時必須知道）

- ⚠️ **O161 C4/C5 之文件行「4×88 = 352 = 2×176 = B·N_d」內部不一致**：B·N_d = 4×44 = **176** ≠ 352。
  正確關係係 **352 = B·Σγ_odd = 2B·N_d = 8N_d**（`scripts/01` C3 已重算並記錄）。
  ⟹ 此為**跨 O 待回報項**；因調律者禁寫 O220 以外目錄，**未寫入 O161 SESSION_START**，
  列於 `SESSION_START.md §四` 待批准清單。
- ⚠️ `idcm-quantization-workflow` 之 γ^μ 為 legacy 約定（見 §三 註）。
- ⚠️ S8（Spin 域規則）本身在 O158 係 🟡（Spin 假說之「唯一精確」部分被無身份反例 (86,39) 挑戰）
  ⟹ 本 O 引用時**只引其結構對應**（Spin-0 單域 vs Spin≥1/2 雙域），唔當佢係閉合預言。
- ⚠️ H3/H5（χ = 2.67°）為**典型值**（O223：定向 null 第 57.8 百分位）⟹ 手性**存在**係結構，
  但其**數值**唔係結構強迫；本 O 唔准用 δ_m 之數值砌無量綱連結。
