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

## 活躍中 O（open/partial 摘要）

完整狀態以 `problem_register/register.py check` 為準；O 索引見 `problem_register/` 同 register.jsonl。