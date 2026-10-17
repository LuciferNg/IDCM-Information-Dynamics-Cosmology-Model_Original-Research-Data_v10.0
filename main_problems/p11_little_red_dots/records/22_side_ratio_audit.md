# Record 22 — 峰高比統計自身審計: 窄線中心 artifact 修正 + 吸收預言未獲支持 (2026-10-17)

狀態: 🔴 **「10/10 藍弱」= artifact (窄線 z 中心 + broad centroid 紅移);
      穩健量度 (broad 峰位中心) 6/10, P=0.377 — 吸收 channel 藍弱預言未獲支持**
Script: `scripts/28_side_ratio_stats.py` (data/28_side_ratio_stats.json)
        + scratch 穩健性檢查
觸發: record 21 後續 — 峰高比統計; 首輪結果 10/10 藍弱 P=0.001 極吸引,
      自身審計 (z 敏感性) 揭穿 artifact

---

## 1. 首輪結果 (吸引但有陷阱)

以窄線 z (DJA zfit) 做中心, Hα 窗藍/紅側 flux 積分比:
- **10/10 光源 R_side < 1, 二項檢驗 P = 0.0010 (3.1σ)** — 表面極強

## 2. 自身審計 (z 敏感性測試) — 揭穿

| 測試 | 結果 |
|:-----|:-----|
| z ±0.002 (≈ 2σ 文獻誤差) | R 變化 35-60% |
| z ±0.01 | R 變化 200-560% (0.35 → 5.6) |
| continuum 窗 ± | 穩定 (<3%) |

⟹ **R_side 對 z 極敏感** — 量度唔穩健。

## 3. 根因

- DJA z 由**窄線** fit (系統紅移); broad Hα centroid 自身 redshifted
  (全部光源 vpeak = +35..+457 km/s — broad component 相對於窄線系統紅移,
  已知 AGN 現象: BLR 幾何/bulk 流)
- 以窄線 z 為中心 ⟹ 紅側必然有更多 broad flux ⟹ R<1 係**必然**, 零物理資訊
- 呢個唔係「吸收 channel 預言」支持 — 係 broad redshift 嘅退化

## 4. 穩健量度 (broad 峰位自身做中心) — 定案

以每光源 Hα 峰位 v_peak 為中心, ±3000 km/s 對稱窗積分比:

| 光源 | v_peak (km/s) | R_side (峰中心) | 判定 |
|:-----|:--:|:--:|:--:|
| A (H) | +84 | 0.776 | 藍弱 |
| A (M) | +86 | 0.817 | 藍弱 |
| C (H) | +70 | 0.900 | 藍弱 |
| C (M) | +184 | 1.471 | 藍強 |
| E | +457 | 1.853 | 藍強 |
| F | +35 | 0.739 | 藍弱 |
| G | +39 | 0.521 | 藍弱 |
| I | +88 | 1.030 | 藍強 |
| J | +112 | 0.794 | 藍弱 |
| K | +136 | 1.578 | 藍強 |

**6/10 藍弱, 二項檢驗 P = 0.377 — 完全唔顯著**

## 5. 判定

| 陳述 | 判定 |
|:-----|:----:|
| 10/10 藍弱 (窄線中心) | 🔴 **artifact** — broad centroid 紅移退化 |
| 吸收 channel 預言 R<1 (穩健量度) | 🔴 **未獲支持** (6/10, P=0.377) |
| record 21 嘅「3/4 藍弱方向一致」 | 🔴 同一個 trap (用窄線 z 做峰位比較) — 作廢 |
| record 21 定理 (純散射保對稱) | 🟢 不受影響 (數學獨立) |
| A Hα 負振幅 (P-Cygni dip) | 🟢 仍有效 (fit 層面, 唔係側比) |
| broad centroid redshifted (+35..+457) | 🟢 新 finding — 有待文獻對照 |

## 6. 教訓 (審計紀律)

- **吸引嘅統計信號要即刻做量度穩健性測試** — z 敏感性係第一道關
- 「中心定義」決定結果: 窄線 z vs broad 峰位 — 唔可以混用
- R_side 呢類量度必須以 broad 自身特徵 (峰位) 做參考系, 唔可以用外界 z

## 7. 後續

- broad centroid redshift 嘅物理: 係 bulk outflow 背側 Emiss (redshifted)?
  定 BLR 幾何? — 可對照 Rusakov fit 嘅 narrow/broad offset
- 吸收 channel 測試需要真正線形 fit (P-Cygni 組件), 唔係側比

*文檔: closeout 攻堅 · 自身審計 · 2026-10-17*