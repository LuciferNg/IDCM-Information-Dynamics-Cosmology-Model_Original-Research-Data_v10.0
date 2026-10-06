# O234 — 質量公式檢驗方法反推: RG-invariant 質量比驗證協議 (FLAG/PDG 凍結觀測層)

<!-- registry
pid:     O234
title:   質量公式檢驗方法反推: RG-invariant 質量比驗證協議 (FLAG/PDG 凍結觀測層)
state:   registered
verdict: -
flags:   -
owner:   O234
created: 2026-10-06
updated: 2026-10-06
prereq:  O120, O233, O136, O137
source:  O233 C_f 無檢驗能力 → 驗證方法反推 (2026-10-06 調律者指示)
-->

> **狀態**: 🟠 **方案設計中 — 第一輪（凍結層 + 前向 z-score + 反推引擎）已交付 (2026-10-06)**
> **建立**: 2026-10-06
> **前置**: O120（C_f 商定義）、O233（C_f 身份 hunt 負閉合）、O136（純冪律障礙定理）、O137（模式集 + 參數屏障）
> **位置**: `open_problems_fresh/o234_mass_ratio_reverse_validation/`

---

## 〇、歸屬審計（合成型問題 fence — 2026-10-06）

**調律者命題**: 「C_f 冇檢驗能力；以檢驗方法反推質量公式（開 O234 檢驗方法）」。

| 準則 | 候選擁有者 | 裁定 |
|:--|:--|:--|
| ① C_f 定義 | **O120** — C_f = m_f/(M₀γ_n) 商定義 ⟹ γ_n·C_f ≡ m_f by construction | 擁有；O234 只引用其結論（by-construction ⟹ 零檢驗力） |
| ② C_f 身份 | **O233** — 生成器 hunt 5 線全負（結構池 p=0.9955）；P2 m_d/m_u = (γ₃C_d)/(γ₂C_u) = 2.1620 EXACT 已閉合（= PDG 中心值按定義） | 擁有；O234 承接「C_f 池不可作獨立預言源」 |
| ③ 純冪律障礙 | **O136** — docs/26 α_i ∈ [0.28, 11.87] 負相關 ⟹ m ∝ γ^α 不可能；比值需 C_f | 擁有；O234 引用為「兩層分離」依據 |
| ④ 模式集/參數屏障 | **O137** — R19 合法模式 {1,2,3,4,5,7,9,11,13}；docs/35 A₅ 0 參數 vs 需 8-9 ⟹ 形狀唔可以靠 A₅ 幾何閉合 | 擁有；O234 只引用合法模式集 |
| ⑤ 比值閉合層 | **O147** — κ 可加性 21/21 比閉合（後驗記號）；**O35** — 8/8 拍頻比 | 擁有「公式層比值」；O234 唔重推公式層 |
| ⑥ assignment 版本 | **O209**（|Δm| 序）vs **O137/O233**（γ 升序；已裁決 O137 正式授權 γ 升序） | O234 兩套並報（Assignment 版本隔離規則） |

**裁定**: 以上零件各有主，但「**用驗證方法（RG-invariant 比值 + FLAG/PDG 凍結觀測層）本身做約束源，反推質量公式結構**」整體無主 ⟹ 合成型問題，保留獨立 O，本表即 fence。O234 **唔重推**：C_f 生成器（O233）、純冪律（O136）、F_proj 幾何（O137）、κ 比閉合（O147）、拍頻比（O35）。

---

## 一、問題陳述

**IDCM 質量公式 m_f = M₀·γ_n·C_f 點樣先有檢驗能力？** 直接比較絕對質量無效：C_f 由 O120 商定義
C_f = m_f/(M₀γ_n) 反推 ⟹ γ_n·C_f ≡ m_f **恆等成立，by-construction，零信息量**（O233 P2「2.1620 EXACT」
即係 PDG 中心值 4.67/2.16 按定義還原，唔係預言）。O233 生成器 hunt 負閉合（C_f 8 值無算子身份，
p=0.9955）⟹ C_f 池唔可以做獨立預言源。

**新方法（調律者指示）**: 反向——**先凍結有檢驗能力嘅觀測量（RG-invariant / 同 scheme 同標度質量比，
FLAG 2024 + PDG 2024），由觀測比值反解「任何公式必須滿足嘅 (n, C) 約束」，再檢查鏈譜 γ 家族可否
唯一供給**。即係「檢驗方法本身做約束源」。凍結層之後：前向 z-score 矩陣 → 反推約束 → 唯一性 +
密度/MC null → LOOCV 盲測。

**核心判準（本 O 第一輪已實測）**: 質量比可分三類——
- **γ 主導**（純鏈譜已可測，C_f 修正非必須）: u/d 純 γ₃/γ₂ = 2.2452 vs FLAG 2.151(11) = **0.85σ** ✅
- **C_f 主導**（未經 C_f 生成器閉合 ⟹ 今日不可檢驗）: c/s 純 γ 3.02 vs 11.85(16) = **55σ** ❌
- **無模式對應**（s/m̂ 等平均量）: 只可做池密度掃描（診斷性，nominal）

