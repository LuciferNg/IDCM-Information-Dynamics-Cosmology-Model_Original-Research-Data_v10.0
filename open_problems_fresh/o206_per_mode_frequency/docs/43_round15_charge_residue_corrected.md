# O206 — 第十五輪 docs/43: Charge-Residue 更正 + 輕子槽成因語境（3 PASS / 0 FAIL）

> **日期**: 2026-10-06 · **Script**: `scripts/39_charge_residue_corrected.py`（**3 PASS / 0 FAIL**）· **Log**: `logs/39_charge_residue_corrected.out` · **Data**: `data/39_charge_residue_corrected.json`
> **承接**: 第十四輪 docs/42 B4 residue 表——**⚠️ 發現表有錯誤**（≡3 中 c 誤標 down-type）。「一次過」⟹ 更正 + 成因語境 + up/down 分析一次過。
> **verdict**: **①更正：≡3 = {d(down), c(UP), b(down)}**——c 係 up-type，docs/42「d,c,b 全 ≡3」誤導；實際 down-type {d,s,b} = {3,0,3}（2/3 ≡3, s 例外）、up-type {u,c,t} = {2,3,1}（3 個全唔同）；②**下型/上型嘅 residue 結構喺 H0 下都唔稀有**（up 3 distinct p=0.369、down 含 ≡0 p=0.333）——**唯一 charge-residue 顯著結構仍然係「輕子全 ≡1」**；③成因語境：88-chain 半週期平移 γ_{n+44}=4−γ_n 保持 residue（44≡0 mod 4）、4=B 分支數（O210: k≡±|B−L| (mod B)）——**語境, 唔係新證明**；「點解輕子佔 ≡1 唔係 ≡3」仍然未解。

---

## C1. ★ 更正（append-only, docs/42 原文唔改）

docs/42 B4 寫「輕子+t 全 ≡1（4/4）；d,c,b 全 ≡3（3/3, s 例外）」——**錯誤**：c(7) 係 up-type（+2/3）。

**正確 residue 表**（R19 assignment）:
```
n ≡ 0 (mod 4): [s(4), down, -1/3]
n ≡ 1 (mod 4): [e(1), μ(5), τ(9)] 全輕子 -1  ＋  [t(13), up, +2/3, VEV]
n ≡ 2 (mod 4): [u(2), up, +2/3]
n ≡ 3 (mod 4): [d(3), down, -1/3]  [c(7), UP, +2/3]  [b(11), down, -1/3]
```

- **down-type {d,s,b}**: residues {3, 0, 3} —— 2/3 ≡3；s≡0 例外
- **up-type {u,c,t}**: residues {2, 3, 1} —— 3 個全唔同
- **輕子 {e,μ,τ}**: residues {1,1,1} —— 全 ≡1（O14 正結果維持）

## C2. 輕子槽成因——語境（唔係證明）

- **88-chain 半週期平移**: γ_{n+44} = 4sin²((n+44)π/88) = 4cos²(nπ/88) = **4−γ_n**（exact）；
  44 ≡ 0 (mod 4) ⟹ **半週期平移保持 residue 類**——毎個 residue 槽喺 88-chain 有兩個半週期對 (n, n+44)
- **4 = B 分支數**（O210-T1: k ≡ ±|B−L| (mod B)）——槽數 = 分支數 = 4
- **O158 先例**: 45族 a奇/47族 a偶 mod-4 方向判準（docs/15, 19/19; docs/18, 18/18）
- **O148 先例**: mod-4 扇區閉式
- ── ⟹ 輕子槽 ≡1 **落入 mod-4 既有家族語境**（唔係孤立巧合），但
  「點解輕子揀 ≡1（而唔係 ≡3 / 其他）」嘅機制**未解**——需要 O137 手性橋／O139 銜接

## C3. up/down residue H0 分析（3 PASS）

| 問題 | H0（MC 10⁶ / 組合） | p | 結果 |
|:--|:--|:--|:--|
| up-type 3 個全唔同 residue | 隨機 3 位試 9 mode | **0.3690** | ✅ 唔稀有——唔係 anomaly |
| up-type 3 個全相同（對照） | 同上 | 0.0605 | — |
| down-type 含 ≡0（s 落唯一 ≡0 槽） | 隨機 3 位 | **0.3333** | ✅ 唔稀有 |

- ⟹ **「up-type 冇固定 residue」/「s 落 ≡0」都係 H0 內正常**——唔好當 anomaly 去追
- 唯一真係稀有嘅 charge-residue 結構 = **輕子全 ≡1 mod 4**（O14: p=0.0476/0.0179）

## 總結（誠實）

- docs/42 B4 錯誤已更正（c=up-type）——實際唔影響 O14 主結論（輕子 ≡1），但影響「d,c,b 全 ≡3」喺 doc 內嘅詮釋
- **輕子槽 ≡1 係唯一 charge-residue 顯著結構**；其餘（up 3 distinct、s≡0）喺 H0 內正常
- 成因仍開放：半週期平移 + 4=B 提供「點解 4 個槽」嘅語境，「點解輕子佔 ≡1」未解

**戰局更新**：
- C_f 正結果維持 5 項（鋸齒 / 階梯 T / 獨立同時極端 / u/d 身份穩健 / lepton ≡1 mod 4 槽）
- 🔴 未解：輕子槽成因（點解 ≡1 唔係 ≡3）——候選銜接 O158（45/47 判準）、O210（B−L mod B）、O137 手性橋
- 🟢 已關：up-type 3 distinct（H0 正常）、s≡0（H0 正常）、κ 非對角（載體失格）
- 🟡 已更正：docs/42 B4（c 標錯 type）

## 文件動作

- scripts/39 + logs/39 + data/39 json + docs/43（本文件, 更正層）。
- docs/42 **原文零改動**（append-only 紀律）；本文件為更正。
- SESSION_START append（第十五輪節）· README O206 行 round-15 更新 · register O206 note。