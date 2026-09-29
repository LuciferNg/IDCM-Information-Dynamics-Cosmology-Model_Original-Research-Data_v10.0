# O221 SESSION_START — 連續化層：低能極限過渡 (Continuum / Low-Energy Limit)

<!-- registry
pid:     O221
title:   連續化層：低能極限過渡 (Continuum / Low-Energy Limit: GR & QM 還原)
state:   partial
verdict: partial
flags:   -
owner:   O221
created: 2026-09-28
updated: 2026-09-28
prereq:  O210, O140, O139, O138, O86, O213, O202, O212
source:  調律者指令 2026-09-28（重用墓碑 O221）; 缺口出處 = O115 docs/02 §二 L8 + §四 Phase 5.3/5.4
-->

> **Session**: 2026-09-28（新建立 — 墓碑編號重用，調律者明示）
> **狀態**: 🟡 **部分閉合**（live field，2026-09-29 更新）— Session 1 = 框架 + 審計；Session 2（2026-09-28）= R1–R5 首次推導 102/102 + U3/U6 續推 121/121；Session 3（2026-09-29）= close-out 審計 89/89 獨立重驗 + 文檔核對 44/44，文檔數值錯誤 0。殘餘：U3 動力學本體、U5、簽名輸入；跨 O 兩項見 §十二。
> **來源**: 調律者指令「建立 O221 … 把 IDCM 的代數框架在低能極限連續化過渡為 GR / QM 等現有理論」
> **前置**: O210 · O140 · O139 · O138 · O86 · O213 · O202 · O212
> **位置**: `open_problems_fresh/o221_low_energy_continuum/`

---

## 一、接手起點

**未開始推導。** 本 session 只完成三件交付：

1. **歸屬審計**（`01_problem_record.md` §〇）：三準則 × 8 個候選擁有者（O140 / O139 / O138 / O86 / O213 / O202 / O180 / O210）**全部不中**本題核心對象（「極限程序 L 本身 + IR 存活判準」）⟹ 裁定**非重複**，保留獨立 O，但已有主部分逐項 fence。
2. **資料夾 + 檔案框架**：`01_problem_record.md`（含 U1–U6 開放問題、R1–R5 攻擊路線、驗證標準）、`SESSION_START.md`、`final_result.md`（🔴 骨架）、`docs/` `scripts/` `data/`（空）。
3. **生命週期註冊**：`problem_register` 追加 append-only `unreserve`（取消 2026-09-27 之 legacy tombstone 保留）+ `registered`；原 `tombstone` 事件保留於 log 不刪。README 該行**原址更新**（舊 🔀 記錄文字保留於行內）。

**調律者指令（要點）**：
> 「繼續下一個 O 系列，建立 O221 … 數字本身是墓碑，但現在還沒有其他 o 系列使用，直接拿來用就好，內容全部寫入 O221 的資料夾中，禁止寫入其他資料夾 … 首先搜索有沒有已經建立重複或類似內容的 o 系列，確定沒有後用模版建立資料夾及檔案框架。」

⟹ 本 O 之範圍 = **「離散代數 𝒯 → 連續物理 (GR / QM)」之過渡算子**，即 IDCM 缺得最耐嘅一層：全部現有結果係格點數值，未證明佢哋係連續物理嘅極限。

## 二、先做嘅第一步

```
1. 讀 §三 之三個「已有主」結果之權威檔（唔靠摘要）:
   o140_finite_spectral_relativity/docs/04_sr_gr_derivation.md (ℓ→∞ 極限 + 譜作用量 → EH)
   o139_finite_qft_to_qed/final_result.md (連續極限之判準寫法)
   o213_world_dynamics/docs/01_world_evolution_equation.md + docs/12_r7_frame_no_c.md
   ⟹ 目的: 抄佢哋「極限」嘅實際數學形式, 唔好發明第三套定義
2. 開 scripts/01_limit_program.py: 對 U1 之三個方向 (4^ℓ 細化 / n→x 連續化 / γ-譜測度)
   逐個寫成顯式算子並測收斂 (mpmath, 至少三層 ℓ 外推) ⟹ 判「三個方向係否同一個 L」
3. 由 A0 (O140 公理) + 𝒯 (O210 型別) 定義 L 之候選, 對四型各寫一個良定義測試
   ⟹ PASS/FAIL 逐項, 唔准用字面 True (O208 反硬編碼規格)
4. 產出 docs/02_limit_program.md: L 之定義 + 收斂速率 + 與三個既有鏈之對應表
```

