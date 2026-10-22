# O70 — 總結：Kähler Cone 極限

> **狀態**: 🟢 v2 完滿閉合 (2026-09-03) — 詳細報告見 `docs/06_extreme_rays_v2.md`
> **歷史**: v1 (08-31) 以 99 boundary rays 歸檔 → v2 推翻 (99 唔 complete, 真解 3732)

## 已閉合結構

### 155 = 2×73+9 ✅
- 73 = Nd + L₇ = 44+29, 73 = L₆×4+1
- 9 = 3² = N_gen² (9 duplicate sr_ideal entries)
- 52/155 nonzero = Nd+2B, rank 30 = 2L₅+2B

### 155 curves ⊂ K 態（O57 更正）✅
- C 態投影: **0.0000** — 完全正交
- K 態投影: **0.961** mean overlap

### Rank 結構 ✅
```
36D: rank 30 = 2L₅+2B
32D: rank 29 = L₇ (loss of 1 via missing divisors [3,4,7,8])
185 curves Q_ij: full rank 32
30 extra curves (185-155): add 3 = N_gen dimensions
```

## ★★ v2 (2026-09-03): Kähler Cone Extreme Rays 完整解

### 方法突破
1. **Facet-defining 篩選**: 185 Mori rays → **只有 46 條真 facet-defining** (139 redundant)
2. **Sage PPL**: `Polyhedron(ieqs=46 rows, backend='ppl')` → **3732 條 extreme rays, 24 秒**

### v2 驗證 (全部 PASS)
```
全部 3732 ∈ K (185 ieqs): min M·r = −6.66e-16 ✅
全部 active-rows rank = 31 (genuine 1-dim faces) ✅
全部 extreme (minimal) ✅
舊 99 ⊂ 3732 ✅ (99/99)
獨立重跑 (script 39): 21/21 PASS ✅
```

### 點解 v1 錯
- v1 用 random LP boundary walk 只搵到 99 條 (subset)
- K ⊄ cone(99) — containment 測試 FAIL (4/300)
- 完整 extreme rays 數目 = **3732**, 遠超 99

## 歷史: v1 嘗試過嘅方法 (全部失敗/唔 complete)

1. CYTools `toric_kahler_cone().extremal_rays()` → d>18 卡死
2. scipy HalfspaceIntersection → 搵唔到 interior point
3. LP boundary walk → 28-99 條 (subset, 唔 complete)
4. Active constraint refinement → boundary points 喺 faces
5. Iterative walk (23+ rounds) → 203-228 條 (收斂極慢)
6. pycddlib / polymake → 編譯/路徑問題

**v2 結論**: redundant constraints 係 DD 卡死元兇; 先 facet-defining 篩選, Sage PPL 24 秒完成。

## 檔案
```
docs/06_extreme_rays_v2.md   ← v2 完整報告 (主)
docs/01-04                   ← v1 歷史分析
data/33_exact_extreme_rays_ppl.npy ← 3732×32 最終答案
scripts/39_independent_full_verification.py ← 21/21 PASS
```
