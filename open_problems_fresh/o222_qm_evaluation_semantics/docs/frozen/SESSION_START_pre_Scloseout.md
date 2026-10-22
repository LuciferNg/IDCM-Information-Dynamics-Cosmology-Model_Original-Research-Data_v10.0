# O222 SESSION_START — 求值語義層：Lazy Load → 量子態 (Evaluation Semantics: Lazy Load → Quantum State)

<!-- registry
pid:     O222
title:   求值語義層：Lazy Load → 量子態 (Evaluation Semantics: Lazy Load → Quantum State)
state:   registered
verdict: -
flags:   -
owner:   O222
created: 2026-09-29
updated: 2026-09-29
prereq:  O210, O138, O126, O221, O143, O223, O41, O121, O212
source:  調律者指令 2026-09-29（重用墓碑 O222）；缺口出處 = O221 docs/02「IDCM 係 QM 的離散實現，唔係導出 QM」
-->

> **Session**: 2026-09-29（新建立 — 墓碑編號重用，調律者明示）
> **狀態**: 📄 **已註冊 — 未開始推導**（本 session 只交付：歸屬審計 + 目標/框架 + 問題記錄 + 目錄結構 + 生命週期註冊）
> **來源**: 調律者指令「O221 是把 IDCM 連接到 GR，現在是時候開辟新戰線 O222，目標就是 QM」
> **前置**: O210 · O138 · O126 · O221 · O143 · O223 · O41 · O121 · O212
> **位置**: `open_problems_fresh/o222_qm_evaluation_semantics/`

---

## 一、接手起點

### 0. 調律者目標（原文，2026-09-29）

> 「O221 是把 IDCM 連接到 GR，現在是時候開辟新戰線 O222，**目標就是 QM**，而最大問題就是 **IDCM 只有 Lazy Load，沒有疊加態**，必需要把 **Lazy Load 機制解出來**才能連接 QM：**什麼時候基於什麼會確定為粒子態，基於什麼會確定為波動態，什麼是量子態，自洽性回滾的機制又是什麼**，然後才是考慮**兩者之間的連接通道**。」

⟹ 本 O 之範圍 = **IDCM 之求值語義層**（延遲表示 → 強制規則 → 自洽性回滾 → 與 QM 之連接通道）。**唔係**連續化（屬 O221）、**唔係**測量層（屬 O138）、**唔係**執行/排程（屬 O126）。

### 1. 框架（候選框架，🔴 未驗證 —— 要建、要測、可被證偽）

> ⚠️ 以下 D1–D6 係**目標物件**，唔係已確立結果。凍結定義（R1）後唔准為容納案例而修改。

```
D1  延遲項 (thunk)：  T = ⟨gen, σ, ctx⟩
     gen = 生成器 (𝒯, γ_n, θ_k)      σ = 待決讀序（長度上界 = N_d = 44，O126 讀=寫=44 雙射）
     ctx = 共享環境 (memo 表 + 已花預算)
     force : T → v（v = 模態索引 + 譜權重）；WHNF = 已定一模態、其餘未展開；
     範式展開 = Σ c_n|n⟩（36→44 模）= QM 之態向量 —— 屬**展開表示**，唔係 primitive
     ⟹ 「IDCM 冇疊加態」之正確形式 = 「IDCM 唔將範式展開當 primitive」（要證表示定理，唔係類比）

D2  判準 C1（Aut-分辨）：讀取算子 R = (扇區, 譜內容 ℓ_read, 目標模式集)
     ℓ_read ≤ 2 ⟹ R ∈ Aut(G)-不變扇區（保護 120）⟹ 分辨唔到節點 ⟹ 相位可累加 ⟹ 波動態（無定域 memo）
     ℓ_read ≥ 3 ⟹ Aut 首破缺（O143）     ⟹ 分辨到節點 ⟹ 粒子態（定域 memo）
     附帶預言：ℓ' = 5 係唯一通道 ⟹ **唔存在 ℓ = 4 之粒子化中間態**

D3  判準 C2（廣延/內涵）：廣延讀（佔據/位置/計數）vs 內涵讀（相位/頻率/干涉）
     C2 必須與 C1 **獨立**（要有「兩準則分裂」案例；同義 = 冗餘 FAIL，唔可以當兩條證據）

D4  量子態身份：L-a 本體 = T（未強制）／L-b 表示 = 範式展開（態向量、密度矩陣）／L-c 讀數 = 強制結果
     聲稱：IDCM 之「態」= L-a + ctx；密度矩陣非對角元素 = ctx 共享表結構
     RT1 表示定理（ℋ₄₄ 態 ⇄ 延遲項，構造性）／RT2 強制值分佈 = γ_n/90（回收 O138 Born）／
     RT3 **最小性**（gen 自由度 ≤ dof(𝒯)；禁由目標態反解 —— 反解 = 循環，零信息量）

D5  自洽性回滾：強制 = 求不動點 s* = N(s*)（O138）；|N(s) − s| > 0 ⟹ 候選值唔可 memo ⟹ 回滾
     約束 (i) 預算守恆 Σ 花費 ≤ 61.5 (O41)；(ii) memo 一致性（共享 thunk 兩次強制必須一致 = [P_A,P_B] = 0 之 lazy 版）；
     (iii) 無全域時鐘 ⟹ 版本序由 tick = T₄₄ = 0.96176 Gyr 提供（O126）
     窗口候選 τ_deco = 2·tick = 1.923521 Gyr —— **身份待證**（數字吻合唔算推導）

D6  連接通道：thunk↔態／force↔測量／memo↔記錄／sharing (call-by-need)↔糾纏／rollback↔退相干／
     σ 長度 44 ↔ dim ℋ／「唔需強制之部分」↔ QC 邊界 F_proj = 17
     無信號候選：共享係語義（同一 thunk 之兩消費者）而非動力學（無傳播）⟹ 強制局部 + memo 一致 ⟹ 不傳信號
     糾纏熵候選：ctx 共享圖之割熵 vs Von Neumann 熵（相等 = 結構身份 / 唔等 = 誠實 FAIL）
```

### 2. 本 session 實際交付（三件）

1. **歸屬審計**（`01_problem_record.md` §〇）：三準則 × 8 候選（O138/O126/O221/O143+O223/O41/O121/O210）逐項裁定 ⟹ 對核心對象（求值語義）**全不中** ⟹ 非重複、獨立 O，但已有主部分逐項 fence（❌ 唔重推清單）。
2. **資料夾 + 檔案框架**：`01_problem_record.md`（§〇 歸屬審計 + Q1–Q4 + 零件表 + U1–U6 + D1–D6 + R1–R7 + 驗證標準）、`SESSION_START.md`（本檔）、`final_result.md`（🔴 骨架）、`docs/` `scripts/` `data/`（空）。
3. **生命週期註冊**：`problem_register` append-only `unreserve`（取消 2026-09-27 legacy tombstone 保留）+ `registered`；原 `tombstone` 事件保留於 log 不刪。README 該行**原址更新**（舊 🔀 併入 O67 之記錄文字保留於行內）。

**未開始推導** —— R1（凍結定義）另開一輪。

## 二、先做嘅第一步

```
1. 讀權威材料（唔靠摘要）:
   o221_low_energy_continuum/docs/02_gr_qm_reduction.md  ← QM 側「非導出」結論之原文與邊界
   o138_qm_measurement_structural/final_result.md        ← Born / N(s) 不動點 / Γ / F_proj = 17 之精確形式
   o126_runtime_isa_verification/docs/04 (+05)           ← tick / POLL / 讀=寫=44 / 預算 61.5 / Γ 收口
   o143_*/SESSION_START.md + o223_observer_position_domains/docs/05–08 ← ℓ-保護表、|Aut| = 120、殼層定理
   ⟹ 目的: 抄佢哋嘅實際定義（唔好發明第三套 ℓ / 扇區 / 預算慣例）
2. scripts/01_lazy_semantics.py: 寫 D1 之可執行小型 lazy 模型（44 模, θ_k, memo, 預算計數）
   + 語法/語義規格；印每個 check 之慣例標籤（44-鏈 vs 88-鏈 vs 176-鏈）
   ⟹ PASS/FAIL 逐項，唔准字面 True（O208 反硬編碼規格）
3. docs/01_evaluation_semantics.md: 凍結 D1（定義 + 型別 + force 規則 + WHNF/範式）
   ⚠️ 凍結後即係公理；之後任何修改 = 新 doc + 明寫「移動球門」
4. 之後依 R2 → R3 → R4 → R5 → R6 → R7 順序（R2/R3 可並行；R6 最可能出 no-go，唔好一早鎖死）
```

## 三、已知陷阱

```
⚠️ 「lazy」在 v10.0 corpus **零命中**（只有 O203「速率維度惰性」與 O197「奇部 Z₁₁ 惰性」，皆與求值無關）
   ⟹ 定義要自建 + 凍結；唔可以「一路做一路改定義」（移動球門 = 擬合）
⚠️ O221 已定調「IDCM = QM 之離散實現，唔係導出 QM」⟹ 本 O 唔可以宣稱導出 Hilbert 空間公理 / ħ / Born
   （Born 已由 O138 導出並擁有）；本 O 聲稱上限 = 表示定理 + 判準 + 回滾
⚠️ O138 擁有測量/塌縮/退相干/QC 邊界 ⟹ 引用唔重推；引用前先讀其 final_result（唔好靠摘要）
⚠️ 慣例: 44-鏈 vs 88-鏈 vs 176-鏈 / ring vs D-D 腔 / 1-based vs 0-based —— 每個 check 名必標慣例
   （O210 憲章: 176-L even/odd = 90/88；88-L even/odd = 46/44 —— 兩者唔可互換）
⚠️ ℓ 「恆等零」判定必須 max-over-axes（O209）—— 固定容差會把低值奇和度假判為零
⚠️ 群幀先裁定（O223）: A₅ 錨定 ICRS 標準二十面體座標；用幾何距離自行抽軸會得錯 δ_m（群幀錯 = 群論量全錯）
⚠️ 維度論證（O201/O212）: 無量綱結構數唔可能生成有量綱量；錨 dof 必須保持 = 1 ⟹ 見到「順手得出長度/時間」= 循環
⚠️ τ_deco = 2·tick「就係回滾窗口」係**候選身份**，唔係事實 —— 兩個 O 之獨立線收斂係證據但唔等於同一件事，
   要寫出可證偽嘅身份檢驗（否則 = 事後敘事）
⚠️ 禁後驗湊算子: 準則/公式必須在看見目標前寫低；質量/態類公式必盲測 + 預測閉合
⚠️ 檔案坑: f-string 混 Unicode 數學符號會 NameError/SyntaxError；mpmath mpf 唔支援 f-string 格式符
   （用 mp.nstr / float()）；長 heredoc 會被 block ⟹ 一律 write_file 寫 .py 再用 /usr/bin/python3 跑
⚠️ 背景 shell 之 python3 = miniforge（缺 numpy/mpmath）⟹ 長腳本用 /usr/bin/python3 絕對路徑
```

