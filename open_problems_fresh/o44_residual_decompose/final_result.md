# O44 — p=0.072 剩餘信號分解

## 狀態: 🟢 已閉合

## 結論
減大冷斑後嘅 mean-nearest p=0.072 殘餘信號 **冇第二結構** — 佢係大冷斑家族（6 斑：lit#1 + SMICA-c2 + 4 Cruz sub-spots，全部最近 node 0）嘅尾巴。移除全部 6 斑後 p→0.385（純噪聲）。node9 反信號（移除後 p 反而更顯著 0.042），node47 零貢獻（最近斑 23.18°）。47/47 verifier + 獨立重算（fresh seed）+ 2026-09-12 全鏈重跑三重確認。

## 關鍵公式
- mean-nearest 統計: d̄ = mean_i min_j angdist(spot_i, node_j)
- p = P(rot_mean ≤ obs_mean)（1000/10000 Rodrigues rotations，單尾：斑比隨機更近）
- z = (obs − rot_mean) / rot_std
- 冷斑族定義: {spots : nearest node = 0}（新 a5_nodes 編號，deterministic 6 斑）
- 確定性 leverage: Δobs_i = mean_nearest(all) − mean_nearest(all \ {i})（無 MC 噪音）
- node9 檢驗: P(node9 closer) = 0.788-0.7925（permutation 10000）

## 關鍵數字
| 量 | 值 |
|:---|:---|
| all-35 p | 0.042 (z=-1.77σ) |
| baseline-34 p | 0.072 (z=-1.58σ) |
| **減冷斑族 (6) p** | **0.365 (1000-rot) / 0.385 (10k-rot)** |
| 減冷斑族 + node9 p | 0.324 / 0.340 |
| 減 node9 斑 p | 0.051 / 0.042（反信號） |
| bootstrap frac p<0.05 | 0.222 |
| 最大 leverage | c2 +0.245° / h2 +0.234° / B +0.234° |

## 依賴
O5 → O44 → O52

## 衍生開放問題
- 🔴 熱斑幾何歸屬（F₆/F₇ 距離節點 8-9°）— O5 遺留
- 🟡 相位機制假說（點解只有特定節點 node0/node9/ΔE=0 有異常？異常 ∝ cos θ_i?）— 未註冊 O 系列
