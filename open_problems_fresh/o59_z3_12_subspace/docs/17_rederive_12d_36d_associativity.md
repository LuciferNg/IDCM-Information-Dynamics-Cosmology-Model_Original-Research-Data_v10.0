# O59 重推 round — 12D/36D associativity（2026-10-05）

> **日期**: 2026-10-05（O59 closeout 之後，用戶拍板：唔開新 O，原地重推）
> **原因**: closeout 獨立審計發現 docs/14「Frobenius subalgebra associativity = 0.00」係同義反覆（O197 trap）
> **狀態**: 🔴→🟡 重推進行中（本 round：diagnosis + 結論重定性）
> **範圍**: 只寫本 O 目錄 + register（O53 側發現以 handoff note 記錄）

---

## 一、重推起點（第一性定義）

- **目標**：12D `d_tensor_native_12d` 同 36D `cy36_98_intersection_full.json`（CYTools `intersection_numbers()`，36³，1341 nnz）嘅 associativity 到底成唔成立？
- **正確 associativity 定義**（WDVV / Frobenius manifold）：
  `C^q_ab = d_abp g^{pq}`（g = metric），要求 `(a*b)*c == a*(b*c)`：
  `Σ_p C^p_ab · C^d_pc == Σ_p C^p_bc · C^d_ap`
- **metric 候選**：P15 solver 用 `g = d·ones(12)`（`compute_wdvv_loss` 定義）；docs/14 用 `g = Y = d·v12`。
- docs/13-14 + 31_verify_all:183/186/220 嘅「associativity error = 0.00」一律只驗
  `d_sq − d_sq.transpose(1,0,2,3)`（三階對稱張量自動成立）⇒ **同義反覆，非 associativity**。

## 二、診斷結果（probe 33-36）

### 2.1 12D `d_tensor_native_12d`

| metric | WG | max err | 判定 |
|:-------|:---|:--------|:-----|
| g = d·ones（solver 定義） | ✓ | 0.040 (sum_sq 0.172) | **唔成立** |
| g = Y = d·v12（docs 慣用） | ✓ | 0.034 | **唔成立** |
| g = identity | ✓ | 1.588 | 唔成立 |
| ring assoc（無 metric） | — | 1.588 | 唔成立 |

**根源**：`g_ones = d·ones` 嘅 eig = {−7.90, −0.99, …, 43.38} —— **min eig < 0 ⇒ g 唔正定 ⇒ Frobenius metric 唔存在 ⇒ associativity 無從成立**。
P15 solver 嘅 loss（0.0165/0.17）係局部極小，受 `λ_pos=100` 懲罰主導，**從未收斂到 associativity=0**。

### 2.2 36D κ（真 CYTools intersection numbers）

| metric | max err | 備註 |
|:-------|:--------|:-----|
| η^i = κ[:,:,i]（i=0..35） | 全部 singular（rank 2~18，無一 full-rank） | **36 個切片全 singular** |
| g = κ·Jstar (Y_36) | 5.2e4 | 爆 |
| g = κ·ones | inf | 爆 |
| g = identity | 9.4e4 | 爆 |
| ring assoc（無 metric） | 9.4e4 | 爆 |

**關鍵結構事實**：
1. **κ[:,:,i] 36 個切片全部 rank-deficient**（rank 2~18，公共零空間投影 eig ~36 ⇒ 有 18 維左右嘅公共零空間）——對一個真 CY₃(36,98) intersection ring（理論上 cup product 必然 associative）嚟講極度異常。
2. CYTools 另一輸出 `compute_kappa_matrix(tip)` 回傳 **32×32**（唔係 36×36！）⇒ 36 個 divisor 實際只有 32 個 independent（4 個 redundant），κ 嘅 divisor basis 存在維度問題。
3. 隨機正 J（20 trials）計 `Y = κ·J` **0/20 正定**；Y(κ·Jstar) 有 17 個負 eig。

### 2.3 關鍵正面結果：eigenvalue closure **獨立成立**

