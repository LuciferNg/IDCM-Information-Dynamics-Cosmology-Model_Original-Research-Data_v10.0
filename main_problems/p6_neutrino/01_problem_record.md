# P6 — 中微子質量譜（Neutrino Mass from W-field p6 Mode）

## 文檔資訊

| 項目 | 內容 |
|:----|:-----|
| **框架** | IDCM v10.0（It-From-Beat） |
| **研究問題** | 從 K_Chain/W-field 結構推導中微子質量譜（m_νi、Δm²₂₁、Δm²₃₁、Σm），零自由參數 |
| **開題** | 2026-08-15（原始 scripts） |
| **狀態** | 🟡 探索中 — 未閉合；唯一「閉合」屬校準＋後驗，未過盲測四硬測 |
| **位置** | `main_problems/p6_neutrino/`（2026-10-20 結構重組） |
| **審計** | 2026-10-20 全量重跑＋獨立複算（見 §4） |

---

## 1. 問題定義

中微子三個可測量（Δm²₃₁ ≈ 2.45×10⁻³ eV² NH、Δm²₂₁ ≈ 7.53×10⁻⁵ eV²、Σm < 0.12 eV）要求 m_ν ~ 0.01–0.06 eV。IDCM 聲稱粒子質量來自 K_Chain 譜 γ_n = 4sin²(πn/88)（n=1..44）乘 12D WDVV eigenvalue（d_tensor ⊗ φ^{−k/12}），中微子被指派做 W-field「p6 模式」。

**閉合標準（IDCM 四硬測）：** ①零自由參數結構推導 ②MC null / 盲測 ③可證偽＋樣本外 ④結構剛性（非後驗凑合）。

## 2. 核心假設

1. 中微子 = W-field p6 模式（K_Chain n=6, γ₆ = 0.180736）
2. 質量公式候選：m = λ·M_Pl·e^{−V_cycle}（01）、m ∝ γ_nᵖ（02）、m = (γ_n·v)²/M_Pl 幾何 seesaw（03）、m = (γ₆·v)²/M_comp（04/05）
3. M_comp = M_Pl/(2·h¹¹·h²¹·N_d) = 3.9325×10¹³ GeV（CY₃ 緊化）+ φ-power hierarchy 1:φ⁻¹:φ⁻²
4. Z₅/Z₃ orbifold 修正（05 引入: Z₃=3² 對 Δm²₂₁）

## 3. 推導時序索引（2026-08-15 原創）

| 序 | script | 產出 | 內容 | 結果 |
|:-:|:-------|:-----|:-----|:----:|
| A1 | `01_neutrino_p6_derivation.py` | — | 12D eigenvalue + V_cycle 法；λ_9,10,11 = 0.2054/0.1061/0.0023 | 🔴 §8 變數洩漏（見 §4.1） |
| A2 | `02_neutrino_kchain_harmonic.py` | — | γ_n 冪次／beat／V_cycle 外推掃描 | ❌ 全方法 fail（10⁵ eV 級） |
| A3 | `03_neutrino_geometric_seesaw.py` | — | m = (λ·v)²/M_Pl | 🔴 單位混用（見 §4.3） |
| A4 | `04_neutrino_compactification.py` | — | 幾何緊化能標掃描 | 🔴 聲稱錯 1000×（見 §4.2） |
| A5 | `05_neutrino_dm2_calibration.py` | `data/neutrino_p6_results.txt` | M_comp 校準＋Z₃ 修正 → Δm² ratio 0.9992/1.0000 | 🟡 校準＋後驗（見 §4.4） |

## 4. 審計註記（2026-10-20 全量重跑＋獨立複算）

> 5 個 scripts 全部喺隔離 scratch 環境重跑成功（symlink d_tensor）。以下為獨立高精度複算核實（非腳本自報）。

### 4.1 `01_..._derivation.py` — 總結段變數洩漏 🔴
§5 用 λ_9/10/11 正確（ν_τ 1.77×10⁷ eV）；§8 總結用殘留 λ=evals[11]=0.00231 印 m_ν_τ = 1.99×10⁵ eV — 錯（實際應 1.77×10⁷）。且 12D 法全線超出 PDG 上限（τ 1.8e4、μ 9e3、e 0.8 eV）→ 路線本身失效。

### 4.2 `04_..._compactification.py` — 聲稱「最佳匹配」1000× 錯 🔴
M_comp(φ法) = 4.5965×10¹⁶ GeV → m_ν = **4.30×10⁻⁵** eV（唔係聲稱嘅 0.043 eV）。腳本自己印 `ratio: 0.00` 但總結仍標「✅」— 內在矛盾。且 d_4=d_0=1 ⟹ m_τ=m_μ ⟹ Δm²₂₁=Δm²₃₁=1.14×10⁻⁹（同 PDG 分層矛盾）。

### 4.3 `03_..._geometric_seesaw.py` — Δm² 單位混用 🔴
腳本印 Δm² ~ 10⁻³³ eV²（把 GeV 值直接平方）；單位一致後真 Δm² ~ 3.1×10⁻¹⁵ eV²。兩者都離 PDG ~10¹⁰ 個數量級。m_ν = (γ₆v)²/M_Pl = 1.6×10⁻⁷ eV vs 0.05 → **十個數量級太低**。路線硬 fail。

