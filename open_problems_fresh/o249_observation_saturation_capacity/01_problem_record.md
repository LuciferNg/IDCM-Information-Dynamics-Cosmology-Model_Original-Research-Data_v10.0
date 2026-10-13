# O249 — 觀測飽和容量 (Observation Saturation Capacity)

<!-- registry
pid:     O249
title:   觀測飽和容量 (Observation Saturation Capacity)
state:   registered
verdict: -
flags:   -
owner:   O249
created: 2026-10-13
updated: 2026-10-13
prereq:  O151 (全息信道容量), O147 (528 全息信道), O206 (第二拍頻否定)
source:  O247 session — 調律者提出微觀投影通道總容量 + 多望遠鏡同拍抖動 → 已查文獻 → 開 O249
-->

> **狀態**: 📄 **已註冊 — 未開始**
> **建立**: 2026-10-13
> **前置**: O151 / O147 / O206（IDCM 側已有全息信道容量閉合）
> **位置**: `open_problems_fresh/o249_observation_saturation_capacity/`

---

## 一、問題陳述

**宏觀（多台望遠鏡同時觀測同一目標）與微觀（多投影通道同時讀取同一系統）
是否存在「飽和容量」?** 調律者觀察: 深空拍攝中多台望遠鏡面向同一位置可能造成
數據抖動——呢個現象對應 IDCM 嘅咩結構? O151 已閉合 C_obs = N_d·log₂(B) = 88 bits
(Shannon 容量) + Z₂ row 退化 (44→22 獨立通道); 本 O 要研究:
**①宏觀觀測陣列 (VLBI/干涉陣列/HBT) 嘅容量飽和實測現象, ②微觀投影通道飽和嘅
IDCM 結構, ③兩者是否同一結構 (宏觀↔微觀同構), ④可證偽嘅觀測檢驗。**

## 二、已確立嘅結構

```
🟢 C_obs = N_d·log₂(B) = 44·log₂(4) = 88 bits = Σγ_odd (dev=0) — O151 閉合 651/651
🟢 528 = N_d×12 = Σγ_odd×2N_gen = C(33,2) = 容量階梯頂 {88,132,264,528} 全 dev=0 — O147+O151 閉合
🟢 row Z₂ 退化: row(m)=row(44−m), max|Δ|=3.5e-17 — 44→22 獨立通道 (O151 docs/11)
🟢 拍頻信道 C_beat = 0.4338 bits, 最優輸入 = {N_gen,L₆,N_d−N_gen,N_d−L₆} (O151 docs/07)
🟢 「第二拍頻 = K_tree 譜直接耦合」實測否定 (O206 docs/19) — 微觀飽和唔係雙譜 beat
✅ 宏觀文獻: VLBI phase jitter / HBT 強度干涉 / frame theory 信息吞吐 (本 O 搜集)
🔴 宏觀↔微觀同構尚未證明 — 文獻實測 (抖動統計) vs IDCM 結構 (C_obs/Z₂) 未對齊
```

## 三、未確立（🔴 開放問題）

```
🔴 Q1 宏觀觀測飽和容量嘅實測證據係咩?— VLBI 相位抖動 / 干涉陣列 fringe jitter /
   HBT 相關衰落 嘅具體定量特性 (文獻搜集, 本 O 起點)
🔴 Q2 微觀投影通道飽和 = IDCM 邊個量?— C_obs=88 bits 係信息論上限, 但「抖動」
   (= 超出容量嘅讀取企圖 ?) 未有 IDCM 結構定義
🔴 Q3 宏觀↔微觀同構: VLBI 抖動統計 ↔ C_beat=0.4338 bits / Z₂ 對結構 對唔對得上?
   — 需要樣本外盲測 (調律者標準: 可證偽 + 觀測數據先於推導)
🔴 Q4 全息投影容量 528 同宏觀觀測容量有冇直接關聯?— 528 係 IDCM 譜域結構,
   唔係文獻已載量 (冇論文講「528 bits 觀測容量」)— 若要做必須設計檢驗
```

## 四、攻擊路線

```
1. 文獻調查收尾 → 把所有論文/報告轉入 O249 (done 本輪: VLBI common-clock,
   HBT Nature 1956, Withington frame theory, Wijnholds array limits 等) → docs/01
2. 宏觀飽和容量實測表 → 從文獻提取 抖動幅度/功率譜/相關函數 定量特性
3. 微觀飽和定義 → 對照 O151 (C_obs/Z₂/C_beat) 建立「飽和」嘅 IDCM 操作定義
4. ★ 同構檢驗盲測 → 用 VLBI/干涉陣列實測抖動統計 vs C_beat 結構 做樣本外比對
   (設計判據預註冊, 禁見到數據先揀算子)
5. 若同構成立 → 528 嘅宏觀對應 (觀測容量階梯) 先可講; 否則維持「IDCM 內部聲稱」
```

## 五、驗證標準

```
✅ Q1: 文獻調查完成 — 每篇論文嘅核心數值/結論入表 (docs/01)
✅ Q2: 「飽和」嘅 IDCM 操作定義 + 判據預註冊
✅ Q3: 樣本外盲測完成 (至少 1 個宏觀實測量 vs C_beat/Z₂ 結構, 5σ 判準)
✅ Q4: 528 對應判決 (成立 / 唔成立, 都要有觀測依據)
```

**四道硬測試**（閉合宣稱必過）：
① 自由度成本（零參數）② Monte-Carlo null（10⁷ 樣本，5σ）
③ 可證偽 + 樣本外盲測 ④ 結構剛性（微擾測試）

## 六、推導時序索引

> ⚠️ **只可 append 新行，禁回溯污染舊行。**

