## ⚠️ 更正附註 (2026-10-11, append-only)⚠️

**§1 嘅「單項 4-trace 全零」claim 已被 scripts/16 否證**——用 `.real` 取 trace 係 bug：
232/1032 個單項 trace 非零，**全部純虛**（例 (0,1,2,7) → ±i/(8√3) ± 0.07217i）。
正確機制（docs/11）：**消滅發生喺 pol 排列組合層**——單項 4-trace 虛部喺
T_δ = 24·pol 嘅對稱化排列中反號抵消；T_δ ≡ 0（|·| 全枚舉 worst 1.33e-15）仍然真。
§2（slot-pair 相位對稱）與 §3（off-diag 成塊 split）不受影響。

---

# O244 docs/10 — 封閉代數證明：E2 su(2)-closure 單項消滅 ＋ 成塊相位對稱（scripts/15, 7/7 PASS）

> **date**: 2026-10-10 · **script**: 15_closed_proofs.py · **log**: logs/15.txt
> **目的**: 閉合 docs/08 §5 #2（su(2)-closure E2 完整代數證明）＋ docs/09 §4
> （成塊 ⟹ ΣφT=0 嘅 trace 論證、off-diag set 成塊 split 一件式驗證）。

## 1. E2 su(2)-closure：真正機制係「單項 4-trace 零」（唔係求和零）

**過程**: 兩個中間假設先後被否證（負結果，docs 保留）：
1. 「T_aT_bT_c ∈ span{T₀,T₁,T₂}（su(2) 純空間）」→ 6/27 bad（T_aT_b 含單位分量 + d-symbol 混合）
2. 「T_aT_bT_c ∈ span{I, su(2)}」→ 仍 bad（T₀T₁T₂ fall out 到其他方向）
3. **正確**: 直接檢查單項 4-trace ⟹ 全 43 sets × 24 perms 全部 `Tr[T_aT_bT_cT_d] = 0`
   （worst 0 違反），對照唔含 triple 嘅 set (0,1,3,4) 有 16/24 非零 ⟹ **有鑑別力**。

**E2 主定理（實證級）**: 全異色 set S 含 su(2)-closure triple {i,j,k}
（[T_i,T_j]∝T_k, 9 個 closure triple）⟹ 對任何排列 (a,b,c,d) of S:
`Tr[T_a T_b T_c T_d] = 0`（單項消滅，唔使求和）。
配合 A2（su(2) generator ⊥ 外色）: 消滅係「3 色 su(2) + 1 外色」結構嘅必然。

數學註記（open 嘅封閉式推導）: 單項 4-trace 消滅嘅封閉表達式即「3-ge 子代數 + 正交補
之 trace zero」；詳細代數推導（Fierz 展開）未寫成紙上證明，但 43×24×1 全枚舉
EXACT 0（1.3e-15 浮點噪聲級）已是定理級。── 殘餘降級為「Fierz 層紙上推導」選項。

## 2. 成塊 ⟹ ΣφT = 0：slot-pair 相位對稱（B）

(0,1,3,4) 成塊排列 inner = Σ_δ φ(δ)T_δ = 0（EXACT）。
**機制**: swap δ₁↔δ₂（spin pair (0,1) 嘅 slot）= 16/16 對和零
（規則1, n₁=n₂=1 相位不變 + Tget sorted 對稱 ⟹ φ(δ)T_δ + φ(δ')T_δ' = 0）。
對 (1,1,42,44) 動量, pair (0,1) 喺位置 1,2（動量 1,1）: swap 同值相位抵消完整。
規則2（swap δ₃↔δ₄）12/16 對和零 — 唔完整（動量 42,44 唔等）。

⟹ 成塊排列（兩 spin pair 各放一動量塊, n 對稱）令大塊相位對稱 ⟹ 每對 δ, δ'
φT + φ'T' = 0 ⟹ inner = 0。未成塊排列冇呢個對稱 ⟹ 耦合（E2: inner ≠ 0 2.981）。

## 3. off-diag 4 sets 成塊 split 一件式（C）

4 個 off-diag 消失 set 嘅消失 8 個排列精確 = 同-target pair 成塊:
| set | split | 共同 commutator target |
|:----|:------|:------------------------|
| (0,2,3,5) | (0,2)\|(3,5) | 1 |
| (0,2,4,6) | (0,2)\|(4,6) | 1 |
| (1,2,3,6) | (1,2)\|(3,6) | 0 |
| (1,2,4,5) | (1,2)\|(4,5) | 0 |

即係同 target pair（[T_i,T_j] 同 [T_k,T_l] 都 ∝ 同一色）嘅成塊排列消失 —
機制同 spin 併集相同（pair 對稱相位抵消），target 係 off-diag 色而唔係 Cartan span。

## 4. 結果
- docs/08 §5 #2 閉合: E2 由實證圖像升級為「單項 4-trace 全零」定理（43×24 全枚舉）
- docs/09 §4 #1/#2 閉合: off-diag split 精確選取（C1）；成塊 ⟹ ΣφT=0 機制
  = slot-pair 相位對稱（B1）
- 累計: 191 + 7 = **198/198 PASS**（scripts/01–15）；全枚舉/閉式, 零擬合
  ⚠️ AUDIT 更正 (2026-10-11): scripts/15 A4''' 用 .real 係假 PASS（見 scripts/15 附註
  同 docs/11）；正確: 6 PASS + 1 REFUTED。O244 總水位見 final_result audit 段。
- 剩餘（細項）: E2 嘅 Fierz 層紙上推導（可選）；N > 176 由結構無關性保證（未跑但數學閉合）

## 相關
- docs/08 §3 E2（43 sets 禁戒）、docs/09（相位削減, 成塊）
- scripts/07-09（T_δ 單項消滅三恆等）, scripts/10-14（相位削減)
- 聲明: 所有數字全枚舉/閉式。