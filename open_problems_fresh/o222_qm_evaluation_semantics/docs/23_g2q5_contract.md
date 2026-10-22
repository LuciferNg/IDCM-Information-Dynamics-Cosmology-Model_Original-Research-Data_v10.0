# 23. G2 + Q5 合約（`g2q5-contract-v1`）

> **凍結輪：`docs/23` 於任何本輪數字之前寫定。** 本輪為**溯源／判定輪（provenance round）**：
> 唔產生新物理數字，只做①釐清 O222 兩個未閉合項之**真正缺口**、②以唯讀上游重證可判定部分、
> ③對不可判定部分報 🟡／🔴 並經 register 交接。
> **時序披露**：為寫合約，我於**偵察階段已讀過**上游若干值（O206 之 f(n) 判定、O121 之譜 JSON、
> O33/O210 之 T_pipe 定義）。合約之**格、謂詞、門檻**係獨立寫定，**唔由**該批值反推；
> 機器（`scripts/34`）必須**由 pinned 檔案重新讀取**，唔准用我嘅記憶值 ✓。

## §0 範圍與聲稱上限

- **本輪唔宣稱**：導出 QM／ħ／Hilbert／Born；唔宣稱 B5 之資源結論失效；唔修改任何上游檔案。
- **本輪宣稱**：① O222 `G2`（O206 `f(n)`）之**層次身份可判定**；② `Q5`（`F_proj = 17 = dim ker T_pipe`）
  之**維數側恆等式可判定**（三重身份＋代數收斂）；③ 能量側殘差**精確量化**（但**唔**宣稱已閉合）。
- **★ 跨 O 鐵律**：對上游 O 只**唯讀**；一切需求／發現**只經** `problem_register`（`note`／`handoff`）。
  **禁止**寫入任何其他 O 目錄任何檔案。

## §1 凍結輸入（唯讀上游；逐項附所有者與用途）

| # | 檔（repo 根相對） | 所有者 | 用途 |
|---|---|---|---|
| **J1** | `open_problems_fresh/o206_per_mode_frequency/final_result.md` | O206 | f(n) 假說之**最終判定** |
| **J2** | `open_problems_fresh/o206_per_mode_frequency/RESULT.md` | O206 | 同 O 之**另一份**總結（狀態／計數與 J1 須並列比對）|
| **J3** | `open_problems_fresh/o206_per_mode_frequency/docs/01_problem_record.md` | O206 | `f(n)` 之**定義式**（`ω_n = μ²·f(n)`）|
| **J4** | `open_problems_fresh/o206_per_mode_frequency/docs/02_f1_existence_audit.md` | O206 | `ω = μ²` 之結構地位（F1 審計）|
| **J5** | `open_problems_fresh/o206_per_mode_frequency/docs/08_round1_verdict.md` | O206 | F1 裁決（fiducial vs 結構強制）|
| **J6** | `open_problems_fresh/o121_black_hole_entropy/data/01_tpipe_dag_spectrum.json` | O121 | T_pipe† 譜 ＋ **17 之三重身份**（A/B/C）|
| **J7** | `open_problems_fresh/o210_causal_tensor_algebra/docs/02_operations_closure.md` | O210 | `F_proj = dim ker T_pipe = 17 = L₆−1` ＋ E_proj/E_sync |
| **J8** | `open_problems_fresh/o210_causal_tensor_algebra/data/02_type_registry.json` | O210 | `F_proj` 之型別登錄（`Sc`／`dim`／`Q`）|
| **J9** | `open_problems_fresh/o33_projection_mechanism/final_result.md` | O33 | `T_pipe = diag(σ_n)`、`n* = N_d − L₆ + 1 = 27`、`E_sync = N_d·L₁₀/88 = 61.5` |
| **J10** | `open_problems_fresh/o193_power_sum_domain/docs/04_moment_domain_cutoff.md` | O193 | `17 = F_proj = L₆ − 1` 之**跨 O 引用** |
| **J11** | `open_problems_fresh/little_red_dots/data/k_chain_modes.json` | LRD | K_chain 44 模之 `γ_n`／`ω_n`（譜表，唯讀）|
| **J12** | `open_problems_fresh/o222_qm_evaluation_semantics/data/01_wfield_qm_verification.json` | O222 R0 | 本 O 自己之 `γ_n = ω_n²` EXACT 驗證（A1）|
| **J13** | `open_problems_fresh/o222_qm_evaluation_semantics/docs/07_b5_contract.md` | O222 B5 | 本 O 之 I1–I5（成本模型原文） |
| **J14** | `open_problems_fresh/o206_per_mode_frequency/merged_o221/docs/01_problem_record.md` | O206/O221 | 三方 `C_f`／`F_proj` 之值清單（`{18/5, 15.5, 37, 42}`）—— **A1 新增** |

## §2 格與謂詞（**判據寫死；每格三件齊備：凍結物件＋可計算謂詞＋數字**）

### G2 — 逐模頻率 `f(n)`（O206）

- **G2a（f(n) 之身份）**：由 **J3** 抽出 `f(n)` 之定義式（`ω_n = μ²·f(n)` 之語境），
  並由 **J1／J2** 抽出其判定。**謂詞**：`f(n)` 被定義為**質量閉合因子**（非資源成本之頻率）
  **且**其假說被**明文否證**。判據 = 兩者皆在 pinned 檔中逐字可引 ⟹ ✅；缺一 ⟹ 🟡。
