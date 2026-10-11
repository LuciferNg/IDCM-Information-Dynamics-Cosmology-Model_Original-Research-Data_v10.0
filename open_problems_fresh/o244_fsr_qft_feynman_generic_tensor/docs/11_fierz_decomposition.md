# O244 docs/11 — E2 Fierz 層完整推導：單項 trace 虛部 ＋ pol 排列消滅（scripts/16, 5/5 PASS）

> **date**: 2026-10-11 · **script**: 16_fierz_decomposition.py · **log**: logs/16.txt
> **目的**: 完整化 E2 su(2)-closure 嘅 Fierz 層機制 + **更正 docs/10 嘅錯誤 claim**。

## ⚠️ 更正 docs/10（append-only 規則：原文保留，此為更正）

**docs/10 §1 宣稱「單項 4-trace 全零（43 sets × 24 perms）」——係錯嘅**。
scripts/15 A4''' 用 `np.trace(...).real` 判斷，而實際非零單項 trace **全部純虛**
（real = 0 令誤判為零）。scripts/16 用 |·| 重掃：
- 1032 個 perms 中 **232 個單項 trace 非零**（全部純虛，例 ±0.07216878i = ±i/(8√3)）
- 其餘 800 個先係真正零

**正確 E2 機制**（升級）:
```
禁戒 set ⇒ ∀δ: T_δ = 24·pol(...) = 0（EXACT, |·| worst 1.33e-15）
但單項 4-trace Tr[T_aT_bT_cT_d] 可以非零（純虛）
⟹ 消滅發生喺 pol 嘅排列組合層, 唔係單項層
```

## 1. Fierz 層結構（scripts/16 [B]）

對 su(2)-closure triple 內色 (i,j)：
- 對易子 `[T_i,T_j] = ±(i/2)T_k`（Hermitian 對易"±0.500" f-structure 確認）
- 平方 `T_i² ∈ span{I, T₂, T₇}` **∀ 8 色**（Cartan 全體, 0 bad）

⟹ 三 su(2) 色乘積: `T_aT_bT_c` 含 `T_aT_c` 型 pair → ±i T_k × T_j →
產品包含 i 因子（虛）︙單項 4-trace 虛部由此產生。

## 2. 代表 (0,1,2,7)（scripts/16 [C]）
24 perms 全部非零、全純虛、幅值 |±i/(8√3)| 對稱：
- (0,1,2,7) → +0.0722i; (0,2,1,7) → −0.0722i（swap 首二色 = 反號）
- 排列對稱性: trace 值 8 對 ± 完全配對 ⟹ 對稱化求和 Σ_σ → 0

## 3. T_δ = 0 嘅真正來源（pol 排列消滅）
```
T_δ = 24·pol(e_{8δ₁+a₁}, e_{8δ₂+a₂}, e_{8δ₃+a₃}, e_{8δ₄+a₄})
pol = (1/24) Σ_S (-1)^{4-|S|} Q4(Σ_{i∈S} X_i)
Q4(u,v) = Tr[(u-v)⁴] − Tr[[u,v]²]   ← real by construction
```
Q4 對 slot-swap 對稱（scripts/07）＋ Tr cyclic ⟹ pol 係**排列對稱化**；
單項 4-trace 嘅虛部（±i/(8√3) 對）喺 |S|-求和中反號相加 ⟹ T_δ real 且 0。
（Q4 嘅 .real 定義 + 排列 ± 配對 ⟹ 虛部結構性消滅）

## 4. 結果
- docs/10 E2 單項 claim **更正**: 機制 = pol 排列消滅（非單項零）
- 新證據: D1（|·| 全枚舉 T_δ worst 1.33e-15）+ A1（232 純虛 + 800 真零）
  + B1（Cartan 平方）+ C1（±i/(8√3) 配對）+ E1（mixed 先耦合）
- 累計: 198 + 5 = **203/203 PASS**（scripts/01–16）；全枚舉/閉式, 零擬合
- 剩餘: 無（docs/09 §4 全閉; E2 機制已 Fierz 層完整化; N>176 結構閉合）

## 相關
- docs/10（舊 claim, 依此更正）、docs/08 §3（E2 43 sets）
- scripts/15（A4''' 假 PASS 源頭——.real bug 教訓）
- 聲明: 所有數字全枚舉/閉式。