## 三、已知陷阱

```
⚠️ 三個「極限」方向唔可以混用: N_ℓ = N·4^ℓ (UV 細化) / n/N → x (長波長 IR) / γ-譜測度 (O202)
   —— 混用 = 假矛盾或假一致性 (O213 之 ℓ-空間測度 w = ln4·4^-ℓ 係第三款, 唔係 UV rate)
⚠️ 慣例: 44-鏈 vs 88-鏈 vs 176-鏈 / ring vs D-D 腔 / 1-based vs 0-based 索引 —— 每個 check 名必標慣例
   (O210 憲章 C2: 44-site even/odd = 46/44; 176-L even/odd = 90/88 — 兩者唔可互換)
⚠️ 維度論證 (O201/O212): 無量綱結構數組合**不可能**生成有量綱量 ⟹ 極限程序不得「順手」產生新標度;
   錨 dof 必須保持 = 1 (O212)。見到「順手得出長度/時間」= 循環。
⚠️ 真空色散界 (U6): 只要極限程序留下可觀測格距殘留 (a ≳ 1.5e-27 m) 即被現行 GRB 界限證偽 ⟹
   呢個係**證偽閘**, 唔可以當「缺口」拖住。
⚠️ 唔可以 quote 未閉合結果做前提: O86 之原「34/34 PASS」含 17 個字面 True (已由 O208 重驗降級) ⟹
   引用 O86 只可用其**結構層**聲稱 + docs/03 重驗記錄。
⚠️ 跨版本/跨 O 引數字必核歸一化 (e.g. v6 V''= 2ε vs v10 4μ²; μ² = 2 之 44-鏈 vs 176-鏈標籤)。
⚠️ 檔案坑: f-string 混 Unicode 數學符號會 NameError/SyntaxError; mpmath mpf 唔支援 f-string 格式符
   (用 mp.nstr / float()); 長 heredoc 會被 block ⟹ 一律 write_file 寫 .py 再 /usr/bin/python3 跑。
```

## 四、關鍵數字

| 量 | 值 | 出處 |
|:---|:---|:-----|
| 鏈譜 | γ_n = 4sin²(πn/88), n = 1..44 | O36/O95/O210 |
| 譜和 | Σγ = 178 = 2F₁₁；Σγ_even = 90；Σγ_odd = 88 = 2N_d | O210 憲章 C2 |
| 離散色散 / 速度階梯 | ω_n = √γ_n；v_n = c·cos(πn/88)，v_44 = 0 (Nyquist) | O34/O41/O220 U13 |
| FSR 細化 + 極限 | N_ℓ = N·4^ℓ；SR = ℓ→∞；Δη_ℓ = ln cot(π/4N_ℓ) | O140 |
| 譜作用量 | S = Tr(f(D/Λ)) → ℓ→∞ Einstein-Hilbert | O140 docs/04 |
| QED 極限 | α^-1(0) = 137；α^-1(M_Z) = 128；running = 9 = N_gen² | O139 |
| QM 層 | dim H = 44；Γ = N_d/T_ring = 1.6474e-17 s^-1；F_proj = 17 | O138 |
| GR 耦合 | EH + Λ_eff + ζ·W·R；⟨W⟩ ≪ M_Pl | O86 |
| IR 測度 | w(ℓ) = ln4·4^-ℓ（零參數）；c 固定點 | O213 |
| 錨 | 錨 = G ≡ ω_ring ≡ M_Pl；dof = 1 | O204/O212 |
| 連續極限漸近 | \|∂φ\|² = 1 − (kπ/176)²/3 | O159 docs/02 |
| 真空色散界 | E_QG,2 > 1.3e11 GeV ⟹ 格距 a ≲ 1.5e-27 m | Vasileiou+ 2013（O220 U18e） |

