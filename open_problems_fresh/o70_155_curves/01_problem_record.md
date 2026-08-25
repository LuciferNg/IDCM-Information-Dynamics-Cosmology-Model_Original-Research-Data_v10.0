# O70 — 155 curves facet 結構（O57 移交）

> **日期**: 2026-08-24
> **狀態**: 🟡 **已註冊 — 線索級（CYTools 卡死）**
> **來源**: O57 docs/24 開放問題 #7
> **前置**: O57 docs/02-03 (155 curves)

---

## 一、問題

CY₃(36,98) 有 155 條特殊 curves（sr_ideal 相關），結構 155 = 2×73 + 9。
完整 facet 結構未證明（36-dim Kähler cone 太大，CYTools extremal rays 卡死）。

## 二、已確立嘅結構

```
🟢 155 = 2×73 + 9
  475 unique sr 對（no_edge 37 + anomaly 25）
  34 triples 全 κ=0（三互異零根源）

🟢 155 curves rank 30 = 2L₅ + 2B = C sector（最強閉合）
  → 155 條 curve 嘅相交矩陣 rank 30

🟡 Kähler cone extremal rays 卡死（d=36）
  → CYTools 無法計算

🟡 J* e^{-V} 範圍 1.85（唔夠 SM 10⁸）
  → Kähler fine-tuning 可達 1.9e7（可行性, 非結構預言）
```

## 三、攻擊路線

```
1. 替代方法計算 36-dim cone extremal rays
   → PALP / Sage / 自寫 cone 演算法
   → 或者降維（Z₃ orbifold → 12 維, O59 已有）

2. 驗證 155 = 2×73+9 嘅結構
   → 73 = L₆×4+1? 9 = 3²?
   → 73×2 = 146 = 2×(2L₆+1)²?

3. 155 curves 同真 Q_ij 3 clusters 關係
   → 185 總 curves, 155 特殊, 30 其他
   → 30 = 2L₅+2B（C sector）
   → 155 = 185 - 30?

4. 同 66 態（O67）連結:
   → 155 curves 可能對應 66 態嘅幾何實現
```

## 四、驗證標準

```
✅ 155 結構有完整幾何解釋
✅ 36-dim cone 有可行計算方法
✅ 同 Q_ij / 66 態一致
```

## 五、狀態

```
🟡 線索級（rank 30 支持, facet 未證, cone 卡死）
⭐ 優先度: ★★
```
