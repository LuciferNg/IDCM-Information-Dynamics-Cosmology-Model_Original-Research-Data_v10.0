# O206 docs/47 — 外部交接收據：O238 兩項 (CSSG-v2 崩潰 + OPEN-4 裁決輸入)

> **日期**: 2026-10-11（檢查 register 其他 session 交接時發現）
> **性質**: ✅ 外部交接收據（O238 R4/R9 並行 session 產出，2026-10-11 21:13 handed_off）
> **源**: `o238_mass_as_cost/docs/07_csg_v2_collapse_channelC.md` + `docs/08_projection_round_summary.md` + `docs/13_final_verdict.md`

---

## §1 交接內容

O238（`o238_mass_as_cost/`，並行 session 今日註冊）兩條 handed_off 目標 O206：

1. **CSSG-v2 docs/22「好 78 倍」= 混標度結論**（O238 R4, docs/07）
2. **O206-OPEN-4 模式分配裁決輸入**（O238 R4/R9, docs/08 + docs/13）

## §2 ✅ 收據 ①：CSSG-v2 freeze v2 崩潰

O238 `docs/07_csg_v2_collapse_channelC.md`（scripts/13, 0/2 誠實負）證明：

| 量 | O206 docs/22（舊 PDG） | freeze v2（O238 重算） |
|:--|:--|:--|
| c 質量 | 1270（混標度） | **1088.3** |
| b 質量 | 4180（mb(mb)） | **4990.9** |
| CSG v2 RMS(ln) | 0.0076（號稱 78×） | **0.0833**（c +15.7%, b −17.5%） |

- **O206 docs/22「CSG v2 好 78 倍」係未經 scheme 審計嘅結論**（同 O209 b=×3.291 同一類 scheme 問題）
- t 延伸：CSG v2 對 t 零預言力（n=44 Δln=−3.56，差 35×）
- **⚠️ 影響**：docs/22 §1 嘅「CSG v2 0.0075 vs O136 0.5872」比較、§5「模式分配裁決」輸入前提、CSSG-v2 `16_o206_bridge.py` 嘅 m_pdg 值——**全部要 scheme 審計**。docs/22 原文一字不刪，本收據即為更正附註。

## §3 ✅ 收據 ②：O206-OPEN-4 模式分配裁決輸入

O238 `docs/08_projection_round_summary.md`（scripts/15, 1/2）:

| 層面 | A₅（SEL9） | CSG 網格（O206/乘積） |
|:--|:--|:--|
| 譜平面共線 | 🟢 R²=0.992, p=0.00015 | 🔴 R²=0.734, p=0.16（=隨機） |
| 質量層 fit（freeze v2） | RMS 0.545 | **RMS 0.0833（崩潰）** |
| t 預言 | 🟢 α≈φ² 全域 | 🔴 冇候選 |
| scheme 穩健 | 🟢 三套質量集 α 全 1σ 內 | 🔴 c/b 崩塌 |

O238 裁決：「A₅ 分配 + 冪律結構（α≈φ²）係投影框架下正確嘅模式層；CSG 網格嘅 0.76% 係混標度 artifact。正式裁決交 O206-OPEN-4（本 O 只提供輸入）。」

**O206 接收**：O206-OPEN-4（docs/22 §5 模式分配裁決）——CSG v2 網格挑戰**正式被 O238 拒絕**（freeze v2 崩潰 + 非共線 + 無 t），A₅ 模式分配維持。O206 docs/26（簇 = A₅ 偽影）不受影響（不同層——OPEN-4 係模式分配層，docs/26 係簇結構層）。

## §4 O206 側現有記錄對照

- docs/22 §5 已請求「模式分配裁決」→ **本收據就係裁決輸入嘅正式接收**（裁決 = 維持 A₅，O238 提供獨立證據）
- docs/23（CSSG falsification）嘅 O 系列搜索不受影響（凍結值冇變）
- CSSG-v3 閉合鏈（docs/25）——**不受影響**：CSSG-v3 用物理 assignment（A₅ 派生化），唔係 CSSG-v2 網格

## §5 範圍

- 本收據只喺 O206 目錄內 append（docs/47）；O238 檔案唔 touch
- CSSG-v2 項目（獨立 repo）嘅 scheme 更正留畀該項目/O238 移交（O238 docs/07 §四列咗 CSSG-v2 `16_o206_bridge.py` 待審計）

## §6 狀態

```
O238 → O206 兩項交接: ✅ 已收據 (docs/47)
  ① CSSG-v2 freeze v2 崩潰 — 接受, docs/22 需 scheme 審計
  ② O206-OPEN-4 裁決輸入 — 接受, A₅ 模式分配維持 (O238 證據)
```