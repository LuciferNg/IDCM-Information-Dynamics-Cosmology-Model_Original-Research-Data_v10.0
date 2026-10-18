# O252 SESSION_START — 視線遮蔽算子 τ(v): 世界環幾何 → 視線光深 (零新常數, 盲測 dip)

<!-- registry
pid:     O252
title:   視線遮蔽算子 τ(v): 世界環幾何 → 視線光深 (零新常數, 盲測 dip)
state:   registered
verdict: -
flags:   -
owner:   O252
created: 2026-10-17
updated: 2026-10-17
prereq:  O180, O143, O179
source:  p11_little_red_dots records 25-30 (死因定案: 遮蔽層從缺)
-->

> **Session**: 2026-10-17（新建立）
> **狀態**: 🟡 **部分閉合**（R1-R13 + closeout 2026-10-17: 窗存在/窗寬閉合, 深度上限/中位命中, 窗中心身份 + 方向開放）
> **來源**: p11_little_red_dots records 25-30（LRD 死因定案：遮蔽層從缺）
> **前置**: O180（世界環投影核）、O143（𝒫 天球投影）、O179（hop 階梯/W 權重）
> **位置**: `open_problems_fresh/o252_los_obscuration_operator/`

---

## 一、接手起點

未開始（用戶指示：開新 O，但**禁止立即開始推**；只做開題註冊收尾）。

起點背景（已確立，唔會重推）：
- p11 五判別唔支持對稱雙峰（records 19-24）— 但死因係「遮蔽層從缺」
- 固有等權 γ_k=γ_{176−k} 代數必然（record 27）
- τ(v) 三次排除確認架構內從缺（record 30）：O180 位置層 / O143 天球
  / O179 位置權重 / 𝒫∘W 複合（channel 身份錯誤：Galactic longitude ≠ 極角 θ）

## 二、先做嘅第一步（待調律者指令，禁開始推）

```text
1. （禁）—— 用戶明確「禁止立即開始推」；本 session 只做開題收尾
2. 開題收尾完成項: README 行 + git commit O252 骨架
```

## 三、已知陷阱

```text
⚠️ channel 身份: 𝒫 用 Galactic longitude 做環相位, record 14 模態對用
   世界環極角 θ — 唔同幾何, 複合前必須證明身份一致 (record 30 教訓)
⚠️ 禁看到目標凑: A Hα dip −283 km/s 喺眼前, τ(v) 必須由幾何獨立推出
   先可以對照觀測; 反推 = numerology
⚠️ 零新常數: τ(v) 嘅尺度/歸一化必須由已閉合譜量定 (O180 Σγ / O179
   ΣW / hop Σ=60), 唔可以新引入自由度
⚠️ 「遮蔽」vs「態選擇」(record 25 後門) 觀測上都係單峰/唔對稱 — 要分開:
   遮蔽=吸收 dip (P-Cygni), 選擇=發射缺失 (單邊峰), 判別唔同
⚠️ script 33 教訓: 𝒫^T·uniform 對照測試係分離「算子自身對稱性」vs
   「權重貢獻」嘅標配 — 任何複合結構都先做
```

## 四、關鍵數字

| 量 | 值 | 出處 |
|:---|:---|:-----|
| A Hα absorber dip | −283 km/s, depth 0.98 | p11 records/24 (盲測目標) |
| E Hα absorber | +47 km/s, FWHM 350 | Nikopoulos+2026 (盲測目標) |
| 固有等權 | γ_k = γ_{176−k} EXACT | p11 records/27 |
| hop 階梯 | [1,4,8,11,12,11,8,4,1] Σ=60 | O179 (record 29 更正) |

## 五、交接 / 依賴

```text
- 前置: O180 (投影核) / O143 (𝒫 天球, 身份注意) / O179 (hop/W)
- 來源: p11_little_red_dots records 25-30（死因定案 → 本 O）
- 範圍警告: 唔做「態選擇規則」對照框架 (屬 O252 內部子問題, 但唔係
  即時推導範圍); 唔重推已閉合結構 (O180/O143/O179)
```

---

> ⚠️ **本檔係起手式快照，唔係狀態權威。**
> 當前狀態以 `open_problems_fresh/README.md` 為準；生命週期事件以 `problem_register/` 為準。

---

## 六、攻堅結果加注 (closeout 2026-10-17)

```text
✅ 已閉合: τ(v)=帶+窗 結構存在 — 窗存在含冇-dip 反例 (hop2 11/13 p=0,
   hop4 9/13 p=0.0004), 窗寬 σ=σ₃·17/15=189.52 (dev 0.12%)
✅ 已閉合: 冇-dip 窗由 Hβ SNR 極限解釋 (Hα ΔAIC 171 vs 37)
🟡 已收窄: 深度上限 τ_w=4 (top-3 0.923, 6%) + 中位 τ_eff=28/15 (3.5%),
   per-source scatter 未鎖定
🟡 後驗 — 唔當結構閉合: hop=2 (204.9) 窗中心候選, 需 pre-register 盲測
🔴 負結果: 窗中心 289.76 (hop=4 事前) — μ_hat=235.7±21.6 出 CI (R10)
🔴 負結果: band-bias 方向 (R4), one-sided 方向 (R8) — 方向 two-sided
   p=0.092 未閉合
🟢 診斷性閉合: hop 階梯 ⟨v⟩=280.03 ≠ 窗中心 235.7 — 需吸收截面新機制 (R13)

新開放問題 (register 已記錄, 唔喺本檔註冊):
  1. 窗中心結構身份 (吸收截面權重機制) — 最硬 gap
  2. 深度 per-source scatter (需每源凝聚密度模型)
  3. 方向 sign (需凝聚層側向身份或更大樣本)
  4. 精確窗中心驗證 (Cycle 3/4 R~2700 高解像 pre-register 分辨 204.9 vs 236)
```