### 4.4 `05_..._dm2_calibration.py` — 校準＋後驗 🟡（唯一產出「閉合」）
- **Δm²₃₁ ratio 1.0000 係恆等，非預言**：m_nu = √(Δ31_PDG/(1−φ⁻⁴)) 直接由 PDG 反推，再反推 M_comp = 3.6909×10¹³ GeV（vs 結構值 3.9325×10¹³ = **−6.14% 未解釋**；prompt 自報 6.57%，數字唔一致）。
- **Z₃=3² 係後驗凑合**：raw Δm²₂₁ ratio = 8.9929 ≈ 9，事後除以 9 → 0.9992。SOUL 禁 φ-power fitting／看到目標凑因子。
- **自相矛盾**：Z₃ 修正後 m_μ = 0.022220 eV，破壞原本 φ⁻¹ hierarchy 嘅 0.033101 — 質量層級同最初假設唔一致。
- Σm = 0.0962 eV：pass Planck18 (<0.12)，**fail DESI/Planck24 (<0.072)**。

### 4.5 跨文件數字不一致
| 量 | 值 | 出處 |
|:--|:---|:-----|
| M_comp 結構 | 3.9325×10¹³ GeV | 幾何公式（prompt） |
| M_comp 校準 | 3.6909×10¹³ GeV | 05 反推（−6.14%） |
| Δm²₃₁ ratio | 0.637（mτ²−mμ²）｜0.881（mτ²−me²）｜1.000（校準） | prompt 表 vs 重算 vs 05 |
| Δm²₂₁ raw ratio | 7.92（結構）｜8.99（校準） | 重算 vs 05 |

### 4.6 遷移依賴問題（結構級，非公式）
- 全部 5 scripts 讀 `data/d_tensor_positive.npy`（repo root），實際檔喺 `main_problems/p15_early_derivations/data/` → 遷移後直接跑會 fail；審計用 symlink 跑通。
- 全部 scripts 寫 output 到 `open_problems_fresh/neutrino_p6_results.txt`（舊路徑，喺 scripts/ 下 relative path 失效）。
- 以上屬「內容修正」範圍，依指示**未改**，只記錄。

## 5. 開放問題

| 問題 | 優先級 | 狀態 | 說明 |
|:-----|:------:|:----:|:-----|
| M_comp 結構值與校準值 −6.14% 缺口 | 高 | 🔴 | 需結構解釋，禁校準補貼 |
| Δm²₂₁ 嘅 9× 壓制結構機制 | 高 | 🔴 | Z₃=3² 純後驗，需事前推導 |
| 質量層級自洽（φ⁻¹ vs Z₃ 修正後 m_μ） | 高 | 🔴 | 05 內部矛盾 |
| 真零參數質量公式（非 12D λ 非 γ_nᵖ） | 高 | 🔴 | 01-04 全線 fail 後無候選 |
| Σm DESI 上限 | 中 | 🟡 | 05 預測 0.0962 已超 0.072 |
| 腳本路徑更新（d_tensor／output） | 中 | 🟡 | 遷移遺留，未改（見 §4.6） |

## 6. 檔案清單

| 檔案 | 內容 | 狀態 |
|:-----|:-----|:----:|
| `01_problem_record.md` | 本文件 | 🟡 |
| `README.md` | 主索引 | 🟡 |
| `docs/01_neutrino_mass_gap_prompt.md` | 質量譜 gap 分析 prompt（後驗路線 A-F 候選） | 🟡 |
| `scripts/01_neutrino_p6_derivation.py` | 12D eigenvalue + V_cycle 法 | 🔴 |
| `scripts/02_neutrino_kchain_harmonic.py` | γ_n 冪次／beat 掃描 | ❌ |
| `scripts/03_neutrino_geometric_seesaw.py` | m=(λ·v)²/M_Pl | 🔴 |
| `scripts/04_neutrino_compactification.py` | M_comp 掃描 | 🔴 |
| `scripts/05_neutrino_dm2_calibration.py` | M_comp 校準 + Z₃ 修正 | 🟡 |
| `data/neutrino_p6_results.txt` | 05 最後輸出（ratio 0.9992/1.0000） | 🟡 |

## 7. 結構重組註記（2026-10-20）

- 原始 flat 7 檔 → `scripts/`（5 .py，編號 01-05）＋ `docs/`（1 .md）＋ `data/`（1 .txt）
- git mv ＆ staging 完成，7 檔全以 rename 記録（0 行內容改動；唯一 10 行 diff 係搬位前已存在嘅 md 未提交修改）
- 內容公式／數字一律未改（依調律者指示）

## 8. 閉合鏈判決附註（2026-10-20，append-only）

> **重要**：§4-§5 嘅「開放問題」評級已過時。上游 O49/O66（08-24→09-14）已將本 P6 大部分未閉合閉合或撤銷。詳見 `docs/02_closure_status.md`（本次攻堅，11/11 獨立重算通過）。

