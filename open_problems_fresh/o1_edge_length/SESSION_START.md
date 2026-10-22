# SESSION_START — 新O1: 邊長 26.09° A₅ 群論閉合

<!-- registry
pid:     O1/edge-length
title:   新O1: 邊長 26.09° — A₅ 群論精確閉合
state:   closed
verdict: closed
flags:   -
owner:   O1
created: 2026-10-22
updated: 2026-10-22
prereq:  O1
source:  o1_edge_length scripts 01-10 (2026-08-16)
-->

## 狀態

🟢 **已閉合** — `closed` / verdict `closed`（register 2026-10-22）

## 一句話

60 節點 A₅ 軌道（冷斑自由軌道，一般位置）邊長 26.0913° 由 A₅ 群 **120° 旋轉**作用喺冷斑向量決定：
θ = arccos(cos²δ − sin²δ/2) = **26.091357°** vs 觀測 **26.091346° ± 0.000022°**（120 對），
偏差 **0.000011°**（0.00004%），旋轉不變性 std = **0°**（相似不變量）。

## 起手式（接手者先讀呢三樣）

1. `final_result.md` — 結論 + 關鍵公式 + 依賴
2. `01_problem_record.md` §推導時序索引 — 10 個 script 嘅真實次序
3. `04_audit_full.md` — 2026-10-22 全量審計（10/10 script 重現 + 1 bug 修正）

## 前置資料（唔使重推）

```
δ = 15.108516°  (冷斑到最近 3-fold 軸角, 由 ICRS (48.2999,-20.4373) 幾何確定)
θ = arccos(cos²δ − sin²δ/2) = arccos((3cos²δ−1)/2)
  = arccos[cos120° + (1−cos120°)cos²δ]   ← 兩式等價 (相差 0.00e+00)
= 26.091357°  vs 觀測 26.091346°±0.000022°  ⟹ 偏差 0.000011°
反推: δ = arccos(√((2cosθ+1)/3)) = 15.108509° (同直量差 6e-6°)
群元素: 26.0914←120°, 26.1664←72°, 31.6787←180°, 42.9712←144°
大圓: δ3+δ5 = 37.7595° ≈ 軸角 3-5 = 37.3774° (差 = 球面過剩 0.8799°/2)
```

## 相關 skills

- `idcm-structural-derivation-workflow` — 結構推導紀律
- `polyhedral-graph-analysis` — A₅ / dodecahedron 群論
- `exact-linear-algebra-verification` — 精確群元素驗證

## 已知陷阱

1. **唔好用舊 O1（15.11°）嘅結果** — 已證係座標系假象（std=7°），搬去 O184；本題目嘅 26.09° 係 std=0° 真結構量。
2. **07_edge_formula_verify.py 有已知變量覆蓋 bug** — L121 loop 內覆蓋 `theta`，令 data 檔 `theta_formula` 寫錯 113.54°。stdout 同 theta2 一直正確，文檔未受污染。2026-10-22 已由 `11_audit_fix_theta_field.py` 修正 data（原檔備份 `.bak_20261022_200350`）。
3. **δ 唔係自由參數** — 由觀測冷斑位置鎖定（l=180+L₇, b=−(44+F₇)），唔可以當擬合參數調。
4. **邊長有兩個值** — 26.0913°×2 (120°元素) + 26.1664°×2 (72°元素)，degree=4；文檔「邊長」指最近鄰 26.0913°。