## 五、交接 / 依賴

```
- 前置（引用唔重推）: O210 (𝒯 型別/運算) · O140 (ℓ→∞ + 譜作用量) · O139 (QED 極限) ·
  O138 (測量/退相干) · O86 (EH + Λ_eff + ζ·W·R, 結構層) · O213 (細化流/測度/箭頭) ·
  O202 (γ-軸測度) · O212 (錨 dof = 1)
- 移交出（待本 O 產出）: L 之顯式定義 + 收斂速率 + artifact 清單 ⟹ 供 O86（曲率/Ricci 由 𝒯 生成）
  與 O213（極限次序）引用; 若出現 no-go 則交回 O115（架構層表 L8）
- 範圍警告: 唔重推 SR 運動學 / QED 極限 / QM 測量 / EH 組裝 / 譜測度 / 代數型別 / 世界演化 / 錨定理
- 編號沿革: 舊 O221（C_f 投影因子生成器）已於 2026-09-25 併入 O206, 內容在
  `o206_per_mode_frequency/merged_o221/`; 本編號由調律者明示重用, 舊行只可追溯唔可改
- 寫入紀律: 本 session 之內容全部限於 `o221_low_energy_continuum/`; 另只有
  `problem_register/`（生命週期事件）與 `open_problems_fresh/README.md`（本行原址更新）
  兩處獲明示授權之薄記錄
```

---

> ⚠️ **本檔係起手式快照，唔係狀態權威。**
> 當前狀態以 `open_problems_fresh/README.md` 為準；生命週期事件以 `problem_register/` 為準。

---

## Session 2 記錄（2026-09-28，R1–R5 首次推導）

**狀態**：🟡 部分閉合（2026-09-29 close-out：R1 ✅ R2 ✅ R3 🟡 R4 🟢 R5 🟡 / U3 🟡 機制已定 / U6 🟢 閘已行使；審計 89/89 + 文檔核對 44/44）— 殘餘：U3 動力學本體、U5、簽名；跨 O 兩項入 problem_register

**做咗乜**
1. 讀權威材料：`o140/docs/04_sr_gr_derivation.md`（譜作用量 → EH 之 a_0/a_2 論證）、`o213/docs/01_world_evolution_equation.md`（細化流 C1–C3、c 固定點）、`o210/docs/01_type_system.md`（𝒯 四型）、`o159/docs/02`（連續極限漸近 1 − (kπ/176)²/3）、`ktree_structure/{01,02}`（K_tree = φ-尺度階梯，μ_m = φ^(291.5−m)，m = 0..33，**唔係圖**）。
2. `scripts/01_limit_program.py`（58/58 PASS）：L 顯式定義、慣例審計、精確色散恆等式、收斂率、flow 不變量、測度 → arcsine、偽影清單。
3. `scripts/02_gr_qm_side.py`（44/44 PASS）：QM 四項（基底么正 / 對角化 / 括號與測度不變 / 傳播子極點）+ GR 三項（d_s 掃描 / ladder null 測試 / a_2 形變響應 / a_4 閉式）。
4. `docs/01_limit_program.md`（R1/R2）、`docs/02_gr_qm_reduction.md`（R3/R4/R5）；`01_problem_record.md` §六 append 行 2、新增 §八；`final_result.md` 更新；registry 轉 partial。