## 四、關鍵數字

| 量 | 值 | 出處 |
|:---|:---|:-----|
| 鏈譜 | γ_n = 4sin²(πn/88), n = 1..44 | O36/O95/O210 |
| 譜和 | Σγ = 178 = 2F₁₁；Σγ_even = 90；Σγ_odd = 88 = 2N_d | O210 憲章 C2 / O211 |
| Hilbert 維度 | dim ℋ = 44（預算強制 61.5/B(n) = 44） | O138 |
| Born 權重 | p_n = γ_n/90（探測器時間積分，非公設） | O138 |
| 讀數成本 | ΔE_read = 44·B(n) = 61.5 = ΣΔE_read；B(n) = 123/88；E_min = 123/176 | O41/O138/O126 |
| 內觀不動點 | 44 超吸引零點 (N' = 0) + 44 排斥極點 (N' = 2)；疊加 min\|N(s) − s\| = 9.387 | O138 |
| 退相干 | Γ = N_d/T_ring = 1/(2·tick) = 1.647400e-17 s⁻¹；τ_deco = 2·tick = 1.923521 Gyr | O138/O126 |
| tick | T₄₄ = T_sync/(2N_d) = 0.96176 Gyr | O126 |
| 讀=寫 雙射 | 44 reads / 44 模；指令空間 990 = C(45,2) | O126 |
| QC 邊界 | F_proj = L₆ − 1 = 17；同數字 = dim ker(T_pipe) | O138 / O121 |
| ℓ-保護 | ℓ ≤ 2 受保護（\|Aut\| = 120）；ℓ = 3 首破缺；ℓ' = 5 唯一通道 | O143 |
| 群/殼層 | \|Aut(G)\| = 120 vs \|GeoAut\| = 60；阻挫邊 ⟺ 同 BFS 殼；θ_i 係自由態 | O223 |
| 連續化控制變量 | x = πn/M = ka/2；ω = c·k·sin(x)/x 精確 | O221 |
| 錨 | 錨 = G ≡ ω_ring ≡ M_Pl；dof = 1 | O204/O212 |

## 五、交接 / 依賴

```
- 前置（引用唔重推）: O210 (𝒯 型別/運算) · O138 (測量/Born/Γ/F_proj) · O126 (tick/POLL/雙射/預算) ·
  O221 (連續化 L；且明文唔重推 QM 測量) · O143 (ℓ-選擇律) · O223 (Aut/殼層/自由態) ·
  O41 (觀察者預算) · O121 (ker T_pipe = 17) · O212 (錨 dof = 1)
- 移交出（待本 O 產出）: 求值語義規格 D1 + 判準 C1/C2 + 表示定理 RT1–RT3 + 回滾規則 D5 + 對映表 D6
  ⟹ 供 O221（QM 側「非導出」結論之補完）、O138（回滾 ≡ 退相干之身份）、O126（POLL 之語義側）引用；
  若 R6 出 no-go（共享 ≠ 糾纏 / 無信號論證循環）⟹ 交回 O115 架構層記錄缺口
- 範圍警告（❌ 唔重推）: 測量/塌縮/Born/退相干/QC 邊界 (O138) · tick/指令/排程/預算 (O126) ·
  極限程序 L 與 IR 判準 (O221) · ℓ-保護與群結構 (O143/O223) · 預算/E_min (O41) · ker(T_pipe) (O121) ·
  𝒯 型別 (O210) · 任何導出 ħ / 導出 Hilbert 公理 / 導出 Born 之聲稱（超出本 O 上限）
- 編號沿革: 舊 O222（規範嵌入層 σ_g + 幾何手徵橋）已於 2026-09-25 併入 O67，內容在
  `o67_sm_labels/merged_o222/`；本編號由調律者明示重用（同 O221 2026-09-28 先例），舊行只可追溯唔可改
- 寫入紀律: 本 session 之內容限於 `o222_qm_evaluation_semantics/`；另只有 `problem_register/`
  （生命週期事件）與 `open_problems_fresh/README.md`（本行原址更新）兩處獲明示授權之薄記錄
```

---

> ⚠️ **本檔係起手式快照，唔係狀態權威。**
> 當前狀態以 `open_problems_fresh/README.md` 為準；生命週期事件以 `problem_register/` 為準。

---

## Session 1 記錄（2026-09-29，建立 + 歸屬審計 + 目標/框架）

**狀態**：📄 已註冊 — 未開始推導（本輪 = bootstrap only）

**做咗乜**
1. **歸屬審計**（`01_problem_record.md` §〇）：候選擁有者 8 個逐項核（O138 / O126 / O221 / O143+O223 / O41 / O121 / O210）—— 三準則對本題核心對象（求值語義：延遲表示 → 強制 → 回滾）全不中；O221 屬「主動放棄」不構成擁有；O138 係真擁有者故 fence。裁定 = **非重複、保留獨立 O**（合成型問題，必須 fence）。
2. **語料現況核實（反幻覺）**：`grep -i "lazy"` 全 v10.0 corpus = **0 命中**；「惰性」只 2 處（O203 量綱、O197 數論）⟹ 求值語義層確係未形式化，非既有工作之重複。
3. **交付檔案框架**：`01_problem_record.md`（§〇 審計 + Q1–Q4 + 零件表 17 項 + U1–U6 + D1–D6 候選框架 + R1–R7 + 驗證標準 + 反幻覺鐵律 8 條）、`SESSION_START.md`（目標 + 框架 + 陷阱 + 關鍵數字 + 交接）、`final_result.md`（🔴 骨架）、空 `docs/` `scripts/` `data/`。
4. **生命週期註冊**：`problem_register/register.py register --num 222 --reuse`（append-only `unreserve` + `registered`，原 `tombstone` 保留）+ `mirror`；README 該行**原址更新**（舊 🔀 記錄文字保留）。

**下一步（下次 session）**：R1 —— 凍結延遲項定義（`scripts/02_lazy_semantics.py` + `docs/02_evaluation_semantics.md`），再攻 R2/R3（判準 C1/C2）。

---

## Session 2 記錄（2026-09-29，調律者加註：Bell 為核心戰場 + R0 引用驗證）

**狀態**：🟡 **部分推進**（R0 🟢 完成 21/21；Bell 專線 B1–B5 🔴 未開始；D1–D6 仍全部未驗證）

**調律者加註（原文）**
> 「QM 最惡地方是貝爾不等式，其他例如測量佯謬、路徑積分等之前在 W-field 相關主題已計算過，可以引用並加以驗證。」

⟹ 分工定案：**① Bell / CHSH / EPR / 糾纏 / 無信號 = 本 O 核心戰場**；② 測量佯謬、路徑積分、Born、退相干 = **引用 + 驗證**（R0）。

**做咗乜（R0）**
1. **語料核實**：`grep -rli "貝爾\|Bell 不等式\|CHSH\|Tsirelson\|entangl\|糾纏\|no-signal"` 全 corpus ⟹ **0 命中**（唯一 "Bell" = Bell 多項式（O194/O196 累積量數學）、"Belle II" = 實驗名）⟹ Bell 確係從未處理。
2. **引用清單**：`docs/01_wfield_qm_inventory.md` — W1–W12（路徑積分 Z[J] / 傳播子 ⟨φφ⟩ / 溫州 Z_0(β) / UV cutoff / Lagrangian / Born / 預算 / Γ+tick / N(s) / 色散 / Feynman 規則 / 譜閉式），逐項標「物件性質 + 可引用範圍」。
3. **獨立驗證**：`scripts/01_verify_wfield_qm.py`（mpmath 50 dps，zero-import）⟹ **21/21 PASS，0 FAIL，3 結構聲稱排除**（`data/01_wfield_qm_verification.json` · `logs/01_wfield_qm_verification.out`）。
4. **產物（已查重）**：`Σ_n G_n(0) = 1291/4 = 322.75 EXACT`（含 Nyquist；漏 = 322.5 陷阱復現）→ **擁有者 = O32**（csc² QED）＝復現；`∏ γ_n = 4N_d = 176 EXACT` → **擁有者 = O144**（scripts/25）＝復現；`Z_0(β→0) = β^{−N_d}/(2√N_d)` ⟹ 路徑積分正規化自動含 dim ℋ = 44（與 O138 預算強制 44 兩鏈收斂）→ ✅ **查重後未見於任何 O（新連接）**，🟡 初報宜第三方再核。教訓：初稿三項全標「新」，查重後 2/3 係復現 ⟹ **產物聲稱必須即時查重**。
5. **⚠️ 引用值偽影診斷**：O138 F4 之 `min|N(s)−s| = 9.387` 係 float64 + FD(h=1e-7) + λ=406.1 之偽影（本 O 復現 **9.387387**；精確解析 = **0.0231**）。目標聲稱（疊加唔係不動點）**存活**（198/199 內部點 > 0；唯一 0 者恰為極點 1/2，α = 3/8）；但幅度係 O(1e−2)，**單一結果論證之權重應移到動力學路線**（Δt/T_ring = 0.3551）。📌 **已交接 O138 = 2026-09-29T18:17:57 `kind=handed_off`**（`register.py handoff`）。★ **調律者定規（2026-09-29）：跨 O 問題交接只限 register 註冊，禁止在其他 O 寫入任何檔案** ⟹ 原計劃「append 入 O138 之 SESSION_START」**作廢**；事件記在 `register.jsonl`（帶 `target_pid: O138`），查 incoming 用 grep（`log --pid O138` 唔顯示）。
6. **失敗記錄（保留）**：初稿聲稱 `∏ω = 176` ⟹ 腳本首跑 **FAIL**（13.2665）⟹ 修正為 `∏ω = 2√N_d`、`∏γ = 4N_d`。驗證捉到自己作者。

**Bell 專線（本 O 核心，🔴 未開始）**
- **結構論題**：Bell 三前提中，**反事實確定性**在延遲求值語言中**類型級**不成立（未強制之項冇值；「若改量 a′」= 未存在項）。
- **但逃逸要「貴」**：只「讀時抽隨機」= 標準 hidden variable ⟹ 仍然 bound = 2。真正逃逸點 = 相異 setting 之讀取算子**不能共存** ⟹ 正好接上 D2 判準 C1（ℓ_read ≥ 3 之 Aut-破缺讀）⟹ **粒子化機制與 Bell 違反機制係同一個**（候選）。
- **路線** B1 前提判別 / B2 C(θ) 由晶格導出（★ 最硬、零參數；注意 A₅/I_h 之 cos 值集離散）/ B3 CHSH 盲測（2 vs 2√2 vs 第三結構值 = 真預言）/ B4 無信號定理（不得循環）/ B5 與 D5 回滾接。
- **成功／失敗標準**：見 `01_problem_record.md` §8.6。

