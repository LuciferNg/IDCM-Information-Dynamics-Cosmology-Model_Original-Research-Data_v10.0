# O234 docs/04 — P1/P2 檢驗：調律者「檢驗時間」方案之自行判斷（2026-10-07）

> **Script**: `scripts/06_p1_p2_verification.py`（7/7 PASS）· **Log**: `logs/06_p1_p2_verification.out`
> **指示**: 「檢驗時間，可以參考Gemini，採用什麼方法自行判斷：要將 IDCM 嘅 L0–L3 質量梯隊
> 與零參數預言（P1 ms/mu=42.89、P2 u/d 雙尺）同真實觀測做交叉驗證」——四步落地方案。
> **verdict**: 🟢 **方案執行完成（3 條判決線）**——**P1 = 循環，killer test 冇效**；
> **P2 = 純 γ 雙尺真檢驗通過（0.85σ/0.51σ，IDCM 質量層唯一實錘）**；P3/P4 = 開放預言。

---

## 一、調律者方案四步逐項判決（自行判斷結果）

| 步 | 方案內容 | 判決 | 原因 |
|:--|:--|:--|:--|
| 一 | FLAG 格點直量 ms/mu 驗 P1（42.89 killer） | 🔴 **循環駁斥** | O234 scripts/05 L83 `C["s"]` 校準自 FLAG ms/mu ⟹ IDCM 預言 ≡ FLAG 觀測（Δ=0, Z≡0）。驗證佢 = 用同一批 FLAG 數字 check 返自己：**非 IDCM 測試** |
| 二 | PDG + RunDec 跑動/RGI 對齊驗 P2 | 🟢 **正確方向, 已執行** | u/d 純 γ 用 MS @2GeV + RGI 雙尺實測 z=0.853/0.506（O234 docs/03 已做, 本輪重核）|
| 三 | LHC/Belle-II 驗 P3/P4 相位類 | 🟡 **開放預言** | 新輕子/新重夸克未出現；已閉合嘅 6 粒子 3/3+3/3（O235 T5）；觸發 = HL-LHC/FCC-ee |
| 四 | 自動化 pipeline（FLAG/PDG 拉取 + Z-score） | 🟢 **做咗**（scripts/06） | 用凍結層數字直接計算, 唔需現網拉取（FLAG 2024 已喺 O234 freeze v2）|

## 二、★★ P1（ms/mu = 42.89）循環駁斥（本輪核心發現）

用戶方案假設「IDCM 零參數預言 m_s/m_u = 42.89 ± 1.52」——**前提不成立**：

```txt
O234 scripts/05 line83:
  C["s"] = (ms/m̂·(1+md/mu)/2) / (γ4/γ2) = (ms/mu)_FLAG / (γ4/γ2)   ← 校準自 FLAG！
O234 scripts/05 line99:  ms/mu = ms/m̂·(1+md/mu)/2  ← 就係 FLAG 導出值

⟹ IDCM 三因子預言  ms/mu_pred = (γ4·C_s)/(γ2·C_u),  C_u=1（C-shape 歸一）
                = (γ4/γ2)·[(ms/mu)_FLAG/(γ4/γ2)] = (ms/mu)_FLAG
⟹ Δ(pred−obs) = 0.000e+00（實數驗證）;  Z = 0.000（照用戶 formula 計算）
⟹ 呢個 test 冇可能失敗 —— 唔係 killer, 係恆等還原（循環）
```

**與 O234 自身先例一致**：docs/02 已判 P2「2.1620 = PDG 中心值按定義還原（循環證明差 0.0, 零檢驗力）」—— P1 42.89 係**同一陷阱**（C_s 用咗 FLAG ms/mu 校準），O234 前輪冇認出。本輪修正：**P1 降格為「IDCM 框架內部表示」, 唔可作測試**。

用 mu/md=0.465(24) 形態交叉計 = 42.890±1.516 —— 同一批 FLAG 輸入嘅另一寫法，**唔係獨立通道**（用戶方案將 ms/m̂ 同 mu/md 視作獨立係誤解——兩者都出自 FLAG 同一 Nf=2+1+1 合集）。

## 三、P2 u/d 純 γ —— IDCM 質量層目前唯一實錘

```txt
IDCM 預言（純鏈譜, 零 C_f）: γ3/γ2 = 2.245204
  MS @2GeV (FLAG): 2.1505 ± 0.111  → z = +0.853σ  ✅（68% 內）
  RGI    (FLAG):  2.1987 ± 0.092  → z = +0.506σ  ✅（68% 內）
⟹ 雙尺獨立通過 —— IDCM 質量層唯一有內容、可樣本外檢驗嘅預言
```

QED/RunDec 修正（用戶方案第二步）：~1%（O(α_em)）＜ 現有 FLAG 誤差（0.111 相對 2.15 ≈ 5%）∨ RGI（0.092/2.20 ≈ 4%）⟹ 對**目前判決**無影響；將來 lattice 1–2% 精度先需要解耦（O234 freeze v2「killer」真正版應該係: 等 lattice 直量 mu/md 1–2% 後, 對 P2 純 γ 判決 —— 唔係 P1）。

## 四、P3/P4 —— 唯一「真 IDCM 內容 + 真 out-of-sample」預言

- 相位類守恆（輕子∈s1 / 重夸克∈s3）由 tick 結構強制（O235 T3/T5）, **唔依賴 C_f** ⟹ 冇循環風險
- 已閉合: 6 個已知粒子 3/3+3/3（O235 T5 docs/05）
- out-of-sample 觸發: 第四輕子/新重夸克（HL-LHC / FCC-ee）⟹ 而家狀態 = 開放預言
- 呢個先係調律者方案第三步真正有牙嘅位（唔係 P1）

## 五、方法學保留/修正對照（對調律者方案）

✅ 保留: FLAG 2024 Nf=2+1+1 做數據源（O234 freeze v2 已凍結, 同一層）; 誤差傳遞 formula（用戶方案 §四 —— 與 O234 line100 一致）; RGI 轉換方向（對 1–2% 精度有用）; 「唔准事後選 scheme」原則（O234 docs/03 已有）
🔴 修正: 「42.89 係 IDCM 預言」= 錯（係 FLAG 導出值嘅重講）; 「ms/m̂ 與 mu/md 係獨立通道」= 錯（同一 FLAG 合集, 循環雙重）; 「1% 直量一擊裁決」應指喺 **P2（u/d）** 而非 P1

## 六、Gemini 參考記錄（唔當證據, 只記）

調律者准許「參考 Gemini」——`ask-web.py gemini` 只返嚟碎片（公式渲染 `ms/mu = ms/m̂ × 2/(1+md/mu)` 與 O234 line99 一致）。按 discipline：chat LLM 答案冇算力、唔當證據；本輪判決全部出自**真實凍結層數字計算**（scripts/06）。無 claim 需要 web_model_verify（冇採用 Gemini 陳述為依據）。

## 七、剩餘

- ⏳ P2 真正 killer: lattice 直量 mu/md 1–2%（O234 freeze v2 已預言觸發條件）
- 🟡 若重啟任何「C_f 池匹配」分析, 必須 freeze v2 同 scheme 比（docs/03 §七 重申）
- P3/P4 開放預言維持（O235 T5 註冊）

## 八、產物

- `scripts/06_p1_p2_verification.py`（7/7 PASS）+ `logs/06_p1_p2_verification.out`
- 引用: O234 docs/03（freeze v2）+ scripts/05 L83/L99（循環源）; O235 T5 docs/05（P3/P4）