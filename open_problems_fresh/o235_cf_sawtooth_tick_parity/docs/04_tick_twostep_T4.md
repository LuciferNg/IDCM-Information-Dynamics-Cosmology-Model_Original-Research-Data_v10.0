# O235 docs/04 — T4: C_f 兩步映射不動點判死（2026-10-07）

> **Script**: `scripts/04_tick_twostep_T4.py`（10/10 PASS）
> **Log**: `logs/04_tick_twostep_T4.out`
> **預註冊**: 判死閾值 θ=0.1（script header 見數前寫死）；map G = 同 parity 兩步平均
> （8-rank ring BC, A_γ 質量序 e,u,d,s,μ,c,τ,b；t=13 VEV 層排除, O233 R19）
> **verdict**: ⚰️ **嚴格式死**（值層 C_f ∉ 兩步映射不動點）；存活剩 pattern 層
> （sign 交替 = 純 checkerboard 模 (−1)^r 嘅固定結構 = O233 鋸齒閉合嘅 tick 重讀）

## 一、兩步映射 G（A1–A3）

```txt
定義: (Gx)_r = (x_{r−2} + x_{r+2})/2, 8-ring periodic —— checkerboard leapfrog 嘅
      同 parity 兩步平均（T2 U2 喺 rank 空間嘅值層投影; ring BC = 88-ring 類比）
🟢 spec(G) = {1×2, −1×2, 0×4} (閉式 cos(πk/2), maxdev 3.33e-16)
🟢 Fix(G) = span{1, (−1)^r} dim 2 —— 常數 + 純 checkerboard 交替 =
   「靜態快照」嘅不動點條件 = 每 parity 內常數
🟢 家族: Fix dim 2 ∀ 2m-ring, m=3..6 (常數 + 交替不變)
```

## 二、pattern 層（B1–B2）

```txt
🟢 local alternation 8/8: 每個 odd-rank C_f < 兩偶鄰居
   (e<u; d<u,s; μ<s,c; τ<c,b —— 值層排列正正係鋸齒)
🟢 純 checkerboard 模 (−1)^r = sign 結構嘅不動點 (偶 rank 全 > 奇 rank;
   ⟨x,alt⟩/8 = −36.25 —— 交替分量顯著)
```

## 三、判死（C1–C3）

```txt
🟢 C_f ∉ Fix(G): R_raw = 0.6796 > θ=0.1; R_log = 0.4301 > θ=0.1
   (投影到 span{1,(−1)^r} 嘅殘差 ~ 43–68% —— 值層完全唔係不動點)
🟢 每 parity 內振幅跨度: even 67.3×, odd 44.4× —— 固定點要求 parity 內
   常數, 大規模違反 (兩個數量級)
🟢 t=13 VEV 排除 (C_f_t=7722.8, O233 R19) —— 判死喺 8 費米子族執行
⟹ 嚴格式「質量譜 = checkerboard 靜態快照」= ⚰️ 死
```

## 四、穩健性（D1–D2）

```txt
🟢 ±10% 值擾動 ×200: 殘差最低 0.6959 > 0.1 —— 判死結論唔係邊界效應
🟢 零參數 + MC N/A: 判死係確定性閾值測試; pattern 統計 = O233 原狀
   (1/56 nominal / look-elsewhere 0.1204, 唔重推)
```

## 五、判決（兩層分離）

```txt
⚰️ 嚴格式 (T4 判死): C_f 8 值唔係兩步映射不動點 —— 「質量譜 = tick 動力學
   靜態快照」喺值層上假咗。時間處理假説嘅 this-strong-form 死, 記錄負結果。
🟢 弱格式存活: pattern 層 (sign 交替 8/8 = (−1)^r 固定結構) = O233 已閉合
   鋸齒 (7/7, p=0.0138) 嘅 tick 重讀 —— tick 宇稱解釋「點解 odd-flow
   細/even-flow 大」嘅排列, 唔解釋 C_f 值本身 (O233 生成器負, 本 O 唔重推)。
🟡 統計層不變: T3/T4 係機制層支持, 唔加統計; 升 🟢 要樣本外盲測。
⟹ O235 整體 = partial（機制層正 + 嚴格式負 + 統計門檻未過）
```

## 六、產物

- `scripts/04_tick_twostep_T4.py`（10/10 PASS）+ `logs/04_tick_twostep_T4.out`
- C_f 值源: O233 01_problem_record L33 (e 3.5941·u 3.803·d 3.662·s 41.32·
  μ 30.03·c 186.06·τ 159.64·b 255.75; t 走 VEV)
- O233 鋸齒統計引用: docs/14 (7/7, 1/14, 1/56, LE 0.1204 docs/12)