**下一步（優先序）**
```
1. R1 凍結 D1 延遲項定義 → scripts/02_lazy_semantics.py + docs/02_evaluation_semantics.md
   （★ 檔號已由 R0 用去 docs/01，故凍結文檔 = docs/02）
2. B1 + B4 先行（類型層 + 無信號；成本低、可證偽性高）
3. B2/B3 = 最硬（C(θ) 由晶格導出 + CHSH 盲測）；記住禁後驗揀 setting、禁假設 C = −cos θ
4. ~~待裁定：是否把 H1 append 入 o138 之 SESSION_START~~ → ✅ 已關閉：改以 **register handoff**（2026-09-29T18:17:57, O222→O138）交接；★ 定規：跨 O 只經 register，禁寫其他 O 檔
```

---

## Session 3 記錄（2026-09-29，調律者裁定 (a)(b) → R1 凍結：D1 語義 + C1 本體化）

**狀態**：🟡 **部分推進**（R1 Part A 8/8 ✅ · R1 Part B 18/18 ✅；`O222/Q1`/`Q2`/`Q5`/`B1` = partial；B2–B5 · Q3 · Q4 · C2 仍 open）

**調律者裁定（原文要點，2026-09-29）**
> (a)「**絕對不能允許多值**，必須堅持單一執行 → 確定性 memo（Pure function + memo）」—— 多值 = 代數總帳後門，摧毀可重播性／對賬日誌，係 Bell 底線（B1–B3）之生命線。
> (b)「應果斷放棄純數值 ℓ_read 索引，直接以 **Aut 破缺與穩定子階數** 作為本體定義，讓 ℓ_read 僅作為派生數值表現」——「用 ℓ_read ≤ 2 或 ≥ 3 當硬性門檻，本質上帶有人為參數化痕跡」。

**做咗乜（R1）**

1. **Part A — D1 延遲項語義凍結**（`scripts/02_lazy_semantics.py`，**8/8 PASS**）：
   - `T = (gen, σ, ctx)` 不可變三元組；`force` 純函數 + memo；換 ctx = 另一 thunk；疊加 `Σ c_n|n⟩` 為**派生**表示（回收 `γ_n/90`：`Σc = 1`、`Σc² = 0.033580…`）。
   - **裁定 (a) 之可執行證明**：A1（1000× 同三元組同值、memo 寫入 1）、A4（10 000 次交錯前後向 → 值集/條目 = 44）、A8（人為多值 force → 單一三元組得 5 值 ⟹ A1/A4 必拒）。
   - A6 塌縮：**7 步精確命中**單一結果；尾誤差 `1.32e−3 → 4.02e−10 → 3.71e−23 → 0.0`，`e_{k−1}/e_{k−2}² = 2.294e−4` ⟹ 二次收斂律。
     ⚠️ 首稿誤要求 `|N(s)−s|` 單調（`|f/f′|` 可跳）⟹ 已改測「限步精確 + 二次律」，**FAIL 記錄保留**。
2. **Part B — C1 本體化**（`scripts/03_aut_stabilizer.py`，**18/18 PASS**，全 Q(√5) 精確算術、零浮點）：
   - 群：`2I = <2T, (φ,1,ψ,0)/2>` 閉包 = **120**（全 unit、逆閉）；`I = 2I/{±1}` = **60**（2 對 1）；`I_h = <I,−Id>` = **120**。
   - ★ **晶格原生軸由群自行導出**（不靠外部座標表）：元素階 5 → 6 線（頂點）／階 3 → 10 線（面心）／階 2 → 15 線（邊中點）；定向提升 = 12/20/30。
   - **內在驗證**：定向頂點集（單一 rep 之全群軌道 ⟹ 共享標度）半徑唯一、30 條最小距邊、每頂點度 5、20 個三角面 ⟹ 真二十面體。
   - 軌道-穩定子全檢：頂點 12×5、邊 30×2、面 20×3、**非晶格通用方向 60×1（負對照：平滑讀即刻破 Aut）**。
   - **梯度階梯** min\|Stab_I\|：r0 = 60（res 1）· r1 = **2**（邊軸；res 30）· r2 = **4**（res 15）· r3 = **1**（res 60）⟹ **派生 ℓ_thresh = 3**，**獨立復現 O143/O223 「ℓ ≤ 2 受保護 / ℓ = 3 首破缺」**，而 ℓ 不再是前提。
   - ⚠️ **非單調發現（誠實記錄）**：res = {1, 30, 15, 60} —— rank-1 邊軸讀比**任何** rank-2 二次型更破 Aut。裁判準只需**閾值**（r = 3），首稿標籤誤稱單調已改正。
   - ⚠️ **座標圖約定（誠實記錄）**：導出之 5 重軸線 = `(0,±1,±ψ)` 及循環置換（ψ = 1/φ），即教科書 `(0,±1,±φ)` 二十面體寫在**反射圖**；精確正交映射 `(x,y,z) ↦ (x,z,y)`（det = −1）送到教科書線集。選 `(φ,1,ψ,0)/2` 而非偶置換版本即此約定，對穩定子階梯無影響 ⟹ 已 `handoff` O223。
   - **失敗記錄（保留）**：首稿 `qmul` 標量部符號錯（`a₃b₃` 項）⟹ 閉包爆走（\|G\| → 70942）；修正後精確落 120，另加 CAP 守衛。
3. **未收之聲稱**（排除項）：ℓ′ = 5「唯一通道」**唔係 rank 語句**（需 G-表示／諧波內容）⟹ 不後驗湊出，留 docs/03；「波動／粒子」為候選映射，非導出量子態。

**下一步（優先序）**
```
1. B2：C(θ) 由晶格導出（★ 最硬、零參數；禁假設 −cos θ；先寫盲測協定再跑）
2. B1 收口（反事實對照組判別）+ B4 無信號（不得循環；只許用已凍結 R1 語義）
3. B3 CHSH 盲測 → B5 接 D5 回滾；docs/03 = G-表示（ℓ′ = 5）或明示 no-go
4. Q2 RT1/RT3（唯一性 + 最小性）；Q5 F_proj = 17 身份統一
```

---

## Session 4 記錄（2026-09-29，調律者「合約鐵律」→ B2 Contract v1 凍結 + 可執行強制者）

**狀態**：🟡 **部分推進**（`O222/B2` = partial：**合約前置完成、C(θ) 未出數**；B1/B4 = partial 先決鎖定）

**調律者指令（原文要點）**
> 「在執行任何關於 C(θ) 的晶格導出之前，我們必須把**合約（Contract）寫死在文檔和代碼裏**，把操作空間封死」：
> ① Setting 表與盲測窗的**強制凍結**（θ 掃描範圍、點集劃分、看見數據前絕不准調之超參數）；
> ② **零參數硬約束**：C(θ) 必須純由 2I 群元素在 C₁₇₆ 環／幾何投射上之重疊分佈導出，**嚴禁寫死 −cos θ 或任何三角擬合補丁**；吻合 = 群論／幾何勝利，唔吻合 = 底層拓撲映射要修；
> ③ B1（前提判別）與 B4（無信號／禁循環）**先決鎖定**：反事實確定性之違背必須**純由 Thunk／Lazy 不可逆對賬**造成，而唔係隱含通訊。

**做咗乜（B2 Contract v1，pre-data）**

1. **合約正文** `docs/03_b2_contract.md`：
   - §1 **L-SET**：setting **唔係人選角度**，而係 R1 導出之 **62 條精確晶格原生軸**（12 頂點／20 面心／30 邊中點；Q(√5) 零浮點）；掃描範圍 = **全部 62² = 3844 有序對**（**無選點**）；type-class 逐類全報。
   - §2 **盲測窗（誠實界定）**：DEV = `V×V` 144（唯一可見）／BLIND = 3700（凍結後才揭示）；同 session 無真資訊隔離 ⟹ 靠**三重替代保證**：① `scripts/05` **code-hash 承諾**（跑前寫入 freeze JSON；byte 一改 = 整輪作廢）② **零參數**（無可調參 ⟹ 只有「改定義」，要 version bump）③ **全報告**（3844 對全數入檔，唔准揀）。
   - §2.3 **H1–H12 超參數寫死**（群測度／二值化／平局規則／參考軸／C 定義／QM 比較量／符號約定／CHSH 視窗／兩種 null／LP 可行性／最小 infeasible 子集）—— 改任何一項 = **Contract v2**。
   - §3 **L-ZERO**：`K(g,a) = sign(u_a·(g n̂))`、`C[a][b] = Σ_g w(g)K(g,a)K(g,b)`；**連比較都唔用三角**：`cos²θ(a,b) = (u_a·u_b)²/(|u_a|²|u_b|²) ∈ Q(√5)` 精確。
   - §4／§5 **L-CAUSAL**：B1 之機械內容（因子表局部性／真跑 LP 可行性／歸因 ℓ ≥ 3 sector）；B4 之 marginal 結構推導 + ablation 通訊歸因 + 禁循環輸入。
   - §6 **預先註冊結構預期 P1–P6**（跑之前寫死）：P1 marginal = 1/2 EXACT；P2 coexistence 級 CHSH ≤ 2 EXACT（g = 共享隱變量 ⟹ Bell 定理適用；若 > 2 ⟹ 實作 bug 而唔係物理）；P3 sequential 級**容許** > 2 但**必須歸因 ℓ ≥ 3**（數值刻意留白）；P4 \|C\| vs \|cos θ\| RMS 門檻 1e−9（無容忍擬合）；P5 隨機軸 null（seed 222，10⁴）P6 ablation C ≡ 0。
   - §7 **閘**：`scripts/04` 任何 FAIL ⟹ 禁跑 `scripts/05`；impl hash 遺失或被改 ⟹ 禁揭示 BLIND。
