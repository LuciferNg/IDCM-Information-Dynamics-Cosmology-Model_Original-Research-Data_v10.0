# O234 docs/02 — Round 2: 完整約束/DOF 審計 + 檢驗能力清單 + 不可證偽性定理

> **日期**: 2026-10-06（第二輪）
> **Scripts**: `scripts/03_doff_census_and_testpower.py`（3 PASS / 0 FAIL）+
> `scripts/04_loocv_and_unfalsifiability.py`（4 PASS / 0 FAIL）
> **承接**: docs/01（未另立檔，01_problem_record 記載首輪）
> **凍結層**: data/01_frozen_observations.json (v1.0) + data/03_derived_ratios.json (v1.1 derived)

---

## 一、凍結層導出比（frozen v1.1，一階誤差傳播）

| 比 | 值 | 誤差 | 精度 | 來源組合 |
|:--|:--|:--|:--|:--|
| m_d/m_u FLAG | 2.1505 | 0.111 | 5.2% | 2+1+1 |
| m_s/m̂ FLAG | 27.227 | 0.081 | **0.30%** | 2+1+1 |
| m_s/m_u (derived) | 42.890 | 1.52 | 3.5% | m_s/m̂ × (1+m_d/m_u)/2 |
| m_s/m_d (derived) | 19.944 | 0.33 | 1.7% | m_s/m̂ × (1+m_u/m_d)/2 |
| m_c/m_s Nf=4 | 11.652 | 0.065 | **0.56%** | FLAG ⊕（ETM 系, mc(5GeV)/ms） |
| m_c/m_s HPQCD | 11.850 | 0.16 | 1.4% | FLAG（HPQCD 09A） |
| m_b/m_c (PDG) | 3.291 | 0.057 | 1.7% | m_b(m_b)/m_c(m_c)，scheme 近似 |
| m_t/m_b | 41.28 | 0.30 | 0.7% | pole/MS 不可通約（WARNING） |
| m_μ/m_e | 206.77 | 0.002 | ≈0 | pole |
| m_τ/m_μ | 16.817 | 0.001 | ≈0 | pole |
| m_τ/m_e | 3477.2 | 0.24 | ≈0 | pole |

★ **凍結層內部張力 watch item**: m_c/m_s 兩值 z = +1.15（11.652 vs 11.85）——凍結層 v1.1 可接受，
但 freeze v2 要決策用邊個做主。提議: Nf=4 值做主（同 m_s/m̂ 同一 Nf 家族），HPQCD 做交叉。

## 二、★★ DOF 審計（scripts/03 [B]）：C-shape 完全由凍結層釘死

```
未知 C: 8（e,μ,τ,u,d,s,c,b；t 走 VEV 除外）
觀測獨立 ratio 約束: 6（輕子 2: μ/e, τ/μ；夸克 4: d/u, s/u(derived), c/s, b/c）
扇區標度: 2（冇 輕子↔夸克 比）⟹ shape DOF = 8 − 6 − 2 = 0
```

反解 C-shape（anchor 每扇區 = 1）: u=1.000 d=0.958 s=10.777 c=41.585 b=57.162 | e=1.000 μ=8.356 τ=44.418

- **shape 零自由度**: 一經給定 6 個 ratio，8 個 C 嘅形狀完全固定——C 層「冇嘢可以再講」
- 剩餘自由度 = 2 個扇區標度（輕子區、夸克區）——都係 by-construction 先有數
- **生成缺口**: 形狀被凍結層釘死 ⟹ 任何「C_f 生成器」預言會係唯一可核；但 O233 已負閉合
  （無算子身份 p=0.9955）⟹ 形狀只有後驗意義
- 交叉驗證: C_d/C_u = 0.9578 vs O233 P2 用 0.9629（PDG 中心）——0.5% 差= FLAG vs PDG central 差；
  方向（C_u > C_d）一致 ✅

★ **凍結層 redundancy = 0**（scripts/04 [B]）: 6 個約束全部必要；留出任何一個 ⟹ shape DOF = 1
⟹ 冇任何 ratio 可以靠其餘「預言」。真正 out-of-sample 測試必須嚟自 **凍結層 v2+ 新量度**（未用過喺
assignment 構建嘅數字），例如 1% 精度 m_s/m_u。

## 三、檢驗能力清單（scripts/03 [C]）：9 比中只有 1 個 γ 可檢驗

