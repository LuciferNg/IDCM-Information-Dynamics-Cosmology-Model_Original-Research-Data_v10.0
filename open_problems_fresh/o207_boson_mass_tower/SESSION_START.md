# O207 — SESSION START

> **Session**: 2026-09-21（新建立 — 未開始推導）
> **狀態**: 🔴 已註冊 — bootstrap 層已建（新 session 處理）
> **來源**: 移交自 O206 第五輪（玻色子扇區審計）；用戶指示「玻色塔應開新O新session處理」
> **前置**: O37 → O38 → O39 → O82 → O83 → O164 → O204 → O206
> **v10.0 位置**: IDCM-v10.0--It-From-Beat/open_problems_fresh/o207_boson_mass_tower/

## 問題

見 `01_problem_record.md`（完整問題陳述 + 已確立結構 + 7 個開放項 B1–B7 + 6 條攻擊路線 + 驗證標準）。

**一句話**：玻色質量塔 `m_n = M₀√γ_n`（n = 1..44，零自由參數）係 IDCM 之玻色子質量譜，
範圍 [1.99, 55.80] MeV；但 **O204 docs/09 C3 = 🔴 FAIL「未有專屬盲測協定」**
（現時只鎖 m₇ = 13.8002 ± 0.0005 MeV）⟹ 本 O 主攻**盲測協定 + 模式身份 + 尺度起源**。

## ★ 本次 session 已完成（移交準備，bootstrap only）

| # | 事項 | 狀態 |
|:-:|:-----|:----:|
| 1 | 編號碰撞檢查（205 墓碑 / 206 已用 ⟹ 用 **207**） | 🟢 |
| 2 | `01_problem_record.md` 撰寫（問題 + 已確立結構 + B1–B7 + 攻擊路線 + 驗證標準） | 🟢 |
| 3 | `SESSION_START.md` 撰寫 | 🟢 |
| 4 | README.md 新行 | 🟢 |
| 5 | ⚠️ **未建** scripts/ data/ docs/ scaffold（用戶指示「新 session 處理」；遵 bootstrap-only 紀律） | ✅ 按指示 |

## ★ 下一 session 從呢度開始（交接點）

**第一步（最平，結果決定後面點做）**：建 44 模式檢定表
```
scripts/01_tower_blindtest_protocol.py
  對每個模式 n = 1..44 列出:
    m_n = M₀√γ_n (MeV) | 觀測通道 | 現行實驗狀態 | 所需靈敏度 | 可判定性
  通道候選:
    · DM 直接探測 (m₇ = 13.8 MeV → 輕 DM / 暗光子搜尋)
    · 輕玻色子搜尋 (beam-dump / 固定靶; 1.99–55.8 MeV 窗口)
    · 星系動力學 (O180 投影核 v_k = c·cosθ_k 已建)
    · CMB 額外輻射 ΔN_eff (Goldstone 熱歷史, O204 U7)
  驗證標準: 至少一個模式有【現行】實驗可判定之預言 (唔係「等未來」)
```

**第二至六步**：見 `01_problem_record.md` §四（B3 模式身份 / B6 焦距 / B2 尺度 / B4 交互算子 / B7 場論陳述）。

## 已確立結構（可直接引用，全部有出處）

```
🟢 玻色塔: m_n = M₀√γ_n, n = 1..44; M₀ = 27.900915 MeV; γ_n = 4sin²(πn/88)
🟢 塔範圍 [1.9917, 55.8018] MeV (跨度 28.0×) — MeV 尺度輕扇區
🟢 m₇ = 13.800155 MeV (O204 DM 候選; 預註冊協定 O204 docs/11)
🟢 m_δW = M₀/2 = 13.9505 MeV (徑向模, V''(W₀) = 4μ² = 8)
🟢 m_θ = 0 EXACT (Goldstone, 導數耦合保護)
🟢 傳播子 G_n(0) = 1/(2ω_n), ω_n = √γ_n (O83, 58/58 PASS)
🟢 質量-頻率鎖 m_n = h_eff·f_n, f_n ∝ √γ_n (O164, 44/44 dev 2.7e-51)
🟢 ★★ 費米/玻色 Z₂ 分離: X 對角精確零 ⟹ 費米機制觸唔到玻色扇區 (O206 docs/14)
🟢 玻色扇區 = Z₂-偶 (不動點 γ_22 = μ² = 2); Σγ_even = 46
🟢 費米子質量 = 玻色子交換 m_f = κ²ω_n, κ² = M₀ (O82)
🔴 玻色塔盲測協定 (O204 C3 = FAIL)
🔴 W/Z/H 唔落喺塔上 (所需 n 非整數); W/Z/H 質量未推導
```