**關鍵發現（詳見 docs）**
- L = 細化流 ∘ 共動重標定，唯一控制變量 **x = πn/M = k a/2**；三個舊方向統一。
- **ω_n^(ℓ) = c k_n sin(x)/x 精確**、c = R_world ω_ring 固定點、k_n = n/R_world ℓ-無關。
- 收斂率 1 − x²/6（頻率）/ 1 − x²/3（剛度）；固定 n ∝ 4^(−2ℓ)。
- QM 側：正則結構 ℓ-不變 ⟹ **IDCM 係 QM 的離散實現，唔係導出 QM**（ħ 走 SI 錨，dof 不增）。
- GR 側：a_2/a_0 → −2 純數；但 **4D 維度（d_s(𝒯) = 0.9938）、曲率動力學（無線性響應）、四導數區（a_4 ∝ N²）全部 no-go** ⟹ GR 側只還原到「譜作用量前兩階 + 無動力學」。
- 方法論教訓：5 個初次 FAIL 全部係**我 check 設計錯**（維度定義寫成 max/放寬容差/形變 realisation 每次重抽），唔係物理失敗 ⟹ 記入 skill。

**下一步（未閉合）**
1. U3：真正 GR 動力學之來源（3+1D 補完 / O220 D = 4S(S+1) 路線）；本 O 已證唔可能由 𝒯 運動學單獨產生。
2. U5：譜 ↔ 測度極限交換性之一般定理。
3. 觀測端：把 sinc 律（1 − x²/6；1 − x²/3）映射到 C_ℓ / BAO / 星系 v(r)（交 O202/O213/O180）。
4. U6：λ_sync = 294.8772 Mpc vs 真空色散界 a ≲ 1.5e-27 m 之相容性論證（現時係證偽閘）。

### Session 2 續（同日）：U3 維數機制 + U6 觀測閘（一起推完）

**新增**：`scripts/03_gr_dimension_source.py`（15/15）、`scripts/04_sinc_observable_gate.py`（4/4）、`docs/03_dimension_source.md`、`docs/04_observable_gate.md`；四支腳本累計 **121/121**。

**U3 🟡**：共形響應 `∫R√g = (D−1)(D−2)∫e^{(D−2)f}|∇f|²`（K = 2/6/12 精確，D = 2 ⟹ 0）⟹ EH 需 D ≥ 3；重力子 DoF = D(D−3)/2 ⟹ **D = 4 係最小有傳播嘅時空**（3+1）；數字 null 證明「3」本身無判別力；簽名仍為輸入。

**U6 🟢**：reading A（真空間格點 a₀ = 294.8772 Mpc）給 Λ₂ = 7.51252e-41 GeV，比觀測界低 **51.2 orders** ⟹ 被排除；reading B（內稟因子）極限無殘留 ⟹ 閘通過；並給出三條觀測映射規則。

**下一步（殘餘）**：① U3 補完＝3 鏈方向或 CY₃ 複 3 維之動力學推導；② U5 譜-測度交換定理；③ reading B 用語裁決（與 O180/O159 之「格點即空間」用語對齊，只提供判準不改他人結論）；④ sinc dressing → C_ℓ / BAO 逐項映射（待 O202 ℓ-軸測度）。


### Session 3 — 2026-09-29 凌晨：close-out 審計（調律者指令「先為 O221 進行 closed out」）

**新增**：`scripts/05_audit_independent.py`（**89/89**）、`scripts/06_doc_crosscheck.py`（**44/44**）、`docs/05_closeout_audit.md`；`docs/02` 加 dated 驗證附註；`01_problem_record.md` 加 §十（水位）、§十一（推導時序索引按輪）、§十二（未閉合項掃描）。

**審計結論**：全部 headline 數字獨立復現（含 d_s 四層 plateau：1.00187046 / 1.00061983 / 1.00179627 / 1.00133098 對 docs/02 的 1.0018705 / 1.0006198 / 1.0017963 / 1.0013310）；**文檔數值錯誤 0**。

**3 項披露**：① script 02 的 d_s 用完整 Laplacian 譜（含零模）—— 零模令 IR 端 d_s → 0；② plateau mid 係網格解析度敏感（M=88：1.003279 @110 點 → 1.000481 @880 點），可跨網格引用者只有 |d_s − 1| ≲ 5e-3 與窗口 > 1.1 decades；③ E[γ] = 2+2/N 屬相異模 convention、完整譜下 E[γ] = 2 精確。