| 比 | 精度 | 純γ z | 類別 |
|:--|:--|:--|:--|
| d/u | 5.2% | +0.9 | 🟢 **γ-testable**（鏈譜唯一直接測試點） |
| s/m̂ | 0.30% | — | 🟡 mode-gap（最銳觀測量但平均量無模式對應） |
| m_s/m_u | 3.5% | −25.7 | 🔴 C-dominated |
| c/s | 0.56% | −132.8 | 🔴 C-dominated（最銳 C 比） |
| b/c | 1.7% | −15.7 | 🔴 C-dominated（scheme 近似） |
| t/b | 0.7% | −131.2 | 🔴 VEV 扇區 |
| μ/e | ≈0% | −9.1e4 | 🔴 C-dominated |
| τ/μ | ≈0% | −1.2e4 | 🔴 C-dominated |
| τ/e | ≈0% | −1.4e4 | 🔴 C-dominated |

## 四、★★ 不可證偽性定理（scripts/04 [A]）

**定理（模型類層）**: 模型類 M = { m_f = M₀·γ_n·C_f : C_f ∈ ℝ⁺ } 對任何 ratio R 都存在 C 調整
（C_i/C_j = R/(γ_i/γ_j)）⟹ P(mismatch)=0 ⟹ **M 對 C-dominated 比不可證偽**。只有 C_f ≡ const
（純γ，零參數）或 C_f 來自凍結公式先可證偽。

- 直接後果: 9 個比中 8 個本質上係「定義商」——第一個公式只講咗「呢啲 C 必須係呢啲值」
- 檢驗方法嘅結論係**負面但精確**: 質量公式 m = M₀γC 喺 ratio 層嘅可證偽內容 = 唯一一個
  純γ比（d/u, 0.85σ 過）；其餘 8 個比嘅檢驗能力 = 0（除非 C 生成器閉合，O233 已負）

## 五、s/m̂ 模式閘（負面閉合，scripts/04 [C]）

m̂ = (m_u+m_d)/2 嘅四種 γ 幾何中點候選全部不合格:

| 中點 | γ_mid | γ₄/mid | 需 C 放大 |
|:--|:--|:--|:--|
| 算術 (γ₂+γ₃)/2 | 0.03303 | 2.45 | 11.1× |
| 幾何 √(γ₂γ₃) | 0.03050 | 2.66 | 10.3× |
| 半整數模 γ(2.5) | 0.03178 | 2.55 | 10.7× |
| 調和 | 0.02817 | 2.88 | 9.5× |

⟹ **mode-gap 係真結構缺口**（唔係「未搵到中點公式」）: s/m̂ 喺任何幾何中點選擇下都係
C 放大比 ~10×，冇純 γ 通道。

## 六、★★ 渾標度發現（O233 C_f 絕對值更正通知）

**凍結層方案正確嘅 C_c/C_s = 3.86（FLAG Nf=4 ⧸ 同 scheme）；O233 docs/15 嘅 C_f 池（by-construction,
PDG 絕對質量）隱含 C_c/C_s = 4.50——15% 偏離**。來源: m_c(m_c)（1270 MeV）vs m_s(2 GeV)（93.4 MeV）
係唔同重整化標度，ratio 直接除 = 混標度。

- **影響範圍（已核）**: O233 正結果建基於質量 rank 次序 ⟹ rank 結構唔受 C 值標度影響 ⟹
  鋸齒/輕子槽/兩流全部不受影响 ✅
- **受影響**: 任何用 C_f「絕對值/池匹配」嘅分析（e.g. b/c 所需 C 比 vs 44/33 近命中 3.0% 要
  用同 scheme mb/ms 重做）——本 O scripts/02 S1a 已標 nominal
- **移交**: O209 Id(f) 用 m/M₀γ（PDG 絕對質量）——同一混標度問題（register handoff 已發，
  本 O 唔代改任何 O209 檔）

## 七、第二輪總結 + 剩餘開放

```
✅ C-shape 完全釘死（shape DOF=0，2 扇區標度）
✅ 檢驗能力清單: 1/9 γ 可檢驗（d/u, 0.85σ）; 8/9 不可證偽（模型類定理）
✅ LOOCV 機械: redundancy=0 ⟹ out-of-sample = 凍結層 v2 新量度
✅ s/m̂ 模式閘: 負面閉合（模式缺口真）
✅ 混標度更正通知（O233 C_f 池 15% 級; O209 watch）
🟡 凍結層 v1.1 內部張力: m_c/m_s 兩值 z=1.15（freeze v2 決策點）
🔴 RGI_b 未入凍結層（FLAG §4.3 要完整讀一次）
🔴 1% 精度 m_s/m_u（未來量度）= 唯一嘅「非 assignment 內含」out-of-sample 測試
```