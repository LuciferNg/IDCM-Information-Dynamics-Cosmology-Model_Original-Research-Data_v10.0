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

## 七、相關文件

```
- O151 (holographic_channel_capacity) — C_obs=88 bits / Z₂ 退化 / C_beat 閉合 (前置)
- O147 (528_holographic_channel) — 528 容量階梯頂 / κ 可加性分母 (前置)
- O206 (per_mode_frequency) docs/19 — 第二拍頻否定 (禁區: 微觀飽和唔係雙譜 beat)
- O164 (world_as_beat) — 拍子第一性: 觀察者 = 宇稱分解 (γ_n+γ_{44−n}=4)
- O248 (phase_sync_mass_bridge) — 相位同步治理頻道 (姊妹 O, 相位橋)
```