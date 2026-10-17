# O252 — R8: 方向 one-sided 事前性拆彈 (2026-10-17)

狀態: 🔴 **方向 gap 維持未閉合 — one-sided p=0.0461 係 post-hoc 收窄,
       record 21 冇 dip sign 事前預言; 正確檢驗 two-sided p=0.0923**
Script: `13_direction_onesided.py` (exit 0)
Data: `data/13_direction_onesided.json`

---

## 1. 誘惑

R3: 10/13 顯著 dip 藍側 → two-sided p=0.0923 未閉合。
誘惑: 「record 21 事前預言 R<1 藍弱 → 應該用 one-sided → p=0.0461 < 0.05 閉合!」

## 2. 拆彈

**record 21 事前預言內容**: 「藍峰弱紅峰強 (R<1), 方向固定」— 係**峰高比**預言
(peak ratio), 唔係「dip 位置 sign」預言。
- O252 τ(v) 嘅 ±v_abs 係 per-source 凝聚層側向身份 — **從未**事前預言
  「dip 普適藍側」
- R4 已證明帶唔製造 sign bias (q_blue≈0.50, band-bias 否證)
- one-sided 收窄 = 睇到數據之後揀方向嚟測 — 統計違規

| 檢驗 | p 值 | 裁定 |
|:-----|:----:|:----:|
| one-sided (探索性上界) | 0.0461 | ❌ 唔適用 — post-hoc |
| two-sided (正確) | 0.0923 | 🔴 未閉合 |
| 敏感度: 剔 K Hβ 邊緣 (n=12, 9藍) | two 0.1460 | 🔴 更差 |

## 3. 結論

方向 gap 係 O252 **唯一未閉合**嘅量。10/13 藍側傾向 (77%) 統計上
唔達標 (two-sided p=0.09, 邊緣), 需要:
- 更大樣本 (Cycle 3/4 R~2700 更多源), 或者
- **事前** dip-sign 預言 (凝聚層側向身份結構 — record 30 已封位置層
  路徑, 需要速度層側向身份)

維持 🟡 partial — 位置/寬度已閉合, 深度雙命中, 方向開放。

*文檔: O252 攻堅 R8 · one-sided 事前性拆彈 · 2026-10-17*