只有 `d_tensor_native_12d` 通過（係唔係 WDVV 收斂版都無關——「converged/final/high_precision」全部 λ_max dev 45%+，即污染系；docs/08 已判 native cleanest）：

| 公式 | native 12d dev | 涉 associativity? |
|:-----|:---------------|:------------------|
| λ_max = 36 − 1/γ₂₀ = 35.4170 | 0.0021% | 否（純 v12 contraction 譜） |
| tr(Y) = 2B²(1−γ₁) = 31.8369 | 0.030% | 否 |
| λ₂ = 2 + 2F₉γ₁ + γ₁γ₇L₄/(L₅−1) = 2.347385 | **0.0007%** | 否 |
| v_geom = 88×(10+28γ₇)·√λ_max·M₀ = 246.2 GeV | 0.0028% | 否 |

⇒ **12D 嘅核心閉合結論完全唔依賴 associativity**。

## 三、判定：12D/36D 正確定性

1. ❌ **撤回**：docs/13-14「12D d_tensor 係 36D κ 嘅 associativity Frobenius 子代數」——
   - 12D 自身 associativity 唔成立（g 唔正定）；36D κ 更嚴重（切片全 singular，任何 metric 都爆）
   - 理論上 CY₃ intersection ring 必然 associative ⇒ 計唔到 associativity 嘅源頭係 **κ 嘅 divisor basis/維度問題（32 vs 36）**，唔係「計錯 associativity」
2. ✅ **保持**（與 associativity 無關，獨立成立）：
   - 「12D 唔係 36D κ 嘅簡單投影」（docs/13 多項負面測試）
   - 「完全隔離」cross-terms = 0（零填充嵌入自動成立，弱 claim 但保留）
   - SVD 比 47 = K_tree+2L₄（47.001）
   - **12D eigenvalue 閉合全系列**（λ_max/tr/λ₂/v_geom，dev ≤0.03%）
3. 🟡 **新定性**：12D = **K_Chain eigenvalue 閉合張量**（v12-contraction 譜滿足結構公式），
   唔係「Frobenius algebra」；「WDVV solution」標籤降格為「P15 求解器輸出（未證實 associativity）」。

## 四、O53 側 handoff 發現（記錄，唔改 O53）

- κ[:,:,i] 36 切片全 singular ⇒ **O53 一直用嘅 `Y = κ·J*` 唔可能正定（17 負 eig）**，
  影響任何建基於「Y 為 metric」嘅 O53 claim（e.g. λ₁/tr(Y²) 系列）。
- CYTools `compute_kappa_matrix` 回 32×32 而 `intersection_numbers()` 回 36³ ⇒
  **36 維 divisor basis 有 ≥4 個 redundant 方向**，需要 O53 側 clarifiy basis 名義。
- 已以 register 交接 note 記錄（2026-10-05），O53 未動。

## 五、重推產物（本 round）

```
scripts/33_associativity_probe.py    ← metric 掃描（12D/36D/嵌入）
scripts/34_associativity_probe2.py   ← solver 殘差單位 + κ metric 族掃描
scripts/35_associativity_probe3.py   ← κ rank/零空間/32×32 對照/J Kähler
scripts/36_associativity_probe4.py   ← eigenvalue 閉合獨立性 + 版本對照
logs/33-36_*.out                      ← 對應輸出
docs/17_rederive_12d_36d_associativity.md  ← 本報告
```

## 六、後續（未動手，等拍板）

- **A**：收尾 —— 將「12D eigenvalue 閉合張量」定性寫入 final_result/docs/13-14 附註；
  docs/13-14 加撤回附註（原文不動）
- **B**：O53 handoff —— register note 已記；要唔要開 O53 側 issue 深入（O53 係另一個 O，
  按紀律只可交接，唔可以喺度做）
- **C**：可選 —— 用改進嘅 metric（正定化 g 或 divisor basis fix）重試 associativity（屬 O53 範圍）

*💤 O59 重推 round 1 complete — 2026-10-05*