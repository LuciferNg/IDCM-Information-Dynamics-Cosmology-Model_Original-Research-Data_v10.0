# O48 / Q1.42-43 — 峰形 joint/不對稱 fit 純 TT：右重結論撤回

> **日期**: 2026-10-10
> **狀態**: 🔴 峰形「右重」撤回（純 TT 方向反轉）；joint fit χ² 爆（尺度問題）
> **Script**: `60_q1_shape_joint_tt.py`（joint L/G 掃描）、`61_q1_asym_tt.py`（不對稱純 TT）

## 1. joint fit 純 TT（60）— χ² 爆, 方法唔 work

跟 scripts/36 框架（純 TT 215 bins + Plik cov TT block 215×215 + μK² residual + 單一 amplitude）:
```
Lorentz 最佳 γ=32.5 χ²=29083 (a=0.0014)
Gauss   最佳 σ=45.0 χ²=28455 (a=0.0023)
A1 L<G FAIL；A3 Δχ²=627.6「可分辨」但 χ² 全譜爆晒
D1 峰+谷 vs 峰only: Δχ²=−447 (谷層面更差) ← 同 scripts/36 SPT 相反！
```
診斷: 全域 log-poly detrend 喺 Plik C_ℓ（唔係 SPT D_ℓ）上留下巨大 residual
（residual RMS 0.037 vs cov diag 4e-4 → χ²/dof ~10³），amplitude 縮到 ~0.001。
→ **Plik C_ℓ 空間 + 全域 polyfit + cov 唔匹配**；scripts/36 成功係 SPT 自己嘅
   binned D_ℓ + 自己 cov 先得。joint fit 路線（47/47b/48/60）正式放棄。

## 2. 不對稱 Lorentz 純 TT（61）— 右重方向反轉 🔴

46b（613-rows 污染版）報: γR=41.5 > γL=28.5（右重, ratio 1.46）
61（純 TT 215 bins + cov TT block）:
```
峰 m=1 ℓ=221: c=209 γL=77.5 γR=37.5 ratio 0.48
峰 m=2 ℓ=527: c=522 γL=50 γR=42.5 ratio 0.85
峰 m=3 ℓ=815: c=803 γL=50 γR=35.0 ratio 0.70
峰 m=5 ℓ=1121: c=1151 γL=27.5 γR=15 ratio 0.55
峰 m=7 ℓ=1409: c=1491 γL=47.5 γR=15 ratio 0.32
平均 γL=50.5 > γR=29.0 → 左重?? A 爆細 (0.02~0.00), fit 心漂 (c=209/1151/1491)
```
- **「右重 γR>γL」撤回** — 46b 個結果係 TE/EE 污染；61 純 TT 報「左重」但 fit 心
  漂晒（c=209/1151/1491 vs 221/1121/1409）+ A 爆細 → **方向本身唔可信**，
  唔係物理反轉。峰形 fit（γL/γR 任何數值）宣佈無統計力。
- ⚠️ 但注意：谷位直接測量（54 script, 純 TT）谷→後峰 = 0.280（谷偏近後峰）
  = **峰高 ℓ 側（右側）較長** 嘅間接證據仍然成立——谷位係直接觀測量,
  唔受 fit 崩潰影響。峰形「右重」嘅谷位 sign 保留, fit 數值撤回。
- 唯一 PASS: 平均 γ=39.8 ∈ (30,55)（峯間隙/8=37.1 帶）, 但 fit 心漂令佢冇意義

## 3. 峰形攻勢最終狀態（Q1.26-34 + 42-43）

| 主張 | 狀態 |
|:-----|:-----|
| Lorentz 全勝 (43) | 🔴 撤回 — 613-rows 污染 |
| 右重 γR>γL (45/46b) | 🔴 撤回 fit 數值 — 61 純 TT 方向唔可信（fit 心漂）; 谷位 sign 保留（54: 谷→後峰 0.280） |
| σ≈50 = 峰固有寬度 (Q1.25) | ✅ 保留 — 組成分解 (binning+beam+lensing 只夠 10-15), 非 fit 產物 |
| γ≈35-38 ≈ 峰間隙/8 | 🟡 不穩 — fit-dependent, 唔可以當閉合 |
| Gauss vs Lorentz | 🟡 純 TT 無分辨力 (52: G 勝/平手 0/5) |

**峰形測量極限**: Plik 215 bins、SPT 52 bins、ACT 40 bins、PR4 detset ℓ-by-ℓ 全部
冇統計力分辨形狀族/不對稱度。σ≈50 嘅「寬度」係**唯一穩健峰形量**，但佢嘅
算子身份（49.5=297/6 vs 50 vs 55=F₁₀）仍然開放。

## 4. 教訓

- 46b/43 等所有 Plik fit 都要重跑純 TT 先算數；613-rows 任何統計都唔可信
- Plik C_ℓ cov 同全域 polyfit 唔匹配（cov 係 bandpower 空間, 唔係 detrend 空間）——
  scripts/36 成功係因為 SPT D_ℓ binned+自己 cov 一齊先自洽
- 峰形（形狀族/不對稱）喺現有公開數據冇解 — 需要未 bin 高分辨譜
  （WMAP 9yr 都係 binned；PR4 xfreq co-add + beam deconv 先有機會）