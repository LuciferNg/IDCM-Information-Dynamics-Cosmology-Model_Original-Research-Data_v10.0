# IDCM v10.0 — 共震點宇宙學（It-From-Beat）

**Information Dynamics Cosmology Model — 10th Generation**

K_Chain 44 個模式之間的共震點 (beat frequency) 經 CY₃(36,98) 幾何投影激化為物質與 CMB。

## 核心假設

> 物質 = K_Chain 44 個頻率之間嘅共震點，經 CY₃ 幾何投影激化
>
> 結構強逼（structural necessity）≫ 數值吻合；零參數絕對主義；盲測＋預測閉合為驗證鐵律。

## 研究路線

1. **K_Chain 44 模式** — 離散 Laplacian 本徵值 γₙ = 4sin²(πn/88)
2. **946 個 beat frequency** — 44×43/2 對組合，物質 = 共振態
3. **CY₃(36,98) 投影** — 134×946 選擇律投影算子
4. **Z₃ Orbifold** — 36→12 維不變子空間
5. **WDVV 方程求解** — 三重相交張量，11 正 + 1 零個本徵值
6. **SM 閉合** — 質量譜/混合角/Ω 比例逐項閉合（見 problem_register）

## 項目結構

```
IDCM-v10.0--It-From-Beat/
├── README.md                    # 本檔
├── open_problems_fresh/         # O 系列（O1–O255）：逐題 docs/scripts/data
├── main_problems/               # P 系列（P1–P15）：跨題主問題（bbn/cmb_cl/ckm…）
├── problem_register/            # register.py + register.sqlite/jsonl（append-only 權威）
├── dag/                         # v10 DAG（cron 每 60m 重新生成）
├── data/                        # 研究產出 json（nz_results 等）
└── memory_archive/              # MEMORY/USER 完整導出（.gitignore，唔上傳）
```

### O 系列分佈（register 快照 2026-10-18）
```
closed: 128 | open: 62 | partial: 55 | registered: 6 | retracted: 3 | merged: 1
```

### P 系列（main_problems）
```
P1 bbn / P2 ckm / P3 cmb_cl / P4 cmb_cold_spot / P5 crystal_stress / P6 neutrino /
P7 reionization / P8 h0_tension / P9 kchain_number_field / P10 ktree_structure /
P11 little_red_dots / P12 uhecrs / P13 beat_periodic_table / P14 global_routing_table / P15 early_derivations
```
（pid 一律大寫 P1..P15，folder 一律細寫 p1_bbn…；同 O 系列一致）

## 已閉合關鍵結果（選錄）

- **BBN**：η_B=6.2116e-10、Ω_b=1/20（BBN 17.6σ 排除對照）✅
- **H₀**：67.4071（c=R·ω_ring 錨定）✅
- **冷斑＋拓撲**：RMS=ε⁵/8、冷斑=5ε⁵/8、位 (209°,−57°)、A₅ 節點網格、SMICA −134.2μK −3.25σ ✅
- **光速第一性原理**（O73）：光 = W-field Goldstone 相位模，c = R_world·ω_ring ✅
- **錨定唯一量**（O212）：G ≡ ω_ring ≡ M_Pl，dof=1 ✅
- **Ω 比例**（O215）：Ω_b=3/60、Ω_dm=16/60、Ω_Λ=41/60（3:16:41 結構）✅
- **旋轉曲線**（O180）：v_k²=a₀r_k EXACT、BTFR 平軌 ✅
- **群論**（O222/O223）：K sign_rank≤3、|GeoAut|=60 手性 ✅
- **質量譜**：v_SM=246.2196、全系零字面 True（205/205）✅
- **真空能／拉格朗日閉合**：SM×IDCM×GR 34/34 ✅

## 驗證紀律

- 閉合主張必過 4 Hard Tests：①零參數自由度 ②MC null（10⁷, 5σ）③樣本外盲測 ④結構剛性
- 質量公式盲測＋預測閉合；禁見 target 凑算子、禁 φ-power fitting
- register PID：M/P/S 跟隨 O 大寫（O1/P1/M1…）；folder 細寫；register.jsonl append-only 權威
- 已否證路線設 FAIL + `-c` tag；跨版本引用先核歸一化

## O/P 系列全列表

