# Self Loop 指令 — SYNC(ω_n) 驗證 (2026-08-25)

> **問題:** 946 拍頻 (i<j) 之外, 有冇 self loop 指令 (i=i)?
> **答案:** ✅ 有 — 44 個, 對應 master_atlas 對角線 "DIAG zero/self"
> **狀態:** ✅ 閉合 (44/44 驗證)

---

## 1. Self Loop 定義

```
(i,i) 指令:
  d = 0    → 差頻 = 0 (零差, NOP 語境)
  s = 2i   → 和頻 = 4sin(iπ/88) = 2ω_i (自耦合)
  
位置: 44×44 master_atlas 對角線, 44 格 (2.3%)
```

## 2. ★ 核心發現: Self Loop = SYNC 指令

```
sum(i,i) = 2ω_i = DUP+ADD(ω_i) = SYNC(ω_i)

self loop 就係 SYNC opcode 作用喺單一模式:
  LOAD ω_i → DUP → ADD → 2ω_i
```

### Degree 一致性 (44/44 ✅)

| 量 | 公式 | 驗證 |
|:---|:---|:---|
| deg(sum(n,n)) | = deg(4sin(nπ/88)) | 44/44 = deg(ω_n) ✅ |
| deg(ω_n) | φ(176/gcd(\|44−n\|,176))/2 | — |

**2ω_n 係 ω_n 嘅有理倍數 → SYNC 唔增加代數複雜度。**

## 3. ★ 對比: 拍頻 vs Self Loop

| | 拍頻 (i≠j) | Self Loop (i=i) |
|:---|:---|:---|
| 數量 | 946 | 44 |
| d | j−i ≠ 0 | 0 |
| degree | **lcm(deg_i, deg_j) 可提升** | **deg_n 唔提升** |
| 語義 | 組合指令 (兩個模式干涉) | 單一指令 (SYNC 自己) |
| 值 | \|ω_i − ω_j\| | 2ω_i |
| 閉合根式 | 6 個 (全含 11/22/33/44) | 4 個高對稱 (n=11,22,33,44) |

## 4. 特殊 self loop (高對稱, 閉合根式)

| n | SYNC(ω_n) = 2ω_n | 閉合形式 | deg | 意義 |
|:---:|:---|:---|:---:|:---|
| 11 | 1.5307337295 | 2√(2−√2) | 4 | 高對稱 |
| 22 | 2.8284271247 | **2√2** | 2 | 半節點, v_g=c |
| 33 | 3.6955181300 | 2√(2+√2) | 4 | 高對稱 |
| 44 | 4.0000000000 | 4 | 1 | Nyquist, 有理 (唯一 deg=1) |

**n=22 self loop = 2√2 — 全表唯一 deg=2 元素, 同 (22,44) 拍頻 = 2−√2 形成 pair:**
```
self loop (22,22): 2√2 ≈ 2.82842712  (γ_22 = 2 嘅 2×)
拍頻 (22,44):     2−√2 ≈ 0.58578644  (γ_11 值!)
```

## 5. ISA 語境

```
Runtime ISA: IDL (IDLE) — 空轉 N ticks
             → self loop d=0 可視為「模式自身保持」= IDL 語義
Boot ISA:    SYNC = DUP+ADD (cost 2, thermal)
             → self loop sum = 2ω_i 就係 SYNC 執行結果
```

**Self loop 唔係 NOP — 佢係「模式對自己執行 SYNC」, 產生 2ω_i 嘅自耦合能量。**

## 6. 誠實標記

| 項目 | 狀態 |
|:---|:---|
| 44 個 self loop 存在 | ✅ master_atlas 對角線 |
| sum = 2ω_i = SYNC(ω_i) | ✅ 恆等式 |
| deg(self loop) = deg(ω_n) 44/44 | ✅ 驗證 |
| self loop = IDL (空轉) 語義 | 🟡 推斷, 未閉合執行語義 |
| self loop 嘅物理對應 (自耦合 = 質量?) | 🔴 未推導 |

## 檔案

```
self_loop.py      — 44 個 self loop 全表 + 語義
self_loop_deep.py — degree 一致性驗證 (44/44 ✅)
```
