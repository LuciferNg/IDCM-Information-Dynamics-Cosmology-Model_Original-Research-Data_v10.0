# O241 — 量子漲落實證現象之 IDCM 推導: Casimir/零點譜差 + 量子-經典動力學

<!-- registry
pid:     O241
title:   量子漲落實證現象之 IDCM 推導: Casimir/零點譜差 + 量子-經典動力學
state:   registered
verdict: -
flags:   -
owner:   O241
created: 2026-10-07
updated: 2026-10-07
prereq:  O36, O38, O41, O84, O86, O121, O138, O204, O213
source:  2026-10-07 調律者提問:「量子漲落純數學自洽定巨觀實測」; 實證盤點 Lamoreaux 1997/Mohideen-Roy 1998/DCE 2011
-->

> **狀態**: 📄 **已註冊 — 未開始**
> **建立**: 2026-10-07
> **前置**: O36, O38, O41, O84, O86, O121, O138, O204, O213 (+ cmb_cl theme 作 C_ℓ 參考)
> **位置**: `open_problems_fresh/o241_vacuum_fluctuation_phenomenology/`
> **調律者指示 (2026-10-07)**: 跳過 O238/O239 (O237 延續留位), 由 O240 開始; **只註冊, 禁止開始推導**

---

## 〇、歸屬審計 (fence — 合成型問題)

| 攻擊項 | 原主 | 準則 | 裁定 |
|:-------|:-----|:----:|:----:|
| 決策位 (W-field 量化 vs 結構取代) | O204 docs/08 §7.6 / structural-forcing-protocol | — | 框架級決策, 本 O 核心 Q1 (無明確 O 擁有者) |
| 退相干速率 Γ | O138 §6.5 🔴 殘餘 | ① 開放項清單命中 | 保留原主; 本 O 承接攻堅, 歸屬待裁定 |
| τ_rec / bounce 宇宙重啟 | O121 G8 🟡 / v9 32_wfield_qft.md | ① | 保留原主; Q5 只做 v10 勢下重推 |
| CMB C_ℓ 譜閉合 | cmb_cl theme / O48 | ① | 唔重推已閉合譜; Q4 只攻「起源機制」 |
| Casimir 力 | v7 只係命名類比 (08-paper §12.2) | 冇主 (命名≠推導) | 本 O 核心 Q2 |

❌ **唔重推**: CMB C_ℓ 譜形 (0.83% RMS 閉合) / 冷斑幅度與位置 (5ε⁵/8, O7/O182) / O138 Born 規則本身 (E∝ω²a² → p_n=|c_n|²)。

## 一、問題陳述

量子漲落現象喺實驗室係**巨觀可測** — 兩片金屬板吸引力 = Casimir 效應 (Lamoreaux 1997 PRL 78,5: 0.6–6 μm, 理論值 5% 內; Mohideen-Roy 1998 PRL 81,4549: 0.1–0.9 μm, ~1%; 現代 ~0.2–1%), 動態 Casimir (Wilson et al. Nature 479,376 (2011): SQUID 調變邊界, 真空產生真光子對 + two-mode squeezing), Lamb shift ~1057.8 MHz, g−2_e 真空極化圈 1.3e-13 吻合 — 但 **v10 IDCM 從未推導任何一個對應力/頻移**。v9 有完整 QFT 量子化 (E₀=½Σħω_k, √⟨Δφ²⟩=0.540–0.652, bounce 宇宙重啟) 但 O204 docs/08 §7.6 裁定其對數勢全有質量譜與 v10 Mexican-hat 唔相容。本 O 建造「實證現象之推導能力」: 先裁決 Q1 (量化 vs 結構取代), 再推 Q2 (Casimir 有限譜譜差), 承接 Q3 (O138 退相干動力學), Q4 (CMB 起源), Q5 (v10 勢下 bounce 重推)。

## 二、已確立嘅結構