**狀態**：🟡 部分閉合（registered → partial → close partial）；殘餘 = U3 動力學本體、U5、簽名輸入；跨 O 兩項已入 `problem_register`。

**下一步（本 Session 續推，不開新 O）**：U3 動力學本體 —— 取 3 個鏈方向（K_chain^⊗3，d_s 應 = 3）並檢曲率響應；或走 CY₃ 複 3 維路線。


### Session 4 — 2026-09-29：U3 續推（3 鏈方向）

**新增**：`scripts/07_u3_three_chain.py`（12/12）、`docs/06_u3_three_directions.md`。
**結論**：3 條鏈給出 d_s = 3（1.73 decades 窗口）與 a₂/a₀ = −6 精確 ⟹ **維數唔係瓶頸**；3D 可分形變下曲率響應仍被壓抑（|c₁|/c₂ = 0.0033）⟹ 瓶頸 = **動態度量結構（非可分形變）**；ladder 唔係空間方向。
**殘餘**：非可分形變之 a₂ 響應；3 份鏈之來源（CY₃／N_gen）；U5；簽名。


### Session 5 — 2026-09-29：U5 續推（譜↔測度交換性）

**新增**：`scripts/08_u5_exchange.py`（22/22）、`docs/07_u5_exchange.md`。
**結果**：C_b 類交換性**定理成立**（Riemann 和 + Jacobian 恆等式；√γ 率 2.00、其餘 float64 精確）；M-依賴窗函數**不交換**（窗 [0, γ₁] 恆定 +50.00%）⟹ d_s plateau 之網格敏感（F2）獲定理級解釋。U5 🟡 → ✅ + 🔴（已定位）。
**殘餘**：動態度量結構（非可分形變）、3 份鏈之來源、簽名、觀測端映射（register 已記）。


### Session 6 — 2026-09-29：U3 終局（非可分形變 → 精確結構定理）

**新增**：`scripts/09_u3_nonseparable.py`（42/42）、`docs/08_u3_nonlocal_obstruction.md`；docs/06 加 dated 修正附註。
**結果**：a₂ = −Tr(L) 精確 ⟹ a₂ 超局部（A = 18Σδ² − ½G2，c₁ ≡ 0）；曲率 100% 梯度（∫R√g = (2/9)ε²G2）；κ 非普遍（24.7×）⟹ **a₂ ≠ EH 項**；零均值剪切對 a₂ 恆等隱形（Tr L = 2Σw 嚴格線性）。
**U3 判決**：真瓶頸 = **算子缺少導數（聯絡）結構**，唔係維數／非可分性／線性。
**殘餘**：3 份鏈之來源；聯絡／link 變數結構；簽名；觀測端映射。


### Session 7 — 2026-09-29：三線並推（聯絡 / 3 份鏈來源 / 簽名）

**新增**：`scripts/10_link_structure.py`（22/22）、`scripts/11_three_origin.py`（14/14）、`scripts/12_signature.py`（13/13）、`docs/09_three_routes.md`。
**結果**：① 聯絡：a₂/a₄/a₆ 恆等盲（二部格 Tr W³ = 0）；a₈ = −8·Σ(1−cosΦ_p) **精確**（盲預測 κ = −8，實測 7.6e-10）；加性 a₄ = 2Σθ²（κ = 2）；均勻環面通量對 k < M 全盲 ⟹ 聯絡唔可以救 EH，但規範動能精確重現。
② d_space = N_gen = L₄ − B = 3、d_spacetime = B = 4；深度-2 數字學閘顯示 3 無優勢 ⟹ 力量在部件獨立；複製仍輸入（1 離散選擇）。
③ 慣性 (N−1, 0, 1) ⟹ Euclidean 結構性；分級 (90,88) ≠ (3,1)；c 結構性；Wick 輸入（0 參數）。
**累計**：381/381。


