# P6 — neutrino（中微子質量譜：W-field p6 模式）

## 狀態: 🟢 上游閉合（O49/O66）＋ 真剩餘 4 項 🟡

**IDCM v10.0「中微子質量譜」問題**：從 K_Chain γ_n = 4sin²(πn/88)
（n=6, γ₆=0.180736）＋ 12D WDVV eigenvalue 推導 m_νi 同 Δm²₂₁/Δm²₃₁，
零自由參數。2026-08-15 五個探索 scripts；唯一產出「閉合」（05 校準＋Z₃ 修正）
屬 **校準＋後驗**：Δ31 ratio=1.0 係恆等（由 PDG 反推 M_comp），
Z₃=3² 係見到 8.99≈9 先後驗除以 9 — 未過 IDCM 四硬測（零參數／盲測／樣本外／結構剛性）。
四條前向路線（12D λ、γ_nᵖ、幾何 seesaw、M_comp 幾何）全部 fail（10⁵–10⁻⁷ eV 錯標度）。

**2026-10-20 審計**：5 scripts 隔離重跑＋獨立複算，確認
04 聲稱錯 1000×、03 Δm² 單位混用、01 §8 變數洩漏、05 Σm 超 DESI 上限。詳見 `01_problem_record.md` §4。

**2026-10-20 攻堅判決**：上游 O49/O66 已閉合 M_comp（3.6890e13 GeV，
vs 校準 0.051%）＋ 閉合零參數質量公式（m₃=γ₆²A、m₁=(γ₄+Δcosπ/4)²A、m₂=(γ₄+Δcosπ/5)²A；
盲測 Δm² dev 0.44%/0.012%）、撤銷 Z₃/φ-power/φ^(1/8)（禁區）。
本次修正 O49 script 11 嘅 δ_CP（應 211.717° 非 72.6°）。**真剩餘 4 項**：束縛態機制、
「點解 1/L₉」、m_ββ 相位、Σm vs DESI（等數據）。詳見 `docs/02_closure_status.md`。
⚠️ **數據審核**：docs/01 原始 prompt 列 φ-power/Z₃/M_comp 3.93e13/ratio 0.637/0.880 全部係已否證歷史，勿引用。

## 檔案

| 檔案 | 描述 | 狀態 |
|:----|:-----|:----:|
| `01_problem_record.md` | 問題陳述 + 時序索引 + 審計註記 + §8 判決附註 | 🟡 |
| `docs/01_neutrino_mass_gap_prompt.md` | 質量譜 gap 分析 prompt（方向 A-F 候選） | 🟡 |
| `docs/02_closure_status.md` | 閉合鏈核對＋攻堅結果（11/11 獨立重算） | 🟢 |
| `scripts/01-05_*.py` | 五條探索路線（08-15 原創；審計後保留原狀） | 🔴/🟡 |
| `data/neutrino_p6_results.txt` | 05 最後輸出（校準＋Z₃） | 🟡 |

## 依賴

IDCM-v10.0 → K_Chain (γ_n) ＋ 12D WDVV d_tensor（`main_problems/p15_early_derivations/data/d_tensor_positive.npy`，需 symlink 先跑得）
→ CY₃(36,98) M_comp → 上游 O49（生成鏈）＋ O66（M_comp 第一性原理）＋ O123（δ_CP=211.717°）。

## 來源

- 原 `open_problems_fresh/neutrino_p6_mode/` 相關 scripts（2026-08-15）；遷 `main_problems/p6_neutrino/`（2026-10-20）
- ⚠️ 腳本內部路徑（`data/d_tensor_positive.npy`、`open_problems_fresh/neutrino_p6_results.txt`）未更新 — 內容修正待指示