# O235 docs/03 — T3: tick 相位 → 輕子槽 ≡1 (mod 4) — 第二條獨立機制鏈（2026-10-07）

> **Script**: `scripts/03_tick_phase_T3.py`（20/20 PASS, numpy + math）
> **Log**: `logs/03_tick_phase_T3.out`
> **verdict**: 🟡 機制層閉合（tick-相位鏈）——「≡1 而唔係 ≡3」由 **deficit 類選取規則**
> （預註冊 R4）命中；**B−L 整數性（O210 T3）完全唔入入力** ⟹ 獨立機制鏈。
> ⚠️ 統計層唔變（1/56 nominal / look-elsewhere 0.1204 = O233 結論, 本 T3 只加機制);
> O210 common-measure no-go 冇被推翻（本鏈唔做數值層對齊）。

## 一、tick 相位 ℤ₄（A1–A3）

```txt
🟢 Ŝ = S²² (半環平移 = 22 ticks = 一個相位四份一): Ŝ|k⟩ = i^k|k⟩ (maxerr 2.45e-14)
   ⟹ 類 r (k ≡ r mod 4) = Ŝ 相位 rπ/2 本徵空間 —— 「tick 相位 r」嘅算子身份
🟢 四類各 22 模: 88/4 = 22 ticks/相位 = B=4 期步驟數 (ℤ₄ 階 = 分支數相合)
```

## 二、類層 world/observer 配對（B1–B2）

```txt
🟢 Σ(s0∪s2) [even k] = 90 EXACT = 世界 (O34 Σγ_even)
🟢 Σ(s1∪s3) [odd  k] = 88 EXACT = 觀察者 (O34 Σγ_odd)
⟹ 奇-tick 類對 = 觀察者側; 偶-tick 類對 = 世界側 (類層 O34 配對, 新事實)
```

## 三、deficit 向量（C1–C6, 全部 EXACT）

```txt
🟢 (Σs0−44, Σs1−44, Σs2−44, Σs3−44) = (μ², −sec(π/88), 0, +sec(π/88))
      = (+2, −1.000637580593, 0, +1.000637580593) —— 對上 O233 docs/13 §四 ① 鏈側缺陷
🟢 s1 (≡1) = 唯一虧缺類 (Σ < 44, 負向); s3 (≡3) = surplus; s2 = 44 EXACT 整數;
   s0 = 44 + μ² (k=44 自對模 ∈ s0)
🟢 k→88−k 對偶: s1↔s3 互換、s0/s2 自對偶 —— (s1,s3) = 唯一對偶相 (87 pairs ok;
   k=88 邊界 dual=0)
```

## 四、假説測試（D1–D5, 預註冊 R4）

```txt
預註冊規則 (見數前寫死): 若鋸齒 Z₂ = tick 宇稱 ⟹ 輕子流 (O233 odd-flow)
  必須落喺 observer 對 {s1,s3} 內嘅 deficit 類 s1 (≡1) —— 3/3, 唔落 s3 (≡3)。

🟢 D1 輕子 {e,μ,τ} 3/3 落 s1 (≡1), 唔落 s3 —— R4 命中 (residues {1,1,1})
🟢 D2 夸克 5/5 避開 s1 (residues {2,3,0,3,3}; partition 守恆 = O233 T4=1/56 對偶)
🟢 D3 s1∩費米子模 = {1,5,9,13} = 輕子³ + t(VEV-exempt) —— 類全滿, 冇多冇少
🟢 D4 B−L 獨立性: 輸入 = {γ_k 類和, O34 觀察者/世界標籤, O233 流指派}
   —— 冇用 B−L 整數性 / Q mod 4 算術 (O210 T3 機制完全隔離)
🟢 D5 統計誠實: P = C(3,3)/C(8,3) = 1/56 nominal; look-elsewhere 0.1204 不變
```

## 五、硬測試（E1–E5）

```txt
① 零參數 ✅ (輸入全部既有)
② MC N/A: 機制層, 統計不變 (D5 已明示)
③ 可證偽 ✅ 家族規則「ℤ₄ 四類平衡 ⟺ M ≡ 0 (mod 4)」—— M=86,90 四類不平衡
   ⟹ 槽位結構喺 M≠0 mod 4 唔存在 (結構要求, 非後驗)
④ 剛性 ✅ deficit 類對 M∈{84,88,92} 保持 (s1 虧缺 / s3 surplus 穩定)
```

## 六、判決（誠實分層）

```txt
✅ T3 機制層閉合:
  「點解 ≡1 唔係 ≡3」= tick 相位鏈: 奇 tick 側 (observer, Σ=88)
  ⟹ 輕子流必須落 observer 對 {s1,s3}; ℤ₄ 相位 1 (Ŝ 本徵 i) 嘅類 s1
  = 唯一虧缺類 (Σ = 44 − sec < 44) ⟹ deficit 選取 —— 預註冊 R4 命中。
  同 O210 T3 (B−L 整數性) 係**兩條獨立機制** (輸入集無交集)。

🟡 誠實邊界:
  • 機制層非定理層 —— 「deficit = 輕子側」係選取規則 (預註冊), 唔係算術強制
  • 統計層完全冇改善 (1/56 / 0.1204 = O233 原狀) —— T3 係機制支持, 唔係新證據
  • O210 docs/11 common-measure no-go: 本鏈唔做鏈↔算子數值層對齊, 冇推翻
  • assignment {1,5,9} 係 O233/O137 R22 已授權輸入 (本 O 唔重推)
⟹ 合成評級: T2×T3 令 O235 假説嘅 mechanism 層完整 (tick 宇稱 + 相位選取),
  統計層維持 O233 裁決; 升 🟢 要樣本外盲測 (見 closeout 規劃)
```

## 七、產物

- `scripts/03_tick_phase_T3.py`（20/20 PASS）+ `logs/03_tick_phase_T3.out`
- 引用: O234 docs/03 凍結層規則 (無質量數字混入); O210 docs/10 (Ŝ iso),
  docs/11 (common measure no-go); O233 docs/12/13/14 (槽位/流/LE)