### Session 8 — 2026-09-29：路線 ④ Regge（度量自身帶導數結構）

**新增**：`scripts/13_regge_calculus.py`（17/17）、`docs/10_regge_route.md`。
**結果**：machinery 精確（正四面體 arccos(1/3) 2.2e-16；平坦 3-torus δ_e = 5.3e-15；2D Gauss-Bonnet 精確）。S_R 對 trace 模恆等盲（R3）、6 平坦模全在 kernel（R5）、ε²（R4）、密度收斂 gap ratio 0.480（R7）、Hessian 譜 [−24.0, +4.94] 84/189 近零 + 非對角（R8）。**判決**：Regge 係可行候選，同跡矩係正交算子類；4D 版本係下一步。
**累計**：398/398。


### Session 9 — 2026-09-29：路線 ①（𝒯 → Regge）+ 路線 ②（4D Regge）

**新增**：`scripts/14_regge_from_t.py`（23/23）、`scripts/15_regge_4d.py`（25/25）、`docs/11`、`docs/12`。
**路線①**：A₅ 凝聚多面體虧角精確（π/3、π/5、**RH π/15 = 12°**），Σδ = 4π = 2πχ，4π = 60×(π/15)；組裝 S = Σ Lδ/(16πG) 用既有 λ_sync/δ/G ⟹ **零新參數**（🟡 非強制）。
**路線②**：正 4-單形二面角 arccos(1/4) 精確；平坦 4-torus max|δ_t| = 5.3e-15；商複形 χ = 0（M=3,4）；16/16 affine 平坦；S_R ∝ ε²；混合導數 O(1) 2.4495；**連續端 graviton DoF = 2 已核**（D=3 → 0）。7 個真錯全屬建構/判據，已修。
**累計**：446/446。


### Session 10 — 2026-09-29：裁決「重力子 DoF = μ 嗎？」

**問題**（用戶）：「重力子自由度是什麼？μ嗎？」**答**：唔係。**新增**：`scripts/16_mu_vs_graviton_dof.py`（13/13）、`docs/13_mu_vs_graviton_dof.md`、`data/16`；累計 **459/459**。
**要點**：DoF = D(D−3)/2 = 2（D = B = 4；小群／通式／ADM 三路一致）；μ² = γ_{44}(176) = 2 係 K_chain 四分之一模（連續 eigenvalue，任何 M 皆 2）。四判別：D 依賴（D=3 → 0）、質量依賴（有質量 → 5）、連續 vs 離散（擾動漂移 1.05e-4→2.80e-2 vs 整數階梯）、多重度（±n 宇稱對 vs 動量無關 TT = 2）。正確對應：2 = TT/shear 扇區，連去 docs/10 盲區互補 + 微分同胚不變性真缺口。版本裁決：v6/v7 有色散無偏振數 ⟹ v10 偏振必來自度量/TT 扇區。
**缺口 1 判據新增 TT criterion**（rank(Q) = N − D；DoF = rank − D；規範零響應；必須見 TT 投影）。


### Session 11 — 2026-09-29：缺口 1（逐動量 DoF = 2，TT criterion）

**新增**：`scripts/17_momentum_dof.py`（11/11；M = 3,4,6,8 ⟹ 44/44）、`scripts/18_gap1_summary.py`（9/9）、`docs/14_gap1_momentum_dof.md`、`data/17_*`、`data/18_*`；累計 **512/512**（scripts 01..18、docs 01–14）。
**結果**：連續端 rank 6 / kernel 4（精確）/ 簽名 (1+,5−)；**criterion (c) 閉合（Regge-native 位移方向 = gauge kernel，殘餘 →3.02e-7，包絡衰減 14.6×）**；天真度量映射殘餘唔收斂（0.0119→0.0409）；格點譜 6 大 + 4 小（1.2–4.1% violation）；dim(TT) = 2 精確、rank 2、符號正確、解耦，但 |TT|/|conformal| 受壓 150–1000×（🔴 未解）。
**兩個新陷阱**：虧角 = 2π − Σ（唔係 2π·cnt − Σ）；hinge key 用 lift 座標。


