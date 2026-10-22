# O70 — 交叉驗證結果

> ⚠️ **歷史文件 (v1, 2026-08-31)** — 內容結論已被 v2 推翻。
> v1 嘅「99 boundary rays 已足夠表徵」係**錯** — 99 只係 subset, 唔 complete。
> **v2 正確結論**: 46 facet-defining → 3732 exact extreme rays (見 `docs/06_extreme_rays_v2.md`)。

## 方法比較

| 方法 | 描述 | Unique Rays | Rank | 結果 |
|:-----|:-----|:-----------:|:----:|:----:|
| **A** | LP (Σt=1) + 隨機方向 | **76** | **32** ✅ | 🟢 全空間 |
| **B** | Active Set Refinement | 75 | 30 | 🟡 接近 |
| **C** | QP sphere minimization | 0 | — | 🔴 失敗 |
| **D** | Random 32-subset | 0 | — | 🔴 太稀疏 |
| **E** | Dual cone QR | 0 | — | 🔴 錯 rows |
| **A+B 交叉** | 共同驗證 | 99 combined | **32** ✅ | 🟢 一致 |

## 結論

**方法 A 成功！** LP 標準形（min c·t s.t. Q·t ≥ 0, Σt = 1）能有效找到 Kähler cone 邊界點。99 條 unique rays 完全 span 32D。

**Kähler cone 已完整表徵：**
- 32D cone，由 185 條曲線不等式定義
- 155 條 adjacency curves 貢獻 rank 29 = L₇
- 30 條 extra curves 貢獻 rank 3 = N_gen
- 185 條 curves 全 rank 32
- 99 條 boundary rays span 全 32D

**未完成：** 精確 extreme rays（32 條 active constraints）需要 convex hull 計算，在高維 (32D) 計算成本高。但從應用角度，99 條 boundary rays 已足夠表徵 cone 結構。

## 檔案

```
data/15_all_rays.npy   — 99 條 boundary rays (rank 32)
data/15_active_counts.npy — active constraints 數
```