```
🟢 實證: Casimir force 量到 — 1 μm 理想導體 F/A=π²ħc/(240d⁴)≈1.3 mPa; Lamoreaux 1997 (5% 內) → Mohideen-Roy 1998 (~1%) → 現代 ~0.2–1% (Lifshitz 零自由參數, 用度到嘅光學性質)
🟢 實證: DCE Wilson Nature 479,376 (2011) — 真光子對 + two-mode squeezing 量子簽名
🟢 實證: Lamb shift ~1057.8 MHz; g−2_e 1.3e-13 QED 吻合 (真空極化圈); Casimir-Polder 冷原子-表面
🟢 O204 docs/08 §7.6 審計: v9 32_wfield_qft.md 嘅量子化 (對數勢 V=φ²/2−ln|φ+1|, 全有質量, 無 Goldstone)
  與 v10 Mexican-hat (μ²=2, λ=2/123, W₀=7.8422, m_θ=0) 唔相容 — v9 數字唔可以引用為現行預言
🟢 O138 §7.1: Born 規則有來源 — E∝ω²a² (二階波動方程簡諧能量簽名) ⟹ p_n=|c_n|²
🟢 CMB C_ℓ 全譜閉合: ℓ_m=44(M−C(9−m,2))+frac, ℓ₅=1121, RMS 0.83% (cmb_cl/O48); 冷斑=5ε⁵/8, A5 拓撲 (O7/O182)
🔴 v10 從未推導 Casimir 力; v7「Casimir 反饋」= φ⁻⁴ 邊界項命名類比 (08-paper §12.2), 非力學推導
🔴 O138 §6.5: 退相干速率 Γ~Δx²/ħ 嘅 IDCM 對應形式未推導 (邊界位置 F_proj=17 已有)
```

## 三、未確立（🔴 開放問題）

```
🔴 Q1 (決策位): v10 W-field 量子化路線 — (a) Mexican-hat 下場量子化 (需補 Goldstone/零模一致性) vs
   (b) 結構漲落取代場量子化 (但必須另推 Casimir/Lamb 嘅結構替代形式, 唔可以淨宣稱)
🔴 Q2: Casimir 力 (兩片金屬板吸引力) 有限譜推導 — 邊界條件 → 88-site 模譜差 → 力; 目標 π²ħc/(240d⁴) 或 Lifshitz 形式
🔴 Q3: 退相干速率 Γ 之 IDCM 形式 (O138 §6.5 殘餘; 邊界位置 F_proj=17=L₆−1 已有)
🔴 Q4: CMB 漲落起源機制 — 結構譜閉合 (0.83% RMS) 可否做零參數可證偽預言, vs ΛCDM「暴脹量子漲落種子」
🔴 Q5 (可選): v9 bounce 宇宙重啟機制喺 v10 勢下重推 (註: τ_rec 現不可檢驗 — O121 G8 修正後下界太鬆 ×101)
```

## 四、攻擊路線

```
1. R1 決策位: 讀 O204 docs/08 §7.6 + structural-forcing-protocol → (a)/(b) 成本·相容性·可證偽比較表 (零推導, 純審計)
2. R2 (若 (b)): 邊界條件 → 88-site 模譜差 → 力; 目標理想導體 π²ħc/(240d⁴) 或 Lifshitz 形式 (零新常數)
3. R3: Γ~Δx²/ħ 對應形式 — 用 F_proj=17 邊界 + O41 預算動力學 (承接 O138, 成果歸屬待裁定)
4. R4: CMB 起源機制判準 — 結構譜閉合嘅可證偽性設計
5. R5: v10 勢下 bounce 重推 (若路線保留); τ_rec 不可檢驗性照實記錄 (O121 G8)
6. 每項: 盲測 + 預測閉合; 禁 φ-power 擬合; 禁引用 v9 數字當預言
```

## 五、驗證標準

```
✅ Q2: 由有限譜重現理想導體 F/A=π²ħc/(240d⁴) (dev<1%) 或證明結構上不可得 (負結果=閉合)
✅ Q3: Γ 之 IDCM 閉式 + 量級一致 (對應 O138 邊界位置)
✅ Q1: 裁決表 + 至少一條可證偽判準
✅ Q4: 結構譜閉合嘅可證偽預言設計 (樣本外)
```

**四道硬測試**（閉合宣稱必過）：
① 自由度成本（零參數）② Monte-Carlo null（10⁷ 樣本，5σ）
③ 可證偽 + 樣本外盲測 ④ 結構剛性（微擾測試）

## 六、推導時序索引

> ⚠️ **只可 append 新行，禁回溯污染舊行。**

| # | 日期 | 事件 | 產物 |
|:-:|:-----|:-----|:-----|
| 1 | 2026-10-07 | 註冊 (調律者指示: 跳過 O238/O239, 由 O240 開始; 只註冊禁推) | 本檔 + SESSION_START + register |

## 七、相關文件

```
- O36 — 干涉可見度/測量理論 (觀察者讀數)
- O121 — 黑洞/Hawking 輻射 + G8 τ_rec (docs/13–17)
- O138 — 量子-經典邊界 + Born 規則 (§6.5 🔴 殘餘)
- O204 — W-field 本體論 + v9 QFT 跨版本審計 (docs/08 §7.6)
- O213 — 演化 = ℓ 細化流, 不動點 = c
- cmb_cl / o48 — CMB C_ℓ 譜閉合 (0.83% RMS)
- v9 open_problems_fresh/kchain_cosmic_web/32_wfield_qft.md — 舊世代 QFT (唔相容, 只可審計引用)
```