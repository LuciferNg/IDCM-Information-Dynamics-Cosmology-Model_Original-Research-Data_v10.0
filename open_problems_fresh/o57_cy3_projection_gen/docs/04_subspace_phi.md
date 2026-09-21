# O57 文檔 04 — 四期攻堅：Subspace 映射 + φ Kähler 搜索

> **日期**: 2026-08-23
> **狀態**: 🟢 **1 個最強閉合 + 1 個誠實限制**
> **腳本**: scripts/30–32
> **前置**: O57 文檔 03 (CYTools 真幾何)

---

## 一、★★ 155 Curves Subspace ⊂ K 態空間（scripts/30, 5/5 ✅）

### 核心發現

```
155 curves volume vectors (52 nonzero) → rank 30
66 態 evecs: 30 C 態 (純 CPX) + 36 K 態 (純 Kähler)
K 態 Kähler 分量: 36×36, rank 36 (full)

Principal angles (curves vs K):
  30 個 ≈ 0 (max 1.9e-6°)
  → curves subspace (30) ⊂ K 態空間 (36)!
K 空間減 curves 後 rank: 6
```

### 意義

**155 toric curves 生成嘅 30-dim subspace 完全包含喺 36 個 Kähler 態嘅空間入面！**

```
K 態空間 (36) = curves subspace (30) ⊕ 獨立 (6)
30 = 2L₅ + 2B (C sector 數)
6 = 36 − 30
```

**呢個係三期「155 curves rank 30」嘅嚴格延伸** — 唔單止 rank 相同，而且 principal angles 證明包含關係。

### 誠實修正（探索過程）

- 最初以為 curves ↔ C 態（30 CPX），但 C 態 Kähler 分量全 0 → 錯
- 正確：curves subspace ⊂ **K 態**空間（36 Kähler 態）
- C 態係純 CPX（Kähler 分量 ≈ 0），同 curves（Kähler 空間）冇直接交集

---

## 二、φ 結構 Kähler 參數搜索（scripts/31-32）

### 候選結果

| 候選 | 描述 | range | n_finite | score |
|:-----|:-----|:-----:|:--------:|:-----:|
| A | t_i = φ^(i-1) | 7.3e5 | ? | 1 |
| **B** | t_i = φ^(35-i) | **2.7e8** | 6 | 1 |
| **C** | t_i = φ^(i mod 12) | 1.2e4 | **60** | **3** |
| D | 3×12 代遞增 | 7.3e5 | ? | 1 |
| F | L_{i mod 12} | 3.7e3 | ? | 3 |
| G | F_{i mod 12+1} | 5.3e3 | ? | 3 |
| J* | I₃⊗J₁₂ | 2.6e3 | ? | 3 |

### ★ 誠實修正：假達標

候選 B（φ^(35-i)）表面 range 2.65e8 > SM 需要 1.7e8，但：
- 166 個 positive curves 中只有 **6 個有有限質量**
- 其餘 **160 個 underflow**（e^-V ≈ 0）

**range 大 ≠ 質量譜好**！真正嘅質量譜需要合理數量嘅有限質量。

### 誠實結論

**冇 φ 結構候選合格（最高 score 3/6）**：
- 候選 C/F/G/J* 有 60 個有限質量但範圍只 ~10⁴（唔夠 10⁸）
- 候選 B 範圍夠但質量譜塌縮（只有 6 個）
- 需要：更複雜 Kähler 參數結構 或 非純 e^{-V} 機制

---

## 三、四期總結

| 發現 | 狀態 |
|:-----|:----:|
| ★★ 155 curves subspace ⊂ K 態空間 | 🟢 **最強閉合** (30 angles ≈ 0) |
| K 空間 = curves (30) ⊕ 獨立 (6) | 🟢 rank 6 剩餘 |
| C 態純 CPX (Kähler 分量 0) | 🟢 澄清 |
| φ Kähler 候選質量階層 | ❌ 冇合格 (最高 3/6) |
| 候選 B 假達標 (160 underflow) | 🟢 誠實修正 |
| 質量階層機制 | 🟡 **仍然開放** |

## 四、開放問題更新

| # | 問題 | 狀態 |
|:-:|:-----|:----:|
| 1 | Z₂ mirror | 🟢 閉合 (頻率對偶) |
| 2 | 66 態 → SM 標籤 | 🟡 66 結構清晰; 質量階層需新機制 |
| 3 | sr_ideal ↔ Kähler cone | 🟡 155 curves rank 30 閉合; 完整 facet 未證 |
| 4 | 25 kernel | 🟢 閉合 (25 = M−2B) |
| 5 | 441 orbifold | 🟡 441 = (3×7)² 候選 |

## 五、檔案

```
scripts/30_subspace_mapping.py   ✅ 5/5  ★★ curves ⊂ K
scripts/31_phi_kahler.py         ✅ 探索 (φ 候選)
scripts/32_mass_quality.py       ✅ 探索 (質量譜指標)
```