2. **可執行強制者** `scripts/04_b2_contract.py`（**12/12 PASS**，1.0 s）：
   - 群重建與 R1 一致（\|2I\| = 120、\|I\| = 60）；62 軸；3844 對精確 cos²；DEV/BLIND 分割。
   - ★ **P1 結構推導 + 實測**：二十面體**中心對稱**（`v ∈ V ⟹ −v ∈ V`）⟹ 任一方向 6 正/6 負，乘 I-軌道重數 5 ⟹ **30/30**，62/62 軸平衡；換 12 個 vertex 作參考軸同驗。
   - ★ **A1 修正（pre-data）**：平局**唔准當無事** —— edge 軸恰 **⊥ 4 個 vertex 方向** × 重數 5 = **20 平局／軸**（vertex／face 軸 = 0）；用 H3 規則**指派**平局符號後 12 refs × 62 軸 × 60 rotations = **7200 tie events、0 軸不平衡** ⟹ `P = 1/2` **包含平局**仍然 EXACT。（只加檢查，**未改** H1–H12 任何值）
   - **AST 封鎖自測**：`def kernel: return -math.cos(a-g)` 被拒 ✓；魔數 `0.7071067811865476` 被拒 ✓；`0.5` 浮點被拒 ✓；乾淨精確 kernel 通過 ✓。**局部性自測**：`k_table(setting, gen, remote_setting)` leak 被拒 ✓；因子表組裝 `C = Σ w·K[a]·K[b]` 通過 ✓。
   - 凍結附證 `data/04_b2_freeze.json`：doc `01d2fb03ead127ef…`／enforcer `830dbf755605c1a4…`／settings `2357006c68e0165d…`／partition `499b3d16b084b780…`；**GATE = CLOSED（05 not frozen）**。
3. **未越界**：C(θ) **一個數都未計**（合約鐵律：設定表／判決規則先於數據）；register 4 × note；跨 O 零寫入。

**下一步（閘內，次序唔可跳）**
```
1. 寫 scripts/05_b2_correlation.py（§3 定義；kernel 表 → C 表 → CHSH 全 tuple → H6 精確平方比較）
2. 跑 scripts/04 --freeze-impl scripts/05_b2_correlation.py → 記 impl hash（此刻起 05 任何 byte 改動 = 整輪作廢）
3. 出數（DEV 打印；BLIND 寫檔唔打印）→ 4. 揭示 BLIND → 全 3844 對報告 + P1–P6 逐項核
5. B1 收口（LP 最小 infeasible 子集）· B4 ablation · B3 CHSH 判別 → B5 接 D5 回滾
```

---

## Session 5（2026-09-29）— B2 共存層出數 + 獨立 GPU 精確整數核對

**交付**
1. **`scripts/05_b2_correlation.py`**（凍結 impl sha256 `be946911c087862d7bd02b460235b0b47fe1ff4ed85d2a855b6855f717e49235`）：2I 群 × 62 條晶格原生軸；`K(g,a) = sign(u_a·(g n̂))`、`C[a][b] = Σ_g w(g)K(g,a)K(g,b)`。快速路徑用結構恆等式（2I 軌道 = 12 頂點 × 重數 10；I60 × 5），但仍以直接 120 元素 loop 雙路徑核對（P0c 0 不符）。**凍結輪 18/18 PASS**；**reveal 輪 19/19 PASS**（`logs/05_b2_correlation.out`、`logs/05_b2_correlation_reveal.out`）。
2. **`docs/04_b2_results.md`**（183 行）＝結果 + 合約修訂 A1–A4 + 方法論 bug 記錄；**`docs/03` 凍結原文未動一個 byte**。
3. **`scripts/06_b2_gpu_verify.py`**：**獨立**核對（唔同實作 + 唔同硬件 + 純 int64 `(P,Q)` 表示 + `A² vs 5B²` 判號）→ **4/4 PASS**（`logs/06_b2_gpu_verify.out`）；GPU 自行重算 2I 軌道重數而非假設。

**核心結果（負面，誠實）**
- `C` 只取 7 值 `{0, ±1/3, ±2/3, ±1}`；**`C ≠ −cos θ`**（精確 `C²` vs `cos²θ`：DEV 24/144、全 634/3844、`max|Δ| = 8/9`；吻合全屬平凡情形）。
- CHSH 全 62⁴ `max|S| = 2`（= 古典上界）；raw 2 經**對蹠軸／重複分區**（平凡）→ 新增 **antipodal-free** 統計量：12 頂點 **4/3** 低於隨機 unit-quaternion null 中位數 **22/15** ⟹ **共存層無量子超額**。
- ⟹ QM 語義若存在，必須在 **rollback／sequential** 層；該層**定義未寫**（A2）⟹ P3 = `NOT COMPUTED`。

**合約紀律實錄**
- 凍結輪 R1→R11（每次改 05 即重凍並記 hash；全部發生在該輪出數之前或同時，且從未改動 H8 預註冊窗）。
- `scripts/04` 驗證**必須**帶 `--freeze-impl`；純跑（無旗標）會報 1 FAIL（`[contract] unfrozen implementation present`）並重寫 `frozen_at`（impl hash／gate 不變）⟹ 唔可以當驗證。
- 最後確認：`frozen_at = 2026-09-29T21:01:03+08:00`，impl hash 與 `scripts/05` 現行 sha256 **MATCH = True**，GATE = OPEN。

**下一步（A2 → B3/B4/B5）**
```
A2: rollback/sequential 層 C(θ) 之定義 + 預註冊窗（新 doc + 新 hash；必須見數前凍結）
B4: no-signalling 之結構推導（二十面體中心對稱 ⟹ 任一方向 6 正/6 負 × I-軌道重數 5 = 30/30）
B3: CHSH 盲測；B5: 接 D5 回滾
```
**register**：`note` ×3（`O222/B2`、`O222` ×2）+ `mirror`；`check`：REF-MISSING 3（O220 舊帳 1 + O221 並行帳 2）、STATUS-DRIFT 0。

**收尾事故與防禦（2026-09-29 21:0x–22:0x）**：6 個早前 session 遺留背景行程逐個被收掉，命令全部重定向到同一批 log 路徑。逐次即時核對 = 零損傷（寫入全在 R11 輪之前）。已落位：`logs/frozen/` + `data/frozen/` 不可變版本化副本（11 件）+ `data/frozen/MANIFEST.json`（12 件，機器可讀）+ `scripts/07_artifact_integrity.py`（核對／`--restore` 逐 byte 還原，先驗副本 hash）。另由凍結 JSON 以 `Fraction` 獨立重算標題數字：`C²` 值集 `{0,1/9,4/9,1}`（重數 960/1660/960/264）、**精確命中 634**（DEV 24 + BLIND 610）、`max|C²−cos²| = 8/9`，並得**更硬**事實：**1920/3844 對 `cos²θ` 無理 ⟹ `C²` 算術上不可能吻合**。

## Session 6（2026-09-29）— **A2 sequential / rollback 層出數（權威值 = 全 62⁴ 枚舉）**

**調律者指令**：「讓代數真正『動起來』——引入狀態機動態演化（Sequential Execution）：ctx 唔再係死座標，
而是在 thunk 觸發時做 dynamic rollback 與 history reconciliation；用計算取代靜態幾何」；
後續硬指令：「**這種重要的計算全部要全量無優化/無簡化下計算才有價值**」。

**合約** `docs/05_a2_contract.md`（A2 v1 + **A1–A9 amendments**，全部見數前或附**時序披露**）；
**強制者** `scripts/08_a2_contract.py` → **17/17 PASS，GATE = OPEN**（C16 AST 閘、C16b 讀算子局部性 `read(G, ctx)`）；
**凍結實作** `scripts/09_a2_rollback.py` sha256 = **`d8037bb16f690a2935c7028b3680d48df6540e01c938ade1d3b5858aed594ace`**；
**權威全量枚舉** `scripts/10_a2_bruteforce.py`；**結果** `docs/06_a2_results.md`。

### 機器（凍結）
`read(G, ctx) = sign(u_ctx·(G n̂))`（逐字複用 B2 之 H2/H3 含平局規則）＋ **memo 命中律**（live ctx 相同 ⟹
回 memo 值、**唔重複寫入**，R1 D1-b）⟹ Push `(ctx, v, G)`、`G ← G·h(ctx)`；`rollback()` pop + 還原世界態；
`reconcile(ctx) = rollback(); read(ctx)`。`h(ctx)` 由結構唯一指派（階最小 + 正對齊 + 字典序）；62/62 **雙射**。

### 兩個估量器（皆精確 120 態）
- **E1（共同 λ 對照）**：每對獨立、**空 ledger** ⟹ 閉式 `C1[a][b] = (1/120)Σ_s K[s][a]·K[MUL[s][h(a)]][b]`（a ≠ b）；
  `a = b` ⟹ memo 命中 ⟹ `C1 = +1` EXACT。
- **E2（史機器）**：單條世界線家族、**persistent ledger**、凍結枚舉次序 ⟹ 精確 DP 推進 `p_k`。

### 結果（**全 62⁴ 枚舉**，零剪枝；計數已證 `raw` = 14,776,336 = 62⁴ EXACT）

| 變體 | E1 | E2 |
|---|---|---|
| `raw` | 4（對角 artifact）| 4（對角 artifact）|
| `distinct`（a≠a′, b≠b′）| 4（同上）| 4（同上）|
| `distinct + 反對蹠` | 4 | 4 |
| **`all4`（四 setting 兩兩相異）** | **2 EXACT** | **3 > 2** |

- **對角 artifact**：`raw`/`distinct` 之 argmax 有 `b′ = a′`，令**對角 `C[a][a] = +1`**（memo 命中律之直接後果）
  入和 ⟹ 唔係物理超額；`raw` 之 null 亦恆飽和 4（零判別力）⟹ **明文全報、以 `all4` 為 v2 判準**（A6）。
- **★ 關鍵判別（負面結果）**：E2 之 3 在**隨機軸 null**（12 draws，每 draw 全枚舉 + 精確 DP）下分佈
  `{7/3: 1, 8/3: 6, 3: 5}`（median **8/3**、max **3**）⟹ **5/12 draws 同達 3.0 ⟹ p ≈ 0.42 ⟹ 無顯著性**
  ⟹ 🔴 **超額係機器語義之通用性質，唔係晶格幾何之性質**。對照 E1 `all4` 之 null **20 draws 全 = 2.000**。
- **零信號**（marginal 62/62、E2 條件 marginal 3844/3844 全 = 1/2 EXACT）· **零通訊**（ablation ≡ 0）·
  `p_k ≡ 均勻`（max L1 dev = 0）＋逐對映射**全部雙射**· `Δ_order = 160/120 > 0`。
- **前瞻註冊 P7 之機制假設（超額必歸因 ℓ ≥ 3 sector）被否證**：argmax = `E27,E28,V01,E29`（edge/vertex）。
- **可宣稱上限**：**「history-mediated contextuality（史誘發語境性），軸無關」**；**唔可以**講量子非局域、
  唔可以講「晶格導出 CHSH 違反」。

### 工具教訓（本輪捉到）
① `chsh_max` 曾係 O(62⁴) 有理數掃描（400+ 次呼叫 ⟹ 數小時）⟹ 改同分母整數 + top/bottom-3（精確等價，
**值逐個相同**）；② **AST 閘真係捉到我**（`R_PASSES ** 0.5` 浮點）⟹ 改精確有理比較 `rms² < 4/R`；
③ MC 判準原寫錯（在 3844 對上取 max）。**全量無優化**為調律者硬指令後，另寫 `scripts/10` 全枚舉為權威值。