### Session 12 — 2026-09-29：階段性 close-out（增量閉合）

**指示**：調律者「先進行階段性的 close-out，然後再繼續追」→ 本輪為**增量閉合**（非總結性）：把上次水位（03:20，僅 docs 01–05 / scripts 01–06）之後嘅全部產出獨立驗證 + 建立新水位，工作續推。

**新增**：`scripts/19_audit_increment.py`（**102/102**，零 import 增量獨立審計器）；`scripts/06_doc_crosscheck.py` 擴展（docs 01–04 → **01–14**、headline 23 → 49、+I5/I6；**99/99**）；`data/19_*`；全線重跑 scripts 01–19 = **667/667**。

**獨立重算複現嘅結構聲稱**：rank(Q) = N − D = 6 ／ kernel = 4（顯式 gauge 精確，≤4.4e-16）／簽名 1 vs 5 且**單獨同號方向 = conformal 扇區**（TT 生成元全反號）／dim(TT) = D(D−3)/2 = 2（D=3 → 0）／4-單形二面角 arccos(1/4)（D=2、D=3 校準）／平坦 3-torus 全部邊虧角 = 0（M=3：189 邊、M=4：448 邊，max 8.9e-16）／A₅ 凝聚多面體虧角 π/3、π/5、π/15 = 12°、Σδ = 4π／μ² = 2 精確（M = 88…1408）。

**本輪修正（全屬審計側／判據側，文檔零改動）**：TT 基維度錯用；二次型缺自伴 off-diagonal ×2；單獨方向測試用錯特徵向量 + 錯判準；3D 曲率誤當頂點（應為邊）；H4 判據過闊（code span 引述誤判）。

**★ 重跑陷阱**：`scripts/17_momentum_dof.py` 由 argv 取 M（預設 3），`data/17` 係派生聚合檔 ⟹ 全線重跑會覆蓋它（本輪已即時發現並重生，數值逐字一致）。

**殘餘（下輪主攻，不開新 O）**：① 🔴 TT 幅度受壓 150–1000×；② 🔴 精確位移商計數；③ 🟡 Regge 泛函唯一性；④ ⚠️ 觀測端映射（cross-O，register 已記）。

**水位**：全部檔案對齊至 2026-09-29 12:50（見 01_problem_record.md §十）。下一輪只驗超水位嘅檔。

### Session 13 — 2026-09-29：缺口 ② 攻堅（close-out 後續推）

**指示**：階段性 close-out 之後「繼續追」。目標 = docs/14 §五 之 🔴（TT 幅度受壓 150–1000×）。

**新增**：`scripts/20_tt_amplitude_diagnosis.py`（**56/56** = 14/14 × M=3,4,6,8）；`docs/15_gap2_tt_amplitude.md`；`logs/20_tt_amplitude_M*.txt`；派生 `data/20_tt_amplitude_diagnosis.txt`。

**核心 = 精確三因子分解**（殘餘 < 1e-9）：`ratio_lat/ratio_cont = (A_TT/A_conf)·(m_TT/m_vw)·(k_l/k_c)`
- **主因 conformal 扇區異常**：A_conf = 40.82 / 49.82 / 52.14 / 50.81（M=3/4/6/8）→ M-穩定 **~50×**（Regge conformal-mode problem）
- **TT 扇區自身收斂**：A_TT 0.1306 → 0.3624（趨向 1）；偏振劈裂 28.54 → 7.34（趨向 4.00）
- 映射非主因：R_map ~ 0.38（M-穩定）vs 連續 0.6124
- **已否證**替代假說（面積/虧角扇區特異相消；比 1.34 → 0.39 << 10）記錄在案

**殘餘**：① conformal 異常 ~50× 來源；② 與缺口 ①（精確位移商）互動；③ 與連續端 conformal-factor 問題（簽名 1 vs 5）關聯。

