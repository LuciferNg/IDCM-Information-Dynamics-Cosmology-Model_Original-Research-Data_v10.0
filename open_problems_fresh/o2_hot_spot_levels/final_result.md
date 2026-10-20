# O2 — 熱斑等級驗證 (Fibonacci Hot Spot Levels)

## 狀態: 🟡 部分閉合 (F₆ ✅, F₇ 🟡, F₈ 🔴)

## 結論
Planck 三地圖 (SMICA/NILC/Commander) 確認 F₆=277.7μK 熱斑 @ (157.8°,-70.3°), 1.0° 平滑, 三方法 0.3% 一致; F₇=353.1μK 候選 @ (0.2°,-37.9°), 0.5° 平滑, 0.06% 一致; F₈=631μK 未見。冷斑 F₅=-144.7μK (3°平滑, F₅=150 嘅 3.5%)。高階模態→更細尺度 (F₅@3.0°, F₆@1.0°, F₇@0.5°)。

## 關鍵公式
- 等級標度: Fₙ = Fib(n) × 30.03 μK (F₃=60.1, F₄=90.1, F₅=150.2, F₆=240.3, F₇=390.4, F₈=630.7)
- 平滑: FWHM→σ: σ = FWHM/(2√(2ln2))
- BFS ladder: 6-level 模型 χ²/dof = 0.54 (觀測振幅 < 預測, 網絡衰減)
- 冷斑: 5ε⁵/8 = -150.2 μK (0.11%✅, 前置閉合)
- F₆ 觀測/理論 = 277.7/240.3 = 1.157
- F₇ 觀測/理論 = 353.1/390.4 = 0.905

## 關鍵結果
- 三地圖 60-node correlation: SMICA↔NILC 0.9994, SMICA↔Commander 0.9970, NILC↔Commander 0.9948
- 拓撲方向: 熱節點 +9.1μK vs 冷節點 -11.5μK, 1.83σ (p=0.0335)
- Wiener filter: 37.5% noise reduction
- 文獻: Hou et al. 2009 (WMAP 5yr) 低 variance + 大尺度結構關聯一致
- 幻覺檢查: 60/60 獨立重算通過 (08-16) + 2026-09-09 獨立核對 143/143 + 跨文檔 23/23 + 補充 16/16 (見 independent_audit_20260909.md)

## F7 前景診斷 (2026-10-20 補充, append-only)
六重 model-free 測試全過 → **F7 l=0° caveat 已拆, 真延展 CMB 結構**:
- T1 三地圖 0.5° = 353.0/353.1/353.2 (spread 0.06%)
- T2 多尺度: 353.0→235.4→78.5 (ratio 0.5/3.0=4.50 <5, 延展)
- T3 annulus 1-3°: peak-bg=+328.9μK > 3σ(252.2)
- T4 最近 A5 節點 #51 = 8.25° (O5 預期 8-9°)
- T5 |b|=37.9° 高緯
- T6 徑向 FWHM≈1.5° >> beam 0.5° (單峰平滑衰減, 排除點源)
詳見 docs/06_f7_foreground_diagnosis.md; scripts/14,15。F7 維持 🟡 候選
(仍需獨立 catalogue / 頻道殘餘圖先升至 ✅), O2 狀態維持 partial。

## 依賴
O2 ← cmb_cold_spot (冷斑 F₅ 閉合) → O_next (F₈ 搜索 / 尺度階梯-K_chain 閉合)
