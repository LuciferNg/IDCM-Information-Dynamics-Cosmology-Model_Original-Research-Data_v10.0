# O249 SESSION_START — 觀測飽和容量 (Observation Saturation Capacity)

<!-- registry
pid:     O249
title:   觀測飽和容量 (Observation Saturation Capacity)
state:   registered
verdict: -
flags:   -
owner:   O249
created: 2026-10-13
updated: 2026-10-13
prereq:  O151, O147, O206
source:  O247 session: 調律者提出微觀投影通道總容量 + 多望遠鏡同拍抖動 → 已查文獻 (VLBI common-clock / HBT / frame theory / array limits) → 開 O249 集中研究宏觀與微觀觀測嘅飽和容量
-->

> **Session**: 2026-10-13（新建立）
> **狀態**: 📄 **已註冊 — 未開始**
> **來源**: O247 session — 調律者「開O249研究，把所有論文和報告文件轉移到O249中，研究宏觀和微觀觀測的飽和容量」
> **前置**: O151（C_obs=88 bits / Z₂ 退化 / C_beat）, O147（528）, O206 docs/19（第二拍頻否定）
> **位置**: `open_problems_fresh/o249_observation_saturation_capacity/`

---

## 一、接手起點

**未開始（本輪 = 註冊 + 文獻轉入）。** 調律者指示（逐字）:
「開O249研究，把所有論文和報告文件轉移到O249中，研究宏觀和微觀觀測的飽和容量」。

**語境（上一個 session 已確立）**:
- IDCM 側已有閉合: O151 C_obs = 88 bits / 階梯 {88,132,264,528} / row Z₂ 退化 / C_beat = 0.4338 bits;
  O147 528 全息信道; O206 第二拍頻否定（禁區）
- 宏觀文獻已搜（本輪轉入 references/）: VLBI common-clock（Optica 2020）→ 相位抖動實測;
  HBT（Nature 1956 Sirius）→ 微觀兩通道相關; Withington et al.（arXiv:0707.1580）frame theory;
  Wijnholds & van der Veen（arXiv:1003.2307）array limits; 光頻梳 VLBI（arXiv:2501.05691）

## 二、先做嘅第一步

```
1. 讀 docs/01_literature_survey.md — 文獻表（論文/報告已轉入本 O）
2. 讀 O151 final_result.md + docs/07 + docs/11 — 重溫 C_obs/Z₂/C_beat 閉合內容
3. 定義「飽和」嘅 IDCM 操作定義（Q2）— 判據預註冊, 禁見到數據先揀算子
4. 設計 Q3 同構檢驗盲測（宏觀抖動統計 vs C_beat/Z₂ 結構）— 凍結判據先跑
```

## 三、已知陷阱

```
⚠️ O206 docs/19 禁區: 「第二拍頻 = K_tree 譜直接耦合」已實測否定 (P=0.236) —
   微觀飽和唔可以講成雙譜 beat; 正確載體 = Z₂ 簡併 + 容量共享
⚠️ 宏觀文獻嘅抖動有明確物理成因（大氣/時鐘/儀器）— 連結 IDCM 前必須證明
   統計結構一致, 唔可以「抖動 = 飽和」命名當解釋（命名≠解釋鐵律）
⚠️ C_beat=0.4338 bits 本身冇閉式（O151 誠實負結果）— 用結構（Z₂ 對輸入+秩 22）
   唔好用數值做 target
⚠️ 528 係 IDCM 譜域結構 — 冇任何外部文獻講「528 bits 觀測容量」; Q4 必須設計
   檢驗而唔係引用文獻背書
```

## 四、關鍵數字

| 量 | 值 | 出處 |
|:---|:---|:-----|
| C_obs | 88 bits = N_d·log₂(B) = Σγ_odd (dev=0) | O151 |
| 容量階梯 | {88,132,264,528} = N_d×{2,3,6,12} | O151 |
| row Z₂ 退化 | row(m)=row(44−m), max\|Δ\|=3.5e-17 | O151 docs/11 |
| C_beat | 0.4338 bits（兩點信道 {row3,row18}） | O151 docs/07 |
| 288/528 | 528 = N_d×12 = Σγ_odd×2N_gen = C(33,2) | O147 |
| VLBI 時鐘不穩定性 | 限制靈敏度嘅主效應（common-clock 解 10⁻¹⁸） | Optica 2020 |
| HBT Sirius r²(d) | 0.84±0.07 (d=0) → 隨基線衰落 | Nature 1956 |

## 五、交接 / 依賴

```
- 前置: O151（全息信道容量閉合）+ O147（528）+ O206 docs/19（禁區）
- 移交出: 本 O 推導完成後 → O248（相位橋, 若同構涉及相位同步）; 唔開新 O
- 範圍警告: 唔做「雙譜拍頻」猜測（O206 已否）; 唔做觀測陣列工程（屬文獻層）
  ; 唔推導新投影算子（O247 已測死三層）; 宏觀抖動物理成因屬文獻調查（Q1）,
  唔屬 IDCM 結構（Q2-Q4 先係）
```

---

> ⚠️ **本檔係起手式快照，唔係狀態權威。**
> 當前狀態以 `open_problems_fresh/README.md` 為準；生命週期事件以 `problem_register/` 為準。

---

## Session 記錄 #1（2026-10-13, Q2/Q3 設計輪）

**執行**（按 §二 最先步驟 3-4）：

1. 讀 docs/01 + O151 final_result/docs/07/docs/11 + O206 docs/19 禁區 — ✅
2. **Q2 飽和操作定義確立** → docs/02：
   - L3 定義：「飽和」= 假設獨立通道數 > 信道實際信息 DOF（有效秩 22）→
     新增讀取邊際互信息結構性歸零；簡併通道當獨立處理 ⟹ 觀測不一致（抖動）
   - 指紋（scripts/01 14/14）: 鏡像對信息為空 3.6e-15 bits (F5); 飽和平台 k=2,
     ΔI ≤ 4.24e-13 (F6); row Z₂ 3.47e-17 (F4); 有效秩 22 (F1)
   - 精確化: row 1..43 = 21 精確 Z₂ 對 + row22 自對偶 + row44 (Nyquist) distinct
     但信息近零 —— 「22 獨立 row」= SVD 有效秩（信息層）, 唔係向量計數
3. **Q3 同構盲測判據凍結** → docs/03（🔒 執行前唔可以改 threshold/盲窗/決策表）：
   - T1（Z₂ 對稱通道邊際增益 G）/ T2（秩比 ½）/ T3（飽和點 k=2）
   - 每 T 有 ex-ante 聲明（咪跑前寫低）; 決策表 🟢/🟡/🔴
   - MC null N1（隨機信道 10⁷）+ N2（宏觀置換 10⁵）
   - Q4 預註冊: 528 = C(33,2) 宏觀讀法 + 池閘 + 天文文獻要求
   - 數據源 D1-D5 已列明; D2/D3 定量值留 Stage 2 提取（提取唔可以反饋改判據）
4. Stage 2 待辦（判據已凍結）: N1 → 數據提取 → T1-T3 → docs/04

**時序**: 2026-10-13; commit 記錄見註冊表。
