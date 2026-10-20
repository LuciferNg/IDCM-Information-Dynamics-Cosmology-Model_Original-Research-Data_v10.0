# O255 — c 結構上限 → no-signaling: 色散結構必然 v≤c, 非時空公設

<!-- registry
pid:     O255
title:   c 結構上限 → no-signaling: 色散結構必然 v≤c, 非時空公設 (O254 scripts/03 概念結論)
state:   registered
verdict: -
flags:   -
owner:   O255
created: 2026-10-20
updated: 2026-10-20
prereq:  O73（c 第一性原理）, O254（scripts/03 + 否證）
source:  O254 概念答覆 → 立項（用戶指示: 只開不推）
-->

> **狀態**: 📄 **已註冊 — 未開始（只開不推, 2026-10-20, O252 先例）**
> **建立**: 2026-10-20
> **前置**: O73（c 第一性原理: 光 = W-field Goldstone 相位模）、O254（scripts/03 + docs/01-03）
> **位置**: `open_problems_fresh/o255_c_structural_no_signaling/`

## 一、問題

兩個粒子之間係咪永遠無法以超越 c 嘅速度交換信息？——O254 概念答覆指出：**喺 IDCM 結構層，呢個係定理而唔係經驗公設**：

```
K_Chain 色散:  ω_n = 2 sin(πn/88),  γ_n = 4 sin²(πn/88)
群速度:        v_g(n) = dω/dk = cos(πn/88)

n=0 (Goldstone)  v_g = 1 = c      ← 唯一達 c（零色散, O73 §10）
n=1  v_g ≈ 0.9994 < c
n=22 v_g ≈ 0.7071 < c
n=44 (Nyquist)  v_g = 0          ← 駐波端
```

資訊交換需要「局部自由度差異嘅可分辨傳播」→ 載體必須係有色散模（非零模）→ **v ≤ c 結構必然**。

## 二、核心區分（已確立, 見 O254 scripts/03）

| | 存在 | 速度 |
|:--|:--|:--|
| **關聯**（共享 Goldstone 相位 / W-field 凝結全域相干） | ✅ 即時 | 非局域（EPR/Bell 型對應） |
| **信息**（A→B 選擇性編碼, 可分辨） | ✅ 但 ≤ c | 載體必有色散 → v < c（最高 = c, Goldstone 但無局部分辨能力） |

即：**no-signaling 唔係禁令，係結構定義**——資訊載體本身一定係有速度嘅模式。

## 三、範圍（本 O 只開不推 — 待辦在推嘅時候）

- [ ] 完整論證立項：由 K_Chain 色散嚴格推導 v≤c（scripts/03 係概念驗證, 非完整證明）
- [ ] 同 SR「c 為時空公設」對比：IDCM 由結構推出 c, 唔係由 frame 幾何假設
- [ ] EPR/Bell 對應結構：Goldstone 相位關聯 vs 資訊不可超光速 — 詳細結構
- [ ] no-communication theorem 嘅 IDCM 翻譯（關聯可即時 / 資訊必亞光速）
- [ ] c 上限係咪嚴格 v_g ≤ c 於所有 K_Chain 派生系統（O149 v_g locking 相關）
- [ ] N 偶偶數/其他色散（半整數 shift, 相關 O）嘅 v_g 行為

## 四、禁區
- **本 O 未開始攻堅前禁寫 scripts/推導**（用戶指示: 只開不推）
- 唔好「證明 SR」——係「證明 IDCM 結構重現 c 上限」, 兩回事
- 唔好引用外部模型當證據（文獻聲稱需獨立重算）

## 五、狀態
```text
state:   registered（只開不推）
verdict: -
來源:    O254 概念答覆 + scripts/03 (3/3 PASS)
```