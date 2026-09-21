# O57 文檔 14 — 十四期：真 Q_ij 幾何 vs γ 近似 + 分流盤點

> **日期**: 2026-08-24
> **狀態**: 🟢 **真 Q_ij 全秩 + 3 cluster 提示** + 🔴 **γ 階梯唔係幾何結構**
> **腳本**: scripts/80–81
> **前置**: O57 文檔 13 (Kähler 譜掃描)

---

## 一、真 Q_ij 相交矩陣（scripts/80）

### 數值微分攞 Q_ij = ∂V_i/∂t_j

```
Q shape: 185×32（CYTools 計 185 條 curve × 32 divisor basis）
Q range: [-16.0, 12.0]（有負相交數 — 結構性）
Q 非零: 719/5920 = 12%（稀疏）
rank: 32/32（全秩！冇零模式）
```

### 結論

- **Q_ij 全秩** → 冇 gauge singlet 零模（每個 divisor 都同某啲 curve 相交）
- 真幾何同 γ-weighted 近似本質唔同

---

## 二、真 Q 世代結構（scripts/81）🔴 γ 階梯唔係幾何

### 譜聚類

```
QQ^T 本徵值: [431.8, 415.6, 368.4, 338.3, ...]
最大 eig gap: 47.2 at position 2 → 3 clusters 提示！

K-means: [81, 70, 34]（3 個 cluster 自然出現）
但 cluster volumes: [0.83, 0.14, -0.07]（冇 φ 階梯）
```

### 誠實對比

| 方法 | 世代結構 | 階梯 |
|:-----|:---------|:-----|
| γ-weighted (scripts/68) | 0.57→1.92→3.16 | ≈φ²,φ ✅ |
| **真 Q_ij (scripts/81)** | 3 clusters (81/70/34) | **冇 φ 階梯 ❌** |

### ★ 關鍵 insight

```
γ-weighted 嘅 3 代階梯係 K_Chain γ 譜嘅 artifact
唔係 CY₃ 幾何嘅結構！

真 Q_ij 有 3 cluster 提示（eig gap 最大 at 3）
但 cluster 內 volume 冇 φ 階梯
→ 3 代結構可能源自 γ 譜, 而質量階梯需要其他機制
```

---

## 三、分流盤點（用戶指示）

### 已開始未閉合（O57 繼續）✅

| # | 問題 | 狀態 |
|:-:|:-----|:----:|
| 1 | 真 Q_ij 幾何分析 | ✅ 本輪完成（全秩 + 3 cluster） |
| 2 | ν/l 統一機制 | 🟡 scripts/60/64 已探索 |
| 3 | Λ 候選審計 | 🟡 scripts/78/79 已開始 |

### 未開始（開新 O 系列）📋

| # | 問題 | 新 O 系列 |
|:-:|:-----|:---------|
| 1 | **Λ 第一性原理推導**（投影算子 → Kähler VEV → 真空能） | O62 |
| 2 | **sector-dependent 幾何**（3 type 各自 curve 子集 → 9 費米子） | O62 |
| 3 | **A_ij(z) pre-factor**（複結構模 3-form 交集） | O61（已註冊） |
| 4 | **Moduli stabilization**（通量鎖定真空） | O61（已註冊） |
| 5 | CKM/PMNS 湧現 | O61（已註冊） |
| 6 | φ^(35-i) 嘅 35 意義 | O61（已註冊） |

---

## 四、總結

| 發現 | 結果 | 狀態 |
|:-----|:-----|:----:|
| 真 Q_ij | 185×32, rank 32/32, 冇零模 | 🟢 完成 |
| 譜聚類 | 最大 gap at 3 → 3 clusters | 🟢 提示 |
| K-means | [81, 70, 34] | 🟢 自然 3 組 |
| γ 階梯 | **唔係幾何結構（artifact）** | 🔴 誠實修正 |

## 五、檔案

```
scripts/80_q_matrix_real.py  ✅ 真 Q_ij (全秩)
scripts/81_q_generations.py  ✅ 世代結構 (3 cluster, 冇階梯)
```
