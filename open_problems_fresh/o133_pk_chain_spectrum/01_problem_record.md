# O133 — P(k) 鏈譜分析

> **創建日期**: 2026-08-29
> **狀態**: 🟢 已閉合 (2026-09-02 — v9.0 推導驗證 + v10.0 遷移)
> **來源**: v9.0 項目審計 — `open_problems_fresh/pk_chain_spectrum/`
> **前置**: O100 (C_ℓ→P(k)) 🟢, O76 (z 紅移) 🟢
> **定位**: 從 v9.0 pk_chain_spectrum/ 遷移 — K_Chain 功率譜 P(k) 喺 v10.0 O100 框架中的驗證

---

## 一、問題

從 v9.0 pk_chain_spectrum/ 遷移 — K_Chain 功率譜 P(k) 喺 v10.0 O100 框架中的驗證。

**原始推導**: v9.0 `P(k) = Σ_{n=1}^{43} γ_n·G(k−k_n)`, k_n = 2πn/R_world, σ = 2π/(R_world/4)。

## 二、假設

1. v9.0 推導喺 v10.0 非膨脹框架中部分或全部有效 → **❌ 已證偽 (2/9 PASS)**
2. 需要驗證的關鍵假設:
   - 是否依賴膨脹宇宙假設？ → **唔依賴 (E1-E4 審計: 數值/結構存活), 但用錯 grid + 權重**
   - 是否使用 v9.0 已 demote 的參數（如 ζ(z)）？ → **冇用 ζ(z)**
   - 是否與 v10.0 已閉合結果（O76, O100, O51 等）一致？ → **矛盾 (σ8 層面 v9.0 冇意義)**

## 三、驗證步驟結果 (2026-09-02 完成)

### 步驟 1：讀取 v9.0 原始推導 ✅
- `IDCM-v9.0--W-Field-Lattice/open_problems_fresh/pk_chain_spectrum/01_derive_pk.py`

### 步驟 2：識別 v9.0 特有假設 ✅
| 假設 | 判決 |
|:-----|:----:|
| R_H = c/72.59 作哈伯半徑 | 🔴 O73 角色替換 (R_world = 環半徑, 72.59 = ω_ring) |
| k_n = 2πn/R_world (鏈整數諧和) | 🔴 觀察結構喺環/sync grid, 唔喺鏈 grid (sync = 環 88 諧和, 鏈 n=14.0056 非整數) |
| γ_n 作 P(k) 幅度 | 🔴 幅度 = 母函 A_m × 2ℓ² transfer (O100); γ_n 係模能量, 升到 Nyquist → 反相關 |
| σ = 2π/(R_world/4) | 🟢 存活 (K_Tree L1 窗口, O140 FSR 一致) |
| 數據路徑 /tmp/... | 🔴 已死, 重指 v10.0 數據 |

### 步驟 3：在 v10.0 框架中重新驗證 ✅ (scripts/01: 2/9 PASS)
- 決定性: 模型 vs BOSS P(k) **r = −0.914** (反相關), χ²/dof = 1.39×10⁴, 包絡 log 斜率 BOSS −16.0 vs 模型 +26.4
- 結構: **sync = 88-site 環第 88 諧和 (精確整數)**; sync 諧和命中 BOSS 7/9

### 步驟 4：遷移或重建 ✅ → **遷移 O100** (scripts/02: 4/4 PASS)
- v9.0 失效 → 遷移 ✓ O100 逆投影算符 ℳ (已閉合 🟢)
- 線譜: k_m = ℓ_m/R_world, 幅度 A_m 母函 × 2ℓ², σ 展寬 (v9.0 存活部件)
- **σ8 = 0.748 vs BOSS 0.783 (Δ−4.4%)** 同量級閉合
- BAO wiggle = sync 諧和 k = 88n/R_world = 2πn/λ_sync

## 四、產出

```
o133_pk_chain_spectrum/
├── 01_problem_record.md      ← 本文件
├── SESSION_START.md          ← 會話起點 (v9.0→v10.0 驗證任務)
├── docs/
│   ├── 01_v9_validation_report.md   ← v9.0 推導驗證報告 (🔴 失效 + 根因)
│   ├── 02_v10_pk_chain_spectrum.md  ← 遷移後 v10.0 P(k) 鏈譜 (🟢 4/4 PASS)
│   ├── 03_pk_broadband.md           ← broadband 量化 (🔴 Δn=+0.86)
│   ├── 04_o86_perturbation_verdict.md ← O86 微擾判決 (🔴 3/5 PASS)
│   └── 05_broadband_synthesis.md    ← 三路徑綜合 (🔴 7/7 PASS)
├── scripts/
│   ├── 01_v9_validation.py   ← v9.0 驗證 (2/9 PASS: 失效)
│   ├── 02_v10_pk_migration.py← v10.0 遷移構建 (4/4 PASS)
│   ├── 03_pk_broadband.py    ← broadband 量化 (0/3 PASS: 未閉合)
│   ├── 04_o86_perturbation.py← O86 W-field 微擾 (3/5 PASS)
│   └── 05_broadband_synthesis.py ← 三路徑綜合 (7/7 PASS)
└── data/
    ├── boss_dr12_bao_wiggles.txt             (82 點 wiggle)
    ├── GilMarin_2016_LOWZDR12_measurement... (全範圍)
    ├── GilMarin_2016_CMASSDR12_measurement... (全範圍)
    ├── 01_v9_validation.json
    └── 02_v10_pk_migration.json
```