## 依賴（上游 O）

| O | 狀態 | 提供嘅輸入 |
|:--|:----:|:-----------|
| O37/O38/O39 | 🟢 | W-field Lagrangian / M₀ / 凝聚 ⟨W⟩² = 61.5 |
| O82 | 🟢 | 費米子質量 = 玻色子交換 (κ² = M₀) |
| O83 | 🟢 | 傳播子 G_n(0) = 1/(2ω_n); C_ℓ 橋接 |
| O164 | 🟢 | 質量-頻率鎖 h_eff |
| O204 | 🟢 | **玻色塔定義 + m_δW + Goldstone + C3 盲測 FAIL** |
| O206 | 🟢 | F1 動態頻率 ω_n = √γ_n; **Z₂ 費米/玻色分離定理** |
| O156/O162 | 🟡/🟢 | CY₃ 鏡頭 / 焦距 detent {55,88,176} |

## 資源路徑

- 問題記錄: `01_problem_record.md`
- 來源 O 診斷: `../o206_per_mode_frequency/docs/14_boson_sector.md`
- 塔之權威定義: `../o204_wfield_constitution/final_result.md` §第二輪
- 盲測 FAIL 原文: `../o204_wfield_constitution/docs/09_closure_criteria_audit.md` §C3
- m₇ 預註冊協定: `../o204_wfield_constitution/docs/11_fifth_round_closure.md`
- 傳播子: `../o83_correlator_cmb/docs/02_derivation_record.md` §2
- CY₃ 鏡頭: `../o156_rge_first_principles/docs/09_cy3_lens_structure.md`

## 方法論紀律（繼承 O136 五判準 + O206 新增三條）

```
① 範圍命中永遠唔係證據（任何無界函數+冪次可達任意範圍）
② 置換 null 退化（重排配對 ⟹ 統計量對置換不變；用 9! 搜索配對才有效）
③ 度量必用對數值（冪律 m ∝ f^a ⟹ 擬合 ln f；原始值 = 指數擬合）
④ 參數可辨識性判準（候選間 ΔRMS < bootstrap σ ⟹ 不可辨識）
⑤ 過度吻合判準（吻合精度優於輸入精度 ⟹ 必然係事後反解）
⑥ ★ 池子 null（O206 docs/12 §C）：任何「命中結構值」必須對 607+ 表達式池做 null，
   計隨機 α 之命中數中位數 —— 若觀測 ≈ 隨機中位 ⟹ 命中無信息
⑦ ★ 扇區分離檢查（O206 docs/14 §三）：用任何算子前先查其宇稱/對角性
⑧ 零新常數；禁 φ-power fitting；禁後驗湊算子
⑨ ★ 單位轉換必須獨立核算（O206 實戰：meV↔MeV = 1e−9；單位 bug 可令 check「PASS」而全錯）
```

## 範圍紀律

- ✅ 只喺 `o207_boson_mass_tower/` 內寫入
- ❌ 唔改 O204 / O206 / 任何其他 O 嘅檔案（如需修正上游，寫入該 O 嘅 SESSION_START 為「待修正點」）
- ❌ 唔做費米子映射層（屬 O206，已收尾）
- ❌ 唔做 SM 電弱對稱破缺鏈（屬 O85）
- ⚠️ 本 O 為 **bootstrap 層** — 未建 scripts/data/docs，由下一 session 建立
