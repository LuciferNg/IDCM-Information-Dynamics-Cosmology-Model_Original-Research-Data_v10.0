# O52 — 60 節點系統性微冷/微熱檢驗

## 狀態: 🟢 已閉合 (2026-08-21 主體 + 2026-09-11 ΔE=0 判死 → 完全閉合)

## 結論
60 個 A₅ 節點**冇系統性微冷/微熱** — 全部 8 尺度 |z|<0.4σ, 堆疊 radial profile 全部 |z|<0.6σ。IDCM「全部 60 節點有異常」假說被否證, 只有 node0 (冷斑) + node9 (高斯極端) 係真異常。ΔE=0 12 節點抑制 (O3/O4) 經多頻譜最後裁決 → 🔴 判死: 只存在於組件分離地圖, HFI 100/143/217 GHz 冇重現 (方向相反), 高緯子集 0/6 達 p<0.05 — 係組件分離/前景假象 (scripts/06 + docs/02)。

## 關鍵公式
- 60 節點 mean (3.0°): −1.522 μK vs 天空 +0.204 → z = −0.27σ (全部尺度 |z|<0.4)
- R3 mask 分層: unmasked 45 z=−0.39, 高緯 31 z=−0.51 (全部 |z|<0.6)
- 剔除 node0/9 後: +2.83 μK, z=+0.46 (無隱藏冷系統性, 反而微熱)
- 冷/熱 = 29/31, 2σ 極端 = 4/2 (期望 1.4, node0/node9 驅動)
- ΔE=0 抑制: 4.17° 跨地圖 ratio 0.508-0.563 (p=0.032-0.051), raw SMICA ratio 0.764 (p=0.209) — **2026-09-11 多頻譜裁決 → 🔴 判死** (docs/02_deltaE0_verdict_20260911.md)

## 依賴
O5 → O7 → O21 → O52 → (ΔE=0 跨地圖 → O143 相位機制)

## 驗證
- 54/54 file simulation verifier PASS (scripts/03_verify.py)
- 獨立重算 (fresh fits sampling, seed 888) 全部一致
- O30 (舊編號) 17/17 + 三重獨立確認一致

## 檔案
NN_results.md (完整報告), VERIFIER_RESULT.md, 01_problem_record.md (時序索引), scripts/01-06, docs/02_deltaE0_verdict_20260911.md (ΔE=0 判死裁決)

<!-- conclusion-history:start -->
## 迭代史（machine-generated from register.conclusion；append-only）

| concl_hash | 日期 | verdict | 結論摘要 | 支撐 | 取代 |
|---|---|---|---|---|---|
| `c9f2dfd42b6787f9` | 2026-10-24 | closed | 60 個 A₅ 節點冇系統性微冷/微熱 — 全部 8 尺度 \|z\|<0.4σ, 堆疊 radial profile 全部 \|z\|<0.6σ。IDCM「全部 60 節點有異常」假說被否證, 只有 node0 (冷斑) + node9 (高斯… | open_problems_fresh/o52_node_systematics/final_result.md | — |
<!-- conclusion-history:end -->
