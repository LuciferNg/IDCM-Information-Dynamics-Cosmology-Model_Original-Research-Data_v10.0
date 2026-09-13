# O175 docs/07 — D4 攻堅: SPARC Fall 關係實測 🟡(樣本覆蓋不足)

> **日期**: 2026-09-13 · **Script**: `scripts/13_d4_sparc_fall.py` · **數據**: SPARC Lelli+16 (J/AJ/152/157, VizieR CDS 下載)

## 數據
- table1.dat: 135 星系 (qual≤2: 129) — Name/L3.6/Rdisk/Vflat
- table2.dat: 完整旋轉曲線

## 結果

**① Fall 關係 (disk-only 樣本)**:
```
log j_star vs log M_star (N=92, M>1e9, qual≤2):
slope = 0.450 ± 0.019   (intercept = −1.60)
Fall+13 帶 [0.52, 0.64] → ✗ 帶外
```

⚠️ **樣本依賴**: Fall+13 帶包含 ellipticals (bulge 主導 → 斜率較高);
SPARC = disk-only → 已知偏低 (文獻: disk-only slope ~0.5)。唔係 IDCM 失敗。

**② IDCM j_spec = 19,867 km/s·kpc**:
```
對應 Fall+13: M_star = 6.76e11 M☉ (log M = 11.83)
SPARC j 範圍: 20 - 7,017 km/s·kpc → j_spec 超出樣本覆蓋 ✗
附近星系 (ΔlogM<0.5): 只有 UGC02487 (logM=11.39, j=5239)
```

## 裁決

- 🟡 **樣本覆蓋不足** — SPARC 冇 M~10^11.8 星系 (j_max 7,017 ≪ 19,867)
- Fall disk-only 斜率 0.45 ± 0.02 (提供實測, 但唔係 IDCM 判決位)
- 需要: 高質量端樣本 (M~10^11.5-12) 嘅 j_star 測量 (Posti+18 類 / 本地大質量 spiral)
- IDCM 預言保持: j_spec = 19,867 @ M = 6.8e11 — 可證偽 (等大質量樣本)

## 依賴
O175 (j_spec) → SPARC (Lelli+16) → D4
