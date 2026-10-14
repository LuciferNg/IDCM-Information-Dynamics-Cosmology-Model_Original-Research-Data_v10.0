# DOC 14 — v15: 機制攻堅 ＋ 外部觀測盲測（預註冊）

日期：2026-10-13 ｜ 狀態：🔮 預註冊（盲測未揭）
相關：docs/13 (v14), scripts/11_v14b/11_v14d, O144 docs/24 (σ 依賴鎖)

## 1. 目標
v14 已證 scheme↔MS-bar 樣本外經驗閉合（m_τ/2/5/1 GeV 全 🟢）。
餘下機制判準 ⑥：**點解 Λ_IDCM = √λ_max·M₀·N_gen/L₅ = 45.2849 MeV？**
本輪四路並攻：攻機制（結構候選＋密度關）、外部觀測驗證（多尺度 α_s、
σ、α′、lattice α_s(M_Z)、Λ⁽⁵⁾）、盲測（下述預註冊）、找原理（綜合）。

## 2. 盲測預註冊（本文件寫成時未查任何外部參考值）

### 2.1 預測來源（全部零新常數，IDCM 邊界 α_s(M_Z)=0.11798543 唯一輸入）
計算：scripts/12_v15_blind_predictions.py（佢唔含任何外部值）

| # | 預測量 | 預測值（未計算，將由 script 產生） | 判準 |
|---|--------|------------------------------------|------|
| P1 | α_s(1.5 GeV) | — | 世界值 ±2σ 🟢 / ±3σ 🟡 / >3σ 🔴 |
| P2 | α_s(3 GeV) | — | 同上 |
| P3 | α_s(10 GeV) | — | 同上 |
| P4 | α_s(M_Z/2 = 45.6 GeV) | — | 同上 |
| P5 | α_s(m_b = 4.18 GeV) | — | 同上 |
| P6 | α_s(M_Z) lattice 共識 | 0.117985 | 對照 lattice QCD 直測（零擬合）z |
| P7 | σ = Σγ_odd·Λ_IDCM² | 0.18046 GeV² | vs Regge 0.18 及 lattice (0.44 GeV)² — 兩者世界值互相分歧 ~7%，預註冊: 中其一定 🟢 |
| P8 | Regge 斜率 α′ = 1/(2πσ) | 0.8822 GeV⁻² | vs 世界 ~0.88 |
| P9 | Λ_MS⁽⁵⁾（標準 implicit 2-loop 公式；by-running 積分判準作廢——該定義非標準 Λ_MS 慣例，唔可比 PDG 5-loop 213±8） | ~166 MeV | vs 文獻 NLO Λ_MS⁽⁵⁾ ≈ 165.8±?（5-loop 213 需 b₃/b₄，本輪唔上） |
| P10 | Λ_MS⁽³⁾（IDCM 邊界落 Nf=3 後標準 implicit 2-loop）【2026-10-13 外部數據揭曉後、計算前補註冊】 | — | vs ALPHA/FLAG 2024 lattice 非微擾 step-scaling: Λ⁽³⁾_MS = 339.5±9.6 MeV（獨立於 α_s(M_Z) 平均值） |

### 2.2 機制候選（攻堅清單＋密度關規則）
| 候選 | 內容 | 命運規則 |
|------|------|---------|
| C1 | σ = Σγ_odd·Λ²（困閉尺度 = observer 譜和 × Λ²） | 數值命中 + density vs V_core/V_wide |
| C2 | b₀ = (11N_c−2N_f)/3，N_c=B−1, N_f=2N_gen → b₀=7=L₄（β 機制已存在，重申） | 文獻閉合 |
| C3 | Landau pole ↔ chain mode 數（μ=Λ 時 active modes=19） | 必須 EXACT，19 = 2F₇−L₄ 檢查 |
| C4 | t = ln(M_Z/Λ) 結構形式（候選 11ln2，dev ~0.2%） | dev>EXACT-bar ⟹ 唔升格，標觀察 |
| C5 | λ_max = 2L₆−1/γ₂₀ 之 operator 身份（v13 已證） | 引用，唔重推 |
| D | 禁 φ-power fitting、禁後見之明凑算子（SOUL 鐵律） | — |

## 3. 工作流
1. scripts/12_v15_blind_predictions.py：全預測計算（含 P9 by-running Λ⁽⁵⁾
   3-loop 慣例：搵 Λ 使 3-loop Nf=5 running 由 Λ 到 M_Z 㩒返 α_s(M_Z)）
2. density 測試 C1（σ 比率 88=Σγ_odd 喺 V_core ±0.5% 窗內唯一性）
3. 先揭數學預測值，再 web 查世界值對比（盲測揭曉）
4. docs/14 收尾：verdicts + 原理綜合

## 4. 話明
- 世界值由 web_search（PDG/FLAG/lattice/Regge）取證，取證優先。
- 任何候選過唔到 density/EXACT-bar 一律標 🟡 觀察或擲返，
  唔會因為「好接近」而升格。
- σ 兩個世界值（Regge 0.18 vs lattice 0.1936）雙方差距 ~7% 屬
  文獻真實現況，預註冊 P7: 中任何一個即 🟢，兩個都不中 🔴。