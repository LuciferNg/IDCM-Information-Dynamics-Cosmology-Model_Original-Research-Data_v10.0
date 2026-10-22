# O237 docs/13 — sin(πℓ) 機制攻堅：K_tree 固定點 = 徑向核（𝒯 雙側 link）

> **日期**: 2026-10-07 · **狀態**: 🟡 U1 機制攻堅（兩個新 hard link；formal 推導仍 🔴）
> **腳本**: `scripts/16_sin_pi_ell_mechanism.py`（9/9 PASS）＋ log
> **前置**: O170 docs/11（0.7116 裁定＋sin(πℓ) 機制剩餘 🔴）、O210（K_tree 譜）、O237 docs/12

---

## 一、問題

O170 docs/11 剩餘 🔴：`n_c(ℓ) = 22 + B·sin(πℓ)`（arch 徑向取樣核中心）嘅 **formal 譜推導**。形式差異：K_tree 譜係 sin²(kπ/68)，O170 用 sin(πℓ)——點解 fundamental harmonic？

## 二、新 hard links（scripts/16, 9/9 PASS）

### L1: √λ₁₇ = √2 = M(0) ★

```
K_tree 固定點 k=17:  λ₁₇ = B sin²(17π/68) = 2 = μ² = B/2
√λ₁₇ = √2 = M(0)   ⟵  O170 徑向核 M(ℓ→0) = √2 (docs/11 S1 ⑤)
```

**徑向核 M(0) 就係 K_tree 譜固定點嘅 beat**（√λ = 2sin(kπ/68)）。唔係獨立公設，係 K_tree 譜固有。

### L2: √λ_k = 2 sin(kπ/68) — K_tree beat 譜同 88-ring 同形

√λ_k 同 b_n = 2sin(nπ/88) 結構一致（分母 68 vs 88）——K_tree 譜係同一弦長代數嘅另一分母實例（68 = 4(B²+1)）。

### L3: sin(πℓ) 倍角 = 2 sin(πℓ/2)cos(πℓ/2)

sin 軌跡可以寫成兩 beat 乘積——形式上可歸 beat 代數（omitted cos 因子 = 相位）。

### L4: n_c 邊界約束全 chain 數

| 邊界 | 值 | Chain 身份 |
|:-----|:---|:-----------|
| n_c(0) | 22 | γ₂₂ = μ² = B/2 = 2 中心模 |
| n_c(1) | 22 | 1+z = 4 = B 第一層邊界返回 |
| peak ℓ=½ | 26 = 22+B | = 2F₇（F₇ = 13 = O145 v₂=2 層 Σγ） |
| 振幅 | B = 4 | 分支度 |

### L5: fundamental m=1 鎖定

- C1 峰值 @ ℓ=½：sin(mπ/2)=+1 ⟹ **m ≡ 1 (mod 4)**
- C2 ℓ→1−ℓ 偶對稱：m odd ✓
- m ∈ {1,5,9,...}；**m=1 係 fundamental（最小正解）**——同 O170 minimality 論證一致

### L6: λ₁₇ = γ₂₂ = 2 ★ — K_chain/K_tree 中點模共享

```
K_tree 固定點能量 = K_chain 中心模能量 = 2 = μ²
⟹ 𝒯 = K_chain ⊗ K_tree 喺「中點」共享同一譜值
```

呢個係 sin(πℓ) 機制嘅 𝒯 源頭候選：arch 軌跡由兩譜中點模共享而唔係獨立公設。

## 三、誠實標記

- **閉合咗**：M(0) = √λ₁₇（K_tree 固定點 beat）；n_c 邊界全 chain 數；fundamental 論證（C1+C2+minimality）formal 化
- **仍然 🔴**（O170 自己標記，本 O 唔 pretend）：點解 sin 唔係 sin²；點解振幅 B（唔係 √B 或其他）；由 K_chain⊗K_tree 配分正式推導 n_c

## 四、意義

1. **U1 嘅剩餘 🔴 收窄**：「點解 M(0)=√2」已收到 K_tree 固定點（L1）；剩「點解 fundamental + 點解 sin 形式」
2. **同 docs/11 閉環一致**：全部投影參數（1−b₁, 1/v_g, √λ₁₇, ln4, 19/18）都係 chain 譜量——**中間層確認係空，訊號延長線＝譜函數**
3. 機制 formal 推導係 O170 級工作（需配分函數），唔喺 O237 範圍內 pretend 閉合

## 五、檔案

```
scripts/16_sin_pi_ell_mechanism.py   9/9 PASS
logs/16_sin_pi_ell_mechanism.out
docs/13_sin_pi_ell_mechanism.md    ← 本檔
```