## Session 7（2026-09-29）— **B5：D5 回滾層之資源界限（合約 `docs/07` + 結果 `docs/08`）**

**調律者指令**：「繼續」⟹ 接 A2 之下一步 = B5（D5 回滾 + O41 預算），照鐵律：**先讀既有定義 → register → 合約先於數字 → 全量枚舉**。

**輸入（全部凍結，零新語義）**：`61.5 = 123/2`（O41）· `E_min = 123/176`（O41）· `ΔE_read = B(n) = 123/88`（O41 + O206 `ω_n = μ²`）· 讀率 44 reads/tick（O126：讀 = 寫 = N_d）· R1 讀算子 + memo 單值律 · A2 之 62 軸 + h 表。

### ★ 結果（`docs/08`，8/8 PASS，全量枚舉）
1. **資源身份（修正後）**：讀成本 = `123/88 = 2·E_min` ⟹ 每 pass 可行讀數 = **44 = N_d EXACT**；**一次耗盡預算之 pass = 44 讀 = 1 tick**；**`τ_deco` = 2 ticks = 2 個 pass**（原「身份待證」⟹ **結構推導完成**，但內容非原猜測）。A2 之 7688 讀超支 **1922/11 ≈ 174.7 倍** ⟹ **不可行**。
2. **預算可行 pass = 凍結次序前綴 15 對**（43 讀；misses/pair ∈ {2,3}；第 16 對被 **per-read** 終止條件擋住）。
3. **★ 預算可行 CHSH ≡ 0**（四統計量全 0；隨機軸 null 亦 median = max = 0）。**結構原因**：字典序位置 = `62a + b` ⟹ 前 15 對只有 `a = 0` ⟹ 冇任何 `a ≠ a′` 之 4-tuple ⟹ **Bell 統計量無法構成**（唔係值變細）。
4. **無限制值重現 A2**（E1/E2 `all4` = 2/3；`distinct` = 4/4；全枚舉 14,303,524 / 12,517,800 tuple）✓
5. 保持項：`p_k ≡ 均勻`（L1 dev = 0）＋逐對雙射；`Δ_order` 前綴 = 2/5 > 0。

### 誠實記錄（我兩個錯，全部照報 + 保留 log）
- **因子 2 錯誤**：原用 `E_min`（**下限**）當讀成本 ⟹ 得 88 讀 ✗；正確 = `B(n) = 2·E_min` ⟹ **44 讀**。**我嘅閘（P1/P4）捉到**，首跑 log 保留於 `logs/12_b5_budget_firstrun_FAILS.out`，合約 A4 修正。
- **終止條件**：原只在每對前檢查 ⟹ 首跑 16 對超支（剩 −123/44）⟹ 改 **per-read**（A5）。
- **標籤**：sweep 內標為 `raw` 者實為 **`distinct`**（訪問數 62²·61² 為證）⟹ 改名重凍（A6，值不變）。
- 閘本身亦被我修嚴：出處檢查須遞歸掃 `.txt`（O126 之 tick 在 `data/*.txt`）；AST 亦禁**變數名** `pi`/`log`（兩次真被捉）。

### 未閉合
**G1**：D5 觸發所需之 **ctx → s 映射唔存在於凍結記錄** ⟹ 本輪只做資源半邊；候選路線（讀成本歷階需 O206 之 f(n) 🔴／O210 投影／memo 一致性——已證此路線觸發為空）。合約 §6 明文**禁止自創映射**。
**G2**：逐模頻率 `f(n)` 仍 🔴（O206）⟹ 本輪讀成本均勻；f(n) 導出後需重算。


## Session 8（2026-09-29 深夜）— **階段性 Closeout（審計，零新推導）**

**指令**：確認整條 session 鏈內容已入文檔／劇本並驗證後才繼續。

- **驗證對象** = 本對話框（thread 93184）**8 條 session 壓縮鏈**（`state.db` 唯讀；`session_key` + `parent_session_id`）—— 唔可以用單一 id（本輪對話期間 id 已換 8 次）。
- **產物**：`scripts/13_closeout_audit.py`（**獨立審計器**：唔 import 09／10／11／12）、`data/13_closeout_audit.json`、`logs/13_closeout_audit.out`、`docs/09_closeout_audit.md`。
- **結果**：**57/57 PASS**。A2／B5／B2 全部 headline 值由**第三條獨立算法**重現（A2 CHSH 8/8 值＋argmax 逐字相同）；B2 `cos²` 由原始軸向量重算 3844/3844；覆蓋率雙向 0 缺失。
- **★ 捉到記載錯誤 G3**：`docs/06 §5.1`／`docs/05 A8` 之 A2 域計數（13,711,284／12,838,884）**無法重現**，正確 = 13,388,280／12,517,800（B5 之 12,517,800 正確）；**不影響任何結果值**；已 append 日期修正附註（原文保留）。
- **自我披露**：我嘅審計器第一版亦有 3 個錯（stale-index 計數、E2 誤用 `C1rev`、核對器排序期望錯）—— **全部由閘／自檢捉到**，已入 skill 教訓。
- **未閉合**：G1（ctx→s 映射唔存在於凍結記錄）／G2（O206 `f(n)` 🔴）—— 均需上游或新輪處理；G3 已判定。
- **下一階段建議**：**B3 第二輪** —— 在資源界限**內**重新定義可測量統計量（Bell 型已被證**無法構成**）；或 **D6 對映表**（thunk ↔ 態，同時係解 G1 入口）。


## Session 9（2026-09-29 深夜→凌晨）— **B3 第二輪（B3R2）：資源界限內之公平讀取分配**

**指令**：繼續推（closeout 後）。**先 register（見數前）**：`O222/B3R2` + 4 子問題 note；**合約先於任何數字**（`docs/10`）。

- **合約**：`docs/10_b3r2_contract.md`（`b3r2-contract-v1`；§2 見數前寫死 **5 條 order**；§3 權威值須**全量枚舉**；§4 四檢查；§5 閘；§6 禁區）。
- **強制者**：`scripts/14` — **13/13 PASS**（order 雙射檢查、AST 閘、出處、register 前置）。
- **機器**：`scripts/15_b3r2_orderfair.py`（凍結 impl `14e17e7c…`（最終；中間輪 `a4f3c1da` 已作廢））— **14/14 PASS**。
- **★ 結構發現 1（可構成性判據）**：合法 4-tuple 存在 ⟺ 前綴 pair 集含 **2×2 矩形**；**覆蓋度（`cov_a`/`cov_b`）唔足夠**。**雙射前綴**（`a ↦ b`）**結構上**不可構成 —— `diag`／`antidiag`／`stride` 皆 `cov = 15~22` 但**零** 4-tuple。合約原寫之等價陳述為**假** ⟹ **amendment A1**（判據改為直接計算；覆蓋度降為診斷），**重凍** impl，**首跑 log 保留**。
- **★ 結構發現 2（前綴長度係拓樸量）**：`diag` 可擠入 **22 對**（每對 2 讀，因相鄰 pair 共用 ledger 頂 ⟹ memo 命中）而 `block` **18 對 / 42 讀**；`lex` 只有 15 對 / 43 讀 ⟹ **讀取次序改變預算之有效容量**（15 → 22 對，+47%）。
- **★ 結果**：唯一可構成 order = `block`。預算可行：**乾淨 `all4` = 16/15 (E1)、13/15 (E2)** ⟹ **兩者 < 2 ⟹ 冇 Bell 違反**；表觀超 2 者（`distinct`／`distinct_anti` = **32/15 (E1)**、**11/5 (E2)**）之 argmax **全部帶對角污染**（`i = a`、`j = a′` ⟹ `C[a][a] = +1` 入和），且 **null 中位數 38/15 = 2.53 本身 > 2**、null 最大 10/3 ⟹ **p ≈ 0.96–0.97 ⟹ 零顯著性**。
- **★ 第三度確認 G3 修正值**：全 62⁴ 全掃重新導出 `distinct_anti` **13,388,280**、`all4` **12,517,800**（另 raw 14,776,336、distinct 14,303,524）✓（closeout 之修正獲第三條路徑支持）。
- **四檢查**：marginal **62/62 balanced = 1/2 EXACT**（no-signalling）／ablation = 0／`Δ_order` = 160/120／歸因（超 2 全歸對角）。
- **獨立審計**：`scripts/16_b3r2_audit.py` — **15/15 PASS**（唔 import 15；**獨立重寫** pair 協定重算五個前綴逐欄相同；CHSH 改用**矩形分解**重算 40 條值，值＋域大小全同）。
- **自我披露（照報）**：首跑 4/5；① 合約缺陷（上文 A1）；② **我寫死之斷言 A3「全部受限 class ≤ 2」被機器否證**（`11/5 > 2`）⟹ **冇改判準救結果**，而係拆成兩條可證偽聲明（A3 乾淨 `all4` ≤ 2；A4 超 2 必屬「對角污染 或 null 不顯著」）＋加逐 class null；③ 我讀錯 `ablation_abs_sum`（誤讀 `chsh` 子典得 `None`）→ 修正。
- **判定**：可量度扇區（44 讀、公平分配）**LHV-class** —— 與 B2／A2／B5 **四路一致**；**唔推翻 B5** 而係**收窄**：「唔係無法構成，而係構成得到但量到零」。
- **未閉合**：G1（D5 `ctx→s`）／G2（O206 `f(n)`）／**G4 公平分配之唯一性**（由 `h` 表／2I 群結構導出？本輪五條係人為家族）／**G5 矩形判據之充要刻畫**。
- **下一階段建議**：**D6 對映表**（thunk ↔ 態；兼 G1 入口）或 **G4 唯一 order**。
---

## Session 10（2026-09-30）— D6 對映表操作化