---

## 二、已確立嘅結構

```
🟢 C_f 定義 by-construction（O120）: C_f = m_f/(M₀γ_n) ⟹ 任何 γ_nC_f 回復質量 = 恆等式, 0 檢驗力
🟢 C_f 無算子身份（O233 docs/19）: 結構池 p=0.9955 / 統一式 dip / 塊參數 0.38 / κ 1.0 / 擴池 0.285
🟢 兩層分離（O136 docs/26）: 純冪律 m∝γ^α 不可能（α_i 跨 42.6×）; 質量問題只有一個障礙: 形狀（比值）
🟢 參數屏障（O137 docs/35）: A₅ 幾何供給 0 參數 vs 數據需 ≥8-9 ⟹ 形狀唔可以靠 A₅ 幾何閉合
🟢 A_γ assignment（O137 R22 正式授權, O233 裁定收錄）: {e:1, u:2, d:3, s:4, μ:5, c:7, τ:9, b:11, t:13}
    驗證: 由模式重構 C_f = m_f/(M₀γ_n) = {3.594, 3.803, 3.662, 41.32, 30.03, 186.06, 159.64, 255.75} ✅ 全對
🟢 FLAG 2024 凍結觀測層（Nf=2+1+1, 主）: ms/m̂ = 27.227(81) @0.3%; m̂ = 3.427(51) MeV; m_u/m_d = 0.465(24)
    → m_d/m_u = 2.1505(111); RGI M̂ = 4.768(71+46) MeV, M_s = 130.0(0.8+1.3) MeV
🟢 RGI 味盲自洽（本 O scripts/01 CHK3）: M_RGI_ud/m̂ = 1.3913 ≈ M_RGI_s/m_s = 1.3909（0.03%）
    ⟹ 比值喺純 QCD 內係 scheme/標度無關（檢驗方法嘅理論基礎 = FLAG (28)-(30)）
🟢 前向判別力（本 O scripts/01 CHK5）: u/d 純 γ 0.85σ ✅（γ 主導, 可檢驗）; c/s 55σ ❌, b/c 15.7σ ❌
    （C_f 主導, 未可檢驗）; t/b 純 γ 1.37 vs 41 → VEV 扇區（O233）
🟢 assignment 判別力（本 O scripts/01 CHK6）: A_Δm（O209 |Δm| 序）u/d 預言 γ₉/γ₁₁ = 0.68 < 1 →
    對觀測 2.1505 = 13.2σ 反向 ⟹ γ 階梯方向判死 A_Δm（u/d 子項）
🔴 Gemini 提案「FLAG ratio_md_mu = (2.14, 0.07)」審計（scripts/01 CHK4）: central 同 FLAG 一致
    （z=-0.09 vs 2+1+1; z=+0.97 vs 2+1）✅; 但誤差棒 0.07 vs FLAG 傳播 0.111 報細 37% ❌; P2=2.1620
    用 FLAG 真誤差 z=0.10 —— 喺 1σ 內但係 by-construction 恆等值, 無獨立信息
🟢 b/c 所需 C 比近命中（scripts/02 S1a, nominal）: C_b/C_c = 1.3746 vs 44/33 = 1.3333 dev 3.0%,
    池成員涉 look-elsewhere（O233 R20 先例）⟹ 維持 nominal, 唔入 PASS 計數
🟢 C-shape 完全釘死（round 2, scripts/03 B1）: shape DOF = 0（8 C − 6 約束 − 2 扇區標度）;
    反解 u=1 d=0.958 s=10.78 c=41.59 b=57.16（夸克 anchor=1）; e=1 μ=8.36 τ=44.42（輕子 anchor=1）
🟢 檢驗能力清單（scripts/03 C1）: 9 比 = 1 γ-testable（d/u 0.85σ）+ 7 C-dominated + 1 mode-gap（s/m̂）
🟢 不可證偽性定理（scripts/04 A1）: M={m=M₀γC, C∈ℝ⁺} 對 C-dominated 比 P(mismatch)=0
🟢 LOOCV（scripts/04 B1）: redundancy = 0（6 約束全部必要）; out-of-sample = 凍結層 v2+ 新量度
    （1% 精度 ms/mu = 唯一非 assignment 內含測試）
🟢 s/m̂ 模式閘負面（scripts/04 C1）: 算術/幾何/半整數/調和中點全敗（C 放大 9.5-11× ⟹ mode-gap 真）
🟢 混標度更正通知（docs/02 §六）: C_c/C_s 同 scheme 3.86 vs O233 池隱含 4.50（15%, m_c(m_c) vs
    m_s(2GeV)）; O233 正結果（質量 rank 次序）不受影响; O209 Id(f) watch（register handoff 已發）
🟡 凍結層 v1.1 內部張力: m_c/m_s 11.85(16) vs 11.652(65) z=+1.15（freeze v2 決策點）
🔴 s/m̂ 池掃描（scripts/02 §3, 診斷性）: F₁₀/2 = 27.5 vs 27.227(81) = +1.0% = 3.3σ 未命中; 其他池值亦無
    1σ 內命中 ⟹ 0.3% 精度下有牙
```

