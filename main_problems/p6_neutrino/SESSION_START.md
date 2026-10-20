# P6_neutrino — SESSION START（中微子質量譜）

**會話起點：** 2026-10-20（結構重組＋全量審計）

---

## 1. 本 session 已完成（2026-10-20）

- **結構重組**：7 檔搬入 `scripts/`（01-05 編號）＋ `docs/` ＋ `data/`；新增 `01_problem_record.md`＋`README.md`。
- **全量審計**：5 個 scripts 隔離重跑（exit=0）＋獨立高精度複算，全部發現記錄喺 `01_problem_record.md` §4。

## 2. 審計結論（未閉合 🟡）

| script | 路線 | 結果 |
|:-------|:-----|:-----|
| `01_..._derivation.py` | 12D eigenvalue + V_cycle | 🔴 §8 變數洩漏；質量超 PDG 上限 |
| `02_..._kchain_harmonic.py` | γ_n 冪次/beat | ❌ 全法 fail（10⁵ eV） |
| `03_..._geometric_seesaw.py` | (γ·v)²/M_Pl | 🔴 Δm² 單位混用；偏 10 個數量級 |
| `04_..._compactification.py` | M_comp 幾何掃描 | 🔴 聲稱 0.043 實 4.3e-5（1000×） |
| `05_..._dm2_calibration.py` | M_comp 校準 + Z₃ | 🟡 校準＋後驗；唔過四硬測 |

## 3. 交接事項（下一 session 起點）

1. **唔好重推已否證路線**：γ_n 線性/二次/beat（02）、(γ_n·v)²/M_Pl（03）、V_cycle 法（01）→ 全部標 🟡/🔴。
2. **05 嘅校準唔算閉合**：Δ31 ratio 1.0 係恆等（由 PDG 反推 M_comp）；Z₃=3² 係後驗凑合（raw ratio 8.99→÷9）。禁引用為「閉合」。
3. **M_comp −6.14% 缺口**（結構 3.9325e13 vs 校準 3.6909e13）→ 需結構解釋，禁校準補貼。
4. **真攻堅方向**：零參數質量公式（候選見 `docs/01_..._gap_prompt.md` 方向 A-F；全部未驗證）。
5. **腳本路徑待修正**：scripts 內 `data/d_tensor_positive.npy`（實際喺 `main_problems/p15_early_derivations/data/`）同 output 路徑 `open_problems_fresh/...`（現結構無效）——審計用 symlink 跑，內容未改（待指示）。
6. **Register**：`neutrino_p6_mode` merge → `P6`（ref 翻譯層已修，check PASS）；後續 register 用 `P6`。
7. **Σm 目標更新**：DESI/Planck24 上限 <0.072 eV（05 預測 0.0962 已超）——Planck18 <0.12 唔再夠。
8. **四硬測**：任何新閉合主張要過 ①零參數 ②MC null ③樣本外盲測 ④結構剛性，先盲測後揭曉。

## 4. 依賴

- d_tensor：`main_problems/p15_early_derivations/data/d_tensor_positive.npy`（12×12×12）
- CY₃：h¹¹=36, h²¹=98；M_comp = M_Pl/(2·h¹¹·h²¹·N_d)
- 上游中性：O49/O66/O71/O136/neutrino（n=6 來源）、O187 中微子扇區適用域（已判明帶電 A₅ 保護模式）

---

*只加註，未改本 O 其他檔案（01_problem_record.md / docs / scripts / data）*