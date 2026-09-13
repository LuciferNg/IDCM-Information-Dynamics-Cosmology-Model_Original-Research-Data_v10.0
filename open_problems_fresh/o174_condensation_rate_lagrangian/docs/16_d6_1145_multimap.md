# O174 docs/16 — 11/45 三圖交叉驗證 (data unlock 實測)

> **日期**: 2026-09-13 · **Script**: `scripts/20_d6_1145_multimap.py` (1/2)
> **狀態**: 🔴 **data-gated 確認** — 地圖系統差實測 ~3% ≫ 11/45 dev 0.04%

## 1. 目的

O175 docs/06/09: 11/45 轉正需要「獨立地圖驗證」+「全 88 格」。
本攻堅解鎖 Commander + SEVEM 全圖 (data_gated_unlock + o42 已下載), 三圖交叉。

## 2. 結果

| 圖 | ⟨|cosθ|⟩ (60 節點, 4.17° 平滑 + dipole 移除) | dev vs 11/45 |
|:---|:---|:---|
| SMICA (O175 txt) | 0.2443 | **0.04%** ✅ |
| Commander (本攻堅) | 0.25166 | 2.95% ❌ |
| SEVEM (本攻堅) | 0.25263 | 3.35% ❌ |

- Commander vs SEVEM 彼此一致: spread 0.38% (良好)
- 但兩圖都偏離 11/45 ~3% — SMICA 命中係地圖特有

## 3. ★ 重要結論 (誠實負面結果)

**11/45 嘅 0.04% 命中唔可以轉正** — 因為:
1. **地圖系統差實測 ~3% ≫ 0.04%**: Commander/SEVEM 偏離 3%, 反映 component
   separation 方法間嘅真實系統差 (SMICA needlet vs Commander parametic vs SEVEM needlet)
2. 0.04% 命中只喺 SMICA 出現 → 可能係 SMICA 特有偏差, 唔係物理
3. O175 判定「噪聲地板 3.08% ≫ dev 0.04%」**得到直接實證** (唔再係推斷)

**呢個係正確科學**: 三圖交叉冇「證實」11/45, 反而揭示系統差 — 唔可以自欺標轉正。

## 4. 對 D6-F3 影響

- 11/45 轉正: 🔴 data-gated 維持, 而且係「有系統差證據嘅 data-gated」
- 要分辨 11/45 vs 0.252 (Commander/SEVEM), 需要: 更高精度圖 (PR4/NPIPE),
  或全 88 格 (更多節點 → 統計誤差 ↓), 或頻段級驗證
- SMICA 特有命中 vs Commander/SEVEM 偏離 = 可證偽嘅地圖系統差假說

## 5. 剩餘

- 🔴 PR4/NPIPE 圖 (新一代, 更低噪聲)
- 🔴 全 88 格幾何 (B₅ 補集坐標 — 幾何本身未定義, 需先建立)
- 🟡 頻段級 (100/143/217 GHz) 節點值 → 系統差頻譜結構