## 五、開放問題 (承接)

1. ~~v9.0 推導是否喺 v10.0 中有效？~~ → **否** (已證偽, 2/9 PASS)
2. ~~是否需要修正以適應非膨脹框架？~~ → **已遷移: O100 逆投影算符 ℳ**
3. ~~與 O1-O121 中已閉合結果的關係？~~ → **O100 (C_ℓ→P(k)) 🟢 + O31 (wiggle) 🟢 + O51 (BAO) ✅ 一致**
4. 🔴 P(k) 平滑 broadband — **2026-09-02 攻堅 2: 三路徑系統性缺口確立** (見 docs/03-05)
   - 結構事實: P(k_m) ∝ A_m (母函) 精確 (O100 ℳ 後果)
   - BOSS 範圍 [0.079,0.3]: IDCM n=−0.67 vs BOSS n=−1.53 → **Δn=+0.86**
   - **docs/04 (O86 微擾)**: W-field 自由 propagator P ∝ 1/ω → n=−0.75, Δn=+0.78 (正=太扁); m_δW 同 κζ 可忽略性 PASS → 傳遞唔受 W-field 修改 (3/5 PASS)
   - **docs/05 (三路徑綜合, 7/7 PASS)**: O86 (−0.75) / 全逆 Abel (−0.67) / 平滑包絡 (−1.01) 收斂 n≈−0.81±0.2 vs BOSS −1.52 → **系統性 Δn=+0.71**
   - **根因 (確立)**: IDCM ℳ 冇物質傳遞函數 T(k) 通道 (k_eq analog 缺失); ℳ 係純幾何映射, k 依賴完全抵消 → P ∝ A_m
   - **新 🔴**: 母函 m>9 延伸未閉合 (O100 標記), 影響 broadband 高 k 端 (P2b: 延伸選擇改變斜率)
   - 下一步: RSD/FOG+bias 轉換 🟡 (可補 Δn≈−0.5) / IDCM k_eq analog 🔴 / 閉合母函 m>9 🔴
5. 🟡 線譜↔星系 P(k) bias 轉換 (b², 窗函數, RSD FOG) — 可能補 broadband Δn≈−0.5
6. 🟡 O100 σ8 0.748→0.81 剩餘 1.6% (流體轉換 + 對偶 budget) — f=0.05 背景 → σ8=0.818 ✅

## 六、閉合總結

> **v9.0 P(k) 鏈譜推導 (γ_n 權重 + 鏈整數諧和 grid) 喺 v10.0 非膨脹框架中失效: 用錯 grid (鏈 vs 環/sync, 偏差 44/π) + 用錯權重 (γ_n 升 vs P(k) 降), 對真 BOSS P(k) 反相關 (r=−0.914)。正確構建 = O100 逆投影算符 ℳ: C_ℓ 峰階梯 ℓ_m/R_world + 母函幅度 + 2ℓ² transfer → σ8 = 0.748 (vs 0.783, Δ−4.4%)。v9.0 唯一存活部件: K_Tree L1 展寬窗口 σ = 2π/(R_world/4)。O133 閉合 = v9.0→v10.0 P(k) 遷移完成, 剩餘缺口 (broadband/bias/1.6%) 承接 O100/O86。**

## 七、審計日誌 (2026-09-02 驗證輪)

本輪全量驗證 5 個 scripts + 7 個 docs + 數值重算, 發現並修正:

