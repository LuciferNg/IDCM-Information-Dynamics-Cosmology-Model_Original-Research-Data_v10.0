# O143 驗證報告 — 推導內容獨立核對 (2026-09-19)

> 觸發: 用戶「繼續O143, 先讀取所有O143檔案, 驗證推導內容」
> 方法: 重跑全部 scripts (/usr/bin/python3) + 獨立重建關鍵量
> 結果: 重跑一致 (data 無漂移); 發現 3 個代碼/推導問題 + 1 個跨目錄 stale 狀態

---

## A. 重跑驗證 (exit 0, 與存檔一致)

| script | 結果 | 對比存檔 |
|:-------|:-----|:---------|
| 01_step1_projection.py | Σγ_even=90, Σγ_odd=88, 61.5/28.5, 41/60, 19/60 ✅ | ✅ 一致 |
| 02_step2_tpipe_eigen.py | λ_m dev 1.67e-15, vac 0.985021 | ✅ 一致 |
| 03_step3_induced_phase.py | 7/60 正交, 24/60 波腹, ΔE=0 5/12 | ✅ 一致 |

重跑結果與 data/*.json 完全一致 — 檔案無漂移。NN_results.md 嘅 🔴 判據標記 (48/60→7/60) 係誠實記錄。

---

## B. 發現嘅問題 (按嚴重度)

### B1 🔴 Step 2「基態 (m=0)」標籤錯位 — θ_0^(0)=135° 唔係所聲稱嘅量

`scripts/02` 用 `np.argsort(eigvals)` 升序排序後, 取 index 0 當「基態 (m=0)」。
但升序 index 0 對應 eigenvalue **-2.0 = Nyquist m=44 模式**, 唔係 m=0 uniform mode
(λ=+2 喺 index 87)。獨立驗證:

```
eigvals_sorted[0] = -2.0  → theory m = 44 (Nyquist)
eigvecs[:,0] = (+1,-1,+1,-1,...)/√88  (alternating)
sum even = -4.69, sum odd = +4.69 → arctan2 = 135.00°
真正 m=0 (uniform, index 87): arctan2 = 45.00°
```

即 θ_0^(0)=135° 係 **Nyquist 交替向量嘅奇偶和比**, 唔係「基態相位」。
更深層問題: theta_0 = arctan2(Σ奇, Σ偶) 依賴 np.linalg.eigh 嘅特徵向量 sign convention —
全域 sign flip 後同一模式變 **-45°** (315°)。因此 135° 唔係譜不變量,
「拓撲相角 θ_0^(0)=135.00° ✅ 由奇偶不對稱性(88/90)鎖定」**冇計算支持**:
arctan2(奇偶和) 公式完全冇用 γ 權重, 同 88/90 無關。

### B2 🔴 Step 2 gamma_even/gamma_odd 標籤與 Step 1 / O34 相反

- Step 1 (正確, 同 O34): `gamma_even = gamma_k[1,3,...,87]` = k=2,4,...,88 (世界, Σ=90); `gamma_odd = gamma_k[0,2,...,86]` = k=1,3,...,87 (觀察者, Σ=88)
- Step 2 code: `gamma_even = gamma_k[::2]` (實際 = 觀察者 88), `gamma_odd = gamma_k[1::2]` (實際 = 世界 90) — **標籤互換**

影響:
- Step 2 打印「偶數 (世界) 能量 = 0.503773」實際係觀察者模式權重平方和
- 「vac_odd/vac_even = 0.985 vs 理論 88/90 = 0.9778, 0.7% 偏差」係**循環論證**:
  對比嘅量唔同 — vac ratio = Σγ²/Σγ² (1.0152 或倒數), 而 88/90 係 Σγ/Σγ 比。真正 Σγ² 比 = 1.0303。

### B3 🔴 Step 3 `node9_in_unproj` key/value 錯位

`scripts/03` line 221: `'node9_in_unproj': bool(node9_idx in proj_idx)` — key 名話「unproj」
但實際 check `proj_idx`。JSON 存 `true` 實質 = node9 ∈ 投影(低緯)組。
同一 script 嘅 print 顯示 node0、node9 **都唔喺**未被投影組 (False),
同 script 意圖 comment「確保 node0 (冷斑) 喺未被投影組」矛盾。

即 41/19 緯度分區將冷斑兩節點都歸入「投影/物質」組 — 分區敘事本身未兌現。

### B4 🔴 CSG-v2「16 約束=唯一解」已被 O144 判定為選擇效應 — README stale

README line 61 仍寫:「CSG-v2 閉合 (O143): X=P_f(E_{n,0}+E_{0,n})/2, ⟨Ω⁻,X⟩=γ_nP_f,
16 約束=16 自由度 → 唯一解, LOOCV 8/8 PASS Δ≤2%」標 🟡 部分閉合。

但 O144 docs/06 (2026-09-17) 被迫性測試判決:
- 同一套形式機制能「唯一導出」**311 個不同網格** — 真網格 = 1/311
- 有效自由度 = 18.6 bits 選擇 (共享模式 6.6 + 對偶集 5.4 + R 6.6)
- LOOCV 8/8 係 value-blind (值盲測), **非 form-blind**; 0 out-of-sample 預言
- 「挑邊三條約束」本身係自由度 (存在兩條不同三約束路徑: 1 解 vs 6 解)

⟹ README O143 行嘅「唯一解」宣稱已失效, 需要降級/附註 (見 D)。
CSG-v2 閉合 docs 位於外置專案 `/home/wsl/Projects/ChronologicalStringSpectralGeometry-v2/docs/02,03`,
唔喺 O143 目錄內 — O143 目錄內並無任何文件記錄該閉合。

### B5 🟡 檔案結構缺口

- `docs/` 空目錄 — 01_problem_record 檔案樹列出 `docs/01_derivation_plan.md`, 從未建立
- 檔案樹列出 `scripts/04_step4_differentiation.py`, 不存在
- 無 SESSION_START.md、無 final_result.md (O-series 四件套不齊)
- 整個目錄 git untracked (從未 commit) — 無 git 歷史可做時序比對

---

## C. 判定標準複核 (01_problem_record §判定標準)

| 標準 | 要求 | 實測 | 狀態 |
|:-----|:-----|:-----|:----:|
| θ_i^ind 由幾何唯一決定, 零自由參數 | 全部 60 | longitude 高斯窗口 + latitude 排序分區 (ad hoc) | 🔴 |
| 48/60 節點正交 | ≈π/2 | 7/60 | 🔴 |
| node0/node9 波腹 | |cos|>0.8 | node0 151°/node9 145°, |cos| 0.88/0.82 | ✅ 定性 |
| ΔE=0 12 節點正交 | 12/12 | 5/12 | 🔴 |
| node0 T 預測 | -134.2 μK | -117.5 μK (12%) | 🟡 形狀近, 幅度歸一化循環 |

---

## D. 同步修正 (本輪已執行)

1. `01_problem_record.md` 末尾加「驗證附註 (2026-09-19)」+ 時序索引 (本文件摘要)
2. `scripts/04_verify_derivation.py` + `scripts/05_verify_gamma_labels.py` — 獨立驗證腳本 (本報告 B1-B3 證據)
3. README O143 行: CSG-v2「唯一解」宣稱加 O144 否定附註, 狀態 🟡→🔴 (開放)

## E. 未修正 (需上游 session / 用戶指示)

- `scripts/02` 同 `scripts/03` 嘅代碼 bug 本身未改 — 原始推導按「修正附註協議」保留,
  如需修正代碼需用戶明示 (或於 O143 下一步攻堅時重寫)
- CSG-v2 外置專案 docs/02,03 未改 (唔喺 O143 目錄範圍內; 應由 CSG-v2 自己標註 O144 否定)
- O152 (R11「16 = γ₄₄² 約束 (O143 唯一解)」) / O147 (O143 grid 引用) 交叉引用未同步 —
  若「唯一解」失效, 呢啲依賴需各自加附註

---

## 時序索引 (O143)

| # | 日期 | 文檔/事件 | 內容 | 驗證 |
|:-:|:-----|:---------|:-----|:----:|
| 1 | 2026-08-31 | 01_problem_record.md | 4 步算子化框架建立 (𝒫/T_pipe/θ_i^ind/分化) | — |
| 2 | 2026-08-31 | scripts/01-03 + data | 初始推導 + 存檔 | ✅ 重跑一致 |
| 3 | 2026-08-31 | NN_results.md | 判據: 7/60 正交, 24/60 波腹, 5/12 ΔE=0 🔴 | ✅ 誠實 |
| 4 | 2026-09-04 | CSG-v2 docs/02,03 (外置) | X=P_f(E_{n,0}+E_{0,n})/2, 16 約束=16 自由度→唯一解, LOOCV 8/8 | ⚠️ 見 #6 |
| 5 | 2026-09-17 | O144 docs/05,06 | 譜語法審計: 144 解; 被迫性: 311 網格, 1/311, 18.6 bits → 選擇效應 | ❌ 否定 #4 |
| 6 | 2026-09-19 | 本報告 (docs/01_verification_notes.md) | 重跑一致; B1-B3 代碼問題; README stale 同步 | ✅ |

時序完整性聲明: 本報告為驗證附註, 無改動任何原始推導內容; 原始 scripts/JSON 保留原樣。
