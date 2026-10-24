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
3. **M_comp −6.14% 缺口**（結構 3.9325e13 vs 校準 3.6909e13）→ **已閉合**：正確結構值 = O66 3.6890e13（M_pl·10^-(1/γ₆−1/76)）；3.9325e13 係錯候選 [B]。
4. **真攻堅方向**：上游 O49/O66 已閉合零參數質量公式——**唔好再從頭推**，直接沿用生成鏈（m₃=γ₆²A、m₁=(γ₄+Δcosπ/4)²A、m₂=(γ₄+Δcosπ/5)²A），盲測 Δm² 0.44%/0.012%。
5. **腳本路徑待修正**：scripts 內 `data/d_tensor_positive.npy`（實際喺 `main_problems/p15_early_derivations/data/`）同 output 路徑 `open_problems_fresh/...`（現結構無效）——審計用 symlink 跑，內容未改（待指示）。
6. **Register**：`neutrino_p6_mode` merge → `P6`（ref 翻譯層已修，check PASS）；後續 register 用 `P6`。
7. **Σm 目標更新**：DESI/Planck24 上限 <0.072 eV（05 預測 0.0962 已超）——Planck18 <0.12 唔再夠。
8. **四硬測**：任何新閉合主張要過 ①零參數 ②MC null ③樣本外盲測 ④結構剛性，先盲測後揭曉。

## 4. 2026-10-20 攻堅後交接更新（append-only，docs/02-07）

> 上游閉合 + 本次推盡後，P6 核心已閉合。真剩餘 4 項，全部有明確出路：

- ✅ **質量譜閉合**：m₁/m₂/m₃ 生成鏈（docs/02, O49/O66）——改用呢套，唔好再用 scripts/01-05。
- ✅ **束縛態機制**（docs/04+05）：角 = O179 hop 干涉核 hop=1（N=8=2B、N=10=2F₅）；t=Δ/2 鎖死（結構剛性 ±5% → dev 8.8%）。
- ✅ **身份精修**（docs/06）：Δ 嘅 9 = n₄+n₅（非 N_gen²）；76 = 88−hop_max；hop 階梯和 = |A₅|=60；Σγ_odd=Σγ_even=88。
- 🟡 **剩餘 #1**：束縛態 hop 強度 t=Δ/2 嘅「9 入 hop」機制（需 hop 層動力學；新 O 建議）。
- 🔴 **剩餘 #2**：M_comp 1/76 修正嘅 log10 機制（身份三層齊：L₉/hop_max/Σγ；Chebyshev 譜積唔湧現 76——需 log↔譜積映射；新 O 建議）。
- 🟡 **剩餘 #3**：m_ββ Majorana 相位（[6.108, 22.169] meV 帶；(π,π) 全相消已 CP 守恆；相位結構需 dim-5 算符相位理論）。
- 🟡 **剩餘 #4**：Σm=0.09714 vs DESI<0.072（模型依賴；等 DESI LRG/ELG + KATRIN/LEGEND）。
- ⚠️ O49 docs/03「EXACT」聲稱唔成立（75/64 dev 0.097%、16/105 dev 0.094%）——後續引用用生成鏈，唔用 operator 比。

### 階段性 closeout（2026-10-20，docs/10）

- ✅ **#1 hop 強度 t=Δ/2 閉合**（docs/09）：gaplessness（帶頂 γ₄+2t=γ₅）唯一決定；充分 Hamiltonian 留新 O。
- 🔴 兩條機制路否定（docs/08）：Feshbach 極點 0 命中；譜積身份搜尋冇 1/76。
- ✅ 第 2 輪審計：scripts/09_audit_docs04_09.py **32/32 PASS**（docs/04-09 全核）；scripts/06-08 重跑 exit=0 一致。
- 🟡 剩餘 3 項：#2 1/76 log10 機制（🔴）、#3 m_ββ 相位（🟡）、#4 Σm vs DESI（🟡 等數據）。

### 全量審計＋v_SM 錨統一（2026-10-21，docs/11+12）

- 🔴 **發現**：scripts/01-05 一直跑唔到（FileNotFoundError，舊審核靠 symlink 冇真執行）——按調律者授權「改script」修正 8 處路徑（讀 d_tensor→p15、寫出→data/），公式零改；重跑 01-09 全部 exit=0，09=32/32 PASS；data md5=HEAD 冇漂移。
- 🟢 **docs/02 閉合鏈 11/11 重現**（v=246.0 版）；docs/03 O49 指正表 6/6 重現；m_ββ 帶用 O65 PMNS 完全重現 [6.1077, 22.1692] meV。
- ⚠️ **v 錨統一（調律者裁定：v_SM=246.2196）**：A=1.64337、m₁=0.020945、m₂=0.022685、m₃=0.0536815、Σm=0.0973116 eV；Δm² dev 0.44%→**0.80%**、0.012%→**0.37%**（仍 <1% 過閘）；scripts/03/04/05/09 已改重跑（09 仍 32/32）；docs/02/05/07/10 舊數字以 docs/12 附註為準。

## 5. 依賴

- d_tensor：`main_problems/p15_early_derivations/data/d_tensor_positive.npy`（12×12×12）
- CY₃：h¹¹=36, h²¹=98；M_comp = M_Pl × 10^-(1/γ₆−1/76)（O66, 3.6890e13 GeV —— ⚠️ 唔係 M_Pl/(2·h¹¹·h²¹·N_d) 3.9325e13，嗰個係錯候選 [B]）
- 上游中性：O49/O66/O71/O136/neutrino（n=6 來源）、O187 中微子扇區適用域（已判明帶電 A₅ 保護模式）

---

*只加註，未改本 O 其他檔案（01_problem_record.md / docs / scripts / data）*
### handoff 落地（2026-10-24，append-only）

- ✅ **O257 → P6**（2026-10-21 發還）已落：**#2 1/76 log10 機制 = falsified**；**M_comp 0.051% 閉合 → 量級閉合 ~3%**（M_cal 係 05 PDG 反推 ⟹ 三重 fit 循環）；保留 1/γ₆ 主項 + 88³/2 大數 EXACT。
- ✅ **M4 → P6**（2026-10-24 發還）已落：**A 譜身份（1.64337 eV/γ²）negative**——13104 組合 0 命中 <0.1%，密度 5.21% 唔可辨識；需 σ 橋（O142）或 Λ_eff（O86）通道。A 身份維持 🔴 開放。
- 落地位置：record §12、docs/02 §8、docs/07 §7；剩餘項：#2 判死、#3 m_ββ 🟡、#4 Σm 🟡、（新）A 身份 🔴。