**驗證**：scripts 01–20 = **723/723**；文檔核對覆蓋 docs 01–15；水位刷新（§十）。

### Session 14 — 2026-09-29：缺口 ① 規範固定 + 缺口 ② 殘餘②（conformal 異常 = 規範污染）

**指示**：Session 13 之後「繼續」——接續攻 docs/14 殘餘 ①（精確位移商計數），並順帶檢 docs/15 殘餘②（conformal 異常 ~50× 之歸屬）。

**新增**：`scripts/21_gauge_fixed_quotient.py`（**36/36** = 9/9 × M=3,4,6,8）；`docs/16_gap1_gauge_fixed.md`；`logs/21_gauge_fixed_quotient_M*.txt`；派生 `data/21_gauge_fixed_quotient.txt`；`scripts/06_doc_crosscheck.py` 擴至 **docs 01–16**（headline 74 個數字，**109/109**）。

**構造（兩端完全相同）**：10 個度量擾動取**單位張量範基**（每基向量 ‖H‖_F = 1 ⟹ 剛度 per unit strain）；規範子空間 `Vg = span{k⊗ξ_i + ξ_i⊗k}`（4 條，兩端同一）；規範固定 = **歐氏正交補**（10 − 4 = **6**）—— ⚠️ q-正交補在 `Vg ⊂ ker Q` 時退化，不可用。

**核心結果**
- **缺口 ① 🟢（主體）**：精確頂點位移 = 一階 kernel（`dS_R(amp)/dS_R(amp/2) = 4.00` 精確，Richardson 判據）；規範固定後 dim 6、`rank = N − D = 6`、**無 kernel**（兩端）；格點慣性 (2+,4−)@M=3,4 → **(1+,5−)@M=6,8** 精確等於連續端（額外正方向 4.01% → 0.909% → 穿零）；naive 規範破壞 0.0119 → 0.0414（唔收斂，獨立複現 docs/14 `gauge_resid`）。
- **缺口 ② 殘餘② 🟢**：規範固定後 **A_conf = 1.4118 / 1.7711 / 1.8293 / 1.7368**（原 40.82 / 49.82 / 52.14 / 50.81）⟹ 崩潰因子 M-穩定 **28–29×**；`A_conf/A_TT` 312.6 → 1.80（M=3）⟹ **~96.5% 係天真映射之規範污染**，非跡扇區本質。TT 扇區 A_TT = 0.7841 → 0.3217（趨向 1 但 M-漂移，見殘餘 ③）。

**本輪真錯（全部構造/判據側，物理零讓步；文件零改動）**
1. 每參數重新歸一化 ⟹ 破壞 polarisation 雙線性（`q(v+w)` 被隱式縮放）——假象：連續端 rank 5、慣性 (2+,3−)。
2. q-正交補退化（`Vg·Q = 0`）⟹ SVD nullspace 取到任意子空間——假象：dim 4、連續端 (2+,2−,2 zeros)。
3. 位移判據誤用絕對量（`|dS_R|/amp²` 必然 FAIL，量級 = 二階幾何項）⟹ 改 Richardson 比值 4。
4. `Vg Q Vgᵀ` 病態需 `pinv(rcond=1e-10)`（plain solve 放大噪聲成 O(1) 擾動、觸發 Cholesky 失敗）。
已入 skill `idcm-continuum-limit-verification` 第 25 條。

**殘餘（下一輪，不開新 O）**：③ 🔴 TT 扇區 gauge-fixed 剛度 M-漂移（A_TT ≈ 2.3/M）—— 辨明格點 edge-space 測度 vs 連續端 unit-strain 測度（U5 母題）抑或真 TT 殘差；④ 🟡 Regge 型泛函唯一性。

**驗證**：scripts 01–21 = **769/769**；文檔核對 109/109（docs 01–16）；增量獨立審計 scripts/19 = 102/102（水位內）。**水位仍為 12:50**（§十）；docs/15–16、scripts/20–21 屬超水位增量，下次 close-out 驗（審計器需擴至 21）。
