# O206 — 第十一輪(d) docs/07_: 鋸齒 Z₂ 三盲測（表現：3 PASS / 1 FAIL）

> **日期**: 2026-10-06 · **Script**: `scripts/07_z2_three_tests.py`（**3 PASS / 1 FAIL**）· **Log**: `logs/07_z2_three_tests.out` · **Data**: `data/07_z2_three_tests.json`
> **承接**: docs/06_ 確認鋸齒真身 = 奇偶 rank 分裂（Z₂），並提出「一源假說」（Z₂ = 位置算子 X 嘅同一結構）。「逐個做」——三個盲測一次過：T1 置換 null · T2 Z₂ 歸因 · T3 u/d scheme 壓力。
> **verdict**: ①鋸齒唔係「質量→模式升序指派」特有（1055/40320 = 2.6% assignment 都做到分裂）——但升序係其中一個；②**鋸齒跟 rank parity 唔跟 mode parity**（max resid 0.844 vs 0.928）——即每個 peak 都係 even rank，包括 c(n=7 odd)、b(n=11 odd)——但殘餘**唔係二值 ±σ** ⟹ 一源假說嘅「Z₂ 修正」形式被壓；③**u/d scheme 壓力 robust**（77.4% 保持交替 / 68.4% 保持完整分裂, MC 10⁶）。

---

## T1. 置換 null —— even/odd 分裂唔係升序指派特有（✅ 升序本身做到, 但唔唯一）

- 完全交替 assignment 數 = **2956 / 40320**（7.3%）
- even/odd 完整分裂（交替 + 兩子序列單調） = **1055 / 40320**（2.6%）
- 升序（質量↔模式正序）屬於分裂類：**True** ✅——但唔係唯一。
- **詮釋**: 鋸齒係「隨機 8 質量 vs γ-階梯」嘅偏普遍特徵（2.6%），唔係「升序指派」嘅識別標誌。
  升序指派嘅獨特性由另一 statistic 支持（O120/O206 8! 升序雙射 Σln block span, p=0.00117）——
  兩者係**唔同資訊**: 階梯 span 驗「塊加權」, 鋸齒驗「奇偶雙流」。

## T2. Z₂ 歸因 —— 跟 rank parity，但唔係二值修正（✅ 1/2）

- rank-parity 修正: σ=0.255, max|resid|=**0.844**（二次 base 1.099 → 改善 23%）
- mode-parity 修正: σ=0.171, max|resid|=**0.928**（base 1.099）
- ⟹ **rank parity 優於 mode parity**（確證: 每個 peak 都係 even rank；c 嘅 n=7 係 odd mode、b 嘅 n=11 係 odd mode, 但兩者都係 even rank 而 peak）
- ❌ 但 quad-base 殘餘 **唔二值**: even = {−0.25, +0.68, +0.60, −0.06}（有正有負）、odd = {+0.55, −1.06, −0.25, −0.21}
  ⟹ 鋸齒唔係「平滑 envelope + 二值 Z₂ ±」——**一源假說嘅「Z₂ 修正生成 C_f」形式唔成立**
- 修正方向: 鋸齒嘅「奇偶」係真實 rank 性質, 但修正幅度隨位置變（唔係常數 σ）。

## T3. u/d scheme 壓力 —— robust ✅

- 理論閾值: y_u − y_d = ln(u/d) + ln(γ₃/γ₂) > 0 ⟺ **u/d > γ₂/γ₃ = 0.44539**
- MC 10⁶（u∈U[1.8,3.5], d∈U[4.5,5.3], 其他固定）:
  - 完全交替保持 p = **0.7740**
  - u-peak 對（u>e 且 u>d）p = **0.7740**
  - even/odd 完整分裂 p = **0.6844**
- ⟹ 結構唔依賴 PDG u/d 中心值；即使 u/d 跌到範圍邊緣, 七成以上保持。
  （即：「u=2.16 啱好令 u>d」唔係结构 claim 嘅弱點——但 u/d=1.8/5.3 嗰 23% 崩潰區承認。）

## 總結（誠實）

| Test | 結果 | 意義 |
|:--|:--|:--|
| T1 置換 null | ✅ 升序係分裂類成員（1055 個之一） | 鋸齒唔識別升序指派——搵「指派之源」轉為「質量譜自身性質」 |
| T2 Z₂ 歸因 | ⚠️ rank>mode 確證, 但殘餘不二值 | 一源假說「Z₂ ± 修正」形式**被壓**——鋸齒真實但修正非常量 |
| T3 u/d 壓力 | ✅ robust（77%/68%） | 結構唔靠 PDG 中心值凑出 |

**剩餘方向（更新）**:
- 🔴 鋸齒嘅非二值修正 → 唔再用「±σ」模型；改問「even-rank 流 vs odd-rank 流各自嘅算子身份」——兩條流各自係乜？（even 流 = {u,s,c,b} 4 夸克; odd 流 = {e,d,μ,τ} 3 輕子+1 夸克）
- 🟡 O120/O206「升序雙射 p=0.00117」同「鋸齒 2.6% 普遍」嘅關係——階梯 T-statistic 喺 1055 個分裂 assignment 上嘅分布（下輪）
- 🟡 u/d 崩潰區（23%）——唯一可測嘅「scheme 敏感點」

## 文件動作

- scripts/07_ + logs/07_ + data/07_ json + docs/07（本文件）。
- SESSION_START append（第十一輪(d) 節）· README O206 行 round-11(d) 更新 · register O206 note。