- **合約**：`docs/12_d6_contract.md`（`d6-contract-v1`）— 凍結物件 𝒜（62 軸，`data/04_b2_settings.json`）／G（2I，`scripts/09` `build_group`）／h（`data/08_a2_h_table.json`）／K（`K[s][a] = sgn(q_s · n̂_a)` ＋ tie 規則）／𝒯（O210，**唯讀**）。謂詞族 P1–P4（13 格）。
- **強制者**：`scripts/17_d6_contract.py` — **12/12 PASS**（群／軸逐字重建、13 格合約↔impl 對齊、AST 閘、K 表 ledger 規則靜態核對、O210 provenance ＋ G6 見證、register 前置、B3R2 引用值核對、FAIL ⟹ `GATE = CLOSED`）。`GATE = OPEN`，impl 凍結 `a681ae8c…`。
- **機器**：`scripts/18_d6_mapping.py` — **13 格 = 9 ✅ / 1 🟡 / 3 🔴**。
- **★ 發現 1（62 = 31 線雙覆蓋）**：62 個軸標籤兩兩成對蹠對（31 對，每軸恰一對蹠）；2I **型別**軌道仍 {12, 20, 30}（vertex／face／edge，型別不變，120/120 群元素為置換）⟹ 型別按**線**分族、方向係雙覆蓋。
- **★ 發現 2（tie 條目 16.13 ％）**：dot = 0 時凍結建構取「旋轉後參考 r 之**首個非零分量**符號」。`scripts/19` A2b **由幾何 ＋ 該規則完全重建 K（0/7440 mismatch，tie = 1200/7440）** ⟹ K **唔係**純幾何符號函數。
- **★ 發現 3（非因式化 ≠ 非局部）**：rank C1 = **61**、C2 = **62**、C1rev = **61**（Bareiss 覆核一致）⟹ 強非因式化；同輪 CHSH 預算內乾淨 `all4` = **16/15 (E1)**、**13/15 (E2)** < 2 ⟹ 兩者**獨立**。
- **★ 記錄側**：append-only（pushes = reads = 85，14 命中零寫入）／記錄**支配**當前態（2 例：存 1 vs 當前 −1）／可及深度 = 1（**單副本，無環境冗餘** ⟹ G8）／每對 ledger 淨增 ≥ 1（rollback 還原態唔還原記錄）。
- **★ 概率側**：表值係帶號相關（C1／C2 值集 15 個；行和 ≠ 1）⟹ **無非負歸一權重** ⟹ 無 Born 結構（G7）。no-signalling 由 62/62 軸 ±1 平衡直接成立（邊際恰 1/2）。
- **獨立審計**：`scripts/19_d6_audit.py` — **10/10 PASS**（唔 import 18；A2b 完全重建 K、A4 閉式命中律 33/33、A5 淨增 ≥ 1、A6 62/62、A7 引用逐字相同）。
- **自我披露**：機器首跑兩處過嚴（P1a 加條件 ⟹ 誤 🟡；P4c 用錯判據 ⟹ 誤 🔴）⟹ 修 impl ＋重凍（`9d9fff37…` → `a681ae8c…`）＋首跑 log 保留；審計首跑兩錯（核關係漏右乘、trail 無 `top`）＋ `sign5` 同號 bug；閘自身**兩缺陷**（C6 切片漏 `pop`；有 FAIL 仍寫 OPEN）。（另：`final_result.md` 仍載 B3R2 中間輪 hash `a4f3c1da…` ⟹ 本輪一併更正為 `14e17e7c…`。）
- **未閉合**：G1（D5 `ctx→s` 唔存在於凍結記錄）／G2（O206 `f(n)` 🔴）／G4（公平分配唯一性）／G5（矩形判據充要）／**G7（Born 🔴）**／**G8（記錄冗餘 🔴）**／C2／`F_proj = 17`。
- **下一階段建議**：**G4**（由 `h` 表／2I 群結構導出唯一 order）或 **C2 + G7**（memo 命中表 ↔ 概率結構之關係），或 **F_proj = 17 = dim ker T_pipe** 身份統一。


## Session 11 — G4 讀取次序之結構導出與唯一性（2026-09-30）

- **合約**：`docs/14_g4_contract.md`（`g4-contract-v1`）：邊集 = 無 loop 有序對（3782）、tie-break = 最小 index、起邊 `(V00,V01)`、公平度／統計量定義寫死；**禁**見數後改邊集／tie-break／判據。
- **強制者**：`scripts/20_g4_contract.py` — **12/12 PASS**，`GATE = OPEN`，impl 凍結 `efa6aaded922…`（`data/20_g4_freeze.json`）。上游 hash 由 freeze 記錄讀取（B5 `f2cb54fa…`／B3R2 `14e17e7c…`／D6 `a681ae8c…`）；AST 閘；**只准 import** 凍結機器（禁本地 `run_pair`／`simulate`／`feasible_chsh`…）。
- **機器**：`scripts/21_g4_eulerian.py` — **6 格全 ✅**。P1 成本律 **242,172/242,172**（0 例外；62 退化 `t=a=b`）；P2 Eulerian 3782/3782；P3 `min` 無 loop = 2／電路總 7565／實測前綴 **21 對/43 讀**／`n=3` 720 排列 18 minimiser 全 Eulerian；P4 `EC(62)` = `62^60(60!)^62`（**5187 位**）＋ `n=3,4` 暴力驗 BEST（3/256、序列 6/768）；P5 canonical 不可構成／類內存在含矩形電路 `all4` = **13/15**；P6 canonical **max|out−in| = 1**（`lex` 14）。
- **★ 結構發現**：① 最優 ⟺ Eulerian（成本律 ⟹ 唯一省讀途徑 = 首讀命中 ⟹ `t = a`）；結構逼出**類**非次序（`EC(62) ≈ 10^5187`）。② 無 loop 21 對係**預算上限**（45 讀 `5535/88 = 62.897 > 61.5`；43 讀 `5289/88 = 60.102 ≤ 61.5`）；`diag` 22 對全屬對角（loop）。③ 最優性 ⊥ 可量測性**類內可並存**（上限同 21 對）；22 對必然含 loop ⟹ 結構上不可能「22 對＋可構成」。
- **獨立審計**：`scripts/22_g4_audit.py` — **9/9 PASS**（唔 import 21）：自寫 ledger 模擬器全表重算 ＋ 跨步 `mod 977` 推過凍結機器 247/247（驗模擬器本身）；自寫 Hierholzer ＋ 首 12 邊逐字相同；**reduced Laplacian 精確行列式**驗 BEST（`n = 3,4,62`，`det(62)` 108 位）；自寫 `anti` ＋ 全 4-tuple 枚舉得 **13/15**、argmax 一致。
- **自我披露**：int→str 上限／BEST 約定／見數後改 impl ⟹ 重凍 ＋ amendment **A1**（impl-only，值不變）／審計 A7 比較錯（已改自寫枚舉）。首跑 log 2 份保留；舊 freeze 存 `data/20_g4_freeze_pre_amendment_a1.json`。
- **未閉合**：G4 類內代表選擇原則（約定）／G5／G1／G2／G7／G8／C2／`F_proj = 17`。
- **下一階段建議**：**G5**（矩形判據充要刻畫：本輪得「trail ⟹ 稀疏」，可與 B3R2 之「雙射 ⟹ 無矩形」合併成充要條件）或 **C2 + G7**（memo 命中表 ↔ 概率結構）或 `F_proj = 17 = dim ker T_pipe` 身份統一。


## Session 12 — G5 矩形判據之充要刻畫（2026-09-30）

- **合約**：`docs/16_g5_contract.md`（`g5-contract-v1`）：判準 `c(a,a2) >= 2`（凍結 ASCII 形式）、`L = min(21, |E|)`、小 n 退化用 `L_small`（n=4→5、n=5→9）、LCG（a=1103515245, c=12345, m=2³¹, seed=20260930, K=1000）、fallback 上限（600 s／30000000 節點）、P3 搜索前 2000 候選、class = 首邊 (0,1)。
- **強制者**：`scripts/23_g5_contract.py` — **12/12 PASS**，`GATE = OPEN`，impl 凍結 `fb9072e4…`（`data/23_g5_freeze.json`）。C2 連 **anti 結構引理**（62 個 True = 31 對、每行恰 1）一併重建；AST 閘**禁 `random`**（抽樣必須手寫 LCG）；九條文件↔實裝字串對齊。
- **機器**：`scripts/24_g5_criterion.py` — **5 ✅ / 1 🟡**。P1 充要判準 **6892/6892 零反例**；P2 必要階梯（injective 627 個全不可構成，B3R2 成推論）；P3 `k ≥ 6 ⟹ 可構成`（正例 6..20）＋界 `k − c ≤ 4` 之**緊例**；P4 `rz(3,4,5) = 6,9,12`、KST `527 ≫ 21`；P5 `euler_canonical` `Σk = 45`、raw 矩形 0（列稀疏）；P6 n=4 **0/256**、n=5 **184704/972000**（皆精確）、n=62 **1/1000**（抽樣）。
- **★ 結構發現**：① 判據可計算化（充要、窮盡驗）；② `k ≥ 6` 與 `k − c ≤ 4` 兩界**皆緊**；③ canonical 不可構成 = **trail 列稀疏**（並非 anti），且類內可構成**罕見** ⟹ 典型而非異常；稀疏**唔強制**（rz(5) = 12、上界 527）。
- **獨立審計**：`scripts/25_g5_audit.py` — **8/8 PASS**（唔 import 24）：自寫 4-tuple 搜索對 6,892 個案零反例；自寫 anti；rz **列主序**＋2¹⁶ 暴力；n=4/n=5 類**重新全枚舉**（256／972,000）並以 **reduced Laplacian 行列式 × BEST** 獨立驗大小、可構成 0／184,704 逐項吻合；均勻隨機交叉核。
- **自我披露**：P3 首跑 🟡（impl 欠測）⟹ 補正例＋重凍＋首跑 log 保留；審計 A2 首跑 FAIL（審計碼比較範圍錯）⟹ 同對象重比；★ **程序過失**：重凍前未 copy 舊 freeze ⟹ `H1` 不可回收（已記 §7 ＋ 寫入 skill）。
- **未閉合**：`rz(n)` 一般閉式 · n ≥ 6 類比例（≈ 10^11 電路）· G4 代表選擇原則 · G1 · G2 · G7 · G8 · C2 · `F_proj = 17`。
- **下一階段建議**：**C2 + G7**（memo 命中表 ↔ 概率結構，兩個 🔴 同源）或 `F_proj = 17 = dim ker T_pipe` 身份統一；或 `rz(n)` 之閉式（含 KST 之構造性方向）。


## Session 13 — C2 + G7 測度 ↔ 概率結構（2026-09-30）