| # | 問題 | 修正 |
|:-:|:-----|:-----|
| 1 | scripts/04 單位換算 bug: MEV_TO_MINV = 5.068e-14 (錯 3 orders) | 改 1.643e-10; m_δW: 7.07e-13 → **2.29e-9 Mpc⁻¹** (仍 ≪ k_min, 結論不變) |
| 2 | scripts/04 3 點斜率取模 bug: idx=[0,1,2] 錯配 (取咗 n=1,2,3 唔係最近模) | 改 argmin 取最近模 (n=10,26,40); n_W: −0.83 → **−0.75** (同 scripts/05 一致) |
| 3 | Δn sign 不統一: docs/04/05 用 n_BOSS−n_model (−0.70/−0.71), docs/03 用 n_model−n_BOSS (+0.86) | 統一為 **Δn = n_model − n_BOSS, 正 = 太扁**; 04/05/record/SESSION 全部改 +0.78/+0.71 |
| 4 | scripts/04 RESULT 硬編碼 +0.53 同主體計算 −0.70 矛盾 | v2 重寫一致化: Δn=+0.78 |
| 5 | docs/03「P(m=2)=P(m=3)=582 Mpc³」單位混淆 | 實際 = **1911.7/1912.3 Mpc³** (582 = 1912·h³, (Mpc/h)³ 混淆); 結構恆等 P₂≈P₃ 仍成立 (差 0.03%) |
| 6 | κζ 引用出處: docs/04 寫「O86 閉合值」 | 精確化: O100 docs/06 + scripts/06_transfer_checks.py 量化驗證值 (κζ=9.4e-22) |
| 7 | 01_problem_record §四 缺 scripts/04-05 + docs/04-05 | 已補齊 |
| 8 | SESSION_START.md 殘留舊 sign (Δn=−0.70/−0.71) | 已改 +0.78/+0.71 |

**修正後最終狀態**: scripts 01=2/9, 02=4/4, 03=0/3, 04=3/5, 05=7/7; 三路徑收斂 n≈−0.81±0.2, 系統性 Δn=+0.71 (正=太扁)。所有修正唔改變核心結論 (broadband 🔴 系統性缺口 + T(k) 通道缺失)。

## 八、推導時序索引 (2026-08-29 → 09-03)

> 依賴/時序守則: 每步只依賴**當時已存在**嘅上游結果, 唔准以新推導回溯污染舊記錄 (docs/01-03 嘅 O86 引用係「未來工作標記」, 唔係已完成結論)。

| 序 | 日期 | 步驟 | 輸入 (依賴) | Script → Doc | 結果 |
|:-:|:-----|:-----|:-----------|:-------------|:-----|
| T0 | 08-29 | O133 建立: v9.0 遷移任務定義 | v9.0 pk_chain_spectrum/ + O100 🟢 | — → `01_problem_record.md` `SESSION_START.md` | 🔴 未開始 |
| T1 | 09-02 | v9.0 推導驗證 (10 項審計) | v9.0 `01_derive_pk.py` + BOSS wiggle | `scripts/01` → `docs/01` | 🔴 失效 2/9 PASS (r=−0.914) |
| T2 | 09-02 | v10.0 遷移構建 (O100 ℳ) | T1 判決 + O100 C_ℓ→P(k) 🟢 + O140 σ | `scripts/02` → `docs/02` | 🟢 遷移 4/4 PASS (σ8=0.748) |
| T3 | 09-02 | Broadband 攻堅 1: 母函包絡判定 | T2 線譜 + BOSS CMASS/LOWZ 全範圍 | `scripts/03` → `docs/03` | 🔴 0/3 PASS (Δn=+0.86) |
| T4 | 09-02 | Broadband 攻堅 2a: O86 W-field 微擾 | T3 缺口 + O86 Lagrangian 🟢 (34/34) + O100 κζ/m_7 | `scripts/04` → `docs/04` | 🔴 3/5 PASS (Δn=+0.78) |
| T5 | 09-02 | Broadband 攻堅 2b: 三路徑綜合 | T4 判決 + 全逆 Abel + 平滑包絡 | `scripts/05` → `docs/05` | 🔴 7/7 PASS (系統性 Δn=+0.71) |
| T6 | 09-02 | 驗證輪審計 (8 項修正) | T1-T5 全量重跑 + docs 核對 | — → §七 審計日誌 | ✅ 一致性確認, 結論不變 |
| T7 | 09-03 | 時序索引 + final_result.md | T0-T6 全鏈 | — → §八 + `final_result.md` | ✅ 完成 |

**推導鏈總覽**:

```
O83 (C_ℓ 母函) → O100 (逆投影 ℳ) → O133 T2 (P(k) 線譜) → T3 (broadband 判定)
                                                             ↓
O86 (Lagrangian) + O100 (κζ, m_7) → T4 (W-field 微擾) → T5 (三路徑綜合) → 根因確立
O140 (FSR 展寬) → O133 T2 (σ 存活部件)
O31/O51 (BAO wiggle) → O133 T2 (sync 諧和)
```

**時序完整性守則** (本文件): docs/01-03 只含各自時點嘅結論; docs/04 嘅三路徑表標明「docs/05 完成」(前向引用); §五開放問題 4 係 T3-T6 累積更新 (唯一會隨進度增長嘅 section)。