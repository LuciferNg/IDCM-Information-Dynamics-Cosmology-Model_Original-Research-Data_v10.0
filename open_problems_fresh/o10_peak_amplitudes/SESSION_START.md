# O10 新 Session 啟動文件 — 峰幅度結構公式

> 開新 session 時: 載入下面 skills, 然後將「啟動 prompt」複製做第一條訊息。

---

## 所需 Skills

### 1. `camb-cmb-verification`（核心, 必須）
- CAMB 峰檢測、振幅提取
- 文獻 D_ℓ 高度 (Planck: D₁≈5700, D₂≈2600, D₃≈1400, D₄≈800)

### 2. `theoretical-physics-validation`（輔助）
- 防止數字遊戲 (φ-power 擬合陷阱)

## 前置資料

```
A₂/A₁ = 0.456 (觀測) vs 3ε = 0.4635 (IDCM, 1.6% ✅)
A₃/A₁ = 0.246 (觀測) vs φ⁻⁴ = 0.146 (41% ❌)
A₄/A₁ = 0.140 (觀測) vs φ⁻⁵ = 0.090 (36% ❌)
ε = φ⁻¹/4 = 0.1545
峰幅度 D_ℓ: D₁≈5700, D₂≈2600, D₃≈1400, D₄≈800 μK²
```

## 啟動 Prompt

```
開 O10 峰幅度專案: /home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o10_peak_amplitudes/

任務: 搵出 CMB 峰幅度 A_m/A₁ 嘅結構公式

背景: A₂/A₁ = 3ε 已閉合 (1.6%)。A₃/A₁, A₄/A₁ 未閉合
(φ⁻⁴/φ⁻⁵ 偏差 36-41%)。

方向:
1. 精確觀測: Planck binned 數據重新量度 A_m/A₁
2. 指數衰減: ln(A_m/A₁) vs m — 斜率 α 有冇結構意義?
3. 組合: A₃ = 3ε × 結構因子? (例如 ×ε, ×φ⁻², ×κ?)
4. WKB 聲波包絡: 解析近似對比
5. 擴散阻尼: exp(-ℓ²/ℓ_d²) 包絡 — ℓ_d 有冇結構值?

載入 skills: camb-cmb-verification, theoretical-physics-validation

鐵律:
- 禁止數字遊戲 — 任何公式要有物理/結構來源
- 3ε 閉合係基準 — 新公式要包含 3ε 做特例
- 誠實: 如果 A₃/A₄ 真係冇結構公式 → 🟡 記錄
最後: 雙重驗證 + 更新 01_problem_record + README
```

## 常見坑

1. 峰高度提取好脆弱 — 用文獻 binned 值, 唔好自己從 CAMB raw 估
2. A₂=3ε 已閉合 — 新公式唔可以破壞呢個
3. 指數衰減 α 可能係 0.5 (WKB) 或 1 (damping) — 要分辨
4. φ⁻⁴/φ⁻⁵ 失敗唔代表「冇公式」— 可能係組合


---

## ★ 全樹路徑衛生審計註記（2026-10-02，append-only）

> 由 skill `script-chain-reproducibility` 全鏈核對器（`path_hygiene_scan.py`）全樹掃描建立——
> **2026-10-02 首次**。**本節唔改動上方任何內容。**
>
> ⚠️ 本節係**工具層審計**（產物路徑衛生），**唔屬本 O 推導**；亦冇對本 O 任何結論作出判定。
> 完整報告：`path_hygiene_audit_20261002/REPORT.md`

### 〇. 一句話

本目錄命中 **2 個 ghost-tree call site**。

### 一. 命中清單

#### ⚠️ ghost tree 依赖

| # | 檔案:行 | 讀取目標（ghost tree 內）|
|:--|:--|:--|
| 1 | `o10_peak_amplitudes/scripts/75_number_check.py:16` | `open_problems_fresh/o9_high_ell_peaks/data/planck_tt.txt` |
| 2 | `o10_peak_amplitudes/scripts/76_number_check_fixed.py:16` | `open_problems_fresh/o9_high_ell_peaks/data/planck_tt.txt` |

### 二. 處置（別 O 執行；本節只記移交）

```
⚠️ ghost tree 依赖：2 個 call site 讀 `/home/wsl/Projects/IDCM/IDCM-v10.0/`。
   ① 把所需檔搬入本 O `data/`（或記明「唯讀外部輸入」）
   ② `BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` ＋ 相對路徑
   ③ 風險（已量化）：ghost tree 係 2026-09-08 副本（全樹 288K）。全樹 301 個 call site 分類：
      ① 69 個目標仍存在（讀嘅係**陳舊副本**）；② 231 個目標已失踪但同相對路徑在 repo 存在
      （⟹ **改一行即可，零資料損失**）；③ 1 個 repo 內完全冇。逐 O 對照表 → 同報告目錄 `ghost_dispatch.md`
```

> ⚠️ 依據 `idcm-closeout` §8.1：跨 O 問題**只登記移交，唔准就地修**。本節由**外部審計**寫入，
> 本 O 之 session **有權刪去或改寫本節**（上方內容不受影響）——但如果決定保留，
> 請在 GATE / 下輪 round doc 裏明文記下「已接納 / 已處理」。
