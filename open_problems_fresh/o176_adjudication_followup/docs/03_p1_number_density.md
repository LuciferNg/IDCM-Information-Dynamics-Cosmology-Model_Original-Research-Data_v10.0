# O176 docs/03 — P1 數密度裁決: 新數據方向閉合, z<2 反彈仍開 🟡→🟢(方向)/🔴(z<2 未測)

> **日期**: 2026-09-13 · **Script**: `scripts/03_p1_slope_test.py`
> **數據**: Billand+2025 (A&A 706 A29), Zhang+2026 (arXiv:2606.02773), Kocevski+2025

## 一、P1 定義 (O173 docs/19)

```
N(z) 嘅 N = 凝聚事件形成率 ∝ 1/(1+z);  斜率 ln N vs ln(1+z) = -1.00 ± 0.2
樣本: mass-complete (EIGER 方法);  P1' 可證偽窗: [-1.2, -0.8]
```

## 二、新數據 (2025-10 至 2026-09)

**Billand+2025** (z<4 LRD 後代, CEERS):
- LRD-classic 數密度 z=6→3 降 **近 2 個數量級**
- 但 z=3±0.5 嘅 **post-LRD 後代數密度 = 10^-4.15 Mpc⁻³, 等於 5<z<7 LRD 數密度**
- 外圍質量比例 + 尺寸隨 z 增 (250 pc @ z=5 → 600 pc @ z=3), M_*→10^10 M⊙
- → **「消失」= V-shape 褪色 (宿主外圍增長), 唔係種群毀滅**

**Zhang+2026**: Φ(LRD) ~ 10^-5 - 10^-4 cMpc⁻³ @ z>4; z<4 稀疏
**Kocevski+2025**: 「number density declines rapidly below z~4」

## 三、斜率分析

```
CLASSIC LRD 密度:  z=6: 10^-4.15 → z=3: ~10^-6.15
slope lnΦ vs ln(1+z) = +8.23   ← phase+selection 主導, 唔係事件率
```

- 觀測 CLASS 密度斜率 (+8.2) ≫ P1 事件率斜率 (-1.0) — **完全唔同嘅可觀測量**
- docs/19 已量化: 光度限制樣本斜率 -1.78 (JADES) / -2.18 (CEERS) = 選擇效應
- **mass-complete 事件率斜率 (EIGER ~ -1.0) 未被新數據觸及, 維持 ✅**

## 四、IDCM 詮釋 — 關鍵強化

Billand+2025 係 P5/P6 嘅直接支持:
- 「LRD 唔會死, 佢哋長大」 — 核心 (red compact) 保持, 外圍 (blue) 增長
- = O173 種子先行: 凝聚核先形成, 宿主 free-fall 收集繼續
- 數密度「下降」= 相位轉變 (V-shape → 正常星系 SED), 唔係事件率下降
- z=5-7 數密度 == z=3 後代數密度 → 種群連續性直接證據

## 五、裁決

| 項 | 裁決 |
|:---|:---|
| P1 方向 (z<4 下降) | ✅ **確認** (3 篇新論文) |
| P1 事件率斜率 -1.0±0.2 | ✅ 不變 (EIGER mass-complete 仍係唯一直接測試) |
| P5/P6 冇老化 | ✅ **強化** (Billand: 核心不滅) |
| P1′ 證偽窗 [-1.2,-0.8] | 🟡 未觸及 (需要 mass-complete 低 z 樣本) |
| **z<2 反彈測試** | 🔴 **仍未執行** — 唯一開放證偽門檻 |

## 六、剩餘門檻

- z<2 mass-complete LRD 樣本 (EIGER 方法擴展到低 z) — 等 JWST Cycle 3/4 數據
- 注意: z<2 個 LRD-classic 幾乎消失 (V-shape 褪色) → 要測嘅係「後代/凝聚事件」
  數密度, 唔係 LRD-classic — 操作定義需喺 O177 或 P1 修訂時一併釘死