- **合約** `docs/18_c2g7_contract.md`（`c2g7-contract-v1`）：凍結 I1–I5（`scripts/09` `d8037bb1…`、`data/09` 相關表、`scripts/12` `f2cb54fa…`、`scripts/15` `14e17e7c…`、D6 P4c 引）；七格 C1–C7；四元組選取規則（`D_all4`、`M <= 2` 則用 all4 argmax，否則用 `|S| <= 2` 子域 argmax）；精確可行性判定 = 頂點枚舉（9 等式 + 7 變量置零，Bareiss 整數消元）；`D_common = 15`；節點上限 `30000000`；時間上限 600 s。
- **強制者**：`scripts/26_c2g7_contract.py` — **15/15 PASS**，`GATE = OPEN`，impl 凍結 `d8d7443603de…`；含上游三 hash pin 與 G5 GATE 檢查；**AST 禁浮點字面值**（本輪即捉到 `log2(120)`）；9 條 doc↔impl ASCII 對齊（`p_k = uniform`、`sum_s K[s][a] = 0`、`|S| <= 2`、`vertex enumeration`、`sign_rank > 1`、`diag(K`、`sqrt(p)sqrt(p)^T`、`30000000`、`c2g7-contract-v1`）。
- **機器**：`scripts/27_c2g7_measure.py` — **5 ✅ / 1 🟡 / 1 🔴**（C1–C4、C6 ✅；C5 🔴；C7 🟡）。
- **獨立審計**：`scripts/28_c2g7_audit.py` — **12/12 PASS**（A0–A8）：群公理路線（400 抽樣映射全雙射）、自算 60 對期望值對凍結 C2 **0 mismatch**、witness 逐項重算、模秩雙向夾住 `rank = 6`、反序 fooling set ≥ 6、換位子群 120/120、飽和機制定位。
- **★ 主結論**：Born 型測度**存在且強制**（態層 uniform、結果層 1/2、四元組顯式 witness）⟹ G7 缺口重新定位為 **amplitude／複相位 + 非交換觀察量**之缺席；並新增 **C2 表 `|S| = 3`（無 joint measure、成因 = memo 飽和而非對蹠）** 之 finding。
- **自我披露**：LP 邊際方程編碼錯（首跑 C3 🟡）、審計 A4 預期錯（實測對蹠 = 0 ⟹ 反而成為 finding）、A5 Fraction 爆位、閘即時拒收浮點字面值。
- **未閉合**：`sign_rank(K)` 精確值 · 窗內 `|S| <= 2` 定量版本 · amplitude/Hilbert 構造 · G4 代表選擇原則 · G1 · G2 · G8 · C2 閉式 · `F_proj = 17`。
- **下一階段建議**：**G1**（`ctx→s` 對映是否存在於凍結記錄）／**G8**（記錄冗餘 = 1）／或由 G4+G5+C2G7 合流成 **O222 階段性 closeout（第三輪）**，再向 G2（O206 `f(n)`）與 `F_proj = 17` 推進。

## Session 14 — G1 + G8 缺口可否由凍結記錄推導（2026-09-30）

- **合約** `docs/20_g1g8_contract.md`（`g1g8-contract-v1`）：凍結 I1–I6（`scripts/09`、`scripts/12`、凍結次序、`docs/13` P3b／P3c 引、`docs/07 §6` 之「禁自創」條款、O210 唯讀 provenance）；六格 G1a–G8c；**A1** 加入 **I7 = `scripts/18_d6_mapping.py`（`a681ae8c…`）** 為 ledger 之權威來源；精確算術（Q(√5) 平方範數）；節點上限 `30000000`、時間上限 600 s。
- **強制者** `scripts/29_g1g8_contract.py` **16/16 PASS**（`GATE = OPEN`，impl 凍結 `840d0d4ed792…`）：三 upstream hash pin（09／12／18）＋ C2G7 GATE ＋ AST（禁重庫／禁浮點字面值／禁變數名 `pi/log/cos…`）＋ 6 條 doc↔impl ASCII 對齊（`s_coord(ctx) = idx[h(ctx)]`、`|N(s) - s|^2 > 0`、`value-level consistency`、`ledger entries per ctx`、`R_consistent = 1`、`R >= 2`）＋ C6／C7（只准申報之重播，且必須逐對與 I7 全量比對）。
- **機器** `scripts/30_g1g8_gaps.py` **6 格 = 4 ✅ / 1 🟡 / 1 🔴**；**獨立審計** `scripts/31_g1g8_audit.py` **12/12 PASS**（唔 import 29／30；執行期載入集 = {09, 12, 18}）。
- **★ 主結論**：`ctx → s` **可由凍結寫入規則逐字讀出**（62/62、單射、7440/7440 零不符）⟹ 缺口**唔在映射而在層次**；D5 觸發之平方範數 ∈ `{2, 3, 5/2 + √5/2}` 且**只依 ctx** ⟹ 字面回滾規則**空轉**、須改讀值層；**D5 鎖距 = 2I orbit 不變量**（12／20／30 ＝三軌道，審計獨立驗證）；**G8** ledger `7564 = 62×122` 全均勻但 `R_consistent = 1`，多重性（K 行 10 重簡併、orbit）**全不可觀測** ⟹ **`R ≥ 2` 失敗**（D6 P3c 🔴 維持、成因精確化）。
- **自我披露**：① 首跑全 FAIL（把 `run_pair` 之一元頂標記誤認 ledger）⟹ 保留首跑 log＋舊 freeze＋**amendment A1**；② G1c override 首版只數尾讀命中（0 vs D6 之 2）⟹ 改為兩路徑都數（全 pass 65）＋更正文字。首跑 log：`logs/30_g1g8_firstrun_runpair_ledger_wrong.out`、`logs/30_g1g8_firstrun_g1c_override_undercount.out`、`logs/30_g1g8_second_pass_text_wrong.out`。
- **★ 文檔欠賬（本輪發現）**：上一輪（C2 + G7）**`final_result.md` 漏咗 C2G7 段** ⟹ 本輪以「**補記**」形式補回並明文標註（不回溯改寫舊段），並在第三輪 closeout 之「活文檔完整性」檢查中列為 finding。
- **未閉合**：G1 之語義修訂未形式化 · G8 之冗餘構造 · `sign_rank(K)` · 窗內 `|S| <= 2` 定量版 · amplitude／Hilbert 構造 · G2 · G4 代表選擇原則 · C2 閉式 · `F_proj = 17`。

## Session 15 — 第三輪階段性 Closeout（2026-09-30）

- **審計器** `scripts/32_closeout3_audit.py` **15/15 PASS**（唔 import 任何輪次機器；只由凍結接口 09／12 重算）。**結果** `docs/22_closeout3_audit.md`。
- **覆蓋**：全鏈 **11 輪**（R0 → B2 → A2 → B5 → closeout1 → B3R2 → D6 → G4 → G5 → C2G7 → G1G8）；MANIFEST **163 件**（**drift 0／missing 0**）；5 份 freeze 記錄與磁碟 impl hash **全一致**（無見數後改動）；四份活文檔對 11 輪**全數有記錄**；register 硬漂移 = **基線 8**（`{DUPLICATE-DIR 4, REF-MISSING 3, README-ONLY 1}`，**皆非 O222**）；106 條 O222 事件 ref 越界 **0**。
- **headline 獨立重算**：D6 tie **1200/7440**；G4 成本律 **242,172** 格（值計數 `{1: 62, 2: 7626, 3: 234484}`；頂限 62 ctx 時 **7564 = 2N(N−1)**，與 G1G8 之 ledger 長度獨立相等 —— 只報**計數恆等**）；C2G7 **62/62 欄和 = 0** 且 `rank_GF(7)(K) = 6`；B5 `44 × 123/88 = 61.5`；G1G8 `2N(N−1) = 7564`；A2 `raw = 62⁴`。
- **★ 本輪修復（真覆蓋缺口）**：MANIFEST 歷來**漏收 43 件** —— `docs/01–04`、`scripts/01–04／07／08`、`data/01–04`（含 **`04_b2_settings.json` 62 軸**、`04_b2_partition.json`、4 個 freeze round、`08_a2_h_table.json`、盲／dev 值、`11_b5_contract_audit.json`）、`logs/01–04`（含 9 個閘 log）。**嚴重度**：`04_b2_settings.json`／`08_a2_h_table.json` 係**每輪都要 pin** 之凍結輸入，此前**無任何完整性記錄**。⟹ 以 `backfilled_by = closeout3 coverage repair` 明標回填，**既有條目一件未改**。
- **設計裁決**：審計器自身 3 件產物**故意唔納入** MANIFEST（自指條目無法與讀取它之同一次執行自洽）；C6 明文標 `untracked-by-design`，其完整性由 freeze 紀律 ＋ `scripts/07` 於 MANIFEST 寫入後核對。
- **審計器自身糾錯（2 件，非被審對象）**：C1 首版猜錯檔名（`docs/01_b2_contract.md` 等不存在）⟹ 改用真實檔名；C3c 首版域算錯（242,172 之來源 = 62×62×**63**，含空頂標記）⟹ 域與期望值更正。
- **未閉合**：同 §9.12 清單。




## Session 16 — G2 + Q5（O206 `f(n)`／`F_proj = 17` 身份統一）（2026-09-30）

**指令**：繼續。**先 register（見數前，6 子問題）＋ 合約先於數字**（`docs/23`，`g2q5-contract-v1` ＋ A1）。

- **性質**：**溯源／判定輪**（唔出物理新數字，唯一新算 = G2c 之界）。**14 件唯讀上游 pin（J1–J14）**，機器只可讀。
- **閘** `scripts/33`：C1 pin／C2 唯讀／C3 精確算術／C3b 名稱＋寫入／C4 六格清單／C5 無上游 import ⟹ **C1–C5 PASS，GATE = OPEN**，impl `84789a1a8314f61cac18beb5…`。
- **★ G2 → 🟢 已判定（負面 ＋ 層次修正）**：
  - 原記「等 O206 之逐模頻率 `f(n)`」係**錯層**：`f(n)`（O206 `docs/01`）= **質量譜閉合因子**（`ω_n = μ²·f(n)`），假說**已否證**（全樹 123 檔遍歷：**無**任何 `f(n)` 數值表）。
  - **資源側所需之頻率早已 available**：`ω_n = √γ_n = 2sin(πn/88)`，44 模，**`γ_n = ω_n²` bit-tight（max dev = 0.00e+00）**、`Σγ = 90`、`ω_44 = 2`（Nyquist）；B5 `I4` 之 `ω_n = μ² = 2` 係 **fiducial**（O206 F1 裁決：非結構強制）。
  - **唯一新算（G2c）**：非均勻歷階 `c_n = (123/88)(ω_n/⟨ω⟩)`（`Σc_n = 61.5` 精確）⟹ 讀數界 **`[29, 790]`**；uniform 之**顯式逐讀模擬 = 44 讀**（重現 B5 ✓ 內建 sanity）。⚠ `read ↦ mode n` **未定義** ⟹ **只報界**；採用非均勻 = **modelling choice**（會破壞 O41 之均勻預算讀法）；O126 之 tick 錨獨立。
