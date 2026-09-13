# O175 docs/07 — 遺留攻堅 D3: 耗散熵流 vs UHECR 預算 — **閉合 (v2 修正版)**

> **狀態**: ✅ **已閉合** (09-13, script 08 v2: 3/3 + script 11: 9/9)
> ⚠️ **誠實修正**: v1 判決「naive 池支付 UHECR 讀法證偽 (deficit 2.45e5)」**撤回** —
> v1 有單位/體積 bug: `R_rel·M_sun(kg)·c²` 出 **J** 但標籤寫 **erg** (factor 10⁷),
> 兼用 W-world 體積 2.95e11 Mpc³ 對比 comoving 觀測 ℒ (factor 40.7).

## 閉合 (零新常數, script 08 v2 3/3)

| 形式 | 池側 | UHECR 側 | dev |
|:-----|:-----|:---------|:----|
| **率形式** | R_rel·M☉·c²/V_comov = **1.00265e45** erg Mpc⁻³yr⁻¹ | ℒ_UHECR = 1e45 (Auger) | **0.26%** |
| **總量形式** | E_strain·M☉·c²×59.35 週轉 = **1.660e68** erg | ℒ·V_comov·t_H = 1.656e68 erg | **0.25%** |

- R_rel = 6,730.86 M☉/yr = O173 **觀測**穩態釋放率 (script 01 能量流審計, 非擬合)
- ℒ_UHECR ≈ 10^45 erg Mpc⁻³yr⁻¹ (Auger-constrained, 兩份獨立 2024/25 論文)
- → **池釋放能量率 = UHECR 總能量率**: O7/O173「UHECR = 阻挫邊重聯 = 池釋放同事件」圖像 **CONFIRMED**
- 寫入通道: 1.6e-42 erg Mpc⁻³yr⁻¹ (comoving) = ℒ 嘅 **10^87 分之一** (控制參數, O175 定理1 重現更強; v1 宣稱「11 數量級」都係錯, 已修正)

## 主/次通道結構

1. **主通道 (直接)**: 池釋放 R_rel → 阻挫邊重聯 → UHECR (dev 0.26%, 零新常數)
2. **再生側 (交叉)**: BH 返池率 = ρ_BH·φ⁻²¹·V_comov/t_H = 8,882 (K&H) – 17,408 (Elvis) M☉/yr vs R_rel = 6,731 (ratio 1.32–2.59, order-level) — O121 T_pipe† 返池以 φ⁻²¹ 效率再生 (script 11 E)
3. **黑洞轉化層**: ρ_BH·φ⁻²¹·c²/t_H = 1.3–2.6e45 (script 11 閉合 A, order-level 交叉, 唔係主通道)

## 剩餘開放 (🔴/🟡)

- 🟡 f_return 因子 1.32–2.59 (ρ_BH 錨 K&H/Elvis 範圍主導) — 等更準 ρ_BH
- 🟡 R_rel ≈ 306×22 = 6732 (dev 0.017%, 觀察, 非推導) — 等結構側身份
- 🟡 ℒ_UHECR = 1e45 係正典值 (~±2× 不確定度) — dev 0.26% 係對正典值, 實質 order-level

## v1→v2 修正清單

| 項 | v1 (錯) | v2 (對) |
|:---|:--------|:--------|
| L_pool 單位 | 4.08e39 「erg」= 實為 J | 1.2033e58 erg/yr |
| 體積 | W-world 2.95e11 | comoving 1.2e13 (對應觀測約定) |
| 判決 | 證偽, deficit 2.45e5, 通道→黑洞 | **閉合, dev 0.26%, 池=主通道** |
| 寫入通道 | 「11 數量級以下」 | 86.8 數量級以下 (更強) |
