# O234 SESSION_START — 質量公式檢驗方法反推: RG-invariant 質量比驗證協議 (FLAG/PDG 凍結觀測層)

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

> **Session**: 2026-10-06（新建立）
> **狀態**: 🟠 **方案設計中 — 第一輪已交付（凍結層 + 前向 z-score + 反推引擎 v1）**
> **來源**: O233 C_f hunt（調律者: 「剛才的C_f, 並沒有檢驗能力」→「以檢驗方法來反推」→「開新資料夾 O234 來檢驗方法」）
> **前置**: O120, O233, O136, O137
> **位置**: `open_problems_fresh/o234_mass_ratio_reverse_validation/`

---

## 〇、調律者目標（原文引用 2026-10-06）

> 「我在想，從另一估角度反向從驗證方法回推IDCM的質量公式，剛才的C_f, 並沒有檢驗能力，
> 但如果以檢驗方法來反推可能可以？可以開新資料夾 O234 來檢驗方法」

**拆解**:
- 0. 診斷事實: O233 P2「m_d/m_u = (γ₃C_d)/(γ₂C_u) = 2.1620 EXACT」冇檢驗能力（C_f = m_f/(M₀γ_n)
  商定義 ⟹ 恆等還原, by-construction; O233 生成器 hunt 已負閉合 p=0.9955）
- 1. 方法: 反向——由**有檢驗能力嘅驗證方法**（RG-invariant 質量比 + FLAG/PDG 凍結觀測層）做約束源,
  反推質量公式結構（n, C 約束 → 唯一性 → 盲測）
- 2. 執行: 開 O234 = 檢驗方法本身嘅開發與驗證

## 一、接手起點

**第一輪交付（本 session）**:
1. 歸屬審計 6 項（01_problem_record §〇）+ 合成型 fence
2. `scripts/01_frozen_observation_layer.py` — 凍結觀測層 JSON + sha256 + 3 項自洽檢查 + Gemini claim 審計 + 前向 z-score 矩陣（兩 assignment）
3. `scripts/02_ratio_constraint_reverse.py` — 反推 (n,C) 約束 + 枚舉密度 null + s/m̂ 池掃描 + P2 循環證明
4. 核心結論（已寫入 01_problem_record §二）:
   - u/d 純 γ = 2.2452 vs FLAG 2.1505(111) = **0.85σ** ⟹ γ 主導、鏈譜可檢驗, 唔需要 C_f 修正
   - c/s 純 γ 3.02 vs 11.85(16) = 55σ ⟹ C_f 主導、今日不可檢驗
   - assignment 判別: A_Δm 對 u/d 方向 13.2σ 反向 ⟹ γ 升序 A_γ 係唯一方向正確

## 二、先做嘅第一步（下一 session）

```bash
1. 睇 scripts/01 + scripts/02 輸出（logs/data 02）確認數字
2. 攻 01_problem_record §三 🔴 一: 反推約束完整解集 —— 凍結 ratio 各 1σ 帶 → (n,C) 解集大小 + 密度
3. 攻 🔴 LOOCV: 留一 ratio, 由餘者反推預言留一（pre-registered）
4. 若解集非空 → 唯一性 + MC 10⁶ null; 升級閘 = 四道硬測試
```

## 三、已知陷阱

```
⚠️ C_f 池（3.6/13/15.5/33/37/44 或 O233 8 值）全部係 by-construction 或後驗 —— 唔可以當獨立預言源;
   任何「γ×C_f 命中觀測」= 恆等式, 唔入 PASS 計數
⚠️ FLAG m_u/m_d 有內部張力（RM123 17 vs MILC 18 = 2.2σ, FLAG 2024 p.19）——u/d 比 5% 誤差,
   單點「命中」零判別力; 判別力喺 ms/m̂（0.3%）同 c/s（1.4%）
⚠️ m_c(m_c)/m_s(2GeV) = 13.6 vs m_c/m_s 同 scheme = 11.85: 唔同 scheme/標度直接比較 = 錯（跑動效應
   係 10% 級）——凍結層只准用 FLAG 提供嘅同 scheme 值
⚠️ 池掃描命中 = nominal（look-elsewhere 未校正）——例 F₁₀/2 = 27.5 vs 27.227(81) = 3.3σ 已報為未命中;
   「55 係池成員」= O233 R20 已殺（max-hits MC P=0.80）
⚠️ A_γ vs A_Δm 兩套並報（Assignment 版本隔離）; 用 O137 R22 正式授權 A_γ 做主, A_Δm 做判別
⚠️ /usr/bin/python3 執行（numpy/mpmath 不一定有; scripts 01/02 只用 stdlib）
```

## 四、關鍵數字（凍結觀測層 — 全部入 data/01_frozen_observations.json）

