# O237 docs/14 — U3 label sieve 確認負＋U5 感知耦合形式化（14/14）

> **日期**: 2026-10-07 · **狀態**: U3 維持 🔴-convention（負確認）；U5 形式化 🆕（關係語言一致，測量機制剩 🔴）
> **腳本**: `scripts/17_u3_u5_attack.py`（14/14 PASS）＋ log

---

## 一、U3 — Assignment label sieve：κ 表測試（負確認）

**問題**（docs/01 §三 U3）：label（點解 e 喺 mode 1）冇結構推導；O236 R1 已證明格**形狀** assignment-invariant，但 label 本身係觀察者約定。

**本輪測試**：O147 κ 表（docs/09，已閉合 21/21）──κ 係每粒子固有 φ 修正指數（全結構數）。若 κ_n = f(mode) 有結構 ⟹ κ 表就係新 label sieve。

**結果（負）**：
1. κ 唔係 mode 單調函數（mode 2 打斷：κ(u)=−16）
2. κ 唔係 γ(n) 函數（u/d/e 都近 γ₁，κ = −16/0/3.5 互異）
3. κ 唔係 mod-4 相位類函數（mode 1 內 e/μ/τ/t κ 都唔同；mod3 內 d/c/b 0/2/2）
4. **κ 冇 13−n 對偶對稱**（s↔τ: 18↔9；u↔b: −16↔2 全不同）
5. κ 表自身結構確認：b=c=2（Z₂）、e=μ=3.5（L₄/2）、d=t=0（基準/VEV 吸收）——同 O143 P_f sharing 平行

**裁決**：κ 表唔提供 label sieve——**docs/01 U3 立場維持：convention 標記**。U3 唔係「等新 sieve」，而係「label 本質上係觀察者約定」（同 O236 R1 形狀不變性一致）。**U3 嘅有意義內容（形狀／格／κ 表結構）已全閉合，剩 label 命名──唔係物理問題。**

## 二、U5 — 感知耦合形式化（新）

**問題**（docs/01 §三 U5）：O206 本體論已閉合概念（性質 = 關係產物；位置 = Object−Reference Frame；速度 = Object−Time），但**質量 = Object−?** 冇定義——觀察者點解把 chain mode 讀做「慣性質量」？

**形式化（本輪）**：
```
位置 = Object−Reference Frame   →  θ_n = nπ/44  (88-ring 相位; γ=|1−U|² 一致, U=e^{inπ/44})
速度 = Object−Time              →  v_g = cos(nπ/88)  (色散斜率/群速度, O170)
質量 = Object−Frame 脫相位度量    →  |1−U_n|² = 4sin²(nπ/88) = γ_n
                                     (Object 相位偏離同步 Frame 嘅二階量)
m_f = M₀γ_nF_proj = M₀ × 脫相位量 × 商殘餘
```

**三個一致性檢查**：
1. `|1−U_n|² = 4sin²(nπ/88) = γ_n` EXACT（U = e^{inπ/44}，88-ring 每步相位 π/44）✓
2. m_n = M₀√γ_n = M₀|1−U_n|（譜層＝偏差振幅，O36 🟢）✓
3. m_f = M₀γ_nF_proj = M₀|1−U_n|²×商殘餘（公式層，O54/O64/O137）✓

**⚠️ 修正（腳本內發現，引用時注意）**：docs/01 §二 S0 寫 `U_n = e^{inπ/88}`——呢個係 **176-L path 版本**（γ_k = |1−U_k|², U_k = e^{ikπ/88}）；**88-L ring 嘅 U_n = e^{inπ/44}**（每 step 相位 2π/88=π/44）。88-ring 用錯 U 會令 γ 差 4×（|1−e^{iπ/88}|² = 0.0051 vs γ₇=0.2446）。本 script 用 88-L 正確定義。

**裁決**：**「感知質量」= Object 對 Frame（88-ring 同步）嘅脫相位度量 × M₀ × 商殘餘**——O206「性質 = 關係產物」語言一致：γ 係 Object↔Frame **關係量**，唔係 Object 內在屬性。位置／速度／質量三種性質統一於同一 chain 相位結構。

**剩餘（誠實）**：①「點解觀察者『必須』用 M₀ 標度讀」（O212 已錨單位 dof=1，但感知機制──儀器/意識點解讀 γ 做質量──屬 O206↔O212 接駁，**仍未正式推導**）② 本 script 只形式化關係語言，唔 pretends 推「意識執行讀數」。

## 三、同 docs/11-13 閉環統一

```
docs/11: CY₃ 參數 (36,98) = chain 跡 (Tr G = 134)
docs/12-13: H₀ 投影因子 = chain 譜量 (1−b₁, √λ₁₇, 1/v_g)
docs/14: 質量 = chain 脫相位度量 (γ=|1−U|²) × M₀ × 商殘餘
⟹ 全部「投影／幾何／質量」量都還原做 chain 內部結構＋商殘餘。
```

## 四、檔案

```
scripts/17_u3_u5_attack.py   14/14 PASS
logs/17_u3_u5_attack.out
docs/14_u3_u5_attack.md    ← 本檔
```