# O27 — 節點 47 前景污染分析

## 狀態: 🟢 已閉合

## 結論
節點 47 (l=313.47°, b=-8.58°) 嘅 -135.7 μK (3.0° SMICA) 係**銀河面塵埃前景污染假象** 🔴, 唔係真實 CMB 冷結構 — 多頻譜測試決定性否決 (143 GHz 唔冷 + 217 GHz 急升 = dust 特徵)。

## 關鍵公式
- 判據: CMB 平譜 217/143 ≈ 1; dust 上升 217/143 >> 1
- node47: 143 GHz = +18.3 μK, 217 GHz = +380.9 μK, 217/143 = 20.8 → 🔴 dust
- 對照 node0 冷斑: 143 GHz = -111.9 μK, 217/143 = 0.36 → 🟢 平譜
- R3 CMB common mask: node47 被遮住 (0.5°-5° 盤 0% 保留, 60 節點 45/60 保留)

## 依賴
O5 → O27 (O5 目錄對比發現 node47 第二冷 → O27 前景驗證); O27 → O52 (60-node 系統學必須分 masked/unmasked)

## 驗證
- 2026-08-21: `08_verify.py` 25/25 + `09_full_verification.py` 82/82
- 2026-09-11 搬遷後重驗證: 107/107 PASS (判定不變)

<!-- conclusion-history:start -->
## 迭代史（machine-generated from register.conclusion；append-only）

| concl_hash | 日期 | verdict | 結論摘要 | 支撐 | 取代 |
|---|---|---|---|---|---|
| `9ab804d1b3052b93` | 2026-10-24 | — | 節點 47 (l=313.47°, b=-8.58°) 嘅 -135.7 μK (3.0° SMICA) 係銀河面塵埃前景污染假象 🔴, 唔係真實 CMB 冷結構 — 多頻譜測試決定性否決 (143 GHz 唔冷 + 217 GHz 急升… | open_problems_fresh/o27_node47_foreground/final_result.md | — |
<!-- conclusion-history:end -->