## 三、未確立（🔴 開放問題）

```
🔴 → ✅ (round 2, scripts/03 B1) 反推約束完整解集: shape DOF = 0; 解集 = 唯一 C-shape
    （up to 2 扇區標度）
🔴 → ✅ (round 2, scripts/04 A1) C_f 主導比檢驗能力: 模型類 {m=M₀γC, C∈ℝ⁺} 不可證偽;
    9 比中 8 個 C-dominated/mode-gap
🔴 → ✅ (round 2, scripts/04 C1) s/m̂ 模式對應: 4 個幾何中點候選全敗 ⟹ mode-gap 真缺口
🔴 → ✅ (round 2, scripts/04 B1) LOOCV: redundancy=0; 真 out-of-sample = 凍結層 v2+ 新量度
🔴 → 🟡 重夸克 scheme 轉換: 主用 FLAG Nf=4 m_c/m_s = 11.652(65) 繞過混標度; 4-loop RGE 實作
    係 freeze v2 可選項
🟡 凍結層 v1.1 內部張力: m_c/m_s 兩值 z = +1.15（freeze v2 決策點）
🔴 RGI_b 入凍結層: FLAG §4.3 完整讀 + m_b(RGI)/m_s(RGI) 做第四條夸克約束（redundancy 0 → 1）
🔴 1% 精度 m_s/m_u 未來量度: 唯一非 assignment 內含嘅 out-of-sample 測試
```

## 四、攻擊路線

```
1. 凍結觀測層（✅ 已交付 scripts/01 + data/01）: FLAG 2024 Nf=2+1+1 為主, Nf=2+1/PDG 為輔;
   只准用 ratio/RGI 量; JSON + sha256 承諾
2. 前向 z-score 矩陣（✅ 已交付 scripts/01 CHK5-6）: 兩套 assignment 並報; γ 主導 vs C_f 主導分類
3. 反推約束 + 唯一性（scripts/02 §1-2）: 由觀測比解 (n,C) 約束; 解集大小/密度 null（枚舉 72
   γ 比 + MC 10⁶ 對照）——成本低
4. C_f 主導比嘅可證偽性定理（scripts/02 §4 方向）: 若 C_f 無生成器, 證明該類比結構上不可檢驗
5. LOOCV 盲測: 凍結層內留一, 由餘者反推預言留一——期望命中數; 升級閘 = pre-registered null
```

## 五、驗證標準

```
✅ 前向 z-score 矩陣完整: 兩 assignment × 全部可得 ratio, 每個標 scheme 標籤
✅ 每類比判別力表: γ 主導（|z|<2）/ C_f 主導（|z|>5）/ scheme 不可比（標 WARNING）
✅ 反推解集: 凍結 ratio ⟹ (n,C) 約束解集明確（非空或空 + 形式證明）
✅ 唯一性 + 密度: 解集大小 vs 枚舉/MC null 期望; 命中優於 5σ
✅ 一律過四道硬測試: ①自由度成本(零參數) ②MC null(10⁶-10⁷) ③樣本外盲測(LOOCV) ④結構剛性
```

## 六、推導時序索引

> ⚠️ **只可 append 新行，禁回溯污染舊行。**

| # | 日期 | 事件 | 產物 |
|:-:|:-----|:-----|:-----|
| 1 | 2026-10-06 | 註冊（O233 C_f 無檢驗能力 → 驗證方法反推, 調律者指示） | scaffold |
| 2 | 2026-10-06 | 歸屬審計 6 項（全部已有主, 合成型保留, fence 建立） | 本檔 §〇 |
| 3 | 2026-10-06 | 凍結觀測層 + RGI 自洽 + Gemini claim 審計 + 前向 z-score | scripts/01, data/01 |
| 4 | 2026-10-06 | 反推引擎: C 約束解集 + 枚舉密度 null + s/m̂ 池掃描 + P2 循環證明 | scripts/02, data/02 |
| 5 | 2026-10-06 | Round2: 凍結層導出比 + DOF 審計（shape DOF=0）+ 檢驗能力清單（1/9 γ-testable） | scripts/03, data/03, docs/02 |
| 6 | 2026-10-06 | Round2: 不可證偽性定理 + LOOCV redundancy=0 + s/m̂ 閘負面 + 混標度通知 | scripts/04, docs/02 |

## 七、相關文件

```
- O120 — C_f 定義（商定義 ⟹ by-construction, 引用其結論）
- O233 — C_f 身份 hunt 負閉合 + P2（本 O 承接其「不可檢驗」結論）
- O136 — 純冪律障礙定理（docs/26）+ 最終裁定（docs/13, m_d/m_u 2.1620 vs 2.1290 = +1.53%）
- O137 — 合法模式集 + 參數屏障（docs/35）+ A_γ 正式授權（R22）
- O147 / O35 — 公式層比值閉合（唔重推）
- O209 — |Δm| assignment（兩套並報來源）
```