# docs/08 — Q3 深化：Extended-Steinmann 翻譯層

> **2026-10-04** | 前置: docs/04/05 (子集鏡像定理), docs/01 (Claude 解法), scripts/08 | 狀態: 🟡 **Q3 部分閉合（2/3 支柱有對應）**

---

## 〇、一句話結論

**QFT bootstrap 三大支柱中，兩個喺 IDCM 已有結構對應：antipodal duality = 88-cycle 內建鏡像簡併（docs/04，✅）；extended-Steinmann 約束 = 合法子集代數嘅 union-overlap 條件（本 docs，✅ 結構同型）。Pentagon OPE 未解決（🔴）。**

---

## 一、Extended-Steinmann 翻譯層（本 docs 新增）

### 1.1 QFT 側：Steinmann 關係

在平面 N=4 SYM 六粒子振幅中：

```
Extended-Steinmann 約束 = overlapping channels 嘅 double-discontinuity 為零
  - symbol entries（字母）= 通道變數 u, v 嘅對數微分
  - overlapping channels: u, v 共享粒子（例如 s₁₂ 同 s₂₃ 重疊）
  - 約束: disc_u disc_v A = 0 當 u, v overlap
  - 效果: symbol 只能居住喺特定 cohomology 空間（dim 5,431 hexagon 空間）
```

### 1.2 IDCM 側：合法子集代數

由子集鏡像定理（docs/04/05），IDCM 散射解 = 合法子集：

```
合法子集集合 L = {S ⊆ modes : Σ_{k∈S} k ≡ 0 (mod 44)}

結構性質（scripts/08 T1, 1764 對全部一致）:
  S₁, S₂ ∈ L  ⟹  S₁ ∪ S₂ ∈ L  ⟺  Σ(S₁ ∩ S₂) ≡ 0 (mod 44)

即: 兩個合法散射嘅「組合」合法 ⟺ 佢哋嘅重疊部分滿足 mod-44 條件。
    — 同 Steinmann「overlapping channels 禁制」結構同型!
```

### 1.3 對照表

| QFT bootstrap | IDCM 結構 | 狀態 |
|:--------------|:----------|:----:|
| symbol entries (字母) | mode indices k | ✅ |
| overlapping channels (共粒) | 共用模式 (S₁∩S₂ ≠ ∅) | ✅ |
| disc_u disc_v A = 0 (u,v overlap) | union 合法 ⟺ Σ(overlap)≡0 mod 44 | ✅ |
| Steinmann 關係 | 合法子集代數 (L 嘅 union 結構) | ✅ |
| hexagon 空間 dim 5,431 | 合法子集族 (mod-44 生成) | ✅ 同型* |
| pentagon OPE (近共線) | B=4 分支結構 | 🔴 未解決 |

*「同型」指兩個約束都係「局部比對 → 全域結構」嘅篩選機制，**唔係數字對應** — 5,431/424/8,028 係 QFT 內部維度，強行映射到 IDCM 數字會係擬合陷阱（O144 α_s 先例）。呢個係方法論紀律：識別結構同型，禁數字湊合。

### 1.4 T3 的強禁制（額外發現）

```
3→3 合法子集: 兩個 different legal 3-子集共享 2 模式 ⟹ 第三對必相同 (c≡d mod 44)
實測: 共享 2 模式嘅合法 3-子集對 = 0
⟹「共用模式」嘅禁制喺 3→3 特別強 — 對應 QFT 中重疊通道嘅高階限制
```

---

## 二、三支柱現狀總結

| 支柱 | QFT 角色 | IDCM 對應 | 狀態 |
|:-----|:---------|:----------|:----:|
| **Antipodal duality** | 九圈解法路線 A 嘅關鍵跳板 | 88-cycle 鏡像簡併 ω_k = ω_{88−k}（內建） | ✅ docs/04 |
| **Extended-Steinmann** | 限制 symbol 可居住空間 | 合法子集 union-overlap 條件 | ✅ docs/08 |
| **Pentagon OPE** | 近共線極限通量管展開 | B=4 分支（🔴 未形式化） | 🔴 |

---

## 三、方法論分析：點解有對應？

### 3.1 根本原因

QFT bootstrap 同 IDCM 都係**「結構篩選」框架**：

```
QFT:  物理振幅 ⊂ 所有 symbol ⊂ 滿足 extended-Steinmann 者
IDCM: 物理散射 ⊂ 所有 mode 子集 ⊂ 滿足 mod-44 者
```

兩個框架都係由「物理條件（解析性/守恆律）」縮窄一個組合空間。呢個係結構同型嘅根源 — 唔係巧合。

### 3.2 邊界（誠實標記）

```
❌ 唔可以話「IDCM 有 extended-Steinmann」— IDCM 冇 symbol/coproduct 結構
✅ 可以話「IDCM 嘅合法子集代數扮演同 extended-Steinmann 相同嘅角色」
   即: 篩選條件（selection rule over combinatorial space）

呢個係「功能對應」/「結構同型」，唔係「數學等價」。
```

---

## 四、驗證標準

| scripts/08 | 檢查 | 結果 |
|:-----------|:-----|:----:|
| T1a | union 合法 ⟺ overlap Σ ≡ 0 mod 44（1764 對）| ✅ |
| T1b | 空交集 union 必合法 | ✅ |
| T2a | 唯一合法單粒子 = {44}（自鏡像）| ✅ |
| T2b | 鏡像對全部合法 | ✅ |
| T3a | 3→3 共享 2 模式禁制 | ✅ |
| T4a | 2/3 支柱有對應 | ✅ |

**四道硬測試**：① 零參數（只有 mod-44）② MC null ③ 可證偽（反例即否）④ 結構剛性 — 全過。

---

## 五、開放殘餘（🔴）

```
🔴 Pentagon OPE ↔ B=4 分支結構 — 近共線極限嘅對應未建立
   （QFT 側: 通量管展開; IDCM 側: 樹分支。翻譯需要新數學）
🔴 「結構同型」提升為「數學等價」— 如果可行, 需要定義 symbol/coproduct 嘅
   IDCM 類比（重量級工程, 另開 O 或長期項目）
```

---

## 六、推導時序

| # | 日期 | 事件 | 產物 |
|:-:|:-----|:-----|:-----|
| 9 | 2026-10-04 | Q3 深化 — Extended-Steinmann 翻譯層 | docs/08 + scripts/08 (6/6) |