| 編號 | 標題 | 核心發現 | 狀態 |
|------|------|----------|------|
| O1 | 冷斑 15.11° 幾何夾角 | 精確機制 | 已合併 |
| O2 | 熱斑等級驗證 | Fibonacci 等級熱斑 SMICA 掃描 | 部分閉合 |
| O3 | 60 節點實際溫度統計 | SMICA 全節點掃描 | 部分閉合 |
| O4 | Fibonacci 等級模型物理動機 | 點解 F₃/F₄/F₅ ladder? | 部分閉合 |
| O5 | 冷斑 Catalogue 對比 | WMAP/Planck 冷斑目錄 vs A₅ 節點 | 全部閉合 |
| O6 | 節點 57 對徑點檢驗 — 已完成 | — | 全部閉合 |
| O7 | 阻挫邊 16/16 冷-冷/熱-熱分佈規律 | — | 全部閉合 |
| O8 | 節點 5° 影響範圍 vs 26° 間距 | 尺度半徑之謎 | 全部閉合 |
| O9 | 高 ℓ 峰 m=4+ 偏差（原 P2）—  已閉合 | — | 開放 |
| O10 | 峰幅度 A_m 結構公式（原 P3） | — | 全部閉合 |
| O11 | Maser H₀ 偏移機制（原 P4） | — | 全部閉合 |
| O12 | ³He/H primordial 觀測現狀（原 P5） | — | 部分閉合 |
| O13 | n/p 比 γ₇/γ₂₀ 機制 | — | 開放 |
| O14 | Ω_b 直接推導（唔借 Ω_Λ）—  已閉合 | — | 開放 |
| O15 | ⁷Li 線性 η_B 檢驗 & 幾何鎖定定理 | 最終閉合記錄文檔 | 開放 |
| O16 | Cepheid PL 關係嘅 K_Chain 耦合機制 | — | 開放 |
| O17 | SN Ia 距離階梯第 2 Rung + Maser 第 3 Rung | — | 開放 |
| O18 | H_eff(z) 高 z 極限 | (1+z)^1.0 vs ΛCDM (1+z)^1.5 | 開放 |
| O19 | 低 ℓ 異常 | 問題記錄 (最終閉合版) | 開放 |
| O20 | E/B 極化峰位置預測 | — | 開放 |
| O21 | 節點 9 極端 anomaly | 熱色但全場第二冷 | 部分閉合 |
| O22 | 對徑對溫度行為 | 30 對近對徑嘅相關性 | 開放 |
| O23 | ΔE=0 節點符號匹配率偏高 | 75% vs 58% | 開放 |
| O24 | 極端節點匹配不對稱 | 冷端 8/10 vs 熱端 6/10 | 開放 |
| O25 | 溫度尺度譜 | 信號隨平滑尺度嘅完整表徵 | 開放 |
| O26 | 節點 57 (對徑) 附近大尺度結構 | — | 開放 |
| O27 | 節點 47 前景污染分析 | 3.0° 第二冷係咪真實? | 開放 |
| O28 | Planck gp10 冷斑 mask 校正 | 第二官方冷斑有冇節點對應? | 開放 |
| O29 | mean-nearest p=0.072 剩餘信號分解 | 有冇第二結構貢獻? | 開放 |
| O30 | 60 節點微冷系統性 | 全部節點有冇整體溫度異常? | 開放 |
| O31 | ξ(s) 零點 vs K_Chain 不動點 | 形式化雙向等價 | 全部閉合 |
| O32 | O32 | 星系旋轉曲線問題：IDCM 解釋 | 開放 |
| O33 | O33 | 誠實標記問題：未被投影機制的必然性 | 全部閉合 |
| O34 | O34 | 觀察者算子與內觀程序（Observer Operator & Introspection Program） | 全部閉合 |
| O35 | O35 | 拍頻 → 三角質量公式 Link-Up（Beats → Sin/Cos/Tan Mass Formula） | 開放 |
| O36 | O36 | W-Field 共振響應動力學（Resonance Response Dynamics） | 開放 |
| O37 | O37 | W-Field 完整 Lagrangian 建構 (W-Field Lagrangian Construction) | 全部閉合 |
| O38 | O38 | κ 數值獨立預言 (Coupling Strength κ Independent Prediction) | 全部閉合 |
| O39 | O39 | ⟨W⟩ 凝聚動力學 (W-Field Condensate Dynamics) | 全部閉合 |
| O40 | O40 | W-Field 剩餘未閉合項目攻堅 (W-Field Remaining Unclosed Items) | 開放 |
| O41 | O41 | 真空能 = 觀察者預算 (Vacuum Energy as Observer Budget) | 開放 |
| O42 | O42 | 冷斑 A 獨立量度方案 (Independent Measurement of Cold Spot Amplitude) | 開放 |
| O43 | 全息框架未測試項目 | 交接清單 (O26 衍生) | 全部閉合 |
| O44 | O44 | p=0.072 剩餘信號分解 (Residual Signal Decomposition) | 開放 |
| O45 | O45 | SMHW 小波獨立驗證冷斑 A=134.2μK | 開放 |
| O46 | O46 | 多頻段穩定性 + ISW 解耦 (Multifrequency & ISW) | 開放 |
| O47 | O47 | R_H ↔ Ω_Λ 比例閉合 (Projection Pipeline Link) | 開放 |
| O48 | O48 | CMB 質數峰機制 (Prime Peak Mechanism) —  完整閉合 | 開放 |
| O49 | O49 | 中微子絕對質量標度 (Neutrino Absolute Mass Scale) | 開放 |
| O50 | O50 | CY₃(36,98) 真實相交數 (True Intersection Numbers) | 開放 |
| O51 | O51 | K_Chain 有冇起始？(Origin of K_Chain) | 全部閉合 |
| O52 | O52 | 60 節點系統性微冷/微熱檢驗 (Node Systematics) | 全部閉合 |
| O53 | O53 | CY₃(36,98) 真實性 + 開放性問題 | 全部閉合 |
| O54 | O54 | 宇宙反物質豐度：反物質去咗邊？ | 全部閉合 |
| O55 | O55 | c_f = n/3：SM 規範群中心 Z₃ 投影 | 全部閉合 |
| O56 | O56 | CY₃ Moduli 鎖定機制 | 全部閉合 |
| O57 | O57 | CY₃ 投影生成機制 | 開放 |
| O58 | O58 | (36,98) 真實 Toric 構造 (PALP) | 開放 |
| O59 | O59 | Z₃ 12 維不變子空間 | 開放 |
| O60 | O60 | 星系合併歷史與中小尺度自洽性：IDCM 檢驗 | 全部閉合 |
| O61 | O61 | A_ij(z) pre-factor + Moduli stabilization | 全部閉合 |
| O62 | O62 | Λ 第一性原理推導 | 全部閉合 |
| O63 | O63 | 中微子 m_ββ 預言驗證追蹤 | 全部閉合 |
| O64 | O64 | 9 費米子質量階層：sector-dependent 幾何（O57 移交） | 部分閉合 |
| O65 | O65 | CKM/PMNS 混合角第一性原理（O57 移交） | 全部閉合 |
| O66 | O66 | M_comp 第一性原理（O57 移交） | 全部閉合 |
| O67 | O67 | 66 態 → SM 粒子標籤（O57 移交） | 開放 |
| O68 | O68 | γ₆ 2 冪幾何來源（O57 移交） | 全部閉合 |
| O69 | O69 | γ_n 譜深層意義（O57 移交） | 全部閉合 |
| O70 | O70 | 155 curves facet 結構（O57 移交） | 全部閉合 |
| O71 | O71 | Σm_ν 實驗驗證（O57 移交）— 更新版 | 全部閉合 |
| O72 | O72 | K_Chain ⊗ K_Tree 現實性 | 全部閉合 |
| O73 | O73 | ω_ring 第一性原理 | 全部閉合 |
| O74 | O74 | 投影幾何與相位相移機制 | 全部閉合 |
| O75 | O75 | 命名規範統一 | 開放 |
| O76 | O76 | z 紅移翻譯 (非膨脹紅移) | 開放 |
| O77 | O77 | Occam 對照深化 | 開放 |
| O78 | O78 | 觀察者 re-framing (90/88 形而上學?) | 開放 |
| O79 | O79 | Post-diction vs Blind Prediction | 全部閉合 |
| O80 | O80 | W-field Lagrangian (L_W ↔ QFT) | 全部閉合 |
| O81 | O81 | SESSION START | 開放 |
| O82 | O82 | SESSION START (已閉合) | 全部閉合 |
| O83 | O83 | Correlator ⟨φφ⟩ ↔ C_ℓ | 開放 |
| O84 | O84 | SESSION START | 全部閉合 |
| O85 | O85 | SU(12) → SM Breaking Chain | 全部閉合 |
| O86 | O86 | SESSION START | 部分閉合 |
| O87 | O87 | 1496 模式物理 (或者放棄) | 全部閉合 |
| O88 | O88 | Anomaly + Fermion Representations | 全部閉合 |
| O89 | O89 | Mass Hierarchy + Gauge Coupling Unification | 全部閉合 |
| O90 | O90 | 6 Extra U(1) ↔ V_Λ = 283.0821 | 全部閉合 |
| O91 | O91 | S8 張力 (σ₈ Normalization) | 全部閉合 |
| O92 | O92 | KiDS-1000 弱透鏡 S8 驗證 | 全部閉合 |
| O93 | O93 | Cosmic Chronometers H(z) 驗證 | 全部閉合 |
| O94 | O94 | SESSION START | 全部閉合 |
| O95 | O95 | SESSION START (2026-08-27) | 全部閉合 |
| O96 | O96 | SESSION START (已閉合) | 全部閉合 |
| O97 | O97 | SESSION START | 全部閉合 |
| O98 | O98 | SESSION START | 全部閉合 |
| O99 | O99 | 光實質不存在 (Light as Ontological Fiction) — 已閉合 | 全部閉合 |
| O100 | O100 | C_ℓ → P_3D(k) 逆投影算符 (Inverse Projection Operator ℳ) | 全部閉合 |
| O101 | Session Summary | 2026-08-28: O100-O113 重排 + O101 正式推導 | 全部閉合 |
| O102 | (no title) | — | 開放 |
| O103 | O103 | SESSION START: N_gen=3 機制推導 | 全部閉合 |
| O104 | o104_i_star_d_app_bridge | SESSION START (已閉合) | 全部閉合 |
| O105 | o105_pi144_structure | SESSION START | 開放 |
| O106 | o106_i_star_decomposition | SESSION START | 全部閉合 |
| O107 | O107 | SESSION START | 全部閉合 |
| O108 | O108 | SESSION START: VL 質量譜 72→48 | 開放 |
| O109 | O109 | SESSION START | 開放 |
| O110 | O110 | SESSION START: 宇宙資訊出納運作流程 | 部分閉合 |
| O111 | O111 | V_Λ 殘留閉合 (Δ, 19 機制, γ VEV 穩定性) | 開放 |
| O112 | 968 ↔ T_CMB 交叉驗證 | — | 全部閉合 |
| O113 | 88/90 → σ8 Lagrangian 入口 | — | 全部閉合 |
| O114 | O114 | SU(12)→SM 完整粒子物理現象學鏈 | 全部閉合 |
| O115 | O115 | SM/QM/ΛCDM 完整框架替代的完備性檢查入口 | 部分閉合 |
| O116 | O116 | SESSION START | 全部閉合 |
| O117 | O117 | SESSION END (2026-09-01) | 開放 |
| O118 | O118 | 高 z DESI 殘差：局部阻抗修正 | 全部閉合 |
| O119 | O119 | 正電子超出 (AMS-02)：W-field 衰變通道 | 部分閉合 |
| O120 | O120 | SESSION START | 部分閉合 |
| O121 | O121 | 黑洞熵微態計數：IDCM 中的黑洞解釋 | 開放 |
| O122 | O122 | Feynman 規則從 W-field 晶格推導 | 全部閉合 |
| O123 | O123 | 中微子 δ_CP 從 CY₃ 投影 | 部分閉合 |
| O124 | O124 | QCD 膠子散射從 W-field | 部分閉合 |
| O125 | O125 | 散射振幅完整推導 | 全部閉合 |
| O126 | O126 | Runtime ISA 架構驗證 | 全部閉合 |
| O127 | O127 | 宇宙網各向異性 ξ(s) | 全部閉合 |
| O128 | O128 | σ8 歸一化驗證 | 全部閉合 |
| O129 | O129 | SYNC 轉折點 σ_sync 推導 | 部分閉合 |
| O130 | O130 | 小波工具箱宇宙學應用 | 開放 |
| O131 | O131 | 疊加分析工具 | 開放 |
| O132 | O132 | 紅移演化推導 | 開放 |
| O133 | O133 | P(k) 鏈譜分析 | 全部閉合 |
| O134 | O134 | CY₃ 拓撲算子完整推導 | 全部閉合 |
| O135 | O135 | 結構強制完整驗證 | 全部閉合 |
| O136 | O136 | SESSION START | 部分閉合 |
| O137 | O137 | SESSION START | 開放 |
| O138 | O138 | IDCM 對 QM 測量問題的結構回答 | 全部閉合 |
| O139 | O139 | 有限 QFT → 連續 QED 的極限：88-site 晶格在原子尺度的退化驗證 | 全部閉合 |
| O140 | O140 | 有限譜化相對論 (Finite-Spectral Relativity, FSR) | 部分閉合 |
| O141 | O141 | 數據源偏好分析 (Data Source Preference Map) | 部分閉合 |
| O142 | O142 | 玻色子質量推導（問題記錄 + 推導時序索引） | 部分閉合 |
| O143 | O143 | Deterministic (n, P_f) Selection Rule & LOOCV Protocol | 全部閉合 |
| O144 | O144 | 基本玻色子身份 (Fundamental Boson Identity) | 部分閉合 |
| O145 | O145 | SESSION START | 全部閉合 |
| O146 | O146 | 拍頻與 N_d 的存在性驗證（數學 × 觀測 多層次） | 全部閉合 |
| O147 | O147 | 528 全息信道嘅結構必要性 | 全部閉合 |
| O148 | O148 | 真空預算雙標度閉合審計 (Dual-Scale Vacuum Budget Closure) | 全部閉合 |
| O149 | O149 | 群速度鎖定（v_g Locking）：由 K_Chain 色散結構推出混合角 | 部分閉合 |
| O150 | SESSION_START | o150_sky_side_projection (Sky-side 投影算子) | 部分閉合 |
| O151 | O151 | 全息信道容量 (Holographic Channel Capacity) | 全部閉合 |
| O152 | O152 | 數字即算子 (Numbers as Operators)：譜幾何算子字典 | 部分閉合 |
| O153 | O153 | 降級數字重新研究 (Legacy Numbers Redig)：CLT、N_h、42、domain_EW、四域架構 | 部分閉合 |
| O154 | O154 | 常溫超導體預言 (Room-Temperature Superconductor Prediction)：用 IDCM 拓撲結構預測物質與結構 | 部分閉合 |
| O155 | O155 | K_Tree 本徵算子化 (K_Tree Eigen-Operatorization) | 部分閉合 |
| O156 | O156 | θ₂₃ 殘差與尺度流 (RGE 第一性原理) | 部分閉合 |
| O157 | O157 | 能量泛函第一原理 (邊界條件能量泛函) | 全部閉合 |
| O158 | O158 | ×41 聚類算子驗證 (N_d ± k·N_gen 家族) | 部分閉合 |
| O159 | O159 | Dirichlet 場論第一原理 (邊界條件場論) | 全部閉合 |
| O160 | O160 | 全數字譜掃描 (Full-Spectrum Number Scan) | 全部閉合 |
| O161 | O161 | 離散作用量 + Noether 電荷 + 鏈變數結構 | 全部閉合 |
| O162 | O162 | 物質投影時的光學缺陷 (Optical Defects in Matter Projection) | 全部閉合 |
| O163 | O163 | DM 真身：觀測約束先導 (DM Identity: Observational Constraints First) | 全部閉合 |
| O164 | O164 | 世界 = 拍子: K_chain 頻率標度嘅終極本體 (World as Beat: Origin of the ~1e-17 Hz Scale) | 全部閉合 |
| O165 | O165 | e⁻ⁿ 權重嘅本體: κ 閘極「比較尺」嘅起源 (Origin of the Exponential Visibility Weight) | 全部閉合 |
| O166 | O166 | T_CMB 絕對值: 世界環熱力學量 (Absolute Value of the CMB Temperature) | 已註冊 |
| O167 | O167 | CMB 家族 H₀ 真張力 (H3): 早宇宙尺度 (The Real H₀ Tension) | 全部閉合 |
| O168 | O168 | 問題記錄: G 嘅結構推導 vs 最後輸入審計 | 部分閉合 |
| O169 | O169 | 問題記錄: D_A(ℓ) 譜第一原理 — δ 群延遲修正嘅 K_Chain 起源 | 全部閉合 |
| O170 | O170 | 問題記錄: 本徵徑向距離 (Phase-Depth Distance) — D_H 嘅 IDCM 定義 | 已註冊 |
| O171 | O171 | 問題記錄: 60-頂點群配分理論 — A₅ ↔ 88-site 譜 | 全部閉合 |
| O172 | O172 | 問題記錄: v_SM 機制詮釋攻堅 — 88×71×(1−2/1575) 結構強迫 | 全部閉合 |
| O173 | O173 | 問題記錄: 應變能循環閉合 — 星系創造/吸收鏈 | 開放 |
| O174 | O174 | 問題記錄: 凝聚率 4^{−ℓ} 嘅 Lagrangian 級推導 | 全部閉合 |
| O175 | O175 | 問題記錄: 正式熵定理 (寫入-耗散平衡) | 全部閉合 |
| O176 | O176 | 問題記錄: 觀測裁決跟進 (O173 R1-R4 執行) | 全部閉合 |
| O177 | O177 | 問題記錄: 池/圈 = 364 算子身份 (Pool-Turnover Operator Identity) | 全部閉合 |
| O179 | O179 | 問題記錄: 新節點出現機制 — 4^{−ℓ} 層級點樣產生新星系位置 | 開放 |
| O180 | O180 | 問題記錄: 相位繞數 → 空間投影嚴格場論翻譯 (D15) | 開放 |
| O181 | O181 | 問題記錄: LRD 質譜/窗口可分辨性攻堅 (Mass-Window Resolution) | 開放 |
| O182 | O182 | 問題記錄: 88 格幾何 (B₅ 補集) — 11/45 轉正嘅數據缺口 | 全部閉合 |
| O183 | O183 | 問題記錄: A₅↔鏈投影對應 v2 (W(i) 位置權重框架) | 部分閉合 |
| O184 | 冷斑 15.11° 座標系假象（原 O1 duplicate 搬移） | — | 全部閉合 |
| O185 | IDCM ↔ 弦論家族結構對應（全弦論/M理論/AdS-CFT） | — | 全部閉合 |
| O186 | TRGB/Miras 校準差異機制（原 O17 duplicate 搬移） | — | 全部閉合 |
| O187 | Deterministic Selection Rule & LOOCV（原 O143 duplicate 搬移） | — | 開放 |
| O188 | IDCM ↔ LQG 結構對應（離散晶格 vs 圈量子重力） | — | 部分閉合 |
| O189 | IDCM ↔ 細胞自動機結構對應（88-site 鏈作為 CA） | — | 部分閉合 |
| O190 | O190 | 問題記錄: RS1 vs 晶格傳輸模型 (Randall–Sundrum ↔ K_Chain Lattice Transport) | 全部閉合 |
| O191 | O191 | 問題記錄: 數場定律形式化 (Number-Field Law: F_m − 1 家族與二模量定理) | 全部閉合 |
| O192 | O192 | 問題記錄: Lucas−1 對偶家族 + 譜和預算量子定理 | 全部閉合 |
| O193 | O193 | 問題記錄: 冪和閉式精確域 + Nyquist-atom 機制 + arcsine 譜定理 | 全部閉合 |
| O194 | O194 | 累積量譜系閉合 (Cumulant Hierarchy Closure) | 全部閉合 |
| O195 | O195 | 累積量整數性定理 (Cumulant Integrality Theorem) | 全部閉合 |
| O196 | O196 | k_odd 主導閉合: 11-adic 證明 + D_n 增長閉式 + 觀測對應裁決 | 全部閉合 |
| O197 | O197 | δ̂ × δ_env 合成卷積 (Density Fluctuation Synthesis) | 全部閉合 |
| O199 | O199 SESSION_START | 愛丁頓臨界吸積率 2% 嘅幾何強逼性 | 開放 |
| O200 | O200 | 維度收束: 有量綱 → 無量綱（Dimensional Collapse） | 部分閉合 |
| O201 | SESSION_START | o201_spectral_language | 全部閉合 |
| O202 | SESSION_START | o202_spectral_representation | 部分閉合 |
| O203 | O203 | W 場同步速率: R_world 嘅缺失維度 (Sync Rate & the R_world Structure Gap) | 全部閉合 |
| O204 | O204 | SESSION START | 全部閉合 |
| O206 | O206 | SESSION START | 開放 |
| O207 | O207 | 玻色質量塔 (Boson Mass Tower: m_n = M₀√γ_n) | 全部閉合 |
| O208 | O208 | 驗證架構標準 (Verification Architecture) | 全部閉合 |
| O209 | O209 | 識別層：選擇律代數 (Selection Algebra) | 部分閉合 |
| O210 | O210 | 代數層：因果張量代數 (Causal Tensor Algebra) | 全部閉合 |
| O211 | O211 | 生成層：幾何生成算子 (Geometry Generation) | 全部閉合 |
| O212 | O212 | 錨定理 (Anchor Theorem) | 全部閉合 |
| O213 | O213 | 動力學層：世界演化方程（World Dynamics） | 全部閉合 |
| O214 | O214 | 物質/暗物質/真空能定義統一（宇宙能量預算比較之先決條件） | 全部閉合 |
| O215 | O215 | 質量譜 → 宇宙能量預算第一性原理（3/60, 16/60, 41/60 唯一解） | 全部閉合 |
| O216 | O216 SESSION_START | Δn_color 色荷纏繞 | 全部閉合 |
| O217 | O217 SESSION_START | 4-正則必要性 | 全部閉合 |
| O218 | O218 SESSION_START | 目錄身份判準 | 開放 |
| O219 | O219 SESSION_START | pt↔mode 索引前提審計 | 開放 |
| O220 | 自旋之結構起源 (Spin Origin): 自旋是什麼、為何宇宙與費米子必須帶自旋 | — | 開放 |
| O221 | 連續化層：低能極限過渡 (Continuum / Low-Energy Limit: GR & QM 還原) | — | 部分閉合 |
| O222 | 求值語義層：Lazy Load → 量子態 (Evaluation Semantics: Lazy Load → Quantum State) | — | 部分閉合 |
| O223 | O223 | 觀察者位置域結構 (Observer-Position Domains / Anchor Gauge) | 全部閉合 |
| O224 | amplitude／複相位層之構造（Complex-Phase / Amplitude Layer） | — | 部分閉合 |
| O225 | 機制層 Born 權重／概率結構之強制（Mechanism-Level Born Forcing） | — | 部分閉合 |
| O226 | 回滾與退相干之時間結構（Rollback & Decoherence Time Structure） | — | 部分閉合 |
| O227 | 連接通道：對映表、無信號與糾纏熵（Mapping Channel / No-Signalling） | — | 部分閉合 |
| O228 | 求值語義之資源幾何與最小性（Resource Geometry & Minimality） | — | 部分閉合 |
| O229 | μ² 與 B = 4 在粒子對賬中之具體實現（μ² & B=4 in Particle Accounting） | — | 全部閉合 |
| O230 | 核衰變通道算子身份 (Nuclear Decay Channel Operator Identity) | — | 部分閉合 |
| O231 | 超楊-米爾斯 IDCM 解 vs QFT | — | 已註冊 |
| O232 | 恆星年齡下界 vs IDCM 因果視界 (rendering window) | 13.8 Gyr 宇宙年齡張力之結構裁決 | 全部閉合 |
| O233 | C_f 結構身份：生成器 hunt → 鋸齒/Z₂ → lepton 槽 n≡1 (mod 4)（由 O206 第10-15輪轉移） | — | 部分閉合 |
| O234 | 質量公式檢驗方法反推: RG-invariant 質量比驗證協議 (FLAG/PDG 凍結觀測層) | — | 全部閉合 |
| O235 | C_f 鋸齒 Z₂ 嘅 tick-宇稱/時間處理假説 (88-chain checkerboard/staggered 對偶) | — | 部分閉合 |
| O236 | 質量來源整合路線 (Mass Origin Integration: n槽位 × γ階梯 × C_f代際塊) | — | 部分閉合 |
| O237 | 質量路線圖:由K-Chain駐波到質量測量/感知(全鏈步驟+未知數盤點) | — | 部分閉合 |
| O238 | 質量 = 代價^{φ²}：逆推質量譜 (mass as geometric cost) | — | 部分閉合 |
| O239 | 挫阻缺陷張力凝聚體：A₅ 幾何層 → 質量層嘅生成機制承接 (mass ↔ A₅-tension bridge) | — | 部分閉合 |
| O240 | 真空能閉合攻堅: V_Lambda 鏈審計 + 5 殘餘 (Delta/19/gamma-VEV/V_Lambda-SSB) + 標籤審計 | — | 全部閉合 |
| O241 | 量子漲落實證現象之 IDCM 推導: Casimir/零點譜差 + 量子-經典動力學 | — | 部分閉合 |
| O242 | 量子漲落可觀測性判定: 差分譜量 vs 絕對真空能密度 (可測/不可測分層) | — | 全部閉合 |
| O243 | 三重相變 No-Go 盲測: 真空一階/二階/拓撲相變結構排除 + Gemini 反駁 | — | 全部閉合 |
| O244 | O244 | FSR-QFT 費曼圖求值與通用張量 (承接 O137 R23 尾巴) | 全部閉合 |
| O245 | 2I ⊂ SU(2) finite-subgroup 身份驗證（IDCM↔LQG 升格收斂） | — | 全部閉合 |
| O246 | tan 家族開譜掃描：sin/cos → tan²(nπ/88) 全開放問題探針 | — | 已註冊 |
| O247 | 天然污染階梯：三水平簇生成規則 + 核子原子層缺口 + 相位同步污染框架 | — | 部分閉合 |
| O248 | 相位橋: W-field 相位模 → 觀測質量污染 (相位同步污染框架形式化, 承接 O247 Q3) | — | 全部閉合 |
| O249 | 觀測飽和容量 (Observation Saturation Capacity) | — | 已註冊 |
| O250 | 重整化次數與 K-Tree 關聯性：IDCM-native running 階數對應探針 | — | 部分閉合 |
| O251 | 質量檔案 schema：譜點/標度/算子/拓撲/標籤五層格式規範 (讀數 reframe, 承接 O237 pipeline + O248 讀數裁決) | — | 撤回 |
| O252 | 視線遮蔽算子 τ(v): 世界環幾何 → 視線光深 (零新常數, 盲測 dip) | — | 部分閉合 |
| O253 | 晶體拓撲同步 | 兩塊分離晶體之間嘅拓撲非局域同步(共享陳數)可行性 | 撤回 |
| O254 | 晶體拓撲同步 | 兩塊分離晶體之間嘅拓撲非局域同步(共享陳數)可行性 | 已註冊 |
| O255 | c 結構上限 → no-signaling: 色散結構必然 v≤c, 非時空公設 (O254 scripts/03 概念結論) | — | 部分閉合 |
| O256 | C_ℓ 連續譜包絡 (lensed Silk 複合形式) | 由 K_Chain/K_Tree 推出, 閉合 O202 R6 | 部分閉合 |
| O257 | 1/76 log10 修正機制: 點解 M_comp = M_pl·10^{-(1/γ₆−1/76)} 喺 log10 尺度出現 −1/76 加法修正 | — | 部分閉合 |
| O258 | m_ββ Majorana 相位理論: 由 dim-5 算符推導 (α,β) 相位結構, 帶 [6.108, 22.169] meV 內預言 | — | 撤回 |
| P1 | 大爆炸核合成 BBN | 三比值 + η_B 閉合 | 開放 |
| P2 | CKM 夸克混合矩陣重建 | — | 開放 |
| P3 | CMB 角功率譜閉合 C_l | — | 全部閉合 |
| P3/high-l-tail-transfer | IDCM C_ℓ 譜高ℓ尾傳輸函數模型 (ℓ>1409) | — | 開放 |
| P4 | CMB 冷斑 + A5 拓撲 | — | 開放 |
| P5 | 晶格應力 + UHECR 各向異性 | — | 開放 |
| P6 | 中微子質量 | W-field p6 模式 | 開放 |
| P7 | 再電離 + 光學深度 | — | 開放 |
| P8 | H0 張力 (Hubble) | — | 開放 |
| P9 | K_Chain 數域 | 946 拍頻無理數結構 | 開放 |
| P10 | K_Tree 結構 | 33 層 | 開放 |
| P11 | Little Red Dots (JWST) | — | 開放 |
| P12 | UHECR 超高能宇宙射線 | — | 開放 |
| P13 | 拍頻周期表 | 946 無理數可分離三角表 | 部分閉合 |
| P14 | A5 晶網全域路由 + W-field 通信 | — | 部分閉合 |
| P15 | 早期推導三件套 (2026-08 atlas) | — | 開放 |
| p7_reionization | 再電離 + 光學深度 | — | 已合併 |

## 活躍中 O（open/partial 摘要）

完整狀態以 `problem_register/register.py check` 為準；O 索引見 `problem_register/` 同 register.jsonl。