| 量 | 值 | scheme/標度 | 出處 |
|:---|:---|:-----|:-----|
| m̂ = m_ud | 3.427(51) MeV | MSbar 2 GeV, Nf=2+1+1 | FLAG 2024 (34) |
| m_s | 93.46(58) MeV | MSbar 2 GeV, Nf=2+1+1 | FLAG 2024 (34) |
| m_s/m̂ | 27.227(81) @0.3% | ratio（RG 無關） | FLAG 2024 (37) |
| M_RGI_ud | 4.768(71)(46) MeV | RGI, Nf=4 | FLAG 2024 (35) |
| M_RGI_s | 130.0(0.8)(1.3) MeV | RGI, Nf=4 | FLAG 2024 (35) |
| m_u/m_d | 0.465(24) / 0.485(19) | Nf=2+1+1 / 2+1 | FLAG 2024 (Tab.10) |
| m_d/m_u（導出） | 2.1505(111) / 2.0619(81) | 倒數 | 本 O 導出 |
| m_u, m_d（PDG） | 2.16(49) / 4.67(48) MeV | MSbar 2 GeV | PDG 2024 |
| m_c/m_s | 11.85(16) | Nf=4 組合 | FLAG 2024 Tab.8 ⊕ |
| m_c(m_c) / m_b(m_b) | 1.27(2) / 4.18 GeV | MSbar 自己標度 | PDG 2024 |
| m_t (pole) | 172.57(29) GeV | pole（renormalon 注意） | PDG 2024 |

## 五、交接 / 依賴

```
- 前置: O120（C_f 定義 by-construction）→ O233（C_f 身份負閉合 + P2）→ O136（兩層分離）→ O137（模式集/A_γ）
- 移交出: （暫無; C_f 主導比嘅「結構上不可檢驗」定理若證成 → O233/O209 需要知）
- 範圍警告: 唔重推 C_f 生成器（O233）; 唔重推公式層比值（O147/O35）; 唔做 F_proj 幾何（O137）;
  唔做 PDG 絕對質量閉合（O209）; 只做「檢驗方法 + 反推約束 + 盲測」層
```

---

> ⚠️ **本檔係起手式快照，唔係狀態權威。**
> 當前狀態以 `open_problems_fresh/README.md` 為準；生命週期事件以 `problem_register/` 為準。

---

## 六、append 2026-10-06（第二輪：DOF 審計 + 檢驗能力 + 不可證偽性）

- **scripts/03（3 PASS / 0 FAIL）+ scripts/04（4 PASS / 0 FAIL）**; docs/02 全記錄
- ★ shape DOF = 0: 8 個 C − 6 個獨立 ratio 約束 − 2 個扇區標度 ⟹ C-shape 完全釘死
  （u=1, d=0.958, s=10.78, c=41.59, b=57.16; e=1, μ=8.36, τ=44.42）
- ★ 檢驗能力清單: 9 比中只有 d/u 係 γ-testable（0.85σ）; 7 C-dominated; 1 mode-gap（s/m̂）
- ★ 不可證偽性定理: M={m=M₀γC, C∈ℝ⁺} 對 C 主導比 P(mismatch)=0（形式閉合 round-2 四大 🔴）
- ★ s/m̂ 模式閘: 4 個幾何中點候選全敗（C 放大 9.5-11×）⟹ mode-gap 真
- ★ 混標度通知: 凍結層 C_c/C_s = 3.86 vs O233 池 4.50（15%）——m_c(m_c) vs m_s(2GeV); rank 結構不受影响; O209 handoff 已發
- 🟡 freeze v2 待辦: RGI_b 入層; m_c/m_s 兩值決策; +1% m_s/m_u 未來量度 = killer out-of-sample

## 七、append 2026-10-07（第三輪：freeze v2 完成）

- **scripts/05（4 PASS / 0 FAIL）**; docs/03 全記錄; 凍結層 v1.1 → v2（v1 data 保留唔改）
- ★ **b/c「near-hit」死亡**: 混標度 mb(mb)/mc(mc)=3.291 → C_b/C_c=1.375 dev 3.0%（round-1 nominal）;
  scheme 正確 HPQCD 21 mb/mc@3GeV=4.586(12) → C_b/C_c=1.915 **dev 43.6%** —— 44/33 近命中係偽影
- ★ **redundancy 0→1**: (b/c@3GeV)×(c/s)=53.436(33) vs M_RGI_b/M_RGI_s=53.369(74) → dev 0.13% z=+0.08 閉環
- ★ 純γ u/d 雙通道: MS z=+0.85 / RGI z=+0.51 都過
- ★ C-shape v2: b=79.65（scheme 更正 39%）; u/d/s/c/e/μ/τ 不变
- ★★ **pre-registered 預言 register**: 8 條可證偽預言（docs/03 §六）; killer = lattice 1% ms/mu vs 42.89±1.52