- **★ Q5**：`F_proj` 係**符號碰撞**（(i) 維數 `17`；(ii) 質量形狀因子 `C_f = {18/5, 15.5, 37, 42}`）；14 件 pinned 檔**零等式斷言** ⟹ **三方「衝突」= 同名，無數學衝突**（建議質量路線統一用 `C_f`，只經 register）。**維數側 🟢 統一**：三重身份 `17 = N_d − n* = L₅ + C(4,2) = L₆ − 1`（44−27／11+6／18−1）且 `n* ≡ N_d − L₆ + 1` 使 A 與 C **代數同一** ⟹ **非數值巧合**；`kernel_modes = {28..44}`（17）✓。**能量側 🟡 已量化**：`E_bottleneck = 0.6154630941421971` 對 `8/13 = 0.6153846153846154` 之**偏差 7.848e-05** ⟹ **唔係 8/13**；成因未定。
- **★ 跨 O 連結**：`E_sync = N_d·L₁₀/88 = 44 × 123/88 = 61.5 = 123/2` **＝ O222 B5 之 `I1`（`⟨W⟩²`）** ⟹ O33 之 sync 預算與 O222 之資源上界係**同一恆等式**。
- **獨立審計** `scripts/35` **8/8 PASS**（**全樹 123 檔遍歷**證明無 `f(n)` 數值表；`γ/ω` **原始文本**重析；**顯式逐讀模擬**重得 [29,790]＋44；**整數算術**重得三重身份；**補集求和**重得 E_capture 一致 1e-14；14 pins 未變；**O222 目錄外零檔案被改**）。
- **自我披露（2 件）**：① 閘首跑**正確拒收**機器浮點字面值（`61.5`／`1e-09`／`1e-06`）⟹ 按鐵律**唔放寬閘**，改 impl 用 `Fraction`／整數十次冪；首跑 log `logs/33_g2q5_contract_firstrun_float_literals.out`（首版 impl `fdba021b03641e34e9eb9d3c`）保留。② 機器 G2a 探針字串「**真實**開放項」miss 上游「**真正**開放項」（機器誠實報 0），審計以另一字串補掃得 **4 檔** ⟹ **判定不變**。
- **register**：`O222/G2a`（negative）、`G2b`（closed）、`G2c`（partial）、`Q5a`（closed）、`Q5b`（closed）、`Q5c`（partial）；`O222` note；**handoff** → **O121**（8/13 唔成立）／**O210**（0.6155 待審計項復核完成）／**O206**（G2 解除依賴 ＋ 兩份總結狀態不一致）。
- **未閉合**：Q5c 能量側殘差**成因**；其餘同 §9.13。

## Session 17 — R19 未閉合結構收束輪（8 格 4✅/4🔴 ＋ K5add ✅）

- 合約 `docs/25_r19_contract.md`（`r19-contract-v1`，**見數前寫定**，8 格謂詞＋唯讀 pin L1–L9）＋修訂 A1–A3；
  結果 `docs/26_r19_results.md`；閘 `scripts/36`（C1–C5 PASS，**GATE = OPEN**，impl `c0272e0a…`）；
  機器 `scripts/37`；獨立審計 `scripts/38` **9/9 PASS**；MANIFEST **193** 件（drift 0／missing 0）。
- **K1 🔴（精確化）**：`rank_R(K) = 6` EXACT（雙向有理證書＋非零 6×6 子式 −64）；**完全** fooling-set 搜尋最大 = **5**
  ⟹ `sign_rank(K) ∈ [5, 6]`（舊記錄下界 4 ⟹ 升至 5）。**K1b 🔴**（推論格未成立）。
- **K2 ✅**：`hits = 2·#pairs − net_ledger` ⟹ **124 = 7688 − 7564**；協定 = 每對 **3 讀事件**（11532 = L8 `reads_per_pass`）
  ＋1 pop；直方圖 **{2: 124, 3: 3720}** 與 L8 逐項一致。
- **K3 🔴（兩項預測皆被否證，機制量清）**：值層規則可完全判定、命中 124（120 起始態不變）；
  override **依起始態**（s0=0 → 58，首讀 28／回滾後 30；120 態範圍 [55, 81]；**=65 恰 10 個態**）
  ⟹ 合約「全部回滾後」與 L8 G1c「全部在首讀」**兩者皆被否證**；實測 = 兩路皆載。
- **K4 ✅**：`R_det = 2`（本機 vs L4 逐對未命中 **0 mismatch**）、`R_indep = 1` ⟹ `R ≥ 2` 在獨立副本義下失敗；缺口 = 架構非算術。
- **K5 🔴（③ 依合約）＋ K5+ ✅**：③ 連分數門檻 1e-12 實測 6.07e-13 ⟹ 門檻與 1/q² 同量級**無判別力**；8/13 = CF 收斂子。
  ★ **補做精確分圓跡檢定**：Φ_88（次數 40）、`Tr_K(G) = −40`（Ramanujan 和）、`20G − Tr_K(G)·1 ≠ 0` ⟹
  **殘差 `= G + 55/2` 代數上非有理**（共軛軌道 20）⟹ 比 ③ 之數值門檻**更強**。
- **K6 ✅（🟡 判定）**：五個凍結次序逐對未命中向量與 L6 **逐字一致**（43/44/44/42/44）；零個代表選擇鍵 ⟹ 代表 = **約定**。
- **K7 ✅**：五窗 all4 精確 `max|S|` = lex 2／diag 2／antidiag 2／block **16/15**／stride 2 ⟹ 全 ≤ 2；
  鏡像以 L7 C4（C1 = 2、C2 = 3）校準；對蹠有序對 112；審計暴力復得 block 16/15。
- 3 次重凍（4 段 log 全留）；三項自我披露（greedy 只到 4、K 無 0 條目、58 vs 65 之起始態成因）見 `docs/26` §3。

## Session 18 — R20 缺口補完輪（`docs/27`／`docs/28`；4 ✅ / 2 🔴）

- **M3（主結果）**：`sign_rank(K) ≤ 3` **已精確認證**（600/600 候選；r = 5/4/3 全接受、r = 2 零接受）
  ⟹ `sign_rank(K) ∈ [2, 3]`（R19 之 `[5, 6]` 兩界皆修正）。
- **M1 🔴**：fooling-set ⟹ sign-rank 之蘊含**無效**（精確反例族 det = 0，對角正／非對角負）⟹ R19 下界 5 撤回。
- **M2 ✅**：有效下界 = 2（秩 1 排除）；arrangement 界不排除。
- **M4 ✅**：`G` 之極小多項式 deg 20 精確（`P(G) ≡ 0 mod Φ₈₈`、`Tr_K(G) = −40`、Newton 恆等式獨立覆核）。
- **M5 🔴**：權威協定（a → b → pop → b 再讀）逐態：命中 124 ✓；三類 override = A 26–40／中讀 26–40／**回滾後 0**；
  R19 之 (28, 30) 與 [55, 81]**不可重現**（其為 R19 鏡像標籤）⟹ **兩路皆載 stale 為必然**，回滾後重讀從不 stale。
- **M6 ✅**：五次序總讀數 `[43,44,44,42,44]` ⟹ 唯一最小 42 = `block` ⟹ 代表由「最小總讀數」唯一決定。
- 制度：閘 `scripts/39`（11/11，GATE = OPEN，impl `0f823398…`；兩次重凍各留舊 freeze）、
  機器 `scripts/41`（4/6）、審計 `scripts/42`（**23/23**）、MANIFEST 回填 18 件、closeout 已納 R20。

## Session 18（R20 收尾 → R21 前半，2026-09-30）
- **R20/M7（秩 2 之組合排除）**：合約 `docs/29`（見數前寫定）· 判定器 `scripts/44`（必要條件：每軸 +1 集須為 12 列類型圓序之連續弧）
  → **🔴 秩 2 不可能（窮盡、22 節點）** ⟹ 配合 M3 上界 ⟹ **`sign_rank(K) = 3` EXACT**（R19 [5,6] 與 R20 [2,3] 皆作廢）。
  控制組 C1 PASS／C2 FAIL；小規模暴力（m=4..7、10 實例）**10/10 一致**；過程三次實作修正全部由控制組／對照抓出（LCG 低位、繞回剪枝、圓弧判式）。
- **R21/N1（剛性）**：合約 `docs/30` → r = 3 族 200/200 **同一 Gram 型與 vsign 型**（r = 4/5 柔性）⟹ 秩 3 實現**至對稱唯一**。
- **R21/N2a（辨識，K 相關）**：U 側 `G_K` vs `gram_sign` **0/144 完全吻合**；V 側 960/3844 不吻合（null 亦 960）。
- **R21/N2b（辨識，凍結向量）**：U 側 `sgn(r_i·r_j)` vs `gram_sign` **0/144 完全吻合（第二獨立路徑）**；
  V 側 790/3844（20.6%）≪ shuffle null 57.3%，且 **ε-規範不存在** ⟹ V 側非軸自身、非其符號規範、非 K 之行相關。
- 制度：MANIFEST 222 件（drift 0）· closeout **15/15（14 輪）** · register：M7／N1 closed、N2a／N2b partial、K1 收。

## Session 19（R22 收尾 → R26；「全部繼續」）
- **R22/QM 收尾**：Q4 修正（`Σ|χ|² = 120+0·√5` 精確 ⟹ 基本 2 維表示不可約 = spin-½）；QV5 形式化（完全最大化、校準：C1 all4 = 2、C2 all4 = 3；權威對蹠集 62 ✓）。
- **R23/U1**：V 側「閉式」更正（搜索候選之 Gram 非 canonical，702/200 不吻合）⟹ 下修 N2d/N2e。
- **R23/U2**：**V 側 canonical 確立** = `sgn(Kᵀ G_frozen K)`（0/3844、0/744、0/3844 三重認證）+ **`rank_{Q(√5)}(G_frozen) = 3 = sign_rank(K)` 結構證明**。
- **R24（四項缺口全推）**：① K5 殘差精確閉式（Z[ζ₁₇₆] 證明）+ 20 次最小多項式重算；② C2 一般閉式 `hits = 2N`、`net = 2N(N−1)`（N=4..62 全中）+ 對角/非對角分解；③ `rz(2..7) = 3,6,9,12,16,21` 精確 + `rz(q²+q+1) = (q+1)(q²+q+1)`（PG(2,q)，q=2,3,4）；④ n≥6 全類比例：n=6 L=9 = 7.9679%、L=10 = 17.787%、**L=21 比例 = 1 已證**（n=7 抽樣 100%）。
- **R25**：K1b 收束（`sign_rank = 3 ≪ 6` ⟹ amplitude 缺口非 rank 現象 ✅）+ 缺口定位（複相位層 + 二分張量層；核 = 2I ⊆ SU(2) 單系統）+ 可證偽判準 F1/F2。
- **R26**：G1 語義形式化（override = D5 觸發之值級翻轉；**`hits = 2N` 對全部 120 初始態恆定**；override ∈ [52,80]）+ G8 冗餘 no-go（決定性協定 ⟹ `R_indep = 1` 定理）。
- 資產：MANIFEST 302 件（drift 0）；closeout 15/15（14 輪）；register drift 0。