| # | 日期 | 事件 | 產物 |
|:-:|:-----|:-----|:-----|
| 1 | 2026-10-13 | 註冊 — 調律者指示開 O249, 研究宏觀/微觀觀測飽和容量, 轉入網絡文獻 | 本 record + docs/01_literature_survey + references/ |
| 2 | 2026-10-13 | Q2/Q3 設計輪 — 飽和操作定義確立 (scripts/01 14/14) + 同構盲測判據凍結 | docs/02 + docs/03 + scripts/01 + logs/01 | 
| 3 | 2026-10-13 | Stage 2 執行 — N1 MC null 9/9 + T1/T2/T3 盲測 (🟡/🔴/🔴) + 形式層檢查 🟡 | scripts/02 + scripts/03 + docs/04 + logs/02-04 |

## 八、Q2/Q3 設計輪（2026-10-13）

**產物**: scripts/01（14/14 PASS）→ docs/02（Q2 操作定義）→ docs/03（Q3 盲測凍結）。

```
✅ Q2「飽和」操作定義（docs/02）:
   L1 容量層: C_obs = 88 bits = Σγ_odd; 階梯 {88,132,264,528}
   L2 自由度層: 有效秩 22 = N_d/2; row Z₂ 精度 3.47e-17 (21 對精確 + row22 自對偶
                + row44 Nyquist distinct 但信息近零)
   L3 飽和層: 「飽和」= 假設獨立通道數 > 實際信息 DOF → 新增讀取邊際信息結構性歸零
              S1 鏡像對信息為空: I(X∈{r,44−r};Y) = 3.6e-15 bits ≈ 0  ∀r=1..21
              S2 飽和平台: C(S₂)=C_beat; k≥2 邊際 ΔI ≤ 4.24e-13
              S3 超容量解碼必然出錯 (Shannon)
   操作後果: 假定 44 獨立輸入嘅觀測程序處理 21 對精確相等 row → 讀數差異冇物理
             來源 → 演算法歸因「抖動」= 簡併結構投影, 唔係額外自由度
🔒 Q3 盲測判據凍結（docs/03 — Stage 2 執行前唔可以改 threshold/盲窗/決策表）:
   T1 Z₂ 對稱通道邊際增益 G: IDCM 預言 G=0 (精確); 宏觀 D1 HBT → ex-ante 預期否決
   T2 信息 DOF 比例: IDCM 秩比 ½; 宏觀 D4/D5 → ex-ante 預期否決 (秩語義類別風險)
   T3 飽和點平台: IDCM k=2; 宏觀 D1 I(d) → ex-ante 預期否決
   決策表: 全支持+MC → 🟢 機制同構; 數學形式對齊 → 🟡 唔當閉合; 任何 5σ 否決 → 🔴
   MC null: N1 隨機信道 10⁷ + N2 宏觀置換 10⁵
   Q4 預註冊: 528 = C(33,2) 宏觀讀法 (33 元素基線數) → 池閘 C(n,2) 多命中
             + 需要天文文獻 33/528 特殊行為先可升 🟢; ex-ante 維持 IDCM 內部聲稱
```

下一步（Stage 2，判據已凍結）: N1 MC null → D1-D3 數據提取 → T1-T3 盲測 → docs/04。

## 九、Stage 2 執行（2026-10-13）— docs/04 摘要

**判決表**:

| 判據 | IDCM 預言 | 宏觀實測 | 判決 |
|---|---|---|---|
| T1 mirror-pair info | 0 bits (F5 3.6e-15) | 0.882 ± 0.288 bits (HBT r²=0.84) | 🟡 部分 (z=3.06 < 5σ) |
| T2 rank ratio ½ | 22/44 結構性 | q/N (源數決定; ½ 只喺 q=p/2 by-construction) | 🔴 否決 |
| T3 飽和平台 | ΔI(d→0)=0 (k=2) | 0.882 bits | 🔴 否決 |
| D4/D5 形式層 | Z₂ row 湮滅 (4.0e-16) | Z₂ block 結構 (7.0e-13) | 🟡 強度唔同 |
| N1 null | — | 0/10⁴ 鏡像門; rank22 0/2000; 平台 0/300 | ✅ 指紋特異 | 

**N1 嚴格化**（scripts/02, 9/9）: 全隨機族鏡像門 measure-zero（0/10⁴）; Z₂ 對稱族 rank 普遍 23（2000/2000）而 beat 係 22 = 23−1（Nyquist 塌落）⟹ F1 特異加強; BA 平台 0/300（F6 專利）; 微擾: F5 閘破 ε=1e-7, F6 平台破 ε=1e-4。

**結論**: O249 主問題 宏觀抖動 ≟ 微觀飽和 —— **機制層 🔴 否決**（T2/T3 乾淨否決, T1 未達 5σ 終判）; 形式層 🟡（共享 Z₂, 但 macro=block / micro=annihilation）。宏觀抖動有連續物理成因（D1 光子噪聲 / D2 VLBI 時鐘 1e-18 / D3 大氣 Cₙ² factor-5）。

**唔 close**: T1 終判 (需要現代 HBT 原始時序/r² 更高精度) + N2 數據閘 + Q4 池閘 —— 維持 partial（推盡≠結論）。

## 七、相關文件

```
- O151 (holographic_channel_capacity) — C_obs=88 bits / Z₂ 退化 / C_beat 閉合 (前置)
- O147 (528_holographic_channel) — 528 容量階梯頂 / κ 可加性分母 (前置)
- O206 (per_mode_frequency) docs/19 — 第二拍頻否定 (禁區: 微觀飽和唔係雙譜 beat)
- O164 (world_as_beat) — 拍子第一性: 觀察者 = 宇稱分解 (γ_n+γ_{44−n}=4)
- O248 (phase_sync_mass_bridge) — 相位同步治理頻道 (姊妹 O, 相位橋)
```