- **G2b（資源側頻率之可用性）**：由 **J9/J11/J12** 判定：逐模頻率 `ω_n^dyn = √γ_n = 2sin(πn/88)`
  是否**已存在且逐模可算**；並由 **J4/J5** 抽出 `ω = μ²` 之結構地位。
  **謂詞**：① 譜表 44 個 `ω_n` 全部可讀且 `γ_n = ω_n²`（相對誤差 ≤ 1e-9）**且** `ω_44 = 2`；
  ② `ω = μ²` 之地位為**非結構強制**（fiducial）。兩者皆成立 ⟹ ✅。
- **G2c（非均勻歷階之靈敏度界）**：**唯一新算**。以 `c_n = (123/88)·(ω_n/⟨ω⟩)`（`ω_n` 由 **J11**）計：
  ① 恆等式 `Σ_{n=1..44} c_n = 123/2 = 61.5`（**精確**，因 `Σω_n/⟨ω⟩ = 44`）；
  ② 預算 61.5、終止條件 `B_rem < E_min = 123/176` 下之**讀數界**
  `[⌊61.5/c_max⌋, ⌊61.5/c_min⌋]`（最貴／最平模態序列）。
  **判據**：① 必須精確成立；② 界必須**包含** B5 之 uniform 值 **88**，否則報 🔴。
  **明標**：`read ↦ mode n` 之對應**未定義於任何凍結記錄** ⟹ **只可報界，唔可以報「實際讀數」**；
  且「採用非均勻歷階」係 **modelling choice**（會破壞 O41 預算恆等式之均勻讀法）⟹ 唔取代 B5 結論。

### Q5 — `F_proj = 17 = dim ker T_pipe` 之身份統一

- **Q5a（符號碰撞）**：由 **J7/J8** 與 **J10** 及 O206/O64 之記錄清單，枚舉 `F_proj` 之**所有**出現語義。
  **謂詞**：至少兩個**互不相同**之對象（(i) 維數 17；(ii) 質量框架之形狀因子 `{18/5, 15.5, 37, 42}`），
  且**冇任何**上游記錄同時斷言兩者相等。⟹ ✅（「三方衝突」= **同名**，非數學衝突）。
- **Q5b（三重身份）**：由 **J6/J7/J9** 抽 `17` 之三條結構式並**獨立計算**：
  `A = N_d − n* = 44 − 27`；`B = L₅ + C(4,2) = 11 + 6`；`C = L₆ − 1 = 18 − 1`。
  **謂詞**：三條**全等 17** **且** `n*` 之結構定義 `N_d − L₆ + 1` 使 A 與 C **代數同一**
  （即 `44 − (44 − 18 + 1) = 18 − 1`）⟹ 恆等式**非數值巧合**。
- **Q5c（能量側）**：由 **J6/J7/J9** 抽三個數：`E_sync^{closed} = N_d·L₁₀/88 = 61.5`（**＝ O222 B5 之 I1**）、
  `E_sync^{theory}`、`E_capture`；並抽 `E_bottleneck = E_sync^{closed} − E_capture`。
  **謂詞**：① 三數**逐字**記錄（唔准只報兩個）；② 由 **J11** 之譜表**獨立重算** `E_capture`
  （相對誤差 ≤ 1e-9）；③ 檢查 `E_bottleneck ≈ 8/13`：**|E_bottleneck − 8/13| ≤ 1e-6** 才可標「= 8/13」，
  否則**必須**明報「**唔係** 8/13（小數級近似；給出確切偏差）」。三項全成立 ⟹ 本格 ✅（量化完成）；
  **成因未定** ⟹ 整個 Q5 之能量側**維持 🟡**（上游 O210 自記「待審計」維持有效）。

## §3 閘（`scripts/33_g2q5_contract.py` 之硬約束）

- **C1** pin：J1–J13 全件 sha256 記錄入 `data/33_g2q5_freeze.json`；執行前重驗（唔一致 ⟹ FAIL）。
- **C2** 唯讀：機器**只可**讀 J1–J13；AST 檢查禁止任何 `open(...,'w')`／`os.remove`／
  `shutil.copy` 到 J1–J13 之路徑；禁止 `subprocess`。
- **C3** 精確算術閘（沿用）：AST 禁 `cos/sin/tan/pi/sqrt/exp/log` **函數呼叫**（`sin` 只可以係
  **字串**出現）＋ 禁非整數浮點字面值 ＋ 禁 `numpy/scipy/math/random`。
- **C4** cell 清單必須恰為 `{G2a, G2b, G2c, Q5a, Q5b, Q5c}`；缺一／多一 ⟹ FAIL。
- **C5** 機器不可 import 上游任何腳本；只可讀 J1–J13（純文字／JSON）。
- ⚠ **C3 例外（明文）**：G2c 需要 `ω_n = 2sin(πn/88)` 之**數值**——**唔准**在機器內呼叫三角函數。
  ⟹ 機器**只可用 J11 譜表之既有數值**（已含 `omega` 欄），或由 `γ_n` 取 `√` 之**牛頓法自寫迭代**
  （純整數／Fraction 除外之算術；迭代次數固定，寫死於合約）。

## §3.5 合約修訂（amendments）

| # | 內容 | 性質 |
|---|---|---|
| **A1** | 2026-09-30（**機器開跑前**）：凍結輸入增列 **J14** = `o206_per_mode_frequency/merged_o221/docs/01_problem_record.md`（Q5a 之形狀因子路線需要「三方值清單」在場作證）。**格、謂詞、門檻一律不變**（G2c 之界準則、Q5a 之「零等式斷言」判據、Q5c 之 8/13 門檻 1e-6 全未動）。 | 補輸入（impl-only）|

## §4 揭示窗

本輪**無盲測窗**（無目標值可對；上游值係輸入而非預測目標）。
**強制披露**：G2c 之界若與 B5 uniform 值 88 之關係不符預期，**照報**，唔准改判據。
