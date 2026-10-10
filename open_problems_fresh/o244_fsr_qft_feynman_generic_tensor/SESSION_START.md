# O244 SESSION_START — O244 — FSR-QFT 費曼圖求值與通用張量 (承接 O137 R23 尾巴)

<!-- registry
pid:     O244
title:   O244 — FSR-QFT 費曼圖求值與通用張量 (承接 O137 R23 尾巴)
state:   registered
verdict: -
flags:   -
owner:   O244
created: 2026-10-09
updated: 2026-10-09
prereq:  -
source:  -
-->

> **Session**: 2026-10-09（承接 O137 R23）
> **狀態**: 📄 **已註冊 — 未開始**
> **來源**: O137 — FSR-QFT 對接尾巴（調律者指示「直接開新O244交接」）
> **前置**: O137 scripts/74+75+76 全 PASS（56/56）；docs/40 FSR-QFT 對接記錄；O124 費曼規則機制
> **位置**: `open_problems_fresh/o244_fsr_qft_feynman_generic_tensor/`

---

## 一、接手起點

```
承接 O137 R23 嘅 FSR-QFT 對接尾巴（docs/40 §七 + §九）。
O137 已完成: [A] 對偶定理 γ_FSR·ω_CHAIN=2 EXACT [B] FSR 費曼規則 (3g=0/4g δΣn≡0 mod 2N)
[C] Gauge 光子 Goldstone 零色散 [D] N=44 ε=γ EXACT [E] b₀=7 ζ(1)×16 [F] 質量差一階釐清。
本 O 未開始 — 承接 4 條尾巴 (T1-T4, 見下)。
```

## 二、先做嘅第一步

```
1. 讀 O137 docs/40_fsr_qft_docking_formal.md 全文 (特別 §三 [B] 費曼規則 + §七 演員表)
2. 讀 O137 scripts/75_fsr_qft_docking_formal.py + scripts/76 (python 環境 = /usr/bin/python3)
3. T2: 寫 N 通用 4g/3g 顯式張量 (色代數不隨 N 變, 動量標籤 n↔2N 通用化; O124 scripts/05 係 N=88 特例)
4. T1: 用 [B] 規則求 4g 頂點散射振幅
```

## 三、已知陷阱

```
⚠️ ζ_N(1) 正確閉式 = (2N²+1)/12 — 唔好抄 O140 docs/03 嘅 ((2N)²−1)/12 (錯 2 倍, 已 handoff O140 更正)
⚠️ 光譜字典三量: ε=4sin²(πn/2N) (頻譜) / γ_FSR=csc (Lorentz 階梯) / ω=2sin (=√ε) — 唔好混用
⚠️ 質量公式: O137 正典 m=M₀γ_n (γ=4sin²) 已鎖定 (O120 closeout §5); FSR √ε 係頻率階梯唔係質量階梯
⚠️ FSR-QFT 嘅費曼求值唔可以交 O125 (已 closed) / O84 (已 closed) — 本 O 就係承接呢啲尾巴
⚠️ 9 費米子指派 = A₅ γ升序 (e→1..t→13); O209 |Δm| 未獲 O137 授權
⚠️ 環境: /usr/bin/python3 (miniforge 空); mpmath/mp.dps 高精度; 禁 tail 截斷判斷
```

## 四、關鍵數字

| 量 | 值 | 出處 |
|:---|:---|:-----|
| 對偶積 csc·2sin | ≡ 2 EXACT（所有 n, N） | O137 scripts/74+75 |
| ζ_N(1) 正確閉式 | (2N²+1)/12（N=44: 322.75 = 1291/4） | O137 docs/40 §六 |
| b₀ | 7（色代數, 與 N 無關） | O124 |
| ζ(1) RG 標度 | N→4N 層 ×16 = B² | O137 scripts/76 E2 |
| N=44 譜恆等 | ε_n^FSR = γ_n^CHAIN | O137 scripts/76 D1 |
| M₀ | 27.900915（質量單位） | O38/O206 |

## 五、交接 / 依賴

```
- 源: O137 (docs/40) — FSR-QFT 尾巴全部移交本 O
- 依賴: O140 質量語義澄清回覆 (T4) / O124 同步 (T2) / O209 最終裁定 (指派)
- 移交出: T4 收到 O140 回覆後做物理閉合
- 範圍警告: 唔做 O137 本身嘅 CY₃ 幾何/質量譜; 唔做 O240-243 真空能/漲落/相變 (QFT 扇區四翼)
```

---

> ⚠️ **本檔係起手式快照，唔係狀態權威。**
> 當前狀態以 `open_problems_fresh/README.md` 為準；生命週期事件以 `problem_register/` 為準。