- ✅ **M_comp 缺口閉合**：O66 結構值 3.6890e13 GeV（M_pl·10^-(1/γ₆−1/76)），vs 校準 3.6909e13 只差 0.051%。§4.4 嘅 −6.14% 源於用錯候選 [B]（3.9325e13，O66 已拒絕）。
- ❌ **Z₃=9、φ-power hierarchy、φ^(1/8) 全撤銷**（O49 終審）→ 禁區，勿再推。
- ✅ **真零參數公式存在**：m₃=γ₆²A（mode 6）、m₁=(γ₄+Δcosπ/4)²A、m₂=(γ₄+Δcosπ/5)²A；盲測 Δm² dev 0.44%/0.012%。
- 🔴 **本次修正 O49 script 11**：δ_CP 應為 211.717474°（O123），原 72.6° 係被否證候選；M₂₃=15.185 meV（δ 唔敏感幾乎唔變），M₁₂/M₁₃ 錯號修正。
- 🟡 **真剩餘 4 項**：束縛態機制、「點解 1/L₉」生成鏈、m_ββ Majorana 相位、Σm vs DESI（等數據，維持 partial 唔 close）。建議分別註冊新 O 攻堅。
- 新增檔：`docs/02_closure_status.md`（推導時序索引更新：§8 之後）。

## 9. 階段性 closeout 附註（2026-10-20，append-only）

> 詳見 `docs/10_closeout_20261020.md`（審計報告）；`scripts/09_audit_docs04_09.py`（獨立重算，32/32 PASS）。

- ✅ **#1 束縛態 hop 強度 t=Δ/2 閉合**（docs/09）：gaplessness 條件（hop 帶頂 γ₄+2t = 譜頂 γ₅）唯一決定 t = Δ/2；零自由參數、非 fit。充分 Hamiltonian 留新 O。
- ✅ **身份精修**（docs/06）：Δ 嘅 9 = n₄+n₅（非 N_gen²——後驗標籤修正）；76 = 88−hop_max（hop_max=12=B·N_gen）；hop 階梯和 = 60 = |A₅|；Σγ_odd = Σγ_even = 88。
- 🔴 **兩條機制路經自製工具否定**（docs/08）：Feshbach 極點（0 位置命中 t=Δ/2）＝hop 階梯唔係單缺陷散射；譜積身份搜尋（1/γ₆−1/76 冇 operator 命中）＝1/76 唔係譜積產物。
- 🟡 **第 2 輪審計**：docs/04-09 + scripts/06-08 全部核過（scripts/09，32/32 PASS）；docs/01-03、scripts/01-05 仍屬 764b017 已審核狀態。
- 🟡 **剩餘 3 項**（原 4 項 − #1 已閉合）：1/76 log10 修正機制（🔴）、m_ββ 相位（🟡）、Σm vs DESI（🟡 等數據）——全部 register 已更新。
## 10. 剩餘項去向裁決（2026-10-21，append-only）

> 調律者裁決：**新 O 只含 #2；#3、#4 繼續留喺 P6**（唔開新 O）。

## 11. v_SM 錨統一（2026-10-21，append-only）

> 調律者裁定：**v_SM（246.2196 GeV）及 v（246.0 GeV）皆保留**——文檔兩版數字並存，原文唔刪。

- §8「盲測 dev 0.44%/0.012%」係 **v=246.0 版**；v_SM 版為 **dev 0.80%/0.37%**（仍 <1% 過閘）。
- v_SM 版閉合鏈：A=1.64337 eV/γ²、m₁/m₂/m₃=0.0209452/0.0226848/0.0536815 eV、Σm=0.0973116 eV（v=246.0 版 0.09714 保留）。
- 全量審計發現 scripts/01-05 一直 FileNotFoundError（舊審核靠 symlink 冇真執行）——按調律者授權改 scripts 路徑 8 處（公式零改）；重跑 01-09 exit=0，09=32/32 PASS。
- 詳見 docs/11（審計報告）＋ docs/12（v_SM 基準附註＋呈報精度原則：m 6 位有效、dev 2 位）。
- scripts/03/04/05/09 已改 v_SM 重跑；docs/02/05/07/10/README 已加更正段（原文保留）。

- ✅ **#2 1/76 log10 修正機制** → 已開 **O257**（`open_problems_fresh/o257_mcomp_log10_mechanism`，state=registered 只開不推）。承接後 O257 嘅前置 = P6/O66/O212/O179；禁區（譜積路已否證、O49 docs/03 後驗凑合、Z₃=9/φ-power）已寫入其 problem record。
- 🟡 **#3 m_ββ Majorana 相位** → **繼續留喺 P6**（曾開 O258 後根據「新O只含#2」即時撤回，2026-10-21 retracted；register 已加 O258_RETRACT_FIX 翻譯層，基線 REF-MISSING 5/HARD DRIFT 47 不變）。重點仍係 6.321 meV 候選無結構必要性、6.108 唔排除 CP。
- 🟡 **#4 Σm vs DESI** → **繼續留喺 P6**（等 DESI LRG/ELG + KATRIN/LEGEND 數據，維持 partial 唔 close）。
